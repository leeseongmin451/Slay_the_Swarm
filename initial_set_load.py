"""
Python file for initializing screen and loading all images needed
"""

import pygame
from pygame.locals import *

import os.path

import ctypes
ctypes.windll.user32.SetProcessDPIAware()

# Initialize pygame
pygame.init()


# Game title and icon
icon = pygame.image.load("img/icon/icon.png")
pygame.display.set_icon(icon)                   # Set icon
pygame.display.set_caption("Slay the Swarm")    # Set title

# Create the screen
screen_width, screen_height = 1920, 1080
flags = FULLSCREEN | DOUBLEBUF
screen = pygame.display.set_mode((screen_width, screen_height), flags, 16)

# Define entire field size and initial camera position
field_width = field_height = 5000
camera_rect = pygame.Rect(field_width // 4 - screen_width // 2, field_height // 4 - screen_height // 2, screen_width, screen_height)

# frame control
FPS = 60
fps_clock = pygame.time.Clock()

# Allow only cretain events (for performance)
pygame.event.set_allowed([pygame.QUIT, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP])

# Load background image
background_grid_img = pygame.image.load("img/background_grid.png").convert()

# Load image for Player sprite
player_img = pygame.image.load("img/character/player.png").convert()

# Load target pointer image
target_pointer_img = pygame.image.load("img/target_pointer/target_pointer.png").convert()
target_pointer_img.set_colorkey((0, 0, 0))          # Make black background invisible(transparent)

# Load image for PlayerNormalBullet sprite
player_normal_bullet_animation = []
for i in range(4):
    new_frame = pygame.image.load("img/projectiles/player_normal_bullet{}.png".format(i // 2)).convert()
    new_frame.set_colorkey((255, 255, 255))         # Make white background invisible(transparent)
    player_normal_bullet_animation.append(new_frame)

# Load image for PlayerEnergyCannonBall sprite
player_energy_cannonball_animation = []
for i in range(4):
    new_frame = pygame.image.load("img/projectiles/player_energy_cannonball{}.png".format(i // 2)).convert()
    new_frame.set_colorkey((255, 255, 255))         # Make white background invisible(transparent)
    player_energy_cannonball_animation.append(new_frame)

# Load 64 image frames for animating spawneffect
spawneffect_animation = []
for i in range(8):
    for j in range(8):
        new_frame = pygame.image.load("img/spawneffect/spawneffect_{}_{}.png".format(i, j)).convert()
        new_frame.set_colorkey((0, 0, 0))           # Set black background of all image frames as transparent
        spawneffect_animation.append(new_frame)

# Load 9 image frames for animating hiteffect
hiteffect_animation = []
for i in range(9):
    new_frame = pygame.image.load("img/hiteffect/hit_000{}.png".format(i)).convert_alpha()
    new_frame.set_colorkey((0, 0, 0))               # Set black background of all image frames as transparent
    hiteffect_animation.append(new_frame)

# Load image for shockwave
shockwave_image = pygame.image.load("img/explosion/shockwave.png").convert()
shockwave_image.set_colorkey((255, 255, 255))       # Set white background as transparent

# Load image frames for animating explosions, all animations have shockwave image at the first frame
explosion_animation_list_small = []         # For 32x32 images
for i in [5, 7]:
    explosion_animation = [shockwave_image]
    j = 0
    while True:
        path = "img/explosion/expl_{:0>2}_{:0>4}.png".format(i, j)
        if not os.path.exists(path):
            break
        new_frame = pygame.image.load(path).convert_alpha()
        explosion_animation.append(new_frame)
        j += 1
    explosion_animation_list_small.append(explosion_animation)

explosion_animation_list_medium = []        # For 64x64 images
for i in [1, 2, 3, 4, 6, 8]:
    explosion_animation = [shockwave_image]
    j = 0
    while True:
        path = "img/explosion/expl_{:0>2}_{:0>4}.png".format(i, j)
        if not os.path.exists(path):
            break
        new_frame = pygame.image.load(path).convert_alpha()
        explosion_animation.append(new_frame)
        j += 1
    explosion_animation_list_medium.append(explosion_animation)

explosion_animation_list_large = []        # For 96x96 and 128x128 images
for i in [9, 10, 11]:
    explosion_animation = [shockwave_image]
    j = 0
    while True:
        path = "img/explosion/expl_{:0>2}_{:0>4}.png".format(i, j)
        if not os.path.exists(path):
            break
        new_frame = pygame.image.load(path).convert_alpha()
        explosion_animation.append(new_frame)
        j += 1
    explosion_animation_list_large.append(explosion_animation)

# Load images for StraightLineMover sprites
straight_line_mover1_img = pygame.image.load("img/character/straight_line_mover1.png").convert()
straight_line_mover1_hit_img = pygame.image.load("img/character/straight_line_mover1_hit.png").convert()
straight_line_mover2_img = pygame.image.load("img/character/straight_line_mover2.png").convert()
straight_line_mover2_hit_img = pygame.image.load("img/character/straight_line_mover2_hit.png").convert()
straight_line_mover3_img = pygame.image.load("img/character/straight_line_mover3.png").convert()
straight_line_mover3_hit_img = pygame.image.load("img/character/straight_line_mover3_hit.png").convert()
