from flask import Flask, jsonify, request, redirect, url_for, render_template_string

app = Flask(__name__)

# Temporary database
lost_items = []

# Home route
@app.route('/')
def home():
    return jsonify({
        "message": "Welcome to the Campus Lost and Found API",
        "status": "running",
        "endpoints": [
            "/items",
            "/report",
            "/search",
            "/admin"
        ]
    })

# API: Get all lost items
@app.route('/items', methods=['GET'])
def get_items():
    return jsonify({
        "total_items": len(lost_items),
        "items": lost_items
    })

# API: Report lost item
@app.route('/report', methods=['POST'])
def report_item():
    data = request.get_json()
    if not data or "name" not in data or "description" not in data:
        return jsonify({"error": "Missing required fields"}), 400

    item = {
        "id": len(lost_items) + 1,
        "name": data["name"],
        "description": data["description"],
        "location": data.get("location", "Unknown"),
        "status": "Lost"
    }
    lost_items.append(item)
    return jsonify({"message": "Item reported successfully", "item": item}), 201

# API: Search lost items
@app.route('/search', methods=['GET'])
def search_item():
    keyword = request.args.get('q', '').lower()
    results = [
        item for item in lost_items
        if keyword in item['name'].lower() or keyword in item['description'].lower()
    ]
    return jsonify({"keyword": keyword, "results": results})

# Admin dashboard using render_template_string
@app.route('/admin')
def admin_dashboard():
    template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Admin Dashboard - Lost & Found</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: center; }
            th { background-color: #f2f2f2; }
            a { text-decoration: none; color: white; padding: 5px 10px; border-radius: 3px; }
            .found { background-color: green; }
            .delete { background-color: red; }
        </style>
    </head>
    <body>
    <h1>Lost & Found Admin Dashboard</h1>
    <table>
        <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Description</th>
            <th>Location</th>
            <th>Status</th>
            <th>Actions</th>
        </tr>
        {% for item in items %}
        <tr>
            <td>{{ item.id }}</td>
            <td>{{ item.name }}</td>
            <td>{{ item.description }}</td>
            <td>{{ item.location }}</td>
            <td>{{ item.status }}</td>
            <td>
                {% if item.status != 'Found' %}
                <a class="found" href="{{ url_for('mark_found', item_id=item.id) }}">Mark Found</a>
                {% endif %}
                <a class="delete" href="{{ url_for('delete_item', item_id=item.id) }}">Delete</a>
            </td>
        </tr>
        {% endfor %}
    </table>
    </body>
    </html>
    """
    return render_template_string(template, items=lost_items)

# Admin: mark item as found
@app.route('/admin/found/<int:item_id>')
def mark_found(item_id):
    for item in lost_items:
        if item["id"] == item_id:
            item["status"] = "Found"
            break
    return redirect(url_for('admin_dashboard'))

# Admin: delete item
@app.route('/admin/delete/<int:item_id>')
def delete_item(item_id):
    global lost_items
    lost_items = [item for item in lost_items if item["id"] != item_id]
    return redirect(url_for('admin_dashboard'))

# Run the app
if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
