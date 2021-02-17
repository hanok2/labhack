import random

DIRECTIONS = {
    'N': (0, -1),  # North
    'W': (-1, 0),  # West
    'E': (1, 0),  # East
    'S': (0, 1),  # South
}


class Cell:
    def __init__(self):
        self.visited = False
        self.path_n = None
        self.path_s = None
        self.path_w = None
        self.path_e = None


class Maze:
    """ This is the constructor for a 2D maze. """
    def __init__(self, width, height, start=(0, 0)):
        self.width = width
        self.height = height

        """ Options for maze construction
            1. Simple 1D list of ints 
            2. 2D array
            3. Dict: points and lists (of neighbors?)
        """

        # Initialize with Cell objects
        self.maze = [Cell() for _ in range(self.width * self.height)]

        self.stack = []  # Contains (x, y) pairs

        # Set first start cell
        self.stack.append(start)
        self.get_cell(*start).visited = True
        self.visited = 1

        """ For us to represent the maze cells onto a console grid, we need to account for path "walls"
            By using a path width of 3, we can bake that in without creating any more work.
            if C represents the cell, and | is the wall, each "Cell" is effectively translated like this: 
                CC|
                CC|
                |||
            
            We only need to be concerned with digging on the eastern and southern walls.
            The relationship to the console is: 
                (Cell Coordinate * 2) + 1
        """
        self.path_width = 2

    def get_cell(self, x, y):
        return self.maze[self.width * y + x]

    def create_maze(self):
        # Depth first search
        turns = 0
        while self.visited < len(self.maze):
            # Create a set of the unvisited neighbors
            x = self.stack[-1][0]
            y = self.stack[-1][1]
            neighbors = self.get_neighbors(x, y)

            # Are there any unvisited neighbors available?
            if neighbors:
                # Pick one at random.
                next_dir = random.choice(list(neighbors.keys()))
                new_coords = neighbors[next_dir]

                print(f"\tNeighbors: {neighbors} -- picked {next_dir} {new_coords}")

                # Create a path between the neighbor and the current cell.
                if next_dir == 'N':
                    # Set the path north on the current cell
                    self.get_cell(x, y).path_n = neighbors[next_dir]
                    # Set the path south on the destination
                    self.get_cell(*new_coords).path_s = x, y

                elif next_dir == 'S':
                    # Set the path south on the current cell
                    self.get_cell(x, y).path_s = neighbors[next_dir]
                    # Set the path north on the destination
                    self.get_cell(*new_coords).path_n = x, y

                elif next_dir == 'E':
                    # Set the path east on the current cell
                    self.get_cell(x, y).path_e = neighbors[next_dir]
                    # Set the path west on the destination
                    self.get_cell(*new_coords).path_w = x, y

                elif next_dir == 'W':
                    # Set the path west on the current cell
                    self.get_cell(x, y).path_w = neighbors[next_dir]
                    # Set the path east on the destination
                    self.get_cell(*new_coords).path_e = x, y

                # Push the next cell to the stack
                self.stack.append(new_coords)

                self.visited += 1
            else:
                # No neighbors = backtrack!
                self.stack.pop()

            # Mark the current cell as visited
            self.get_cell(x, y).visited = True  # ???

            print('')
            turns += 1

    def get_neighbors(self, x, y):
        # We'll build up a dict of directions and resulting coordinates.
        # If there isn't a valid coordinate we don't add it.
        neighbors = {}

        for d in DIRECTIONS:
            # Use the directions dict to lookup the dx and dy change.
            dest_x = x + DIRECTIONS[d][0]
            dest_y = y + DIRECTIONS[d][1]

            # Make sure the destination is not out of bounds. If it is, we'll just return None
            if dest_x < 0 or dest_y < 0:
                continue
            if dest_x >= self.width or dest_y >= self.height:
                continue

            # If the destination cell has not been visited, we'll return it as a valid neighbor.
            if not self.get_cell(dest_x, dest_y).visited:
                neighbors[d] = (dest_x, dest_y)

        return neighbors

    def draw(self):
        max_width = self.width * (self.path_width + 1)
        max_height = self.height * (self.path_width + 1)
        console = [['#' for x in range(max_width)] for y in range(max_height)]

        for x in range(self.width):
            for y in range(self.height):

                # Each cell is inflated by m_nPathWidth, so fill it in
                for py in range(self.path_width):
                    for px in range(self.path_width):

                        if self.maze[y * self.width + x].visited:
                            # Draw Cell
                            console[y * (self.path_width + 1) + py][x * (self.path_width + 1) + px] = '.'
                        # else:
                            # Draw Cell (What is the purpose of this? Draw unvisited cells?
                            # console[y * (self.path_width + 1) + py][x * (self.path_width + 1) + px] = ','

                # Draw passageways between cells
                for p in range(self.path_width):
                    if self.maze[y * self.width + x].path_s:
                        # Draw South Passage
                        console[y * (self.path_width + 1) + self.path_width][x * (self.path_width + 1) + p] = '.'

                    if self.maze[y * self.width + x].path_e:
                        # Draw East Passage
                        console[y * (self.path_width + 1) + p][x * (self.path_width + 1) + self.path_width] = '.'

        for y in console:
            print(''.join(y))


if __name__ == "__main__":
    m = Maze(width=30, height=10)
    m.create_maze()
    m.draw()
