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

# --- HOME TEMPLATE (Enhanced Size) ---
HOME_HTML = """
<!DOCTYPE html>
<html>
<head>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <title>Campus Lost & Found</title>
    <style>
        body { background-color: #f0f2f5; }
        .navbar { background: #0d6efd; padding: 1.5rem; }
        /* Larger Form Section */
        .report-card { border-radius: 15px; padding: 2.5rem !important; }
        .report-card h3 { font-size: 2rem; margin-bottom: 1.5rem; color: #333; }
        .form-control { padding: 0.8rem; font-size: 1.1rem; margin-bottom: 1rem; }
        /* Larger Item Cards */
        .item-card { border-radius: 15px; padding: 2rem !important; border-left: 8px solid #dc3545; }
        .item-card h4 { font-size: 1.8rem; font-weight: 800; color: #1a1a1a; }
        .badge-lost { font-size: 1rem; padding: 0.5rem 1rem; margin-bottom: 1rem; display: inline-block; }
        .location-text { font-size: 1.2rem; color: #444; }
        .desc-text { font-size: 1.1rem; color: #666; }
    </style>
</head>
<body>
    <nav class="navbar navbar-dark mb-5 shadow">
        <div class="container">
            <a class="navbar-brand fw-bold fs-2" href="/">📍 Campus Lost & Found</a>
            <a href="/admin" class="btn btn-outline-light">Admin Portal</a>
        </div>
    </nav>

    <div class="container">
        <div class="row g-5">
            <div class="col-lg-5">
                <div class="card report-card shadow border-0">
                    <h3 class="fw-bold">Report Lost Item</h3>
                    <p class="text-muted mb-4">Provide details to help return your item.</p>
                    <form action="/report-ui" method="POST">
                        <label class="fw-bold small mb-1">ITEM NAME</label>
                        <input type="text" name="name" class="form-control" placeholder="What did you lose?" required>
                        
                        <label class="fw-bold small mb-1">LOCATION SEEN</label>
                        <input type="text" name="loc" class="form-control" placeholder="e.g. Science Wing Library">
                        
                        <label class="fw-bold small mb-1">DESCRIPTION</label>
                        <textarea name="desc" class="form-control" rows="4" placeholder="Color, brand, or unique marks..." required></textarea>
                        
                        <button type="submit" class="btn btn-primary btn-lg w-100 fw-bold mt-2 py-3">Post to Board Now</button>
                    </form>
                </div>
            </div>

            <div class="col-lg-7">
                <h2 class="fw-bold mb-4">Active Lost Reports</h2>
                <div class="row">
                    {% if not items %}
                        <div class="text-center mt-5">
                            <h4 class="text-muted">No items currently on the board.</h4>
                        </div>
                    {% endif %}
                    {% for item in items if item[4] == 'Lost' %}
                    <div class="col-12 mb-4">
                        <div class="card item-card shadow-sm border-0 bg-white">
                            <span class="badge bg-danger badge-lost">LOST REPORT</span>
                            <h4 class="mb-2">{{ item[1] }}</h4>
                            <p class="location-text fw-semibold mb-2">📍 {{ item[3] }}</p>
                            <p class="desc-text">{{ item[2] }}</p>
                            <div class="mt-3 text-muted border-top pt-2 small">
                                Report ID: #{{ item[0] }}
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
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM items ORDER BY id DESC")
    items = c.fetchall()
    c.close(); conn.close()
    return render_template_string(HOME_HTML, items=items)

# Fixed report route to ensure status is set to 'Lost'
@app.route('/report-ui', methods=['POST'])
def report():
    n = request.form.get('name')
    l = request.form.get('loc', 'Not specified')
    d = request.form.get('desc')
    
    conn = get_db_connection()
    c = conn.cursor()
    # Explicitly inserting 'Lost' as the 4th index value
    c.execute("INSERT INTO items (name, description, location, status) VALUES (%s, %s, %s, 'Lost')", (n, d, l))
    conn.commit()
    c.close(); conn.close()
    return redirect(url_for('home'))

# ... (rest of your admin routes remain the same) ...

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
