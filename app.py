from flask import Flask, render_template_string, request, redirect, url_for
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
DB_FILE = "database.db"
ADMIN_PASSWORD = "rotgadmin"
TELEGRAM_USERNAME = "JohnRipper1337"  # Apnar Telegram Username/Bot ID

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            price TEXT DEFAULT 'Free',
            description TEXT,
            custom_html TEXT,
            created_at TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rat One The Go Store</title>
    <style>
        :root {
            --bg-color: #0f172a;
            --card-bg: #1e293b;
            --accent-color: #6366f1;
            --danger-color: #ef4444;
            --text-color: #f8fafc;
            --text-muted: #94a3b8;
            --border-color: rgba(255, 255, 255, 0.1);
        }

        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, sans-serif; }
        body { background-color: var(--bg-color); color: var(--text-color); min-height: 100vh; }

        /* Top Bar Navigation Menu */
        header {
            background: rgba(30, 41, 59, 0.9);
            backdrop-filter: blur(10px);
            padding: 1rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--border-color);
            position: sticky;
            top: 0;
            z-index: 100;
        }

        .logo {
            font-size: 1.5rem;
            font-weight: bold;
            background: linear-gradient(135deg, #a855f7, #6366f1);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .nav-menu {
            display: flex;
            gap: 15px;
            align-items: center;
            list-style: none;
        }

        .nav-link {
            color: var(--text-color);
            text-decoration: none;
            padding: 0.5rem 1rem;
            border-radius: 8px;
            font-weight: 500;
            transition: all 0.3s ease;
        }

        .nav-link:hover {
            background: rgba(255, 255, 255, 0.05);
            color: var(--accent-color);
        }

        .btn-accent {
            background: var(--accent-color);
            color: white !important;
        }

        .container { max-width: 1200px; margin: 2rem auto; padding: 0 1rem; }

        /* Grid Layout */
        .product-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 1.5rem;
            margin-top: 1.5rem;
        }

        .product-card {
            background: var(--card-bg);
            border-radius: 12px;
            padding: 1.5rem;
            border: 1px solid var(--border-color);
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            transition: transform 0.2s ease;
        }

        .product-card:hover { transform: translateY(-4px); }

        .price-badge {
            background: rgba(99, 102, 241, 0.2);
            color: #a5b4fc;
            padding: 0.3rem 0.6rem;
            border-radius: 6px;
            font-size: 0.85rem;
            font-weight: bold;
            display: inline-block;
            margin-bottom: 0.5rem;
        }

        .product-title { font-size: 1.25rem; margin-bottom: 0.5rem; color: #fff; }
        .product-desc { color: var(--text-muted); font-size: 0.95rem; margin-bottom: 1rem; line-height: 1.4; }
        .custom-html-box { background: rgba(0,0,0,0.2); padding: 0.8rem; border-radius: 8px; border: 1px dashed var(--border-color); margin-bottom: 1rem; }
        .product-date { font-size: 0.75rem; color: var(--text-muted); display: block; margin-top: auto; }

        /* Admin Forms */
        .admin-box {
            max-width: 650px;
            margin: 0 auto;
            background: var(--card-bg);
            padding: 2rem;
            border-radius: 12px;
            border: 1px solid var(--border-color);
        }

        .form-group { margin-bottom: 1.2rem; }
        .form-group label { display: block; margin-bottom: 0.5rem; color: var(--text-muted); }
        .form-group input, .form-group textarea {
            width: 100%; padding: 0.8rem;
            background: var(--bg-color);
            border: 1px solid var(--border-color);
            color: var(--text-color);
            border-radius: 8px; outline: none;
        }
        .form-group textarea { height: 120px; }

        .btn-submit {
            background: var(--accent-color); color: white; border: none;
            padding: 0.8rem 1.5rem; border-radius: 8px; cursor: pointer; font-weight: 600; width: 100%;
        }

        .btn-delete {
            background: var(--danger-color); color: white; border: none;
            padding: 0.4rem 0.8rem; border-radius: 6px; cursor: pointer; font-size: 0.8rem; margin-top: 0.5rem;
        }
    </style>
</head>
<body>

    <!-- Serial Top Navigation Bar -->
    <header>
        <div class="logo">Rat One The Go Store</div>
        <ul class="nav-menu">
            <li><a href="/" class="nav-link">Store Home</a></li>
            <li><a href="https://t.me/{{ telegram_user }}" target="_blank" class="nav-link">Contact Admin</a></li>
            {% if is_admin %}
                <li><a href="/" class="nav-link btn-accent">View Live Store</a></li>
            {% else %}
                <li><a href="/admin" class="nav-link btn-accent">Admin Panel</a></li>
            {% endif %}
        </ul>
    </header>

    <div class="container">
        {% if is_admin %}
            <!-- ADMIN DASHBOARD -->
            <div class="admin-box">
                <h2>Admin Dashboard - Post New Item</h2>
                {% if error %}<p style="color: var(--danger-color); margin-top: 0.5rem;">{{ error }}</p>{% endif %}
                
                <form action="/add-product" method="post" style="margin-top: 1.5rem;">
                    <div class="form-group">
                        <label>Admin Password</label>
                        <input type="password" name="password" required placeholder="Enter admin password">
                    </div>
                    <div class="form-group">
                        <label>Product Title</label>
                        <input type="text" name="title" required placeholder="e.g. Premium Access Pack">
                    </div>
                    <div class="form-group">
                        <label>Price</label>
                        <input type="text" name="price" placeholder="e.g. $10 or Free">
                    </div>
                    <div class="form-group">
                        <label>Product Description</label>
                        <textarea name="description" placeholder="Write product overview, features, or details..."></textarea>
                    </div>
                    <div class="form-group">
                        <label>Custom HTML/CSS Styling (Optional Code Box)</label>
                        <textarea name="custom_html" placeholder="<span style='color:lime;'>Status: Active</span>"></textarea>
                    </div>
                    <button type="submit" class="btn-submit">Publish Product</button>
                </form>

                <hr style="margin: 2rem 0; border-color: var(--border-color);">

                <h3>Manage / Delete Existing Products</h3>
                <div style="margin-top: 1rem;">
                    {% for item in products %}
                        <div style="display: flex; justify-content: space-between; align-items: center; background: var(--bg-color); padding: 0.8rem; border-radius: 8px; margin-bottom: 0.5rem;">
                            <div>
                                <strong>{{ item[1] }}</strong> ({{ item[2] }})
                            </div>
                            <form action="/delete-product/{{ item[0] }}" method="post" style="display:inline;">
                                <input type="hidden" name="password" value="rotgadmin">
                                <button type="submit" class="btn-delete" onclick="return confirm('Delete this post?')">Delete</button>
                            </form>
                        </div>
                    {% else %}
                        <p style="color: var(--text-muted);">No products to manage.</p>
                    {% endfor %}
                </div>
            </div>

        {% else %}
            <!-- STORE PUBLIC FRONTEND -->
            <h2>Available Products</h2>
            <div class="product-grid">
                {% for item in products %}
                    <div class="product-card">
                        <div>
                            <span class="price-badge">{{ item[2] }}</span>
                            <h3 class="product-title">{{ item[1] }}</h3>
                            <p class="product-desc">{{ item[3] }}</p>
                            
                            {% if item[4] %}
                                <div class="custom-html-box">
                                    {{ item[4] | safe }}
                                </div>
                            {% endif %}
                        </div>
                        <div>
                            <span class="product-date">Posted on: {{ item[5] }}</span>
                        </div>
                    </div>
                {% else %}
                    <p style="color: var(--text-muted);">No products posted yet.</p>
                {% endfor %}
            </div>
        {% endif %}
    </div>

</body>
</html>
"""

@app.route("/")
def index():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products ORDER BY id DESC")
    products = cursor.fetchall()
    conn.close()
    return render_template_string(HTML_TEMPLATE, products=products, is_admin=False, telegram_user=TELEGRAM_USERNAME)

@app.route("/admin")
def admin():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products ORDER BY id DESC")
    products = cursor.fetchall()
    conn.close()
    return render_template_string(HTML_TEMPLATE, products=products, is_admin=True, error=None, telegram_user=TELEGRAM_USERNAME)

@app.route("/add-product", methods=["POST"])
def add_product():
    password = request.form.get("password")
    title = request.form.get("title")
    price = request.form.get("price") or "Free"
    description = request.form.get("description")
    custom_html = request.form.get("custom_html")

    if password != ADMIN_PASSWORD:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products ORDER BY id DESC")
        products = cursor.fetchall()
        conn.close()
        return render_template_string(HTML_TEMPLATE, products=products, is_admin=True, error="Incorrect Password!", telegram_user=TELEGRAM_USERNAME)

    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO products (title, price, description, custom_html, created_at) VALUES (?, ?, ?, ?, ?)",
                   (title, price, description, custom_html, created_at))
    conn.commit()
    conn.close()

    return redirect(url_for("index"))

@app.route("/delete-product/<int:product_id>", methods=["POST"])
def delete_product(product_id):
    password = request.form.get("password")
    if password == ADMIN_PASSWORD:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
        conn.commit()
        conn.close()
    return redirect(url_for("admin"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)