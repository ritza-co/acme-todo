# Simple Todo API - Flask Implementation

A Flask server implementation of the Simple Todo API defined in `acmetodo.yaml`.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the server:
```bash
python app.py
```

The server will start on `http://localhost:5000`

## API Endpoints

- `GET /todos` - List all todos
- `POST /todos` - Create a new todo
- `GET /todos/{id}` - Get a specific todo
- `PUT /todos/{id}` - Replace a todo
- `PATCH /todos/{id}` - Update a todo
- `DELETE /todos/{id}` - Delete a todo

## Example Usage

```bash
# List all todos
curl http://localhost:5000/todos

# Create a new todo
curl -X POST http://localhost:5000/todos \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy groceries", "completed": false}'

# Get a specific todo
curl http://localhost:5000/todos/1

# Update a todo
curl -X PATCH http://localhost:5000/todos/1 \
  -H "Content-Type: application/json" \
  -d '{"completed": true}'

# Delete a todo
curl -X DELETE http://localhost:5000/todos/1
```

## Data Format

Todos have the following structure:
- `id` (integer, read-only) - Unique identifier
- `title` (string, required) - Todo title
- `completed` (boolean, default: false) - Completion status
- `dueDate` (string, optional) - Due date in YYYY-MM-DD format
