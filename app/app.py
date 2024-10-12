from flask import Flask, render_template, request, redirect, url_for
import pymongo
import datetime
from dotenv import load_dotenv

load_dotenv()

def create_app():
    """
    Create and configure the Flask application.
    returns: app: the Flask application object
    """
    app=Flask(__name__)
    cxn = pymongo.MongoClient(os.getenv("MONGO_URI"))
    db = cxn[os.getenv("MONGO_DBNAME")]
    
    try:
        cxn.admin.command("ping")
        print(" *", "Connected to MongoDB!")
    except Exception as e:
        print(" * MongoDB connection error:", e) 
           
    # Home route
    @app.route('/')
    def index():
        return render_template('index.html')

    # Route for adding a task
    @app.route('/add', methods=['GET', 'POST'])
    def add_task():
        if request.method == 'POST':
            title = request.form["title"]
            category = request.form.get['category']
            description = request.form["description"]
            deadline = request.form["deadline"]

            task = {
                "title": title,
                "category": category,
                "description": description,
                "created_at": datetime.datetime.utcnow(),
                "deadline": deadline,
                "status" : "Not completed"

            }
            
            db.tasks.insert_one(task)
            return redirect('/') #this redirects to the homepage after adding task
    

        return render_template('data_add.html')

    # Route for editing a task
    @app.route('/edit/<task_id>')
    def edit_task():
        task = db.tasks.find_one({"_id": ObjectId(task_id)})
        return render_template("data_edit.html", task=task)
    @app.route("/edit/<task_id>", methods=["POST"])
    def edit_submit(task_id):
        """
        Route for POST requests to the edit page.
        Accepts the form submission data for the specified document and updates the document in the database.
        Args:
            post_id (str): The ID of the post to edit.
        Returns:
            redirect (Response): A redirect response to the home page.
        """
        title = request.form["title"]
        category = request.form.get['category']
        description = request.form["description"]
        deadline = request.form["deadline"]

        task = {
            "title": title,
            "category": category,
            "description": description,
            "deadline": deadline
        }

        db.tasks.update_one({"_id": ObjectId(task_id)}, {"$set": task})

        return redirect("/")
        
    # Route for deleting a task
    @app.route("/delete/<task_id>")
    def delete_task(task_id):
        db.tasks.delete_one({"_id": ObjectId(task_id)})
        return redirect("/")

    @app.route("/delete-by-many", methods=["GET","POST"])
    def delete_by_many():
        if request.method == 'POST':
            title = request.form["title"]
            category = request.form.get['category']
            db.tasks.delete_many({"title": title, "category": category})
        return render_template('data_delete.html')

    # Route for displaying all tasks
    @app.route('/display', methods=['GET', 'POST'])
    def display_tasks():
        pending_tasks = list(db.tasks.find({"status": "Not completed"}))
        completed_tasks = list(db.tasks.find({"status": "Completed"}))
        return render_template('display_all.html', pending_tasks = pending_tasks, completed_tasks = completed_tasks)
        #tasks = tasks means that it's passing data from the backend to the frontend html template

    # Route for displaying pending tasks
    #@app.route('/pending', methods=['GET', 'POST'])
    #def pending_tasks():
    #    return render_template('pending.html')

    # Route for searching tasks
    @app.route('/search', methods=['GET', 'POST'])
    def search_task():
        return render_template('search.html')
    return app

if __name__ == '__main__':
    FLASK_PORT = os.getenv("FLASK_PORT", "11000")
    app = create_app()
    app.run(debug=True)