from . import actions
from .melee import MeleeAction
from src import factory
from src import exceptions
from tests import toolkit
import pytest


@pytest.fixture
def test_map():
    return toolkit.test_map()


def test_MeleeAction_is_Action(test_map):
    player = test_map.player
    a = MeleeAction(entity=player, dx=1, dy=-1)
    assert isinstance(a, actions.Action)


def test_MeleeAction_is_ActionWithDirection(test_map):
    player = test_map.player
    a = MeleeAction(entity=player, dx=1, dy=-1)
    assert isinstance(a, actions.ActionWithDirection)


def test_MeleeAction_init(test_map):
    player = test_map.player
    a = MeleeAction(entity=player, dx=1, dy=-1)
    assert a.dx == 1
    assert a.dy == -1
    assert a.entity == player


def test_MeleeAction_perform__no_target__raises_Impossible(test_map):
    player = test_map.player
    a = MeleeAction(entity=player, dx=-1, dy=-1)
    with pytest.raises(exceptions.Impossible):
        a.perform()

# perform-Case: no target
# perform-Case: miss, calls miss
# perform-Case: hit w weapon, calls hit_with_weapon
# perform-Case: hit w hands, calls hit_withhands_


def test_MeleeAction_calc_target_number__positive_ac(test_map):
    player = test_map.player
    a = MeleeAction(entity=player, dx=-1, dy=-1)

    target = factory.orc
    assert target.attributes.ac == 7

    result = a.calc_target_number(target)
    expected = 10 + target.attributes.ac + player.level.current_level
    assert result == expected


def test_MeleeAction_calc_target_number__negative_ac(test_map):
    player = test_map.player
    a = MeleeAction(entity=player, dx=-1, dy=-1)

    target = factory.troll
    assert target.attributes.ac == -2

    result = a.calc_target_number(target)
    max_expected = 10 - 1 + player.level.current_level
    min_expected = 10 + target.attributes.ac + player.level.current_level

    assert result >= min_expected
    assert result <= max_expected


def test_MeleeAction_calc_target_number__negative_target_number(test_map):
    player = test_map.player
    a = MeleeAction(entity=player, dx=-1, dy=-1)

    target = factory.storm_drone
    assert target.attributes.ac == -20

    result = a.calc_target_number(target)
    assert result >= 1


def test_MeleeAction_roll_hit_die(test_map):
    player = test_map.player
    a = MeleeAction(entity=player, dx=-1, dy=-1)
    result = a.roll_hit_die()
    # Just testing that the random number is between 1 and the sides (usually
    # 20)
    assert result >= 1
    assert result <= a.die


def test_MeleeAction_hit_with_weapon__returns_dmg(test_map):
    player = test_map.player
    dagger = player.inventory.items.get('a')
    assert player.equipment.toggle_equip(dagger)

    a = MeleeAction(entity=player, dx=-1, dy=-1)
    target = factory.orc
    atk = player.equipment.slots['WEAPON'].equippable.attack.attacks[0]
    result = a.hit_with_weapon(target, atk)
    attack_max = sum(atk.dies)  # Sum all the dice in this attack
    assert result >= 1
    assert result <= attack_max


def test_MeleeAction_hit_with_weapon__msg__you_hit(test_map):
    player = test_map.player
    dagger = player.inventory.items.get('a')
    assert player.equipment.toggle_equip(dagger)

    a = MeleeAction(entity=player, dx=-1, dy=-1)
    target = factory.orc
    atk = player.equipment.slots['WEAPON'].equippable.attack.attacks[0]
    result = a.hit_with_weapon(target, atk)
    assert a.msg == f"You hit the Orc with your dagger for {result}! "


def test_MeleeAction_hit_with_barehands__returns_dmg(test_map):
    player = test_map.player
    assert not player.equipment.slots['WEAPON']

    a = MeleeAction(entity=player, dx=-1, dy=-1)
    target = factory.orc
    atk = player.attacks.attacks[0]
    result = a.hit_with_barehands(target, atk)
    attack_max = sum(atk.dies)
    assert result >= 1
    assert result <= attack_max


def test_MeleeAction_hit_with_barehands__msg(test_map):
    player = test_map.player
    a = MeleeAction(entity=player, dx=-1, dy=-1)
    target = factory.orc
    atk = player.attacks.attacks[0]
    result = a.hit_with_barehands(target, atk)
    assert a.msg == f"You punch the Orc for {result}! "


def test_MeleeAction_hit_with_barehands__msg__enemy_hits_you(test_map):
    target = test_map.player
    orc = factory.orc
    a = MeleeAction(entity=orc, dx=0, dy=1)
    atk = orc.attacks.attacks[0]
    result = a.hit_with_barehands(target, atk)
    assert a.msg == f"The Orc hits you for {result}! "


def test_MeleeAction_miss__player_misses(test_map):
    player = test_map.player
    a = MeleeAction(entity=player, dx=-1, dy=-1)
    target = factory.orc
    result = a.miss(target)
    assert a.msg == f"You miss the Orc. "


def test_MeleeAction_miss__enemy_misses_you(test_map):
    target = test_map.player
    orc = factory.orc
    a = MeleeAction(entity=orc, dx=0, dy=1)
    result = a.miss(target)
    assert a.msg == f"The Orc misses you. "


def test_MeleeAction_reduce_dmg__positive_ac_equals_no_reduction():
    orc = factory.orc
    assert orc.attributes.ac == 7
    result = MeleeAction.reduce_dmg(orc, 5)
    assert result == 5


def test_MeleeAction_reduce_dmg__negative_ac():
    troll = factory.troll
    assert troll.attributes.ac == -2
    result = MeleeAction.reduce_dmg(troll, 5)
    assert result == 3 or result == 4


def test_MeleeAction_reduce_dmg__ac_reduces_dmg_below_0__returns_1():
    stormdrone = factory.storm_drone
    assert stormdrone.attributes.ac == -20

    # Note: We'll only pass in 1 damage to test that damage can never be reduced below 1.
    # With any -AC, the defender will always try to reduce it to 0.
    result = MeleeAction.reduce_dmg(stormdrone, 1)
    assert result == 1
