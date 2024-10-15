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
from service.models import db, Shopcart
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

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_index(self):
        """It should call the home page"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["name"], "Shopcarts REST API Service")
        self.assertEqual(data["version"], "1.0")

    ######################################################################
    #  S H O P C A R T   T E S T   C A S E S
    ######################################################################

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
    # TEST UPDATE
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

    ######################################################################
    #  I T E M   T E S T   C A S E S
    ######################################################################

    # ----------------------------------------------------------
    # TEST CREATE
    # ----------------------------------------------------------

    def test_add_item(self):
        """It should create a new item and add to a shopcart"""
        shopcart = self._create_shopcarts(1)[0]
        item = ItemFactory()
        resp = self.client.post(
            f"{BASE_URL}/{shopcart.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = resp.headers.get("Location", None)
        self.assertIsNotNone(location)

        data = resp.get_json()
        logging.debug(data)
        self.assertEqual(str(data["shopcart_id"]), str(shopcart.id))
        self.assertEqual(str(data["item_id"]), str(item.item_id))
        self.assertEqual(data["description"], item.description)
        self.assertEqual(str(data["quantity"]), str(item.quantity))
        self.assertEqual(str(data["price"]), str(item.price))

        # Check that the location header was correct by getting it
        resp = self.client.get(location, content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_item = resp.get_json()
        # Converting both to string for comparison
        self.assertEqual(
            str(new_item["item_id"]), str(item.item_id), "item name does not match"
        )

    # ----------------------------------------------------------
    # TEST READ
    # ----------------------------------------------------------
    def test_read_an_item(self):
        """It should Read an item from an shopcart"""
        # create a known item
        shopcart = self._create_shopcarts(1)[0]
        item = ItemFactory()
        resp = self.client.post(
            f"{BASE_URL}/{shopcart.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        data = resp.get_json()
        logging.debug(data)
        item_id = data["id"]

        # retrieve it back
        resp = self.client.get(
            f"{BASE_URL}/{shopcart.id}/items/{item_id}",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        logging.debug(data)
        self.assertEqual(str(data["shopcart_id"]), str(shopcart.id))
        self.assertEqual(str(data["item_id"]), str(item.item_id))
        self.assertEqual(data["description"], item.description)
        self.assertEqual(str(data["quantity"]), str(item.quantity))
        self.assertEqual(str(data["price"]), str(item.price))

    # ----------------------------------------------------------
    # TEST UPDATE
    # ----------------------------------------------------------

    def test_update_item_quantity(self):
        """It should update the quantity of an existing item in a shopcart"""
        # Create a shopcart
        shopcart = ShopcartFactory()
        resp = self.client.post(BASE_URL, json=shopcart.serialize())
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        new_shopcart = resp.get_json()

        # Add an item to the shopcart
        item = ItemFactory(shopcart_id=new_shopcart["id"])
        resp = self.client.post(
            f"{BASE_URL}/{new_shopcart['id']}/items", json=item.serialize()
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        new_item = resp.get_json()

        # Update the item's quantity
        updated_quantity = new_item["quantity"] + 5
        resp = self.client.put(
            f"{BASE_URL}/{new_shopcart['id']}/items/{new_item['id']}",
            json={"quantity": updated_quantity},
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        # Verify the item's quantity has been updated
        resp = self.client.get(
            f"{BASE_URL}/{new_shopcart['id']}/items/{new_item['id']}"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["quantity"], updated_quantity)

    def test_update_non_existent_item(self):
        """It should return 404 when trying to update an item that does not exist"""
        # Create a shopcart
        shopcart = ShopcartFactory()
        resp = self.client.post(BASE_URL, json=shopcart.serialize())
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        new_shopcart = resp.get_json()

        # Attempt to update a non-existent item
        resp = self.client.put(
            f"{BASE_URL}/{new_shopcart['id']}/items/0",  # Item ID 0 doesn't exist
            json={"quantity": 10},
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

        # Verify the error message
        data = resp.get_json()
        self.assertIn("was not found", data["message"])

    def test_update_item_in_non_existent_shopcart(self):
        """It should return 404 when trying to update an item in a non-existent shopcart"""
        # Attempt to update an item in a non-existent shopcart
        resp = self.client.put(
            f"{BASE_URL}/0/items/1",  # Shopcart ID 0 doesn't exist
            json={"quantity": 10},
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

        # Verify the error message
        data = resp.get_json()
        self.assertIn("was not found", data["message"])

    def test_update_item_with_invalid_quantity(self):
        """It should return 400 when trying to update an item with an invalid quantity"""
        # Create a shopcart
        shopcart = ShopcartFactory()
        resp = self.client.post(BASE_URL, json=shopcart.serialize())
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        new_shopcart = resp.get_json()

        # Add an item to the shopcart
        item = ItemFactory(shopcart_id=new_shopcart["id"])
        resp = self.client.post(
            f"{BASE_URL}/{new_shopcart['id']}/items", json=item.serialize()
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        new_item = resp.get_json()

        # Attempt to update the item with a non-integer quantity
        resp = self.client.put(
            f"{BASE_URL}/{new_shopcart['id']}/items/{new_item['id']}",
            json={"quantity": "ten"},
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

        # Attempt to update the item with a negative quantity
        resp = self.client.put(
            f"{BASE_URL}/{new_shopcart['id']}/items/{new_item['id']}",
            json={"quantity": -5},
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

        # Attempt to update the item with zero quantity
        resp = self.client.put(
            f"{BASE_URL}/{new_shopcart['id']}/items/{new_item['id']}",
            json={"quantity": 0},
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_item_missing_quantity(self):
        """It should return 400 when the quantity is missing in the update request"""
        # Create a shopcart
        shopcart = ShopcartFactory()
        resp = self.client.post(BASE_URL, json=shopcart.serialize())
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        new_shopcart = resp.get_json()

        # Add an item to the shopcart
        item = ItemFactory(shopcart_id=new_shopcart["id"])
        resp = self.client.post(
            f"{BASE_URL}/{new_shopcart['id']}/items", json=item.serialize()
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        new_item = resp.get_json()

        # Attempt to update the item without a quantity in the request body
        resp = self.client.put(
            f"{BASE_URL}/{new_shopcart['id']}/items/{new_item['id']}", json={}
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

        # Verify the error message
        data = resp.get_json()
        self.assertIn("must contain 'quantity'", data["message"])

    def test_update_item_with_unsupported_media_type(self):
        """It should return 415 when trying to update with an unsupported content type"""
        # Create a shopcart
        shopcart = ShopcartFactory()
        resp = self.client.post(BASE_URL, json=shopcart.serialize())
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        new_shopcart = resp.get_json()

        # Add an item to the shopcart
        item = ItemFactory(shopcart_id=new_shopcart["id"])
        resp = self.client.post(
            f"{BASE_URL}/{new_shopcart['id']}/items", json=item.serialize()
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        new_item = resp.get_json()

        # Attempt to update the item with an unsupported content type
        headers = {"Content-Type": "text/plain"}
        data = "quantity: 10"
        resp = self.client.put(
            f"{BASE_URL}/{new_shopcart['id']}/items/{new_item['id']}",
            data=data,
            headers=headers,
        )
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

        # Verify the error message
        data = resp.get_json()
        self.assertIn("Unsupported media type", data["error"])

    # ----------------------------------------------------------
    # TEST DELETE
    # ----------------------------------------------------------
    def test_delete_item_from_shopcart(self):
        """It should delete an Item from a Shopcart"""
        # Create a shopcart
        shopcart = ShopcartFactory()
        resp = self.client.post(BASE_URL, json=shopcart.serialize())
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        new_shopcart = resp.get_json()

        # Add an item to the shopcart and explicitly pass shopcart_id
        item = ItemFactory(shopcart_id=new_shopcart["id"])
        resp = self.client.post(
            f"{BASE_URL}/{new_shopcart['id']}/items", json=item.serialize()
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        new_item = resp.get_json()

        # Delete the item from the shopcart
        resp = self.client.delete(
            f"{BASE_URL}/{new_shopcart['id']}/items/{new_item['id']}"
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

        # Verify the item is no longer in the shopcart
        resp = self.client.get(
            f"{BASE_URL}/{new_shopcart['id']}/items/{new_item['id']}"
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_item_not_found(self):
        """It should return 404 when trying to delete an item that does not exist"""
        # Create a shopcart
        shopcart = ShopcartFactory()
        resp = self.client.post(BASE_URL, json=shopcart.serialize())
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        new_shopcart = resp.get_json()

        # Try deleting a non-existing item
        resp = self.client.delete(
            f"{BASE_URL}/{new_shopcart['id']}/items/0"
        )  # ID 0 doesn't exist
        self.assertEqual(
            resp.status_code, status.HTTP_404_NOT_FOUND
        )  # Expect 404 for non-existent item

    # ----------------------------------------------------------
    # TEST LIST
    # ----------------------------------------------------------
    def test_list_items_in_shopcart(self):
        """It should List all items in a particular Shopcart"""
        # Create a shopcart
        shopcart = ShopcartFactory()
        resp = self.client.post(BASE_URL, json=shopcart.serialize())
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        new_shopcart = resp.get_json()

        # Add multiple items to the shopcart
        item1 = ItemFactory(shopcart_id=new_shopcart["id"])
        item2 = ItemFactory(shopcart_id=new_shopcart["id"])

        # Add item1
        resp = self.client.post(
            f"{BASE_URL}/{new_shopcart['id']}/items", json=item1.serialize()
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Add item2
        resp = self.client.post(
            f"{BASE_URL}/{new_shopcart['id']}/items", json=item2.serialize()
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Retrieve all items in the shopcart
        resp = self.client.get(f"{BASE_URL}/{new_shopcart['id']}/items")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        # Verify the response contains both items
        data = resp.get_json()
        self.assertEqual(len(data), 2)

        # Convert item_id from response to int and ensure the items returned are the ones we added
        self.assertEqual(int(data[0]["item_id"]), item1.item_id)
        self.assertEqual(int(data[1]["item_id"]), item2.item_id)

    def test_create_shopcart_bad_request(self):
        """It should return 400 Bad Request when the request data is invalid"""
        # Create a shopcart payload without the required 'name' field
        invalid_shopcart_data = {"description": "A shopcart without a name"}

        # Send POST request to create a shopcart with invalid data
        resp = self.client.post(BASE_URL, json=invalid_shopcart_data)

        # Assert that the response status code is 400
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

        # Assert that the response contains expected error information
        error_response = resp.get_json()
        self.assertEqual(error_response["status"], status.HTTP_400_BAD_REQUEST)
        self.assertEqual(error_response["error"], "Bad Request")
        self.assertIn("message", error_response)
        # Optionally check if the error message contains specific text
        self.assertIn("invalid", error_response["message"].lower())

    def test_method_not_allowed(self):
        """It should return 405 Method Not Allowed for unsupported HTTP methods"""
        # Attempt to POST to an endpoint that only supports GET
        resp = self.client.post("/", content_type="application/json")

        # Assert that the response status code is 405
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # Assert that the response contains expected error information
        error_response = resp.get_json()
        self.assertEqual(error_response["status"], status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(error_response["error"], "Method not Allowed")
        self.assertIn("message", error_response)
        # Optionally check if the error message contains specific text related to method not allowed
        self.assertIn("not allowed", error_response["message"].lower())

    def test_unsupported_media_type(self):
        """It should return 415 Unsupported Media Type for unsupported Content-Type"""
        # Send a request with an unsupported Content-Type
        headers = {"Content-Type": "text/plain"}
        data = "This is not JSON"

        resp = self.client.post(BASE_URL, data=data, headers=headers)

        # Assert that the response status code is 415
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

        # Assert that the response contains expected error information
        error_response = resp.get_json()
        self.assertEqual(
            error_response["status"], status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
        )
        self.assertEqual(error_response["error"], "Unsupported media type")
        self.assertIn("message", error_response)
        # Optionally check if the error message contains specific text related to unsupported media type
        self.assertIn("unsupported", error_response["message"].lower())
