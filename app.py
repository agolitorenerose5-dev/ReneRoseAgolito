from flask import Flask, jsonify, request, redirect, url_for, render_template_string
import sqlite3
import os

app = Flask(__name__)
DB_NAME = 'lost_found.db'

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

# --- HTML TEMPLATES ---

BASE_STYLES = """
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
<style>
    body { background-color: #f8f9fa; }
    .navbar { background-color: #0d6efd; }
    .card { border: none; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .badge-lost { background-color: #dc3545; }
    .badge-found { background-color: #198754; }
</style>
"""

NAVBAR = """
<nav class="navbar navbar-expand-lg navbar-dark mb-4">
    <div class="container">
        <a class="navbar-brand fw-bold" href="/">Campus Lost & Found</a>
        <div class="navbar-nav ms-auto">
            <a class="nav-link text-white" href="/admin">Admin Dashboard</a>
        </div>
    </div>
</nav>
"""

# --- ROUTES ---

@app.route('/')
def home():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT * FROM items WHERE status = "Lost" ORDER BY id DESC')
    items = c.fetchall()
    conn.close()

    template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Home - Lost & Found</title>
        {BASE_STYLES}
    </head>
    <body>
        {NAVBAR}
        <div class="container">
            <div class="row">
                <div class="col-md-4">
                    <div class="card p-4 mb-4">
                        <h4 class="mb-3">Report Lost Item</h4>
                        <form action="/report-ui" method="POST">
                            <div class="mb-3">
                                <label class="form-label">Item Name</label>
                                <input type="text" name="name" class="form-control" placeholder="e.g. Blue Umbrella" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Location Lost</label>
                                <input type="text" name="location" class="form-control" placeholder="e.g. Library 2nd Floor">
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Description</label>
                                <textarea name="description" class="form-control" rows="3" required></textarea>
                            </div>
                            <button type="submit" class="btn btn-primary w-100">Post Report</button>
                        </form>
                    </div>
                </div>

                <div class="col-md-8">
                    <h4 class="mb-3">Recent Lost Items</h4>
                    {% if not items %}
                        <div class="alert alert-info">No items reported lost yet.</div>
                    {% endif %}
                    <div class="row">
                        {{% for item in items %}}
                        <div class="col-md-6 mb-3">
                            <div class="card h-100">
                                <div class="card-body">
                                    <span class="badge badge-lost mb-2">LOST</span>
                                    <h5 class="card-title">{{{{ item[1] }}}}</h5>
                                    <p class="card-text text-muted small"><strong>Location:</strong> {{{{ item[3] }}}}</p>
                                    <p class="card-text">{{{{ item[2] }}}}</p>
                                </div>
                            </div>
                        </div>
                        {{% endfor %}}
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return render_template_string(template, items=items)

# Helper route for the UI form
@app.route('/report-ui', methods=['POST'])
def report_ui():
    name = request.form.get('name')
    description = request.form.get('description')
    location = request.form.get('location', 'Unknown')

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('INSERT INTO items (name, description, location) VALUES (?, ?, ?)', (name, description, location))
    conn.commit()
    conn.close()
    return redirect(url_for('home'))

@app.route('/admin')
def admin_dashboard():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT * FROM items ORDER BY id DESC')
    items = c.fetchall()
    conn.close()

    template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Admin - Lost & Found</title>
        {BASE_STYLES}
    </head>
    <body>
        {NAVBAR}
        <div class="container">
            <h2 class="mb-4">Admin Management</h2>
            <div class="card">
                <table class="table table-hover mb-0">
                    <thead class="table-light">
                        <tr>
                            <th>ID</th>
                            <th>Item</th>
                            <th>Location</th>
                            <th>Status</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {{% for item in items %}}
                        <tr>
                            <td>{{{{ item[0] }}}}</td>
                            <td><strong>{{{{ item[1] }}}}</strong><br><small>{{{{ item[2] }}}}</small></td>
                            <td>{{{{ item[3] }}}}</td>
                            <td>
                                <span class="badge {{{{ 'badge-found' if item[4] == 'Found' else 'badge-lost' }}}}">
                                    {{{{ item[4] }}}}
                                </span>
                            </td>
                            <td>
                                {{% if item[4] != 'Found' %}}
                                <a href="/admin/found/{{{{ item[0] }}}}" class="btn btn-sm btn-success">Mark Found</a>
                                {{% endif %}}
                                <a href="/admin/delete/{{{{ item[0] }}}}" class="btn btn-sm btn-danger" onclick="return confirm('Delete this report?')">Delete</a>
                            </td>
                        </tr>
                        {{% endfor %}}
                    </tbody>
                </table>
            </div>
        </div>
    </body>
    </html>
    """
    return render_template_string(template, items=items)

# (Existing mark_found and delete_item routes go here...)
@app.route('/admin/found/<int:item_id>')
def mark_found(item_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('UPDATE items SET status = "Found" WHERE id = ?', (item_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete/<int:item_id>')
def delete_item(item_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('DELETE FROM items WHERE id = ?', (item_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
