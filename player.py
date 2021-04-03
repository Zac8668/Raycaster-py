from dataclasses import dataclass
import pygame
from math import pi, cos, sin, tan, sqrt

@dataclass
class Map:
    array = [
        [1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 0, 0, 0 ,1],
        [1, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1]
    ]
    width:int = len(array[0])
    height:int = len(array)
    size:int = 64

@dataclass
class Player:
    x:int = 200
    y:int = 240
    size:int = 20
    velocity:float = 8
    
    angle:float = pi / 2
    rot_speed:float = 0.05
    l_size:int = 5
    
    fov:int = 60
    rays:int = 256
    map:Map = Map()
    
    h_v = False
    
    def update(self):
        if hasattr(self, 'rect') == False:
            self.deltax = 0
            self.deltay = 0
            deltax, deltay = self.calc_delta(self.deltax, self.deltay, self.angle)
            self.l_pos = (self.x + self.deltax * self.l_size,
                          (self.y + self.deltay * self.l_size) - 1)
            self.rect = pygame.Rect(self.get_topleft()[0], self.get_topleft()[1], self.size, self.size)

        else:
            self.move(pygame.key.get_pressed())
            self.rect.topleft = self.get_topleft()
    
    def move(self, keys):
        if keys[pygame.K_w] and keys[pygame.K_s] == False:
            self.x += self.deltax
            self.y += self.deltay
            
        elif keys[pygame.K_s] and keys[pygame.K_w] == False:
            self.x -= self.deltax
            self.y -= self.deltay
        self.calc_angle()
            
        if keys[pygame.K_a] and keys[pygame.K_d] == False:
            angle = self.angle - pi / 2
            if angle > 2 * pi:
                angle -= 2 * pi
            if angle < 0:
                angle += 2 * pi
                
            x, y = self.calc_delta(0, 0, angle)
            
            self.x += x
            self.y += y
            
        elif keys[pygame.K_d] and keys[pygame.K_a] == False:
            angle = self.angle + pi / 2
            if angle > 2 * pi:
                angle -= 2 * pi
            if angle < 0:
                angle += 2 * pi
                
            x, y = self.calc_delta(0, 0, angle)
            
            self.x += x
            self.y += y
            
        self.calc_angle()
            
        if keys[pygame.K_UP] and keys[pygame.K_DOWN] == False:
            self.fov += 1
        elif keys[pygame.K_DOWN] and keys[pygame.K_UP] == False:
            self.fov -= 1
            
        self.deltax, self.deltay = self.calc_delta(self.deltax, self.deltay, self.angle)
        self.l_pos = (self.x + self.deltax * self.l_size,
                      (self.y + self.deltay * self.l_size) - 1)
        
    def closest_int(self, n, closest):
        return int(int(n/closest)*closest)
    
    def line_lenght(self, pos):
        spos = [self.x, self.y]
        return sqrt((spos[0] - pos[0])**2 + (spos[1] - pos[1])**2)
    
    def cast_ray(self, ray_angle):
        v = self.cast_vray(ray_angle)
        h = self.cast_hray(ray_angle)
        v_l = self.line_lenght(v)
        h_l = self.line_lenght(h)
        
        if self.h_v == True:
            return h
        elif self.h_v == 'both':
            if h_l < v_l:
                return h
            if v_l < h_l:
                return v
        else:
            return v
    
    def cast_hray(self, ray_angle, checks = 8):
        tan_ = tan(ray_angle)
        
        if tan_ != 0:
            tan_ = -1/tan(ray_angle)

        calc_off = [0, checks]
            
        if ray_angle > pi: #looking up
            ray_y = self.closest_int(self.y, self.map.size) - 1
            ray_x = (self.y - ray_y) * tan_ + self.x + 1
            off_y = -self.map.size
            off_x = -off_y * tan_
            
        if ray_angle < pi: #looking down
            ray_y = self.closest_int(self.y, self.map.size) + self.map.size + 1
            ray_x = (self.y - ray_y) * tan_ + self.x + 1
            off_y = self.map.size
            off_x = -off_y * tan_
            
        if ray_angle == 0 or ray_angle == pi: #looking left or right
            ray_x = self.x
            ray_y = self.y
            calc_off[0] = calc_off[1]
            
        while calc_off[0] < calc_off[1]:
            #getting map positions
            map_x = int(ray_x / self.map.size)
            map_y = int(ray_y / self.map.size)
            
            #check if hit wall
            if map_x < self.map.width and map_y < self.map.height and map_x > -1 and map_y > -1 and self.map.array[map_y][map_x] == 1:
                #hit wall
                calc_off[0] = calc_off[1]
            #if not add offset
            else:
                ray_x += off_x
                ray_y += off_y
                if calc_off[0] == calc_off[1] - 1:
                    return [ray_x, ray_y, None]
                
                calc_off[0] += 1
        
        return [ray_x, ray_y, 'h']
    
    def cast_vray(self, ray_angle, checks = 8):
        neg_tan = -tan(ray_angle)
        calc_off = [0, checks]
                    
        if ray_angle > pi / 2 and ray_angle < pi + pi / 2: #looking left
            ray_x = self.closest_int(self.x, self.map.size) - 1
            ray_y = ((self.x - ray_x) * neg_tan + self.y)
            
            off_x = -self.map.size
            off_y = -off_x * neg_tan
            
        if ray_angle > pi + pi / 2 or ray_angle < pi / 2: #looking right
            ray_x = self.closest_int(self.x, self.map.size) + self.map.size + 1
            ray_y = (self.x - ray_x) * neg_tan + self.y
            
            off_x = self.map.size
            off_y = -off_x * neg_tan
            
        if ray_angle == pi / 2 or ray_angle == pi + pi / 2: #looking up or down
            ray_x = self.x
            ray_y = self.y
            calc_off[0] = calc_off[1]
            
        while calc_off[0] < calc_off[1]:
            #getting map positions
            map_x = int(ray_x / self.map.size)
            map_y = int(ray_y / self.map.size)
            
            #check if hit wall
            if map_x < self.map.width and map_y < self.map.height and map_x > -1 and map_y > -1 and self.map.array[map_y][map_x] == 1:
                #hit wall
                calc_off[0] = calc_off[1]
                
            #if not hit wall add offset
            else:
                ray_x += off_x
                ray_y += off_y
                
                if calc_off[0] == calc_off[1] - 1:
                    return [ray_x, ray_y, None]
                
                calc_off[0] += 1
                
        return [ray_x, ray_y, 'v']
        
    def calc_angle(self):
        if self.angle > pi * 2:
            self.angle -= pi * 2
        elif self.angle < 0:
            self.angle += pi * 2
            
    def calc_delta(self, deltax, deltay, angle):
        deltax = cos(angle) * self.velocity
        deltay = sin(angle) * self.velocity
        return deltax, deltay
                
    def get_topleft(self):
        x = self.x - int(self.size / 2)
        y = self.y - int(self.size / 2)
        return (x, y)