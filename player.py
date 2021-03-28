from dataclasses import dataclass
import pygame
from math import pi, cos, sin, tan, sqrt

@dataclass
class Map:
    array = [
        [1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 1, 1, 1, 0, 0 ,1],
        [1, 0, 0, 0, 0, 1, 0, 1],
        [1, 0, 1, 1, 1, 0, 0, 1],
        [1, 0, 1, 0, 1, 0, 0, 1],
        [1, 0, 1, 1, 1, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1]
    ]
    width:int = len(array[0])
    height:int = len(array)
    size:int = 64

@dataclass
class Player:
    x:int = 200
    y:int = 200
    size:int = 20
    velocity:float = 2
    
    angle:float = 0
    rot_speed:float = 0.1
    l_size:int = 5
    
    fov:int = 180
    map:Map = Map()
    
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
        
    def closest_int(self, n, closest):
        return int((int(int(n)>>6)<<6) -0.001)
    
    def line_lenght(self, pos):
        spos = [self.x, self.y]
        return sqrt((spos[0] - pos[0])**2 + (spos[1] - pos[1])**2)
    
    def cast_ray(self, ray_angle):
        v = self.cast_vray(ray_angle)
        h = self.cast_hray(ray_angle)
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
            ray_y = self.closest_int(self.y, self.map.size)
            ray_x = (self.y - ray_y) * neg_tan + self.x
            off_y = -self.map.size
            off_x = -off_y * neg_tan
            
        if ray_angle < pi: #looking down
            ray_y = self.closest_int(self.y, self.map.size) + 65
            ray_x = (self.y - ray_y) * neg_tan + self.x
            off_y = self.map.size
            off_x = -off_y * neg_tan
            
        if ray_angle == 0 or ray_angle == pi:
            ray_x = self.x
            ray_y = self.y
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
            ray_x = self.closest_int(self.x, self.map.size)
            ray_y = ((self.x - ray_x) * neg_tan + self.y)
            
            off_x = -self.map.size
            off_y = -off_x * neg_tan
            
        if ray_angle > pi + pi / 2 or ray_angle < pi / 2: #looking right
            ray_x = self.closest_int(self.x, self.map.size) + 65
            ray_y = (self.x - ray_x) * neg_tan + self.y
            
            off_x = self.map.size
            off_y = -off_x * neg_tan
            
        if ray_angle == pi / 2 or ray_angle == pi + pi / 2:
            ray_x = self.x
            ray_y = self.y
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