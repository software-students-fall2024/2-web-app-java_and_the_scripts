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
    @app.route('/edit', methods=['GET', 'POST'])
    def edit_task():
        return render_template('data_edit.html')

    # Route for deleting a task
    @app.route('/delete', methods=['GET', 'POST'])
    def delete_task():
        return render_template('data_delete.html')

    # Route for displaying all tasks
    @app.route('/display', methods=['GET', 'POST'])
    def display_tasks():
        return render_template('display_all.html')

    # Route for displaying pending tasks
    @app.route('/pending', methods=['GET', 'POST'])
    def pending_tasks():
        return render_template('pending.html')

    # Route for searching tasks
    @app.route('/search', methods=['GET', 'POST'])
    def search_task():
        return render_template('search.html')
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
