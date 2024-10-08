"""
Test cases for Product Model
"""

import logging
import os
from unittest import TestCase
from unittest.mock import patch
from wsgi import app
from service.models import Shopcart, Product, DataValidationError, db
from tests.factories import ShopcartFactory, ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#        P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
class TestProduct(TestCase):
    """Product Model Test Cases"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Shopcart).delete()  # clean up the last tests
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_add_shopcart_product(self):
        """It should Create a shopcart with a product and add it to the database"""
        shopcarts = Shopcart.all()
        self.assertEqual(shopcarts, [])
        shopcart = ShopcartFactory()
        # product = ProductFactory(shopcart=shopcart)
        product = ProductFactory()
        shopcart.products.append(product)
        shopcart.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(shopcart.id)
        shopcarts = Shopcart.all()
        self.assertEqual(len(shopcarts), 1)

        new_shopcart = Shopcart.find(shopcart.id)
        self.assertEqual(new_shopcart.products[0].product_id, product.product_id)

        # product2 = ProductFactory(shopcart=shopcart)
        product2 = ProductFactory()
        shopcart.products.append(product2)
        shopcart.update()

        new_shopcart = Shopcart.find(shopcart.id)
        self.assertEqual(len(new_shopcart.products), 2)
        self.assertEqual(new_shopcart.products[1].product_id, product2.product_id)
