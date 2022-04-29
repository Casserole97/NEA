import pygame
from random import choice, random, randrange
from pathfinding.finder.a_star import AStarFinder
from pathfinding.core.grid import Grid as PathGrid
from sys import exit

pygame.init()

## DECLARING CONSTANTS
# Max resolution.
MAX_WIDTH = 1280
MAX_HEIGHT = 720

# Common RGB values.
COLOUR1 = (255, 255, 255)
COLOUR2 = (0, 0, 0)
COLOUR3 = (128, 128, 128)
COLOUR4 = (0, 0, 128)
COLOUR5 = (30, 30, 30)
COLOUR6 = (230, 230, 230)

# Fonts that will be used to render text.
SMALL_FONT = pygame.font.SysFont(None, 35)
BIG_FONT = pygame.font.SysFont(None, 70)

# Custom events.
TIMER_EVENT = pygame.USEREVENT + 1
ENEMY_UPDATE_PATH_EVENT = pygame.USEREVENT + 2

# Sprite groups.
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

# The two item textures.
BREAK_TEXTURE = pygame.image.load("textures/W_Mace003.png").convert_alpha()
JUMP_TEXTURE = pygame.image.load("textures/I_FrogLeg.png").convert_alpha()

## CLASSES
# Sprite that acts as a row/column coordinate on the grid.
# Only needed for the other tiles to inherit from, will never be placed on the 
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

    def get_pos(self):
        return self.row, self.col

    def change_colour(self, colour):
        self.colour = colour
        self.image.fill(self.colour)

class Wall(Tile):
    def __init__(self, row, col, is_special):
        super().__init__(row, col)
        self.type = "WALL"
        self.special = is_special
        self.is_exit = False
        if self.special:
            self.colour = COLOUR6
        else:
            self.colour = COLOUR1
        self.image.fill(self.colour)
        WALLS_GROUP.add(self)
    
    # Changes the wall to an exit.
    def make_exit(self):
        self.is_exit = True
        self.change_colour(COLOUR2)

class Cell(Tile):
    def __init__(self, row, col):
        super().__init__(row, col)
        self.type = "CELL"
        self.visited = False
        self.change_colour(COLOUR2)
        CELLS_GROUP.add(self)

    def is_visited(self):
        return self.visited

    def visit(self):
        self.visited = True

class Passage(Tile):
    def __init__(self, row, col):
        super().__init__(row, col)
        self.type = "PASSAGE"
        self.change_colour(COLOUR2)
        PASSAGES_GROUP.add(self)

