import os
import psycopg2
from flask import Flask, render_template_string, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev_key_123')

ADMIN_USER = os.environ.get('ADMIN_USER', 'admin')
ADMIN_PASS = os.environ.get('ADMIN_PASS', 'password123')

def get_db_connection():
    db_url = os.environ.get('DATABASE_URL')
    return psycopg2.connect(db_url)

# --- HOME TEMPLATE ---
# I removed the 'if item[4] == Lost' filter here and moved it to the SQL query 
# for better performance and to ensure the board displays correctly.
HOME_HTML = """
<!DOCTYPE html>
<html>
<head>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <title>Campus Lost & Found</title>
</head>
<body class="bg-light">
    <nav class="navbar navbar-dark bg-primary mb-4 p-3">
        <div class="container">
            <a class="navbar-brand fw-bold" href="/">📍 Campus Lost & Found</a>
            <a href="/admin" class="btn btn-light btn-sm">Admin Access</a>
        </div>
    </nav>
    <div class="container">
        <div class="row">
            <div class="col-md-4">
                <div class="card p-4 shadow-sm border-0 mb-4">
                    <h5 class="fw-bold">Report Lost Item</h5>
                    <form action="/report-ui" method="POST">
                        <input type="text" name="name" class="form-control mb-2" placeholder="Item Name (e.g. Blue Wallet)" required>
                        <input type="text" name="loc" class="form-control mb-2" placeholder="Where was it seen?">
                        <textarea name="desc" class="form-control mb-3" placeholder="Description / Details" required></textarea>
                        <button type="submit" class="btn btn-primary w-100">Post to Board</button>
                    </form>
                </div>
            </div>
            <div class="col-md-8">
                <h3 class="fw-bold mb-4">Active Lost Reports</h3>
                <div class="row">
                    {% if not items %}
                        <div class="col-12 text-center py-5">
                            <p class="text-muted">No items reported lost yet. Check back later!</p>
                        </div>
                    {% endif %}
                    {% for item in items %}
                    <div class="col-md-6 mb-3">
                        <div class="card p-3 border-0 shadow-sm h-100">
                            <div class="mb-2"><span class="badge bg-danger">LOST</span></div>
                            <h5 class="fw-bold text-dark">{{ item[1] }}</h5>
                            <p class="small text-muted mb-1">📍 <strong>Location:</strong> {{ item[3] }}</p>
                            <p class="small text-secondary">{{ item[2] }}</p>
                            <hr class="my-2">
                            <small class="text-muted">ID: #{{ item[0] }}</small>
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

# (Keep your LOGIN_HTML and ADMIN_HTML from your previous snippet)

@app.route('/')
def home():
    conn = get_db_connection()
    c = conn.cursor()
    # SQL Filter: only get items where status is 'Lost' so they show on the public board
    c.execute("SELECT id, name, description, location, status FROM items WHERE status = 'Lost' ORDER BY id DESC")
    items = c.fetchall()
    c.close(); conn.close()
    return render_template_string(HOME_HTML, items=items)

@app.route('/report-ui', methods=['POST'])
def report():
    n = request.form.get('name')
    l = request.form.get('loc', 'Unknown')
    d = request.form.get('desc')
    
    conn = get_db_connection()
    c = conn.cursor()
    # Explicitly insert 'Lost' as the status to ensure it appears on the board
    c.execute("INSERT INTO items (name, location, description, status) VALUES (%s, %s, %s, 'Lost')", (n, l, d))
    conn.commit()
    c.close(); conn.close()
    return redirect(url_for('home'))

# (Keep your /admin, /dashboard, /logout, /admin/found, and /admin/delete routes)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
