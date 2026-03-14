import os
import psycopg2
from flask import Flask, render_template_string, request, redirect, url_for

app = Flask(__name__)

# --- Database Connection ---
def get_db_connection():
    # Use the DATABASE_URL provided by Render
    db_url = os.environ.get('DATABASE_URL')
    return psycopg2.connect(db_url)

# --- The HTML (NO f-strings, NO extra braces) ---
# This fixes the "curly braces showing on screen" issue.
HOME_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <title>Campus Lost & Found</title>
    <style>
        body { background-color: #f8f9fa; font-family: 'Segoe UI', sans-serif; }
        .navbar { background-color: #2c3e50; }
        .card { border-radius: 12px; border: none; box-shadow: 0 4px 10px rgba(0,0,0,0.05); }
        .badge-lost { background-color: #e74c3c; color: white; padding: 5px 12px; border-radius: 50px; font-size: 0.75rem; font-weight: bold; }
    </style>
</head>
<body>
    <nav class="navbar navbar-dark p-3 mb-4">
        <div class="container">
            <a class="navbar-brand fw-bold" href="/">📍 Campus Lost & Found</a>
            <a class="btn btn-outline-light btn-sm" href="/admin">Admin</a>
        </div>
    </nav>

    <div class="container">
        <div class="row">
            <div class="col-md-4 mb-4">
                <div class="card p-4">
                    <h4 class="fw-bold mb-3">Report an Item</h4>
                    <form action="/report-ui" method="POST">
                        <div class="mb-3">
                            <label class="form-label fw-semibold">Item Name</label>
                            <input type="text" name="name" class="form-control" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label fw-semibold">Location</label>
                            <input type="text" name="location" class="form-control">
                        </div>
                        <div class="mb-3">
                            <label class="form-label fw-semibold">Description</label>
                            <textarea name="description" class="form-control" rows="3" required></textarea>
                        </div>
                        <button type="submit" class="btn btn-primary w-100 fw-bold">Post to Board</button>
                    </form>
                </div>
            </div>

            <div class="col-md-8">
                <h3 class="fw-bold mb-4">Active Lost Reports</h3>
                <div class="row">
                    {% for item in items %}
                    <div class="col-md-6 mb-4">
                        <div class="card h-100 p-3">
                            <div><span class="badge-lost">LOST</span></div>
                            <h5 class="fw-bold text-primary mt-2">{{ item[1] }}</h5>
                            <p class="mb-1 text-muted small"><strong>Location:</strong> {{ item[3] }}</p>
                            <p class="text-secondary small">{{ item[2] }}</p>
                            <div class="mt-auto border-top pt-2">
                                <small class="text-muted">Report #{{ item[0] }}</small>
                            </div>
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
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM items WHERE status = 'Lost' ORDER BY id DESC")
        items = c.fetchall()
        c.close()
        conn.close()
        return render_template_string(HOME_HTML, items=items)
    except Exception as e:
        return f"Database Error: {str(e)}", 500

@app.route('/report-ui', methods=['POST'])
def report_ui():
    name = request.form.get('name')
    description = request.form.get('description')
    location = request.form.get('location', 'Not Specified')
    
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("INSERT INTO items (name, description, location) VALUES (%s, %s, %s)", (name, description, location))
    conn.commit()
    c.close()
    conn.close()
    return redirect(url_for('home'))

# Admin simple dashboard
@app.route('/admin')
def admin():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM items ORDER BY id DESC")
    items = c.fetchall()
    c.close()
    conn.close()
    return render_template_string(HOME_HTML, items=items)

if __name__ == '__main__':
    # Required for Render to bind to the correct port
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
