"""
Test Factory to make fake objects for testing
"""

from factory import Factory, Sequence, Faker, post_generation, SubFactory
from factory.fuzzy import FuzzyInteger, FuzzyText
from service.models import Shopcart, Item


class ShopcartFactory(Factory):
    """Creates fake pets that you don't have to feed"""

    # pylint: disable=too-few-public-methods
    class Meta:
        """Maps factory to data model"""

        model = Shopcart

    id = Sequence(lambda n: n)
    name = Faker("first_name")

    @post_generation
    def items(
        self, create, extracted, **kwargs
    ):  # pylint: disable=method-hidden, unused-argument
        """Creates the items list"""
        if not create:
            return

        if extracted:
            self.items = extracted


class ProductFactory(Factory):
    """Creates fake Addresses"""

    # pylint: disable=too-few-public-methods
    class Meta:
        """Persistent class"""

        model = Item

    id = Sequence(lambda n: n)
    shopcart_id = None
    item_id = FuzzyInteger(1, 20)
    description = FuzzyText(length=12)
    quantity = FuzzyInteger(1, 30)
    price = FuzzyInteger(100, 1000)
    # shopcart = SubFactory(ShopcartFactory)
