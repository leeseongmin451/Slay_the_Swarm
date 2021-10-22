import math
import random

import pygame.sprite

from initial_set_load import *


# Global variable for score
player_score = [0]


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


class FieldVibrationController:
    """
    Field offset controller for field vibrating effect.
    Uses sine function to implement vibrating magnitude, length, frequency, and attenuation

    FieldVibrationController has two types of vibrating pattern.

    Vibration: Vibrating magnitude should be constant,
    so the attenuation constant will be 1.

    Shake: Occurs when a big explosion effect or death of a boss sprite happens.
    Vibrating magnitude should be gradually decrease at a constant ratio(attenuation).
    So the attenuation constant will be less than 1.
    """

    def __init__(self):
        self.vibe_magnitude = 0         # Magnitude of vinration
        self.vibe_length = 0            # Length of vibration in frames
        self.vibe_frequency = 0         # Frequency of vibration in Hz

        self.vibe_type = None           # "v": vibration, "s": shaking
        self.attenuation_const = -1     # Attenuation of vibration

        self.now_vibrating = False      # Indicates whether start vibrating

    def initialize(self, magnitude, length, frequency=30, vibe_type="v"):
        """
        Start vibration with given vibration parameters
        :param magnitude:
        :param length:
        :param frequency:
        :param vibe_type:
        :return: None
        """

        # Set vibrating attributes
        self.vibe_type = vibe_type          # Whether vibrate or shake
        self.vibe_magnitude = magnitude     # Initial magnitude
        self.vibe_length = length           # Length of vibration in frames
        self.vibe_frequency = frequency     # Frequency of vibration in Hz

        # Determine attenuation constant according to vibration type
        if self.vibe_type == "v":           # For vibrating
            self.attenuation_const = 1
        if self.vibe_type == "s":           # For shaking
            self.attenuation_const = (1 / self.vibe_magnitude) ** (1 / self.vibe_length)

        self.now_vibrating = True           # Start vibration

    def update(self):
        """
        Calculate field offset using vibrating attrubutes at each loop of game
        :return: current field offset
        """

        field_offset = 0        # Field offset to be calculated

        if self.now_vibrating:
            # Calculate field offset
            field_offset = self.vibe_magnitude * math.sin(math.pi * self.vibe_frequency * self.vibe_length / FPS)

            self.vibe_magnitude *= self.attenuation_const   # Attenuate magnitude
            self.vibe_length -= 1                           # Count remaining vibration length

            # If vibration ends
            if self.vibe_length <= 0:
                field_offset = 0            # Reset field offset
                self.now_vibrating = False

        return field_offset


# Player sprite
class Player(pygame.sprite.Sprite):
    """
    A player class which user can control
    """

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        # Attributes related to HP and dealing with damage event
        self.full_hp = 100
        self.hp = self.full_hp
        self.got_damaged = False                # Indicates whether got damaged
        self.blink_count = 6                    # The two images will take turn being displayed 3 times for each
        self.frames_per_blink = FPS // 30       # Blinking animation will be displayed at 30fps
        self.current_damage_animation_frame = 0

        # MP attributes
        self.full_mp = 100
        self.mp = self.full_mp

        # score & coins attribute
        self.score = 0
        self.coins = 0
        self.coin_magnet_range = 100

        # Position, Speed & acceleration attribute
        # Unit of speed: pixel/sec
        # Unit of acceleration: pixel/sec^2
        self.x_pos, self.y_pos = screen_width // 2, screen_height // 2          # Same as the camrea center position
        self.max_speed = 360
        self.speed = 0
        self.max_x_speed = self.max_y_speed = 0
        self.x_speed = self.y_speed = 0
        self.acc = 1800

        # Image & rect attributes
        self.norm_image = pygame.transform.scale(player_img, [30, 30])          # Normal image of Player
        self.hit_image = pygame.Surface([30, 30])                               # Image displayed only when got damaged
        self.hit_image.fill((255, 0, 0))                                        # Blink red
        self.image_list = [self.norm_image, self.hit_image]                     # Image list for faster image selection
        self.current_imagenum = 0
        self.image = self.image_list[self.current_imagenum]                     # Initially set current image to normal image
        self.rect = self.image.get_rect()
        x_offset = screen_width // 2 - field_width // 2
        y_offset = screen_height // 2 - field_height // 2
        self.rect.centerx = round(self.x_pos - camera_offset[0] - x_offset) % field_width + x_offset
        self.rect.centery = round(self.y_pos - camera_offset[1] - y_offset) % field_height + y_offset

        # Attributes for weapons
        self.target_pos = [0, 0]                                # Target position to shoot, equivalent to cursor position
        # Automatic weapon: Only aiming is controlled by mouse, and attacking will be done automatically
        self.automatic_weapon = PlayerMinigun(self)
        # Manual weapon: Both aiming and attacking are controlled by mouse movement and clicking
        self.manual_weapon = PlayerEnergyCannonLauncher(self)

        # Death attribute
        self.dead = False

        # Automatically add self to sprite groups
        all_sprites.add(self)
        player_group.add(self)

    def update(self, curspos, mouse_button_down):
        """
        Update function for moving player sprite, using weapons per frame
        :param curspos: current cursor position on screen
        :param mouse_button_down: variable to check holding mouse button
        :return: None
        """

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
        if self.x_speed < self.max_x_speed - self.acc / (2 * FPS):
            self.x_speed += self.acc / FPS
        elif self.x_speed > self.max_x_speed + self.acc / (2 * FPS):
            self.x_speed -= self.acc / FPS
        # for y direction
        if self.y_speed < self.max_y_speed - self.acc / (2 * FPS):
            self.y_speed += self.acc / FPS
        elif self.y_speed > self.max_y_speed + self.acc / (2 * FPS):
            self.y_speed -= self.acc / FPS

        # Move the position of player according to current speed (per FPS)
        # And set the actual position on the screen with respect to camera position
        self.x_pos += self.x_speed / FPS
        self.y_pos += self.y_speed / FPS
        x_offset = screen_width // 2 - field_width // 2
        y_offset = screen_height // 2 - field_height // 2
        self.rect.centerx = round(self.x_pos - camera_offset[0] - x_offset) % field_width + x_offset
        self.rect.centery = round(self.y_pos - camera_offset[1] - y_offset) % field_height + y_offset

        # Use all equipped weapons
        self.automatic_weapon.update()
        self.manual_weapon.update(mouse_button_down)

        # Check collision with any of enemy sprites
        collided_enemies = pygame.sprite.spritecollide(self, all_enemies, False)    # Check collision with enemy sprite
        for enemy in collided_enemies:
            self.get_damage(enemy.touch_damage)     # Apply damage to player
            enemy.death()                           # Kill the touched enemy

        # Collect coins in a specified range
        for coin in coin_group:
            if get_distance(self.rect.center, coin.rect.center) < self.coin_magnet_range:
                coin.attract(self.rect.center)
                self.coins += coin.coin_amount

        # HP & MP regeneration
        self.hp = min(self.full_hp, self.hp + self.full_hp / (100 * FPS))
        self.mp = min(self.full_mp, self.mp + self.full_mp / (150 * FPS))

        # Get score update
        self.update_score()

    def aim(self, target_pos):
        """
        Update target position
        :param target_pos: target position value to update
        :return: None
        """

        self.target_pos = target_pos

    def get_pos(self):
        """
        Returns player's position in field
        :return: player's position in field
        """

        return self.x_pos, self.y_pos

    def set_pos(self, pos):
        """
        Setting method : player's position on screen
        :param pos: position to set
        :return: None
        """

        self.x_pos, self.y_pos = pos

    def update_score(self):
        """
        Increase score when killed an enemy
        :return: None
        """

        self.score = player_score

    def get_damage(self, damage):
        """
        Reduce player's HP. If HP <= 0 then kill player
        :param damage: Amount of damage
        :return: None
        """

        # Start blinking animation and initialize blink count
        self.got_damaged = True
        self.blink_count = 6

        self.hp -= damage       # Reduce HP of player
        if self.hp <= 0:
            self.death()

    def death(self):
        self.dead = True


