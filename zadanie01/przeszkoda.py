# przeszkoda

import pygame
import sys

pygame.init()


class Ball:
    def __init__(self, x, y, x1, x2, y1):
        self.x = x
        self.y = y
        self.gx = 0
        self.gy = -10
        self.vx = 15
        self.vy = 25
        self.radius = 20
        self.dt = 6
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y_old = y

    def change_of_speed(self):
        self.y_old = self.y
        self.vx += self.gx * 1 / self.dt
        self.vy += self.gy * 1 / self.dt
        self.x += self.vx * 1 / self.dt
        self.y += self.vy * 1 / self.dt

        if self.y < self.y1 and self.x2 > self.x > self.x1:
            if self.y_old > self.y1:
                self.vy = - self.vy
                self.y = self.y1
                return
            if self.vx > 0:
                self.x = self.x1
            else:
                self.x = self.x2
            self.vx = -self.vx
        if self.x < 0.0:
            self.x = 0.0
            self.vx = - self.vx
        if self.x > 800:
            self.x = 800
            self.vx = - self.vx
        if self.y < 0.0:
            self.y = 0.0
            self.vy = -self.vy


width, height = 800, 600
screen = pygame.display.set_mode((width, height))
gx = 0
gy = -10
vx = 15
vy = 25

x, y = 200, 200
radius = 20
clock = pygame.time.Clock()

the_chosen_ball1 = Ball(200, 200, 300, 500, 150)
the_chosen_ball2 = Ball(600, 200, 300, 500, 150)

def cY(poxy):
    return 600 - poxy


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.fill((255, 255, 255))

    the_chosen_ball1.change_of_speed()
    the_chosen_ball2.change_of_speed()
    pygame.draw.circle(screen, (0, 0, 255), (int(the_chosen_ball1.x), int(cY(the_chosen_ball1.y))), the_chosen_ball1.radius)
    pygame.draw.circle(screen, (0, 0, 255), (int(the_chosen_ball2.x), int(cY(the_chosen_ball2.y))), the_chosen_ball2.radius)
    pygame.draw.polygon(screen, (0, 0, 255), ((int(the_chosen_ball1.x1), cY(0)), (int(the_chosen_ball1.x1), cY(int(the_chosen_ball1.y1))),
                                              (int(the_chosen_ball1.x2), cY(int(the_chosen_ball1.y1))), (int(the_chosen_ball1.x2), cY(0))))

    pygame.display.flip()
    clock.tick(60)
