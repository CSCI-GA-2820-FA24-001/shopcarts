"""
Test cases for Shopcart Model
"""

import logging
import os
from unittest import TestCase
from unittest.mock import patch
from wsgi import app
from service.models import Shopcart, Item, DataValidationError, db
from tests.factories import ShopcartFactory, ItemFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#        S H O P C A R T   M O D E L   T E S T   C A S E S
######################################################################


class TestShopcart(TestCase):
    """Shopcart Model Test Cases"""

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

    def test_create_a_shopcart(self):
        """It should Create a Shopcart and assert that it exists"""
        fake_shopcart = ShopcartFactory()
        # pylint: disable=unexpected-keyword-arg
        account = Shopcart(
            name=fake_shopcart.name,
        )

        self.assertIsNotNone(account)
        self.assertEqual(account.id, None)
        self.assertEqual(account.name, fake_shopcart.name)

    def test_add_a_account(self):
        """It should Create a Shopcart and add it to the database"""
        shopcarts = Shopcart.all()
        self.assertEqual(shopcarts, [])
        shopcart = ShopcartFactory()
        shopcart.create()

        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(shopcart.id)
        shopcarts = Shopcart.all()
        self.assertEqual(len(shopcarts), 1)

    @patch("service.models.db.session.commit")
    def test_add_account_failed(self, exception_mock):
        """It should not create a Shopcart on database error"""
        exception_mock.side_effect = Exception()
        shopcart = ShopcartFactory()
        self.assertRaises(DataValidationError, shopcart.create)

    def test_read_shopcart(self):
        """It should Read a Shopcart"""
        shopcart = ShopcartFactory()
        shopcart.create()

        # Read it back
        found_shopcart = Shopcart.find(shopcart.id)
        self.assertEqual(found_shopcart.id, shopcart.id)
        self.assertEqual(found_shopcart.name, shopcart.name)
        self.assertEqual(found_shopcart.items, [])

    def test_update_shopcart(self):
        """It should Update a Shopcart"""
        shopcart = ShopcartFactory(name="apple")
        shopcart.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(shopcart.id)
        self.assertEqual(shopcart.name, "apple")

        # Fetch it back
        shopcart = Shopcart.find(shopcart.id)
        shopcart.name = "banana"
        shopcart.update()

        # Fetch it back again
        shopcart = Shopcart.find(shopcart.id)
        self.assertEqual(shopcart.name, "banana")

    @patch("service.models.db.session.commit")
    def test_update_shopcart_failed(self, exception_mock):
        """It should not update a Shopcart on database error"""
        exception_mock.side_effect = Exception()
        shopcart = ShopcartFactory()
        self.assertRaises(DataValidationError, shopcart.update)

    def test_delete_a_shopcart(self):
        """It should Delete a Shopcart from the database"""
        shopcarts = Shopcart.all()
        self.assertEqual(shopcarts, [])
        shopcart = ShopcartFactory()
        shopcart.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(shopcart.id)
        shopcarts = Shopcart.all()
        self.assertEqual(len(shopcarts), 1)
        shopcart = shopcarts[0]
        shopcart.delete()
        shopcarts = Shopcart.all()
        self.assertEqual(len(shopcarts), 0)

    @patch("service.models.db.session.commit")
    def test_delete_shopcart_failed(self, exception_mock):
        """It should not delete a Shopcart on database error"""
        exception_mock.side_effect = Exception()
        shopcart = ShopcartFactory()
        self.assertRaises(DataValidationError, shopcart.delete)

    def test_list_all_shopcarts(self):
        """It should List all Shopcarts in the database"""
        shopcarts = Shopcart.all()
        self.assertEqual(shopcarts, [])
        for shopcart in ShopcartFactory.create_batch(5):
            shopcart.create()
        # Assert that there are not 5 shopcarts in the database
        shopcarts = Shopcart.all()
        self.assertEqual(len(shopcarts), 5)

    def test_find_by_name(self):
        """It should Find a Shopcart by name"""
        shopcart = ShopcartFactory()
        shopcart.create()

        # Fetch it back by name
        same_shopcart = Shopcart.find_by_name(shopcart.name)[0]
        self.assertEqual(same_shopcart.id, shopcart.id)
        self.assertEqual(same_shopcart.name, shopcart.name)

    def test_serialize_a_shopcart(self):
        """It should Serialize a Shopcart"""
        shopcart = Shopcart()
        item = ItemFactory()
        shopcart.items.append(item)
        serial_shopcart = shopcart.serialize()
        self.assertEqual(serial_shopcart["id"], shopcart.id)
        self.assertEqual(serial_shopcart["name"], shopcart.name)
        self.assertEqual(len(serial_shopcart["items"]), 1)

        items = serial_shopcart["items"]
        self.assertEqual(items[0]["id"], item.id)
        self.assertEqual(items[0]["shopcart_id"], item.shopcart_id)
        self.assertEqual(items[0]["item_id"], item.item_id)
        self.assertEqual(items[0]["description"], item.description)
        self.assertEqual(items[0]["quantity"], item.quantity)
        self.assertEqual(items[0]["price"], item.price)

    def test_deserialize_a_shopcart(self):
        """It should Deserialize a Shopcart"""
        shopcart = ShopcartFactory()
        shopcart.items.append(ItemFactory())
        shopcart.create()
        serial_shopcart = shopcart.serialize()
        new_shopcart = Shopcart()
        new_shopcart.deserialize(serial_shopcart)
        self.assertEqual(new_shopcart.name, shopcart.name)

    def test_deserialize_with_key_error(self):
        """It should not Deserialize a Shopcart with a KeyError"""
        shopcart = Shopcart()
        self.assertRaises(DataValidationError, shopcart.deserialize, {})

    def test_deserialize_with_type_error(self):
        """It should not Deserialize a Shopcart with a TypeError"""
        shopcart = Shopcart()
        self.assertRaises(DataValidationError, shopcart.deserialize, [])

    def test_deserialize_product_key_error(self):
        """It should not Deserialize a Item with a KeyError"""
        item = Item()
        self.assertRaises(DataValidationError, item.deserialize, {})

    def test_deserialize_product_type_error(self):
        """It should not Deserialize a Item with a TypeError"""
        item = Item()
        self.assertRaises(DataValidationError, item.deserialize, [])

    # def test_total_price(self):
    #     """It should test total price"""
    #     shopcart = ShopcartFactory()
    #     item1 = ItemFactory()
    #     shopcart.items.append(item1)
    #     item2 = ItemFactory()
    #     shopcart.items.append(item2)
    #     item3 = ItemFactory()
    #     shopcart.items.append(item3)
    #     shopcart.create()
    #     test_total_price = item1.price + item2.price + item3.price

    #     total_price = Shopcart.calculate_total_price(shopcart.id)
    #     self.assertEqual(total_price, test_total_price)

    # def test_total_price_selected(self):
    #     """It should total price selected"""
    #     shopcart = ShopcartFactory()
    #     item1 = ItemFactory()
    #     shopcart.items.append(item1)
    #     item2 = ItemFactory()
    #     shopcart.items.append(item2)
    #     item3 = ItemFactory()
    #     shopcart.items.append(item3)
    #     shopcart.create()
    #     test_total_price = item1.price + item3.price

    #     total_price = Shopcart.calculate_selected_items_price(
    #         shopcart.id, [int(item1.item_id), int(item3.item_id)]
    #     )
    #     self.assertEqual(total_price, test_total_price)
