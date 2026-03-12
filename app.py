from flask import Flask, jsonify, request, redirect, url_for, render_template_string
import sqlite3
import os

app = Flask(__name__)
DB_NAME = 'lost_found.db'

# Initialize database
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            location TEXT,
            status TEXT DEFAULT 'Lost'
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Home route
@app.route('/')
def home():
    return jsonify({
        "message": "Welcome to the Campus Lost and Found API",
        "status": "running",
        "endpoints": [
            "/items",
            "/report",
            "/search",
            "/admin"
        ]
    })

# API: Get all lost items
@app.route('/items', methods=['GET'])
def get_items():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT * FROM items')
    rows = c.fetchall()
    conn.close()
    items = [{"id": r[0], "name": r[1], "description": r[2], "location": r[3], "status": r[4]} for r in rows]
    return jsonify({"total_items": len(items), "items": items})

# API: Report lost item
@app.route('/report', methods=['POST'])
def report_item():
    data = request.get_json()
    if not data or "name" not in data or "description" not in data:
        return jsonify({"error": "Missing required fields"}), 400

    name = data["name"]
    description = data["description"]
    location = data.get("location", "Unknown")

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('INSERT INTO items (name, description, location) VALUES (?, ?, ?)', (name, description, location))
    conn.commit()
    item_id = c.lastrowid
    conn.close()

    return jsonify({
        "message": "Item reported successfully",
        "item": {"id": item_id, "name": name, "description": description, "location": location, "status": "Lost"}
    }), 201

# API: Search lost items
@app.route('/search', methods=['GET'])
def search_item():
    keyword = request.args.get('q', '').lower()
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT * FROM items WHERE LOWER(name) LIKE ? OR LOWER(description) LIKE ?', (f'%{keyword}%', f'%{keyword}%'))
    rows = c.fetchall()
    conn.close()
    results = [{"id": r[0], "name": r[1], "description": r[2], "location": r[3], "status": r[4]} for r in rows]
    return jsonify({"keyword": keyword, "results": results})

# Admin dashboard
@app.route('/admin')
def admin_dashboard():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT * FROM items')
    rows = c.fetchall()
    conn.close()
    items = [{"id": r[0], "name": r[1], "description": r[2], "location": r[3], "status": r[4]} for r in rows]

    template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Admin Dashboard - Lost & Found</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: center; }
            th { background-color: #f2f2f2; }
            a { text-decoration: none; color: white; padding: 5px 10px; border-radius: 3px; }
            .found { background-color: green; }
            .delete { background-color: red; }
        </style>
    </head>
    <body>
    <h1>Lost & Found Admin Dashboard</h1>
    <table>
        <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Description</th>
            <th>Location</th>
            <th>Status</th>
            <th>Actions</th>
        </tr>
        {% for item in items %}
        <tr>
            <td>{{ item.id }}</td>
            <td>{{ item.name }}</td>
            <td>{{ item.description }}</td>
            <td>{{ item.location }}</td>
            <td>{{ item.status }}</td>
            <td>
                {% if item.status != 'Found' %}
                <a class="found" href="{{ url_for('mark_found', item_id=item.id) }}">Mark Found</a>
                {% endif %}
                <a class="delete" href="{{ url_for('delete_item', item_id=item.id) }}">Delete</a>
            </td>
        </tr>
        {% endfor %}
    </table>
    </body>
    </html>
    """
    return render_template_string(template, items=items)

# Admin: mark as found
@app.route('/admin/found/<int:item_id>')
def mark_found(item_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('UPDATE items SET status = "Found" WHERE id = ?', (item_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_dashboard'))

# Admin: delete item
@app.route('/admin/delete/<int:item_id>')
def delete_item(item_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('DELETE FROM items WHERE id = ?', (item_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_dashboard'))

# Run the app
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
