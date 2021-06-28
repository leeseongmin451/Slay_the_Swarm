"""
Python file for initializing screen and loading all images needed
"""

import pygame
from pygame.locals import *


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

# Load images for StraightLineMover sprites
straight_line_mover1_img = pygame.image.load("img/character/straight_line_mover1.png").convert()
straight_line_mover1_hit_img = pygame.image.load("img/character/straight_line_mover1_hit.png").convert()
straight_line_mover2_img = pygame.image.load("img/character/straight_line_mover2.png").convert()
straight_line_mover2_hit_img = pygame.image.load("img/character/straight_line_mover2_hit.png").convert()
straight_line_mover3_img = pygame.image.load("img/character/straight_line_mover3.png").convert()
straight_line_mover3_hit_img = pygame.image.load("img/character/straight_line_mover3_hit.png").convert()
