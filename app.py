import psycopg2
import os
from flask import Flask, render_template_string, request, redirect, url_for

app = Flask(__name__)

# --- POSTGRESQL CONNECTION ---
# Render automatically provides 'DATABASE_URL' if you link them
DB_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    return psycopg2.connect(DB_URL, sslmode='require')

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            location TEXT,
            status TEXT DEFAULT 'Lost'
        )
    ''')
    conn.commit()
    cur.close()
    conn.close()

init_db()

# --- UPDATE YOUR ROUTES TO USE THE NEW CONNECTION ---
@app.route('/report-ui', methods=['POST'])
def report_ui():
    name = request.form.get('name')
    description = request.form.get('description')
    location = request.form.get('location', 'Unknown')

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('INSERT INTO items (name, description, location) VALUES (%s, %s, %s)', 
                (name, description, location))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('home'))
