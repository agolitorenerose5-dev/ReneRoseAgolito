from flask import Flask, jsonify, request, redirect, url_for, render_template_string
import sqlite3
import os

app = Flask(_name_)
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

# --- CSS & JS Components (Reusable) ---
BASE_HEAD = """
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
<style>
    body { background-color: #f4f7f6; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    .navbar { background-color: #2c3e50; }
    .card { border: none; border-radius: 12px; transition: 0.3s; }
    .card:hover { transform: translateY(-5px); box-shadow: 0 10px 20px rgba(0,0,0,0.1); }
    .btn-primary { background-color: #3498db; border: none; }
    .badge-lost { background-color: #e74c3c; }
    .badge-found { background-color: #2ecc71; }
</style>
"""

NAVBAR = """
<nav class="navbar navbar-expand-lg navbar-dark mb-4">
    <div class="container">
        <a class="navbar-brand fw-bold" href="/">📍 Campus Lost & Found</a>
        <div class="navbar-nav ms-auto">
            <a class="nav-link btn btn-outline-light btn-sm px-3" href="/admin">Admin Login</a>
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
        <title>Home | Campus Lost & Found</title>
        {BASE_HEAD}
    </head>
    <body>
        {NAVBAR}
        <div class="container">
            <div class="row">
                <div class="col-md-4">
                    <div class="card p-4 shadow-sm mb-4">
                        <h4 class="fw-bold text-dark">Report an Item</h4>
                        <p class="text-muted small">Help your fellow students find their belongings.</p>
                        <hr>
                        <form action="/report-ui" method="POST">
                            <div class="mb-3">
                                <label class="form-label fw-semibold">What did you lose?</label>
                                <input type="text" name="name" class="form-control" placeholder="e.g. Mechanical Pencil" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label fw-semibold">Where was it last seen?</label>
                                <input type="text" name="location" class="form-control" placeholder="e.g. IT Building Room 102">
                            </div>
                            <div class="mb-3">
                                <label class="form-label fw-semibold">Description</label>
                                <textarea name="description" class="form-control" rows="3" placeholder="Colors, brand, or unique marks..." required></textarea>
                            </div>
                            <button type="submit" class="btn btn-primary w-100 fw-bold">Post to Board</button>
                        </form>
                    </div>
                </div>

                <div class="col-md-8">
                    <h3 class="fw-bold mb-4">Active Lost Reports</h3>
                    <div class="row">
                        {{% if not items %}}
                            <div class="col-12">
                                <div class="alert alert-light border text-center py-5">
                                    <h5 class="text-muted">No items reported lost yet. Check back later!</h5>
                                </div>
                            </div>
                        {{% endif %}}
                        
                        {{% for item in items %}}
                        <div class="col-md-6 mb-4">
                            <div class="card h-100 shadow-sm">
                                <div class="card-body">
                                    <span class="badge badge-lost mb-2">LOST</span>
                                    <h5 class="card-title fw-bold text-primary text-capitalize">{{{{ item[1] }}}}</h5>
                                    <p class="mb-1 text-muted small"><strong>📍 Location:</strong> {{{{ item[3] }}}}</p>
                                    <p class="card-text text-secondary mt-2">{{{{ item[2] }}}}</p>
                                </div>
                                <div class="card-footer bg-white border-0">
                                    <small class="text-muted">Reported ID: #{{{{ item[0] }}}}</small>
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

@app.route('/report-ui', methods=['POST'])
def report_ui():
    name = request.form.get('name')
    description = request.form.get('description')
    location = request.form.get('location', 'Not Specified')

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
        <title>Admin Dashboard</title>
        {BASE_HEAD}
    </head>
    <body>
        {NAVBAR}
        <div class="container">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h2 class="fw-bold">System Management</h2>
                <span class="badge bg-dark">Total Items: {{{{ items|length }}}}</span>
            </div>
            <div class="card shadow-sm">
                <div class="table-responsive">
                    <table class="table table-hover align-middle mb-0">
                        <thead class="table-dark">
                            <tr>
                                <th>ID</th>
                                <th>Item Details</th>
                                <th>Location</th>
                                <th>Status</th>
                                <th class="text-center">Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {{% for item in items %}}
                            <tr>
                                <td class="text-muted">#{{{{ item[0] }}}}</td>
                                <td>
                                    <div class="fw-bold">{{{{ item[1] }}}}</div>
                                    <small class="text-secondary">{{{{ item[2] }}}}</small>
                                </td>
                                <td>{{{{ item[3] }}}}</td>
                                <td>
                                    <span class="badge {{{{ 'badge-found' if item[4] == 'Found' else 'badge-lost' }}}}">
                                        {{{{ item[4] }}}}
                                    </span>
                                </td>
                                <td class="text-center">
                                    <div class="btn-group">
                                        {{% if item[4] != 'Found' %}}
                                        <a href="/admin/found/{{{{ item[0] }}}}" class="btn btn-sm btn-success px-3">Mark Found</a>
                                        {{% endif %}}
                                        <a href="/admin/delete/{{{{ item[0] }}}}" class="btn btn-sm btn-outline-danger" onclick="return confirm('Permanently delete this record?')">Delete</a>
                                    </div>
                                </td>
                            </tr>
                            {{% endfor %}}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return render_template_string(template, items=items)

# --- Functional Routes for Admin ---
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

if _name_ == '_main_':
    app.run(debug=True, port=5000)
cdn.jsdelivr.net
