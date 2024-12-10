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

from flask import request
from flask import current_app as app  # Import Flask application
from flask_restx import Resource, fields, reqparse
from service.models import Shopcart, Item
from service.common import status  # HTTP Status Codes
from . import api  # pylint: disable=cyclic-import


######################################################################
# GET HEALTH CHECK
######################################################################
@app.route("/health")
def health_check():
    """Let them know our heart is still beating"""
    return {"status": 200, "message": "Healthy"}, 200


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    app.logger.info("Request for Root URL")
    return app.send_static_file("index.html")


create_item_model = api.model(
    "Item",
    {
        "shopcart_id": fields.Integer(required=True, description="ID of the shopcart"),
        "item_id": fields.String(required=True, description="Id (Name) of the item"),
        "product_id": fields.Integer(required=True, description="ID of the product"),
        "description": fields.String(
            required=True,
            description="Description of the item",
        ),
        "quantity": fields.Integer(required=True, description="Quantity of the item"),
        "price": fields.Integer(required=True, description="Price of the item"),
    },
)

item_model = api.inherit(
    "ItemModel",
    create_item_model,
    {
        "id": fields.String(readOnly=True, description="The unique id for item"),
    },
)

create_shopcart_model = api.model(
    "Shopcart",
    {
        "name": fields.String(required=True, description="Name of the shopcart"),
        "items": fields.List(
            fields.Nested(item_model),
            required=False,
            description="Items in shopcart",
        ),
    },
)

shopcart_model = api.inherit(
    "ShopcartModel",
    create_shopcart_model,
    {
        "id": fields.Integer(
            readOnly=True,
            description="The unique ID for shopcart",
        ),
    },
)

shopcart_args = reqparse.RequestParser()
shopcart_args.add_argument(
    "name",
    type=str,
    location="args",
    required=False,
    help="Name of the Shopcart",
)

item_args = reqparse.RequestParser()
item_args.add_argument(
    "item_id",
    type=str,
    location="args",
    required=False,
    help="ID of the Item",
)
item_args.add_argument(
    "quantity",
    type=int,
    location="args",
    required=False,
    help="Quantity of the Item",
)
item_args.add_argument(
    "price",
    type=int,
    location="args",
    required=False,
    help="Price the Item",
)

######################################################################
#  PATH: /shopcarts/{id}
######################################################################


@api.route("/shopcarts/<int:shopcart_id>")
@api.param("shopcart_id", "The Shopcart identifier")
class ShopcartResource(Resource):
    """
    ShopcartResource class

    Allows the manipulation of a single Shopcart
    GET /shopcarts/{id} - Returns a Shopcart with the id
    PUT /shopcarts/{id} - Update a Shopcart with the id
    DELETE /shopcarts/{id} -  Deletes a Shopcart with the id
    """

    # ------------------------------------------------------------------
    # RETRIEVE A SHOPCART
    # ------------------------------------------------------------------
    @api.doc("get_shopcarts")
    @api.response(404, "Shopcart not found")
    @api.marshal_with(shopcart_model)
    def get(self, shopcart_id):
        """
        Retrieve a single Shopcart

        This endpoint will return a Shopcart based on it's id
        """

        app.logger.info("Request to Retrieve a shopcart with id: %s", shopcart_id)
        shopcart = Shopcart.find(shopcart_id)
        if not shopcart:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Shopcart with id {shopcart_id} was not found",
            )

        app.logger.info("Returning shopcart: %s", shopcart.name)
        return shopcart.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # UPDATE AN EXISTING SHOPCART
    # ------------------------------------------------------------------
    @api.doc("update_shopcarts")
    @api.response(404, "Shopcart not found")
    @api.response(400, "The posted Shopcart data was not valid")
    @api.expect(shopcart_model)
    @api.marshal_with(shopcart_model)
    def put(self, shopcart_id):
        """
        Update a Shopcart

        This endpoint will update an Shopcart based on the body that is posted
        """

        app.logger.info("Request to update shopcart with id: %s", shopcart_id)
        shopcart = Shopcart.find(shopcart_id)
        if not shopcart:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"shopcart with id '{shopcart_id}' was not found.",
            )

        app.logger.info("Processing: %s", api.payload)

        shopcart.deserialize(api.payload)
        shopcart.id = shopcart_id
        shopcart.update()

        return shopcart.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # DELETE A SHOPCART
    # ------------------------------------------------------------------
    @api.doc("delete_shopcarts")
    @api.response(204, "Shopcart deleted")
    def delete(self, shopcart_id):
        """
        Delete a Shopcart

        This endpoint will delete a Shopcart based on its id
        """

        app.logger.info("Request to Delete a shopcart with id: %s", shopcart_id)
        shopcart = Shopcart.find(shopcart_id)
        if shopcart:
            app.logger.info("Shopcart with ID: %d found", shopcart_id)
            shopcart.delete()

        return "", status.HTTP_204_NO_CONTENT


