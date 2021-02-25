import pytest
from src.entity import Entity
import toolkit


@pytest.fixture
def test_map():
    return toolkit.test_map()


def test_init__defaults__always_has_parent_component():
    e = Entity()
    assert e.parent is None


def test_init__components_dict():
    e = Entity(x=0, y=0)
    assert e.components == {'parent': None, 'x': 0, 'y': 0}


def test_str__has_name():
    e = Entity(name='Player')
    assert str(e) == 'Player'


def test_str__unnamed():
    e = Entity(x=0, y=0)
    assert str(e) == 'Unnamed'


def test_init__add_comp__1_kwarg():
    e = Entity(x=0)
    e.add_comp(y=1)
    assert e.components['y'] == 1


def test_init__add_comp__2_kwargs():
    e = Entity(x=0, y=1)
    e.add_comp(a=1, b=2)
    assert e.components['a'] == 1
    assert e.components['b'] == 2


def test_init__add_comp__already_exists_and_replaces():
    e = Entity(x=0, y=1)
    e.add_comp(x=1)
    e.add_comp(x=2)
    assert e.components['x'] == 2


def test_contains__init_args():
    e = Entity(x=0, y=1)
    assert 'x' in e
    assert 'y' in e


def test_init__rm_comp__success_removes_component():
    e = Entity(x=0, y=1)
    e.rm_comp('x')
    assert 'x' not in e.components


def test_init__rm_comp__success_returns_True():
    e = Entity(x=0, y=1)
    result = e.rm_comp('x')
    assert result


def test_init__rm_comp__fail_returns_False():
    e = Entity(x=0, y=1)
    assert e.rm_comp('z') is False
    # Raise exception?


def test_init__getattr__returns_component_value():
    e = Entity(x=0, y=1)
    assert e.x == 0


def test_init__getattr__DNE_returns_None():
    e = Entity(x=0, y=0)
    with pytest.raises(AttributeError):
        result = e.z


def test_move():
    e = Entity(x=0, y=0)
    e.move(1, 1)
    assert e.x == 1
    assert e.y == 1


def test_spawn__creates_clone(test_map):
    e = Entity(name='cloner')
    result = e.spawn(test_map, 2, 3)
    # Should be a clone
    assert e.name == result.name

    # Not an exact clone thogh
    assert result != e
    assert result is not e


def test_spawn__not_exact_clone(test_map):
    e = Entity(name='cloner')
    result = e.spawn(test_map, 2, 3)
    assert result != e
    assert result is not e


def test_spawn__in_gamemap_entities(test_map):
    e = Entity()
    result = e.spawn(test_map, 2, 3)
    assert result in test_map


def test_spawn__xy(test_map):
    e = Entity()
    result = e.spawn(test_map, 2, 3)
    assert result.x == 2
    assert result.y == 3


def test_distance__same_point():
    e = Entity(x=0, y=0)
    assert e.x == 0
    assert e.y == 0
    assert e.distance(0, 0) == 0


def test_distance__1_tile_away():
    e = Entity(x=0, y=0)
    assert e.distance(1, 0) == 1


def test_distance__1_diagonal_tile_away():
    e = Entity(x=0, y=0)
    result = e.distance(1, 1)
    result = round(result, 2)  # Round to 2 decimal places
    assert result == 1.41
