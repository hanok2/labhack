import math

import numpy as np

from . import tiles
from . import factory
from . import gamemap
from . import rect
from . import settings
import random
import tcod

# Break up methods
# mk_rooms: Create a set of rooms and dig them out of a map
# tunnel_between
# Place entity?
from .rect import Door


def place_items(room, dungeon, floor_number):
    number_of_items = random.randint(
        0, get_max_value_for_floor(settings.max_items_by_floor, floor_number)
    )

    items = get_entities_at_random(
        factory.item_chances, number_of_items, floor_number
    )

    for entity in items:
        x, y = room.random_point_inside()
        # x = random.randint(room.x1 + 1, room.x2 - 2)
        # y = random.randint(room.y1 + 1, room.y2 - 2)
        # We don't care if they stack on the map
        entity.spawn(dungeon, x, y)


def place_monsters(room, dungeon, floor_number):
    number_of_monsters = random.randint(
        0, get_max_value_for_floor(settings.max_monsters_by_floor, floor_number)
    )

    monsters = get_entities_at_random(
        factory.enemy_chances, number_of_monsters, floor_number
    )

    for entity in monsters:
        x = random.randint(room.x1 + 1, room.x2 - 2)
        y = random.randint(room.y1 + 1, room.y2 - 2)

        # Don't spawn them on top of each other.
        if not any(entity.x == x and entity.y == y for entity in dungeon.entities):
            entity.spawn(dungeon, x, y)


def generate_map(max_rooms, room_min_size, room_max_size, map_width, map_height, engine):
    """Generate a new dungeon map with rooms, corridors, and stairs.."""
    new_map = gamemap.GameMap(engine, map_width, map_height)

    # Create all the rects for the rooms
    generate_rooms(new_map, max_rooms, room_min_size, room_max_size)

    # Create the room coordinates for easy reference.
    new_map.room_coords = new_map.room_coordinates()

    # Use some algorithm to connect the rooms.
    # Requirement: All rooms must be connected somehow and reachable by some means.
    connecting_algorithm(new_map)

    # Put the upstair in the first room generated
    center_of_first_room = new_map.rooms[0].center
    new_map.tiles[center_of_first_room] = tiles.up_stairs
    new_map.upstairs_location = center_of_first_room

    # Put the downstair in the last room generated
    center_of_last_room = new_map.rooms[-1].center
    new_map.tiles[center_of_last_room] = tiles.down_stairs
    new_map.downstairs_location = center_of_last_room
    return new_map


def connecting_algorithm(new_map):
    print('-----------------------------------')

    # First connect rooms with a minimum spanning tree.
    edges = minimum_spanning_tree(new_map.rooms)
    for room1, room2 in edges:
        connect_room_to_room(new_map, room1, room2)

    # Extras
    # Connect 1 extra random room.
    # We'll try to add 1/2 of the room count as extra connections.
    extra_connections = len(new_map.rooms) // 2

    print('Connecting extra rooms')
    for i in range(extra_connections):
        room1 = random.choice(new_map.rooms)
        room2 = get_nearest_unconnected_room(new_map, room1)
        connect_room_to_room(new_map, room1, room2)

    # Draw doors last
    draw_doors(new_map)

    # Print list of rooms and connections
    # print('Room connections')
    # for c in new_map.rooms:
    #     print(f"Room {c.label}: {c.connections}")


def draw_doors(new_map):
    """ Drawing doors needs to be a separate activity done last after corridors, because if it's combined with
    corridor drawing, there are conflicts in where doors and floor appear.
    """
    for d in new_map.doors:
        # print(f"Door: {d.x, d.y}")
        valid_door = True
        for direction in settings.CARDINAL_DIR.values():
            dx, dy = direction

            # Check around for other doors.
            if new_map.tiles[d.x + dx][d.y + dy] == tiles.door:
                print('Abort door creation!!!!!')
                # Oh no, a door is adjacent! Abort mission!
                valid_door = False
                continue

        if valid_door:
            new_map.tiles[d.x, d.y] = tiles.door

            # Is the closet wall yet?
            closet_x, closet_y = d.closet()
            if new_map.tiles[closet_x, closet_y] == tiles.wall:
                # Dig out the closet
                new_map.tiles[closet_x, closet_y] = tiles.floor


