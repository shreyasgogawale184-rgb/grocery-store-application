import os
import tempfile
import unittest

from app import create_app

ADMIN = {"X-Admin-Key": "admin123"}


class GroceryApiTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        app = create_app({"DATABASE": os.path.join(self.tmp.name, "test.db"), "TESTING": True})
        self.client = app.test_client()

    def tearDown(self):
        self.tmp.cleanup()

    def milk(self):
        return self.client.get("/api/products?q=Milk").get_json()[0]

    def test_list_and_filter_products(self):
        self.assertEqual(len(self.client.get("/api/products").get_json()), 10)
        dairy = self.client.get("/api/products?category=Dairy").get_json()
        self.assertEqual({p["name"] for p in dairy}, {"Milk", "Paneer"})
        self.assertEqual(self.client.get("/api/products?q=apple").get_json()[0]["name"], "Apple")

    def test_create_requires_admin_key(self):
        r = self.client.post("/api/products", json={"name": "Eggs", "price": 7})
        self.assertEqual(r.status_code, 401)

    def test_product_crud(self):
        r = self.client.post("/api/products", headers=ADMIN,
                             json={"name": "Eggs", "category": "Dairy", "price": 7, "stock": 100})
        self.assertEqual(r.status_code, 201)
        pid = r.get_json()["id"]

        r = self.client.put(f"/api/products/{pid}", headers=ADMIN, json={"price": 8})
        self.assertEqual(r.get_json()["price"], 8.0)

        self.assertEqual(self.client.delete(f"/api/products/{pid}", headers=ADMIN).status_code, 204)
        self.assertEqual(self.client.get(f"/api/products/{pid}").status_code, 404)

    def test_validation_error(self):
        r = self.client.post("/api/products", headers=ADMIN, json={"name": "", "price": -1})
        self.assertEqual(r.status_code, 400)

    def test_order_reduces_stock(self):
        milk = self.milk()
        r = self.client.post("/api/orders", json={
            "customer_name": "Shreyas", "items": [{"product_id": milk["id"], "quantity": 2}]})
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.get_json()["total"], milk["price"] * 2)
        after = self.client.get(f"/api/products/{milk['id']}").get_json()
        self.assertEqual(after["stock"], milk["stock"] - 2)

    def test_order_insufficient_stock(self):
        milk = self.milk()
        r = self.client.post("/api/orders", json={
            "customer_name": "X", "items": [{"product_id": milk["id"], "quantity": 9999}]})
        self.assertEqual(r.status_code, 409)

    def test_duplicate_lines_cannot_bypass_stock(self):
        milk = self.milk()
        half = milk["stock"] // 2 + 1
        r = self.client.post("/api/orders", json={"customer_name": "X", "items": [
            {"product_id": milk["id"], "quantity": half},
            {"product_id": milk["id"], "quantity": half}]})
        self.assertEqual(r.status_code, 409)

    def test_admin_can_view_orders(self):
        milk = self.milk()
        oid = self.client.post("/api/orders", json={
            "customer_name": "A", "items": [{"product_id": milk["id"], "quantity": 1}]}).get_json()["id"]
        self.assertEqual(self.client.get("/api/orders").status_code, 401)
        detail = self.client.get(f"/api/orders/{oid}", headers=ADMIN).get_json()
        self.assertEqual(detail["items"][0]["name"], "Milk")

    def test_frontend_served(self):
        self.assertEqual(self.client.get("/").status_code, 200)


if __name__ == "__main__":
    unittest.main()
