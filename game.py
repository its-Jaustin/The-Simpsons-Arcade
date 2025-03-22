import pygame
import sys
from os.path import join
from player import Homer 

# Initialize Pygame
pygame.init()

clock = pygame.time.Clock()


# Set up the display
SCREEN_WIDTH, SCREEN_HEIGHT = 600, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT),vsync=1)
pygame.display.set_caption("The Simpsons - Arcade")


#set up font
font = pygame.font.Font(None, 36)

# Define colors
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
BLACK = (0,0,0)
tBLUE = (0, 0, 255, 128)  # Transparent blue

# Define wanted frame rate
FPS = 60.0
MS_PER_FRAME = 1000.0 / FPS

# Render the FPS counter
fps_text = font.render(f"FPS: {0}", True, BLACK)
text_rect = fps_text.get_rect(topright=(SCREEN_WIDTH - 10, 10))

#initialize homer
homer = Homer()
homer.z = SCREEN_HEIGHT - 100  # Set initial z position for depth effect


# Game loop
running = True
lastTime = pygame.time.get_ticks()
accumulator = 0
counter = 0
deltaTime = 0

while running:
    #Time changes
    counter += 1
    current = pygame.time.get_ticks()
    elapsedTime = current - lastTime
    deltaTime = elapsedTime / 1000.0
    accumulator += elapsedTime
    if accumulator > 1000.0:
        accumulator -= 1000.0
        #print("FPS: ", counter)

        # Render the FPS counter
        fps_text = font.render(f"FPS: {counter}", True, BLACK)
        text_rect = fps_text.get_rect(topright=(SCREEN_WIDTH - 10, 10))
        counter = 0

    keyDowns = {}
    # Check for events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            keyDowns[event.key] = True
 
    # Fill the screen with white
    screen.fill(WHITE)

    # Draw the FPS counter to the screen
    screen.blit(fps_text, text_rect)

    # Get the state of all keys
    keys = pygame.key.get_pressed()

    # Update and Draw the player on the screen
    homer.update(keys, keyDowns)
    homer.draw(screen)


    # Update the display
    pygame.display.update()

    pygame.time.wait(int(current + MS_PER_FRAME - pygame.time.get_ticks()))
    lastTime = current


# Quit Pygame
pygame.quit()
sys.exit()