######################################################################
#  PATH: /shopcarts
######################################################################
@api.route("/shopcarts", strict_slashes=False)
class ShopcartCollection(Resource):
    """Handles all interactions with collections of Shopcarts"""

    # ------------------------------------------------------------------
    # LIST ALL SHOPCARTS
    # ------------------------------------------------------------------
    @api.doc("list_shopcarts")
    @api.expect(shopcart_args, validate=True)
    @api.marshal_list_with(shopcart_model)
    def get(self):
        """Returns all of the Shopcarts"""

        app.logger.info("Request for Shopcart list")
        shopcarts = []

        args = shopcart_args.parse_args()

        if args["name"]:
            app.logger.info("Filtering by name: %s", args["name"])
            shopcarts = Shopcart.find_by_name(args["name"])
        else:
            app.logger.info("Returning unfiltered list")
            shopcarts = Shopcart.all()

        shopcarts = [shopcart.serialize() for shopcart in shopcarts]
        app.logger.info("Returning [%d] shopcarts", len(shopcarts))

        return shopcarts, status.HTTP_200_OK

    # ------------------------------------------------------------------
    # CREATE A NEW SHOPCART
    # ------------------------------------------------------------------
    @api.doc("create_shopcarts")
    @api.response(400, "The posted Shopcart data was not valid")
    @api.expect(create_shopcart_model)
    @api.marshal_with(shopcart_model, code=201)
    def post(self):
        """
        Creates a Shopcart

        This endpoint will create an Shopcart based the data on the body that is posted
        """

        app.logger.info("Request to create a Shopcart")
        app.logger.info("Processing: %s", api.payload)

        shopcart = Shopcart()
        shopcart.deserialize(request.get_json())
        shopcart.create()

        app.logger.info("Shopcart id [%s] created!", shopcart.id)
        location_url = api.url_for(
            ShopcartResource, shopcart_id=shopcart.id, _external=True
        )

        return shopcart.serialize(), status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
#  CLEAR ACTION => PATH: /shopcarts/{id}/clear
######################################################################
@api.route("/shopcarts/<int:shopcart_id>/clear")
@api.param("shopcart_id", "The Shopcart identifier")
class ClearResource(Resource):
    """
    Clear action on a Shopcart
    """

    @api.doc("clear_shopcarts")
    @api.response(404, "Shopcart not found")
    def put(self, shopcart_id):
        """
        Clear a Shopcart

        This endpoint will clear a Shopcart based on its id and make it empty
        """
        app.logger.info(f"Request to clear shopcart : {shopcart_id}")

        shopcart = Shopcart.find(shopcart_id)
        if not shopcart:
            abort(status.HTTP_404_NOT_FOUND, f"No such shopcart : {shopcart_id}.")

        for item in shopcart.items:
            item.delete()

        shopcart.id = shopcart_id
        shopcart.update()

        return shopcart.serialize(), status.HTTP_200_OK


