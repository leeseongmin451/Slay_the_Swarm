import pygame.draw

from levels_phases import *


class Button(pygame.sprite.Sprite):
    """
    A rectangular button class
    """

    def __init__(self, rect, text, text_font, text_font_size, color, default_back_color=(0, 0, 0)):
        """
        Initialize and apply basic settings to button
        :param rect: position and rectangular size of button
        :param text: text located at the center of button
        :param text_font: font of text
        :param text_font_size: font size of text in pixels
        :param color: color of button boundary and text
        :param default_back_color: color of background of button, default value is black(0, 0, 0)
        """

        pygame.sprite.Sprite.__init__(self)

        # Rect attribute
        self.rect = pygame.Rect(rect)

        # Text & font attribute
        self.text = text
        self.text_font = text_font
        self.text_font_size = text_font_size

        # Color attrubutes
        self.active_color = color
        self.font = pygame.font.SysFont(self.text_font, self.text_font_size)
        self.text_surface = self.font.render(self.text, True, self.active_color)
        self.text_surface_rect = self.text_surface.get_rect(center=self.rect.center)

        # Background color attributes
        # Default color is the darkest color
        self.default_back_color = default_back_color
        # Hovered color displayed when cursor is in rect has half brightness of active color
        self.hovered_back_color = ((self.active_color[0] + self.default_back_color[0]) // 2,
                                   (self.active_color[1] + self.default_back_color[1]) // 2,
                                   (self.active_color[2] + self.default_back_color[2]) // 2)
        # Clicked color displayed when the button is pressed has half brightness of hovered color
        self.clicked_back_color = ((self.hovered_back_color[0] + self.default_back_color[0]) // 2,
                                   (self.hovered_back_color[1] + self.default_back_color[1]) // 2,
                                   (self.hovered_back_color[2] + self.default_back_color[2]) // 2)
        # Set initial color of button
        self.current_color = self.active_color
        self.current_back_color = self.default_back_color
        self.inactive_color = self.hovered_back_color

        # Boolean values for button control
        self.active = True
        self.cursor_in_rect = False
        self.is_clicked = False

        # Add self to button group
        all_buttons.add(self)

    def activate(self):
        """
        Make button active(clickable)
        :return: None
        """

        self.current_color = self.active_color
        # Rerender text surface with newly set color
        self.text_surface = self.font.render(self.text, True, self.active_color)
        self.text_surface_rect = self.text_surface.get_rect(center=self.rect.center)
        self.active = True      # Update method will be executed

    def deactivate(self):
        """
        Make button inactive(not clickable)
        :return:
        """

        self.current_color = self.inactive_color
        # Rerender text surface with newly set color
        self.text_surface = self.font.render(self.text, True, self.active_color)
        self.text_surface_rect = self.text_surface.get_rect(center=self.rect.center)
        self.active = False     # Update method will be passed
        self.current_back_color = self.default_back_color

    def update(self, curspos, mouse_button_down):
        """
        Check whether cursor is in button or clicked the button when button is active(clickable).
        Only if click-and-release the button, operate() method will be executed.
        :param curspos: current cursor position on screen
        :param mouse_button_down: boolean value to check mouse button is pressed
        :return: None
        """

        # Check whether cursor is in button boundary and change background color
        if self.active and self.rect.collidepoint(curspos):
            self.cursor_in_rect = True
            self.current_back_color = self.hovered_back_color       # Change background status
        else:
            self.cursor_in_rect = False
            self.current_back_color = self.default_back_color       # Change background status

        # Check mouse click event when the cursor is in button
        if self.cursor_in_rect and mouse_button_down:
            self.is_clicked = True
            self.current_back_color = self.clicked_back_color       # Change background status
        # Check mouse release event when clicked
        if self.is_clicked and not mouse_button_down:
            self.operate()                                          # Operate the button
            self.is_clicked = False
            self.current_back_color = self.hovered_back_color       # Change background status

    def operate(self):
        """
        Button's specific function will be defined here.
        Child button classes will have specific functions by overriding this method
        :return: None
        """

        pass

    def draw(self, surface):
        """
        Draw button on screen
        :param surface: surface on which draw button
        :return: None
        """

        pygame.draw.rect(surface, self.current_back_color, self.rect)   # Draw background first
        pygame.draw.rect(surface, self.current_color, self.rect, 3)     # Draw boundary of button
        surface.blit(self.text_surface, self.text_surface_rect)         # Draw text in button


class StartButton(Button):
    """
    A specific type of Button class which starts the game
    """

    def __init__(self):
        Button.__init__(self, [800, 800, 320, 100], "START", "verdana", 60, (255, 255, 255))

    def operate(self):
        """
        Start game
        :return: None
        """

        # Hide main menu and show game play screen
        main_menu.hide()
        play_screen.show()

        # Hide mouse cursor
        pygame.mouse.set_visible(False)


class QuitButton(Button):
    """
    A specific type of Button class which quits the game
    """

    def __init__(self):
        Button.__init__(self, [820, 930, 280, 70], "QUIT GAME", "verdana", 40, (255, 255, 255))

        self.terminate_game = False

    def operate(self):
        self.terminate_game = True


def is_terminated():
    """
    Check termination of game. returns QuitButton class instance's attribute "terminate_game"
    :return: QuitButton class instance's attribute "terminate_game"
    """

    return main_menu.quit_button.terminate_game


class MainMenuScreen:
    """
    A screen class to display main menu screen before starting game

    MainMenuScreen has 3 parts:
     - Title text
     - Main image
     - Start button
    """

    def __init__(self):
        # Title text
        self.title_text_font = pygame.font.SysFont("verdana", 80)
        self.title_text_surface = self.title_text_font.render("SLAY THE SWARM", True, (255, 255, 255))
        self.title_text_surface_rect = self.title_text_surface.get_rect(center=(960, 100))

        # Main image
        self.main_image = pygame.image.load("img/icon/icon.png")
        self.main_image_rect = self.main_image.get_rect(center=(960, 540))

        # Start and quit button
        self.start_button = StartButton()
        self.quit_button = QuitButton()

        # Boolean attribute whether display main menu or not
        self.now_display = False

    def update(self, curspos, mouse_button_down):
        """
        Update all buttons in the screen
        :param curspos: current cursor position on screen
        :param mouse_button_down: boolean value to check mouse button is pressed
        :return: None
        """

        self.start_button.update(curspos, mouse_button_down)
        self.quit_button.update(curspos, mouse_button_down)

    def draw(self, surface):
        """
        Draw all things in the screen on a given surface
        :param surface: surface to draw on
        :return: None
        """

        surface.fill((0, 0, 0))
        surface.blit(self.title_text_surface, self.title_text_surface_rect)
        surface.blit(self.main_image, self.main_image_rect)
        self.start_button.draw(surface)
        self.quit_button.draw(surface)

    def show(self):
        """
        Show this screen
        :return: None
        """

        self.now_display = True

    def hide(self):
        """
        Hide this screen
        :return: None
        """

        self.now_display = False


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
        self.camera_offset = camera

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
            self.screen_w // 2 + (1.5 * self.part_width - self.camera_offset[0]) % (2 * self.part_width) - self.part_width
        self.part10_rect.centerx = self.part11_rect.centerx = \
            self.screen_w // 2 + (2.5 * self.part_width - self.camera_offset[0]) % (2 * self.part_width) - self.part_width

        self.part00_rect.centery = self.part10_rect.centery = \
            self.screen_h // 2 + (1.5 * self.part_height - self.camera_offset[1]) % (2 * self.part_height) - self.part_height
        self.part01_rect.centery = self.part11_rect.centery = \
            self.screen_h // 2 + (2.5 * self.part_height - self.camera_offset[1]) % (2 * self.part_height) - self.part_height

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


class BoundedBar:
    """
    Bar class with boundary that visualizes various kinds of measurements, progress, etc...
    """

    def __init__(self, rect: pygame.Rect, target_value, background_color, bar_color, boundary_color):
        self.rect = rect
        self.full_length = self.rect.w
        self.bar_rect = rect.copy()
        self.target_value = target_value
        self.background_color = background_color
        self.bar_color = bar_color
        self.boundary_color = boundary_color

    def update(self, current_value):
        """
        Update current length of bar
        :param current_value: to calculate current length of bar
        :return: None
        """

        self.bar_rect.w = round(self.full_length * current_value / self.target_value)

    def draw(self, surface):
        """
        Draw background, current length of bar, and boundary
        :param surface: surface to draw
        :return: None
        """

        pygame.draw.rect(surface, self.background_color, self.rect)
        pygame.draw.rect(surface, self.bar_color, self.bar_rect)
        pygame.draw.rect(surface, self.boundary_color, self.rect, 3)


class PlayerHPBar(BoundedBar):
    """
    A child class of BoundedBar to display HP of player
    """

    def __init__(self, target_value):
        BoundedBar.__init__(self, pygame.Rect([30, 30, 300, 20]), target_value, (0, 0, 0), (0, 255, 0), (255, 255, 255))


class PlayerMPBar(BoundedBar):
    """
    A child class of BoundedBar to display MP of player
    """

    def __init__(self, target_value):
        BoundedBar.__init__(self, pygame.Rect([30, 60, 300, 20]), target_value, (0, 0, 0), (0, 255, 255), (255, 255, 255))


class PlayerManualWeaponCoolTimeBar(BoundedBar):
    """
    A child class of BoundedBar to display remaining cooling time of manual weapon of player
    """

    def __init__(self, target_value):
        BoundedBar.__init__(self, pygame.Rect([30, 80, 300, 10]), target_value, (0, 0, 0), (255, 0, 0), (255, 255, 255))


class PhaseProgressBar(BoundedBar):
    """
    A child class of BoundedBar to display current phase progress
    """

    def __init__(self, target_value):
        BoundedBar.__init__(self, pygame.Rect([710, 40, 500, 30]), target_value, (0, 0, 0), (255, 255, 0), (255, 255, 255))


class GamePlayScreen:
    """
    A screen class to display game play screen

    This displays main game progress. It updates and draws all sprites and background.
    """

    def __init__(self):
        # Background instance
        self.background = Background(background_grid_img, [screen_width, screen_height], camera_offset)

        # Player & target pointer instance
        self.player = Player()
        self.target_pointer = TargetPointer()

        # Player HP, MP & manual weapon cooltime bar instances
        self.player_hp_bar = PlayerHPBar(self.player.full_hp)
        self.player_mp_bar = PlayerMPBar(self.player.full_mp)
        self.player_manual_weapon_cooltime_bar = PlayerManualWeaponCoolTimeBar(self.player.manual_weapon.max_cooltime_frame_count)

        # Boolean attribute whether display game play screen or not
        self.now_display = False

        self.boss = BossLV1()
        self.player.generate_boss_pointer(self.boss)

    def update(self, curspos, mouse_button_down):
        """
        Update background and all sprites on the screen during gameplay
        :return: None
        """

        # Update background position with respect to screen
        self.background.update()

        # Update all sprites
        all_sprites.update(curspos, mouse_button_down)
        self.player.aim(curspos)
        self.target_pointer.update(curspos)

        # Update field vibrating effect
        field_offset = field_vibrator.update()

        # Set camera position to player
        player_x_pos, player_y_pos = self.player.get_pos()
        camera_offset[0] = player_x_pos - screen_width // 2
        camera_offset[1] = player_y_pos - screen_height // 2 + field_offset     # Vibrate camera vertically

        # Generate enemy sprites
        if len(StraightLineMover1.group) < 200:
            StraightLineMover1()
        if len(StraightLineMover1.group) < 70:
            StraightLineMover2()
        if len(StraightLineMover1.group) < 30:
            StraightLineMover3()

        # Update player HP, MP & manual weapon cooltime bars
        self.player_hp_bar.update(self.player.hp)
        self.player_mp_bar.update(self.player.mp)
        self.player_manual_weapon_cooltime_bar.update(self.player.manual_weapon.remaining_cooltime_frames)

        # Show game over screen if player dies
        if self.player.dead:
            self.hide()
            game_over_screen.show()
            pygame.mouse.set_visible(True)      # Show mouse cursor
            self.initialize()

    def draw(self, surface):
        """
        Draw background and all sprites on the screen during gameplay
        :return: None
        """

        # Draw background gridlines
        self.background.draw(surface)

        # Draw all sprites
        coin_group.draw(surface)            # Draw all coins
        spawneffect_group.draw(surface)     # Draw all spawneffects
        player_group.draw(surface)          # Draw player
        all_enemies.draw(surface)           # Draw all enemies
        player_projectiles.draw(surface)    # Draw all projectiles shot from player
        hiteffect_group.draw(surface)       # Draw all hiteffects
        explosion_group.draw(surface)       # Draw all explosions
        hp_bar_group.draw(surface)          # Draw all HP bar of enemy sprites
        target_pointer_group.draw(surface)  # Draw target pointer

        # Draw player HP, MP & manual weapon cooltime bars
        self.player_hp_bar.draw(surface)
        self.player_mp_bar.draw(surface)
        self.player_manual_weapon_cooltime_bar.draw(surface)

    def show(self):
        """
        Show this screen
        :return: None
        """

        self.now_display = True

    def hide(self):
        """
        Hide this screen
        :return: None
        """

        self.now_display = False

    def initialize(self):
        """
        Remove all sprites from all groups except player
        :return: None
        """

        # Kill all sprites including player
        for sprite in all_sprites:
            sprite.kill()

        # Regenerate player & target pointer instance
        self.player = Player()
        self.target_pointer.kill()
        self.target_pointer = TargetPointer()


class MainMenuButton(Button):
    """
    A specific type of Button class which returns to the main menu screen
    """

    def __init__(self):
        Button.__init__(self, [760, 800, 400, 100], "MAIN MENU", "verdana", 60, (255, 255, 255))

    def operate(self):
        game_over_screen.hide()
        main_menu.show()


class GameOverScreen:
    def __init__(self):
        # Game over text
        self.gameover_text_font = pygame.font.SysFont("verdana", 80)
        self.gameover_text_surface = self.gameover_text_font.render("GAME OVER", True, (255, 255, 255))
        self.gameover_text_surface_rect = self.gameover_text_surface.get_rect(center=(960, 100))

        # Main image
        self.main_image = pygame.image.load("img/icon/gameover_icon.png")
        self.main_image_rect = self.main_image.get_rect(center=(960, 540))

        # Restart button
        self.restart_button = MainMenuButton()

        # Boolean attribute whether display game over screen or not
        self.now_display = False

    def update(self, curspos, mouse_button_down):
        """
        Update all buttons in the screen
        :param curspos: current cursor position on screen
        :param mouse_button_down: boolean value to check mouse button is pressed
        :return: None
        """

        self.restart_button.update(curspos, mouse_button_down)

    def draw(self, surface):
        """
        Draw all things in the screen on a given surface
        :param surface: surface to draw on
        :return: None
        """

        surface.fill((0, 0, 0))
        surface.blit(self.gameover_text_surface, self.gameover_text_surface_rect)
        surface.blit(self.main_image, self.main_image_rect)
        self.restart_button.draw(surface)

    def show(self):
        """
        Show this screen
        :return: None
        """

        self.now_display = True

    def hide(self):
        """
        Hide this screen
        :return: None
        """

        self.now_display = False


main_menu = MainMenuScreen()            # Main menu instance
play_screen = GamePlayScreen()          # Game play screen instance
game_over_screen = GameOverScreen()     # Game over screen instance