class Grid():
    def __init__(self, vertical_cells, horizontal_cells):
        self.MAX_VER_TILES = vertical_cells*2+1
        self.MAX_HOR_TILES = horizontal_cells*2+1
        # Total pixels that the grid will take up.
        self.total_ver_pixels = self.MAX_VER_TILES*TILE_PIXELS
        self.total_hor_pixels = self.MAX_HOR_TILES*TILE_PIXELS
        # Initialize a grid of walls, cells, and passages.
        self.grid = [[self.__generate_cell_or_wall(row, col) for col in range(0, self.MAX_HOR_TILES)] for row in range(0, self.MAX_VER_TILES)]

    # Given coordinates, returns the correct tile to be placed.
    def __generate_cell_or_wall(self, row, col):
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
    def update_tile_pos(self):
        count1 = 0
        count2 = 0
        for row in self.grid:
            for tile in row:
                tile.rect.update(count1, count2, TILE_PIXELS, TILE_PIXELS)  
                count1 += TILE_PIXELS
            count1 = 0
            count2 += TILE_PIXELS
        # Weird bug occured where every wall tile was duplicated. This is a
        # short-term fix.
        pygame.sprite.spritecollide(self.get_tile(0, 0), WALLS_GROUP, True)
        WALLS_GROUP.add(self.get_tile(0, 0))
        TILES_GROUP.add(self.get_tile(0, 0))
        CAMERA_GROUP.add(self.get_tile(0, 0))

    def get_tile(self, row, col):
        return self.grid[row][col]
    
    # Returns the unvisited cells adjacent to a target cell.
    def get_unvisited_neighbours(self, cell):
        unvisited_neighbours = []
        row, col = cell.get_pos()
        N = -2
        E = 2
        S = 2
        W = -2
        # Statements are inside try except blocks because the tile checked can
        # be something other than a cell, or it could check outside of the
        # grid, where tiles don't exist.
        try:
            if not self.get_tile(row+N, col).is_visited():
                unvisited_neighbours.append(self.get_tile(row+N, col))
        except Exception:
            pass
        try:
            if not self.get_tile(row, col+E).is_visited():
                unvisited_neighbours.append(self.get_tile(row, col+E))
        except Exception:
            pass
        try:
            if not self.get_tile(row+S, col).is_visited():
                unvisited_neighbours.append(self.get_tile(row+S, col))
        except Exception:
            pass
        try:
            if not self.get_tile(row, col+W).is_visited():
                unvisited_neighbours.append(self.get_tile(row, col+W))
        except Exception:
            pass
        return unvisited_neighbours

    # Changes a wall between two cells to a passage.
    def carve_passage(self, cell1, cell2):
        row = (cell1.row + cell2.row) // 2
        col = (cell1.col + cell2.col) // 2
        self.grid[row][col] = Passage(row, col)

    def recursive_backtracker(self, cell, loop_chance):
        neighbours = self.get_unvisited_neighbours(cell)
        cell.visit()
        while len(neighbours) != 0:
            next_cell = choice(neighbours)
            neighbours.remove(next_cell)
            if not next_cell.is_visited(): 
                self.carve_passage(cell, next_cell)
            elif random() <= loop_chance:
                self.carve_passage(cell, next_cell)
            self.recursive_backtracker(next_cell, loop_chance)

    # Displays the grid in a textual form. Only needed for debugging now.
    def print_grid(self):
        for row in self.grid:
            print()
            for tile in row:
                if tile.type == "WALL":
                    print('H ', end='')
                else:
                    print('  ', end='')

    # Returns a surface on which the map is drawn.
    def draw_map(self, player, enemy, tile_pixels=5):
        map_surf = pygame.Surface((self.MAX_HOR_TILES*tile_pixels, self.MAX_VER_TILES*tile_pixels)).convert()
        count1 = 0
        count2 = 0
        for row in self.grid:
            for tile in row:
                coords = tile.get_pos()
                # Draws the bordering walls.
                if coords[0] == 0 or coords[1] == 0 or coords[0] == self.MAX_VER_TILES-1 or coords[1] == self.MAX_HOR_TILES-1:
                    pygame.draw.rect(map_surf, COLOUR1, pygame.Rect(count1, count2, tile_pixels, tile_pixels))
                # Draws the player square.
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
    
    def get_random_cell(self):
        # Numbers are always odd since cells reside only on odd-numbered rows
        # and columns.
        random_row = randrange(1, self.MAX_VER_TILES-2, 2)
        random_col = randrange(1, self.MAX_HOR_TILES-2, 2)
        return self.get_tile(random_row, random_col)
    
    def is_dead_end(self, cell):
        walls = 0
        row, col = cell.get_pos()
        if self.get_tile(row+1, col).type == "WALL":
            walls += 1
        if self.get_tile(row-1, col).type == "WALL":
            walls += 1
        if self.get_tile(row, col+1).type == "WALL":
            walls += 1
        if self.get_tile(row, col-1).type == "WALL":
            walls += 1
        if walls == 3:
            return True
        else:
            return False
    
    def generate_items(self, chance):
        for cell in CELLS_GROUP:
                if self.is_dead_end(cell) and random() <= chance:
                    row, col = cell.get_pos()
                    if random() < 0.5:
                        Item(row, col, "BREAK", cell.rect.center)
                    else:
                        Item(row, col, "JUMP", cell.rect.center)

    def generate_exit(self):
        # First creates a list of odd-numbered outside walls, and then picks
        # one to make into an exit.
        available_walls = []
        for row in self.grid:
            for tile in row:
                pos = tile.get_pos()
                if pos[0] == 0 or pos[1] == 0 or pos[0] == self.MAX_VER_TILES-1 or pos[1] == self.MAX_HOR_TILES-1:
                    if pos[0] % 2 != 0 or pos[1] % 2 != 0:
                        available_walls.append(tile)
        chosen_wall = choice(available_walls)
        chosen_wall.make_exit()

