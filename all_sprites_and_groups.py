import time
import math
import random

import pygame.sprite

from initial_set_load import *


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

        # Automatically add self to sprite groups
        all_sprites.add(self)
        player_group.add(self)

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

        # Automatically add self to sprite groups
        all_sprites.add(self)
        player_projectiles.add(self)

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


class StraightLineMover1(pygame.sprite.Sprite):
    """
    Enemy sprite
    Moves only through stright line, does not attack player.
    """

    def __init__(self, camera):
        pygame.sprite.Sprite.__init__(self)

        self.camera_rect = camera

        self.size = [20, 20]
        self.norm_image = pygame.transform.scale(straight_line_mover1_img, self.size)
        self.hit_image = pygame.transform.scale(straight_line_mover1_hit_img, self.size)

        self.image = self.norm_image
        self.rect = self.image.get_rect()

        self.hp = 1

        self.x_pos = self.y_pos = 0         # needs to be random
        self.speed = random.uniform(300, 500)
        self.direction = random.uniform(-math.pi, math.pi)
        self.x_speed = self.speed * math.cos(self.direction)
        self.y_speed = self.speed * math.sin(self.direction)

        all_sprites.add(self)
        all_enemies.add(self)

    def update(self, fps):
        self.x_pos += self.x_speed
        self.y_pos += self.y_speed

    def get_damage(self, damage):
        self.hp -= damage
        if self.hp <= 0:
            self.death()

    def death(self):
        pass


# Generate sprite groups
all_sprites = pygame.sprite.Group()             # Contains all sprites subject to update every frame

# Generate additional sprite groups to specify drawing order
player_group = pygame.sprite.Group()            # Only player sprite will be added here
player_projectiles = pygame.sprite.Group()      # All projectiles shot from player
all_enemies = pygame.sprite.Group()             # Sprite group for all enemy sprites
