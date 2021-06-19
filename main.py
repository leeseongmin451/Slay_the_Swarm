import pygame


# Initialize the pygame
pygame.init()

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
