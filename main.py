import pygame
import math


# Initialize the pygame
pygame.init()


def rms(*args):
    """
    Returns root-mean-square of input values.
    :param args:
    :return:
    """

    return math.sqrt(sum([x*x for x in args]))


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
        self.max_speed = 240
        self.speed = 0
        self.max_x_speed = self.max_y_speed = 0
        self.x_speed = self.y_speed = 0
        self.acc = 1200

        # Image & rect attributes
        self.image = pygame.transform.scale(player_img, [30, 30])
        self.rect = self.image.get_rect()
        self.rect.topleft = [self.x_pos, self.y_pos]

        # Attributes for weapons
        self.weapons = []

    def update(self):
        """
        Update function for moving player sprite, using weapons per frame
        :return: None
        """

        # Accelerate player with WASD key
        keys = pygame.key.get_pressed()         # Get keyboard inputs
        wsad_pressed = [keys[pygame.K_w], keys[pygame.K_s], keys[pygame.K_a], keys[pygame.K_d]]     # Get only WSAD inputs

        # Determine max speed in x/y direction according to combination of WSAD keys
        # Restrict max speed for x, y direction within 70.7% of max speed when moving diagonal direction using two keys
        if wsad_pressed == [True, False, False, False]:     # Accelerate up
            self.max_x_speed = 0
            self.max_y_speed = -self.max_speed
        elif wsad_pressed == [False, True, False, False]:   # Accelerate down
            self.max_x_speed = 0
            self.max_y_speed = self.max_speed
        elif wsad_pressed == [False, False, True, False]:   # Accelerate left
            self.max_x_speed = -self.max_speed
            self.max_y_speed = 0
        elif wsad_pressed == [False, False, False, True]:   # Accelerate right
            self.max_x_speed = self.max_speed
            self.max_y_speed = 0
        elif wsad_pressed == [True, False, True, False]:    # Accelerate up & left
            self.max_x_speed = -self.max_speed / math.sqrt(2)
            self.max_y_speed = -self.max_speed / math.sqrt(2)
        elif wsad_pressed == [True, False, False, True]:    # Accelerate up & right
            self.max_x_speed = self.max_speed / math.sqrt(2)
            self.max_y_speed = -self.max_speed / math.sqrt(2)
        elif wsad_pressed == [False, True, True, False]:    # Accelerate down & left
            self.max_x_speed = -self.max_speed / math.sqrt(2)
            self.max_y_speed = self.max_speed / math.sqrt(2)
        elif wsad_pressed == [False, True, False, True]:    # Accelerate down & right
            self.max_x_speed = self.max_speed / math.sqrt(2)
            self.max_y_speed = self.max_speed / math.sqrt(2)
        else:                                               # Stop when all other combinations of keys
            self.max_x_speed = self.max_y_speed = 0

        # Increment or decrement x/y direction speed
        # Do not accelerate when current speed is near 0. (-acc/2 <= speed <= acc/2)
        # for x direction
        if self.x_speed < self.max_x_speed - self.acc / (2 * fps):
            self.x_speed += self.acc / fps
        elif self.x_speed > self.max_x_speed + self.acc / (2 * fps):
            self.x_speed -= self.acc / fps
        # for y direction
        if self.y_speed < self.max_y_speed - self.acc / (2 * fps):
            self.y_speed += self.acc / fps
        elif self.y_speed > self.max_y_speed + self.acc / (2 * fps):
            self.y_speed -= self.acc / fps

        # Move the position of player according to current speed (per fps)
        # And set the actual position on the screen
        self.x_pos += self.x_speed / fps
        self.y_pos += self.y_speed / fps
        self.rect.topleft = [round(self.x_pos), round(self.y_pos)]


# Create the screen
screen = pygame.display.set_mode((1200, 800))

# Game title and icon
icon = pygame.image.load("img/icon/icon.png")
pygame.display.set_icon(icon)                   # Set icon
pygame.display.set_caption("Slay the Swarm")    # Set title

# frame control
fps = 60
fps_clock = pygame.time.Clock()

# Load all images
player_img = pygame.image.load("img/character/player.png").convert()

# Generate sprite groups
all_sprites = pygame.sprite.Group()

# Generate player instance and add to sprite group
player = Player()
all_sprites.add(player)


# Main game loop
running = True      # Variable to check whether continue game
while running:

    # Get all events occurred during the game
    for event in pygame.event.get():
        # Check whether quit button clicked
        if event.type == pygame.QUIT:
            running = False

    # Update all sprites
    all_sprites.update()

    # All colors will be represented with RGB tuple (r, g, b)
    screen.fill((0, 0, 0))      # fill the screen background with black(0, 0, 0) before drawing all other sprites

    # Draw all sprites
    all_sprites.draw(screen)

    pygame.display.update()     # update all display changes and show them
    fps_clock.tick(fps)         # make program never run at more than "fps" frames per second
