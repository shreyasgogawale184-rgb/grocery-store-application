import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    DATABASE = os.environ.get("GROCERY_DB", os.path.join(BASE_DIR, "grocery.db"))
    # Simple admin key for write operations (change this in production!)
    ADMIN_KEY = os.environ.get("GROCERY_ADMIN_KEY", "admin123")
    JSON_SORT_KEYS = False
