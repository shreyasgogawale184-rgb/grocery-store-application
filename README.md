# Grocery Store Application

A full-stack Python project: **Flask** backend + REST API + **SQLite** database + vanilla HTML/CSS/JS frontend.

## Structure
```
grocery_store_application/
├── run.py              # entry point
├── config.py           # settings (DB path, admin key)
├── requirements.txt
├── app/
│   ├── __init__.py     # app factory
│   ├── db.py           # schema, seed data, connection helpers
│   ├── auth.py         # admin-key decorator
│   └── routes/
│       ├── products.py # product & category APIs
│       └── orders.py   # order APIs
├── static/             # frontend (index.html, style.css, app.js)
└── tests/test_api.py
```

## Run
```bash
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
python run.py
```
Open http://127.0.0.1:5000

## API
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | /api/categories | – | List categories |
| GET | /api/products?q=&category= | – | List / search / filter products |
| GET | /api/products/<id> | – | Single product |
| POST | /api/products | Admin | Create product |
| PUT | /api/products/<id> | Admin | Update product |
| DELETE | /api/products/<id> | Admin | Delete product |
| POST | /api/orders | – | Place order (reduces stock) |
| GET | /api/orders, /api/orders/<id> | Admin | View orders |

Admin endpoints need the header `X-Admin-Key: admin123` (override with env var `GROCERY_ADMIN_KEY`).

Example:
```bash
curl -X POST localhost:5000/api/products -H "X-Admin-Key: admin123" \
  -H "Content-Type: application/json" \
  -d '{"name":"Eggs","category":"Dairy","price":7,"unit":"each","stock":100}'
```

## Tests
```bash
python -m unittest
```

## Ideas to extend
User login (JWT), payment integration, admin dashboard, SQLAlchemy/PostgreSQL, sales analytics with pandas.
