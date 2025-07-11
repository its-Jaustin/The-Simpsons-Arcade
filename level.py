import pygame
import json
import spritesheet
from pygame import Color
from npc import Goon
import random
from pygame import Color

TOP_OF_STREET = 163

class Stage1:
    def __init__(self):
        self.spritesheet = spritesheet.Spritesheet("Sprites\stage1-sprites.png", (86,177,222))

        self.street_image = self.spritesheet.parse_sprite('main-street.png')
        self.street_rect = pygame.Rect(0,0, self.street_image.get_width(), 256) 
        self.shops_image = self.spritesheet.parse_sprite('shops-and-bridge-0.png')
        self.shops_rect = pygame.Rect(0,0, self.shops_image.get_width(), 159) 
        self.npcs = []
        self.camera_x = 306  # Horizontal scrolling position
        self.can_scroll = False
        self.all_rects = [self.shops_rect, self.street_rect]
        self.num_zone = 0
        self.spawnzone = {
    0: {"completed": False, "visited": False, "x": 300, "num-goons-right": 3, "num-goons-left": 2},
    1: {"completed": False, "visited": False, "x": 600, "num-goons-right": 4, "num-goons-left": 1},
    2: {"completed": False, "visited": False, "x": 900, "num-goons-right": 2, "num-goons-left": 3},
    3: {"completed": False, "visited": False, "x": 1200, "num-goons-right": 5, "num-goons-left": 0},
    4: {"completed": False, "visited": False, "x": 1500, "num-goons-right": 1, "num-goons-left": 4},
    5: {"completed": False, "visited": False, "x": 1660, "num-goons-right": 0, "num-goons-left": 5},
}
        

    def update(self, player, screen):
        self.spawnzone[self.num_zone]
        """Move the level when the player moves and update NPCs."""
        self.can_scroll = player.rect.centerx >= screen.get_width() * .55 and self.camera_x < self.spawnzone[self.num_zone]['x']
        # Handle side-scrolling
        if self.can_scroll:
            scroll_speed = abs(player.vel_x) #scrolls with player
            self.camera_x += scroll_speed 

            for rect in self.all_rects:
                rect.x -= scroll_speed  # Shift level elements left

            # Move NPCs
            for npc in self.npcs:
                npc.rect.x -= scroll_speed  # Shift NPCs left
        if self.camera_x >= self.spawnzone[self.num_zone]['x'] and not self.spawnzone[self.num_zone]["visited"]:
            self.spawnzone[self.num_zone]["visited"] = True
            for n in range(self.spawnzone[self.num_zone]["num-goons-right"]):
                self.spawnGoon(screen.get_width(), screen.get_height(), 'r')
            for n in range(self.spawnzone[self.num_zone]["num-goons-left"]):
                self.spawnGoon(screen.get_width(), screen.get_height(), 'l')
        if not self.npcs and self.spawnzone[self.num_zone]["visited"]:
            self.spawnzone[self.num_zone]["completed"] = True
        if self.spawnzone[self.num_zone]["completed"] == True:
            self.num_zone += 1
        # Update NPCs
        self.npcs = [npc for npc in self.npcs if not npc.dead]
        
                

    def spawnGoon(self, w, h, dir='r'):
        self.spawnzone[self.num_zone]["num-goons-right"] -= 1
        npc = Goon()
        npc.z = h - int(random.random() * (h-TOP_OF_STREET))
        npc.rect.y = npc.z
        npc.rect.x = w + 20 if dir == 'r' else w - 20
        self.npcs.append(npc)

        

    def draw(self, screen):
        # Draw the street with an offset
        screen.blit(self.street_image, self.street_rect.topleft)

        # for npc in self.npcs:
        #     npc.draw()

        # Draw the shops with an offset
        screen.blit(self.shops_image, self.shops_rect.topleft)
        

    def draw_rects(self, screen):
        # Draw the hitboxes for debugging purposes
        for r in [self.shops_rect, self.street_rect]:
            pygame.draw.rect(screen, Color(0, 255, 0, a=100), r, 1)
