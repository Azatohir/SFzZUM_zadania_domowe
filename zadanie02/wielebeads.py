#wiele beads
import pygame
import math
import random
import sys


class Vector2D:
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y

    def set(self, other):
        self.x = other.x
        self.y = other.y
        return self

    def clone(self):
        return Vector2D(self.x, self.y)

    def add(self, other, s=1.0):
        self.x += other.x * s
        self.y += other.y * s
        return self

    def addVectors(self, a, b):
        self.x = a.x + b.x
        self.y = a.y + b.y
        return self

    def subtract(self, v, s=1.0):
        self.x -= v.x * s
        self.y -= v.y * s
        return self

    def subtractVectors(self, a, b):
        self.x = a.x - b.x
        self.y = a.y - b.y
        return self

    def length(self):
        return math.sqrt(self.x * self.x + self.y * self.y)

    def scale(self, s):
        self.x *= s
        self.y *= s
        return self

    def dot(self, v):
        return self.x * v.x + self.y * v.y

    def perp(self):
        return Vector2D(-self.y, self.x)


class Bead:
    def __init__(self, radius, mass, pos):
        self.radius = radius
        self.mass = mass
        self.pos = pos.clone()
        self.prevPos = pos.clone()
        self.vel = Vector2D()

    def start_step(self, dt, gravity: Vector2D):
        self.vel.add(gravity, dt)
        self.prevPos.set(self.pos)
        self.pos.add(self.vel, dt)

    def keep_on_wire(self, center: Vector2D, wire_radius):
        dir_vec = Vector2D()
        dir_vec.subtractVectors(self.pos, center)
        length = dir_vec.length()
        if length == 0.0:
            return 0.0
        dir_vec.scale(1.0 / length)
        lam = wire_radius - length
        self.pos.add(dir_vec, lam)
        return lam

    def end_step(self, dt):
        self.vel.subtractVectors(self.pos, self.prevPos)
        self.vel.scale(1.0 / dt)


def handle_bead_bead_collision(bead1, bead2):
    restitution = 1.0
    dir_vec = Vector2D()
    dir_vec.subtractVectors(bead2.pos, bead1.pos)
    d = dir_vec.length()
    if d == 0.0 or d > bead1.radius + bead2.radius:
        return
    dir_vec.scale(1.0 / d)

    corr = (bead1.radius + bead2.radius - d) / 2.0
    bead1.pos.add(dir_vec, -corr)
    bead2.pos.add(dir_vec, corr)

    v1 = bead1.vel.dot(dir_vec)
    v2 = bead2.vel.dot(dir_vec)
    m1, m2 = bead1.mass, bead2.mass

    newV1 = (m1 * v1 + m2 * v2 - m2 * (v1 - v2) * restitution) / (m1 + m2)
    newV2 = (m1 * v1 + m2 * v2 - m1 * (v2 - v1) * restitution) / (m1 + m2)

    bead1.vel.add(dir_vec, newV1 - v1)
    bead2.vel.add(dir_vec, newV2 - v2)


def setup_scene():
    beads = []
    num_beads = 5
    r = 0.1
    angle = 0.0
    for _ in range(num_beads):
        mass = math.pi * r * r
        pos = Vector2D(
            wireCenter.x + wireRadius * math.cos(angle),
            wireCenter.y + wireRadius * math.sin(angle)
        )
        beads.append(Bead(r * 100, mass, pos))
        angle += math.pi / num_beads
        r = 0.05 + random.random() * 0.1
    return beads


gravity = Vector2D(0.0, -10.0)
dt = 1.0 / 10.0
numSteps = 100

pygame.init()
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Constrained Dynamics - Multiple Beads")
clock = pygame.time.Clock()

wireCenter = Vector2D(width / 2, height / 2)
wireRadius = 200

beads = setup_scene()


def cY(y):
    return height - y


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            beads = setup_scene()

    sdt = dt / numSteps
    for _ in range(numSteps):
        for bead in beads:
            bead.start_step(sdt, gravity)

        for bead in beads:
            bead.keep_on_wire(wireCenter, wireRadius)

        for bead in beads:
            bead.end_step(sdt)

        for i in range(len(beads)):
            for j in range(i):
                handle_bead_bead_collision(beads[i], beads[j])

    screen.fill((255, 255, 255))
    pygame.draw.circle(screen, (255, 0, 0), (int(wireCenter.x), int(cY(wireCenter.y))), wireRadius, 2)

    for bead in beads:
        pygame.draw.circle(screen, (0, 0, 255), (int(bead.pos.x), int(cY(bead.pos.y))), int(bead.radius))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
