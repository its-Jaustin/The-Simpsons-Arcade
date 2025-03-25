import pygame
import player
import spritesheet
import random
from pygame import Color

GRAVITY = player.GRAVITY
H_SPEED = player.H_SPEED
V_SPEED = player.V_SPEED
JUMP_STRENGTH = player.JUMP_STRENGTH
CALCULATED_MAX_JUMP_HEIGHT = player.CALCULATED_MAX_JUMP_HEIGHT
MID_AIR_ATTACK_XSPEED = player.MID_AIR_ATTACK_XSPEED # Speed applied during midair attacks
MID_AIR_ATTACK_YSPEED = player.MID_AIR_ATTACK_YSPEED # 45-degree force component (approx. sqrt(2)/2)
STEP_FORWARD = player.STEP_FORWARD



class Goon:
    def __init__(self):
        self.spritesheet = spritesheet.Spritesheet("Sprites\goon-sprites.png", (255,0,219))
        self.sprite_name = 'idle.png'
        self.image = self.spritesheet.parse_sprite(self.sprite_name)
        self.rect = pygame.Rect(100, 100, self.image.get_width(),self.image.get_height())  # Placeholder for hitbox
        self.show_hitbox = False  # For debugging hitbox visibility
        self.hurt_box = None
        self.sprite_number = 0
        self.frames_elapsed = 0
        self.frame_buffer = 0
        self.elapsedTime = 0
        self.health = 100

        # Movement variables
        self.movement_state = 'idle'
        self.last_movement_state = None

        
        
        self.z = 0 #player z position
        self.vel_x = 0
        self.vel_y = 0
        self.max_jump_height = 20

        #player state variables
        self.npc_can_move = True
        self.on_ground = True
        self.attacking = False
        self.stunned = False
        self.facing = "r"

    def update(self, player_x, player_z):
        # handle user input
        self.horizontal_input = 0  # Reset horizontal input
        self.vertical_input = 0  # Reset vertical input
       
        
        #Updates goon movement based on input and physics.
        self.handle_movement(player_x, player_z)
        
        

        #apply movement
        
        r1 = 0 if random.random() < 0.4 else 1
        r2 = 0 if random.random() < 0.4 else 1
        self.rect.x += self.vel_x * r1 # Apply horizontal movement
        self.rect.y += self.vel_y  * r2 # Apply vertical movement
        if self.on_ground:
            self.z = self.rect.bottom
        else:
            self.vel_y += GRAVITY #apply gravity if in the air
            if self.rect.bottom >= self.z:  # Collision with ground
                self.rect.bottom = self.z
                self.vel_y = 0
                self.on_ground = True
                self.attacking = False  # Reset attack state when landing
                self.stunned = False  # Player can move again after landing
                self.movement_state = 'idle'

        #update sprite
        self.handle_sprite()
        

    def move_towards(self, target_x, target_z):
        """Moves the goon towards the player in both x and z directions."""
        dx = target_x - self.rect.x
        dz = target_z - self.z
        distance = (dx**2 + dz**2) ** 0.5  # Euclidean distance

        if distance > STEP_FORWARD:  
            # Normalize direction and move at a consistent speed
            if distance != 0:
                self.vel_x = (dx / distance) * (H_SPEED - 1)
                self.vel_y = (dz / distance) * (V_SPEED - 1) # Adjusting z-movement

    def find_movement_state(self):
        #update movement state (facing direction is updated in handle_movement)
        if self.on_ground:
            if not self.attacking:
                if self.vel_x == 0 and self.vel_y == 0:
                    if self.movement_state in ['idle', 'idle-facing-up', 'waving-fist']:
                        return self.movement_state
                    else:
                        return 'idle'
                    
                else:
                    if self.npc_can_move:
                        if self.vel_y < 0:
                            return 'walking-up'
                        elif self.vel_y > 0:
                            return 'walking-down'  
                        else:
                            return 'walking'
            else:
                if self.movement_state in ['attack1','attack2', 'attack3']:
                    return self.movement_state
                ms = 'attack1' if random.random() < .33333 else 'attack2'
                if ms.endswith('2'):
                    ms = 'attack2' if random.random() < 0.5 else 'attack3'
                return ms
        else:
            if self.stunned:
                return 'injury-midair'
            elif self.attacking:
                if self.movement_state.startswith('jump-attack'):
                    return self.movement_state
                    
            elif self.vel_y <= 0:
                return 'jumping'
            elif self.vel_y > 0:
                return 'falling'
        #raise ValueError('No state returned')
        return 'idle'
    
    def handle_movement(self, player_x, player_z):
        
        """Handles the goon's movement logic, moving closer to the player if needed."""
        if abs(player_x - self.rect.x) <= STEP_FORWARD and abs(player_z - self.z) <= STEP_FORWARD:
            self.movement_state = "attacking"
            self.vel_x = 0
            self.vel_y = 0
        else:
            self.movement_state = "moving"
            self.move_towards(player_x, player_z)

        # Apply movement limits
        self.rect.x += self.vel_x
        self.z += self.vel_y

    def handle_sprite(self):
        self.last_movement_state = self.movement_state
        self.movement_state = self.find_movement_state()

        if self.last_movement_state != self.movement_state:
            self.sprite_number = 0
            self.frames_elapsed = 0
            self.frame_buffer = 0
        
        self.frames_elapsed += 1
        if self.frame_buffer > 0:
            self.frame_buffer -= 1
            return
        
        last_sprite = self.sprite_name
        match self.movement_state:
            case 'idle':
                self.sprite_name = 'idle.png'
                self.hurt_box = None
                self.sprite_number += 1
                self.frame_buffer = 100 #time before an idle animiation
                if self.sprite_number > 1:
                    self.sprite_number = 0
            case 'idle-up':
                self.sprite_name = 'idle-faceing-up.png'
                self.hurt_box = None
                self.sprite_number += 1
                self.frame_buffer = 100 #time before an idle animiation
                if self.sprite_number > 1:
                    self.sprite_number = 0
                
            case 'walking':
                buffer = {0:5, 1:5, 2:5, 3:5, 4:5, 5:5, 6:5, 7:5}
                self.sprite_name = f'walking-{self.sprite_number}.png'
                self.frame_buffer = 5
                self.sprite_number += 1
                if self.sprite_number > 7:
                    self.sprite_number = 0
            case 'walking-up':
                buffer = {0:5, 1:5, 2:5, 3:5, 4:5, 5:5, 6:5, 7:5}
                self.sprite_name = f'walking-up-{self.sprite_number}.png'
                self.frame_buffer = 5
                self.sprite_number += 1
                if self.sprite_number > 7:
                    self.sprite_number = 0
            case 'walking-down':
                #buffer = {0:5, 1:5, 2:5, 3:5, 4:5, 5:5, 6:5, 7:5}
                self.sprite_name = f'walking-down-{self.sprite_number}.png'
                self.frame_buffer = 5
                self.sprite_number += 1
                if self.sprite_number > 7:
                    self.sprite_number = 0



        # Update the sprite image
        if self.sprite_name != last_sprite:
            self.elapsedTime = 0
            self.image = self.spritesheet.parse_sprite(self.sprite_name)

            # Get dimensions
            img_width, img_height = self.image.get_width(), self.image.get_height()
    
            #pivot at midbottom
            pivot = {"x":0.5,"y":1} 
    
            # Calculate new position based on pivot (x=0.5 means mid, y=1 means bottom)
            pivot_x = pivot["x"] * img_width
            pivot_y = pivot["y"] * img_height
    
            # Adjust rect based on the pivot
            self.rect = pygame.Rect(
                self.rect.x + (self.rect.width // 2) - pivot_x,
                self.rect.y + self.rect.height - pivot_y,
                img_width,
                img_height
            )
            if self.facing == "l":  
                self.image = pygame.transform.flip(self.image, True, False)

        
    def draw(self, screen):
        # Draw the player on the given screen
        screen.blit(self.image, self.rect)
    def draw_hitbox(self, screen):
        # Draw the hitbox for debugging purposes
        pygame.draw.rect(screen, Color(0, 0, 255, a=100), self.rect, 1)
        if self.hurt_box:
            pygame.draw.rect(screen, Color(255, 0, 0, a=100), self.hurt_box, 1)
