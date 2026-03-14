import os
import psycopg2
from flask import Flask, render_template_string, request, redirect, url_for, session

app = Flask(__name__)
# CRITICAL: Change this to a random string for security
app.secret_key = 'super_secret_key_change_me' 

# --- Admin Credentials (Hardcoded for simplicity) ---
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123" 

def get_db_connection():
    db_url = os.environ.get('DATABASE_URL')
    return psycopg2.connect(db_url)

# --- NEW: LOGIN HTML ---
LOGIN_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <title>Admin Login</title>
</head>
<body class="bg-light d-flex align-items-center" style="height: 100vh;">
    <div class="container">
        <div class="row justify-content-center">
            <div class="col-md-4">
                <div class="card p-4 shadow border-0">
                    <h3 class="fw-bold text-center mb-4">Admin Login</h3>
                    {% if error %}
                        <div class="alert alert-danger p-2 small">{{ error }}</div>
                    {% endif %}
                    <form method="POST">
                        <div class="mb-3">
                            <label class="form-label">Username</label>
                            <input type="text" name="username" class="form-control" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Password</label>
                            <input type="password" name="password" class="form-control" required>
                        </div>
                        <button type="submit" class="btn btn-dark w-100">Login</button>
                    </form>
                    <div class="text-center mt-3">
                        <a href="/" class="text-muted small">← Back to Home</a>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""

# --- (Keep your HOME_HTML and ADMIN_HTML variables from the previous step) ---

@app.route('/')
def home():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM items WHERE status = 'Lost' ORDER BY id DESC")
    items = c.fetchall()
    c.close(); conn.close()
    return render_template_string(HOME_HTML, items=items)

# --- UPDATED ADMIN ROUTE WITH LOGIN ---
@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    error = None
    if request.method == 'POST':
        user = request.form.get('username')
        pw = request.form.get('password')
        
        if user == ADMIN_USERNAME and pw == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            error = "Invalid credentials. Try again."
            
    return render_template_string(LOGIN_HTML, error=error)

@app.route('/dashboard')
def admin_dashboard():
    # Check if user is actually logged in
    if not session.get('logged_in'):
        return redirect(url_for('admin_login'))
        
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM items ORDER BY id DESC")
    items = c.fetchall()
    c.close(); conn.close()
    return render_template_string(ADMIN_HTML, items=items)

@app.route('/admin/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('home'))

# --- (Keep your report-ui, mark_found, and delete_item routes) ---

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
