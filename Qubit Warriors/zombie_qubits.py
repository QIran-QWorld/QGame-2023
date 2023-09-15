from game_classes import *
import pygame
import sys
import os
import cirq

# Initialize Pygame
pygame.init()

person_speed = 10

# zombie_speed = 2
white = (255, 255, 255)

# Create the game window
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Quantum Survival: Zombie Quantum Realm")

# Load Background Music
pygame.mixer.init()
pygame.mixer.music.load(os.path.join("sounds","bg-sound","4.mp3"))  # Replace with your music file
pygame.mixer.music.set_volume(background_sound_level)

# Play Background Music
pygame.mixer.music.play(-1)  #


GAME_PLAYING = 0
GAME_WIN = 1
GAME_LOSE = 2
GAME_RESTART = 3 

def display_end_scene(screen, game_state):
    # Clear the screen
    screen.fill((0, 0, 0))

    # Create a font for displaying messages
    font = pygame.font.Font(None, 72)

    if game_state == GAME_WIN:
        message = "You Win!"
    elif game_state == GAME_LOSE:
        message = "Game Over"

    # Render and display the message
    text = font.render(message, True, (255, 255, 255))
    text_rect = text.get_rect(center=(screen_width // 2, screen_height // 2))
    screen.blit(text, text_rect)

    # Create options for restarting and exiting the game
    restart_option = font.render("Press 'R' to Restart", True, (255, 255, 255))
    exit_option = font.render("Press 'Q' to Quit", True, (255, 255, 255))

    # Calculate the positions for options
    restart_rect = restart_option.get_rect(center=(screen_width // 2, screen_height // 2 + 100))
    exit_rect = exit_option.get_rect(center=(screen_width // 2, screen_height // 2 + 150))

    screen.blit(restart_option, restart_rect)
    screen.blit(exit_option, exit_rect)


bullets = pygame.sprite.Group()
person = Person()

zombies_group = pygame.sprite.Group()
for _ in range(initial_zombie_count):
    zombies_group.add(Zombie())
    
bullets = pygame.sprite.Group()  # Create a group for bullets
nav_bar = NavBar()  # Create an instance of the NavBar class

active_bullet_type = "X"  
# Game loop
clock = pygame.time.Clock()
game_over = False
game_state = GAME_PLAYING 
# Inside the while loop, update the zombie movement:
while not game_over:
    for event in pygame.event.get():
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if event.type == pygame.QUIT:
            game_over = True
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if remaining_ammo[active_bullet_type] > 0:
                    bullet = Bullet(person.rect.centerx+person.rect.width//4, person.rect.centery+person.rect.height//7, mouse_x, mouse_y, active_bullet_type)
                    bullets.add(bullet)
                    remaining_ammo[active_bullet_type] -= 1
                    sounds_ammo[active_bullet_type].play()
            elif event.button == 3:  # Right mouse button for changing bullet type
            # Change the active bullet type in a cyclic manner
                bullet_types = ["X","Z" ,"H", "M"]
                current_index = bullet_types.index(active_bullet_type)
                new_index = (current_index + 1) % len(bullet_types)
                active_bullet_type = bullet_types[new_index]
                person.set_bullet_type(active_bullet_type)
                nav_bar.active_bullet_index = new_index
                fire_sounds[0].play()

        # Handle number key presses to change the active bullet type
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_x:
                active_bullet_type = "X"
                nav_bar.active_bullet_index = 0
                person.set_bullet_type(active_bullet_type)
            elif event.key == pygame.K_z:
                active_bullet_type = "Z"
                nav_bar.active_bullet_index = 1
                person.set_bullet_type(active_bullet_type)
            elif event.key == pygame.K_h:
                active_bullet_type = "H"
                nav_bar.active_bullet_index = 1
                person.set_bullet_type(active_bullet_type)
            elif event.key == pygame.K_m:
                active_bullet_type = "M"
                nav_bar.active_bullet_index = 2
                person.set_bullet_type(active_bullet_type)  
            elif event.key == pygame.K_p:
                draw_vector=not draw_vector

    keys = pygame.key.get_pressed()
    if keys[pygame.K_a] and person.rect.left > 0:
        person.rect.x -= person_speed
    if keys[pygame.K_d] and person.rect.right < screen_width:
        person.rect.x += person_speed
    if keys[pygame.K_w] and person.rect.top > 0:
        person.rect.y -= person_speed
    if keys[pygame.K_s] and person.rect.bottom < screen_height:
        person.rect.y += person_speed
    
    # screen.fill(white)
    screen.blit(background_image, (0, 0)) 
    if person.is_visible():
        screen.blit(person.image, person.rect)
      # Draw the bullet type on the player's sprite
        person.draw_bullet_type(screen)
    person.update()

    for zombie in zombies_group:
        zombie.follow_person(person.rect)
        zombie.avoid_zombies(zombies_group.sprites())
    zombies_group.draw(screen)
    for zombie in zombies_group:
        zombie.draw(screen,draw_vector=draw_vector) 

    handle_collisions(bullets, zombies_group,person)

    bullets.update()
    bullets.draw(screen)

    nav_bar.draw(screen,person.lives)
        # Check for game over conditions
    if person.lives <1 :
        game_state = GAME_LOSE
    elif len(zombies_group) == 0:
        game_state = GAME_WIN

    # Display the appropriate end scene if the game is over
    if game_state == GAME_WIN or game_state == GAME_LOSE:
        display_end_scene(screen, game_state)
        
        # Check for the 'R' key press to restart the game
        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            # Reset game variables and restart the game
            game_state = GAME_RESTART
            person.lives = 3
            person.rect.x = 0
            zombies_group.empty()  # Clear all zombies
            for _ in range(initial_zombie_count):
                zombies_group.add(Zombie())
            # remaining_ammo = {"X": 10,"Z": 10, "H": 10, "M": 10}
            remaining_ammo["X"]=10
            remaining_ammo["Z"]=10
            remaining_ammo["H"]=10
            remaining_ammo["M"]=10
            active_bullet_type = "X"
            person = Person()
            nav_bar=NavBar()
        if keys[pygame.K_q]:
            game_over=True

    pygame.display.flip()
    clock.tick(60)

# Quit Pygame
pygame.quit()
sys.exit()