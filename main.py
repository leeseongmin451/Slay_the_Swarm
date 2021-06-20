import pygame


# Initialize the pygame
pygame.init()


# Player sprite
class Player(pygame.sprite.Sprite):
    """
    A player class which user can control
    """

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        # HP & MP attributes
        self.full_hp = 100
        self.hp = self.full_hp
        self.full_mp = 100
        self.mp = self.full_mp

        # score & coins attribute
        self.score = 0
        self.coins = 0

        # Position, Speed & acceleration attribute
        # Unit of speed: pixel/sec
        # Unit of acceleration: pixel/sec^2
        self.x_pos = self.y_pos = 0
        self.max_speed = 180
        self.speed = 0
        self.x_speed = self.y_speed = 0
        self.acc = 6

        # Attributes for attack
        self.weapons = []


# Create the screen
screen = pygame.display.set_mode((1200, 800))

# Game title and icon
icon = pygame.image.load("icon.png")
pygame.display.set_icon(icon)                   # Set icon
pygame.display.set_caption("Slay the Swarm")    # Set title


# Main game loop
running = True      # Variable to check whether continue game
while running:

    # Get all events occurred during the game
    for event in pygame.event.get():
        # Check whether quit button clicked
        if event.type == pygame.QUIT:
            running = False

    # All colors will be represented with RGB tuple (r, g, b)
    screen.fill((0, 0, 0))      # fill the screen background with black(0, 0, 0) before drawing all other sprites

    pygame.display.update()     # update all display changes and show them
