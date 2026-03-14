import os
import psycopg2
from flask import Flask, render_template_string, request, redirect, url_for

app = Flask(__name__)

def get_db_connection():
    # This pulls the database URL from Render's environment variables
    db_url = os.environ.get('DATABASE_URL')
    return psycopg2.connect(db_url)

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
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

try:
    init_db()
except Exception as e:
    print(f"Database error: {e}")

# --- UI Styles ---
BASE_HEAD = """
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
<style>
    body { background-color: #f8f9fa; font-family: sans-serif; }
    .navbar { background-color: #2c3e50; }
    .card { border-radius: 10px; border: none; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .badge-lost { background-color: #dc3545; color: white; padding: 5px 10px; border-radius: 5px; font-size: 0.8rem; }
</style>
"""

# --- HOME ROUTE ---
@app.route('/')
def home():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM items WHERE status = %s ORDER BY id DESC', ('Lost',))
    items = c.fetchall()
    c.close()
    conn.close()

    # The string below uses double curly braces {{ }} which Flask will now read correctly
    template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        {BASE_HEAD}
        <title>Campus Lost & Found</title>
    </head>
    <body>
        <nav class="navbar navbar-dark mb-4 p-3">
            <div class="container">
                <a class="navbar-brand fw-bold" href="/">📍 Campus Lost & Found</a>
            </div>
        </nav>
        <div class="container">
            <div class="row">
                <div class="col-md-4">
                    <div class="card p-4">
                        <h4 class="fw-bold">Report an Item</h4>
                        <form action="/report-ui" method="POST">
                            <div class="mb-3">
                                <label class="form-label">What did you lose?</label>
                                <input type="text" name="name" class="form-control" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Location</label>
                                <input type="text" name="location" class="form-control">
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Description</label>
                                <textarea name="description" class="form-control" required></textarea>
                            </div>
                            <button type="submit" class="btn btn-primary w-100">Post to Board</button>
                        </form>
                    </div>
                </div>
                <div class="col-md-8">
                    <h3 class="fw-bold mb-4">Active Lost Reports</h3>
                    <div class="row">
                        {{% for item in items %}}
                        <div class="col-md-6 mb-4">
                            <div class="card p-3">
                                <span class="badge-lost mb-2" style="width: fit-content;">LOST</span>
                                <h5 class="fw-bold text-primary">{{ item[1] }}</h5>
                                <p class="mb-1 text-muted">📍 {{ item[3] }}</p>
                                <p class="small text-secondary">{{ item[2] }}</p>
                                <hr>
                                <small class="text-muted">ID: #{{ item[0] }}</small>
                            </div>
                        </div>
                        {{% endfor %}}
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """.replace('{{%', '{%').replace('%++%', '%}').replace('{{', '{{').replace('}}', '}}')
    
    # Cleaning up the template string to ensure no extra braces remain
    final_template = template.replace('{{%', '{%').replace('%}}', '%}')
    return render_template_string(final_template, items=items)

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

# (Rest of admin routes follow the same pattern)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
