from flask import Flask, render_template, request, redirect, session, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import pymongo
import datetime
import os
from dotenv import load_dotenv
from bson import ObjectId
load_dotenv()

#User Class
class User(UserMixin):
    def __init__(self, user_id, username, password):
        self.id = user_id
        self.username = username
        self.password = password

def create_app():
    """
    Create and configure the Flask application.
    returns: app: the Flask application object
    """
    app=Flask(__name__)
    cxn = pymongo.MongoClient(os.getenv("MONGO_URI"))
    db = cxn[os.getenv("MONGO_DBNAME")]
    app.secret_key = os.getenv("SECRET_KEY")
    
    try:
        cxn.admin.command("ping")
        print(" *", "Connected to MongoDB!")
    except Exception as e:
        print(" * MongoDB connection error:", e) 
        
    ##########################################       
    # LOGIN MANAGER
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    @login_manager.user_loader
    def load_user(user_id):
        user_data = db.users.find_one({"_id": ObjectId(user_id)})
        if user_data:
            return User(user_id=str(user_data['_id']), username=user_data['username'], password=user_data['password'])
        return None

    # REGISTER
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            repassword = request.form['repassword']
            if password != repassword:
                flash("Passwords do not match.")
                return redirect(url_for('register'))
            
            hashed_password = generate_password_hash(password)
            if db.users.find_one({"username": username}):
                flash("Username already exists.")
                return redirect(url_for('register'))
            

            db.users.insert_one({"username": username, "password": hashed_password})
            flash("Registration successful. Please log in.")
            return redirect(url_for('login'))

        return render_template('register.html')

    # LOGIN
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            user_data = db.users.find_one({"username": username})

            if user_data and check_password_hash(user_data['password'], password):
                user = User(user_id=str(user_data['_id']), username=user_data['username'], password=user_data['password'])
                login_user(user)
                flash('Login successful!')
                return redirect(url_for('index'))
            else:
                flash('Invalid username or password.')
                return redirect(url_for('login'))

        return render_template('login.html')

    # LOGOUT
    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        session.pop('_flashes', None) 
        flash('You have been logged out.')
        return redirect(url_for('login'))


    @app.route('/')
    @login_required
    def index():
        user_id = current_user.get_id()
        current_tasks = list(db.tasks.find({
            "posted_by": user_id, 
            "status": "Not completed"
            }).sort("created_at", pymongo.DESCENDING))
    
        return render_template('index.html', tasks=current_tasks)

    # Route for adding a task
    @app.route('/add', methods=['GET', 'POST'])
    def add_task():
        if request.method == 'POST':
            title = request.form["title"]
            category = request.form.get('category')
            description = request.form["description"]
            deadline = request.form["deadline"]
            user_id = current_user.get_id()
            task = {
                "title": title,
                "category": category,
                "description": description,
                "created_at": datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M'),
                "deadline": deadline,
                "status" : "Not completed",
                "posted_by": user_id
            }
            
            db.tasks.insert_one(task)
            return redirect('/') #this redirects to the homepage after adding task
    

        return render_template('data_add.html')

    # Route for editing a task
    @app.route('/edit/<task_id>', methods=['GET', 'POST'])
    def edit_task(task_id):
        if request.method == 'POST':
            redirect_to = request.args.get("redirect_to")
            

            title = request.form["title"]
            category = request.form.get('category')
            description = request.form["description"]
            deadline = request.form["deadline"]

            task = {
                "title": title,
                "category": category,
                "description": description,
                "deadline": deadline
            }

            db.tasks.update_one({"_id": ObjectId(task_id)}, {"$set": task})

            # Redirect  after updating the task
            if redirect_to == "display":
                return redirect("/display")
            else:
                return redirect("/")

        else:
            task = db.tasks.find_one({"_id": ObjectId(task_id)})
            return render_template("data_edit.html", task=task)
   
        
    # Route for deleting a task
    @app.route("/delete/<task_id>")
    def delete_task(task_id):
        redirect_to = request.args.get("redirect_to")
        db.tasks.delete_one({"_id": ObjectId(task_id)})
        if redirect_to == "display":
            return redirect("/display")
        else:
            return redirect("/")



    @app.route('/delete_selected', methods=['POST'])
    def delete_selected_tasks():
        task_ids = request.form.getlist('task_ids')  

        title = request.form.get('title', '').strip()  
        category = request.form.get('category', '').strip()  

        if task_ids:
            db.tasks.delete_many({"_id": {"$in": [ObjectId(task_id) for task_id in task_ids]}})
       


        query = {"posted_by": current_user.get_id()}
        if title:
            query["title"] = {"$regex": title, "$options": "i"}
        if category:
            query["category"] = category

        tasks = list(db.tasks.find(query))

        return render_template('search.html', tasks=tasks, title=title, category=category, searched=True)

    
    # Route for deleting a task
    @app.route("/complete/<task_id>")
    def complete_task(task_id):
        redirect_to = request.args.get("redirect_to")
        db.tasks.update_one(
            {"_id": ObjectId(task_id)},
            {
                "$set": {
                    "status": "Completed",
                    "completed_at": datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M') 
                }
            }
         )
        if redirect_to == "display":
            return redirect("/display")
        else:
            return redirect("/")
    
    # Route for displaying all tasks
    @app.route('/display', methods=['GET', 'POST'])
    def display_tasks():
        user_id = current_user.get_id()
        pending_tasks = list(db.tasks.find({"status": "Not completed", "posted_by": user_id}).sort("deadline", pymongo.ASCENDING))
        completed_tasks = list(db.tasks.find({"status": "Completed", "posted_by": user_id}).sort("completed_at", pymongo.DESCENDING))
        return render_template('display_all.html', pending_tasks = pending_tasks, completed_tasks = completed_tasks)

    

    # Route for searching tasks by title and category
    @app.route('/search', methods=['GET', 'POST'])
    def search_task():
        tasks = []
        searched = False

        if request.method == 'POST':
            title = request.form.get('title', '').strip()
            category = request.form.get('category', '').strip()

            return redirect(url_for('search_task', title=title, category=category))

        title = request.args.get('title', '').strip()
        category = request.args.get('category', '').strip()
        
        query = {}

        if title or category:
            searched = True
            query = {"posted_by": current_user.get_id()}
            if title:
                query["title"] = {"$regex" : title, "$options": "i"}
            if category:
                query["category"] = category
        
        if query:
            tasks = list(db.tasks.find(query))

        return render_template('search.html', tasks=tasks, title=title, category=category, searched = searched)
    return app

if __name__ == '__main__':
    FLASK_PORT = os.getenv("FLASK_PORT", "11000")
    app = create_app()
    app.run(debug=True)