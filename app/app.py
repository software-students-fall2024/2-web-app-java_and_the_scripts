from flask import Flask, render_template, request, redirect, url_for
import pymongo
import datetime
import os
from dotenv import load_dotenv
from bson import ObjectId
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
        current_tasks = list(db.tasks.find({"status": "Not completed"}).sort("created_at", pymongo.DESCENDING))
        return render_template('index.html', tasks=current_tasks)

    # Route for adding a task
    @app.route('/add', methods=['GET', 'POST'])
    def add_task():
        if request.method == 'POST':
            title = request.form["title"]
            category = request.form.get('category')
            description = request.form["description"]
            deadline = request.form["deadline"]

            task = {
                "title": title,
                "category": category,
                "description": description,
                "created_at": datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M'),
                "deadline": deadline,
                "status" : "Not completed"

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

    @app.route("/delete-by-many", methods=["GET","POST"])
    def delete_by_many():
        if request.method == 'POST':
            title = request.form["title"]
            category = request.form.get['category']
            db.tasks.delete_many({"title": title, "category": category})
        return render_template('data_delete.html')
    
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
        pending_tasks = list(db.tasks.find({"status": "Not completed"}).sort("deadline", pymongo.ASCENDING))
        completed_tasks = list(db.tasks.find({"status": "Completed"}).sort("completed_at", pymongo.DESCENDING))
        return render_template('display_all.html', pending_tasks = pending_tasks, completed_tasks = completed_tasks)
        #tasks = tasks means that it's passing data from the backend to the frontend html template
        #remember to modify html to use tasks
    

    # Route for searching tasks by title and category
    @app.route('/search', methods=['GET', 'POST'])
    def search_task():
        tasks = []
        if request.method == 'POST':
            title = request.form.get('title')
            category = request.form.get('category')

            query = {}
            if title:
                #this builds the critria we need to use for .find
                #regex means regular expression
                #options: i  is a flag that will make the search case-insensitive
                if title:
                    query["title"] = {"$regex" : title, "$options": "i"}
                if category:
                    query["category"] = {"$regex": category, "$options": "i"}
                
                tasks = list(db.tasks.find(query))

        return render_template('search.html', tasks = tasks) #remember to modify html to use tasks
    return app

if __name__ == '__main__':
    FLASK_PORT = os.getenv("FLASK_PORT", "11000")
    app = create_app()
    app.run(debug=True)