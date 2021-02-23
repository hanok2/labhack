import pytest

from .component import Component
from .attacks import Attack, AttackComponent


@pytest.fixture
def testattacks():
    return [
        Attack('bite', [8]),
        Attack('bite', [8]),
        Attack('kick', [6, 6])
    ]


def test_init__is_Component(testattacks):
    ac = AttackComponent(*testattacks)
    assert isinstance(ac, Component)


def test_init__tuple():
    atk = Attack('bite', [8])
    ac = AttackComponent(atk)
    assert ac.attacks == (atk,)  # Single tuple


def test_init__2_attacks_tuple_():
    atk = Attack('bite', [8])
    ac = AttackComponent(atk, atk)
    assert ac.attacks == (atk, atk)


def test_len(testattacks):
    ac = AttackComponent(*testattacks)
    assert len(ac) == 3


def test_init__single_attack():
    ac = AttackComponent(Attack('bite', [8]))
    assert len(ac) == 1
    assert isinstance(ac.attacks, tuple)


def test_init__roll_dies__1d1():
    result = AttackComponent.roll_dies([1])
    assert result == 1


def test_init__roll_dies__2d1():
    result = AttackComponent.roll_dies([1, 1])
    assert result == 2


def test_init__roll_dies__1d2():
    result = AttackComponent.roll_dies([2])
    assert result >= 1
    assert result <= 2


def test_min_dmg__1_die():
    atk = Attack('bite', [2])
    result = atk.min_dmg()
    assert result == 1


def test_min_dmg__2_die():
    atk = Attack('bite', [2, 2])
    result = atk.min_dmg()
    assert result == 2


def test_max_dmg__1_die():
    atk = Attack('bite', [2])
    result = atk.max_dmg()
    assert result == 2


def test_max_dmg__2_die():
    atk = Attack('bite', [2, 2])
    result = atk.max_dmg()
    assert result == 4


