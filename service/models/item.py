"""
Persistent Base class for database CRUD functions
"""

import logging
from .persistent_base import db, PersistentBase, DataValidationError

logger = logging.getLogger("flask.app")

######################################################################
#  I T E M  M O D E L
######################################################################


class Item(db.Model, PersistentBase):
    """
    Class that represents an Item
    """

    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
    shopcart_id = db.Column(
        db.Integer, db.ForeignKey("shopcart.id", ondelete="CASCADE"), nullable=False
    )
    item_id = db.Column(db.String(16), nullable=False)
    description = db.Column(db.String(64), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<Item {self.item_id} id=[{self.id}] shopcart[{self.shopcart_id}]>"

    def __str__(self):
        return f"{self.item_id}: {self.description}, {self.quantity}, {self.price}"

    def serialize(self) -> dict:
        """Converts an Address into a dictionary"""
        return {
            "id": self.id,
            "shopcart_id": self.shopcart_id,
            "item_id": self.item_id,
            "description": self.description,
            "quantity": self.quantity,
            "price": self.price,
        }

    def deserialize(self, data: dict) -> None:
        """
        Populates a Item from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        # try:
        #     self.shopcart_id = data["shopcart_id"]
        #     self.item_id = data["item_id"]
        #     self.description = data["description"]
        #     self.quantity = data["quantity"]
        #     self.price = data["price"]
        # except AttributeError as error:
        #     raise DataValidationError("Invalid attribute: " + error.args[0]) from error
        # except KeyError as error:
        #     raise DataValidationError(
        #         "Invalid Item: missing " + error.args[0]
        #     ) from error
        # except TypeError as error:
        #     raise DataValidationError(
        #         "Invalid Item: body of request contained bad or no data " + str(error)
        #     ) from error
        try:
            self.shopcart_id = data["shopcart_id"]
            self.item_id = data["item_id"]
            self.description = data["description"]
            # Ensure quantity and price are integers
            self.quantity = int(data["quantity"])
            self.price = int(data["price"])
        except ValueError as error:
            raise DataValidationError("Invalid data type: " + str(error)) from error
        except AttributeError as error:
            raise DataValidationError("Invalid attribute: " + error.args[0]) from error
        except KeyError as error:
            raise DataValidationError(
                "Invalid Item: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Item: body of request contained bad or no data " + str(error)
            ) from error

        return self
