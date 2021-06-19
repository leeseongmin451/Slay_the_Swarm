import pygame


# Initialize the pygame
pygame.init()

# Create the screen
screen = pygame.display.set_mode((1200, 800))

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
