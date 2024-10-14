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

    def test_serialize_a_item(self):
        """It should serialize a Item"""
        item = ItemFactory()
        serial_item = item.serialize()
        self.assertEqual(serial_item["id"], item.id)
        self.assertEqual(serial_item["shopcart_id"], item.shopcart_id)
        self.assertEqual(serial_item["item_id"], item.item_id)
        self.assertEqual(serial_item["description"], item.description)
        self.assertEqual(serial_item["quantity"], item.quantity)
        self.assertEqual(serial_item["price"], item.price)

    def test_deserialize_a_item(self):
        """It should deserialize a Item"""
        item = ItemFactory()
        item.create()

        new_item = Item()
        new_item = item.deserialize(item.serialize())
        self.assertEqual(new_item.id, item.id)
        self.assertEqual(new_item.shopcart_id, item.shopcart_id)
        self.assertEqual(new_item.description, item.description)
        self.assertEqual(new_item.description, item.description)
        self.assertEqual(new_item.quantity, item.quantity)
        self.assertEqual(new_item.price, item.price)

    # ----------------------------------------------------------
    # TEST CREATE
    # ----------------------------------------------------------
    def test_add_shopcart_product(self):
        """It should Create a shopcart with a item and add it to the serial_itembase"""
        shopcarts = Shopcart.all()
        self.assertEqual(shopcarts, [])
        shopcart = ShopcartFactory()
        item = ItemFactory(shopcart=shopcart)

        shopcart.items.append(item)
        shopcart.create()
        # Assert that it was assigned an id and shows up in the serial_itembase
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

    # ----------------------------------------------------------
    # TEST READ
    # ----------------------------------------------------------
    def test_read_item_from_shopcart(self):
        """It should Read an item from a particular shopcart"""
        shopcart = ShopcartFactory()
        item1 = ItemFactory(shopcart=shopcart)
        item2 = ItemFactory(shopcart=shopcart)

        shopcart.items.extend([item1, item2])
        shopcart.create()

        new_shopcart = Shopcart.find(shopcart.id)
        self.assertEqual(len(new_shopcart.items), 2)

        # Verify item1
        retrieved_item = next(
            (
                item
                for item in new_shopcart.items
                if str(item.item_id) == str(item1.item_id)
            ),
            None,
        )
        self.assertIsNotNone(retrieved_item)
        self.assertEqual(str(retrieved_item.item_id), str(item1.item_id))
        self.assertEqual(retrieved_item.description, item1.description)
        self.assertEqual(retrieved_item.quantity, item1.quantity)
        self.assertEqual(retrieved_item.price, item1.price)

        # Verify item2
        retrieved_item2 = next(
            (
                item
                for item in new_shopcart.items
                if str(item.item_id) == str(item2.item_id)
            ),
            None,
        )
        self.assertIsNotNone(retrieved_item2)
        self.assertEqual(str(retrieved_item2.item_id), str(item2.item_id))
        self.assertEqual(retrieved_item2.description, item2.description)
        self.assertEqual(retrieved_item2.quantity, item2.quantity)
        self.assertEqual(retrieved_item2.price, item2.price)
