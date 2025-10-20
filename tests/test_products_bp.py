import unittest
from app import app 

class FlaskAppTestCase(unittest.TestCase):

    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_products_page(self):
        """Тест маршруту /prroducts."""
        response = self.client.get("products")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Banana", response.data)


    def test_product_page(self):
        """Тест маршруту /products/<id>."""
        response = self.client.get("products/1")

        self.assertIn(b'1', response.data)
        self.assertIn(b"Lemon", response.data)
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()