def connect_room_to_room(new_map, room1, room2):
    connected = False

    # Find all the possible door locations in the 2 rooms
    # Find all the pairs of doors that face eachother.
    facing_doors = match_facing_doors(room1, room2)

    if facing_doors:
        closest_pair = get_closest_pair_of_doors(facing_doors)

        pair = get_valid_pair_of_doors(facing_doors)
        if pair:
            print(f'Facing Pair! {room1.label}->{room2.label}')
        else:
            print(f'Closest pair! {room1.label}->{room2.label}')
            pair = closest_pair

        door1, door2 = pair
        connected = connect_2_doors(new_map, door1, door2)

    if not connected:
        # Either: we don't have facing doors, or the first connector didn't work.
        print(f'A* tunnel! {room1.label}->{room2.label}')
        tries = 0
        while not connected and tries < 100:
            tries += 1
            # We'll allow a lot of tries before we give up
            print(f'Try {tries}')
            # Get a random set of doors
            door1 = rect.Door(room1, *room1.random_door_loc())
            door2 = rect.Door(room2, *room2.random_door_loc())

            # TODO: Check that the new doors are valid.
            if not new_map.valid_door_location(room1, door1.x, door1.y):
                print('invalid door')
                continue
            if not new_map.valid_door_location(room2, door2.x, door2.y):
                print('invalid door')
                continue

            connected = tunnel_astar(new_map, door1, door2)


    if connected:
        # Dig out adjacent doors
        if distance(door1.x, door1.y, door2.x, door2.y) == 1:
            # If the doors are next to eachother, just leave it as floor.
            new_map.tiles[door1.x, door1.y] = tiles.floor
            new_map.tiles[door2.x, door2.y] = tiles.floor
        else:
            new_map.doors.append(door1)
            new_map.doors.append(door2)

        # Add the rooms to each-other's list of connections
        room1.connections.append(room2.label)
        room2.connections.append(room1.label)
    else:
        print(f'Could not connect rooms {room1.label} and {room2.label}')


def get_valid_pair_of_doors(matches):
    """ Iterates through a list of facing doors and picks until we find a valid choice.
    """
    while matches:
        # Choose a pair at random.
        pair = random.choice(matches)

        # Remove it from the list
        matches.remove(pair)

        door1, door2 = pair

        # We have to check that these are not lined up so that the closets are over-extended
        x_diff = abs(door1.x - door2.x)
        y_diff = abs(door1.y - door2.y)

        # Hopefully we only have to test one door to see if they are facing vertically or horizontally.

        if door1.facing in ['S', 'N'] and y_diff == 1:
            # Vertical facing: If the y-difference is 1, the x-difference has to be 0 (aligned)
            if x_diff == 0:
                return pair
            continue

        if door1.facing in ['E', 'W'] and x_diff == 1:
            # Horizontal facing: If the x-difference is 1, the y-difference has to be 0 (aligned)
            if x_diff == 0:
                return pair
            continue

        # If the pair passes the above tests, it should be okay.
        return pair


def connect_2_doors(new_map, door1, door2):
    # Get the closets outside the doors
    x1, y1 = door1.closet()
    x2, y2 = door2.closet()

    # Choose a method of creating the tunnel:
    # Draw an L tunnel
    path = tunnel_between((x1, y1), (x2, y2))
    # print((x1, y1), (x2, y2))
    # print(path)

    # Draw a diagonal
    # path = diagonal_tunnel(start, end):

    # First: Check the path to make sure it doesn't have major conflicts (walls, corners)
    for x, y in path:
        # Stop drawing if we run into room corners.
        if new_map.tiles[x, y] in tiles.room_corners:
            return False

        # Do not draw over inner room floors
        if new_map.tiles[x, y] == tiles.room_floor:
            return False

    # Dig out a tunnel between this room and the previous one.
    for x, y in path:
        # Also stop drawing if we run into a corridor floor.
        # if new_map.tiles[x, y] == tiles.floor:
            # However, we'll count this as a connection since we made it to the corridor.
            # return True

        new_map.tiles[x, y] = tiles.floor

    return True


def tunnel_astar(new_map, door1, door2):
    # Get the closets outside the doors
    x1, y1 = door1.closet()
    x2, y2 = door2.closet()

    # A* path
    path = get_path_to(new_map, x1, y1, x2, y2)
    print(path)
    # If we get a single point - the path is not able to complete
    # This can cause infinite loops - some maps are not able to be totally connected.
    if len(path) == 1:
        return False

    # Check all points first (A* already will not draw over floor.
    for point in path:
        x, y = point

        # We won't allow drawing over room walls or doors.
        if new_map.tiles[x, y] in tiles.room_walls:
            return False

    for point in path:
        new_map.tiles[point] = tiles.floor

    return True


