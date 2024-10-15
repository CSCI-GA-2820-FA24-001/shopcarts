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
YourResourceModel Service

This service implements a REST API that allows you to Create, Read, Update
and Delete YourResourceModel
"""

from flask import jsonify, request, url_for, abort
from flask import current_app as app  # Import Flask application
from service.models import Shopcart, Item
from service.common import status  # HTTP Status Codes


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    app.logger.info("Request for Root URL")
    return (
        jsonify(
            name="Shopcarts REST API Service",
            version="1.0",
            paths={
                "create_shopcarts": url_for("create_shopcarts", _external=True),
                "read_shopcarts": url_for(
                    "get_shopcarts", shopcart_id=1, _external=True
                ),
                "update_shopcarts": url_for(
                    "update_shopcarts", shopcart_id=1, _external=True
                ),
                "delete_shopcarts": url_for(
                    "delete_shopcarts", shopcart_id=1, _external=True
                ),
                "list_shopcarts": url_for("list_shopcarts", _external=True),
                "create_shopcart_items": url_for(
                    "create_items", shopcart_id=1, _external=True
                ),
                "read_shopcart_items": url_for(
                    "get_items", shopcart_id=1, item_id=1, _external=True
                ),
                "update_shopcart_items": url_for(
                    "update_items", shopcart_id=1, item_id=1, _external=True
                ),
                "delete_shopcart_items": url_for(
                    "delete_item_from_shopcart",
                    shopcart_id=1,
                    item_id=1,
                    _external=True,
                ),
                "list_shopcart_items": url_for(
                    "list_items_in_shopcart", shopcart_id=1, _external=True
                ),
            },
        ),
        status.HTTP_200_OK,
    )


######################################################################
# CREATE A NEW ACCOUNT
######################################################################
@app.route("/shopcarts", methods=["POST"])
def create_shopcarts():
    """
    Creates a Shopcart
    This endpoint will create a Shopcart based the data in the body that is posted
    """
    app.logger.info("Request to create a Shopcart")
    check_content_type("application/json")

    # Create the shopcart
    shopcart = Shopcart()
    shopcart.deserialize(request.get_json())
    shopcart.create()

    # Create a message to return
    message = shopcart.serialize()
    location_url = url_for("get_shopcarts", shopcart_id=shopcart.id, _external=True)

    return jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
# READ A SHOPCART
######################################################################
@app.route("/shopcarts/<int:shopcart_id>", methods=["GET"])
def get_shopcarts(shopcart_id):
    """
    Retrieve a single Shopcart

    This endpoint will return a Shopcart based on it's id
    """
    app.logger.info("Request to Retrieve a shopcart with id: %s", shopcart_id)
    shopcart = Shopcart.find(shopcart_id)
    if not shopcart:
        abort(
            status.HTTP_404_NOT_FOUND, f"Shopcart with id {shopcart_id} was not found"
        )

    app.logger.info("Returning shopcart: %s", shopcart.name)
    return jsonify(shopcart.serialize()), status.HTTP_200_OK


######################################################################
# UPDATE AN EXISTING Shopcart
######################################################################
@app.route("/shopcarts/<int:shopcart_id>", methods=["PUT"])
def update_shopcarts(shopcart_id):
    """
    Update an shopcart

    This endpoint will update an shopcart based the body that is posted
    """
    app.logger.info("Request to update shopcart with id: %s", shopcart_id)
    check_content_type("application/json")

    # See if the shopcart exists and abort if it doesn't
    shopcart = Shopcart.find(shopcart_id)
    if not shopcart:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"shopcart with id '{shopcart_id}' was not found.",
        )

    # Update from the json in the body of the request
    shopcart.deserialize(request.get_json())
    shopcart.id = shopcart_id
    shopcart.update()

    return jsonify(shopcart.serialize()), status.HTTP_200_OK


######################################################################
# DELETE A SHOPCART
######################################################################
@app.route("/shopcarts/<int:shopcart_id>", methods=["DELETE"])
def delete_shopcarts(shopcart_id):
    """
    Delete a Shopcart

    This endpoint will delete a Shopcart based the id specified in the path
    """
    app.logger.info("Request to Delete a shopcart with id: %s", shopcart_id)

    # Delete the shopcart if it exists
    shopcart = Shopcart.find(shopcart_id)
    if shopcart:
        app.logger.info("Shopcart with ID: %d found", shopcart_id)
        shopcart.delete()

    app.logger.info("Shopcart with ID: %d deleted", shopcart_id)
    return {}, status.HTTP_204_NO_CONTENT


######################################################################
# LIST ALL SHOPCARTS
######################################################################
@app.route("/shopcarts", methods=["GET"])
def list_shopcarts():
    """Returns all of the Shopcarts"""
    app.logger.info("Request for Shopcart list")
    shopcarts = []

    # Process the query string if any
    name = request.args.get("name")
    if name:
        shopcarts = Shopcart.find_by_name(name)
    else:
        shopcarts = Shopcart.all()

    # Return as an array of dictionaries
    results = [shopcart.serialize() for shopcart in shopcarts]

    return jsonify(results), status.HTTP_200_OK


# ---------------------------------------------------------------------
#                A D D R E S S   M E T H O D S
# ---------------------------------------------------------------------

######################################################################
# CREATE A ITEM TO A SHOPCART
######################################################################


@app.route("/shopcarts/<int:shopcart_id>/items", methods=["POST"])
def create_items(shopcart_id):
    """
    Create a Item on a Shopcart
    """

    app.logger.info("Request to create a Item for Shopcart with id: %s", shopcart_id)
    check_content_type("application/json")

    shopcart = Shopcart.find(shopcart_id)
    if not shopcart:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Shopcart with id '{shopcart_id}' could not be found.",
        )

    # Create an Item from the json POST data
    item = Item()
    item.deserialize(request.get_json())

    # Append the Item to the Shopcart
    shopcart.items.append(item)
    shopcart.update()

    # Return message
    message = item.serialize()

    # Send the location to GET the new item
    location_url = url_for(
        "get_items", shopcart_id=shopcart.id, item_id=item.id, _external=True
    )

    return jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
# RETRIEVE AN ITEM FROM SHOPCART
######################################################################
@app.route("/shopcarts/<int:shopcart_id>/items/<int:item_id>", methods=["GET"])
def get_items(shopcart_id, item_id):
    """
    Get an Item

    This endpoint returns just an item
    """
    app.logger.info(
        "Request to retrieve Item %s for Account id: %s", (item_id, shopcart_id)
    )

    # See if the item exists and abort if it doesn't
    item = Item.find(item_id)
    if not item:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Account with id '{item_id}' could not be found.",
        )

    return jsonify(item.serialize()), status.HTTP_200_OK


######################################################################
# UPDATE AN EXISTING ITEM
######################################################################
@app.route("/shopcarts/<int:shopcart_id>/items/<int:item_id>", methods=["PUT"])
def update_items(shopcart_id, item_id):
    """
    Update an Item

    This endpoint will update an Item based the body that is posted
    """
    app.logger.info(
        "Request to update Address %s for Account id: %s", (item_id, shopcart_id)
    )
    check_content_type("application/json")

    # See if the address exists and abort if it doesn't
    item = Item.find(item_id)
    if not item:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Item with id '{item_id}' could not be found.",
        )

    # Update from the json in the body of the request
    item.deserialize(request.get_json())
    item.id = item_id
    item.update()

    return jsonify(item.serialize()), status.HTTP_200_OK


######################################################################
# DELETE AN ITEM FROM A SHOPCART
######################################################################
@app.route("/shopcarts/<int:shopcart_id>/items/<int:item_id>", methods=["DELETE"])
def delete_item_from_shopcart(shopcart_id, item_id):
    """
    Delete an Item from a Shopcart
    This endpoint will delete an Item based on the item_id from the specified shopcart
    """
    app.logger.info("Request to delete Item %s from Shopcart %s", item_id, shopcart_id)

    # Find the shopcart by shopcart_id
    shopcart = Shopcart.find(shopcart_id)
    if not shopcart:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Shopcart with id '{shopcart_id}' was not found.",
        )

    # Find the item by item_id within the shopcart
    item = Item.query.filter_by(id=item_id, shopcart_id=shopcart_id).first()
    if not item:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Item with id '{item_id}' in Shopcart '{shopcart_id}' was not found.",
        )

    # Delete the item
    item.delete()

    app.logger.info("Item with id %s deleted from Shopcart %s", item_id, shopcart_id)
    return {}, status.HTTP_204_NO_CONTENT


######################################################################
# LIST ALL ITEMS IN A SHOPCART
######################################################################
@app.route("/shopcarts/<int:shopcart_id>/items", methods=["GET"])
def list_items_in_shopcart(shopcart_id):
    """
    List all items in a Shopcart
    This endpoint will return all items in the shopcart with the given id.
    """
    app.logger.info("Request to list items in Shopcart %s", shopcart_id)

    # Find the shopcart by id
    shopcart = Shopcart.find(shopcart_id)
    if not shopcart:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Shopcart with id '{shopcart_id}' was not found.",
        )

    # Serialize all items in the shopcart
    items = [item.serialize() for item in shopcart.items]

    app.logger.info("Returning %d items from Shopcart %s", len(items), shopcart_id)
    return jsonify(items), status.HTTP_200_OK


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


def check_content_type(content_type):
    """Checks that the media type is correct"""
    if "Content-Type" not in request.headers:
        app.logger.error("No Content-Type specified.")
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )

    if request.headers["Content-Type"] == content_type:
        return

    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, f"Content-Type must be {content_type}"
    )
