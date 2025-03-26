import pygame
import json

class Spritesheet:
    def __init__(self):
        self.goon
        
    def __init__(self, filename, transparent_color=(0, 0, 0)):
        self.filename = filename
        self.transparent_color = transparent_color
        self.sprite_sheet = pygame.image.load(filename).convert()
        self.meta_data = self.filename.replace('png', 'json')
        with open(self.meta_data) as f: 
            self.data = json.load(f)
        f.close()



    def get_sprite(self, x, y, w, h, visible):
        
        sprite = pygame.Surface((w, h))
        sprite.set_colorkey(self.transparent_color)
        if visible:
            sprite.blit(self.sprite_sheet,(0, 0),(x, y, w, h))
        return sprite

    def parse_sprite(self, name, visible=True):
        sprite = self.data['frames'][name]['frame']
        x, y, w, h = sprite["x"], sprite["y"], sprite["w"], sprite["h"]
        image = self.get_sprite(x, y, w, h, visible)
        return image






