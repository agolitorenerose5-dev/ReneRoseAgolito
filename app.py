import os
import psycopg2
from flask import Flask, render_template_string, request, redirect, url_for

app = Flask(__name__)

# --- Database Connection Logic ---
def get_db_connection():
    # Render provides 'DATABASE_URL' automatically if linked, 
    # or you can add it in Environment Variables.
    db_url = os.environ.get('DATABASE_URL')
    conn = psycopg2.connect(db_url)
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    # PostgreSQL uses SERIAL for auto-incrementing IDs
    c.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            location TEXT,
            status TEXT DEFAULT 'Lost'
        )
    ''')
    conn.commit()
    c.close()
    conn.close()

# Initialize the database table on startup
try:
    init_db()
except Exception as e:
    print(f"Database init error: {e}")

# --- UI Components ---
BASE_HEAD = """
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
<style>
    body { background-color: #f4f7f6; font-family: 'Segoe UI', Tahoma, sans-serif; }
    .navbar { background-color: #2c3e50; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    .card { border: none; border-radius: 12px; transition: 0.3s; }
    .card:hover { transform: translateY(-5px); box-shadow: 0 10px 20px rgba(0,0,0,0.1); }
    .btn-primary { background-color: #3498db; border: none; }
    .badge-lost { background-color: #e74c3c; color: white; padding: 5px 10px; border-radius: 6px; font-size: 0.75rem; }
    .badge-found { background-color: #2ecc71; color: white; padding: 5px 10px; border-radius: 6px; font-size: 0.75rem; }
</style>
"""

NAVBAR = """
<nav class="navbar navbar-expand-lg navbar-dark mb-4">
    <div class="container">
        <a class="navbar-brand fw-bold" href="/">📍 Campus Lost & Found</a>
        <div class="navbar-nav ms-auto">
            <a class="nav-link btn btn-outline-light btn-sm px-3" href="/admin">Admin Dashboard</a>
        </div>
    </div>
</nav>
"""

# --- ROUTES ---

@app.route('/')
def home():
    conn = get_db_connection()
    c = conn.cursor()
    # PostgreSQL uses %s as placeholders
    c.execute('SELECT * FROM items WHERE status = %s ORDER BY id DESC', ('Lost',))
    items = c.fetchall()
    c.close()
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
                        <p class="text-muted small">Help others find their belongings.</p>
                        <hr>
                        <form action="/report-ui" method="POST">
                            <div class="mb-3">
                                <label class="form-label fw-semibold">Item Name</label>
                                <input type="text" name="name" class="form-control" placeholder="e.g. Blue Wallet" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label fw-semibold">Last Seen At</label>
                                <input type="text" name="location" class="form-control" placeholder="e.g. Library 2nd Floor">
                            </div>
                            <div class="mb-3">
                                <label class="form-label fw-semibold">Description</label>
                                <textarea name="description" class="form-control" rows="3" placeholder="Any unique marks..." required></textarea>
                            </div>
                            <button type="submit" class="btn btn-primary w-100 fw-bold">Post Report</button>
                        </form>
                    </div>
                </div>

                <div class="col-md-8">
                    <h3 class="fw-bold mb-4">Active Lost Reports</h3>
                    <div class="row">
                        {{% if not items %}}
                            <div class="col-12 text-center py-5 border rounded bg-white">
                                <h5 class="text-muted">No active reports. Everything is found!</h5>
                            </div>
                        {{% endif %}}
                        
                        {{% for item in items %}}
                        <div class="col-md-6 mb-4">
                            <div class="card h-100 shadow-sm">
                                <div class="card-body">
                                    <span class="badge-lost mb-2 d-inline-block">LOST</span>
                                    <h5 class="card-title fw-bold text-primary">{{{{ item[1] }}}}</h5>
                                    <p class="mb-1 text-muted small"><strong>📍 Location:</strong> {{{{ item[3] }}}}</p>
                                    <p class="card-text text-secondary mt-2">{{{{ item[2] }}}}</p>
                                </div>
                                <div class="card-footer bg-white border-0">
                                    <small class="text-muted">Report ID: #{{{{ item[0] }}}}</small>
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
    """.replace('{{%', '{%').replace('%}}', '%}').replace('{{{{', '{{').replace('}}}}', '}}')
    return render_template_string(template, items=items)

@app.route('/report-ui', methods=['POST'])
def report_ui():
    name = request.form.get('name')
    description = request.form.get('description')
    location = request.form.get('location', 'Not Specified')

    conn = get_db_connection()
    c = conn.cursor()
    c.execute('INSERT INTO items (name, description, location) VALUES (%s, %s, %s)', (name, description, location))
    conn.commit()
    c.close()
    conn.close()
    return redirect(url_for('home'))

@app.route('/admin')
def admin_dashboard():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM items ORDER BY id DESC')
    items = c.fetchall()
    c.close()
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
            <h2 class="fw-bold mb-4">System Management</h2>
            <div class="card shadow-sm overflow-hidden">
                <table class="table table-hover align-middle mb-0">
                    <thead class="table-dark">
                        <tr>
                            <th>ID</th><th>Item Details</th><th>Location</th><th>Status</th><th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {{% for item in items %}}
                        <tr>
                            <td class="text-muted">#{{{{ item[0] }}}}</td>
                            <td>
                                <strong>{{{{ item[1] }}}}</strong><br>
                                <small class="text-muted">{{{{ item[2] }}}}</small>
                            </td>
                            <td>{{{{ item[3] }}}}</td>
                            <td>
                                <span class="{{{{ 'badge-found' if item[4] == 'Found' else 'badge-lost' }}}}">
                                    {{{{ item[4] }}}}
                                </span>
                            </td>
                            <td>
                                {{% if item[4] != 'Found' %}}
                                <a href="/admin/found/{{{{ item[0] }}}}" class="btn btn-sm btn-success">Mark Found</a>
                                {{% endif %}}
                                <a href="/admin/delete/{{{{
