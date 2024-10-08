"""
Test cases for Shopcart Model
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
#        S H O P C A R T   M O D E L   T E S T   C A S E S
######################################################################
class TestShopcart(TestCase):
    """Account Model Test Cases"""

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
