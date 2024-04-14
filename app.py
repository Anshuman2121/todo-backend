import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import mysql.connector

# Load environment variables from .env file
load_dotenv()

MYSQL_HOST = os.getenv("MYSQL_HOST", "host.docker.internal")
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "my_password")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "my_database")

# MySQL connection
connection = mysql.connector.connect(
    host=MYSQL_HOST,
    user=MYSQL_USER,
    password=MYSQL_PASSWORD,
    database=MYSQL_DATABASE
)

app = Flask(__name__)
CORS(app, origins="*", allow_headers=["Content-Type", "Authorization"])  # Explicitly allow all origins

# Define the Task model
class Task:
    def __init__(self, title, description):
        self.title = title
        self.description = description

    def to_dict(self):
        return {
            'title': self.title,
            'description': self.description
        }

# Create a table for tasks (You can run this once outside of the app)
@app.route("/api", methods=['GET'])
def create_tasks_table():
    try:
        cursor = connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Tasks (
                ID int NOT NULL AUTO_INCREMENT PRIMARY KEY,
                Title varchar(255),
                Description text
            );
        """)
        connection.commit()        
    except Exception as e:
        print(e)
    return "Table Created... Tasks API Ready"

# List all tasks
@app.route("/tasks", methods=['GET'])
def get_tasks_without_api():
    tasks = []
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM Tasks")
        for row in cursor.fetchall():
            task = {
                "ID": row[0],
                "Title": row[1],
                "Description": row[2]
            }
            tasks.append(task)
    return jsonify(tasks)

# Retrieve a single task by ID
@app.route("/api/tasks/<int:task_id>", methods=['GET'])
def get_task(task_id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM Tasks WHERE ID = %s", (task_id,))
        row = cursor.fetchone()
        if row:
            task = {
                "ID": row[0],
                "Title": row[1],
                "Description": row[2]
            }
            return jsonify(task)
        return jsonify({"message": "Task not found"})

# Create a new task
@app.route("/tasks", methods=['POST'])
def create_task():
    task_data = request.json
    task = Task(**task_data)
    with connection.cursor() as cursor:
        cursor.execute("INSERT INTO Tasks (Title, Description) VALUES (%s, %s)", (task.title, task.description))
        connection.commit()
    return jsonify(task.to_dict())


# Update an existing task by ID
@app.route("/api/tasks/<int:task_id>", methods=['PUT'])
def update_task(task_id):
    updated_task_data = request.json
    updated_task = Task(**updated_task_data)
    with connection.cursor() as cursor:
        cursor.execute("UPDATE Tasks SET Title = %s, Description = %s WHERE ID = %s", (updated_task.title, updated_task.description, task_id))
        connection.commit()
        return jsonify({"message": "Task updated"})

# Delete a task by ID
@app.route("/api/tasks/<int:task_id>", methods=['DELETE'])
def delete_task(task_id):
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM Tasks WHERE ID = %s", (task_id,))
        connection.commit()
        return jsonify({"message": "Task deleted"})

# Handle OPTIONS requests
@app.route("/api/tasks", methods=['OPTIONS'])
def handle_options_request():
    return jsonify({'status': 'ok'}), 200

if __name__ == "__main__":
    create_tasks_table()
    app.run(host="0.0.0.0", port=8000)