def get_all_possible_doors_in_room(room):
    walls = room.perimeter().difference(room.corners())
    return [Door(room, x, y) for x, y in walls]


def match_facing_doors(room1, room2):
    # room1_walls = room1.perimeter().difference(room1.corners())
    # room2_walls = room2.perimeter().difference(room2.corners())
    # room1_doors = [Door(room1, x, y) for x, y in room1_walls]
    # room2_doors = [Door(room2, x, y) for x, y in room2_walls]
    room1_doors = get_all_possible_doors_in_room(room1)
    room2_doors = get_all_possible_doors_in_room(room2)

    matches = []

    for a in room1_doors:
        for b in room2_doors:
            if a.facing_other(b):
                matches.append({a, b})
    return matches


def get_closest_pair_of_doors(matches):
    # Find the pair of doors that are the closest in distance.
    closest_pair = None
    record = 10000000000
    for pair in matches:
        door1, door2 = pair
        dist_between = distance(door1.x, door1.y, door2.x, door2.y)
        if dist_between < record:
            record = dist_between
            closest_pair = pair
    return closest_pair


def get_nearest_unconnected_room(new_map, room):
    # Use tiles_around to look for a tiles that belong to rooms.
    # Keep pushing outward until we find a room that is not connected to this room.
    # If we find 2+ rooms, choose at random.
    x, y = room.center

    # The maximum radius so we don't look out of bounds
    min_radius = 3
    # max_radius = min(new_map.height - y, new_map.width - x, x, y)

    for r in range(min_radius, new_map.height):
        # Get all the tiles in the new radius
        surrounding_tiles = new_map.tiles_around(x, y, r)

        for st in surrounding_tiles:
            # Check each tile and see if it belongs to a room.
            result = new_map.room_coords.get(st)
            if not result:
                continue
            # Make sure it's not the same room we are looking out from.
            if room.label == result.label:
                continue
            # Make sure it's not connected to this room already.
            if result.label in room.connections:
                continue

            # Passed all checks!
            return result


def populate_map(new_map, engine):
    # Place entities
    for room in new_map.rooms:
        # Populate the room with monsters and items
        place_monsters(room, new_map, engine.game_world.current_floor)
        place_items(room, new_map, engine.game_world.current_floor)


def generate_rooms(new_map, max_rooms, room_min_size, room_max_size):
    for r in range(max_rooms):
        new_room = mk_room(new_map, room_min_size, room_max_size)

        # Run through the other rooms and see if they intersect with this one.
        if any(new_room.intersects(other_room) for other_room in new_map.rooms):
            continue  # This room intersects, so go to the next attempt.

        # If there are no intersections then the room is valid.

        # Dig out this rooms inner area.
        new_map.tiles[new_room.inner] = tiles.room_floor

        # Draw walls
        for point in new_room.horz_walls():
            new_map.tiles[point] = tiles.room_horz_wall
        for point in new_room.vert_walls():
            new_map.tiles[point] = tiles.room_vert_wall

        # Draw corners (must be ordered after walls)
        new_map.tiles[new_room.ne_corner] = tiles.room_ne_corner
        new_map.tiles[new_room.nw_corner] = tiles.room_nw_corner
        new_map.tiles[new_room.se_corner] = tiles.room_se_corner
        new_map.tiles[new_room.sw_corner] = tiles.room_sw_corner

        # Label the room to match it's index in new_map.rooms
        label = len(new_map.rooms)
        new_room.label = label

        # Add this room to the map's list.
        new_map.rooms.append(new_room)


def mk_room(new_map, min_size, max_size):
    room_width = random.randint(min_size, max_size)
    room_height = random.randint(min_size, max_size)

    x = random.randint(0, new_map.width - room_width - 1)
    y = random.randint(0, new_map.height - room_height - 1)

    return rect.Rect(x, y, room_width, room_height)


