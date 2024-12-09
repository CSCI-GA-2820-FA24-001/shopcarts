"""
Persistent Base class for database CRUD functions
"""

import logging
from .persistent_base import db, PersistentBase, DataValidationError
from .item import Item

logger = logging.getLogger("flask.app")

######################################################################
#  S H O P C A R T   M O D E L
######################################################################


class Shopcart(db.Model, PersistentBase):
    """
    Class that represents an Shopcart
    """

    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    items = db.relationship("Item", backref="shopcart", passive_deletes=True)

    def __repr__(self):
        return f"<Shopcart {self.name} id=[{self.id}]>"

    def serialize(self):
        """Converts an Account into a dictionary"""
        shopcart = {
            "id": self.id,
            "name": self.name,
            "items": [],
        }
        for item in self.items:
            shopcart["items"].append(item.serialize())
        return shopcart

    def deserialize(self, data):
        """
        Populates an Shopcart from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.name = data["name"]

            # handle inner list of items
            product_list = data.get("items")

            for json_product in product_list:
                item = Item()
                item.deserialize(json_product)
                self.items.append(item)

        except AttributeError as error:
            raise DataValidationError("Invalid attribute: " + error.args[0]) from error
        except KeyError as error:
            raise DataValidationError(
                "Invalid Shopcart: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Shopcart: body of request contained bad or no data "
                + str(error)
            ) from error

        return self

    @classmethod
    def find_by_name(cls, name):
        """Returns the unique Shopcart with the given name

        Args:
            name (string): the name of the Accounts you want to match
        """
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name)

    @classmethod
    def calculate_selected_items_price(
        cls, shopcart_id: int, selected_item_ids: list[int]
    ) -> int:
        """_summary_

        Args:
            id (_type_): _description_

        Returns:
            _type_: _description_
        """
        shopcart = cls.find(shopcart_id)
        total_price = sum(
            item.quantity * item.price
            for item in shopcart.items
            if int(item.item_id) in selected_item_ids
        )
        return total_price

    @classmethod
    def calculate_total_price(cls, shopcart_id: int):
        """_summary_

        Args:
            id (_type_): _description_

        Returns:
            _type_: _description_
        """
        shopcart = cls.find(shopcart_id)
        total_price = sum(item.quantity * item.price for item in shopcart.items)
        return total_price
