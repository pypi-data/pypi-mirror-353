import math
import os
import pygame
from .particle import Particle

class ParticleLife:
    def __init__(self, height=500, width=1000):
        pygame.init()
        self.height = height
        self.width = width
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption('Particle Life')
        self.clock = pygame.time.Clock()
        
        self.show_fps = True
    
    def rule(self, particles1, particles2, G):
        for i in range(len(particles1)):
            Fx = 0
            Fy = 0
            for j in range(len(particles2)):
                a = particles1[i]
                b = particles2[j]

                if a==b:
                    continue

                dx = b.x - a.x
                dy = b.y - a.y
                d = math.sqrt(dx**2 + dy**2)
                if d > 1 and d < 80:
                    F = (G * a.mass * b.mass) / (d**2)
                    Fx += F * dx
                    Fy += F * dy

            a.vx = (a.vx + Fx)*0.5
            a.vy = (a.vy + Fy)*0.5

            a.move()
            if a.x < 20 or a.x > self.width-20:
                a.vx *= -1
            if a.y < 20 or a.y > self.height-20:
                a.vy *= -1
        
        for i in range(len(particles2)):
            Fx = 0
            Fy = 0
            for j in range(len(particles1)):
                a = particles2[i]
                b = particles1[j]

                if a==b:
                    continue

                dx = b.x - a.x
                dy = b.y - a.y
                d = math.sqrt(dx**2 + dy**2)
                if d > 1 and d < 80:
                    F = (G * a.mass * b.mass) / (d**2)
                    Fx += F * dx
                    Fy += F * dy

            a.vx = (a.vx + Fx)*0.5
            a.vy = (a.vy + Fy)*0.5

            a.move()
            if a.x <= 10 or a.x >= 990:
                a.vx *= -1
            if a.y <= 10 or a.y >= 490:
                a.vy *= -1
    
    def create(self, n, color, mass=1, radius=5):
        if mass < 0 or radius < 5:
            print('Error: Mass should be greater than or equal to 0 (zero) and Radius should be greater than or equal to 5 (five).')
            import sys
            sys.exit()
        group = []
        for i in range(n):
            group.append(Particle(color, mass, radius))
        return group
    
    def draw(self, group):
        for particle in group:
            particle.draw(self.screen)    
    
    def run(self, function):
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self.screen.fill('white')
            function()

            pygame.display.update()
            self.clock.tick(1000)
            if self.show_fps:
                os.system('cls')
                print(f"FPS: {int(self.clock.get_fps())}")

def example():
    sim = ParticleLife()
    
    blue = sim.create(200, 'blue')
    red = sim.create(200, 'red')

    def main():
        sim.draw(blue)
        sim.draw(red)

        sim.rule(blue, blue, 10)
        sim.rule(blue, red, -10)
        sim.rule(red, red, -1)

    sim.run(main)