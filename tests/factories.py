"""
Test Factory to make fake objects for testing
"""

from factory import Factory, Sequence, Faker, post_generation, SubFactory
from factory.fuzzy import FuzzyInteger, FuzzyText
from service.models import Shopcart, Product


class ShopcartFactory(Factory):
    """Creates fake pets that you don't have to feed"""

    # pylint: disable=too-few-public-methods
    class Meta:
        """Maps factory to data model"""

        model = Shopcart

    id = Sequence(lambda n: n)
    name = Faker("first_name")

    @post_generation
    def products(
        self, create, extracted, **kwargs
    ):  # pylint: disable=method-hidden, unused-argument
        """Creates the products list"""
        if not create:
            return

        if extracted:
            self.products = extracted


class ProductFactory(Factory):
    """Creates fake Addresses"""

    # pylint: disable=too-few-public-methods
    class Meta:
        """Persistent class"""

        model = Product

    id = Sequence(lambda n: n)
    shopcart_id = None
    product_id = FuzzyInteger(1, 20)
    description = FuzzyText(length=12)
    quantity = FuzzyInteger(1, 30)
    price = FuzzyInteger(100, 1000)
    # shopcart = SubFactory(ShopcartFactory)
