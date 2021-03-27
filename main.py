import pygame
from dataclasses import dataclass
from math import pi, cos, sin, tan, sqrt
import sys

deg = 0.0174533

@dataclass
class Map:
    array = [
        [1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 1, 1, 1, 0, 0 ,1],
        [1, 0, 1, 1, 1, 1, 0, 1],
        [1, 0, 1, 1, 1, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1]
    ]
    width:int = len(array[0])
    height:int = len(array)
    size:int = 64

@dataclass
class Player:
    map_size:int
    map_array:'array'
    
    x:int = 200
    y:int = 200
    size:int = 20
    velocity:float = 2
    
    angle:float = 0
    rot_speed:float = 0.01
    l_size:int = 5
    
    fov:int = 6
    
    def update(self):
        if hasattr(self, 'rect') == False:
            self.calc_delta()
            self.rect = pygame.Rect(self.get_tl()[0], self.get_tl()[1], self.size, self.size)

        else:
            self.move(pygame.key.get_pressed())
            self.rect.topleft = self.get_tl()
    
    def move(self, keys):
        if keys[pygame.K_w] and keys[pygame.K_s] == False:
            self.x += self.deltax
            self.y += self.deltay
            
        elif keys[pygame.K_s] and keys[pygame.K_w] == False:
            self.x -= self.deltax
            self.y -= self.deltay
        self.calc_angle()
            
        if keys[pygame.K_a] and keys[pygame.K_d] == False:
            self.angle -= self.rot_speed
                
        elif keys[pygame.K_d] and keys[pygame.K_a] == False:
            self.angle += self.rot_speed
            
        self.calc_delta()
        
    def calc_angle(self):
        if self.angle > pi * 2:
            self.angle -= pi * 2
        elif self.angle < 0:
            self.angle += pi * 2
            
    def calc_delta(self):
        self.deltax = cos(self.angle) * 5
        self.deltay = sin(self.angle) * 5
        self.l_pos = (self.x + self.deltax * self.l_size,
                      (self.y + self.deltay * self.l_size) - 1)
                
    def get_tl(self):
        x = self.x - int(self.size / 2)
        y = self.y - int(self.size / 2)
        return (x, y)
    
@dataclass
class Settings:
    screen_res = None
    fps = 60
    background_color = (200, 200, 200)