# Player class.
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((TILE_PIXELS//2, TILE_PIXELS//2)).convert()
        self.image.fill(COLOUR3)
        self.rect = self.image.get_rect()
        self.speed = TILE_PIXELS//10
        self.item_break = 1
        self.item_jump = 1
        PLAYER_GROUP.add(self)
        CAMERA_GROUP.add(self)
        
    # Returns a cell or passage which collides with the center of the player's 
    # rect.
    def get_current_tile(self):
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

    # Method responsible for player movement and collision. In the case of
    # touching the enemy or the exit, a value is returned.
    def update(self, item_used, maze, elem, enemy):
        pressed_keys = pygame.key.get_pressed()
        h_vel = 0
        v_vel = 0

        if pygame.sprite.spritecollideany(self, ENEMY_GROUP):
            return "ENEMY"

        # Colour the cells and passages upon collision and collect items.
        touched_tile = self.get_current_tile()
        if touched_tile.colour != COLOUR4:
            touched_tile.change_colour(COLOUR4)
            elem.add_to_score(10)
        for item in ITEMS_GROUP:
            if (item.row, item.col) == touched_tile.get_pos():
                item.kill()
                if item.type == "BREAK":
                    self.item_break += 1
                elif item.type == "JUMP":
                    self.item_jump += 1
                elem.add_to_score(100)

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
            if wall.is_exit:
                return "EXIT"
            if h_vel > 0:
                self.rect.right = wall.rect.left
                # Allows to use the items.
                if not wall.special and item_used != None:
                    if item_used == "JUMP" and self.item_jump > 0:
                        if self.rect.top >= wall.rect.top and self.rect.bottom <= wall.rect.bottom:
                            self.use_item("JUMP")
                            self.rect.left = wall.rect.right
                    elif item_used == "BREAK" and self.item_break > 0:
                        self.use_item("BREAK")
                        row, col = wall.get_pos()
                        wall.kill()
                        maze.grid[row][col] = Passage(row, col)
                        maze.update_tile_pos()

            elif h_vel < 0:
                self.rect.left = wall.rect.right
                if not wall.special and item_used != None:
                    if item_used == "JUMP" and self.item_jump > 0:
                        if self.rect.top >= wall.rect.top and self.rect.bottom <= wall.rect.bottom:
                            self.use_item("JUMP")
                            self.rect.right = wall.rect.left
                    elif item_used == "BREAK" and self.item_break > 0:
                        self.use_item("BREAK")
                        row, col = wall.get_pos()
                        wall.kill()
                        maze.grid[row][col] = Passage(row, col)
                        maze.update_tile_pos()
        
        # Code repeated for vertical movement.
        if pressed_keys[pygame.K_UP]:
            v_vel = -self.speed
            self.rect.move_ip(0, v_vel)
        if pressed_keys[pygame.K_DOWN]:
            v_vel = self.speed
            self.rect.move_ip(0, v_vel)
        
        collided_walls = pygame.sprite.spritecollide(self, WALLS_GROUP, False)
        for wall in collided_walls:
            if wall.is_exit:
                return "EXIT"
            if v_vel > 0:
                self.rect.bottom = wall.rect.top
                if not wall.special and item_used != None:
                    if item_used == "JUMP" and self.item_jump > 0:
                        if self.rect.left >= wall.rect.left and self.rect.right <= wall.rect.right:
                            self.use_item("JUMP")
                            self.rect.top = wall.rect.bottom
                    elif item_used == "BREAK" and self.item_break > 0:
                        self.use_item("BREAK")
                        row, col = wall.get_pos()
                        wall.kill()
                        maze.grid[row][col] = Passage(row, col)
                        maze.update_tile_pos()
                        
            elif v_vel < 0:
                self.rect.top = wall.rect.bottom
                if not wall.special and item_used != None:
                    if item_used == "JUMP" and self.item_jump > 0:
                        if self.rect.left >= wall.rect.left and self.rect.right <= wall.rect.right:
                            self.use_item("JUMP")
                            self.rect.bottom = wall.rect.top
                    elif item_used == "BREAK" and self.item_break > 0:
                        self.use_item("BREAK")
                        row, col = wall.get_pos()
                        wall.kill()
                        maze.grid[row][col] = Passage(row, col)
                        maze.update_tile_pos()

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
        for sprite in sorted(self, key = lambda sprite: sprite in PLAYER_GROUP or sprite in ENEMY_GROUP):
            # Only blit something if it is visible on the screen.
            if sprite.rect.colliderect(pygame.Rect(280+offset[0], offset[1], 720, 720)):
                new_pos = ((sprite.rect.topleft[0] - offset[0]), (sprite.rect.topleft[1] - offset[1]))
                display.blit(sprite.image, new_pos)

# Both item types are created using this object.
class Item(pygame.sprite.Sprite):
    def __init__(self, row, col, type, new_center):
        super().__init__()
        self.type = type
        if self.type == "BREAK":
            self.image = BREAK_TEXTURE
        elif self.type == "JUMP":
            self.image = JUMP_TEXTURE
        self.rect = self.image.get_rect(center=(new_center))
        self.row = row
        self.col = col
        ITEMS_GROUP.add(self)
        CAMERA_GROUP.add(self)

# Class that is responsible for the HUD.
class GameElements():
    def __init__(self, game_time):
        # Surfaces to be blitted.
        self.border1 = pygame.Rect(0, 0, 280, 720)
        self.border2 = pygame.Rect(1000, 0, 280, 720)
        self.break_2x = pygame.transform.scale2x(BREAK_TEXTURE).convert_alpha()
        self.jump_2x = pygame.transform.scale2x(JUMP_TEXTURE).convert_alpha()
        self.text_score_title = BIG_FONT.render("SCORE", False, COLOUR1)
        self.text_time_title = BIG_FONT.render("TIME", False, COLOUR1)
        self.text_info_break = BIG_FONT.render("'Z' - ITEM1", False, COLOUR1)
        self.text_info_jump = BIG_FONT.render("'X' - ITEM2", False, COLOUR1)
        self.text_info_menu = BIG_FONT.render("'ESC'-MENU", False, COLOUR1)
        # Actual variables.
        self.time_at_start = game_time
        self.time = self.time_at_start
        self.score = self.time*5

    def start_timer(self):
        pygame.time.set_timer(TIMER_EVENT, 1000)

    def add_to_score(self, amount):
        self.score += amount
    
    def second_passed(self):
        self.time -= 1

    # Returns as string with seconds converted to minutes and seconds.
    def get_time_str(self):
        minutes = self.time // 60
        seconds = self.time % 60
        if seconds < 10:
            seconds = "0" + str(seconds)
        else:
            seconds = str(seconds)
        if minutes < 10:
            minutes = "0" + str(minutes)
        else:
            minutes = str(minutes)
        return minutes + ":" + seconds

    def draw_borders(self):
        pygame.draw.rect(display_surface, COLOUR5, self.border1)
        pygame.draw.rect(display_surface, COLOUR5, self.border2)
    
    def draw_items_counter(self, player):
        # Draws the boxes around the items
        pygame.draw.rect(display_surface, COLOUR1, (1046, 590, 70, 70), 5)
        pygame.draw.rect(display_surface, COLOUR1, (1162, 590, 70, 70), 5)
        # Draw the item icons in the boxes.
        display_surface.blit(self.break_2x, (1046, 590))
        display_surface.blit(self.jump_2x, (1162, 590))
        # Renders the item counts and draws them.
        text_break_count = SMALL_FONT.render(str(player.item_break), False, COLOUR1)
        text_jump_count = SMALL_FONT.render(str(player.item_jump), False, COLOUR1)
        display_surface.blit(text_break_count, (1078, 665))
        display_surface.blit(text_jump_count, (1194, 665))
    
    def draw_map(self, maze_map):
        display_surface.blit(maze_map, (((280-maze_map.get_width())//2), ((280-maze_map.get_width())//2)))
    
    def draw_score(self):
        display_surface.blit(self.text_score_title, (52, 440))
        text_score = BIG_FONT.render(str(self.score), False, COLOUR1)
        display_surface.blit(text_score, (self.border1.centerx-len(str(self.score))*15, 495))
    
    def draw_timer(self):
        display_surface.blit(self.text_time_title, (75, 580))
        text_time = BIG_FONT.render(self.get_time_str(), False, COLOUR1)
        display_surface.blit(text_time, (self.border1.centerx-len(self.get_time_str())*14, 635))
    
    def draw_tips(self):
        display_surface.blit(self.text_info_break, (1015, 15))
        display_surface.blit(self.text_info_jump, (1015, 115))
        display_surface.blit(self.text_info_menu, (1000, 215))
    
    # Draws all the elements together.
    def draw_hud(self, maze_map, player):
        self.draw_borders()
        self.draw_items_counter(player)
        self.draw_map(maze_map)
        self.draw_score()
        self.draw_timer()
        self.draw_tips()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, starting_tile):
        super().__init__()
        self.image = pygame.Surface((TILE_PIXELS, TILE_PIXELS)).convert()
        self.image.fill((0, 255, 0))
        self.rect = self.image.get_rect()
        self.speed = TILE_PIXELS//10
        # Path grid - matrix converted to node objects that A* can use.
        self.pathgrid = None
        self.path_finder = AStarFinder()
        self.path = []
        self.current_tile = starting_tile
        self.next_tile = None
        ENEMY_GROUP.add(self)
        CAMERA_GROUP.add(self)

    # Generate a matrix based on the grid, and then update the path grid.
    def update_pathgrid(self, grid):
        # Matrix is a representation of the maze using 1s and 0s.
        # 1 - TRAVERSABLE TILE
        # 0 - WALL
        matrix = [[self.__generate_1_or_0(tile) for tile in row] for row in grid.grid]
        self.pathgrid = PathGrid(matrix=matrix)
    
    def __generate_1_or_0(self, tile):
        if tile.type == "WALL":
            return 0
        else:
            return 1
    
    # Creates a path made from one tile to another using the A* algorithm.
    def update_path(self, maze, tile1, tile2):
        coords1 = tile1.get_pos()
        coords2 = tile2.get_pos()
        start = self.pathgrid.node(coords1[1], coords1[0])
        end = self.pathgrid.node(coords2[1], coords2[0])
        xy_path, _ = self.path_finder.find_path(start, end, self.pathgrid)
        self.pathgrid.cleanup()
        # Converts (x, y) coordinates of the path to (row, col) and returns.
        rowcol_path = []
        for coord in xy_path:
            coord = coord[::-1]
            rowcol_path.append(maze.get_tile(coord[0], coord[1]))
        self.path = rowcol_path
        self.next_tile = self.path[1]
    
    # Calculates the direction to move in to reach the next tile.
    def get_tile_direction(self, tile):
        if tile.rect.centerx > self.rect.centerx:
            return "RIGHT"
        elif tile.rect.centerx < self.rect.centerx:
            return "LEFT"
        elif tile.rect.centery > self.rect.centery:
            return "DOWN"
        elif tile.rect.centery < self.rect.centery:
            return "UP"

    def update(self, maze, player):
        if self.rect.center != self.next_tile.rect.center:
            direction = self.get_tile_direction(self.next_tile)
            if direction == "RIGHT":
                self.rect.move_ip(self.speed, 0)
            elif direction == "LEFT":
                self.rect.move_ip(-self.speed, 0)
            elif direction == "DOWN":
                self.rect.move_ip(0, self.speed)
            elif direction == "UP":
                self.rect.move_ip(0, -self.speed)
        else:
            self.current_tile = self.next_tile
            self.update_path(maze, self.current_tile, player.get_current_tile())
            self.next_tile = self.path[1]

## GAME CODE
#Camera group initialized as it could not be initialized earlier in the code.
CAMERA_GROUP = Camera()

# The grid object is initialized, and then the maze algorithm is invoked on a
# random cell.
cells = 27
maze1 = Grid(cells, cells)
maze1.recursive_backtracker(maze1.get_random_cell(), 0.02)
maze1.update_tile_pos()
maze1.generate_items(0.1)
maze1.generate_exit()

# HUD initialized and timer started.
time = 130
game_elements = GameElements(time)
game_elements.start_timer()

# Player object is initialized and positioned on a random cell in the maze.
p1 = Player()
# random_cell = maze1.get_random_cell()
p1.rect.center = maze1.get_tile(5, 5).rect.center

# Enemy is initialized and placed on a cell.
starting_cell = maze1.get_tile(1, 1)
enemy = Enemy(starting_cell)
enemy.update_pathgrid(maze1)
enemy.rect.center = maze1.get_tile(1, 1).rect.center
enemy.update_path(maze1, enemy.current_tile, p1.get_current_tile())

# Clock object initialized. Needed to keep FPS stable during runtime.
clock = pygame.time.Clock()

# Game loop. Runs each frame.
running = True
while running:
    item_used = None
    # Event handler.
    for event in pygame.event.get():
        # Checks the keypresses.
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            # Sends a signal that an item is used.
            if event.key == pygame.K_z:
                item_used = "BREAK"
            elif event.key == pygame.K_x:
                item_used = "JUMP"
        # Checks for custom events.
        if event.type == TIMER_EVENT:
            game_elements.second_passed()
            if game_elements.time % 10 == 0:
                game_elements.add_to_score(-50)
        # if event.type == ENEMY_UPDATE_PATH_EVENT:
        #     enemy.update_pathgrid(maze1)
        # If the window is closed, the game is quit.
        if event.type == pygame.QUIT:
            running = False    

    # Update and draw everything.
    display_surface.fill(COLOUR2)
    CAMERA_GROUP.draw(display_surface, p1)
    status = p1.update(item_used, maze1, game_elements, enemy)
    enemy.update(maze1, p1)
    if item_used == "BREAK":
        enemy.update_pathgrid(maze1)
    if status == "EXIT":
        running = False
    elif status == "ENEMY":
        running = False

    # Updates the map and HUD.
    maze1_map = maze1.draw_map(p1, 5)
    game_elements.draw_hud(maze1_map, p1)

    # Update display.
    pygame.display.update()

    # Game is lost if time reaches 0.
    if game_elements.time == 0:
        running = False

    # Makes the game run at a set FPS.
    clock.tick(60)

# Successfuly closes the game.
pygame.quit()
exit()