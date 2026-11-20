"""SQLite database layer (stdlib only)."""
import sqlite3
from flask import current_app, g

SCHEMA = """
CREATE TABLE IF NOT EXISTS categories (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS products (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL,
    category_id INTEGER NOT NULL REFERENCES categories(id),
    price       REAL NOT NULL CHECK (price >= 0),
    unit        TEXT NOT NULL DEFAULT 'each',
    stock       INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0)
);

CREATE TABLE IF NOT EXISTS orders (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_name TEXT NOT NULL,
    total         REAL NOT NULL,
    created_at    TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS order_items (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id   INTEGER NOT NULL REFERENCES orders(id),
    product_id INTEGER NOT NULL REFERENCES products(id),
    quantity   INTEGER NOT NULL CHECK (quantity > 0),
    unit_price REAL NOT NULL
);
"""

SEED_CATEGORIES = ["Fruits", "Vegetables", "Dairy", "Bakery", "Beverages", "Snacks"]

# (name, category, price, unit, stock)
SEED_PRODUCTS = [
    ("Apple", "Fruits", 120.0, "kg", 50),
    ("Banana", "Fruits", 60.0, "dozen", 80),
    ("Tomato", "Vegetables", 40.0, "kg", 100),
    ("Potato", "Vegetables", 30.0, "kg", 150),
    ("Spinach", "Vegetables", 25.0, "bunch", 40),
    ("Milk", "Dairy", 56.0, "litre", 60),
    ("Paneer", "Dairy", 90.0, "250g", 30),
    ("Bread", "Bakery", 45.0, "loaf", 35),
    ("Orange Juice", "Beverages", 110.0, "litre", 25),
    ("Potato Chips", "Snacks", 20.0, "pack", 200),
]


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(_exc=None):
    conn = g.pop("db", None)
    if conn is not None:
        conn.close()


def init_db():
    conn = get_db()
    conn.executescript(SCHEMA)
    if conn.execute("SELECT COUNT(*) FROM categories").fetchone()[0] == 0:
        conn.executemany(
            "INSERT INTO categories (name) VALUES (?)", [(c,) for c in SEED_CATEGORIES]
        )
        cat_ids = {r["name"]: r["id"] for r in conn.execute("SELECT * FROM categories")}
        conn.executemany(
            "INSERT INTO products (name, category_id, price, unit, stock) VALUES (?,?,?,?,?)",
            [(n, cat_ids[c], p, u, s) for n, c, p, u, s in SEED_PRODUCTS],
        )
    conn.commit()


def init_app(app):
    app.teardown_appcontext(close_db)
    with app.app_context():
        init_db()
