import os
import psycopg2
from flask import Flask, render_template_string, request, redirect, url_for

app = Flask(__name__)

def get_db_connection():
    db_url = os.environ.get('DATABASE_URL')
    return psycopg2.connect(db_url)

# --- HOME TEMPLATE ---
HOME_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <title>Campus Lost & Found</title>
    <style>
        body { background-color: #f8f9fa; }
        .navbar { background-color: #2c3e50; }
        .badge-lost { background-color: #e74c3c; color: white; padding: 5px 12px; border-radius: 50px; font-size: 0.75rem; }
    </style>
</head>
<body>
    <nav class="navbar navbar-dark p-3 mb-4">
        <div class="container">
            <a class="navbar-brand fw-bold" href="/">📍 Campus Lost & Found</a>
            <a class="btn btn-outline-light btn-sm" href="/admin">Admin Login</a>
        </div>
    </nav>
    <div class="container">
        <div class="row">
            <div class="col-md-4 mb-4">
                <div class="card p-4 shadow-sm border-0">
                    <h4 class="fw-bold">Report Item</h4>
                    <form action="/report-ui" method="POST">
                        <div class="mb-3"><label class="form-label">Item Name</label><input type="text" name="name" class="form-control" required></div>
                        <div class="mb-3"><label class="form-label">Location</label><input type="text" name="location" class="form-control"></div>
                        <div class="mb-3"><label class="form-label">Description</label><textarea name="description" class="form-control" required></textarea></div>
                        <button type="submit" class="btn btn-primary w-100">Post</button>
                    </form>
                </div>
            </div>
            <div class="col-md-8">
                <h3 class="fw-bold mb-4">Active Lost Reports</h3>
                <div class="row">
                    {% for item in items %}
                    <div class="col-md-6 mb-4">
                        <div class="card p-3 shadow-sm border-0">
                            <div><span class="badge-lost">LOST</span></div>
                            <h5 class="fw-bold text-primary mt-2">{{ item[1] }}</h5>
                            <p class="mb-1 text-muted small">📍 {{ item[3] }}</p>
                            <p class="text-secondary small">{{ item[2] }}</p>
                        </div>
                    </div>
                    {% endfor %}
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""

# --- ADMIN TEMPLATE ---
ADMIN_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <title>Admin Dashboard</title>
</head>
<body class="bg-light">
    <nav class="navbar navbar-dark bg-dark p-3 mb-4">
        <div class="container">
            <a class="navbar-brand" href="/">← Back to Public Board</a>
            <span class="navbar-text text-white">Admin Management</span>
        </div>
    </nav>
    <div class="container">
        <div class="card shadow-sm border-0">
            <table class="table align-middle mb-0">
                <thead class="table-light">
                    <tr><th>ID</th><th>Item</th><th>Status</th><th>Actions</th></tr>
                </thead>
                <tbody>
                    {% for item in items %}
                    <tr>
                        <td>#{{ item[0] }}</td>
                        <td><strong>{{ item[1] }}</strong><br><small class="text-muted">{{ item[3] }}</small></td>
                        <td><span class="badge {{ 'bg-success' if item[4] == 'Found' else 'bg-danger' }}">{{ item[4] }}</span></td>
                        <td>
                            {% if item[4] != 'Found' %}
                            <a href="/admin/found/{{ item[0] }}" class="btn btn-sm btn-success">Mark Found</a>
                            {% endif %}
                            <a href="/admin/delete/{{ item[0] }}" class="btn btn-sm btn-outline-danger">Delete</a>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM items WHERE status = 'Lost' ORDER BY id DESC")
    items = c.fetchall()
    c.close()
    conn.close()
    return render_template_string(HOME_HTML, items=items)

@app.route('/admin')
def admin_dashboard():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM items ORDER BY id DESC")
    items = c.fetchall()
    c.close()
    conn.close()
    return render_template_string(ADMIN_HTML, items=items)

@app.route('/report-ui', methods=['POST'])
def report_ui():
    name, desc, loc = request.form.get('name'), request.form.get('description'), request.form.get('location')
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("INSERT INTO items (name, description, location) VALUES (%s, %s, %s)", (name, desc, loc))
    conn.commit()
    c.close(); conn.close()
    return redirect(url_for('home'))

@app.route('/admin/found/<int:item_id>')
def mark_found(item_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("UPDATE items SET status = 'Found' WHERE id = %s", (item_id,))
    conn.commit()
    c.close(); conn.close()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete/<int:item_id>')
def delete_item(item_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("DELETE FROM items WHERE id = %s", (item_id,))
    conn.commit()
    c.close(); conn.close()
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
