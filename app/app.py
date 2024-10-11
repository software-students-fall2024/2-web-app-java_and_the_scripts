from flask import Flask, render_template

app = Flask(__name__)

# Home route
@app.route('/')
def index():
    return render_template('index.html')

# Route for adding a task
@app.route('/add', methods=['GET', 'POST'])
def add_task():
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

if __name__ == '__main__':
    app.run(debug=True)
