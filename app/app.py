from flask import Flask, render_template, request, redirect, url_for, flash
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
        flash('You have been logged out.')
        return redirect(url_for('login'))

    # HOME but have to login or register to access
    @app.route('/')
    @login_required
    def index():
        user_id = current_user.get_id()
        current_tasks = list(db.tasks.find({
            "posted_by": user_id,  # Make sure tasks have a user_id field associated with them
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
            
            # Handle POST request to update the task
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
            # Handle GET request to display the edit form
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

    # @app.route('/delete_by_many', methods=['GET', 'POST'])
    # def delete_by_many():
    #     message = ""
    #     if request.method == 'POST':
    #         category = request.form.get('category')
    #         # Check how many tasks match the category
    #         tasks_to_delete = db.tasks.count_documents({"category": category})
            
    #         if tasks_to_delete > 0:
    #             # If there are matching tasks, delete them and set success message
    #             db.tasks.delete_many({"category": category})
    #             message = f"Tasks in the {category} category were successfully deleted."
    #         else:
    #             # If no matching tasks, set a different message
    #             message = f"No tasks found in the {category} category to delete."
        
    #     return render_template('delete_by_many.html', message=message)


    @app.route('/delete_selected', methods=['POST'])
    def delete_selected_tasks():
        task_ids = request.form.getlist('task_ids')  # Get the selected task IDs from the form

        title = request.form.get('title', '').strip()  # Single title
        category = request.form.get('category', '').strip()  # Single category

        if task_ids:
            # Convert string IDs to ObjectId and delete the selected tasks
            db.tasks.delete_many({"_id": {"$in": [ObjectId(task_id) for task_id in task_ids]}})
            flash(f"Deleted {len(task_ids)} task(s) successfully.")
        else:
            flash("No tasks selected for deletion.")


        query = {}
        if title:
            query["title"] = {"$regex": title, "$options": "i"}  # Case-insensitive search
        if category:
            query["category"] = category

        # Fetch the remaining tasks after deletion
        tasks = list(db.tasks.find(query))

        # Render the updated task list with the search parameters
        return render_template('search.html', tasks=tasks, title=title, category=category, searched=True)

        # return redirect(url_for('search_task'))

    
    # Route for deleting a task
    @app.route("/complete/<task_id>")
    def complete_task(task_id):
        redirect_to = request.args.get("redirect_to")
        db.tasks.update_one(
            {"_id": ObjectId(task_id)},
            {
                "$set": {
                    "status": "Completed",
                    "completed_at": datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M')  # Optionally track the completion time
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
        #tasks = tasks means that it's passing data from the backend to the frontend html template
        #remember to modify html to use tasks
    

    # Route for searching tasks by title and category
    @app.route('/search', methods=['GET', 'POST'])
    def search_task():
        tasks = []
        searched = False

        if request.method == 'POST':
            # title = request.form.get('title')
            # category = request.form.get('category')
            title = request.form.get('title', '').strip()
            category = request.form.get('category', '').strip()

            return redirect(url_for('search_task', title=title, category=category))

        title = request.args.get('title', '').strip()
        category = request.args.get('category', '').strip()
        
        query = {}

        if title or category:
            searched = True
            query["title"] = {"$regex" : title, "$options": "i"}
        if category:
            query["category"] = category
        
        if query:
            tasks = list(db.tasks.find(query))

        return render_template('search.html', tasks=tasks, title=title, category=category, searched = searched)
        # return render_template('search.html', tasks = tasks) #remember to modify html to use tasks
    return app

if __name__ == '__main__':
    FLASK_PORT = os.getenv("FLASK_PORT", "11000")
    app = create_app()
    app.run(debug=True)