######################################################################
#  Total Price ACTION => PATH: /shopcarts/{id}/clear
######################################################################
@api.route("/shopcarts/<int:shopcart_id>/calculate_total_price")
@api.param("shopcart_id", "The Shopcart identifier")
class CalculateTotalPriceResource(Resource):
    """
    Calculate total price for selected or all items in a Shopcart
    """

    @api.doc("calculate_total_price")
    @api.response(404, "Shopcart not found")
    def get(self, shopcart_id):
        """
        Calculate total price of all items in a Shopcart

        This endpoint calculates the total price of all items in the specified shopcart.
        """
        app.logger.info(
            "Request to calculate total price for all items in Shopcart %s", shopcart_id
        )

        shopcart = Shopcart.find(shopcart_id)
        if not shopcart:
            abort(status.HTTP_404_NOT_FOUND, f"No such shopcart: {shopcart_id}.")

        total_price = Shopcart.calculate_total_price(shopcart_id)
        app.logger.info(
            "Total price for all items in Shopcart %s is %d", shopcart_id, total_price
        )

        return {"total_price": total_price}, status.HTTP_200_OK


######################################################################
#  PATH: /shopcarts/{id}/items/{id}
######################################################################
@api.route("/shopcarts/<int:shopcart_id>/items/<int:item_id>")
@api.param("shopcart_id", "The Shopcart id")
@api.param("item_id", "The Item id")
class ItemResource(Resource):
    """
    ItemResource class

    Allows the manipulation of a single Shopcart Item
    GET /shopcarts/{id}/items/{id} - Returns a Item with the id
    PUT /shopcarts/{id}/items/{id} - Update a Item with the id
    DELETE /shopcarts/{id}/items/{id} -  Deletes a Item with the id
    """

    # ------------------------------------------------------------------
    # RETRIEVE AN ITEM FROM A SHOPCART
    # ------------------------------------------------------------------
    @api.doc("get_items")
    @api.response(404, "Item not found")
    @api.marshal_with(item_model)
    def get(self, shopcart_id, item_id):
        """
        Retrieve a Item from Shopcart
        This endpoint returns just an item
        """
        app.logger.info(
            "Request to retrieve Item %s for Account id: %s", (item_id, shopcart_id)
        )

        item = Item.find(item_id)
        if not item:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Account with id '{item_id}' could not be found.",
            )

        return item.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # UPDATE A SHOPCART ITEM
    # ------------------------------------------------------------------
    @api.doc("update_item")
    @api.response(404, "Item not found")
    @api.response(400, "The Item data was not valid")
    @api.expect(item_model)
    @api.marshal_with(item_model)
    def put(self, shopcart_id, item_id):
        """
        Update an Item
        This endpoint will update an Item based the body that is posted
        """
        app.logger.info(
            "Request to update Address %s for Account id: %s", (item_id, shopcart_id)
        )

        item = Item.find(item_id)
        if not item:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Item with id '{item_id}' could not be found.",
            )

        item.deserialize(api.payload)
        item.update()

        return item.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # DELETE A SHOPCART ITEM
    # ------------------------------------------------------------------
    @api.doc("delete_item")
    @api.response(204, "Item deleted")
    def delete(self, shopcart_id, item_id):
        """
        Delete an Item from a Shopcart
        This endpoint will delete an Item based on the item_id from the specified shopcart
        """
        app.logger.info(
            "Request to delete Item %s from Shopcart %s", item_id, shopcart_id
        )

        shopcart = Shopcart.find(shopcart_id)
        if not shopcart:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Shopcart with id '{shopcart_id}' was not found.",
            )

        item = Item.query.filter_by(id=item_id, shopcart_id=shopcart_id).first()
        if item:
            # Delete the item if it exists
            item.delete()
            app.logger.info(
                "Item with id %s deleted from Shopcart %s", item_id, shopcart_id
            )
        else:
            app.logger.info(
                "Item with id %s not found in Shopcart %s", item_id, shopcart_id
            )

        return "", status.HTTP_204_NO_CONTENT


