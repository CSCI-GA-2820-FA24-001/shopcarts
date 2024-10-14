######################################################################
# Copyright 2016, 2024 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

"""
TestYourResourceModel API Service Test Suite
"""

# pylint: disable=duplicate-code
import os
import logging
from unittest import TestCase
from wsgi import app
from service.common import status
from service.models import db, Shopcart, Item
from tests.factories import ShopcartFactory, ItemFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)

BASE_URL = "/shopcarts"


######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestShopcartService(TestCase):
    """REST API Server Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests"""
        db.session.close()

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()
        db.session.query(Shopcart).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  H E L P E R   M E T H O D S
    ######################################################################

    def _create_shopcarts(self, count, name=None) -> list:
        """Factory method to create shopcarts in bulk"""
        shopcarts = []
        for i in range(count):
            shopcart = ShopcartFactory(name=name if name else f"shopcart{i}")
            resp = self.client.post(BASE_URL, json=shopcart.serialize())
            self.assertEqual(
                resp.status_code,
                status.HTTP_201_CREATED,
                "Could not create test Shopcart",
            )
            new_shopcart = resp.get_json()
            shopcart.id = new_shopcart["id"]
            shopcarts.append(shopcart)
        return shopcarts
    
    def _create_shopcart_with_item(self, name="Test Shopcart", item_data=None):
        """Helper function to create a shopcart with one item and persist to the database.
        
        Args:
            name (str): Name of the shopcart to create.
            item_data (dict): Data for the item to create. If None, defaults to a sample item.

        Returns:
            tuple: The created Shopcart and Item objects.
        """
        # Create a default item if no item_data is provided
        if item_data is None:
            item_data = {
                "item_id": "item1",
                "description": "Sample Item",
                "quantity": 1,
                "price": 100,
            }

        # Create an item using the ItemFactory
        item = ItemFactory(**item_data)

        # Create a shopcart and associate the item with it
        shopcart = ShopcartFactory(name=name, items=[item])  # Pass item in a list

        resp = self.client.post(
            BASE_URL, json=shopcart.serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED ,"Could not create shopcart-with-item")
        
        return shopcart, item



    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """It should call the home page"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["name"], "Shopcarts REST API Service")
        self.assertEqual(data["version"], "1.0")

    # ----------------------------------------------------------
    # TEST CREATE
    # ----------------------------------------------------------
    def test_create_shopcart(self):
        """It should Create a new Shopcart"""
        shopcart = ShopcartFactory()
        resp = self.client.post(
            BASE_URL, json=shopcart.serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = resp.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_shopcart = resp.get_json()
        self.assertEqual(new_shopcart["name"], shopcart.name, "Names does not match")

        # Check that the location header was correct by getting it
        resp = self.client.get(location, content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_shopcart = resp.get_json()
        self.assertEqual(new_shopcart["name"], shopcart.name, "Names does not match")

    # ----------------------------------------------------------
    # TEST LIST
    # ----------------------------------------------------------
    def test_list_shopcarts(self):
        """It should Get a list of Shopcarts and filter by name"""
        # Create 5 shopcarts with default names
        self._create_shopcarts(5)

        self._create_shopcarts(1, name="special_shopcart")

        # Test getting all shopcarts
        resp = self.client.get(BASE_URL)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 6)

        # Test getting shopcarts by name
        resp = self.client.get(BASE_URL + "?name=special_shopcart")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "special_shopcart")

    # ----------------------------------------------------------
    # TEST READ
    # ----------------------------------------------------------
    def test_get_shopcart(self):
        """It should Get a single Shopcart"""
        test_shopcart = self._create_shopcarts(1)[0]
        resp = self.client.get(f"/shopcarts/{test_shopcart.id}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["name"], test_shopcart.name)

    def test_get_shopcart_not_found(self):
        """It should not Get a Shopcart that's not found"""
        resp = self.client.get("/shopcarts/0")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        data = resp.get_json()
        logging.debug("resp data = %s", data)
        self.assertIn("was not found", data["message"])

    # ----------------------------------------------------------
    # TEST READ
    # ----------------------------------------------------------
    def test_update_shopcart(self):
        """It should Update an existing shopcarts"""
        # create a shopcart to update
        test_shopcart = ShopcartFactory()
        resp = self.client.post(BASE_URL, json=test_shopcart.serialize())
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # update the shopcart
        new_shopcart = resp.get_json()
        new_shopcart["name"] = "special_shopcart"
        new_shopcart_id = new_shopcart["id"]
        resp = self.client.put(f"{BASE_URL}/{new_shopcart_id}", json=new_shopcart)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_shopcart = resp.get_json()
        self.assertEqual(updated_shopcart["name"], "special_shopcart")

    def test_update_nonexistent_shopcart(self):
        """It should return 404 when updating a shopcart that does not exist"""
        update_data = {"name": "some_name"}
        resp = self.client.put(f"{BASE_URL}/0", json=update_data)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        
    # ----------------------------------------------------------
    # TEST DELETE
    # ----------------------------------------------------------
    def test_delete_shopcart(self):
        """It should delete a Shopcart"""
        test_shopcart = self._create_shopcarts(1)[0]
        resp = self.client.delete(f"{BASE_URL}/{test_shopcart.id}")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(resp.data), 0)
        # make sure they are deleted
        resp = self.client.get(f"{BASE_URL}/{test_shopcart.id}")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_non_exist_shopcart(self):
        """It should Delete a Shopcart even if it does not exist"""
        resp = self.client.delete(f"{BASE_URL}/0")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(resp.data), 0)
    
   # ----------------------------------------------------------
    # TEST ITEM QUANTITY GET
    # ----------------------------------------------------------
    def test_get_item_quantity(self):
        """It should Get the quantity of a specific Item"""
        # Step 1 and Step 2 are workarounds until create shopcart-item is available.
        # Step 1: Create a shopcart with no items
        shopcart_payload = {
            "name": "TESTCART",
            "items": []
        }
        resp = self.client.post(BASE_URL, json=shopcart_payload, content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        shopcart_data = resp.get_json()
        shopcart_id = shopcart_data['id']

        # Step 2: Add an item to the shopcart
        item_payload = {
            "name": "TESTCART",
            "items": [
                {
                    "shopcart_id": shopcart_id,
                    "item_id": "item_1",
                    "description": "Item 1 Description",
                    "quantity": 2,
                    "price": 100
                }
            ]
        }
        resp = self.client.put(f"{BASE_URL}/{shopcart_id}", json=item_payload, content_type="application/json")
        item_pid = resp.get_json()["items"][0]["id"]
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        # Perform the test:
        # Step 3: Now get the item quantity
        resp = self.client.get(f"{BASE_URL}/{shopcart_id}/items/{item_pid}")  # Adjusted the URL based on item_id
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["quantity"], 2)

    # ----------------------------------------------------------
    # TEST ITEM QUANTITY GET NOT FOUND
    # ----------------------------------------------------------
    def test_get_item_quantity_not_found(self):
        """It should not Get an Item quantity that doesn't exist"""
        
        # Step 1: Create a shopcart
        shopcart_payload = {
            "name": "TESTCART2",
            "items": []
        }
        resp = self.client.post(BASE_URL, json=shopcart_payload, content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        shopcart_data = resp.get_json()

        # Step 2: Attempt to get the quantity for a non-existent item
        resp = self.client.get(f"{BASE_URL}/{shopcart_data['id']}/items/999")  # Use an invalid item_id
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        data = resp.get_json()
        self.assertIn("was not found", data["message"])

    # ----------------------------------------------------------
    # TEST ITEM QUANTITY UPDATE
    # ----------------------------------------------------------
    def test_update_item_quantity(self):
        """It should Update the quantity of a specific Item"""
        
        # Step 1: Create a shopcart
        shopcart_payload = {
            "name": "TESTCART3",
            "items": []
        }
        resp = self.client.post(BASE_URL, json=shopcart_payload, content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        shopcart_data = resp.get_json()
        shopcart_id = shopcart_data['id']

        # Step 2: Add an item to the shopcart
        item_payload = {
            "name": "TESTCART3",
            "items": [
                {
                    "shopcart_id": shopcart_id,
                    "item_id": "item_1",
                    "description": "Item 1 Description",
                    "quantity": 2,
                    "price": 100
                }
            ]
        }
        resp = self.client.put(f"{BASE_URL}/{shopcart_id}", json=item_payload, content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        item_pid = resp.get_json()["items"][0]["id"]

        # Step 3: Now update the item quantity
        new_quantity = 5  # New quantity for the item
        resp = self.client.put(f"{BASE_URL}/{shopcart_id}/items/{item_pid}", json={"quantity": new_quantity})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        # Step 4: Verify that the quantity has been updated
        resp = self.client.get(f"{BASE_URL}/{shopcart_id}/items/{item_pid}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["quantity"], new_quantity)

    # ----------------------------------------------------------
    # TEST ITEM QUANTITY UPDATE NOT FOUND
    # ----------------------------------------------------------
    def test_update_item_quantity_not_found(self):
        """It should not Update an Item quantity that doesn't exist"""
        
        # Step 1: Create a shopcart
        shopcart_payload = {
            "name": "New Shopcart",
            "items": []
        }
        resp = self.client.post(BASE_URL, json=shopcart_payload, content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        shopcart_data = resp.get_json()
        # Step 2: Attempt to update the quantity of a non-existent item
        resp = self.client.put(f"{BASE_URL}/{shopcart_data['id']}/items/999/quantity", json={"quantity": 10})
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        data = resp.get_json()
        self.assertIn("was not found", data["message"])