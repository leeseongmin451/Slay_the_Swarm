from all_sprites_and_groups import *


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


# Define entire field size and initial camera position
field_width = field_height = 5000
camera_rect = pygame.Rect(field_width // 4 - screen_width // 2, field_height // 4 - screen_height // 2, screen_width, screen_height)

# Define background
background = Background(background_grid_img, [screen_width, screen_height], camera_rect)

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
