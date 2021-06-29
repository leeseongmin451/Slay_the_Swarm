import time
import math
import random

import pygame.sprite

from initial_set_load import *


def get_distance(pos1, pos2):
    """
    Calculate distance between two given (x, y) coordinate points usin Pythagorean theoram
    :param pos1: first point
    :param pos2: second point
    :return: distance of two points
    """

    x_difference = pos1[0] - pos2[0]
    y_difference = pos1[1] - pos2[1]
    return math.sqrt(x_difference*x_difference + y_difference*y_difference)


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
        self.size = [20, 10]
        self.image_frame_list = player_normal_bullet_animation[::(60 // FPS)]        # Get image frames according to fps
        self.n_frames = len(self.image_frame_list)                          # Number of frames

        # Rotate image towards moving direction
        for n in range(self.n_frames):
            rotated_image = pygame.transform.rotate(self.image_frame_list[n], -angle * 180 / math.pi)
            self.image_frame_list[n] = rotated_image

        # Get new rect object from rotated image
        rotated_rect = self.image_frame_list[0].get_rect()
        self.rotated_image_w, self.rotated_image_h = rotated_rect.w, rotated_rect.h

        self.current_frame_num = 0                                          # Variable for counting frames
        self.image = pygame.transform.scale(self.image_frame_list[self.current_frame_num], [self.rotated_image_w // 2, self.rotated_image_h // 2])   # Get first image to display
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

        # Blink the image of bullet
        self.image = pygame.transform.scale(self.image_frame_list[self.current_frame_num % self.n_frames], [self.rotated_image_w // 2, self.rotated_image_h // 2])
        self.current_frame_num += 1

        # Check collision with any of enemy sprites
        collided_enemies = pygame.sprite.spritecollide(self, all_enemies, False)    # Check collision with enemy sprite
        if collided_enemies:                # If one or more sprite collided with bullet
            enemy = collided_enemies[0]     # Only one enemy sprite will get damaged (Because bullet cannot deal splash damage).
            # Damage value will be random, but has current power as mean value.
            damage = self.power * random.uniform(0.5, 1.5)
            enemy.get_damage(damage)
            HitEffect(self.camera_rect, [self.x_pos, self.y_pos])       # Generate hiteffect
            self.kill()                     # Delete the bullet after collision

        # Move bullet
        self.x_pos += self.x_speed / fps
        self.y_pos += self.y_speed / fps
        self.rect.center = [round(self.x_pos - self.camera_rect.left), round(self.y_pos - self.camera_rect.top)]

        # Delete the bullet sprite when it goes too far from the center of screen
        if get_distance([screen_width // 2, screen_height // 2], self.rect.center) > 1500:
            self.kill()


class SpawnEffect(pygame.sprite.Sprite):
    """
    An effect sprite generated right before an enemy appears.
    """

    def __init__(self, camera, pos, size):
        pygame.sprite.Sprite.__init__(self)

        # Camera attribute to calculate relative position from screen
        self.camera_rect = camera

        # Set position
        self.x_pos, self.y_pos = pos        # Spawneffect's field position given by sprite to be generated

        # Size & image attributes
        self.size = size            # Spawneffect's size given by sprite to be generated
        self.image_frame_list = spawneffect_animation[::(60 // FPS)]        # Get image frames according to fps
        self.n_frames = len(self.image_frame_list)                          # Number of frames
        self.current_frame_num = 0                                          # Variable for counting frames
        self.image = pygame.transform.scale(self.image_frame_list[self.current_frame_num], self.size)   # Get first image to display
        self.rect = self.image.get_rect()

        # Calculate the spawneffect's actual position on screen using camera center position
        self.rect.centerx = round(self.x_pos - self.camera_rect.centerx) % field_width + screen_width // 2 - field_width // 2
        self.rect.centery = round(self.y_pos - self.camera_rect.centery) % field_height + screen_height // 2 - field_height // 2

        # Attribute for check whether spawning animation is over
        # This attribute will be referenced by the enemy sprite generated from this spawneffect.
        # Enemy sprite will be actually displayed and move/attack only if value of this attribute is True.
        self.complete = False

        # Add this sprite to sprite groups
        all_sprites.add(self)
        spawneffect_group.add(self)

    def update(self, fps):
        """
        Update(change) image for spawning animation at each frame.
        :return: None
        """

        # Calculate the spawneffect's actual position on screen using camera center position
        self.rect.centerx = round(self.x_pos - self.camera_rect.centerx) % field_width + screen_width // 2 - field_width // 2
        self.rect.centery = round(self.y_pos - self.camera_rect.centery) % field_height + screen_height // 2 - field_height // 2

        # Update image at each frame
        if self.current_frame_num < self.n_frames:
            # Update image if frames to display remains
            self.image = pygame.transform.scale(self.image_frame_list[self.current_frame_num], self.size)
            self.current_frame_num += 1     # Increment frame number
        else:
            # Kill this effect if no new image to display remains
            self.complete = True
            self.kill()


class HitEffect(pygame.sprite.Sprite):
    """
    An effect sprite generated when a bullet collide with enemy sprite
    """

    def __init__(self, camera, pos):
        pygame.sprite.Sprite.__init__(self)

        # Camera attribute to calculate relative position from screen
        self.camera_rect = camera

        # Set position
        self.x_pos, self.y_pos = pos        # Hiteffect's field position given by bullet collided with enemy sprite

        # Size & image attributes
        self.size = [48, 48]
        self.image_frame_list = hiteffect_animation[::(60 // FPS)]          # Get image frames according to fps
        self.n_frames = len(self.image_frame_list)                          # Number of frames
        self.current_frame_num = 0                                          # Variable for counting frames
        self.image = pygame.transform.scale(self.image_frame_list[self.current_frame_num], self.size)   # Get first image to display
        self.rect = self.image.get_rect()

        # Calculate the hiteffect's actual position on screen using camera center position
        self.rect.centerx = round(self.x_pos - self.camera_rect.centerx + field_width // 2) % field_width + screen_width // 2 - field_width // 2
        self.rect.centery = round(self.y_pos - self.camera_rect.centery + field_height // 2) % field_height + screen_height // 2 - field_height // 2

        # Add this sprite to sprite groups
        all_sprites.add(self)
        hiteffect_group.add(self)

    def update(self, fps):
        """
        Update(change) image for hitting animation at each frame.
        :return: None
        """

        # Calculate the hiteffect's actual position on screen using camera center position
        self.rect.centerx = round(self.x_pos - self.camera_rect.centerx + field_width // 2) % field_width + screen_width // 2 - field_width // 2
        self.rect.centery = round(self.y_pos - self.camera_rect.centery + field_height // 2) % field_height + screen_height // 2 - field_height // 2

        # Update image at each frame
        if self.current_frame_num < self.n_frames:
            # Update image if frames to display remains
            self.image = pygame.transform.scale(self.image_frame_list[self.current_frame_num], self.size)
            self.current_frame_num += 1     # Increment frame number
        else:
            # Kill this effect if no new image to display remains
            self.kill()


class Explosion(pygame.sprite.Sprite):
    """
    An effect sprite generated when a enemy sprite killed or large projectiles (cannonballs, rockets, etc) exploded
    """

    def __init__(self, camera, pos, size):
        pygame.sprite.Sprite.__init__(self)

        # Camera attribute to calculate relative position from screen
        self.camera_rect = camera

        # Set position
        self.x_pos, self.y_pos = pos        # Explosion's field position given by bullet collided with enemy sprite

        # Size & image attributes
        self.size = size
        self.n_frames = 0
        # Select right size of explosion animation according to size
        while not self.n_frames:
            if self.size[0] < 128:
                self.image_frame_list = random.choice(explosion_animation_list_small)[::(60 // FPS)]        # Get image frames according to fps
            elif self.size[0] < 256:
                self.image_frame_list = random.choice(explosion_animation_list_medium)[::(60 // FPS)]       # Get image frames according to fps
            else:
                self.image_frame_list = random.choice(explosion_animation_list_large)[::(60 // FPS)]        # Get image frames according to fps
            self.n_frames = len(self.image_frame_list)                          # Number of frames
        self.current_frame_num = 0                                          # Variable for counting frames
        self.image = pygame.transform.scale(self.image_frame_list[self.current_frame_num], self.size)   # Get first image to display
        self.rect = self.image.get_rect()

        # Calculate the explosion's actual position on screen using camera center position
        self.rect.centerx = round(self.x_pos - self.camera_rect.centerx) % field_width + screen_width // 2 - field_width // 2
        self.rect.centery = round(self.y_pos - self.camera_rect.centery) % field_height + screen_height // 2 - field_height // 2

        # Add this sprite to sprite groups
        all_sprites.add(self)
        explosion_group.add(self)

    def update(self, fps):
        """
        Update(change) image for hitting animation at each frame.
        :return: None
        """

        # Calculate the explosions's actual position on screen using camera center position
        self.rect.centerx = round(self.x_pos - self.camera_rect.centerx) % field_width + screen_width // 2 - field_width // 2
        self.rect.centery = round(self.y_pos - self.camera_rect.centery) % field_height + screen_height // 2 - field_height // 2

        # Update image at each frame
        if self.current_frame_num < self.n_frames:
            # Update image if frames to display remains
            self.image = pygame.transform.scale(self.image_frame_list[self.current_frame_num], self.size)
            self.current_frame_num += 1     # Increment frame number
        else:
            # Kill this effect if no new image to display remains
            self.kill()


class StraightLineMover(pygame.sprite.Sprite):
    """
    Enemy sprite
    Moves only through stright line, does not attack player.
    """

    def __init__(self, camera, hp, speed, size, norm_image, hit_image):
        pygame.sprite.Sprite.__init__(self)

        # Camera attribute to calculate relative position from screen
        self.camera_rect = camera

        # Attributes related to HP and dealing with damage event
        self.hp = hp                            # Max HP for StraightLineMover sprite
        self.got_damaged = False                # Indicates whether got damaged
        self.blink_count = 6                    # The two images will take turn being displayed 3 times for each
        self.frames_per_blink = FPS // 30       # Blinking animation will be displayed at 30fps
        self.current_damage_animation_frame = 0

        # Position and speed attributes
        self.x_pos = random.randrange(0, field_width)           # Generating position is completely random in entire field
        self.y_pos = random.randrange(0, field_height)          # Same as x_pos
        self.speed = speed                                      # Moves at a fixed random speed
        self.direction = random.uniform(-math.pi, math.pi)      # Moves towards a fixed, random direction in radians
        self.x_speed = self.speed * math.cos(self.direction)    # Calculate x-direction speed using trigonometry
        self.y_speed = self.speed * math.sin(self.direction)    # Same as x_speed

        # Size & image attributes
        self.size = size
        self.norm_image = pygame.transform.scale(norm_image, self.size)         # Normal image of StraightLineMover instance
        self.hit_image = pygame.transform.scale(hit_image, self.size)           # Image displayed only when got damaged, slightly brighter than normal one
        self.image_list = [self.norm_image, self.hit_image]                     # Image list for faster image selection
        self.current_imagenum = 0
        self.image = self.image_list[self.current_imagenum]                     # Initially set current image to normal image
        self.rect = self.image.get_rect()

        # Calculate the spawneffect's actual position on screen using camera center position
        self.rect.centerx = round(self.x_pos - self.camera_rect.centerx) % field_width + screen_width // 2 - field_width // 2
        self.rect.centery = round(self.y_pos - self.camera_rect.centery) % field_height + screen_height // 2 - field_height // 2

        # Add this sprite to sprite groups
        all_sprites.add(self)

        # Attribute to check whether spawneffect animation is complete
        self.spawning = True
        self.spawneffect = SpawnEffect(self.camera_rect, [self.x_pos, self.y_pos], self.size)   # Generate spawneffect

    def update(self, fps):
        """
        Move sprite by updating position. Does nothing until spawneffect animation ends.
        :param fps: for calculating moving distance per frame in pixels (speed(px/sec) / fps(frame/sec) = pixels per frame(px/frame))
        :return: None
        """

        # Does nothing until spawneffect animation ends
        if self.spawning:
            if self.spawneffect.complete:
                self.spawning = False
                all_enemies.add(self)       # Add sprite to enemy sprite group to draw
        else:
            # Deal with damage event
            if self.got_damaged:
                if self.current_damage_animation_frame % self.frames_per_blink == 0:
                    self.current_imagenum = (self.current_imagenum + 1) % 2     # Change imagenum to 0 or 1
                    self.blink_count -= 1                                       # Reduce remaining blinking counts
                    self.image = self.image_list[self.current_imagenum]     # Set the image according to imagenum

                self.current_damage_animation_frame += 1                    # Count frames passed from got damaged

                # If blinking animation ends
                if self.blink_count == 0:
                    self.current_imagenum = 0       # Set the image to normal one
                    self.got_damaged = False        # No blinking until getting another damage
                    self.image = self.image_list[self.current_imagenum]     # Set the image according to imagenum

            # Update position
            self.x_pos += self.x_speed / fps
            self.y_pos += self.y_speed / fps

        # Calculate the spawneffect's actual position on screen using camera center position
        self.rect.centerx = round(self.x_pos - self.camera_rect.centerx) % field_width + screen_width // 2 - field_width // 2
        self.rect.centery = round(self.y_pos - self.camera_rect.centery) % field_height + screen_height // 2 - field_height // 2

    def get_damage(self, damage):
        """
        Reduce HP when collided with projectile from player(attacked by player). Call death function when HP <= 0
        :param damage: power of the projectile
        :return: None
        """

        # Start blinking animation and initialize blink count
        self.got_damaged = True
        self.blink_count = 6

        # Apply damage by reducing HP, or call death() if HP <= 0
        self.hp -= damage
        if self.hp <= 0:
            self.death()

    def death(self):
        """
        Generate explosion effect and coins/item, then delete sprite
        :return: None
        """

        # Generate explosion animation twice as big as self, then killed
        explode_size = [self.size[0] * 3, self.size[1] * 3]
        Explosion(self.camera_rect, [self.x_pos, self.y_pos], explode_size)
        self.kill()


class StraightLineMover1(StraightLineMover):
    """
    A child class that inherited StraightLineMover class
    Has 1 HP, 30x30 pixel size, and speed of 300~500 pixels/sec.
    """

    def __init__(self, camera):
        StraightLineMover.__init__(
            self,
            camera=camera,
            hp=1,
            speed=random.uniform(300, 500),
            size=[30, 30],
            norm_image=straight_line_mover1_img,
            hit_image=straight_line_mover1_hit_img
        )
        straight_line_mover1_group.add(self)


class StraightLineMover2(StraightLineMover):
    """
    A child class that inherited StraightLineMover class
    Has 5 HP, 50x50 pixel size, and speed of 200~350 pixels/sec.
    """

    def __init__(self, camera):
        StraightLineMover.__init__(
            self,
            camera=camera,
            hp=5,
            speed=random.uniform(200, 350),
            size=[50, 50],
            norm_image=straight_line_mover2_img,
            hit_image=straight_line_mover2_hit_img
        )
        straight_line_mover2_group.add(self)


class StraightLineMover3(StraightLineMover):
    """
    A child class that inherited StraightLineMover class
    Has 20 HP, 100x100 pixel size, and speed of 100~250 pixels/sec.
    """

    def __init__(self, camera):
        StraightLineMover.__init__(
            self,
            camera=camera,
            hp=20,
            speed=random.uniform(100, 250),
            size=[100, 100],
            norm_image=straight_line_mover3_img,
            hit_image=straight_line_mover3_hit_img
        )
        straight_line_mover3_group.add(self)


# Generate sprite groups
all_sprites = pygame.sprite.Group()             # Contains all sprites subject to update every frame

# Generate additional sprite groups to specify drawing order
player_group = pygame.sprite.Group()            # Only player sprite will be added here
player_projectiles = pygame.sprite.Group()      # All projectiles shot from player

spawneffect_group = pygame.sprite.Group()       # Sprite group for all spawn effects
hiteffect_group = pygame.sprite.Group()         # Sprite group for all hit effects
explosion_group = pygame.sprite.Group()         # Sprite group for all explosions

all_enemies = pygame.sprite.Group()                 # Sprite group for all enemy sprites
straight_line_mover1_group = pygame.sprite.Group()  # Sprite group for StraightLineMover1 sprites
straight_line_mover2_group = pygame.sprite.Group()  # Sprite group for StraightLineMover2 sprites
straight_line_mover3_group = pygame.sprite.Group()  # Sprite group for StraightLineMover3 sprites
