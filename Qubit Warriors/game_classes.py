import pygame
import os
import numpy as np
import random
import cirq
import math
import glob

# Constants
screen_width = 1920
screen_height = 1080
person_speed = 10
sound_vol_level=.5
initial_zombie_count = 6  
remaining_ammo = {
    "X": 10,
    "Z": 10,
    "H": 10,
    "M": 10
}


epsilon=.001

zombie_sound_level=.2*sound_vol_level
laser_sound_level=sound_vol_level
background_sound_level=.75*sound_vol_level
draw_vector=True


white = (255, 255, 255)


zombie_width=screen_width // 20





# ========================================== files  ==========================================================
background_image = pygame.transform.scale(pygame.image.load(os.path.join("images", "background","1.jpg")),(screen_width,screen_height))  

zombie_path = os.path.join("images", "characters","zombies")
# Use glob to find all PNG files in the directory
zombie_files = glob.glob(os.path.join(zombie_path, "*.png"))

zombie_path_sound = os.path.join("sounds", "zombie-hitted")
# Use glob to find all PNG files in the directory
zombie_sounds = glob.glob(os.path.join(zombie_path_sound, "*.mp3"))
pygame.mixer.init()
collision_sounds = [pygame.mixer.Sound(zombie_sounds[i]) for i in range(len(zombie_sounds))]
for sound in collision_sounds:
    sound.set_volume(zombie_sound_level)


fire_path_sound = os.path.join("sounds", "gate_sounds")
# Use glob to find all PNG files in the directory
fire_sound_files = glob.glob(os.path.join(fire_path_sound, "*.mp3"))
pygame.mixer.init()
fire_sounds = [pygame.mixer.Sound(fire_sound_files[i]) for i in range(len(fire_sound_files))]
for sound in collision_sounds:
    sound.set_volume(laser_sound_level)

sounds_ammo = {
    "X": fire_sounds[3],
    "Z": fire_sounds[4],
    "H": fire_sounds[1],
    "M": fire_sounds[2]
}

