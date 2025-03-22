import pygame
import json
import spritesheet
import random
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
    "jump-falling": [0],
    "jump-up": [0],
    "respawn": [0, 1],
    "rolling": [0,1,2],
    "idle-standing": [0],
    "walking": [0,1,2,3,4,5,6,7],
    "walking-up": [0,1,2,3,4,5,6,7]
}
"""
Movement states:
-idle (standing still)
-walking (moving left/right)
-airborne
-jump attack
-injured (taking damage)
"""
GRAVITY = 0.5
H_SPEED = 5
V_SPEED = 2
JUMP_STRENGTH = -10
MAX_JUMP_HOLD_TIME = 15  # Max frames the jump can be held
JUMP_HOLD_BOOST = -0.5  # Additional boost per frame jump is held
MID_AIR_ATTACK_SPEED = 7  # Speed applied during midair attacks
ATTACK_FORCE_ANGLE = MID_AIR_ATTACK_SPEED / 1.414  # 45-degree force component (approx. sqrt(2)/2)

class Homer:
    def __init__(self):
        self.rect = pygame.Rect(100, 100, 50, 100)  # Placeholder for hitbox
        self.spritesheet = spritesheet.Spritesheet("Sprites\homer-sprites.png", (25,255,95))
        self.image = self.spritesheet.parse_sprite('idle-standing.png')
        self.show_hitbox = False  # For debugging hitbox visibility
        self.sprite_number = 0
        self.health = 100

        # Movement variables
        self.jump_key_pressed = False
        self.jump_key_held = False
        self.horizontal_input = 0 # Placeholder for horizontal input (left/right)
        self.vertical_input = 0 # vertical input (up/down) along the street
        self.z = 0, 0, 0
        self.vel_x = 0
        self.vel_y = 0
        self.player_can_move = True
        self.on_ground = True
        self.attacking = False
        self.stunned = False
        self.facing = "right"
        



    def update(self, keys, keyDowns):
        # handle user input
        self.horizontal_input = 0  # Reset horizontal input
        self.vertical_input = 0  # Reset vertical input
       
        if pygame.K_p in keyDowns and keyDowns[pygame.K_p]:
            self.show_hitbox = not self.show_hitbox
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
        self.jump_key_held = keys[pygame.K_c]
        if pygame.K_x in keyDowns:
            self.attacking = keyDowns[pygame.K_x]
        
        self.handle_movement()
        


        """Updates player movement based on input and physics."""
        
        self.rect.x += self.vel_x  # Apply horizontal movement
        self.rect.y += self.vel_y  # Apply vertical movement
        if self.on_ground:
            self.z = self.rect.bottom
        self.apply_gravity()
        self.handle_sprite()
        
    def apply_gravity(self):
        """Applies gravity normally unless attacking downward (now always affected by gravity)."""
        self.vel_y += GRAVITY  

        if self.rect.bottom >= self.z:  # Collision with ground
            self.rect.bottom = self.z
            self.vel_y = 0
            self.on_ground = True
            self.attacking = False  # Reset attack state when landing
            self.stunned = False  # Player can move again after landing
    def handle_movement(self):

        # Determine if player can move
        self.player_can_move = not (self.attacking or self.stunned)

        if self.player_can_move:

            ##left and right movement
            self.vel_x = self.horizontal_input * H_SPEED

            #up and down movement only if on ground
            if self.on_ground:
                self.vel_y = self.vertical_input * V_SPEED

            # Jumping (hold to jump higher)
            if self.jump_key_pressed:
                self.jump_key_pressed = False  # Reset jump key pressed state
                if self.on_ground:
                    self.jumping = True
                    self.jump_start_y = self.rect.y  # Store jump start height
                    self.vel_y = JUMP_STRENGTH
                    self.on_ground = False

                elif self.jump_key_held and self.jump_hold_time < MAX_JUMP_HOLD_TIME:
                    self.vel_y += JUMP_HOLD_BOOST  # Extend jump height
                    self.jump_hold_time += 1  # Count frames jump is held

            else:
                self.jumping = False  # Reset jump hold when button is released
                self.jump_hold_time = 0
            
            
    
    def handle_sprite(self):
        pass
    def draw(self, screen):
        # Draw the player on the given screen
        screen.blit(self.image, self.rect.midbottom)
    def draw_hitbox(self, screen):
        # Draw the hitbox for debugging purposes
        pygame.draw.rect(screen, (255, 0, 0), self.rect, 1)


