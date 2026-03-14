import os
import psycopg2
from flask import Flask, render_template_string, request, redirect, url_for, session

app = Flask(__name__)

# This key is required for sessions (login). 
# On Render, it's best to set this as an Environment Variable.
app.secret_key = os.environ.get('SECRET_KEY', 'dev_key_123')

# --- Admin Credentials ---
ADMIN_USER = os.environ.get('ADMIN_USER', 'admin')
ADMIN_PASS = os.environ.get('ADMIN_PASS', 'password123')

def get_db_connection():
    db_url = os.environ.get('DATABASE_URL')
    return psycopg2.connect(db_url)

# --- HTML TEMPLATES ---

LOGIN_HTML = """
<!DOCTYPE html>
<html>
<head>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <title>Admin Login</title>
</head>
<body class="bg-light d-flex align-items-center" style="height: 100vh;">
    <div class="container col-md-4">
        <div class="card p-4 shadow-sm border-0">
            <h4 class="fw-bold mb-3 text-center">Admin Login</h4>
            {% if error %}<div class="alert alert-danger small">{{ error }}</div>{% endif %}
            <form method="POST">
                <div class="mb-3"><label class="small fw-bold">USERNAME</label><input type="text" name="user" class="form-control" required></div>
                <div class="mb-3"><label class="small fw-bold">PASSWORD</label><input type="password" name="pass" class="form-control" required></div>
                <button type="submit" class="btn btn-dark w-100">Login</button>
            </form>
            <a href="/" class="text-center d-block mt-3 text-muted small">← Back to Board</a>
        </div>
    </div>
</body>
</html>
"""

ADMIN_HTML = """
<!DOCTYPE html>
<html>
<head>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <title>Admin Dashboard</title>
</head>
<body class="bg-light">
    <nav class="navbar navbar-dark bg-dark mb-4 p-3">
        <div class="container">
            <a class="navbar-brand" href="/">📍 Campus Lost & Found</a>
            <a href="/logout" class="btn btn-outline-light btn-sm">Logout</a>
        </div>
    </nav>
    <div class="container">
        <div class="card shadow-sm overflow-hidden">
            <table class="table table-hover align-middle mb-0">
                <thead class="table-dark">
                    <tr><th>ID</th><th>Item</th><th>Location</th><th>Status</th><th>Actions</th></tr>
                </thead>
                <tbody>
                    {% for item in items %}
                    <tr>
                        <td>#{{ item[0] }}</td>
                        <td><strong>{{ item[1] }}</strong><br><small>{{ item[2] }}</small></td>
                        <td>{{ item[3] }}</td>
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

# (Include your HOME_HTML here without the 'f' prefix)
HOME_HTML = """
<!DOCTYPE html>
<html>
<head>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <title>Lost & Found</title>
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
                        <input type="text" name="name" class="form-control mb-2" placeholder="Item Name" required>
                        <input type="text" name="loc" class="form-control mb-2" placeholder="Location Seen">
                        <textarea name="desc" class="form-control mb-3" placeholder="Description" required></textarea>
                        <button type="submit" class="btn btn-primary w-100">Post to Board</button>
                    </form>
                </div>
            </div>
            <div class="col-md-8">
                <div class="row">
                    {% for item in items if item[4] == 'Lost' %}
                    <div class="col-md-6 mb-3">
                        <div class="card p-3 border-0 shadow-sm">
                            <span class="text-danger small fw-bold">LOST</span>
                            <h5 class="fw-bold">{{ item[1] }}</h5>
                            <p class="small text-muted mb-1">📍 {{ item[3] }}</p>
                            <p class="small">{{ item[2] }}</p>
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

# --- ROUTES ---

@app.route('/')
def home():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM items ORDER BY id DESC")
    items = c.fetchall()
    c.close(); conn.close()
    return render_template_string(HOME_HTML, items=items)

@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    error = None
    if request.method == 'POST':
        if request.form['user'] == ADMIN_USER and request.form['pass'] == ADMIN_PASS:
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        error = "Invalid Credentials"
    return render_template_string(LOGIN_HTML, error=error)

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('admin_login'))
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM items ORDER BY id DESC")
    items = c.fetchall()
    c.close(); conn.close()
    return render_template_string(ADMIN_HTML, items=items)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/report-ui', methods=['POST'])
def report():
    n, l, d = request.form['name'], request.form['loc'], request.form['desc']
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("INSERT INTO items (name, location, description) VALUES (%s, %s, %s)", (n, l, d))
    conn.commit()
    c.close(); conn.close()
    return redirect(url_for('home'))

@app.route('/admin/found/<int:id>')
def found(id):
    if not session.get('logged_in'): return redirect(url_for('admin_login'))
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("UPDATE items SET status = 'Found' WHERE id = %s", (id,))
    conn.commit(); c.close(); conn.close()
    return redirect(url_for('dashboard'))

@app.route('/admin/delete/<int:id>')
def delete(id):
    if not session.get('logged_in'): return redirect(url_for('admin_login'))
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("DELETE FROM items WHERE id = %s", (id,))
    conn.commit(); c.close(); conn.close()
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