bg_sound_files=glob.glob(os.path.join(os.path.join("sounds", "bg-sound"), "*.mp3"))
bg_sounds= [pygame.mixer.Sound(bg_sound_files[i]) for i in range(len(bg_sound_files))]
# ====================================== Person Class =======================================================
heart_image=pygame.image.load(os.path.join("images", "characters","heart.png"))
class Person(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load(os.path.join("images", "characters", "h1.png"))
        original_width, original_height = self.image.get_size()
        new_width = screen_width // 20
        scaling_factor = new_width / original_width
        self.image = pygame.transform.scale(self.image, (int(new_width), int(original_height * scaling_factor)))
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = screen_height // 2 - self.rect.height // 2
        self.lives = 3  # Initialize the player's lives
        self.collision_cooldown = 0
        self.collision_cooldown_duration = 300  # 5 seconds cooldown (300 frames)
        self.blink_duration = 5  # Blink on/off duration (adjust as needed)
        self.is_blinking = False  # Flag to control blinking
        self.bullet_type = "X"
        self.font = pygame.font.Font(None, 36)



    def set_gun_position(self,screen):
        gun_image = pygame.image.load(os.path.join("images","weapon","laser_gun.png"))
        original_gun_width = gun_image.get_width()
        original_gun_height = gun_image.get_height()
        new_gun_width = .75 * self.rect.width  # Twice the width of the person image
        scaling_factor = new_gun_width / original_gun_width
        gun_image = pygame.transform.scale(gun_image, (int(new_gun_width), int(original_gun_height * scaling_factor)))
        self.gun_rect = gun_image.get_rect()
        # Set the gun's position one-third from the bottom of the person's image
        self.gun_rect.center = (self.rect.centerx + 10, self.rect.bottom - self.rect.height // 4)  # Adjust the position as needed
        
        screen.blit(gun_image, self.gun_rect)

    def set_bullet_type(self, bullet_type):
        self.bullet_type = bullet_type


    def draw_bullet_type(self, screen):
        text = self.font.render(self.bullet_type, True, (255, 0, 255))
        text_rect = text.get_rect()
        text_rect.centerx = self.rect.centerx
        text_rect.y = self.rect.y - 20
        screen.blit(text, text_rect)
        screen.blit(self.image, self.rect)
        self.set_gun_position(screen)  # New line: Set the gun's position based on character's hand
        # screen.blit(self.gun_image, self.gun_rect) 


    def decrease_lives(self):
        if self.collision_cooldown == 0:
            self.lives -= 1
            if self.lives < 0:
                self.lives = 0  # Ensure that lives do not go negative
            self.collision_cooldown = self.collision_cooldown_duration
            self.is_blinking = True  # Start blinking

    def is_visible(self):
        if self.collision_cooldown == 0:
            return True
        return self.collision_cooldown % (2 * self.blink_duration) < self.blink_duration

    def update(self):
        if self.collision_cooldown > 0:
            self.collision_cooldown -= 1

    def check_collision_with_zombies(self, zombies_group):
        # Check for collisions with zombies
        collisions = pygame.sprite.spritecollide(self, zombies_group, False)

        # If a collision occurs, start blinking and decrease lives
        if collisions:
            self.is_blinking = True  # Start blinking
            self.decrease_lives()
        
        return collisions
# ================================================ Zombie class =================================================
# Specify the directory path where you want to search for PNG files


class Zombie(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load(random.choice(zombie_files))
        original_width, original_height = self.image.get_size()
        scaling_factor = zombie_width / original_width
        self.image = pygame.transform.scale(self.image, (int(zombie_width), int(original_height * scaling_factor)))
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(self.rect.width, screen_width - self.rect.width)
        self.rect.y = random.randint(self.rect.height, screen_height - self.rect.height)


        self.q = cirq.LineQubit(0)
        self.circuit= cirq.Circuit()
        self.simulator = cirq.Simulator()

        self.quantum_state = self.init_quantum_state()
        self.measurement_result=None

        # Create a font object for rendering text
        self.font = pygame.font.Font(None, 36)  # You can customize the font size and style

        self.timer = 0  # Initialize the timer to 0
        self.delay = 300  # Set the delay in frames (60 frames per second * 5 seconds = 300 frames)

        self.stop_timer = 0  # Initialize the stop timer to 0
        self.stop_delay = 300  # Set the stop delay in frames (60 frames per second * 5 seconds = 300 frames)

                # Randomly choose a speed for the zombie within the specified range
        self.min_speed = .5
        self.max_speed = person_speed / 10
        self.zombie_speed = random.uniform(self.min_speed, self.max_speed)

    def init_quantum_state(self):
        if random.random() < 0.5:
            self.circuit.append(cirq.X(self.q))
            if random.random() < 0.5:
                self.circuit.append(cirq.H(self.q))
        elif random.random() < 0.5:
            self.circuit.append(cirq.H(self.q))
        return np.real(self.simulator.simulate(self.circuit).final_state_vector).round(3)


    def follow_person(self, person_rect):
            dx = person_rect.x - self.rect.x
            dy = person_rect.y - self.rect.y
            random_angle = random.uniform(0, 2 * math.pi)  
            length = max(1, pygame.math.Vector2(dx, dy).length())
            dx /= length
            dy /= length
            self.rect.x += dx * self.zombie_speed+math.cos(random_angle)
            self.rect.y += dy * self.zombie_speed+math.sin(random_angle)


    def avoid_zombies(self, all_zombies):
        for zombie in all_zombies:
            if zombie != self:
                if pygame.sprite.collide_rect(self, zombie):
                    # Calculate the vector from self to the other zombie
                    dx = zombie.rect.centerx - self.rect.centerx
                    dy = zombie.rect.centery - self.rect.centery
                    distance = max(1, pygame.math.Vector2(dx, dy).length())

                    # Calculate the overlap distance
                    overlap = (self.rect.width + self.rect.height) / 4 - distance
                    # Adjust the position to avoid overlap
                    if overlap > 0:
                        self.rect.x -= overlap * (dx / distance)
                        self.rect.y -= overlap * (dy / distance)

    def set_quantum_state(self):
        self.quantum_state = np.real(self.simulator.simulate(self.circuit).final_state_vector).round(3)


    def get_quantum_state(self):
        return self.quantum_state



    def plot_state(self,screen, a0,a1):
        angle = math.atan2(a1, -a0)
        base_x = self.rect.centerx
        base_y = self.rect.centery-2*self.rect.height//3
        arrow_length = self.rect.height//4
        arrow_width = 5

        tip_x = base_x + arrow_length * math.cos(angle)
        tip_y = base_y + arrow_length * math.sin(angle)

        left_x = tip_x + arrow_width * math.cos(angle + math.pi / 2)
        left_y = tip_y + arrow_width * math.sin(angle + math.pi / 2)

        right_x = tip_x + arrow_width * math.cos(angle - math.pi / 2)
        right_y = tip_y + arrow_width * math.sin(angle - math.pi / 2)

        color = (int(255*abs(a1)), int(255*abs(a0)), 0)
        # Draw the arrow
        pygame.draw.polygon(screen, color, [(base_x, base_y), (left_x, left_y), (right_x, right_y)])


    def draw(self, screen,draw_text=True,draw_vector=False):

        if self.measurement_result is not None:
            state_text = self.font.render(f"{self.measurement_result[0]}", True, (255, 0, 0))
        else:
            if len(self.get_quantum_state())>1:
                a0 = self.get_quantum_state()[0]
                a1 = self.get_quantum_state()[1]
            else:
                a0 =self.get_quantum_state()[0]
                a1 = 0
            # state_text = self.font.render(f"{a0:.3f}|0> + {a1:.3f}|1>", True, (0, 0, 0))
            if draw_vector:
                self.plot_state(screen,a0,a1)
                return
            if abs(a0)<epsilon:
                if a1<0:
                    text="-|1>"
                else:
                    text="|1>"
            elif  abs(a1)<epsilon:
                if a0<0:
                    text = "-|0>"
                else:
                    text = "|0>"
            else:
                if a1>0:
                    sgn="+"
                else:
                    sgn=""
                text = f"{a0:.2f}|0> {sgn} {a1:.2f}|1>"
            state_text = self.font.render(text, True, (int(abs(a1)*255), int(abs(a0)*255), 0))
            # self.plot_state(screen,a0,a1)
        # self.font.render(f"{self.quantum_state}", True, (255, 0, 0))
        text_rect = state_text.get_rect()
        text_rect.centerx = self.rect.centerx
        text_rect.y = self.rect.y - 20
        screen.blit(state_text, text_rect)


# ============================================== NavBar =============================================
class NavBar(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.bullet_types = ["X","Z","H", "M"]
        self.active_bullet_index = 0
        self.font = pygame.font.Font(None, 36)
        self.image = pygame.Surface((screen_width, 50))
        self.rect = self.image.get_rect()

    def draw(self, screen,lives):
        # Draw the navigation bar background
        pygame.draw.rect(screen, (0, 0, 0), (0, 0, screen_width, 50))

        for i, bullet_type in enumerate(self.bullet_types):
            if i == self.active_bullet_index:
                # Active gate is white
                color = (255, 255, 255)
            else:
                # Inactive gates are gray
                color = (150, 150, 150)

            # Create a text string with bullet type and remaining ammo
            text = f"{bullet_type} ({remaining_ammo[bullet_type]})"
            label = self.font.render(text, True, color)
            label_rect = label.get_rect()
            label_rect.x = 20 + i * 120
            label_rect.y = 10
            screen.blit(label, label_rect)

        heart_width = self.rect.height - 20  # Adjust the size as needed
        heart_height = self.rect.height - 20  # Adjust the size as needed

        heart_resized = pygame.transform.scale(heart_image, (heart_width, heart_height))

        heart_margin_x = 10  # Horizontal margin
        heart_margin_y = 10  # Vertical margin
        x_position = screen_width - heart_margin_x - (heart_width + heart_margin_x) * lives

        for _ in range(lives):
            screen.blit(heart_resized, (x_position, heart_margin_y))
            x_position += heart_width + heart_margin_x




# ===============================================  Bullet ===============================================
class Bullet(pygame.sprite.Sprite):
    def __init__(self, start_x, start_y, target_x, target_y, bullet_type):
        super().__init__()

        # Define a dictionary to map bullet types to their images
        bullet_images = {
            "X": "x_bullet.png",
            "Z": "z_bullet.png",  
            "H": "h_bullet.png",  
            "M": "m_bullet.png", 
        }
        # Load the image based on the bullet type
        self.image = pygame.transform.scale(pygame.image.load(os.path.join("images", "weapon", bullet_images[bullet_type])), (20, 20))
        self.rect = self.image.get_rect()
        self.rect.x = start_x
        self.rect.y = start_y
        self.speed = 2*person_speed
        self.target_x = target_x
        self.target_y = target_y
        self.bullet_type = bullet_type  # Store the bullet type

        self.lifespan = 200
    def update(self):
        # Move the bullet towards the target
        dx = self.target_x - self.rect.x
        dy = self.target_y - self.rect.y
        length = max(1, pygame.math.Vector2(dx, dy).length())
        dx /= length
        dy /= length
        self.rect.x += dx * self.speed
        self.rect.y += dy * self.speed
        if np.sqrt((self.rect.x-self.target_x)**2+(self.rect.y-self.target_y)**2) < .25*zombie_width:  # Adjust the threshold as needed
            self.kill()  


# ================================ handle colllisins ======================================

# Modify the handle_collisions function to take the Person instance as an argument
def handle_collisions(bullets, zombies, person):
    # Check for collisions between bullets and the zombies
    collisions = pygame.sprite.groupcollide(bullets, zombies, True, False)
    if collisions:
        for bullet, zombies_hit in collisions.items():
            for zombie_hit in zombies_hit:
                collision_sounds[random.randrange(len(collision_sounds))].play()
                if zombie_hit.measurement_result is None:
                    if bullet.bullet_type == "X":
                        zombie_hit.circuit.append(cirq.X(zombie_hit.q))
                        zombie_hit.set_quantum_state()
                    elif bullet.bullet_type == "Z":
                        zombie_hit.circuit.append(cirq.Z(zombie_hit.q))
                        zombie_hit.set_quantum_state()              
                    elif bullet.bullet_type == "H":
                        zombie_hit.circuit.append(cirq.H(zombie_hit.q))
                        zombie_hit.set_quantum_state()
                    elif bullet.bullet_type == "M":
                        zombie_hit.circuit.append(cirq.measure(zombie_hit.q, key='measurement'))
                        zombie_hit.measurement_result = zombie_hit.simulator.run(zombie_hit.circuit, repetitions=1).measurements['measurement'][0]
                        if (zombie_hit.measurement_result[0])<epsilon:
                            zombies.remove(zombie_hit)
                else:
                    if bullet.bullet_type == "X":
                        zombies.remove(zombie_hit)
    person_collisions = pygame.sprite.spritecollide(person, zombies, False)
    if person_collisions:
        for _ in person_collisions:
            person.decrease_lives()