class TargetPointer(pygame.sprite.Sprite):
    """
    A very simple sprite class which visualizes cursor targeting point.
    Just follows cursor.
    """

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        self.size = [30, 30]
        self.image = pygame.transform.scale(target_pointer_img, self.size)
        self.rect = self.image.get_rect()

        target_pointer_group.add(self)

    def update(self, curspos):
        """
        Update position of target pointer
        :return: None
        """

        self.rect.center = curspos


class BossPointer(pygame.sprite.Sprite):
    """
    An arrow-shaped sprite which indicates the location of boss sprite.
    Appears only at boss phase.
    """

    def __init__(self, targeting_from, targeting_to):
        pygame.sprite.Sprite.__init__(self)

        # Define targeting-from/to sprites
        self.targeting_from = targeting_from
        self.targeting_to = targeting_to

        # Use two images for implementing rotation of arrow
        self.image_orig = pygame.transform.scale(boss_pointer_img, (80, 15))    # Original image before rotating
        self.image = self.image_orig.copy()                                     # Image to rotate
        self.rect = self.image.get_rect()
        self.rect.center = self.targeting_from.rect.center                      # Set position

        # Add this sprite to sprite groups
        all_sprites.add(self)
        target_pointer_group.add(self)

    def update(self, curspos, mouse_button_down):
        """
        Rotate image according to relative position of two sprites
        :param curspos: current cursor position on screen
        :param mouse_button_down: variable to check holding mouse button
        :return: None
        """

        # Reset position
        self.rect.center = self.targeting_from.rect.center

        # Calculate rotation angleof arrow to indicate targeting direction
        dist_x = self.targeting_to.rect.centerx - self.targeting_from.rect.centerx
        dist_y = self.targeting_to.rect.centery - self.targeting_from.rect.centery
        angle = math.atan2(dist_y, dist_x) * 180 / math.pi

        # Rotate image and set position
        new_image = pygame.transform.rotate(self.image_orig, -angle)    # Rotate image
        old_center = self.rect.center                                   # Copy position of original image
        self.image = new_image                                          # Apply rotated image
        self.rect = self.image.get_rect()                               # Get new rect from rotated image
        self.rect.center = old_center                                   # Set position of new image rect


class PlayerMinigun:
    """
    A weapon class which player sprite can use.
    Shoots one/multiple lines of small bullets.
    This is an abstract sprite and invisible on the screen.
    """

    def __init__(self, weapon_user: Player):
        self.user = weapon_user                     # User of this weapon (player)

        self.level = 1                              # Level of this weapon
        self.pos = [0, 0]                           # Will follow player's position
        self.target_pos = [0, 0]                    # Will follow cursor position
        self.aiming_angle = 0

        self.attack_interval = 6                    # 6 frames/attack (10 attacks/sec)
        self.passed_frames_from_last_attack = 0     # To measure elapsed time from last attack

    def update(self):
        """
        Update the target position and check firing interval.
        :return: None
        """

        # Update positions
        self.pos = self.user.rect.center
        self.target_pos = self.user.target_pos

        # After attack interval, calculate shooting angle and call "attack" method
        self.passed_frames_from_last_attack += 1
        if self.passed_frames_from_last_attack >= self.attack_interval:
            relative_x = self.target_pos[0] - self.pos[0]
            relative_y = self.target_pos[1] - self.pos[1]
            self.aiming_angle = math.atan2(relative_y, relative_x)

            self.attack()
            self.passed_frames_from_last_attack = 0       # reset passed_frames_from_last_attack to 0

    def attack(self):
        """
        Shoots bullet(s) every interval.
        Attack pattern depends on this weapon's level.
        :return: None
        """

        if self.level == 1:
            PlayerNormalBullet(self, 600, self.aiming_angle, 1)


