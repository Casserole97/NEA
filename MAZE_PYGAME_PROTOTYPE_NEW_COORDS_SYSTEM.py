import pygame
from random import choice, random
pygame.init()

# REMEMBER THE DIFFERENCE BETWEEN CARTESIAN AND ROW/COLUMN
#  X 0 1 2 3 4   |  C 0 1 2 3 4
# Y              | R
# 0              | 0
# 1              | 1
# 2              | 2
# 3              | 3
# 4              | 4

#Declaring variables
MAX_WIDTH = 1000
MAX_HEIGHT = 800

#Creating surface to draw on
DisplaySurface = pygame.display.set_mode((MAX_WIDTH, MAX_HEIGHT))
DisplaySurface.fill(pygame.Color("white"))
pygame.display.set_caption("test")

#Basic class that acts as a coordinate on a map.
#Only needed for other classes to inherit from.
class Tile():
    def __init__(self, row, y):
        self.row = row
        self.y = y

    #Return row and y.
    def GetPos(self):
        return self.row, self.y

#A tile that cannot be walked through.
class Wall(Tile):
    def __init__(self, row, y):
        super().__init__(row, y)
        self.type = "WALL"

#A tile that can be walked through. It acts as the nodes of a graph.
class Cell(Tile):
    def __init__(self, row, y):
        super().__init__(row, y)
        self.type = "CELL"
        self.visited = False

    #Return a boolean.
    def IsVisited(self):
        return self.visited
    
    #Change the visited status.
    def Visit(self):
        self.visited = True

#The passage class is used to indiciate a connection between cells, acts as
#the edges of a graph.
class Passage(Tile):
    def __init__(self, row, y):
        super().__init__(row, y)
        self.type = "PASSAGE"

#The grid class is basically a two dimensional array with special methods.
#Each space will hold either a wall, a cell, or a passage.
class Maze():
    def __init__(self, horizontal_cells, vertical_cells, tile_size):
        self.MAX_HOR_TILES = horizontal_cells*2+1
        self.MAX_VER_TILES = vertical_cells*2+1
        self.tile_size = tile_size
        self.total_hor_pixels = (horizontal_cells*2+1)*tile_size
        self.total_ver_pixels = (vertical_cells*2+1)*tile_size
        #Initialize a blank grid of walls and cells.
        self.grid = [[self.__GenerateCellorWall(x, y) for x in range(0, self.MAX_HOR_TILES)] for y in range(0, self.MAX_VER_TILES)]
        
    #Method used in the init of the grid.
    def __GenerateCellorWall(self, x, y):
        if x % 2 != 0 and y % 2 != 0:
            return Cell(x, y)
        else:
            return Wall(x, y)
    
    #Displays the maze in a textual form.
    def DisplayMaze(self):
        for x in self.grid:
            print()
            for tile in x:
                if tile.type == "WALL":
                    print('H ', end='')
                else:
                    print('  ', end='')
    
    #Returns the surface on which the maze is graphically drawn.
    def DrawMaze(self):
        maze_surf = pygame.Surface((self.total_hor_pixels, self.total_ver_pixels))
        maze_surf.fill(pygame.Color("white"))
        count1 = 0
        count2 = 0
        for x in self.grid:
            for tile in x:
                if tile.type == "WALL":
                    pygame.draw.rect(maze_surf, pygame.Color("black"), pygame.Rect(count1, count2, self.tile_size, self.tile_size))
                count1 += self.tile_size
            count1 = 0
            count2 += self.tile_size
        return maze_surf
        
    #Return the tile on that x and y.
    def GetTile(self, x, y):
        return self.grid[x][y]
    
    #Returns a list of adjacent unvisited neighbours of a cell.
    def GetUnvisitedNeighbours(self, cell):
        unvisited_neighbours = []
        x, y = cell.GetPos()
        N = -2
        E = 2
        S = 2
        W = -2
        try:
            if not self.GetTile(x+N, y).IsVisited():
                unvisited_neighbours.append(self.GetTile(x+N, y))
        except:
            pass
        try:
            if not self.GetTile(x, y+E).IsVisited():
                unvisited_neighbours.append(self.GetTile(x, y+E))
        except:
            pass
        try:
            if not self.GetTile(x+S, y).IsVisited():
                unvisited_neighbours.append(self.GetTile(x+S, y))
        except:
            pass
        try:
            if not self.GetTile(x, y+W).IsVisited():
                unvisited_neighbours.append(self.GetTile(x, y+W))
        except:
            pass
        return unvisited_neighbours
    
    #Changes the wall between two cells to a passage.
    def CarvePassage(self, cell1, cell2):
        x = (cell1.x + cell2.x) // 2
        y = (cell1.y + cell2.y) // 2
        self.grid[x][y] = Passage(x, y)
    
    #Recursive backtracker algorithm.
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

maze1 = Maze(5, 10, 15)
# maze1.RecursiveBacktracker(maze1.GetTile(1, 1), 0.0)
# Maze = maze1.DrawMaze()
# DisplaySurface.blit(Maze, ((MAX_WIDTH-maze1.total_hor_pixels)//2, (MAX_HEIGHT-maze1.total_ver_pixels)//2))
maze1.DisplayMaze()

clock = pygame.time.Clock()
pygame.display.flip()

#Game loop
# running = True
# while running:
#     for event in pygame.event.get():
#         if event.type == pygame.KEYDOWN:
#             if event.key == pygame.K_ESCAPE:
#                 running = False
#         if event.type == pygame.QUIT:
#             running = False
    
#     clock.tick(60)

pygame.quit()
