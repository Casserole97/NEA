import pygame
from random import choice, random, randrange
from sys import exit
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
MAX_WIDTH = 1280
MAX_HEIGHT = 720

# Colours to be used in the game.
COLOUR1 = (255, 255, 255)
COLOUR2 = (0, 0, 0)
COLOUR3 = (128, 128, 128)

# The size, in pixels, of a side of each individual square tile. Important
# constant, as many other variables will depend on it.
TILE_PIXELS = 50

# Creating the screen which will be displayed.
display_surface = pygame.display.set_mode((MAX_WIDTH, MAX_HEIGHT))
pygame.display.set_caption("Game")

# Sprite that acts as a row/column coordinate on the grid.
# Only needed for other classes to inherit from, will never be placed on the 
# grid.
class Tile(pygame.sprite.Sprite):
    def __init__(self, row, col):
        super().__init__()
        self.row = row
        self.col = col
        self.image = pygame.Surface((TILE_PIXELS, TILE_PIXELS))
        self.rect = self.image.get_rect()
        tiles_group.add(self)
        camera_group.add(self)

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
        walls_group.add(self)

# A tile that can be walked through. It acts as the nodes of a graph.
class Cell(Tile):
    def __init__(self, row, col):
        super().__init__(row, col)
        self.type = "CELL"
        self.visited = False
        self.colour = COLOUR2
        self.image.fill(self.colour)
        cells_group.add(self)

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
        pssgs_group.add(self)

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
        except Exception:
            pass
        try:
            if not self.GetTile(row, col+E).IsVisited():
                unvisited_neighbours.append(self.GetTile(row, col+E))
        except Exception:
            pass
        try:
            if not self.GetTile(row+S, col).IsVisited():
                unvisited_neighbours.append(self.GetTile(row+S, col))
        except Exception:
            pass
        try:
            if not self.GetTile(row, col+W).IsVisited():
                unvisited_neighbours.append(self.GetTile(row, col+W))
        except Exception:
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
    def UpdateTilePos(self):
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
    def OLD_DRAW_GRID(self):
        grid_surf = pygame.Surface((self.total_hor_pixels, self.total_ver_pixels))
        grid_surf.fill(COLOUR2)
        count1 = 0
        count2 = 0
        for row in self.grid:
            for tile in row:
                if tile.type == "WALL":
                    pygame.draw.rect(grid_surf, COLOUR1, pygame.Rect(count1, count2, TILE_PIXELS, TILE_PIXELS))
                count1 += TILE_PIXELS
            count1 = 0
            count2 += TILE_PIXELS
        return grid_surf

# Player class.
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((TILE_PIXELS//2, TILE_PIXELS//2))
        self.image.fill(COLOUR3)
        self.rect = self.image.get_rect()
        camera_group.add(self)

    def update(self):
        speed = TILE_PIXELS//10
        pressed_keys = pygame.key.get_pressed()
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
        collided = pygame.sprite.spritecollide(self, walls_group, False)
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
        
        # "collided" must be updated again.
        collided = pygame.sprite.spritecollide(self, walls_group, False)
        for wall in collided:
            if v_vel > 0:
                self.rect.bottom = wall.rect.top
            elif v_vel < 0:
                self.rect.top = wall.rect.bottom

# Camera class.
class Camera(pygame.sprite.Group):
    def __init__(self):
        super().__init__()

    # Calculates the X and Y offset required to keep the sprite in the center
    # of the screen.
    def calculate_offset(self, sprite):
        offset_x = sprite.rect.centerx - MAX_WIDTH//2
        offset_y = sprite.rect.centery - MAX_HEIGHT//2
        return offset_x, offset_y
    
    # Overrides the default draw method, with the addition of centering the
    # camera on the player.
    def draw(self, display):
        offset = self.calculate_offset(p1)
        for sprite in self:
            # The offset is subtracted from the topleft corner of every rect.
            new_pos = ((sprite.rect.topleft[0] - offset[0]), (sprite.rect.topleft[1] - offset[1]))
            display.blit(sprite.image, new_pos)

# Initialization of groups.
tiles_group = pygame.sprite.Group()
walls_group = pygame.sprite.Group()
cells_group = pygame.sprite.Group()
pssgs_group = pygame.sprite.Group()
camera_group = Camera()

# The grid object is initialized, populated with tiles, and then the maze 
# algorithm is invoked on a cell.
maze1 = Grid(25, 25)
maze1.RecursiveBacktracker(maze1.GetTile(25, 25), 0.025)
maze1_surface = maze1.UpdateTilePos()

# Player object is initialized and positioned in a random cell in the maze.
p1 = Player()
p1.rect.center = maze1.GetTile(randrange(1, 27, 2), randrange(1, 27, 2)).rect.center

# Clock object initialized. Needed to keep FPS stable during runtime.
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

    # Update and draw everything.
    display_surface.fill(COLOUR2)
    camera_group.update()
    camera_group.draw(display_surface)

    # Update display.
    pygame.display.update()

    # Makes the game run at a set FPS.
    clock.tick(60)

# Successfuly closes the game.
pygame.quit()
exit()