from screens import *


# Generate player instance and add to sprite group
player = Player(camera_rect)
player.set_pos([field_width // 4, field_height // 4])

main_menu.show()

# Main game loop
running = True              # Variable to check whether continue game
mouse_button_down = False   # Variable to check mouse button click event
while running:

    # Get all events occurred during the game
    for event in pygame.event.get():
        # Check whether quit button clicked
        if event.type == pygame.QUIT:
            running = False
        # Check mouse button click event
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_button_down = True
        if event.type == pygame.MOUSEBUTTONUP:
            mouse_button_down = False

    # Get cursor position on the screen
    curspos_screen = pygame.mouse.get_pos()        # Position displayed on screen

    # Update and draw main menu screen
    if main_menu.now_display:
        main_menu.update(curspos_screen, mouse_button_down)
        main_menu.draw(screen)

    # Update and draw game play screen
    if play_screen.now_display:
        play_screen.update(curspos_screen, mouse_button_down)
        play_screen.draw(screen)

    # Update and draw game over screen
    if game_over_screen.now_display:
        game_over_screen.update(curspos_screen, mouse_button_down)
        game_over_screen.draw(screen)

    pygame.display.update()     # update all display changes and show them
    fps_clock.tick(FPS)         # make program never run at more than "FPS" frames per second