######################################################################
#  PATH: /shopcarts/{id}/items
######################################################################
@api.route("/shopcarts/<int:shopcart_id>/items", strict_slashes=False)
@api.param("shopcart_id", "The Shopcart identifier")
class ItemCollection(Resource):
    """Handles all interactions with collections of Shopcart Items"""

    # ------------------------------------------------------------------
    # LIST ALL ITEMS IN A SHOPCART
    # ------------------------------------------------------------------
    @api.doc("list_shopcart_items")
    @api.expect(item_args, validate=True)
    @api.marshal_list_with(item_model)
    def get(self, shopcart_id):
        """
        List all items in a Shopcart
        This endpoint will return all items in the shopcart with the given id.
        """
        app.logger.info("Request to list items in Shopcart %s", shopcart_id)

        # Attempt to find the Shopcart and abort if not found
        shopcart = Shopcart.find(shopcart_id)
        if not shopcart:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Shopcart with id '{shopcart_id}' was not found.",
            )

        items = shopcart.items

        # Get the query parameters
        args = item_args.parse_args()
        item_id = args.get("item_id")
        quantity = args.get("quantity")
        price = args.get("price")

        if item_id:
            app.logger.info("Filtering by item_id: %s", item_id)
            items = [item for item in items if item.item_id == item_id]
        if quantity:
            app.logger.info("Filtering by quantity: %s", quantity)
            items = [item for item in items if item.quantity == quantity]
        if price:
            app.logger.info("Filtering by price: %s", price)
            items = [item for item in items if item.price == price]

        result = [item.serialize() for item in items]

        app.logger.info("Returning %d items from Shopcart %s", len(result), shopcart_id)

        return result, status.HTTP_200_OK

    # ------------------------------------------------------------------
    # CREATE AN ITEM
    # ------------------------------------------------------------------
    @api.doc("create_shopcart_items")
    @api.response(400, "The posted Shopcart Item data was not valid")
    @api.expect(create_item_model)
    @api.marshal_with(item_model, code=201)
    def post(self, shopcart_id):
        """
        Create a Item on a Shopcart
        """
        app.logger.info(
            "Request to create a Item for Shopcart with id: %s", shopcart_id
        )

        shopcart = Shopcart.find(shopcart_id)
        if not shopcart:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Shopcart with id '{shopcart_id}' could not be found.",
            )

        data = api.payload

        app.logger.info("Processing: %s", data)

        item = Item()
        item.deserialize(data)

        shopcart.items.append(item)
        shopcart.update()

        # Return the location of the new item
        location_url = api.url_for(
            ItemResource,
            item_id=item.id,
            shopcart_id=shopcart_id,
            _external=True,
        )

        return item.serialize(), status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


def abort(error_code: int, message: str):
    """Logs errors before aborting"""
    app.logger.error(message)
    api.abort(error_code, message)


# @app.route("/shopcarts/<int:shopcart_id>/calculate_total_price", methods=["POST"])
# def calculate_selected_price(shopcart_id):
#     """
#     Calculate total price of selected items in a Shopcart
#     This endpoint will calculate the total price of all items marked as selected in the specified shopcart
#     """
#     app.logger.info(
#         "Request to calculate total price for selected items in Shopcart %s",
#         shopcart_id,
#     )

#     # Get item.id list
#     data = request.get_json()
#     selected_item_ids = data.get("selected_items", [])

#     # Find the shopcart by id
#     total_price = Shopcart.calculate_selected_items_price(
#         shopcart_id, selected_item_ids
#     )
#     app.logger.info(
#         "Total price for selected items in Shopcart %s is %s", shopcart_id, total_price
#     )
#     return jsonify(total_price=total_price), status.HTTP_200_OK
