import pygame
import random

# Initialize pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Player movement settings
GRAVITY = 0.5
JUMP_STRENGTH = -8
MAX_JUMP_HOLD_TIME = 15  # Max frames the jump can be held
JUMP_HOLD_BOOST = -0.6  # Additional boost per frame jump is held
SPEED = 5
MID_AIR_ATTACK_SPEED = 7  # Speed applied during midair attacks
DOUBLE_JUMP_BOOST = -7  # Upward boost for double jump attack
ATTACK_FORCE_ANGLE = MID_AIR_ATTACK_SPEED / 1.414  # 45-degree force component (approx. sqrt(2)/2)

class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 50, 50)  # Rectangle for movement
        self.vel_x = 0
        self.vel_y = 0
        self.facing_right = True  # Track direction
        self.attacking = False  # True if midair attack is happening
        self.stunned = False  # True if hit and unable to move
        self.on_ground = False
        self.player_can_move = True  # Controls whether movement is allowed

        # Jump tracking variables
        self.jump_start_y = y  # Y position before jumping
        self.jump_hold_time = 0  # How long the jump button is held
        self.jumping = False  # Whether the player is currently jumping

    def handle_input(self):
        """Handles player movement and attacks, unless stunned."""
        keys = pygame.key.get_pressed()

        # Determine if player can move
        self.player_can_move = not (self.attacking or self.stunned)

        if self.player_can_move:
            self.vel_x = 0  # Reset x velocity

            # Left & right movement
            if keys[pygame.K_LEFT]:
                self.vel_x = -SPEED
                self.facing_right = False
            if keys[pygame.K_RIGHT]:
                self.vel_x = SPEED
                self.facing_right = True

            # Jumping (hold to jump higher)
            if keys[pygame.K_SPACE]:
                if self.on_ground:
                    self.jumping = True
                    self.jump_start_y = self.rect.y  # Store jump start height
                    self.vel_y = JUMP_STRENGTH
                    self.on_ground = False

                elif self.jumping and self.jump_hold_time < MAX_JUMP_HOLD_TIME:
                    self.vel_y += JUMP_HOLD_BOOST  # Extend jump height
                    self.jump_hold_time += 1  # Count frames jump is held

            else:
                self.jumping = False  # Reset jump hold when button is released
                self.jump_hold_time = 0

            # Midair Attack (based on height)
            if keys[pygame.K_x] and not self.on_ground:
                self.attacking = True
                if self.facing_right:
                    self.vel_x = MID_AIR_ATTACK_SPEED
                else:
                    self.vel_x = -MID_AIR_ATTACK_SPEED

                attack_threshold = self.jump_start_y - (MAX_JUMP_HOLD_TIME * abs(JUMP_HOLD_BOOST) / 2)

                if self.rect.y < attack_threshold:
                    self.vel_y -= ATTACK_FORCE_ANGLE  # Upward attack
                else:
                    self.vel_y += ATTACK_FORCE_ANGLE  # Downward attack

    def apply_gravity(self):
        """Applies gravity normally unless attacking downward (now always affected by gravity)."""
        self.vel_y += GRAVITY  

        if self.rect.bottom >= HEIGHT:  # Collision with ground
            self.rect.bottom = HEIGHT
            self.vel_y = 0
            self.on_ground = True
            self.attacking = False  # Reset attack state when landing
            self.stunned = False  # Player can move again after landing

    def update(self):
        """Updates player movement based on input and physics."""
        self.handle_input()
        self.rect.x += self.vel_x  # Apply horizontal movement
        self.rect.y += self.vel_y  # Apply vertical movement
        self.apply_gravity()

    def draw(self, screen):
        """Draws player as a rectangle (replace with sprite later)."""
        color = (255, 0, 0) if self.attacking else (0, 255, 0) if not self.stunned else (255, 255, 0)  # Red = attacking, Yellow = stunned
        pygame.draw.rect(screen, color, self.rect)  # Simple rectangle for testing

# Create player instance
player = Player(200, 500)

# Main game loop
running = True
while running:
    screen.fill((30, 30, 30))  # Background color

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    player.update()
    player.draw(screen)

    pygame.display.update()
    clock.tick(60)  # 60 FPS

pygame.quit()
