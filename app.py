import psycopg2
import os
from flask import Flask, render_template_string, request, redirect, url_for

app = Flask(__name__)

# Connect to the Render Postgres Database
def get_db_connection():
    conn = psycopg2.connect(os.environ.get('DATABASE_URL'), sslmode='require')
    return conn

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
