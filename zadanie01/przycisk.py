# przycisk aby podskoczyly
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
        self.vx = random.randint(-15, 15)
        self.vy = random.randint(-15, 25)
        self.radius = 20
        self.dt = 6

    def change_of_speed(self):
        self.vx += self.gx * 1 / self.dt
        self.vy += self.gy * 1 / self.dt
        self.x += self.vx * 1 / self.dt
        self.y += self.vy * 1 / self.dt

        if self.x - self.radius < 0:
            self.x = self.radius
            self.vx = -self.vx
        if self.x + self.radius > 800:
            self.x = 800 - self.radius
            self.vx = -self.vx
        if self.y - self.radius < 0:
            self.y = self.radius
            self.vy = -self.vy
        if self.y + self.radius > 600:
            self.y = 600 - self.radius
            self.vy = -self.vy

    def jump(self):
        self.vy += 35


width, height = 800, 600
screen = pygame.display.set_mode((width, height))

clock = pygame.time.Clock()

number_of_balls = 10
all_balls = []
for i in range(number_of_balls):
    all_balls.append(Ball(random.randint(50, width-50), random.randint(50, height-50)))


def cY(poxy):
    return 600 - poxy


button_rect = pygame.Rect(width - 180, height - 70, 150, 50)
font = pygame.font.SysFont(None, 36)

def draw_button():
    pygame.draw.rect(screen, (0, 120, 255), button_rect, border_radius=12)
    text = font.render("Jump", True, (255, 255, 255))
    screen.blit(text, (button_rect.x + 10, button_rect.y + 10))


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if button_rect.collidepoint(event.pos):
                for ball in all_balls:
                    ball.jump()

    screen.fill((255, 255, 255))

    for ball in all_balls:
        ball.change_of_speed()
        pygame.draw.circle(screen, (0, 0, 255), (int(ball.x), int(cY(ball.y))), ball.radius)

    draw_button()

    pygame.display.flip()
    clock.tick(60)

