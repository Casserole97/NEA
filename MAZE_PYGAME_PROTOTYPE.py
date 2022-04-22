import pygame
from random import choice, random, randrange
from sys import exit

from pygments import highlight
pygame.init()

# REMEMBER THE DIFFERENCE BETWEEN X/Y AND ROW/COLUMN.
#  X 0 1 2 3 4   |  C 0 1 2 3 4
# Y              | R
# 0              | 0
# 1              | 1
# 2              | 2
# 3              | 3
# 4              | 4

# Optimization attempt by reducing number of possible events.
pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.KEYUP])

# Declaring constants.
# Size of the screen.
MAX_WIDTH = 1280
MAX_HEIGHT = 720

# Colours to be used in the game.
COLOUR1 = (255, 255, 255) # WHITE
COLOUR2 = (0, 0, 0)       # BLACK
COLOUR3 = (128, 128, 128) # GREY
COLOUR4 = (0, 0, 255)
COLOUR5 = (30, 30, 30)

# Initialization of groups.
TILES_GROUP = pygame.sprite.Group()
WALLS_GROUP = pygame.sprite.Group()
CELLS_GROUP = pygame.sprite.Group()
PASSAGES_GROUP = pygame.sprite.Group()
ENEMY_GROUP = pygame.sprite.Group()
ITEMS_GROUP = pygame.sprite.Group()
PLAYER_GROUP = pygame.sprite.Group()

# The size, in pixels, of a side of each individual square tile. Important
# constant, as many other variables will depend on it.
TILE_PIXELS = 40

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
        self.image = pygame.Surface((TILE_PIXELS, TILE_PIXELS)).convert()
        self.rect = self.image.get_rect()
        TILES_GROUP.add(self)
        CAMERA_GROUP.add(self)

    # Return the row and column in the grid on which the tile resides.
    def GetPos(self):
        return self.row, self.col

# A tile that cannot be walked through.
class Wall(Tile):
    def __init__(self, row, col, is_special):
        super().__init__(row, col)
        self.type = "WALL"
        self.colour = COLOUR1
        self.special = is_special
        self.image.fill(self.colour)
        WALLS_GROUP.add(self)

# A tile that can be walked through. It acts as the nodes of a graph.
class Cell(Tile):
    def __init__(self, row, col):
        super().__init__(row, col)
        self.type = "CELL"
        self.visited = False
        self.colour = COLOUR2
        self.image.fill(self.colour)
        CELLS_GROUP.add(self)

    def change_colour(self, colour):
        self.colour = colour
        self.image.fill(self.colour)

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
        PASSAGES_GROUP.add(self)
    
    def change_colour(self, colour):
        self.colour = colour
        self.image.fill(self.colour)

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
            if row % 2 == 0 and col % 2 == 0:
                return Wall(row, col, True)
            elif row == 0 or col == 0 or row == self.MAX_VER_TILES-1 or col == self.MAX_HOR_TILES-1:
                return Wall(row, col, True)
            else:
                return Wall(row, col, False)

    # Update's the tiles' positions, as each tile's initial pixel position is
    # (0, 0).
    def UpdateTilePos(self):
        count1 = 0
        count2 = 0
        for row in self.grid:
            for tile in row:
                tile.rect.update(count1, count2, TILE_PIXELS, TILE_PIXELS)  
                count1 += TILE_PIXELS
            count1 = 0
            count2 += TILE_PIXELS

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
            elif random() <= loop_chance:
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


    # Returns a surface on which the map is drawn.
    def DrawMap(self, player, tile_pixels=5):
        map_surf = pygame.Surface((self.MAX_HOR_TILES*tile_pixels, self.MAX_VER_TILES*tile_pixels)).convert()
        count1 = 0
        count2 = 0
        for row in self.grid:
            for tile in row:
                coords = tile.GetPos()
                if coords[0] == 0 or coords[1] == 0 or coords[0] == self.MAX_VER_TILES-1 or coords[1] == self.MAX_HOR_TILES-1:
                    pygame.draw.rect(map_surf, COLOUR1, pygame.Rect(count1, count2, tile_pixels, tile_pixels))
                elif tile.rect.collidepoint(player.rect.center):
                    pygame.draw.rect(map_surf, COLOUR3, pygame.Rect(count1, count2, tile_pixels, tile_pixels))
                elif tile.type == "CELL":
                    pygame.draw.rect(map_surf, tile.colour, pygame.Rect(count1, count2, tile_pixels, tile_pixels))
                elif tile.type == "PASSAGE":
                    pygame.draw.rect(map_surf, tile.colour, pygame.Rect(count1, count2, tile_pixels, tile_pixels))
                count1 += tile_pixels
            count1 = 0
            count2 += tile_pixels
        return map_surf

    # Returns a random cell in the grid
    def GetRandomCell(self):
        last_cell = self.grid[-2][-2].GetPos()
        random_row = randrange(1, last_cell[0], 2)
        random_col = randrange(1, last_cell[1], 2)
        return self.GetTile(random_row, random_col)
    
    def IsDeadEnd(self, cell):
        walls = 0
        row, col = cell.GetPos()
        if self.GetTile(row+1, col).type == "WALL":
            walls += 1
        if self.GetTile(row-1, col).type == "WALL":
            walls += 1
        if self.GetTile(row, col+1).type == "WALL":
            walls += 1
        if self.GetTile(row, col-1).type == "WALL":
            walls += 1
        if walls == 3:
            return True
        else:
            return False
    
    def GenerateItems(self):
        for cell in CELLS_GROUP:
                if self.IsDeadEnd(cell) and random() <= 0.1:
                    row, col = cell.GetPos()
                    if random() < 0.5:
                        Item(row, col, "BREAK", cell.rect.center)
                    else:
                        Item(row, col, "JUMP", cell.rect.center)

