from flask import render_template
from app import app

from flask import render_template
from app import app

@app.route('/add', methods=['GET', 'POST'])
def add_task():
    # Your logic for adding a task
    return render_template('data_add.html')

@app.route('/edit', methods=['GET', 'POST'])
def edit_task():
    # Your logic for editing a task
    return render_template('data_edit.html')

@app.route('/delete', methods=['GET', 'POST'])
def delete_task():
    # Your logic for deleting a task
    return render_template('data_delete.html')

@app.route('/display', methods=['GET', 'POST'])
def display_tasks():
    # Your logic for displaying all tasks
    return render_template('display_all.html')

@app.route('/pending', methods=['GET', 'POST'])
def pending_tasks():
    # Your logic for displaying pending tasks
    return render_template('pending.html')

@app.route('/search', methods=['GET', 'POST'])
def search_task():
    # Your logic for searching tasks
    return render_template('search.html')
