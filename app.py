from flask import Flask, jsonify, request

app = Flask(__name__)

# Sample database (temporary list)
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
            "/search"
        ]
    })

# Get all lost items
@app.route('/items', methods=['GET'])
def get_items():
    return jsonify({
        "total_items": len(lost_items),
        "items": lost_items
    })

# Report lost item
@app.route('/report', methods=['POST'])
def report_item():
    data = request.get_json()

    if not data or "name" not in data or "description" not in data:
        return jsonify({
            "error": "Missing required fields"
        }), 400

    item = {
        "id": len(lost_items) + 1,
        "name": data["name"],
        "description": data["description"],
        "location": data.get("location", "Unknown"),
        "status": "lost"
    }

    lost_items.append(item)

    return jsonify({
        "message": "Item reported successfully",
        "item": item
    }), 201


# Search lost items
@app.route('/search', methods=['GET'])
def search_item():
    keyword = request.args.get('q', '').lower()

    results = [
        item for item in lost_items
        if keyword in item['name'].lower()
        or keyword in item['description'].lower()
    ]

    return jsonify({
        "keyword": keyword,
        "results": results
    })


# Run locally
if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