def tunnel_between(start, end, twist=0):
    """ Return an L-shaped tunnel between these two points.
        If the lines are on the same x-axis or y-axis it will simply draw a straight line.
        start: Tuple[int, int],
        end: Tuple[int, int]
        returns Iterator[Tuple[int, int]]:
    """
    x1, y1 = start
    x2, y2 = end

    if twist == 0:
        twist = random.randint(1, 2)

    if twist == 1:  # 50% chance.
        corner_x, corner_y = x2, y1  # Move horizontally, then vertically.
    else:
        corner_x, corner_y = x1, y2  # Move vertically, then horizontally.

    # Generate the coordinates for this tunnel.
    # line-of-sight module: draws Bresenham lines.
    coordinates = []
    for x, y in tcod.los.bresenham((x1, y1), (corner_x, corner_y)).tolist():
        coordinates.append((x, y))

    # There will be a duplicate value from the corner point, we want to remove this!
    for x, y in tcod.los.bresenham((corner_x, corner_y), (x2, y2)).tolist()[1:]:
        coordinates.append((x, y))
    return coordinates


def diagonal_tunnel(start, end):
    # Generate the coordinates for this tunnel.
    # line-of-sight module: draws Bresenham lines.
    x1, y1 = start
    x2, y2 = end
    coordinates = []
    for x, y in tcod.los.bresenham((x1, y1), (x2, y2)).tolist():
        coordinates.append((x, y))
    return coordinates


def get_max_value_for_floor(weighted_chances_by_floor, floor):
    current_value = 0

    for floor_minimum, value in weighted_chances_by_floor:
        if floor_minimum > floor:
            break
        else:
            current_value = value

    return current_value


def get_entities_at_random(weighted_chances_by_floor, number_of_entities, floor):
    """ This function goes through they keys (floor numbers) and values (list of
        weighted entities), stopping when the key is higher than the given floor
        number. It sets up a dictionary of the weights for each entity, based on
        which floor the player is currently on. So if we were trying to get the
        weights for floor 6, entity_weighted_chances would look like this:
            { orc: 80, troll: 30 }.

        Then, we get both the keys and values in list format, so that they can
        be passed to random.choices (it accepts choices and weights as lists).
        k represents the number of items that random.choices should pick, so we
        can simply pass the number of entities we’ve decided to generate. Finally,
        we return the list of chosen entities.
    """
    entity_weighted_chances = {}

    for key, values in weighted_chances_by_floor.items():
        if key > floor:
            break
        else:
            for value in values:
                entity = value[0]
                weighted_chance = value[1]

                entity_weighted_chances[entity] = weighted_chance

    entities = list(entity_weighted_chances.keys())
    entity_weighted_chance_values = list(entity_weighted_chances.values())

    chosen_entities = random.choices(
        entities, weights=entity_weighted_chance_values, k=number_of_entities
    )

    return chosen_entities


def get_path_to(_map, start_x, start_y, dest_x, dest_y):
    """ Compute and return a path to the target position.
        If there is no valid path then returns an empty list.
        See components.ai.BaseAI.get_path_to for full comments.
    """
    cost = np.array(_map.tiles["diggable"], dtype=np.int8)

    # Create a graph from the cost array and pass that graph to a new pathfinder.
    graph = tcod.path.SimpleGraph(cost=cost, cardinal=2, diagonal=0)
    pathfinder = tcod.path.Pathfinder(graph)

    pathfinder.add_root((start_x, start_y))  # Start position.

    # Compute the path to the destination (remove starting point.)
    # path = pathfinder.path_to((dest_x, dest_y))[1:-1].tolist()
    path = pathfinder.path_to((dest_x, dest_y)).tolist()

    # Convert from List[List[int]] to List[Tuple[int, int]].
    return [(index[0], index[1]) for index in path]


def minimum_spanning_tree(rooms):
    """ Connects all the rooms by using Prim's Algorithm

    :return: A list of all the edges (room to room connections)
    """
    edges = []
    visited = []
    unvisited = rooms[:]   # Copy all vertices to this list.

    # Random start point.
    start = unvisited[0]
    visited.append(start)
    unvisited.pop(0)  # Remove the start point from the unvisited list.

    while len(unvisited) > 0:
        record = 100000   # A very high number, maybe even max
        r_match = None
        u_match = None

        for r in visited:
            for u in unvisited:
                x1, y1 = r.center
                x2, y2 = u.center
                dist = distance(x1, y1, x2, y2)

                if dist < record:
                    record = dist
                    r_match = r
                    u_match = u

        edges.append((r_match, u_match))

        # Take the u_match out of unvisited and put it into visited.
        visited.append(u_match)
        unvisited.remove(u_match)

    return edges


def distance(x1, y1, x2, y2):
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)