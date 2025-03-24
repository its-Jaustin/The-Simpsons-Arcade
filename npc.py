import pygame
import player
import spritesheet

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

        
        
        self.z = 0 #player z position
        self.vel_x = 0
        self.vel_y = 0
        self.max_jump_height = 20

        #player state variables
        self.player_can_move = True
        self.on_ground = True
        self.attacking = False
        self.stunned = False
        self.facing = "r"

    def update(self):
        # handle user input
        self.horizontal_input = 0  # Reset horizontal input
        self.vertical_input = 0  # Reset vertical input
       
        
        #Updates goon movement based on input and physics.
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
        