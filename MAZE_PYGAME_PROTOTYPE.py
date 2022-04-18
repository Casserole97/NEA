import pygame
from random import choice, random, randint
pygame.init()

# REMEMBER THE DIFFERENCE BETWEEN X/Y AND ROW/COLUMN.
#  X 0 1 2 3 4   |  C 0 1 2 3 4
# Y              | R
# 0              | 0
# 1              | 1
# 2              | 2
# 3              | 3
# 4              | 4

# Declaring constants.
# Size of the screen.
MAX_WIDTH = 800
MAX_HEIGHT = 600

# Colours to be used in the game.
COLOUR1 = (255, 255, 255)
COLOUR2 = (0, 0, 0)
COLOUR3 = (128, 128, 128)

# The size, in pixels, of a side of each individual square tile. Important
# constant, as many variables will depend on it.
TILE_PIXELS = 20

# Four sprite groups to which the respective sprites will be added to.
TILES = pygame.sprite.Group()
WALLS = pygame.sprite.Group()
CELLS = pygame.sprite.Group()
PSSGS = pygame.sprite.Group()

# Creating the screen which will be displayed.
DISPLAY_SURFACE = pygame.display.set_mode((MAX_WIDTH, MAX_HEIGHT))
DISPLAY_SURFACE.fill(COLOUR2)
pygame.display.set_caption("yooo pog pog pog")

# Sprite that acts as a row/column coordinate on the grid.
# Only needed for other classes to inherit from, will never be placed
# on the grid.
class Tile(pygame.sprite.Sprite):
    def __init__(self, row, col):
        super().__init__()
        self.row = row
        self.col = col
        self.image = pygame.Surface((TILE_PIXELS, TILE_PIXELS))
        self.rect = self.image.get_rect()
        TILES.add(self)

    # Return the row and column in the grid on which the tile resides.
    def GetPos(self):
        return self.row, self.col

# A tile that cannot be walked through.
class Wall(Tile):
    def __init__(self, row, col):
        super().__init__(row, col)
        self.type = "WALL"
        self.colour = COLOUR1
        self.image.fill(self.colour)
        WALLS.add(self)

# A tile that can be walked through. It acts as the nodes of a graph.
class Cell(Tile):
    def __init__(self, row, col):
        super().__init__(row, col)
        self.type = "CELL"
        self.visited = False
        self.colour = COLOUR2
        self.image.fill(self.colour)
        CELLS.add(self)

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
        self.colour = COLOUR2
        self.image.fill(self.colour)
        PSSGS.add(self)

# The grid class is basically a two dimensional array with special methods.
# Each space will hold either a wall, a cell, or a passage.
class Grid():
    def __init__(self, vertical_cells, horizontal_cells):
        # Maximum vertical and horizontal tiles in the grid.
        self.MAX_VER_TILES = vertical_cells*2+1
        self.MAX_HOR_TILES = horizontal_cells*2+1
        # Total vertical and horizontal pixels that the grid will take up.
        self.total_ver_pixels = self.MAX_VER_TILES*TILE_PIXELS
        self.total_hor_pixels = self.MAX_HOR_TILES*TILE_PIXELS
        # Initialize a grid of walls and cells.
        self.grid = [[self.__GenerateCellorWall(row, col) for col in range(0, self.MAX_HOR_TILES)] for row in range(0, self.MAX_VER_TILES)]

    # Method used in the init of the grid.
    def __GenerateCellorWall(self, row, col):
        if row % 2 != 0 and col % 2 != 0:
            return Cell(row, col)
        else:
            return Wall(row, col)

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

    # Displays the grid in a textual form.
    def PrintGrid(self):
        for row in self.grid:
            print()
            for tile in row:
                if tile.type == "WALL":
                    print('H ', end='')
                else:
                    print('  ', end='')

    # Update's the tile's positions, as each tile's initial position is (0, 0). 
    def DrawGrid(self):
        count1 = 0
        count2 = 0
        for row in self.grid:
            for tile in row:
                tile.rect.update(count1, count2, TILE_PIXELS, TILE_PIXELS)  
                count1 += TILE_PIXELS
            count1 = 0
            count2 += TILE_PIXELS

    ### OLD METHOD
    # Returns a surface on which the maze is drawn.
    # def DrawGrid(self):
    #     grid_surf = pygame.Surface((self.total_hor_pixels, self.total_ver_pixels))
    #     grid_surf.fill(COLOUR2)
    #     count1 = 0
    #     count2 = 0
    #     for row in self.grid:
    #         for tile in row:
    #             if tile.type == "WALL":
    #                 pygame.draw.rect(grid_surf, COLOUR1, pygame.Rect(count1, count2, self.tile_pixels, self.tile_pixels))
    #             count1 += self.tile_pixels
    #         count1 = 0
    #         count2 += self.tile_pixels
    #     return grid_surf

# Player class.
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((TILE_PIXELS//2, TILE_PIXELS//2))
        self.image.fill(COLOUR3)
        self.rect = self.image.get_rect()

    def update(self, pressed_keys):
        speed = TILE_PIXELS//10

        h_vel = 0
        v_vel = 0

        # Horizontal movement.
        if pressed_keys[pygame.K_LEFT]:
            h_vel = -speed
            self.rect.move_ip(h_vel, 0)
        if pressed_keys[pygame.K_RIGHT]:
            h_vel = speed
            self.rect.move_ip(h_vel, 0)

        # Checks for collided tiles and prevents movement.
        collided = pygame.sprite.spritecollide(self, WALLS, False)
        for wall in collided:
            if h_vel > 0:
                self.rect.right = wall.rect.left
            elif h_vel < 0:
                self.rect.left = wall.rect.right
        
        # Vertical movement.
        if pressed_keys[pygame.K_UP]:
            v_vel = -speed
            self.rect.move_ip(0, v_vel)
        if pressed_keys[pygame.K_DOWN]:
            v_vel = speed
            self.rect.move_ip(0, v_vel)
            
        collided = pygame.sprite.spritecollide(self, WALLS, False)
        for wall in collided:
            if v_vel > 0:
                self.rect.bottom = wall.rect.top
            elif v_vel < 0:
                self.rect.top = wall.rect.bottom

# Initializing objects.
# The grid object is created, populated with tiles, and then the maze algorithm
# is invoked.
maze1 = Grid(13, 13)
maze1.RecursiveBacktracker(maze1.GetTile(13, 13), 0.05)
maze1_surface = maze1.DrawGrid()

# Player object is initialized and positioned in a cell in the maze.
p1 = Player()
p1.rect.center = maze1.GetTile(1, 1).rect.center

# Clock object initialized. Needed to keep FPS stable during each cycle.
clock = pygame.time.Clock()

# Game loop. Runs each frame.
running = True
while running:
    # If ESC is pressed or the window is closed, the process quits.
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
        if event.type == pygame.QUIT:
            running = False

    # Get the list of pressed keys and update the character's position.
    pressed_keys = pygame.key.get_pressed()
    p1.update(pressed_keys)

    # Draw everything.
    TILES.draw(DISPLAY_SURFACE)
    DISPLAY_SURFACE.blit(p1.image, p1.rect)

    # Flip display.
    pygame.display.flip()

    # Makes the game run at a set FPS.
    clock.tick(60)

# Quits pygame to successfuly close the game.
pygame.quit()