class PlayerNormalBullet(pygame.sprite.Sprite):
    """
    A bullet class shot from PlayerMinigun class.
    Moves straight line from the player to aimed direction.
    Killed(disappears) when collided with enemy sprites and gives damage to them.
    """

    def __init__(self, fired_weapon, speed, angle, power):
        pygame.sprite.Sprite.__init__(self)

        # Weapon which fired this sprite
        self.fired_weapon = fired_weapon

        # Position & speed attributes
        self.x_pos = self.fired_weapon.pos[0] + camera_offset[0]                # Initial x position
        self.y_pos = self.fired_weapon.pos[1] + camera_offset[1]                # Initial y position
        self.x_speed = speed * math.cos(angle)      # Derive speed of x/y direction from given speed and shooting angle
        self.y_speed = speed * math.sin(angle)

        # Image & rect attributes
        self.size = [20, 10]
        self.image_frame_list = player_normal_bullet_animation[::(60 // FPS)]           # Get image frames according to fps
        self.n_frames = len(self.image_frame_list)                                      # Number of frames

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

        # Set the sprite's screen position using field position and camera offset
        x_offset = screen_width // 2 - field_width // 2
        y_offset = screen_height // 2 - field_height // 2
        self.rect.centerx = round(self.x_pos - camera_offset[0] - x_offset) % field_width + x_offset
        self.rect.centery = round(self.y_pos - camera_offset[1] - y_offset) % field_height + y_offset

        # Damage dealt to enemy
        self.power = power

        # Automatically add self to sprite groups
        all_sprites.add(self)
        player_projectiles.add(self)

        # Check how many frames the bullet existed
        self.frames = 1

    def update(self, curspos, mouse_button_down):
        """
        Update function for moving bullet sprite
        :param curspos: current cursor position on screen
        :param mouse_button_down: variable to check holding mouse button
        :return: None
        """

        # Blink the image of bullet
        self.image = pygame.transform.scale(self.image_frame_list[self.current_frame_num % self.n_frames], [self.rotated_image_w // 2, self.rotated_image_h // 2])
        self.current_frame_num += 1

        if self.frames >= 5:
            # Check collision with any of enemy sprites for bullets existed at least 5 frames
            collided_enemies = pygame.sprite.spritecollide(self, all_enemies, False)    # Check collision with enemy sprite
            if collided_enemies:                # If one or more sprite collided with bullet
                enemy = collided_enemies[0]     # Only one enemy sprite will get damaged (Because bullet cannot deal splash damage).

                # Damage value will be random, but has current power as mean value.
                damage = self.power * random.uniform(0.5, 1.5)
                enemy.get_damage(damage)
                HitEffect(self)                 # Generate hiteffect
                self.kill()                     # Delete the bullet after collision

        # Move bullet
        self.x_pos += self.x_speed / FPS
        self.y_pos += self.y_speed / FPS

        # Update the sprite's screen position using field position and camera offset
        x_offset = screen_width // 2 - field_width // 2
        y_offset = screen_height // 2 - field_height // 2
        self.rect.centerx = round(self.x_pos - camera_offset[0] - x_offset) % field_width + x_offset
        self.rect.centery = round(self.y_pos - camera_offset[1] - y_offset) % field_height + y_offset

        # Delete the bullet sprite when it goes too far from the center of screen
        if get_distance([screen_width // 2, screen_height // 2], self.rect.center) > 1500:
            self.kill()

        # Increase existed frames of this bullet
        self.frames += 1


class PlayerEnergyCannonLauncher:
    """
    A weapon class which player sprite can use.
    Shoots large, exploding energy cannonball one by one.
    This is an abstract sprite and invisible on the screen.
    """

    def __init__(self, weapon_user: Player):
        self.user = weapon_user                     # User of this weapon (player)

        self.level = 1                              # Level of this weapon
        self.pos = [0, 0]                           # Will follow player's position
        self.target_pos = [0, 0]                    # Will follow cursor position
        self.aiming_angle = 0

        # Attributes for timing control of charging cannonball
        self.holding_cannonball = None                      # Will be PlayerEnergyCannonBall class instance if a cannonball is generated
        self.remaining_cannonball_holding_frame = 2 * FPS   # To measure remaining length of cannonball charging time (max: 2 seconds)

        # Attributes for cooling down weapon
        self.overheated = False                     # Can fire cannonball only if not overheated
        self.max_cooltime_frame_count = 4 * FPS     # Max length of time for cooling down weapon
        self.remaining_cooltime_frames = 0          # To measure remaining length of cooldown time

    def update(self, mouse_button_down):
        """
        Update the target position and check mouse button hold.
        :param mouse_button_down: to control weapon with mouse button held
        :return: None
        """

        # Update positions
        self.pos = self.user.rect.center
        self.target_pos = self.user.target_pos

        # Weapon control
        # Cannot use weapon while overheated
        if self.overheated:
            self.remaining_cooltime_frames -= 1         # Count on cooldown frames
            if self.remaining_cooltime_frames <= 0:     # If counting is complete
                self.overheated = False                 # Finish overheating

        # Can use weapon while not overheated
        else:
            if not self.holding_cannonball and mouse_button_down:               # If mouse button pressed while not having cannonball
                self.start_charging_cannonball()                                # Generate a cannonball
            if self.holding_cannonball:                                         # Charging cannonball
                self.remaining_cannonball_holding_frame -= 1                    # Count on charging frames

                # If mouse button released or counting is complete or player is out of MP
                if not mouse_button_down or self.remaining_cannonball_holding_frame <= 0 or self.user.mp <= 0:
                    self.release_cannonball()                                   # Release cannonball

    def start_charging_cannonball(self):
        """
        Generate a cannonball.
        self.holding_cannonball attribute will be changed from None to PlayerEnergyCannonBall class instance.
        :return: None
        """

        if self.level == 1:
            self.holding_cannonball = PlayerEnergyCannonBall(self, 600, 150)

    def release_cannonball(self):
        """
        Give cannonball speed and direction and release cannonball to that direction.
        :return: None
        """

        # Calculate shooting angle and speed and give them to cannonball
        relative_x = self.target_pos[0] - self.pos[0]
        relative_y = self.target_pos[1] - self.pos[1]
        self.aiming_angle = math.atan2(relative_y, relative_x)

        # Release cannonball
        self.holding_cannonball.set_direction(self.aiming_angle)

        # Calculate cooldown time according to the length of time for charging the cannonball
        self.remaining_cooltime_frames = round(4 * FPS * self.holding_cannonball.power / self.holding_cannonball.max_power)
        self.holding_cannonball = None                      # Now weapon holds no cannonball
        self.overheated = True                              # Player cannot use this weapon until overheating ends
        self.remaining_cannonball_holding_frame = 2 * FPS   # Initialize frame counter for cannonball holding


class PlayerEnergyCannonBall(pygame.sprite.Sprite):
    """
    A bullet class shot from PlayerEnergyCannonLauncher class.
    Moves straight line from the player to aimed direction.
    Killed(disappears) when collided with enemy sprites and gives direct damage to them with multiple explosion effect.
    It also attacks enemies within a specified range giving splash damage.
    """

    def __init__(self, fired_weapon, speed, max_power):
        pygame.sprite.Sprite.__init__(self)

        # Weapon which fired this sprite
        self.fired_weapon = fired_weapon

        # Position & speed attributes
        self.x_pos = self.fired_weapon.pos[0] + camera_offset[0]                # Initial x position
        self.y_pos = self.fired_weapon.pos[1] + camera_offset[1]                # Initial y position
        self.speed = speed
        self.x_speed = self.y_speed = 0

        # Image & rect attributes
        self.size = [5, 5]
        self.image_frame_list = player_energy_cannonball_animation[::(60 // FPS)]       # Get image frames according to fps
        self.n_frames = len(self.image_frame_list)                                      # Number of frames
        self.current_frame_num = 0                                                      # Variable for counting frames
        self.image = pygame.transform.scale(self.image_frame_list[self.current_frame_num], self.size)   # Get first image to display
        self.rect = self.image.get_rect()
        x_offset = screen_width // 2 - field_width // 2
        y_offset = screen_height // 2 - field_height // 2
        self.rect.centerx = round(self.x_pos - camera_offset[0] - x_offset) % field_width + x_offset
        self.rect.centery = round(self.y_pos - camera_offset[1] - y_offset) % field_height + y_offset

        # Maximum attributes of cannonball
        self.max_power = max_power      # Maximum power the cannonball can have when fully charged
        self.max_size = [60, 60]        # Maximum size the cannonball can have when fully charged

        # Per-frame attributes: increment amount per frame while charging
        self.power_charging_increment = self.max_power / (2 * FPS)                      # Power increasing speed
        self.size_charging_increment = (self.max_size[0] - self.size[0]) / (2 * FPS)    # Size increasing speed
        self.charging_mp = self.max_power / (6 * FPS)                                   # MP decreasing speed

        # Damage dealt to enemy
        self.power = self.power_charging_increment
        self.shock_range = self.power * 2               # Range of splash damage, proportional to power

        # Boolean attribute for charging
        self.charging = True

        # Automatically add self to sprite groups
        all_sprites.add(self)
        player_projectiles.add(self)

    def update(self, curspos, mouse_button_down):
        """
        Move cannonball by updating position.
        :param curspos: current cursor position on screen
        :param mouse_button_down: variable to check holding mouse button
        :return: None
        """

        # Blink the image of cannonball
        self.image = pygame.transform.scale(self.image_frame_list[self.current_frame_num % self.n_frames], [round(self.size[0]), round(self.size[1])])
        self.current_frame_num += 1

        # Cannonball control
        # Fixed to the position of weapon(or player) while charging
        if self.charging:
            # Increase power and shock range
            self.power += self.power_charging_increment
            self.shock_range = self.power * 2

            # Increase size
            self.size[0] += self.size_charging_increment
            self.size[1] += self.size_charging_increment

            # Fix the position to the center of weapon(or player) while charging
            self.x_pos = round(self.fired_weapon.pos[0] + camera_offset[0])
            self.y_pos = round(self.fired_weapon.pos[1] + camera_offset[1])
            self.rect = self.image.get_rect()

            # Decrease MP of player
            self.fired_weapon.user.mp -= self.charging_mp

        # Move cannonball if released
        else:
            # Move cannonball and update position on screen
            self.x_pos += self.x_speed / FPS
            self.y_pos += self.y_speed / FPS

        # Update the sprite's screen position using field position and camera offset
        x_offset = screen_width // 2 - field_width // 2
        y_offset = screen_height // 2 - field_height // 2
        self.rect.centerx = round(self.x_pos - camera_offset[0] - x_offset) % field_width + x_offset
        self.rect.centery = round(self.y_pos - camera_offset[1] - y_offset) % field_height + y_offset

        # Attack enemies
        # Check collision with any of enemy sprites
        collided_enemies = pygame.sprite.spritecollide(self, all_enemies, False)

        # If one or more enemy sprites touches cannonball
        if collided_enemies:
            # Apply full damage of cannonball on enemy which directly collided with cannonball
            collided_enemies[0].get_damage(self.power)

            # Applying splash damage on nearby enemies within shock range
            current_shock_range = self.shock_range

            # Check all enemy sprites whether it is in the shock range
            for enemy in all_enemies:
                distance_from_explosion = get_distance(self.rect.center, enemy.rect.center)     # Distance from cannonball to enemy

                # Apply partial damage of cannonball on all enemy sprites in the shock range
                if distance_from_explosion <= current_shock_range:
                    damage = (current_shock_range - distance_from_explosion) * self.power / current_shock_range
                    enemy.get_damage(damage)

            # Generate cluster explosion effect
            Explosion(self, [round(s * 8) for s in self.size])                          # Generate center explosion first

            # Generate additional explosions
            for _ in range(round(current_shock_range ** 2 / 20000)):                    # Number of explosions will be determined by the density of explosion
                size_multiplier = random.uniform(4, 8)                                  # Random size of explosion
                x_offset = random.uniform(-current_shock_range, current_shock_range)    # Random position of explosion (offset from center)
                y_offset = random.uniform(-current_shock_range, current_shock_range)
                Explosion(self, [round(s * size_multiplier) for s in self.size], offset=(x_offset, y_offset))   # Generate explosion with offset

            # Generate field shaking effect
            field_vibrator.initialize(20, 90, frequency=30, vibe_type="s")

            # Delete cannonball
            self.kill()

        # Delete the cannonball sprite when it goes too far from the center of screen
        if get_distance([screen_width // 2, screen_height // 2], self.rect.center) > 1500:
            self.kill()

    def set_direction(self, angle):
        """
        Calculate speed for x and y direction of cannonball and start moving.
        :param angle: direction to move
        :return: None
        """

        self.x_speed = self.speed * math.cos(angle)
        self.y_speed = self.speed * math.sin(angle)
        self.charging = False       # Complete charging


class SpawnEffect(pygame.sprite.Sprite):
    """
    An effect sprite generated right before an enemy appears.
    """

    def __init__(self, pos, size):
        pygame.sprite.Sprite.__init__(self)

        # Set position
        self.x_pos, self.y_pos = pos        # Spawneffect's field position given by sprite to be generated

        # Size & image attributes
        self.size = size            # Spawneffect's size given by sprite to be generated
        self.image_frame_list = spawneffect_animation[::(60 // FPS)]        # Get image frames according to fps
        self.n_frames = len(self.image_frame_list)                          # Number of frames
        self.current_frame_num = 0                                          # Variable for counting frames
        self.image = pygame.transform.scale(self.image_frame_list[self.current_frame_num], self.size)   # Get first image to display
        self.rect = self.image.get_rect()

        # Update the sprite's screen position using foeld position and camera offset
        x_offset = screen_width // 2 - field_width // 2
        y_offset = screen_height // 2 - field_height // 2
        self.rect.centerx = round(self.x_pos - camera_offset[0] - x_offset) % field_width + x_offset
        self.rect.centery = round(self.y_pos - camera_offset[1] - y_offset) % field_height + y_offset

        # Attribute for check whether spawning animation is over
        # This attribute will be referenced by the enemy sprite generated from this spawneffect.
        # Enemy sprite will be actually displayed and move/attack only if value of this attribute is True.
        self.complete = False

        # Add this sprite to sprite groups
        all_sprites.add(self)
        spawneffect_group.add(self)

    def update(self, curspos, mouse_button_down):
        """
        Update(change) image for spawning animation at each frame.
        :param curspos: current cursor position on screen
        :param mouse_button_down: variable to check holding mouse button
        :return: None
        """

        # Update the sprite's screen position using foeld position and camera offset
        x_offset = screen_width // 2 - field_width // 2
        y_offset = screen_height // 2 - field_height // 2
        self.rect.centerx = round(self.x_pos - camera_offset[0] - x_offset) % field_width + x_offset
        self.rect.centery = round(self.y_pos - camera_offset[1] - y_offset) % field_height + y_offset

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
    An effect sprite generated when a bullet collide with enemy or player sprite
    """

    def __init__(self, trigger_sprite):
        pygame.sprite.Sprite.__init__(self)

        # Bullet sprite generating this effect
        self.trigger_sprite = trigger_sprite      # Hiteffect's field position given by bullet collided with enemy sprite

        # Size & image attributes
        self.size = [48, 48]
        self.image_frame_list = hiteffect_animation[::(60 // FPS)]          # Get image frames according to fps
        self.n_frames = len(self.image_frame_list)                          # Number of frames
        self.current_frame_num = 0                                          # Variable for counting frames
        self.image = pygame.transform.scale(self.image_frame_list[self.current_frame_num], self.size)   # Get first image to display
        self.rect = self.image.get_rect()

        # Define the sprite's screen position
        self.rect.centerx = trigger_sprite.rect.centerx
        self.rect.centery = trigger_sprite.rect.centery

        # Calculate field position using screen position and camera offset
        self.x_pos = self.rect.centerx + camera_offset[0]
        self.y_pos = self.rect.centery + camera_offset[1]

        # Add this sprite to sprite groups
        all_sprites.add(self)
        hiteffect_group.add(self)

    def update(self, curspos, mouse_button_down):
        """
        Update(change) image for hitting animation at each frame.
        :param curspos: current cursor position on screen
        :param mouse_button_down: variable to check holding mouse button
        :return: None
        """

        # Update the sprite's screen position using field position and camera offset
        x_offset = screen_width // 2 - field_width // 2
        y_offset = screen_height // 2 - field_height // 2
        self.rect.centerx = round(self.x_pos - camera_offset[0] - x_offset) % field_width + x_offset
        self.rect.centery = round(self.y_pos - camera_offset[1] - y_offset) % field_height + y_offset

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

    def __init__(self, trigger_sprite, size, offset=(0, 0)):
        pygame.sprite.Sprite.__init__(self)

        # Projectile or enemy sprite generating this effect
        self.trigger_sprite = trigger_sprite

        # Size & image attributes
        self.size = size
        self.n_frames = 0
        # Select right size of explosion animation according to size
        while self.n_frames <= 1:
            if self.size[0] < 128:
                self.image_frame_list = random.choice(explosion_animation_list_small)[::(60 // FPS)]        # Get image frames according to fps
            elif self.size[0] < 256:
                self.image_frame_list = random.choice(explosion_animation_list_medium)[::(60 // FPS)]       # Get image frames according to fps
            else:
                self.image_frame_list = random.choice(explosion_animation_list_large)[::(60 // FPS)]        # Get image frames according to fps
            self.n_frames = len(self.image_frame_list)                          # Number of frames
        self.current_frame_num = 0                                          # Variable for counting frames
        self.shockwave_size = [round(self.size[0] * .7), round(self.size[1] * .7)]
        self.image = pygame.transform.scale(self.image_frame_list[self.current_frame_num], self.shockwave_size)       # Get first image(shockwave) to display
        self.rect = self.image.get_rect()

        # Define the sprite's screen position
        self.rect.centerx = trigger_sprite.rect.centerx + offset[0]
        self.rect.centery = trigger_sprite.rect.centery + offset[1]

        # Calculate field position using screen position and camera offset
        self.x_pos = self.rect.centerx + camera_offset[0]
        self.y_pos = self.rect.centery + camera_offset[1]

        # Add this sprite to sprite groups
        all_sprites.add(self)
        explosion_group.add(self)

    def update(self, curspos, mouse_button_down):
        """
        Update(change) image for hitting animation at each frame.
        :param curspos: current cursor position on screen
        :param mouse_button_down: variable to check holding mouse button
        :return: None
        """

        # Update the sprite's screen position using field position and camera offset
        x_offset = screen_width // 2 - field_width // 2
        y_offset = screen_height // 2 - field_height // 2
        self.rect.centerx = round(self.x_pos - camera_offset[0] - x_offset) % field_width + x_offset
        self.rect.centery = round(self.y_pos - camera_offset[1] - y_offset) % field_height + y_offset

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

    def __init__(self, hp, speed, size, touch_damage, norm_image, hit_image, coin_amount, score):
        pygame.sprite.Sprite.__init__(self)

        # Attributes related to HP and dealing with damage event
        self.full_hp = hp                       # Max HP for StraightLineMover sprite
        self.hp = self.full_hp                  # Current HP for StraightLineMover sprite
        self.got_damaged = False                # Indicates whether got damaged
        self.blink_count = 6                    # The two images will take turn being displayed 3 times for each
        self.frames_per_blink = FPS // 30       # Blinking animation will be displayed at 30fps
        self.current_damage_animation_frame = 0
        self.hp_bar = None                      # HP bar of this sprite (currently not displayed)

        # Position and speed attributes
        self.x_pos = self.y_pos = 0                             # Field position, will be determined after screen position is defined
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

        # Define the sprite's screen position
        self.rect.center = (random.randrange(0, field_width) + screen_width // 2 - field_width // 2,
                            random.randrange(0, field_height) + screen_height // 2 - field_height // 2)

        # Calculate field position using screen position and camera offset
        self.x_pos = self.rect.centerx + camera_offset[0]
        self.y_pos = self.rect.centery + camera_offset[1]

        # Touch damage which will be applied to player
        self.touch_damage = touch_damage

        # Coin amount & coin scatter speed attribute
        self.coin_amount = coin_amount
        self.coin_scatter_speed_min_max = (100 + 22 * self.coin_amount, 100 + 25 * self.coin_amount)

        # Score attribute
        self.score = score

        # Add this sprite to sprite groups
        all_sprites.add(self)

        # Attribute to check whether spawneffect animation is complete
        self.spawning = True
        self.spawneffect = SpawnEffect([self.x_pos, self.y_pos], self.size)   # Generate spawneffect

    def update(self, curspos, mouse_button_down):
        """
        Move sprite by updating position. Does nothing until spawneffect animation ends.
        :param curspos: current cursor position on screen
        :param mouse_button_down: variable to check holding mouse button
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
            self.x_pos += self.x_speed / FPS
            self.y_pos += self.y_speed / FPS

        # Update the sprite's screen position using field position and camera offset
        x_offset = screen_width // 2 - field_width // 2
        y_offset = screen_height // 2 - field_height // 2
        self.rect.centerx = round(self.x_pos - camera_offset[0] - x_offset) % field_width + x_offset
        self.rect.centery = round(self.y_pos - camera_offset[1] - y_offset) % field_height + y_offset

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
        # If HP bar already exists, delete it and generate new HP bar.
        if self.hp_bar:
            self.hp_bar.kill()
        if self.hp > 0:
            self.hp_bar = HPBar(self)
        else:
            self.death()

    def death(self):
        """
        Generate explosion effect and coins/item, then delete sprite
        :return: None
        """

        # Delete HP bar if exists
        if self.hp_bar:
            self.hp_bar.kill()

        # Scatter coins
        scatter_coins(self)

        # Give score to player
        player_score[0] += self.score

        # Generate explosion animation three times as big as self, then killed
        explode_size = [self.size[0] * 3, self.size[1] * 3]
        Explosion(self, explode_size)
        self.kill()


class StraightLineMover1(StraightLineMover):
    """
    A child class that inherited StraightLineMover class
    Has 1 HP, 30x30 pixel size, -15 touch damage, and speed of 300~500 pixels/sec.
    """
    group = pygame.sprite.Group()       # Sprite group for StraightLineMover1 sprites

    def __init__(self):
        StraightLineMover.__init__(
            self,
            hp=1,
            speed=random.uniform(300, 500),
            size=[30, 30],
            touch_damage=15,
            norm_image=straight_line_mover1_img,
            hit_image=straight_line_mover1_hit_img,
            coin_amount=10,
            score=10
        )
        StraightLineMover1.group.add(self)


class StraightLineMover2(StraightLineMover):
    """
    A child class that inherited StraightLineMover class
    Has 5 HP, 50x50 pixel size, -45 touch damage, and speed of 200~350 pixels/sec.
    """
    group = pygame.sprite.Group()       # Sprite group for StraightLineMover2 sprites

    def __init__(self):
        StraightLineMover.__init__(
            self,
            hp=5,
            speed=random.uniform(200, 350),
            size=[50, 50],
            touch_damage=45,
            norm_image=straight_line_mover2_img,
            hit_image=straight_line_mover2_hit_img,
            coin_amount=15,
            score=30
        )
        StraightLineMover2.group.add(self)


class StraightLineMover3(StraightLineMover):
    """
    A child class that inherited StraightLineMover class
    Has 20 HP, 100x100 pixel size, -143 touch damage, and speed of 100~250 pixels/sec.
    """
    group = pygame.sprite.Group()       # Sprite group for StraightLineMover3 sprites

    def __init__(self):
        StraightLineMover.__init__(
            self,
            hp=20,
            speed=random.uniform(100, 250),
            size=[100, 100],
            touch_damage=143,
            norm_image=straight_line_mover3_img,
            hit_image=straight_line_mover3_hit_img,
            coin_amount=30,
            score=100
        )
        StraightLineMover3.group.add(self)


class WallUnit(pygame.sprite.Sprite):
    """
    Enemy sprite



    It does not attack player.
    """

    def __init__(self, hp, screen_pos, speed, direction, size, touch_damage, norm_image, hit_image, coin_amount, score):
        pygame.sprite.Sprite.__init__(self)

        # Attributes related to HP and dealing with damage event
        self.full_hp = hp                       # Max HP for StraightLineMover sprite
        self.hp = self.full_hp                  # Current HP for StraightLineMover sprite
        self.got_damaged = False                # Indicates whether got damaged
        self.blink_count = 6                    # The two images will take turn being displayed 3 times for each
        self.frames_per_blink = FPS // 30       # Blinking animation will be displayed at 30fps
        self.current_damage_animation_frame = 0
        self.hp_bar = None                      # HP bar of this sprite (currently not displayed)

        # Position and speed attributes
        self.x_pos = self.y_pos = 0                             # Field position, will be determined after screen position is defined
        self.speed = speed                                      # Moves at a fixed random speed
        self.direction = direction                              # Will be up, down, left, or right

        # Set speed using direction info
        if self.direction == "up":
            self.x_speed = 0
            self.y_speed = -speed
        elif self.direction == "down":
            self.x_speed = 0
            self.y_speed = speed
        elif self.direction == "left":
            self.x_speed = -speed
            self.y_speed = 0
        else:
            self.x_speed = speed
            self.y_speed = 0

        # Size & image attributes
        self.size = size
        self.norm_image = pygame.transform.scale(norm_image, self.size)         # Normal image of StraightLineMover instance
        self.hit_image = pygame.transform.scale(hit_image, self.size)           # Image displayed only when got damaged, slightly brighter than normal one
        self.image_list = [self.norm_image, self.hit_image]                     # Image list for faster image selection
        self.current_imagenum = 0
        self.image = self.image_list[self.current_imagenum]                     # Initially set current image to normal image
        self.rect = self.image.get_rect()

        # Define the sprite's screen position
        self.rect.topleft = screen_pos

        # Calculate field position using screen position and camera offset
        self.x_pos = self.rect.centerx + camera_offset[0]
        self.y_pos = self.rect.centery + camera_offset[1]

        # Touch damage which will be applied to player
        self.touch_damage = touch_damage

        # Coin amount & coin scatter speed attribute
        self.coin_amount = coin_amount
        self.coin_scatter_speed_min_max = (100 + 22 * self.coin_amount, 100 + 25 * self.coin_amount)

        # Score attribute
        self.score = score

        # Add this sprite to sprite groups
        all_sprites.add(self)
        all_enemies.add(self)       # Add sprite to enemy sprite group to draw

    def update(self, curspos, mouse_button_down):
        """
        Move sprite by updating position.
        :param curspos: current cursor position on screen
        :param mouse_button_down: variable to check holding mouse button
        :return: None
        """

        # Deal with damage event
        if self.got_damaged:
            if self.current_damage_animation_frame % self.frames_per_blink == 0:
                self.current_imagenum = (self.current_imagenum + 1) % 2  # Change imagenum to 0 or 1
                self.blink_count -= 1  # Reduce remaining blinking counts
                self.image = self.image_list[self.current_imagenum]  # Set the image according to imagenum

            self.current_damage_animation_frame += 1  # Count frames passed from got damaged

            # If blinking animation ends
            if self.blink_count == 0:
                self.current_imagenum = 0  # Set the image to normal one
                self.got_damaged = False  # No blinking until getting another damage
                self.image = self.image_list[self.current_imagenum]  # Set the image according to imagenum

        # Update position
        self.x_pos += self.x_speed / FPS
        self.y_pos += self.y_speed / FPS

        # Update the sprite's screen position using field position and camera offset
        x_offset = screen_width // 2 - field_width // 2
        y_offset = screen_height // 2 - field_height // 2
        self.rect.centerx = round(self.x_pos - camera_offset[0] - x_offset) % field_width + x_offset
        self.rect.centery = round(self.y_pos - camera_offset[1] - y_offset) % field_height + y_offset

        # Kill this sprite if it goes out too far from player
        if not (-field_width // 2 < self.rect.centerx - screen_width // 2 < field_width // 2 and
                -field_height // 2 < self.rect.centery - screen_height // 2 < field_height // 2):
            self.kill()

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
        # If HP bar already exists, delete it and generate new HP bar.
        if self.hp_bar:
            self.hp_bar.kill()
        if self.hp > 0:
            self.hp_bar = HPBar(self)
        else:
            self.death()

    def death(self):
        """
        Generate explosion effect and coins/item, then delete sprite
        :return: None
        """

        # Delete HP bar if exists
        if self.hp_bar:
            self.hp_bar.kill()

        # Scatter coins
        scatter_coins(self)

        # Give score to player
        player_score[0] += self.score

        # Generate explosion animation three times as big as self, then killed
        explode_size = [self.size[0] * 3, self.size[1] * 3]
        Explosion(self, explode_size)
        self.kill()


class WallUnit1(WallUnit):
    """
    A child class that inherited WallUnit class
    Has 2 HP, 40x40 pixel size, and -15 touch damage.
    """
    group = pygame.sprite.Group()       # Sprite group for WallUnit1 sprites

    def __init__(self, screen_pos, speed, direction):
        WallUnit.__init__(
            self,
            hp=2,
            screen_pos=screen_pos,
            speed=speed,
            direction=direction,
            size=(40, 40),
            touch_damage=15,
            norm_image=wall_unit1_img,
            hit_image=wall_unit1_hit_img,
            coin_amount=5,
            score=5
        )
        WallUnit1.group.add(self)


class WallUnit2(WallUnit):
    """
    A child class that inherited WallUnit class
    Has 3 HP, 40x40 pixel size, and -25 touch damage.
    """
    group = pygame.sprite.Group()       # Sprite group for WallUnit2 sprites

    def __init__(self, screen_pos, speed, direction):
        WallUnit.__init__(
            self,
            hp=3,
            screen_pos=screen_pos,
            speed=speed,
            direction=direction,
            size=(40, 40),
            touch_damage=25,
            norm_image=wall_unit2_img,
            hit_image=wall_unit2_hit_img,
            coin_amount=7,
            score=8
        )
        WallUnit2.group.add(self)


class WallUnit3(WallUnit):
    """
    A child class that inherited WallUnit class
    Has 8 HP, 80x80 pixel size, and -56 touch damage.
    """
    group = pygame.sprite.Group()       # Sprite group for WallUnit3 sprites

    def __init__(self, screen_pos, speed, direction):
        WallUnit.__init__(
            self,
            hp=8,
            screen_pos=screen_pos,
            speed=speed,
            direction=direction,
            size=(70, 70),
            touch_damage=56,
            norm_image=wall_unit3_img,
            hit_image=wall_unit3_hit_img,
            coin_amount=18,
            score=25
        )
        WallUnit3.group.add(self)


class Wall:
    def __init__(self, walltype):
        self.walltype = walltype

        if self.walltype == 1:
            self.wall_unit_type = WallUnit1
            self.grid_size = 40
            self.speed = random.uniform(200, 300)
            self.grid_hcnt, self.grid_vcnt = random.choice([(1, random.randrange(1, 35)),
                                                            (random.randrange(1, 35), 1)])

        elif self.walltype == 2:
            self.wall_unit_type = WallUnit2
            self.grid_size = 40
            self.speed = random.uniform(250, 350)
            self.grid_hcnt, self.grid_vcnt = random.choice([(random.randrange(1, 3), random.randrange(1, 35)),
                                                            (random.randrange(1, 35), random.randrange(1, 3))])

        else:
            self.wall_unit_type = WallUnit3
            self.grid_size = 70
            self.speed = random.uniform(50, 100)
            self.grid_hcnt, self.grid_vcnt = random.choice([(random.randrange(1, 4), random.randrange(1, 20)),
                                                            (random.randrange(1, 20), random.randrange(1, 4))])

        self.width = self.grid_hcnt * self.grid_size
        self.height = self.grid_vcnt * self.grid_size

        self.x = random.uniform(-field_width // 2, field_width // 2 - self.width) + screen_width // 2
        if -self.width <= self.x <= screen_width:
            self.y = random.uniform(screen_height // 2 - field_height // 2, -self.height) if random.choice([1, 2]) == 1 \
                else random.uniform(screen_height, screen_height // 2 + field_height // 2 - self.height)

        else:
            self.y = random.uniform(-field_height // 2, field_height // 2 - self.height) + screen_height // 2

        self.topleft = (round(self.x), round(self.y))

        for m in range(self.grid_vcnt):
            for n in range(self.grid_hcnt):
                self.wall_unit_type((self.topleft[0] + n * self.grid_size, self.topleft[1] + m * self.grid_size),
                                    self.speed, random.choice(["up", "down", "left", "right"]))


"""
DEFINING BOSS SPRITES

Each level has a unique boss sprite at the last phase (phase 5).
The boss behaves and looks similar to commom enemy sprites, 
but has very high HP, attack patterns hard to deal with, and very big size.

When a boss is killed, it does disappear not immediately but with a time interval.
Multiple explosion effects surround boss sprite.
It gives a lot of score and coins after killed.
"""


class BossLV1(pygame.sprite.Sprite):
    """
    Level 1 Boss

    Boss Lv.1 has exactly same movement as StraightLineMover sprites,
    but has big size, high HP, slow speed.
    """

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        # Attributes related to HP and dealing with damage event
        self.full_hp = 400                      # Max HP for StraightLineMover sprite
        self.hp = self.full_hp                  # Current HP for StraightLineMover sprite
        self.got_damaged = False                # Indicates whether got damaged
        self.dead = False                       # For starting death effect of boss
        self.death_frame_count = 2 * FPS        # Disappears 2 secs after HP gets 0
        self.blink_count = 6                    # The two images will take turn being displayed 3 times for each
        self.frames_per_blink = FPS // 30       # Blinking animation will be displayed at 30fps
        self.current_damage_animation_frame = 0
        self.hp_bar = None                      # HP bar of this sprite (currently not displayed)

        # Position and speed attributes
        self.x_pos = self.y_pos = 0                             # Field position, will be determined after screen position is defined
        self.speed = 100                                        # Moves at a fixed random speed
        self.direction = random.uniform(-math.pi, math.pi)      # Moves towards a fixed, random direction in radians
        self.x_speed = self.speed * math.cos(self.direction)    # Calculate x-direction speed using trigonometry
        self.y_speed = self.speed * math.sin(self.direction)    # Same as x_speed

        # Size & image attributes
        self.size = [200, 200]
        self.norm_image = pygame.transform.scale(boss_lv1_img, self.size)       # Normal image of StraightLineMover instance
        self.hit_image = pygame.transform.scale(boss_lv1_hit_img, self.size)    # Image displayed only when got damaged, slightly brighter than normal one
        self.image_list = [self.norm_image, self.hit_image]                     # Image list for faster image selection
        self.current_imagenum = 0
        self.image = self.image_list[self.current_imagenum]                     # Initially set current image to normal image
        self.rect = self.image.get_rect()

        # Define the sprite's screen position
        # Boss sprite spawns out of screen, but not too far from player
        # One of four sides of screen will be selected to spawn on
        spawn_pos_type = random.choice(["up", "down", "left", "right"])
        if spawn_pos_type == "up":
            self.rect.centerx = random.randrange(-self.size[0], screen_width + self.size[0])
            self.rect.centery = -self.size[1]
        elif spawn_pos_type == "down":
            self.rect.centerx = random.randrange(-self.size[0], screen_width + self.size[0])
            self.rect.centery = screen_height + self.size[1]
        if spawn_pos_type == "left":
            self.rect.centerx = -self.size[0]
            self.rect.centery = random.randrange(-self.size[1], screen_height + self.size[1])
        elif spawn_pos_type == "right":
            self.rect.centerx = screen_width + self.size[0]
            self.rect.centery = random.randrange(-self.size[1], screen_height + self.size[0])

        # Calculate field position using screen position and camera offset
        self.x_pos = self.rect.centerx + camera_offset[0]
        self.y_pos = self.rect.centery + camera_offset[1]

        # Touch damage which will be applied to player
        self.touch_damage = 2300

        # Coin amount & coin scatter speed attribute
        self.coin_amount = 500
        self.coin_scatter_speed_min_max = (100 + 22 * self.coin_amount, 100 + 25 * self.coin_amount)

        # Score attribute
        self.score = 2500

        # Add this sprite to sprite groups
        all_sprites.add(self)
        all_enemies.add(self)

    def update(self, curspos, mouse_button_down):
        """
        Move sprite by updating position.
        :param curspos: current cursor position on screen
        :param mouse_button_down: variable to check holding mouse button
        :return: None
        """

        # Normal movement if HP > 0
        if not self.dead:
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
            self.x_pos += self.x_speed / FPS
            self.y_pos += self.y_speed / FPS

        # Generate sequential explosions for 2 seconds and then kill the boss sprite
        else:
            self.current_imagenum = (self.current_imagenum + 1) % 4     # Change imagenum to 0 or 1
            self.image = self.image_list[self.current_imagenum // 2]    # Set the image according to imagenum

            if random.random() < .15:
                size_multiplier = random.uniform(.4, 1.2)
                explosion_size = [round(s * size_multiplier) for s in self.size]
                explosion_x_offset = random.uniform(-self.rect.w, self.rect.w)
                explosion_y_offset = random.uniform(-self.rect.h, self.rect.h)
                Explosion(self, explosion_size, offset=(explosion_x_offset, explosion_y_offset))

            self.death_frame_count -= 1
            if self.death_frame_count <= 0:
                self.death()

        # Update the sprite's screen position using field position and camera offset
        x_offset = screen_width // 2 - field_width // 2
        y_offset = screen_height // 2 - field_height // 2
        self.rect.centerx = round(self.x_pos - camera_offset[0] - x_offset) % field_width + x_offset
        self.rect.centery = round(self.y_pos - camera_offset[1] - y_offset) % field_height + y_offset

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
        # If HP bar already exists, delete it and generate new HP bar.
        if self.hp_bar:
            self.hp_bar.kill()
        if self.hp > 0:
            self.hp_bar = HPBar(self)
        else:
            self.dead = True

    def death(self):
        """
        Generate explosion effect and coins/item, then delete sprite
        :return: None
        """

        # Delete HP bar if exists
        if self.hp_bar:
            self.hp_bar.kill()

        # Scatter coins
        scatter_coins(self)

        # Give score to player
        player_score[0] = self.score

        # Generate additional explosions
        explode_x_range = self.size[0] * 1.8
        explode_y_range = self.size[1] * 1.8
        for _ in range(round(explode_x_range * explode_y_range / 15000)):       # Number of explosions will be determined by the density of explosion
            size_multiplier = random.uniform(1, 4)                             # Random size of explosion
            x_offset = random.uniform(-explode_x_range, explode_x_range)        # Random position of explosion (offset from center)
            y_offset = random.uniform(-explode_y_range, explode_y_range)
            Explosion(self, [round(s * size_multiplier) for s in self.size], offset=(x_offset, y_offset))   # Generate explosion with offset

        # Generate field shaking effect
        field_vibrator.initialize(30, 120, frequency=30, vibe_type="s")

        # Delete sprite
        self.kill()


class HPBar(pygame.sprite.Sprite):
    """
    A rectangular sprite class which represents remaining HP of enemy sprite.

    All enemy sprites has green HPBar sprite class displayed right above them.
    HPBar sprites are displayed when enemy sprite gets damaged, and lasts only 3 seconds.
    """

    def __init__(self, parent_sprite):
        pygame.sprite.Sprite.__init__(self)

        self.parent_sprite = parent_sprite      # Sprite that has hp to visualize
        # The length of HP bar is determined by the ratio of current HP to full HP of sprite
        # The length of full HP bar is the same as width of sprite
        self.width = self.parent_sprite.rect.w * (self.parent_sprite.hp / self.parent_sprite.full_hp)

        self.image = pygame.Surface([round(self.width), 5])
        self.image.fill((0, 255, 0))            # HP bar has green color
        # Set the position of HP bar right above teh sprite
        self.rect = self.image.get_rect(topleft=(self.parent_sprite.rect.x, self.parent_sprite.rect.y - 10))

        # Add this sprite to sprite groups
        all_sprites.add(self)
        hp_bar_group.add(self)

        self.duration = 3 * FPS                 # Only lasts for 3 secs, then disappeare after 3 secs
        self.remaining_frames = self.duration   # Remaining frames to disappear

    def update(self, curspos, mouse_button_down):
        """
        Update position and duration
        :param curspos: current cursor position on screen
        :param mouse_button_down: variable to check holding mouse button
        :return: None
        """

        # Update position
        self.rect.topleft = (self.parent_sprite.rect.x, self.parent_sprite.rect.y - 10)

        # Count remaining frames
        self.remaining_frames -= 1

        # Delete HP bar after 3 seconds
        if self.remaining_frames <= 0:
            self.kill()

    def reset_timer(self):
        """
        Set the length of HP bar to the ratio of current HP and reset remaining duration to 3 secs
        :return: None
        """

        # Set the length of HP bar to the ratio of current HP
        self.width = self.parent_sprite.rect.w * (self.parent_sprite.hp / self.parent_sprite.full_hp)
        self.image = pygame.transform.scale(self.image, (round(self.width), 5))
        self.rect = self.image.get_rect(topleft=(self.parent_sprite.rect.x, self.parent_sprite.rect.y - 10))

        # reset remaining duration to 3 secs
        self.remaining_frames = self.duration


class Coin(pygame.sprite.Sprite):
    """
    A coin class collectable by player.

    Coin sprite is small, yellowish square object. When a enemy sprite is killed, several coins are scattered with
    explosion. Then if player approaches near to them, they are attarcted to the player and increases the player.coin
    attribute. Coins have size attributes, and bigger coins deal more.

    Initially generated coin has a fixed, random speed and direction.
    """

    def __init__(self, enemy_sprite, coin_amount):
        pygame.sprite.Sprite.__init__(self)

        # Size & image attributes
        # Size of a coin is determined by coin_amount attribute.
        self.coin_amount = coin_amount
        self.size = [round(math.sqrt(16 * self.coin_amount))] * 2
        self.image = pygame.Surface(self.size)
        self.image.fill((255, 255, 0))             # Yellow coin
        self.rect = self.image.get_rect()

        # Position speed, and acceleration attributes
        self.x_pos, self.y_pos = enemy_sprite.x_pos, enemy_sprite.y_pos     # Coin's field position given by killed enemy sprite
        self.scatter_speed_min_max = (300 + 5 * self.coin_amount, 450 + 8 * self.coin_amount)
        self.speed = random.uniform(*self.scatter_speed_min_max)            # Moves at a fixed random speed
        self.acc = -1500
        self.direction = random.uniform(-math.pi, math.pi)                  # Moves towards a fixed, random direction in radians
        self.x_speed = self.speed * math.cos(self.direction)                # Calculate x-direction speed using trigonometry
        self.y_speed = self.speed * math.sin(self.direction)                # Same as x_speed
        self.x_acc = self.acc * math.cos(self.direction)
        self.y_acc = self.acc * math.sin(self.direction)

        # Update the sprite's screen position using field position and camera offset
        x_offset = screen_width // 2 - field_width // 2
        y_offset = screen_height // 2 - field_height // 2
        self.rect.centerx = round(self.x_pos - camera_offset[0] - x_offset) % field_width + x_offset
        self.rect.centery = round(self.y_pos - camera_offset[1] - y_offset) % field_height + y_offset

        self.scattered = False          # Is scattering action over?
        self.attracted = False          # Is attraction by player started?
        self.attaction_center = None    # Origin of attraction

        # For caluculating duration
        self.existed_frames = 0
        self.duration = 6 * random.uniform(0.8, 1.2) * FPS

        # Add this sprite to sprite groups
        all_sprites.add(self)
        coin_group.add(self)

    def update(self, curspos, mouse_button_down):
        """
        Move sprite by updating position.
        :param curspos: current cursor position on screen
        :param mouse_button_down: variable to check holding mouse button
        :return: None
        """

        # Scattering - After the death of enemy sprite, starts at high speed, then slows down and stop on the field
        if not self.scattered:
            self.x_speed += self.x_acc / FPS
            self.y_speed += self.y_acc / FPS
        if abs(self.x_speed) < 60 or self.attracted:
            self.x_acc = self.y_acc = 0
            self.x_speed = self.y_speed = 0
            self.scattered = True

        self.x_pos += self.x_speed / FPS
        self.y_pos += self.y_speed / FPS

        # Update the sprite's screen position using field position and camera offset
        x_offset = screen_width // 2 - field_width // 2
        y_offset = screen_height // 2 - field_height // 2
        self.rect.centerx = round(self.x_pos - camera_offset[0] - x_offset) % field_width + x_offset
        self.rect.centery = round(self.y_pos - camera_offset[1] - y_offset) % field_height + y_offset

        # When collected by player
        if self.attaction_center and get_distance(self.rect.center, self.attaction_center) < 10:
            self.kill()

        # Kill coin after 6 secs (on average)
        self.existed_frames += 1
        if self.existed_frames > self.duration:
            self.kill()

    def attract(self, attraction_center):
        """
        Change direction and speed to be attracted to a given point
        :param attraction_center: position on screen, center of attraction
        :return: None
        """

        # Calculate attraction direction using attractioin center and coin position
        self.attaction_center = attraction_center
        distance = get_distance(self.rect.center, self.attaction_center)
        x_difference = self.attaction_center[0] - self.rect.centerx
        y_difference = self.attaction_center[1] - self.rect.centery
        x_ratio = x_difference / distance
        y_ratio = y_difference / distance

        # Attraction speed is 1000 pixels/sec
        self.x_speed = 1000 * x_ratio
        self.y_speed = 1000 * y_ratio


def scatter_coins(enemy_sprite):
    """
    Generates several coin sprites at a given point and scatter them at random speed and random direction.
    The value of each coin will be randomly selected in a specific range, but total amount of coins will be constant.
    :param enemy_sprite: an enemy sprite that scatters coin
    :return: None
    """

    total_coins_amount = enemy_sprite.coin_amount

    # Value of each coin will be randomly selected in a specific range
    coin_amount_min = total_coins_amount // 20 + 1
    coin_amount_max = total_coins_amount // 10

    # Repeatedly generate Coin sprite until total amount of coins become 0
    current_coin_amount = random.randint(coin_amount_min, coin_amount_max)
    while total_coins_amount > current_coin_amount:
        Coin(enemy_sprite, current_coin_amount)
        total_coins_amount -= current_coin_amount
        current_coin_amount = random.randint(coin_amount_min, coin_amount_max)
    Coin(enemy_sprite, total_coins_amount)


# Generate field vibrator
field_vibrator = FieldVibrationController()

# Generate sprite groups
all_sprites = pygame.sprite.Group()             # Contains all sprites subject to update every frame
all_buttons = pygame.sprite.Group()             # All buttons to update and draw

# Generate additional sprite groups to specify drawing order
player_group = pygame.sprite.Group()            # Only player sprite will be added here
target_pointer_group = pygame.sprite.Group()    # Only target pointer will be added here
player_projectiles = pygame.sprite.Group()      # All projectiles shot from player

spawneffect_group = pygame.sprite.Group()       # Sprite group for all spawn effects
hiteffect_group = pygame.sprite.Group()         # Sprite group for all hit effects
explosion_group = pygame.sprite.Group()         # Sprite group for all explosions

all_enemies = pygame.sprite.Group()                 # Sprite group for all enemy sprites

hp_bar_group = pygame.sprite.Group()                # Sprite group for HPBar sprites
coin_group = pygame.sprite.Group()                  # Sprite group for Coin sprites
