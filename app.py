from flask import Flask, request, jsonify, abort
from datetime import datetime
from typing import Dict, List, Optional
import json

app = Flask(__name__)

# In-memory storage for todos
todos_storage: Dict[int, dict] = {}
next_id = 1

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

@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad Request', 'message': str(error.description)}), 400

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not Found', 'message': str(error.description)}), 404

if __name__ == '__main__':
    # Add some sample data
    todos_storage[1] = {'id': 1, 'title': 'Buy milk', 'completed': False, 'dueDate': None}
    todos_storage[2] = {'id': 2, 'title': 'Walk the dog', 'completed': True, 'dueDate': '2024-12-07'}
    next_id = 3
    
    app.run(debug=True, host='0.0.0.0', port=5004)
