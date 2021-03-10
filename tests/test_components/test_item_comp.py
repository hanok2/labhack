import pytest

from src.entity import Entity
from components.item_comp import ItemComponent
from components.component import Component


@pytest.fixture
def itemcomp():
    return ItemComponent()


@pytest.fixture
def testitem():
    e = Entity(name="fleepgork", item=ItemComponent())
    e.item.size = 10
    return e


def test_init__is_Component(itemcomp):
    assert isinstance(itemcomp, Component)


def test_init__last_letter__None_by_default(itemcomp):
    assert itemcomp.last_letter is None
