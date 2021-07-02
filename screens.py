from all_sprites_and_groups import *


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

    def __init__(self, rect, text, text_font, text_font_size, color, default_back_color=(0, 0, 0)):
        Button.__init__(self, rect, text, text_font, text_font_size, color, default_back_color)

    def operate(self):
        main_menu.hide()
        play_screen.show()


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

        # Start button
        self.start_button = StartButton([800, 800, 320, 100], "START", "verdana", 60, (255, 255, 255))

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


class GamePlayScreen:
    """
    A screen class to display game play screen

    This displays main game progress. It updates and draws all sprites and background.
    """

    def __init__(self):
        # Background instance
        self.background = Background(background_grid_img, [screen_width, screen_height], camera_rect)

        # Player instance
        self.player = Player(camera_rect)

        # Boolean attribute whether display game play screen or not
        self.now_display = False

    def update(self, curspos, mouse_button_down):
        """
        Update background and all sprites on the screen during gameplay
        :return: None
        """

        # Actual cursor position on game field
        curspos_field = [curspos[0] + camera_rect.left, curspos[1] + camera_rect.top]

        # Update background position with respect to screen
        self.background.update()

        # Update all sprites
        all_sprites.update(FPS)
        self.player.aim(curspos_field)

        # Set camera position to player
        camera_rect.center = self.player.get_pos()

        # Generate enemy sprites
        if len(straight_line_mover1_group) < 120:
            StraightLineMover1(camera_rect)
        if len(straight_line_mover2_group) < 50:
            StraightLineMover2(camera_rect)
        if len(straight_line_mover3_group) < 20:
            StraightLineMover3(camera_rect)

    def draw(self, surface):
        """
        Draw background and all sprites on the screen during gameplay
        :return: None
        """

        # Draw background gridlines
        self.background.draw(surface)

        # Draw all sprites
        spawneffect_group.draw(surface)     # Draw all spawneffects
        player_group.draw(surface)          # Draw player
        all_enemies.draw(surface)           # Draw all enemies
        player_projectiles.draw(surface)    # Draw all projectiles shot from player
        hiteffect_group.draw(surface)       # Draw all hiteffects
        explosion_group.draw(surface)       # Draw all explosions
        hp_bars.draw(surface)               # Draw all HP bare of enemy sprites

        # Show game over screen if player dies
        if self.player.dead:
            self.hide()
            game_over_screen.show()
            self.initialize()

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

        # Regenerate player instance
        self.player = Player(camera_rect)


class RestartButton(Button):
    """
    A specific type of Button class which returns to the main menu screen
    """

    def __init__(self, rect, text, text_font, text_font_size, color, default_back_color=(0, 0, 0)):
        Button.__init__(self, rect, text, text_font, text_font_size, color, default_back_color)

    def operate(self):
        game_over_screen.hide()
        main_menu.show()


class GameOverScreen:
    def __init__(self):
        # Game over text
        self.gameover_text_font = pygame.font.SysFont("verdana", 80)
        self.gameover_text_surface = self.gameover_text_font.render("GAME OVER", True, (255, 255, 255))
        self.gameover_text_surface_rect = self.gameover_text_surface.get_rect(center=(960, 100))

        # Restart button
        self.restart_button = RestartButton([800, 800, 320, 100], "RESTART", "verdana", 60, (255, 255, 255))

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
