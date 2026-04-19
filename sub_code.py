from flask import Flask, redirect, request, jsonify
import sqlite3
import os

app = Flask(__name__)

# Update this path when deploying to PythonAnywhere (e.g., /home/yourusername/mysite/redirect.db)
DB_PATH = "redirect.db"


# ✅ Initialize DB
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS config (
            id INTEGER PRIMARY KEY,
            url TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS search_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device TEXT,
            url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Ensure one row exists
    cursor.execute("SELECT COUNT(*) FROM config")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO config (id, url) VALUES (1, '')")

    conn.commit()
    conn.close()


init_db()


# 🌐 Main endpoint → redirect
@app.route("/")
def index():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT url FROM config WHERE id = 1")
    result = cursor.fetchone()

    conn.close()

    if result and result[0]:
        response = redirect(result[0], code=302)
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response
    else:
        return "No URL configured", 404


# 🔄 Update endpoint (POST)
@app.route("/update", methods=["POST"])
def update_url():
    new_url = request.form.get("url")

    if not new_url:
        return jsonify({"error": "URL required"}), 400

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("UPDATE config SET url = ? WHERE id = 1", (new_url,))
    conn.commit()
    conn.close()

    return jsonify({"message": "URL updated", "url": new_url})


# 🔍 Optional: check current URL
@app.route("/current")
def current():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT url FROM config WHERE id = 1")
    result = cursor.fetchone()

    conn.close()

    return jsonify({"url": result[0] if result else None})


if __name__ == "__main__":
    app.run(debug=True, port=5001)
