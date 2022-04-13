# https://coderslegacy.com/python/python-pygame-tutorial/
# https://realpython.com/pygame-a-primer/

import pygame
import random
pygame.init()

# Declaring variables
MAX_WIDTH = 1000
MAX_HEIGHT = 800

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Creating enemy and cloud spawning events and making them appear every interval
ADDENEMY = pygame.USEREVENT + 1
pygame.time.set_timer(ADDENEMY, 250)
ADDCLOUD = pygame.USEREVENT + 2
pygame.time.set_timer(ADDCLOUD, 1000)

# Creating surface to draw on
display_surface = pygame.display.set_mode((MAX_WIDTH, MAX_HEIGHT))
display_surface.fill(WHITE)

# Player class


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.surf = pygame.image.load("misc/texture_player1.png").convert()
        self.surf.set_colorkey(WHITE, pygame.RLEACCEL)
        self.rect = self.surf.get_rect()

    # Checks pressed keys and moves accordingly
    def update(self, pressed_keys):
        speed = 10
        # Updates player's position by speed depending on the button press
        if pressed_keys[pygame.K_UP]:
            self.rect.move_ip(0, -speed)
        if pressed_keys[pygame.K_DOWN]:
            self.rect.move_ip(0, speed)
        if pressed_keys[pygame.K_LEFT]:
            self.rect.move_ip(-speed, 0)
        if pressed_keys[pygame.K_RIGHT]:
            self.rect.move_ip(speed, 0)

        # Prevents out of bounds movement
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > MAX_WIDTH:
            self.rect.right = MAX_WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > MAX_HEIGHT:
            self.rect.bottom = MAX_HEIGHT

# Enemy class


class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.surf = pygame.image.load("misc/texture_enemy.png").convert()
        self.surf.set_colorkey((255, 255, 255), pygame.RLEACCEL)
        self.rect = self.surf.get_rect(center=(random.randint(
            MAX_WIDTH + 20, MAX_WIDTH + 100), random.randint(0, MAX_HEIGHT)))
        self.speed = random.randint(5, 20)

    # Move the sprite based on speed
    # Remove the sprite when it passes the left edge of the screen
    def update(self):
        self.rect.move_ip(-self.speed, 0)
        if self.rect.right < 0:
            self.kill()


class Cloud(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.surf = pygame.image.load("misc/texture_cloud.png").convert()
        self.surf.set_colorkey(BLACK, pygame.RLEACCEL)
        # The starting position is randomly generated
        self.rect = self.surf.get_rect(center=(random.randint(
            MAX_WIDTH + 20, MAX_WIDTH + 100), random.randint(0, MAX_HEIGHT)))

    def update(self):
        self.rect.move_ip(-5, 0)
        if self.rect.right < 0:
            self.kill()


p1 = Player()
enemies = pygame.sprite.Group()
clouds = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
all_sprites.add(p1)

clock = pygame.time.Clock()

# Game loop
running = True
while running:
    # Event handler
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
        elif event.type == pygame.QUIT:
            running = False
        # Custom event, adds an enemy to two groups
        elif event.type == ADDENEMY:
            new_enemy = Enemy()
            enemies.add(new_enemy)
            all_sprites.add(new_enemy)
        # Custom event, adds a cloud to two groups
        elif event.type == ADDCLOUD:
            new_cloud = Cloud()
            clouds.add(new_cloud)
            all_sprites.add(new_cloud)

    # Updates the character's position
    pressed_keys = pygame.key.get_pressed()
    p1.update(pressed_keys)

    # Checks for collisions between the character and any enemies
    if pygame.sprite.spritecollideany(p1, enemies):
        running = False

    # Fills everything with a color
    display_surface.fill(pygame.Color("skyblue"))

    # Draws all sprites on the screen
    for entity in all_sprites:
        display_surface.blit(entity.surf, entity.rect)

    # Updates the cloud and enemy positions
    clouds.update()
    enemies.update()

    # Draws everything on the screen
    pygame.display.flip()

    # Sets FPS
    clock.tick(60)

pygame.quit()