class Game:
    def __init__(self):
        #logic stuff
        self.map = Map()
        self.player = Player(self.map.size, self.map.array)
        
        #pygame stuff
        self.settings = Settings()
        self.settings.screen_res = (self.map.width * self.map.size, self.map.height * self.map.size)
        
        self.run = True
        pygame.init()
        self.screen = pygame.display.set_mode(self.settings.screen_res)
        self.clock = pygame.time.Clock()
        self.pa_sur = pygame.Surface((self.map.width, self.map.height))
        self.pa = pygame.PixelArray(self.pa_sur)
        
    def render(self):  
        #Draw map
        for x in range(self.map.width):
            for y in range(self.map.height):
                if self.map.array[y][x] == 0:
                    self.pa[x,y] = pygame.Color(30, 30, 30)
                elif self.map.array[y][x] == 1:
                    self.pa[x,y] = pygame.Color(200, 200, 200)
                
        pygame.transform.scale(self.pa_sur, self.settings.screen_res, self.screen)
        
                #grid
        for i in range(self.map.width):
            pygame.draw.line(self.screen, (0,0,0), (0, i*self.map.size), (self.map.size * self.map.width, i*self.map.size))
        
        for i in range(self.map.width):
            pygame.draw.line(self.screen, (0,0,0), (i*self.map.size, 0), (i*self.map.size, self.map.size * self.map.width))
        
        #Draw Player
        pygame.draw.rect(self.screen, (100,100,100), self.player.rect)
        self.draw_rays(self.player.angle, self.player.fov)
        pygame.draw.line(self.screen, (200, 200, 200), (self.player.x, self.player.y - 1), self.player.l_pos, 3)
                
        #Regular stuff
        pygame.display.flip()
        
    def draw_rays(self, angle, n):
        angle -= (n/2) * deg
        for i in range(n):
            pygame.draw.line(self.screen, (200, 20, 60), (self.player.x, self.player.y), self.cast_ray(angle))
            angle += deg
        
    def closest_int(self, n, closest):
        return int((int(int(n)>>6)<<6) -0.001)
    
    def line_lenght(self, pos):
        spos = [self.player.x, self.player.y]
        return sqrt((spos[0] - pos[0])**2 + (spos[1] - pos[1])**2)
    
    def cast_ray(self, ray_angle):
        v = self.cast_vray(ray_angle, 3)
        h = self.cast_hray(ray_angle, 3)
        v_l = self.line_lenght(v)
        h_l = self.line_lenght(h)
        if v_l < h_l:
            return v
        if h_l < v_l:
            return h
    
    def cast_hray(self, ray_angle, checks = 8):
        tan_ = tan(ray_angle)
        if tan_ == 0:
            neg_tan = 0
        else:
            neg_tan = -1/tan(ray_angle)

        calc_off = [0, checks]
            
        if ray_angle > pi: #looking up
            ray_y = self.closest_int(self.player.y, self.map.size)
            ray_x = (self.player.y - ray_y) * neg_tan + self.player.x
            off_y = -self.map.size
            off_x = -off_y * neg_tan
            
        if ray_angle < pi: #looking down
            ray_y = self.closest_int(self.player.y, self.map.size) + 64
            ray_x = (self.player.y - ray_y) * neg_tan + self.player.x
            off_y = self.map.size
            off_x = -off_y * neg_tan
            
        if ray_angle == 0 or ray_angle == pi:
            ray_x = self.player.x
            ray_y = self.player.y
            calc_off[0] = calc_off[1]
            
        while calc_off[0] < calc_off[1]:
            #getting map positions
            map_x = int(ray_x / self.map.size)
            map_y = int(ray_y / self.map.size)
            
            if map_x < self.map.width and map_y < self.map.height and map_x > -1 and map_y > -1 and self.map.array[map_y][map_x] == 1:
                    #hit wall
                calc_off[0] = calc_off[1]

            else:
                ray_x += off_x
                ray_y += off_y
                calc_off[0] += 1
                
        return [ray_x, ray_y]
    
    def cast_vray(self, ray_angle, checks = 8):
        neg_tan = -tan(ray_angle)
        calc_off = [0, checks]
            
        if ray_angle > pi / 2 and ray_angle < pi + pi / 2: #looking left
            ray_x = self.closest_int(self.player.x, self.map.size)
            ray_y = (self.player.x - ray_x) * neg_tan + self.player.y
            
            off_x = -self.map.size
            off_y = -off_x * neg_tan
            
        if ray_angle > pi + pi / 2 or ray_angle < pi / 2: #looking right
            ray_x = self.closest_int(self.player.x, self.map.size) + 64
            ray_y = (self.player.x - ray_x) * neg_tan + self.player.y
            
            off_x = self.map.size
            off_y = -off_x * neg_tan
            
        if ray_angle == pi / 2 or ray_angle == pi + pi / 2:
            ray_x = self.player.x
            ray_y = self.player.y
            calc_off[0] = calc_off[1]
            
        while calc_off[0] < calc_off[1]:
            #getting map positions
            map_x = int(ray_x / self.map.size)
            map_y = int(ray_y / self.map.size)
            
            if map_x < self.map.width and map_y < self.map.height and map_x > -1 and map_y > -1 and self.map.array[map_y][map_x] == 1:
                    #hit wall
                calc_off[0] = calc_off[1]

            else:
                ray_x += off_x
                ray_y += off_y
                calc_off[0] += 1
                
        return [ray_x, ray_y]
        
    def main_loop(self):
        while self.run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                    
            self.player.update()
            print(self.player.angle)
            self.render()
            self.clock.tick(self.settings.fps)
            
game = Game()
game.main_loop()
