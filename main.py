import pygame
from dataclasses import dataclass
from math import pi, cos, sin, tan, sqrt
from player import Player
import sys

DEG = 0.0174533
    
@dataclass
class Settings:
    screen_res = None
    game_res = None
    fps = 60
    background_color = (200, 200, 200)
    
@dataclass
class Colors:
    pygame.Color((20,20,20))

class Game:
    def __init__(self):
        #logic stuff
        self.player = Player()
        
        #pygame stuff
        self.settings = Settings()
        self.settings.screen_res = [(self.player.map.width * self.player.map.size) * 2, self.player.map.height * self.player.map.size]
        
        self.settings.game_res = [self.player.map.width * self.player.map.size, self.player.map.height * self.player.map.size]
        self.game_sur = pygame.Surface(self.settings.game_res)
        
        self.screen = pygame.display.set_mode(self.settings.screen_res)
        self.clock = pygame.time.Clock()
        
        self.pa_sur = pygame.Surface((self.player.map.width, self.player.map.height))
        self.pa = pygame.PixelArray(self.pa_sur)
        pygame.init()
        
    def render(self):
        self.screen.fill((10,10,10))
        #Draw map
        for x in range(self.player.map.width):
            for y in range(self.player.map.height):
                if self.player.map.array[y][x] == 0:
                    self.pa[x,y] = pygame.Color(30, 30, 30)
                elif self.player.map.array[y][x] == 1:
                    self.pa[x,y] = pygame.Color(200, 200, 200)
        
        pygame.transform.scale(self.pa_sur, self.settings.game_res, self.game_sur)
        self.screen.blit(self.game_sur, (0,0))
        
        #grid
        for i in range(self.player.map.width):
            pygame.draw.line(self.screen, (0,0,0), (0, i*self.player.map.size), (self.player.map.size * self.player.map.width, i*self.player.map.size))
        
        for i in range(self.player.map.height):
            pygame.draw.line(self.screen, (0,0,0), (i*self.player.map.size, 0), (i*self.player.map.size, self.player.map.size * self.player.map.width))
        
        #Draw Player
        pygame.draw.rect(self.screen, (100,100,100), self.player.rect)
        self.draw_rays(self.player.angle, self.player.fov)
        pygame.draw.line(self.screen, (200, 200, 200), (self.player.x, self.player.y- 1 ), self.player.l_pos, 3)
                
        #Regular stuff
        pygame.display.flip()
        
    def draw_rays(self, angle, quantity:int, frequency = 1):
        angle -= (quantity/2) * (DEG * frequency)
        
        if angle > pi * 2:
            angle -= pi * 2
        if angle < 0:
            angle += pi * 2
            
        for i in range(quantity):
            pygame.draw.line(self.screen, (200, 20, 60), (self.player.x, self.player.y), self.player.cast_ray(angle))
            angle += (DEG * frequency)
            if angle > pi * 2:
                angle -= pi * 2
            if angle < 0:
                angle += pi * 2
        
    def main_loop(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                    
            self.player.update()
            self.render()
            self.clock.tick(self.settings.fps)
            
game = Game()
game.main_loop()
