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
        self.max_speed = 180
        self.speed = 0
        self.x_speed = self.y_speed = 0
        self.acc = 6

        # Image & rect attributes
        self.image = pygame.Surface([30, 30])
        self.image.fill((255, 255, 255))        # player color white
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
        keys = pygame.key.get_pressed()
        current_speed = rms(self.x_speed, self.y_speed)

        if keys[pygame.K_w]:        # Accelerate upwards with key "w"
            if current_speed < self.max_speed:
                self.y_speed -= self.acc
        elif self.y_speed < 0:
            self.y_speed += self.acc

        if keys[pygame.K_s]:        # Accelerate downwards with key "s"
            if current_speed < self.max_speed:
                self.y_speed += self.acc
        elif self.y_speed > 0:
            self.y_speed -= self.acc

        if keys[pygame.K_a]:        # Accelerate left with key "a"
            if current_speed < self.max_speed:
                self.x_speed -= self.acc
        elif self.x_speed < 0:
            self.x_speed += self.acc

        if keys[pygame.K_d]:        # Accelerate right with key "d"
            if current_speed < self.max_speed:
                self.x_speed += self.acc
        elif self.x_speed > 0:
            self.x_speed -= self.acc

        # Move the position of player according to current speed (per fps)
        # And set the actual position on the screen
        self.x_pos += self.x_speed / fps
        self.y_pos += self.y_speed / fps
        self.rect.topleft = [round(self.x_pos), round(self.y_pos)]


# Create the screen
screen = pygame.display.set_mode((1200, 800))

# Game title and icon
icon = pygame.image.load("icon.png")
pygame.display.set_icon(icon)                   # Set icon
pygame.display.set_caption("Slay the Swarm")    # Set title

# frame control
fps = 60
fps_clock = pygame.time.Clock()

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
