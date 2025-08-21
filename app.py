from flask import Flask, request, jsonify, abort

app = Flask(__name__)

# Hardcoded readonly TODO data
todos_data = [
    {
        'id': 1,
        'title': 'Set up development environment',
        'completed': True,
        'dueDate': '2024-12-01',
        'description': 'Install necessary development tools and configure workspace'
    },
    {
        'id': 2,
        'title': 'Design system architecture',
        'completed': False,
        'dueDate': '2024-12-15',
        'description': 'Create high-level system design and component architecture'
    },
    {
        'id': 3,
        'title': 'Implement user authentication',
        'completed': False,
        'dueDate': '2024-12-20',
        'description': 'Build secure login and registration functionality'
    },
    {
        'id': 4,
        'title': 'Write unit tests',
        'completed': False,
        'dueDate': '2024-12-25',
        'description': 'Create comprehensive test coverage for core functionality'
    },
    {
        'id': 5,
        'title': 'Deploy to production',
        'completed': False,
        'dueDate': '2024-12-30',
        'description': 'Set up production environment and deploy application'
    }
]



@app.route('/search', methods=['POST'])
def search():
    """Search for todos based on query - MCP server search tool"""
    if not request.is_json:
        abort(400, description="Request must be JSON")
    
    data = request.get_json()
    
    if not data or 'query' not in data:
        abort(400, description="Query is required")
    
    query = data['query'].lower()
    results = []
    
    for todo in todos_data:
        # Search in title and description
        if (query in todo['title'].lower() or 
            query in todo.get('description', '').lower()):
            
            # Create a snippet from description or title
            description = todo.get('description', '')
            if description:
                text_snippet = description[:150] + "..." if len(description) > 150 else description
            else:
                text_snippet = todo['title']
            
            # Add completion status to snippet
            status = "✓ Completed" if todo.get('completed', False) else "○ Pending"
            if todo.get('dueDate'):
                status += f" | Due: {todo['dueDate']}"
            text_snippet = f"{text_snippet} ({status})"
            
            result = {
                "id": str(todo['id']),
                "title": todo['title'],
                "text": text_snippet,
                "url": f"https://acme-todo-gpt-mcp.ritzademo.com/fetch/{todo['id']}"
            }
            results.append(result)
    
    return jsonify(results)

@app.route('/fetch', methods=['POST'])
def fetch():
    """Fetch complete todo details by ID - MCP server fetch tool"""
    if not request.is_json:
        abort(400, description="Request must be JSON")
    
    data = request.get_json()
    
    if not data or 'id' not in data:
        abort(400, description="ID is required")
    
    try:
        todo_id = int(data['id'])
    except ValueError:
        abort(400, description="ID must be a valid integer")
    
    # Find todo in our hardcoded data
    todo = next((t for t in todos_data if t['id'] == todo_id), None)
    
    if not todo:
        abort(404, description="Todo not found")
    
    # Create full text content
    full_text = f"Title: {todo['title']}\n"
    full_text += f"Status: {'Completed' if todo.get('completed', False) else 'Not completed'}\n"
    if todo.get('dueDate'):
        full_text += f"Due Date: {todo['dueDate']}\n"
    if todo.get('description'):
        full_text += f"Description: {todo['description']}\n"
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
        "url": f"https://acme-todo-gpt-mcp.ritzademo.com/fetch/{todo['id']}",
        "metadata": {
            "completed": todo.get('completed', False),
            "dueDate": todo.get('dueDate'),
            "description": todo.get('description')
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
    app.run(debug=True, host='0.0.0.0', port=5004)
