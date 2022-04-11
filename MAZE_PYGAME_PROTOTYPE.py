import pygame
from random import choice, random
pygame.init()

# REMEMBER THE DIFFERENCE BETWEEN X/Y AND ROW/COLUMN
#  X 0 1 2 3 4   |  C 0 1 2 3 4
# Y              | R
# 0              | 0
# 1              | 1
# 2              | 2
# 3              | 3
# 4              | 4

# Declaring variables
MAX_WIDTH = 1000
MAX_HEIGHT = 800

# Creating the surface which will be displayed
DisplaySurface = pygame.display.set_mode((MAX_WIDTH, MAX_HEIGHT))
DisplaySurface.fill(pygame.Color("white"))
pygame.display.set_caption("test")

# Basic class that acts as a coordinate on a map.
# Only needed for other classes to inherit from, will never be placed
# on the grid.
class Tile():
    def __init__(self, row, col):
        self.row = row
        self.col = col

    # Return row and column.
    def GetPos(self):
        return self.row, self.col

# A tile that cannot be walked through.
class Wall(Tile):
    def __init__(self, row, col):
        super().__init__(row, col)
        self.type = "WALL"

# A tile that can be walked through. It acts as the nodes of a graph.
class Cell(Tile):
    def __init__(self, row, col):
        super().__init__(row, col)
        self.type = "CELL"
        self.visited = False

    # Return a boolean.
    def IsVisited(self):
        return self.visited

    # Change the visited status.
    def Visit(self):
        self.visited = True

# The passage class is used to indiciate a connection between cells, acts as
# the edges of a graph.
class Passage(Tile):
    def __init__(self, row, col):
        super().__init__(row, col)
        self.type = "PASSAGE"

# The grid class is basically a two dimensional array with special methods.
# Each space will hold either a wall, a cell, or a passage.
class Grid():
    def __init__(self, vertical_cells, horizontal_cells, tile_pixels):
        # Maximum vertical and horizontal tiles in the maze.
        self.MAX_VER_TILES = vertical_cells*2+1
        self.MAX_HOR_TILES = horizontal_cells*2+1
        # The lengths of the sides of a tile square in pixels.
        self.tile_pixels = tile_pixels
        # Total vertical and horizontal pixels used for the surface on which
        # the maze will be drawn.
        self.total_ver_pixels = self.MAX_VER_TILES*tile_pixels
        self.total_hor_pixels = self.MAX_HOR_TILES*tile_pixels
        # Initialize a blank grid of walls and cells.
        self.grid = [[self.__GenerateCellorWall(row, col) for col in range(0, self.MAX_HOR_TILES)] for row in range(0, self.MAX_VER_TILES)]

    # Method used in the init of the grid.
    def __GenerateCellorWall(self, row, col):
        if row % 2 != 0 and col % 2 != 0:
            return Cell(row, col)
        else:
            return Wall(row, col)

    # Displays the maze in a textual form.
    def PrintMaze(self):
        for row in self.grid:
            print()
            for tile in row:
                if tile.type == "WALL":
                    print('H ', end='')
                else:
                    print('  ', end='')

    # A maze is drawn on a new surface which is then returned.
    def DrawMaze(self):
        maze_surf = pygame.Surface((self.total_hor_pixels, self.total_ver_pixels))
        maze_surf.fill(pygame.Color("white"))
        count1 = 0
        count2 = 0
        for row in self.grid:
            for tile in row:
                if tile.type == "WALL":
                    pygame.draw.rect(maze_surf, pygame.Color("black"), pygame.Rect(count1, count2, self.tile_pixels, self.tile_pixels))
                count1 += self.tile_pixels
            count1 = 0
            count2 += self.tile_pixels
        return maze_surf

    # Return the tile on that row and column.
    def GetTile(self, row, col):
        return self.grid[row][col]

    # Returns a list of unvisited neighbours of a cell.
    def GetUnvisitedNeighbours(self, cell):
        unvisited_neighbours = []
        row, col = cell.GetPos()
        N = -2
        E = 2
        S = 2
        W = -2
        try:
            if not self.GetTile(row+N, col).IsVisited():
                unvisited_neighbours.append(self.GetTile(row+N, col))
        except:
            pass
        try:
            if not self.GetTile(row, col+E).IsVisited():
                unvisited_neighbours.append(self.GetTile(row, col+E))
        except:
            pass
        try:
            if not self.GetTile(row+S, col).IsVisited():
                unvisited_neighbours.append(self.GetTile(row+S, col))
        except:
            pass
        try:
            if not self.GetTile(row, col+W).IsVisited():
                unvisited_neighbours.append(self.GetTile(row, col+W))
        except:
            pass
        return unvisited_neighbours

    # Changes the wall between two cells to a passage.
    def CarvePassage(self, cell1, cell2):
        row = (cell1.row + cell2.row) // 2
        col = (cell1.col + cell2.col) // 2
        self.grid[row][col] = Passage(row, col)

    # Recursive backtracker algorithm.
    def RecursiveBacktracker(self, cell, loop_chance):
        neighbours = self.GetUnvisitedNeighbours(cell)
        cell.Visit()
        while len(neighbours) != 0:
            next_cell = choice(neighbours)
            neighbours.remove(next_cell)
            if not next_cell.IsVisited(): 
                self.CarvePassage(cell, next_cell)
            elif random() < loop_chance:
                self.CarvePassage(cell, next_cell)
            self.RecursiveBacktracker(next_cell, loop_chance)

# Created a maze object, invoked recursive backtracker, drew the maze, blitted it, and flipped the display.
maze1 = Grid(12, 12, 20)
maze1.RecursiveBacktracker(maze1.GetTile(1, 1), 0.0)
maze_surface = maze1.DrawMaze()
DisplaySurface.blit(maze_surface, ((MAX_WIDTH-maze1.total_hor_pixels)//2, ((MAX_HEIGHT-maze1.total_ver_pixels)//2)))
pygame.display.flip()

# Created a clock object.
clock = pygame.time.Clock()

# Game loop
running = True
while running:
    # If ESC is pressed or the window is closed, the process quits.
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
        if event.type == pygame.QUIT:
            running = False

    # Makes the game run at 60 FPS.
    clock.tick(60)

pygame.quit()
