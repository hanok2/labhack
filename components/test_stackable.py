import pytest
from src.entity import Entity
from .component import Component
from src import exceptions
from .stackable import StackableComponent


@pytest.fixture
def stackcomp():
    return StackableComponent()


@pytest.fixture
def testitem():
    e = Entity(name="fleepgork", stackable=StackableComponent())
    e.stackable.stacksize = 10
    return e


def test_init__is_Component(stackcomp):
    assert isinstance(stackcomp, Component)


def test_init__stacksize_always_starts_as_1():
    s = StackableComponent()
    assert s.stacksize == 1


# def test_merge_stack__identical_Item__returns_True():
# def test_merge_stack__identical_Item__adds_to_stack():
# def test_merge_stack__identical_Item__destroy_other_stack():
# def test_merge_stack__different_Item__returns_False():


def test_split_stack__0_qty__raises_ValueError(testitem):
    with pytest.raises(ValueError):
        testitem.stackable.split_stack(0)


def test_split_stack__partial__returns_copied_Item(testitem):
    assert testitem.stackable.stacksize == 10
    result = testitem.stackable.split_stack(1)
    # Is the item the same type? Name?
    assert result.name == testitem.name


def test_split_stack__partial__stacksize_depleted(testitem):
    assert testitem.stackable.stacksize == 10
    testitem.stackable.split_stack(1)
    assert testitem.stackable.stacksize == 9


def test_split_stack__partial__copy_stacksize(testitem):
    assert testitem.stackable.stacksize == 10
    result = testitem.stackable.split_stack(1)
    assert result.stackable.stacksize == 1


def test_split_stack__full__stacksize_depleted(testitem):
    assert testitem.stackable.stacksize == 10
    result = testitem.stackable.split_stack(10)
    assert result
    assert testitem.stackable.stacksize == 0


def test_split_stack__more_than_stacksize__raises_ValueError(testitem):
    assert testitem.stackable.stacksize == 10
    with pytest.raises(ValueError):
        testitem.stackable.split_stack(11)


def test_deplete_stack__0_qty__raises_ValueError():
    s = StackableComponent()
    with pytest.raises(ValueError):
        s.deplete_stack(0)


def test_deplete_stack__partial():
    s = StackableComponent()
    s.stacksize = 2
    s.deplete_stack(1)
    assert s.stacksize == 1


def test_deplete_stack__success_returns_True():
    s = StackableComponent()
    s.stacksize = 2
    assert s.deplete_stack(1)


def test_deplete_stack__more_than_stacksize__raises_ValueError():
    s = StackableComponent()
    assert s.stacksize == 1
    with pytest.raises(ValueError):
        s.deplete_stack(2)


# def test_deplete_stack__full__destroys_item():