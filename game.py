import pygame
import sys
from os.path import join
from player import Homer 
import level as lvl
import tkinter as tk
from tkinter import ttk

# Initialize Pygame
pygame.init()

clock = pygame.time.Clock()


# Function to get user-selected scale factor
def get_scale_factor():
    root = tk.Tk()
    root.title("Select Resolution")

    scale_factor = tk.DoubleVar(value=2.5)

    def submit():
        root.quit()
        root.destroy()

    tk.Label(root, text="Select Resolution Scale :").pack(pady=20)
    
    # Dropdown menu with predefined scale factors
    options = [1.0, 1.5, 2.0, 2.5, 3.0]
    ttk.Combobox(root, textvariable=scale_factor, values=options, state="readonly").pack(pady=5)

    tk.Button(root, text="Start Game", command=submit).pack(pady=20)

    root.mainloop()
    return scale_factor.get()

# Get user-selected scale factor
#SCALE_FACTOR = get_scale_factor()
SCALE_FACTOR = 2.5
SCREEN_WIDTH, SCREEN_HEIGHT = 250, 250

screen = pygame.display.set_mode((SCREEN_WIDTH * SCALE_FACTOR, SCREEN_HEIGHT * SCALE_FACTOR),vsync=1)
pygame.display.set_caption("The Simpsons - Arcade")


# Create a smaller surface to render the game
game_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))


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
homer.z = SCREEN_HEIGHT  # Set initial z position for depth effect

level = lvl.Stage1()

health_bar = pygame.image.load("Sprites\\ui\\homer-health-bar-0.png").convert()
health_bar.set_colorkey((0,0,0))
health_bar_rect = pygame.Rect(0,5, health_bar.get_width(), health_bar.get_height())

# Game loop
running = True
lastTime = pygame.time.get_ticks()
accumulator = 0
counter = 0
deltaTime = 0
dev_view = False

while running:
    #Time changes
    counter += 1
    current = pygame.time.get_ticks()
    elapsedTime = current - lastTime
    lastTime = current
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
    
    if pygame.K_p in keyDowns:
        dev_view = not dev_view

 
    # Fill the screen with white
    game_surface.fill(WHITE)

    # Draw the FPS counter to the screen
    game_surface.blit(fps_text, text_rect)

    # Get the state of all keys
    keys = pygame.key.get_pressed()

    #Update state of goons
    for npc in level.npcs:
        npc.update(homer.rect.x, homer.z)

    # Update and Draw the player on the scxxxreen
    homer.update(keys, keyDowns, elapsedTime)

    #handle collisions
    if homer.rect.right >= SCREEN_WIDTH:
        homer.rect.right = SCREEN_WIDTH
    if homer.rect.left <= 0:
        homer.rect.left = 0
    if homer.rect.bottom >= SCREEN_HEIGHT:
        homer.rect.bottom = SCREEN_HEIGHT


    level.update(homer, game_surface)
    
    level.draw(game_surface)
    homer.draw(game_surface)
    z_sorted = [homer] + level.npcs
    def sort_z(x):
        return x.z
    z_sorted.sort(key=sort_z)
    for guy in z_sorted:
        guy.draw(game_surface)

    game_surface.blit(health_bar, health_bar_rect)

    if dev_view:
        level.draw_rects(game_surface)
        homer.draw_hitbox(game_surface)
        for npc in level.npcs:
            npc.draw_hitbox(game_surface)
    

    # Scale the game surface before rendering it to the actual screen
    scaled_surface = pygame.transform.scale(game_surface, (SCREEN_HEIGHT * SCALE_FACTOR, SCREEN_HEIGHT * SCALE_FACTOR))
    screen.blit(scaled_surface, (0, 0))

    # Update the display
    pygame.display.flip()

    pygame.time.wait(int(current + MS_PER_FRAME - pygame.time.get_ticks()))
    


# Quit Pygame
pygame.quit()
sys.exit()


