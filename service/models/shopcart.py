"""
Persistent Base class for database CRUD functions
"""

import logging
from .persistent_base import db, PersistentBase, DataValidationError
from .product import Product

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
    products = db.relationship("Product", backref="product", passive_deletes=True)

    def __repr__(self):
        return f"<Shopcart {self.name} id=[{self.id}]>"

    def serialize(self):
        """Converts an Account into a dictionary"""
        shopcart = {
            "id": self.id,
            "name": self.name,
            "products": [],
        }
        for product in self.products:
            shopcart["products"].append(product.serialize())
        return shopcart

    def deserialize(self, data):
        """
        Populates an Shopcart from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.name = data["name"]

            # handle inner list of products
            product_list = data.get("products")

            for json_product in product_list:
                product = Product()
                product.deserialize(json_product)
                self.products.append(product)

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
