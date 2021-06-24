"""
Python file for initializing screen and loading all images needed
"""

import pygame
from pygame.locals import *


pygame.init()


# Game title and icon
icon = pygame.image.load("img/icon/icon.png")
pygame.display.set_icon(icon)                   # Set icon
pygame.display.set_caption("Slay the Swarm")    # Set title

# Create the screen
screen_width, screen_height = 1920, 1080
flags = FULLSCREEN | DOUBLEBUF
screen = pygame.display.set_mode((screen_width, screen_height), flags, 16)

# frame control
FPS = 60
fps_clock = pygame.time.Clock()

# Allow only cretain events (for performance)
pygame.event.set_allowed([pygame.QUIT, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP])

# Load background image
background_grid_img = pygame.image.load("img/background_grid.png").convert()

# Load image for Player sprite
player_img = pygame.image.load("img/character/player.png").convert()
