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


# Background class
class Background:
    """
    Background movement control & display class.
    5000px x 5000px background is splitted into 4 2500px x 2500px subbackground and controlled individually
    to implement infinitly scrolled background.
    """

    def __init__(self, image, screen_size, camera):
        self.image = image
        self.part_width, self.part_height = self.image.get_size()
        self.screen_w, self.screen_h = screen_size
        self.camera_rect = camera

        # Define four part of background
        self.part00_rect = self.image.get_rect()        # upper left part
        self.part10_rect = self.image.get_rect()        # upper right part
        self.part01_rect = self.image.get_rect()        # lower left part
        self.part11_rect = self.image.get_rect()        # lower right part

    def update(self):
        """
        Move the background image at opposite direction of camera(player) movement.
        Using remainder operation, the part of background too far from camera can be moved in front of the direction of camera movement.
        :return: None
        """

        self.part00_rect.centerx = self.part01_rect.centerx = \
            self.screen_w // 2 + (1.5 * self.part_width - self.camera_rect.centerx) % (2 * self.part_width) - self.part_width
        self.part10_rect.centerx = self.part11_rect.centerx = \
            self.screen_w // 2 + (2.5 * self.part_width - self.camera_rect.centerx) % (2 * self.part_width) - self.part_width

        self.part00_rect.centery = self.part10_rect.centery = \
            self.screen_h // 2 + (1.5 * self.part_height - self.camera_rect.centery) % (2 * self.part_height) - self.part_height
        self.part01_rect.centery = self.part11_rect.centery = \
            self.screen_h // 2 + (2.5 * self.part_height - self.camera_rect.centery) % (2 * self.part_height) - self.part_height

    def draw(self, surface):
        """
        Display background image at a desired position
        :param surface: surface to display
        :return: None
        """

        surface.blit(self.image, self.part00_rect)
        surface.blit(self.image, self.part10_rect)
        surface.blit(self.image, self.part01_rect)
        surface.blit(self.image, self.part11_rect)


# Player sprite
class Player(pygame.sprite.Sprite):
    """
    A player class which user can control
    """

    def __init__(self, camera):
        pygame.sprite.Sprite.__init__(self)

        # camera attribute following the player
        self.camera_rect = camera

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
        self.max_speed = 360
        self.speed = 0
        self.max_x_speed = self.max_y_speed = 0
        self.x_speed = self.y_speed = 0
        self.acc = 1800

        # Image & rect attributes
        self.image = pygame.transform.scale(player_img, [30, 30])
        self.rect = self.image.get_rect()
        self.rect.center = [round(self.x_pos - self.camera_rect.left), round(self.y_pos - self.camera_rect.top)]

        # Attributes for weapons
        self.weapons = [PlayerMinigun(self.camera_rect)]        # List of all weapons currently equipped by player
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
        # And set the actual position on the screen with respect to camera position
        self.x_pos += self.x_speed / fps
        self.y_pos += self.y_speed / fps
        self.rect.center = [round(self.x_pos - self.camera_rect.left), round(self.y_pos - self.camera_rect.top)]

        # Use all equipped weapons
        for weapon in self.weapons:
            weapon.update([self.x_pos, self.y_pos], self.target_pos)

    def aim(self, target_pos):
        """
        Update target position
        :param target_pos: target position value to update
        :return: None
        """

        self.target_pos = target_pos

    def get_pos(self):
        return self.x_pos, self.y_pos

    def set_pos(self, pos):
        """
        Setting method : player's position on screen
        :param pos: position to set
        :return: None
        """

        self.x_pos, self.y_pos = pos


class PlayerMinigun:
    """
    A weapon class which player sprite can use.
    Shoots one/multiple lines of small bullets.
    This is an abstract sprite and invisible on the screen.
    """

    def __init__(self, camera):
        self.camera_rect = camera               # camera attribute to give as a parameter of bullet class

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
            PlayerNormalBullet(self.camera_rect, self.pos, 600, aiming_angle, 1)


class PlayerNormalBullet(pygame.sprite.Sprite):
    """
    A bullet class shot from PlayerMinigun class.
    Moves straight line from the player to aimed direction.
    Killed(disappears) when collided with enemy sprites and gives damage to them.
    """

    def __init__(self, camera, fired_pos, speed, angle, power):
        pygame.sprite.Sprite.__init__(self)

        # camera attribute to calculate relative position from screen
        self.camera_rect = camera

        # Position & speed attributes
        self.x_pos, self.y_pos = fired_pos          # Initial position
        self.x_speed = speed * math.cos(angle)      # Derive speed of x/y direction from given speed and shooting angle
        self.y_speed = speed * math.sin(angle)

        # Image & rect attributes
        self.image = pygame.Surface([5, 5])
        self.image.fill((0, 255, 255))
        self.rect = self.image.get_rect()
        self.rect.center = [round(self.x_pos - self.camera_rect.left), round(self.y_pos - self.camera_rect.top)]

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
        self.rect.center = [round(self.x_pos - self.camera_rect.left), round(self.y_pos - self.camera_rect.top)]

        # Kill the bullet sprite when it goes out of screen
        if not (0 <= self.rect.centerx < 1920 and 0 <= self.rect.centery < 1080):
            self.kill()


# Create the screen
screen_width, screen_height = 1920, 1080
flags = FULLSCREEN | DOUBLEBUF
screen = pygame.display.set_mode((screen_width, screen_height), flags, 16)

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
background_grid_img = pygame.image.load("img/background_grid.png").convert()
player_img = pygame.image.load("img/character/player.png").convert()

# Define entire field size and initial camera position
field_width = field_height = 5000
camera_rect = pygame.Rect(field_width // 4 - screen_width // 2, field_height // 4 - screen_height // 2, screen_width, screen_height)

# Define background
background = Background(background_grid_img, [screen_width, screen_height], camera_rect)

# Generate sprite groups
all_sprites = pygame.sprite.Group()     # Contains all sprites subject to update every frame

# Generate player instance and add to sprite group
player = Player(camera_rect)
player.set_pos([field_width // 4, field_height // 4])
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
    curspos_screen = pygame.mouse.get_pos()        # Position displayed on screen
    curspos_field = [curspos_screen[0] + camera_rect.left, curspos_screen[1] + camera_rect.top]     # Actual position on game field

    # Update all sprites
    all_sprites.update(FPS)
    player.aim(curspos_field)

    # Set camera position to player
    camera_rect.center = player.get_pos()

    # Update background position with respect to screen
    background.update()

    # Draw background gridlines
    background.draw(screen)

    # Draw all sprites
    all_sprites.draw(screen)

    pygame.display.update()     # update all display changes and show them
    fps_clock.tick(FPS)         # make program never run at more than "FPS" frames per second