# Player class.
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((TILE_PIXELS//2, TILE_PIXELS//2)).convert()
        self.image.fill(COLOUR3)
        self.rect = self.image.get_rect()
        self.speed = TILE_PIXELS//10
        self.item_break = 999
        self.item_jump = 999
        PLAYER_GROUP.add(self)
        CAMERA_GROUP.add(self)
        
    # Returns the tile which intersects with the center of the player sprite.
    def GetCurrentTile(self):
        center = self.rect.center
        for cell in CELLS_GROUP:
            if cell.rect.collidepoint(center):
                return cell
        for passage in PASSAGES_GROUP:
            if passage.rect.collidepoint(center):
                return passage

    def use_item(self, item):
        if item == "BREAK" and self.item_break > 0:
            self.item_break -= 1
        elif item == "JUMP" and self.item_jump > 0:
            self.item_jump -= 1

    def update(self, item_used, maze):
        pressed_keys = pygame.key.get_pressed()
        h_vel = 0
        v_vel = 0

        # Colour the cells and passages upon collision and grab items.
        touched_tile = self.GetCurrentTile()
        if touched_tile.colour != COLOUR4:
            touched_tile.change_colour(COLOUR4)
        for item in ITEMS_GROUP:
            if (item.row, item.col) == touched_tile.GetPos():
                item.kill()
                if item.type == "BREAK":
                    self.item_break += 1
                elif item.type == "JUMP":
                    self.item_jump += 1

        # Horizontal movement.
        if pressed_keys[pygame.K_LEFT]:
            h_vel = -self.speed
            self.rect.move_ip(h_vel, 0)
        if pressed_keys[pygame.K_RIGHT]:
            h_vel = self.speed
            self.rect.move_ip(h_vel, 0)

        # Checks for collided walls and prevents movement.
        collided_walls = pygame.sprite.spritecollide(self, WALLS_GROUP, False)
        for wall in collided_walls:
            if h_vel > 0:
                self.rect.right = wall.rect.left
                if not wall.special:
                    if item_used == "JUMP" and self.item_jump > 0:
                        self.rect.left = wall.rect.right
                        self.use_item("JUMP")
                    elif item_used == "BREAK" and self.item_break > 0:
                        self.use_item("BREAK")
                        row, col = wall.GetPos()
                        wall.kill()
                        maze.grid[row][col] = Passage(row, col)
                        maze.UpdateTilePos()

            elif h_vel < 0:
                self.rect.left = wall.rect.right
                if not wall.special:
                    if item_used == "JUMP" and self.item_jump > 0:
                        self.use_item("JUMP")
                        self.rect.right = wall.rect.left
                    elif item_used == "BREAK" and self.item_break > 0:
                        self.use_item("BREAK")
                        row, col = wall.GetPos()
                        wall.kill()
                        maze.grid[row][col] = Passage(row, col)
                        maze.UpdateTilePos()
        
        # Vertical movement.
        if pressed_keys[pygame.K_UP]:
            v_vel = -self.speed
            self.rect.move_ip(0, v_vel)
        if pressed_keys[pygame.K_DOWN]:
            v_vel = self.speed
            self.rect.move_ip(0, v_vel)
        
        # "collided" must be updated again.
        collided_walls = pygame.sprite.spritecollide(self, WALLS_GROUP, False)
        for wall in collided_walls:
            if v_vel > 0:
                self.rect.bottom = wall.rect.top
                if not wall.special:
                    if item_used == "JUMP" and self.item_jump > 0:
                        self.rect.top = wall.rect.bottom
                        self.use_item("JUMP")
                    elif item_used == "BREAK" and self.item_break > 0:
                        self.use_item("BREAK")
                        row, col = wall.GetPos()
                        wall.kill()
                        maze.grid[row][col] = Passage(row, col)
                        maze.UpdateTilePos()
            elif v_vel < 0:
                self.rect.top = wall.rect.bottom
                if not wall.special:
                    if item_used == "JUMP" and self.item_jump > 0:
                        self.use_item("JUMP")
                        self.rect.bottom = wall.rect.top
                    elif item_used == "BREAK" and self.item_break > 0:
                        self.use_item("BREAK")
                        row, col = wall.GetPos()
                        wall.kill()
                        maze.grid[row][col] = Passage(row, col)
                        maze.UpdateTilePos()

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
    # camera on the player and only drawing entities that are on screen.
    def draw(self, display, offset_sprite):
        offset = self.calculate_offset(offset_sprite)
        for sprite in sorted(self, key = lambda sprite: sprite in PLAYER_GROUP):
            # Only blit something if it is visible on the screen.
            if sprite.rect.colliderect(pygame.Rect(280+offset[0], offset[1], 720, 720)):
                # The offset is subtracted from the topleft corner of every rect.
                new_pos = ((sprite.rect.topleft[0] - offset[0]), (sprite.rect.topleft[1] - offset[1]))
                display.blit(sprite.image, new_pos)

CAMERA_GROUP = Camera()

#The item class.
class Item(pygame.sprite.Sprite):
    def __init__(self, row, col, type, new_center):
        super().__init__()
        self.type = type
        if self.type == "BREAK":
            self.image = pygame.image.load("textures/W_Mace003.png").convert_alpha()
        elif self.type == "JUMP":
            self.image = pygame.image.load("textures/I_FrogLeg.png").convert_alpha()
        self.rect = self.image.get_rect(center=(new_center))
        self.row = row
        self.col = col
        ITEMS_GROUP.add(self)
        CAMERA_GROUP.add(self)

# The grid object is initialized, populated with tiles, and then the maze 
# algorithm is invoked on a random cell.
cells = 27
maze1 = Grid(cells, cells)
maze1.RecursiveBacktracker(maze1.GetRandomCell(), 0.025)
maze1.UpdateTilePos()
maze1.GenerateItems()

# Player object is initialized and positioned in a random cell in the maze.
p1 = Player()
# p1.rect.center = maze1.GetRandomCell().rect.center
p1.rect.center = maze1.GetTile(1, 1).rect.center

# Creating the borders for the HUD.
border = pygame.surface.Surface((280, 720)).convert()
border.fill(COLOUR5)

# Clock object initialized. Needed to keep FPS stable during runtime.
clock = pygame.time.Clock()


font = pygame.font.SysFont(None, 24)


# Game loop. Runs each frame.
running = True
while running:
    item_used = None
    # If ESC is pressed or the window is closed, the process quits.
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            # Use items.
            if event.key == pygame.K_z:
                item_used = "BREAK"
            elif event.key == pygame.K_x:
                item_used = "JUMP"

        if event.type == pygame.QUIT:
            running = False
            
        
    text = font.render("Break: " + str(p1.item_break)+ " " + "Jump: " + str(p1.item_jump), True, COLOUR4)
    

    # Update and draw everything.
    display_surface.fill(COLOUR2)
    CAMERA_GROUP.draw(display_surface, p1)
    p1.update(item_used, maze1)

    # HUD.
    display_surface.blit(border, (0, 0))
    display_surface.blit(border, (1000, 0))
    maze1_map = maze1.DrawMap(p1)
    display_surface.blit(maze1_map, (((280-maze1_map.get_width())//2), ((280-maze1_map.get_width())//2)))
    display_surface.blit(text, (20, 290))

    # Update display.
    pygame.display.update()

    # Makes the game run at a set FPS.
    clock.tick(60)
# Successfuly closes the game.
pygame.quit()
exit()