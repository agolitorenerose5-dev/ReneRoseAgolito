@app.route('/')
def home():
    # 1. Fetch data from database
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT * FROM items WHERE status = "Lost" ORDER BY id DESC')
    items = c.fetchall()
    conn.close()

    # 2. This is the HTML UI code
    template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <title>Campus Lost & Found</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body {{ background-color: #f8f9fa; }}
            .navbar {{ background-color: #2c3e50; }}
            .card {{ border-radius: 12px; border: none; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        </style>
    </head>
    <body>
        <nav class="navbar navbar-dark mb-4">
            <div class="container"><a class="navbar-brand" href="/">📍 Lost & Found</a></div>
        </nav>
        <div class="container">
            <div class="row">
                <div class="col-md-4">
                    <div class="card p-4">
                        <h4>Report Item</h4>
                        <form action="/report-ui" method="POST">
                            <input type="text" name="name" class="form-control mb-2" placeholder="Item Name" required>
                            <input type="text" name="location" class="form-control mb-2" placeholder="Location">
                            <textarea name="description" class="form-control mb-2" placeholder="Description" required></textarea>
                            <button type="submit" class="btn btn-primary w-100">Submit Report</button>
                        </form>
                    </div>
                </div>
                <div class="col-md-8">
                    <h4>Lost Items Board</h4>
                    <div class="row">
                        {{% for item in items %}}
                        <div class="col-md-6 mb-3">
                            <div class="card p-3">
                                <h5 class="text-primary">{{{{ item[1] }}}}</h5>
                                <p class="small text-muted mb-1">📍 {{{{ item[3] }}}}</p>
                                <p>{{{{ item[2] }}}}</p>
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
    # 3. Return the HTML instead of jsonify
    return render_template_string(template, items=items)
