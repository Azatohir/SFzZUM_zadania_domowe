# strata energi przy odbiciu
import random

import pygame
import sys

pygame.init()


class Ball:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.gx = 0
        self.gy = -10
        self.vx = 15
        self.vy = 25
        self.radius = 20
        self.dt = 6

    def change_of_speed(self):
        self.vx += self.gx * 1 / self.dt
        self.vy += self.gy * 1 / self.dt

        # nasze opory pow
        self.vx *= 0.99
        self.vy *= 0.99

        self.x += self.vx * 1 / self.dt
        self.y += self.vy * 1 / self.dt

        if self.x < 0.0:
            self.x = 0.0
            self.vx = - 0.95 * self.vx
        if self.x > 800:
            self.x = 800
            self.vx = - 0.95 * self.vx
        if self.y < 0.0:
            self.y = 0.0
            self.vy = - 0.95 * self.vy


width, height = 800, 600
screen = pygame.display.set_mode((width, height))
gx = 0
gy = -10
vx = 15
vy = 25

x, y = 200, 200
radius = 20
clock = pygame.time.Clock()

number_of_balls = 1
all_balls = []
for i in range(number_of_balls):
    all_balls.append(Ball(random.randint(50, width-50), random.randint(50, height-50)))



def cY(poxy):
    return 600 - poxy


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.fill((255, 255, 255))

    for ball in all_balls:
        ball.change_of_speed()
        pygame.draw.circle(screen, (0, 0, 255), (int(ball.x), int(cY(ball.y))), ball.radius)

    pygame.display.flip()
    clock.tick(60)

