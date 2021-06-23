import pygame
from dataclasses import dataclass
from math import pi, cos, sin, tan, sqrt
from player import Player
from time import time
import sys

DEG = 0.0174533
    
@dataclass
class Settings:
    screen_res = None
    game_res = None
    first_person = False
    fps = 60
    background_color = (200, 200, 200)

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
        t = time()
        self.draw_rays(self.player.angle, self.player.rays, self.player.fov)
        t = time() - t
        self.draw_text(f'compute time: {t:.2f}secs', (10,40))
        pygame.draw.line(self.screen, (200, 200, 200), (self.player.x, self.player.y- 1 ), self.player.l_pos, 3)
        self.draw_text(f'fps: {self.clock.get_fps():.2f}', (10, 70))
        self.draw_text(f'mouse pos: {pygame.mouse.get_pos()}', (10, 100))
        
        #Regular stuff
        pygame.display.flip()
        
    def draw_text(self, text:str, pos:str):
        text_img = pygame.font.SysFont('Calibri', 40).render(text, True, (255,255,255))
        text_rect = text_img.get_rect()
        text_rect.topleft = tuple(pos) 
        self.screen.blit(text_img, text_rect)
        
    def draw_rays(self, angle, quantity:int, fov:float):
        self.draw_text(f'fov: {fov}', (10,10))
        
        fov = fov/quantity
        angle -= (quantity/2) * (DEG * fov)
        
        #check angle
        if angle > pi * 2:
            angle -= pi * 2
        if angle < 0:
            angle += pi * 2
            
        for i in range(quantity):
            ray = self.player.cast_ray(angle)
            
            #draw 2d
            pygame.draw.line(self.screen, (200, 20, 60), (self.player.x, self.player.y), (ray[0], ray[1]))
            
            #get now angle
            line_width = int((self.game_sur.get_width()) / quantity)
            line_x = (i * line_width) + self.game_sur.get_width()
            
            #get l height
            ca = self.player.angle - angle
            if ca > pi * 2:
                ca -= pi * 2
            if ca < 0:
                ca += pi * 2
            
            l_length = self.player.line_lenght(ray)
            l_length *= cos(ca)
                
            l_length = (self.player.map.size * self.game_sur.get_height())/l_length
            if l_length > self.game_sur.get_height():
                l_length = self.game_sur.get_height()
            
            #fix fisheye
            off_line = (self.game_sur.get_width() - l_length / 2) -200
            
            #draw pseudo 3d
            if ray[2] == 'v':
                pygame.draw.line(self.screen, ((185,40,40)), (line_x, l_length + off_line), (line_x, off_line), int(line_width))
            elif ray[2] == 'h':
                pygame.draw.line(self.screen, ((255,60,60)), (line_x, l_length + off_line), (line_x, off_line), int(line_width))
            
            #add and check angle
            angle += (DEG * fov)
            if angle > pi * 2:
                angle -= pi * 2
            if angle < 0:
                angle += pi * 2
        
    def main_loop(self):
        while True:
            mouse_move = None
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                #change map
                elif event.type == pygame.MOUSEBUTTONDOWN and not self.settings.first_person:
                    if event.pos[0] <= self.game_sur.get_width() and event.pos[0] >= 0:
                        if event.pos[1] <= self.game_sur.get_height() and event.pos[1] >= 0:
                            x = int(event.pos[0]/self.player.map.size)
                            y = int(event.pos[1]/self.player.map.size)
                            if self.player.map.array[y][x] == 1:
                                self.player.map.array[y][x] = 0
                            elif self.player.map.array[y][x] == 0:
                                self.player.map.array[y][x] = 1
                #get mouse relative pos 
                elif event.type == pygame.MOUSEMOTION:
                    mouse_move = event.rel
                #change camera mode
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_QUOTE:
                    if self.settings.first_person == False:
                        self.settings.first_person = True
                    else:
                        self.settings.first_person = False
                        pygame.event.set_grab(False)       
                        pygame.mouse.set_visible(True)
                        pygame.mouse.set_pos((int(self.screen.get_width()/2), int(self.screen.get_height()/2)))
                        
                #change lines rendering
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_1:
                    if self.player.lines == 'horizontal':
                        self.player.lines = 'vertical'
                    elif self.player.lines == 'vertical':
                        self.player.lines = 'both'
                    elif self.player.lines == 'both':
                        self.player.lines = 'horizontal'
            
            #camera mode
            if self.settings.first_person:
                pygame.event.set_grab(True)
                pygame.mouse.set_visible(False)
                
                if mouse_move:
                    self.player.angle += mouse_move[0]/ 50
                                
            self.player.update()
            self.render()
            self.clock.tick(self.settings.fps +  30)
            
game = Game()
game.main_loop()
