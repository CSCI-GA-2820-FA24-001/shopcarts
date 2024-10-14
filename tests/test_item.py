"""
Test cases for Item Model
"""

import logging
import os
from unittest import TestCase
from wsgi import app
from service.models import Shopcart, Item, DataValidationError, db
from tests.factories import ShopcartFactory, ItemFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#        P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
class TestItem(TestCase):
    """Item Model Test Cases"""

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
        db.session.query(Item).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_add_shopcart_product(self):
        """It should Create a shopcart with a item and add it to the database"""
        shopcarts = Shopcart.all()
        self.assertEqual(shopcarts, [])
        shopcart = ShopcartFactory()
        item = ItemFactory(shopcart=shopcart)

        shopcart.items.append(item)
        shopcart.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(shopcart.id)
        shopcarts = Shopcart.all()
        self.assertEqual(len(shopcarts), 1)

        new_shopcart = Shopcart.find(shopcart.id)
        self.assertEqual(new_shopcart.items[0].item_id, item.item_id)

        product2 = ItemFactory(shopcart=shopcart)
        shopcart.items.append(product2)
        shopcart.update()

        new_shopcart = Shopcart.find(shopcart.id)
        self.assertEqual(len(new_shopcart.items), 2)
        self.assertEqual(new_shopcart.items[1].item_id, product2.item_id)

    def test_list_all_items_in_shopcart(self):
        """It should List all items in a Shopcart"""
        # Create a shopcart
        shopcart = ShopcartFactory()
        shopcart.create()

        # Add multiple items to the shopcart
        item1 = ItemFactory(shopcart_id=shopcart.id)
        item2 = ItemFactory(shopcart_id=shopcart.id)

        # Add items to the shopcart
        item1.create()
        item2.create()

        # Retrieve all items in the shopcart
        shopcart = Shopcart.find(shopcart.id)
        items = shopcart.items

        # Verify the response contains both items
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0].item_id, item1.item_id)
        self.assertEqual(items[1].item_id, item2.item_id)
