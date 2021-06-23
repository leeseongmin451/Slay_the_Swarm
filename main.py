import pygame
from pygame.locals import *
import math
import time


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
        self.x_pos = self.y_pos = 400
        self.max_speed = 360
        self.speed = 0
        self.max_x_speed = self.max_y_speed = 0
        self.x_speed = self.y_speed = 0
        self.acc = 1800

        # Image & rect attributes
        self.image = pygame.transform.scale(player_img, [30, 30])
        self.rect = self.image.get_rect()
        self.rect.center = [self.x_pos, self.y_pos]

        # Attributes for weapons
        self.weapons = [PlayerMinigun()]        # List of all weapons currently equipped by player
        self.target_pos = [0, 0]                # Target position to shoot, equivalent to cursor position

    def update(self, fps):
        """
        Update function for moving player sprite, using weapons per frame
        :param fps: for calculating moving distance per frame in pixels (speed(px/sec) / fps(frame/sec) = pixels per frame(px/frame))
        :return: None
        """

        # Accelerate player with WASD key
        keys = pygame.key.get_pressed()         # Get keyboard inputs
        w_pressed, s_pressed, a_pressed, d_pressed = \
            int(keys[pygame.K_w]), int(keys[pygame.K_s]), int(keys[pygame.K_a]), int(keys[pygame.K_d])  # 1 for pressed, 0 for released
        # Move only if W, S inputs or A, D inputs are different
        if (w_pressed ^ s_pressed) or (a_pressed ^ d_pressed):
            move_angle_direction = (w_pressed*math.pi*3/2 + s_pressed*math.pi/2 + a_pressed*math.pi +
                                    d_pressed*(2*math.pi if w_pressed else 0)) / \
                                   (w_pressed + s_pressed + a_pressed + d_pressed)      # Determine moving direction in radians
            self.max_x_speed = self.max_speed * math.cos(move_angle_direction)
            self.max_y_speed = self.max_speed * math.sin(move_angle_direction)
        else:
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

        # Move the position of player according to current speed (per FPS)
        # And set the actual position on the screen
        self.x_pos += self.x_speed / fps
        self.y_pos += self.y_speed / fps
        self.rect.center = [round(self.x_pos), round(self.y_pos)]

        # Use all equipped weapons
        for weapon in self.weapons:
            weapon.update(self.rect.center, self.target_pos)

    def aim(self, target_pos):
        """
        Update target position
        :param target_pos: target position value to update
        :return: None
        """

        self.target_pos = target_pos


class PlayerMinigun:
    """
    A weapon class which player sprite can use.
    Shoots one/multiple lines of small bullets.
    This is an abstract sprite and invisible on the screen.
    """

    def __init__(self):
        self.level = 1                          # Level of this weapon
        self.pos = [0, 0]                       # Will follow player's position
        self.target_pos = [0, 0]                # Will follow cursor position

        self.attack_interval = .1               # 10 attacks/sec
        self.last_attacked_time = time.time()   # A fixed timepoint to measure interval

    def update(self, pos, target_pos):
        """
        Update the target position and check firing interval.
        :param pos: position of weapon's user(player sprite)
        :param target_pos: target position to shoot at
        :return: None
        """

        # update positions
        self.pos = pos
        self.target_pos = target_pos

        # After attack interval, calculate shotting angle and call "attack" method
        if time.time() - self.last_attacked_time >= self.attack_interval:
            relative_x = self.target_pos[0] - self.pos[0]
            relative_y = self.target_pos[1] - self.pos[1]
            aiming_angle = math.atan2(relative_y, relative_x)

            self.attack(aiming_angle)
            self.last_attacked_time = time.time()       # reset last_attacked_time to now

    def attack(self, aiming_angle):
        """
        Shoots bullet(s) every interval.
        Attack pattern depends on this weapon's level.
        :param aiming_angle: direction to shoot in radians
        :return: None
        """

        if self.level == 1:
            PlayerNormalBullet(self.pos, 600, aiming_angle, 1)


class PlayerNormalBullet(pygame.sprite.Sprite):
    """
    A bullet class shot from PlayerMinigun class.
    Moves straight line from the player to aimed direction.
    Killed(disappears) when collided with enemy sprites and gives damage to them.
    """

    def __init__(self, fired_pos, speed, angle, power):
        pygame.sprite.Sprite.__init__(self)

        # Position & speed attributes
        self.x_pos, self.y_pos = fired_pos          # Initial position
        self.x_speed = speed * math.cos(angle)      # Derive speed of x/y direction from given speed and shooting angle
        self.y_speed = speed * math.sin(angle)

        # Image & rect attributes
        self.image = pygame.Surface([5, 5])
        self.image.fill((0, 255, 255))
        self.rect = self.image.get_rect()
        self.rect.center = [self.x_pos, self.y_pos]

        # Damage dealt to enemy
        self.power = power

        # Add this instance to
        all_sprites.add(self)

    def update(self, fps):
        """
        Update function for moving bullet sprite
        :param fps: for calculating moving distance per frame in pixels (speed(px/sec) / fps(frame/sec) = pixels per frame(px/frame))
        :return: None
        """

        # move bullet
        self.x_pos += self.x_speed / fps
        self.y_pos += self.y_speed / fps
        self.rect.center = [round(self.x_pos), round(self.y_pos)]

        # Kill the bullet sprite when it goes out of screen
        if not (0 <= self.rect.centerx < 1920 and 0 <= self.rect.centery < 1080):
            self.kill()


# Create the screen
flags = FULLSCREEN | DOUBLEBUF
screen = pygame.display.set_mode((1920, 1080), flags, 16)

# Game title and icon
icon = pygame.image.load("img/icon/icon.png")
pygame.display.set_icon(icon)                   # Set icon
pygame.display.set_caption("Slay the Swarm")    # Set title

# frame control
FPS = 60
fps_clock = pygame.time.Clock()

# Allow only cretain events (for performance)
pygame.event.set_allowed([pygame.QUIT, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP])

# Load all images
player_img = pygame.image.load("img/character/player.png").convert()

# Generate sprite groups
all_sprites = pygame.sprite.Group()     # Contains all sprites subject to update every frame

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

    # Get cursor position on the screen
    curspos = pygame.mouse.get_pos()

    # Update all sprites
    all_sprites.update(FPS)
    player.aim(curspos)

    # All colors will be represented with RGB tuple (r, g, b)
    screen.fill((0, 0, 0))      # fill the screen background with black(0, 0, 0) before drawing all other sprites

    # Draw all sprites
    all_sprites.draw(screen)

    pygame.display.update()     # update all display changes and show them
    fps_clock.tick(FPS)         # make program never run at more than "FPS" frames per second
