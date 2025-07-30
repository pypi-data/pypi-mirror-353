import pygame
import random
import math

class Particle:
    def __init__(self, color, mass, radius):
        self.mass = mass
        self.color = color
        self.radius = radius
        self.x = random.randint(10, 990)
        self.y = random.randint(10, 490)
        self.vx = 0
        self.vy = 0
        self.max_speed = 5

    def move(self):
        speed = math.sqrt(self.vx ** 2 + self.vy ** 2)
        if speed > self.max_speed:
            scale = self.max_speed / speed
            self.vx *= scale
            self.vy *= scale
        
        self.x += self.vx
        self.y += self.vy

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)