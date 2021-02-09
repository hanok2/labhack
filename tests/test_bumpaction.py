from actions.bumpaction import BumpAction
from actions.moveaction import MovementAction
from actions.meleeaction import MeleeAction
from actions import actions
import pytest
import toolkit


@pytest.fixture
def test_map():
    return toolkit.test_map()


def test_BumpAction_is_Action(test_map):
    player = test_map.get_player()
    a = BumpAction(entity=player, dx=1, dy=-1)
    assert isinstance(a, actions.Action)


def test_BumpAction_is_ActionWithDirection(test_map):
    player = test_map.get_player()
    a = BumpAction(entity=player, dx=1, dy=-1)
    assert isinstance(a, actions.ActionWithDirection)


def test_BumpAction_init(test_map):
    player = test_map.get_player()
    a = BumpAction(entity=player, dx=1, dy=-1)
    assert a.entity == player
    assert a.dx == 1
    assert a.dy == -1
    assert a.msg == ''


def test_BumpAction_perform__Move(test_map):
    player = test_map.get_player()
    a = BumpAction(entity=player, dx=1, dy=1)
    result = a.perform()
    assert isinstance(result, MovementAction)


def test_BumpAction_perform__Move(test_map):
    # We'll attack the Grid Bug at (2, 5)
    player = test_map.get_player()
    player.place(2, 4, test_map)
    a = BumpAction(entity=player, dx=0, dy=1)
    result = a.perform()
    assert isinstance(result, MeleeAction)


