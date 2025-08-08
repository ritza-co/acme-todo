from flask import Flask, request, jsonify, abort
from datetime import datetime
from typing import Dict, List, Optional
import json
from functools import wraps

app = Flask(__name__)

# In-memory storage for todos
todos_storage: Dict[int, dict] = {}
secret_todos_storage: Dict[int, dict] = {}
next_id = 1
next_secret_id = 1

# Simple API key for authentication (in production, use environment variables)
API_KEY = "sk-todo-THISISSECRET"

def require_api_key(f):
    """Decorator to require API key authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key or api_key != API_KEY:
            abort(401, description="Invalid or missing API key")
        return f(*args, **kwargs)
    return decorated_function

def validate_date(date_string: str) -> bool:
    """Validate date string format (YYYY-MM-DD)"""
    try:
        datetime.strptime(date_string, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def create_todo_response(todo_data: dict) -> dict:
    """Create a standardized todo response"""
    return {
        'id': todo_data['id'],
        'title': todo_data['title'],
        'completed': todo_data.get('completed', False),
        'dueDate': todo_data.get('dueDate')
    }

@app.route('/todos', methods=['GET'])
def list_todos():
    """List all todos"""
    return jsonify([create_todo_response(todo) for todo in todos_storage.values()])

@app.route('/todos', methods=['POST'])
def create_todo():
    """Create a new todo"""
    global next_id
    
    if not request.is_json:
        abort(400, description="Request must be JSON")
    
    data = request.get_json()
    
    if not data or 'title' not in data:
        abort(400, description="Title is required")
    
    # Validate dueDate if provided
    if 'dueDate' in data and data['dueDate'] is not None:
        if not validate_date(data['dueDate']):
            abort(400, description="Invalid date format. Use YYYY-MM-DD")
    
    new_todo = {
        'id': next_id,
        'title': data['title'],
        'completed': data.get('completed', False),
        'dueDate': data.get('dueDate')
    }
    
    todos_storage[next_id] = new_todo
    next_id += 1
    
    return jsonify(create_todo_response(new_todo)), 201

@app.route('/todos/<int:todo_id>', methods=['GET'])
def get_todo(todo_id: int):
    """Retrieve a specific todo"""
    if todo_id not in todos_storage:
        abort(404, description="Todo not found")
    
    return jsonify(create_todo_response(todos_storage[todo_id]))

@app.route('/todos/<int:todo_id>', methods=['PUT'])
def replace_todo(todo_id: int):
    """Replace a todo (full update)"""
    if todo_id not in todos_storage:
        abort(404, description="Todo not found")
    
    if not request.is_json:
        abort(400, description="Request must be JSON")
    
    data = request.get_json()
    
    if not data or 'title' not in data:
        abort(400, description="Title is required")
    
    # Validate dueDate if provided
    if 'dueDate' in data and data['dueDate'] is not None:
        if not validate_date(data['dueDate']):
            abort(400, description="Invalid date format. Use YYYY-MM-DD")
    
    # Replace the entire todo (except id)
    todos_storage[todo_id] = {
        'id': todo_id,
        'title': data['title'],
        'completed': data.get('completed', False),
        'dueDate': data.get('dueDate')
    }
    
    return jsonify(create_todo_response(todos_storage[todo_id]))

@app.route('/todos/<int:todo_id>', methods=['PATCH'])
def update_todo(todo_id: int):
    """Update a todo (partial update)"""
    if todo_id not in todos_storage:
        abort(404, description="Todo not found")
    
    if not request.is_json:
        abort(400, description="Request must be JSON")
    
    data = request.get_json()
    
    if not data:
        abort(400, description="No data provided")
    
    # Validate dueDate if provided
    if 'dueDate' in data and data['dueDate'] is not None:
        if not validate_date(data['dueDate']):
            abort(400, description="Invalid date format. Use YYYY-MM-DD")
    
    # Update only provided fields
    todo = todos_storage[todo_id]
    if 'title' in data:
        todo['title'] = data['title']
    if 'completed' in data:
        todo['completed'] = data['completed']
    if 'dueDate' in data:
        todo['dueDate'] = data['dueDate']
    
    return jsonify(create_todo_response(todo))

@app.route('/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id: int):
    """Delete a todo"""
    if todo_id not in todos_storage:
        abort(404, description="Todo not found")
    
    del todos_storage[todo_id]
    return '', 204

@app.route('/add-secret-todo', methods=['POST'])
@require_api_key
def add_secret_todo():
    """Add a secret todo (requires API key)"""
    global next_secret_id
    
    if not request.is_json:
        abort(400, description="Request must be JSON")
    
    data = request.get_json()
    
    if not data or 'title' not in data:
        abort(400, description="Title is required")
    
    # Validate dueDate if provided
    if 'dueDate' in data and data['dueDate'] is not None:
        if not validate_date(data['dueDate']):
            abort(400, description="Invalid date format. Use YYYY-MM-DD")
    
    new_todo = {
        'id': next_secret_id,
        'title': data['title'],
        'completed': data.get('completed', False),
        'dueDate': data.get('dueDate')
    }
    
    secret_todos_storage[next_secret_id] = new_todo
    next_secret_id += 1
    
    return jsonify(create_todo_response(new_todo)), 201

@app.route('/read-secret-todos', methods=['GET'])
@require_api_key
def read_secret_todos():
    """Read all secret todos (requires API key)"""
    return jsonify([create_todo_response(todo) for todo in secret_todos_storage.values()])

@app.route('/search', methods=['POST'])
def search():
    """Search for todos based on query - ChatGPT connector endpoint"""
    if not request.is_json:
        abort(400, description="Request must be JSON")
    
    data = request.get_json()
    
    if not data or 'query' not in data:
        abort(400, description="Query is required")
    
    query = data['query'].lower()
    results = []
    
    # Search through all todos (both regular and secret for now)
    all_todos = list(todos_storage.values()) + list(secret_todos_storage.values())
    
    for todo in all_todos:
        # Simple text matching on title
        if query in todo['title'].lower():
            # Create a snippet (first 100 chars of title)
            text_snippet = todo['title'][:100] + "..." if len(todo['title']) > 100 else todo['title']
            
            # Add completion status to snippet
            status = "✓ Completed" if todo.get('completed', False) else "○ Pending"
            if todo.get('dueDate'):
                status += f" | Due: {todo['dueDate']}"
            text_snippet = f"{text_snippet} ({status})"
            
            result = {
                "id": str(todo['id']),
                "title": todo['title'],
                "text": text_snippet,
                "url": f"https://acme-todo-gpt-mcp.ritzademo.com/todos/{todo['id']}"
            }
            results.append(result)
    
    return jsonify({"results": results})

@app.route('/fetch', methods=['POST'])
def fetch():
    """Fetch complete todo details by ID - ChatGPT connector endpoint"""
    if not request.is_json:
        abort(400, description="Request must be JSON")
    
    data = request.get_json()
    
    if not data or 'id' not in data:
        abort(400, description="ID is required")
    
    try:
        todo_id = int(data['id'])
    except ValueError:
        abort(400, description="ID must be a valid integer")
    
    # Look for todo in both storages
    todo = todos_storage.get(todo_id) or secret_todos_storage.get(todo_id)
    
    if not todo:
        abort(404, description="Todo not found")
    
    # Create full text content
    full_text = f"Title: {todo['title']}\n"
    full_text += f"Status: {'Completed' if todo.get('completed', False) else 'Not completed'}\n"
    if todo.get('dueDate'):
        full_text += f"Due Date: {todo['dueDate']}\n"
    full_text += "\n"
    full_text += f"This is a todo item with ID {todo_id}. "
    if todo.get('completed', False):
        full_text += "This task has been marked as completed."
    else:
        full_text += "This task is still pending completion."
    
    result = {
        "id": str(todo['id']),
        "title": todo['title'],
        "text": full_text,
        "url": f"https://acme-todo-gpt-mcp.ritzademo.com/todos/{todo['id']}",
        "metadata": {
            "completed": todo.get('completed', False),
            "dueDate": todo.get('dueDate')
        }
    }
    
    return jsonify(result)

@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad Request', 'message': str(error.description)}), 400

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({'error': 'Unauthorized', 'message': str(error.description)}), 401

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not Found', 'message': str(error.description)}), 404

if __name__ == '__main__':
    # Add some sample data
    todos_storage[1] = {'id': 1, 'title': 'Buy milk', 'completed': False, 'dueDate': None}
    todos_storage[2] = {'id': 2, 'title': 'Walk the dog', 'completed': True, 'dueDate': '2024-12-07'}
    next_id = 3
    
    app.run(debug=True, host='0.0.0.0', port=5004)
