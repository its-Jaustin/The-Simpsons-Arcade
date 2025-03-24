import pygame
import json
import spritesheet
import random
from pygame import Color

"""
Movement states:
-idle (standing still)
-walking (moving left/right)
-airborne
-stunned
-jump attack
-injured (taking damage)
"""
GRAVITY = 0.5
H_SPEED = 2
V_SPEED = 2
JUMP_STRENGTH = 8
MAX_JUMP_HOLD_TIME = 20  # Max frames the jump can be held
JUMP_HOLD_BOOST = 0.3  # Additional boost per frame jump is held
CALCULATED_MAX_JUMP_HEIGHT = 143 ##CHANGE MANUALLY - calculate in apply_gravity() if you change the jump values
MID_AIR_ATTACK_XSPEED = 4  # Speed applied during midair attacks
MID_AIR_ATTACK_YSPEED = MID_AIR_ATTACK_XSPEED / 1.414  # 45-degree force component (approx. sqrt(2)/2)
STEP_FORWARD = 13

class Homer:
    def __init__(self):
        self.spritesheet = spritesheet.Spritesheet("Sprites\homer-sprites.png", (25,255,95))
        self.sprite_name = 'idle-standing.png'
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
        self.jump_key_pressed = False
        self.jump_key_held = False
        self.jump_hold_time = 0  # Time the jump key is held
        self.attack_key_pressed = False
        self.horizontal_input = 0 # Placeholder for horizontal input (left/right)
        self.vertical_input = 0 # vertical input (up/down) along the street
        self.z = 0 #player z position
        self.vel_x = 0
        self.vel_y = 0
        self.player_can_move = True
        self.on_ground = True
        self.attacking = False
        self.stunned = False
        self.facing = "r"
        self.max_jump_height = 20
        



    def update(self, keys, keyDowns, elapsedTime):
        # handle user input
        self.horizontal_input = 0  # Reset horizontal input
        self.vertical_input = 0  # Reset vertical input
       
        
        if keys[pygame.K_RIGHT]:
            self.horizontal_input += 1
        if keys[pygame.K_LEFT]:
            self.horizontal_input -= 1
        if keys[pygame.K_UP]:
            self.vertical_input -= 1
        if keys[pygame.K_DOWN]:
            self.vertical_input += 1

        # Handle jump key press
        if pygame.K_c in keyDowns:
            self.jump_key_pressed = keyDowns[pygame.K_c]
        if keys[pygame.K_c]:
            self.jump_key_held = True
            self.jump_hold_time += 1
        else:
            self.jump_key_held = False
            self.jump_hold_time = 0

        self.attack_key_pressed = pygame.K_x in keyDowns
             

        
        #Updates player movement based on input and physics.
        self.handle_movement()
        
        #apply movement
        self.rect.x += self.vel_x  # Apply horizontal movement
        self.rect.y += self.vel_y  # Apply vertical movement
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
        self.handle_sprite(elapsedTime)
        
        
    
             

    def print_max_heights(self):
        ######## use this to calculate max jump height if you change the jump values ######### 
        jump_height = abs(self.rect.bottom - self.z)
        if  jump_height > self.max_jump_height:
            self.max_jump_height = jump_height
            print(f"New max jump height: {self.max_jump_height}")
        
        


    def handle_movement(self):

        # Determine if player can move
        self.player_can_move = not (self.attacking or self.stunned)


        if self.player_can_move:
            
            if self.horizontal_input > 0 and self.facing == "l":
                self.facing = 'r'
                self.image = pygame.transform.flip(self.image, True, False)
            elif self.horizontal_input < 0 and self.facing == "r":
                self.facing = 'l'
                self.image = pygame.transform.flip(self.image, True, False)

            ##left and right movement
            self.vel_x = self.horizontal_input * H_SPEED

            
            if self.on_ground:
                #up and down movement only if on ground
                self.vel_y = self.vertical_input * V_SPEED
            #check for landing on the ground
            elif self.rect.bottom >= self.z:  # Collision with ground
                self.rect.bottom = self.z
                self.vel_y = 0
                self.on_ground = True
                self.attacking = False  # Reset attack state when landing
                self.stunned = False  # Player can move again after landing
                self.movement_state = 'idle'

            # Jumping (hold to jump higher)
            if self.jump_key_pressed:
                self.jump_key_pressed = False  # Reset jump key pressed state
                if self.on_ground:
                    self.jump_start_y = self.rect.y  # Store jump start height
                    self.vel_y = -JUMP_STRENGTH
                    self.on_ground = False
            elif self.jump_key_held and self.jump_hold_time < MAX_JUMP_HOLD_TIME:
                self.vel_y -= JUMP_HOLD_BOOST  # Extend jump height

            # Attack
            if self.attack_key_pressed:
                self.attack_key_pressed = False
                self.attacking = True

                #Midair Attack
                if not self.on_ground:
                    self.vel_x = H_SPEED if self.facing == "r" else -H_SPEED

                    attack_threshold = self.jump_start_y - (CALCULATED_MAX_JUMP_HEIGHT * .65)
                    if self.rect.y < attack_threshold:
                        self.vel_y = MID_AIR_ATTACK_YSPEED #downward attack
                        if self.facing == 'r':
                            self.vel_x += 1
                        else: 
                            self.vel_x -= 1
                        self.movement_state = 'jump-attack1-0'
                    else:
                        self.vel_y = -MID_AIR_ATTACK_YSPEED - 2 #upward attack
                        self.movement_state = 'jump-attack1' if random.random() < 0.5 else 'jump-attack2'
                #GROUNDED ATTACK
                else:
                    self.vel_y = 0
                    self.vel_x = 0
                    self.rect.x += STEP_FORWARD if self.facing == 'r' else -STEP_FORWARD #jump forward a tiny bit and jump back after animation
        #handle stun animation movement                
        elif self.stunned:
            self.attacking = False
            
        elif self.attacking and not self.on_ground:
            self.vel_y -= .2  # Extend air time
            if self.rect.bottom >= self.z:  # Collision with ground
                self.rect.bottom = self.z
                self.vel_y = 0
                self.on_ground = True
                self.attacking = False  # Reset attack state when landing
                self.stunned = False  # Player can move again after landing
                self.movement_state = 'idle'
        if self.on_ground and self.attacking:
            #if its not a grounded attack
            if not self.movement_state.startswith('attack'):
                self.vel_x = 0  # Reset horizontal movement
                self.vel_y = 0
        if not self.attacking:
            self.hurt_box = None
            

    def find_movement_state(self):
        #update movement state (facing direction is updated in handle_movement)
        last_state = self.movement_state
        if self.on_ground:
            if not self.attacking:
                if self.vel_x == 0 and self.vel_y == 0:
                    if self.movement_state in ['idle', 'idle-flex', 'idle-yawn']:
                        return self.movement_state
                    else:
                        return 'idle'
                    
                else:
                    if self.player_can_move:
                        if self.vel_y < 0:
                            return 'walking-up'
                        else:
                            return 'walking'  
            else:
                if self.movement_state in ['attack1','attack2']:
                    return self.movement_state
                ms = 'attack1' if random.random() < .5 else 'attack2'
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
        

            
            
    
    def handle_sprite(self, elapsedTime):
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
                self.sprite_name = 'idle-standing.png'
                self.hurt_box = None
                self.sprite_number += 1
                self.frame_buffer = 100 #time before an idle animiation
                if self.sprite_number > 1:
                    self.sprite_number = 0
                    self.movement_state = 'idle-yawn' if random.random() < 0.5 else 'idle-flex'
            case 'idle-flex':
                if self.sprite_number <= 1:
                    buffer = {1:20, 2:30}
                    self.sprite_name = f'idle-flex-{self.sprite_number+1}.png'
                    self.frame_buffer = buffer[self.sprite_number+1]
                    self.sprite_number += 1
                else:
                    self.sprite_number = 0
                    self.movement_state = 'idle'
            case 'idle-yawn':
                if self.sprite_number <= 2:
                    buffer = {0:20, 1:20, 2:20}
                    self.sprite_name = f'idle-yawn-{self.sprite_number}.png'
                    self.frame_buffer = buffer[self.sprite_number]
                    self.sprite_number += 1
                else:
                    self.sprite_number = 0
                    self.movement_state = 'idle'
                
                
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
            case 'jumping':
                self.sprite_name = 'jump-up.png'
            case 'falling':
                self.sprite_name = 'jump-falling.png'
            case 'jump-attack1-0':
                buffer = {0:6, 1:5}
                self.sprite_name = f'jump-attack1-{self.sprite_number}.png'
                self.frame_buffer = buffer[self.sprite_number]
                self.sprite_number += 1
                if self.sprite_number > 1:
                    self.sprite_number = 1
                hurtbox_width = self.rect.width - 10  # Slightly smaller than the player's rect
                hurtbox_height = self.rect.height - 40
            
                self.hurt_box = pygame.Rect(self.rect.x, self.rect.y, hurtbox_width, hurtbox_height)
                if self.facing == 'l':
                    self.hurt_box.left = self.rect.left
                else:
                    self.hurt_box.right = self.rect.right
                self.hurt_box.bottom = self.rect.bottom
            case 'jump-attack1':
                buffer = {0:10, 1:5}
                self.sprite_name = f'jump-attack1-{self.sprite_number}.png'
                self.frame_buffer = buffer[self.sprite_number]
                self.sprite_number += 1
                if self.sprite_number > 1:
                    self.sprite_number = 1
                hurtbox_width = self.rect.width - 10  # Slightly smaller than the player's rect
                hurtbox_height = self.rect.height - 40
            
                self.hurt_box = pygame.Rect(self.rect.x, self.rect.y, hurtbox_width, hurtbox_height)
                if self.facing == 'l':
                    self.hurt_box.left = self.rect.left
                else:
                    self.hurt_box.right = self.rect.right
                self.hurt_box.bottom = self.rect.bottom
            case 'jump-attack2':
                buffer = {0:10, 1:5}
                self.sprite_name = f'jump-attack2-{self.sprite_number}.png'
                self.frame_buffer = buffer[self.sprite_number]
                self.sprite_number += 1
                if self.sprite_number > 1:
                    self.sprite_number = 1
                hurtbox_width = self.rect.width - 10  # Slightly smaller than the player's rect
                hurtbox_height = self.rect.height - 40
            
                self.hurt_box = pygame.Rect(self.rect.x, self.rect.y, hurtbox_width, hurtbox_height)
                if self.facing == 'l':
                    self.hurt_box.left = self.rect.left
                else:
                    self.hurt_box.right = self.rect.right
                self.hurt_box.bottom = self.rect.bottom

            case 'attack1':
                if self.sprite_number <=3:
                    buffer = {0: 4, 1: 4, 2: 3, 3: 3} #total 14
                    self.sprite_name = f'attack1-{self.sprite_number}.png'
                    self.frame_buffer = buffer[self.sprite_number]
                        
                    self.sprite_number += 1
                    # Define the hurtbox for specific frames
                    if self.sprite_number in [2, 3]:
                        hurtbox_width = self.rect.width - 20  # Slightly smaller than the player's rect
                        hurtbox_height = self.rect.height - 30
                    
                        self.hurt_box = pygame.Rect(self.rect.x, self.rect.y+5, hurtbox_width, hurtbox_height)
                        if self.facing == 'l':
                            self.hurt_box.left = self.rect.left - 5
                        else:
                            self.hurt_box.right = self.rect.right + 5
                else:
                    self.rect.x -= (STEP_FORWARD-4) if self.facing == 'r' else -(STEP_FORWARD+4) 
                    self.hurt_box = None  # Disable the hurtbox after the attack animation
                    self.sprite_number = 0
                    self.movement_state = 'idle'
                    self.attacking = False
            case 'attack2':
                if self.sprite_number <=7:
                    #buffer = {0: 4, 1: 4, 2: 3, 3: 2}
                    self.sprite_name = f'attack2-{self.sprite_number}.png'
                    self.frame_buffer = 2
                        
                    self.sprite_number += 1
                    # Define the hurtbox for specific frames
                    if self.sprite_number in range(3,8):
                        hurtbox_width = self.rect.width - 20  # Slightly smaller than the player's rect
                        hurtbox_height = self.rect.height - 30
                    
                        self.hurt_box = pygame.Rect(self.rect.x, self.rect.y+5, hurtbox_width, hurtbox_height)
                        if self.facing == 'l':
                            self.hurt_box.left = self.rect.left - 5
                        else:
                            self.hurt_box.right = self.rect.right + 5
                else:
                    self.rect.x -= (STEP_FORWARD-2) if self.facing == 'r' else -(STEP_FORWARD+2) 
                    self.hurt_box = None  # Disable the hurtbox after the attack animation
                    self.sprite_number = 0
                    self.movement_state = 'idle'
                    self.attacking = False







        
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

sequence = {
    "attack1": [0, 1, 2, 3],
    "attack2": [0, 1, 2, 3, 4, 5, 6, 7],
    "death": [0, 1, 2],
    "fall-back": [0, 1, 2, 3],
    "fall-forward": [0, 1, 2, 3],
    "get-up-back": [0, 1, 2, 3],
    "get-up-front": [0, 1, 2, 3],
    "idle-flex": [0, 1],
    "idle-yawn": [0, 1, 2],
    "injury-behind": [0, 1], 
    "injury-front": [0,1],
    "injury-midair": [0, 1, 2],
    "injury-screen": [0, 1, 2, 3],
    "jump-attack1": [0,1],
    "jump-attack2": [0,1],
    "respawn": [0, 1],
    "rolling": [0,1,2]
}