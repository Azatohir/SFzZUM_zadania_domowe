#zmienna masa srodka
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

    def clone(self, other):
        return Vector2D(other.x, other.y)

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
    def __init__(self, radius, bead_radius, mass, pos: Vector2D, angle=0):
        self.radius = radius
        self.mass = mass
        self.pos = pos.clone(pos)
        self.prevPos = pos.clone(pos)
        self.vel = Vector2D()
        self.bead_radius = bead_radius
        self.angle = angle
        self.omega = 0.0

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

        dir_vec.scale(1.0/length)
        lam = wire_radius - length
        self.pos.add(dir_vec, lam)
        return lam

    def end_step(self, dt):
        self.vel.subtractVectors(self.pos, self.prevPos)
        self.vel.scale(1.0/dt)

    def simulate_analytic(self, dt, gravity):
        acc = -gravity / self.radius * math.sin(self.angle)
        self.omega += acc * dt
        self.angle += self.omega * dt

        centrifugal_force = self.omega ** 2 * self.radius
        total_force = centrifugal_force + math.cos(self.angle) * abs(gravity)
        return total_force

    def get_pos_analytic(self):
        return Vector2(
            math.sin(self.angle) * self.radius,
            -math.cos(self.angle) * self.radius
        )


gravity = Vector2D(0.0, -10.0)
dt = 1.0 / 10.0
numSteps = 1000
paused = False

pygame.init()
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()

wireCenter = Vector2D(width / 2, height / 2)
wireRadius = 200
bead_radius = 50
bead_mass = 1000.0

start_pos = Vector2D(wireCenter.x + wireRadius, wireCenter.y)
bead = Bead(wireRadius, bead_radius, bead_mass, start_pos)

# srodek
wire_mass = 1.0
wire_pos = wireCenter.clone(wireCenter)
wire_vel = Vector2D()


def keep_on_wire_pbd(bead: Bead, center: Vector2D, wire_radius, wire_mass):
    dir_vec = Vector2D()
    dir_vec.subtractVectors(bead.pos, center)
    length = dir_vec.length()
    if length == 0.0:
        return 0.0
    dir_vec.scale(1.0 / length)
    correction = wire_radius - length

    w_bead = 1.0 / bead.mass
    w_wire = 1.0 / wire_mass
    sum_w = w_bead + w_wire

    bead_correction = dir_vec.clone(dir_vec).scale(correction * w_bead / sum_w)
    wire_correction = dir_vec.clone(dir_vec).scale(-correction * w_wire / sum_w)

    bead.pos.add(bead_correction)
    center.add(wire_correction)
    return correction


def cY(y):
    return height - y


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            bead = Bead(wireRadius, bead_radius, bead_mass, start_pos)

    sdt = dt / numSteps
    for _ in range(numSteps):
        bead.start_step(sdt, gravity)
        lam = keep_on_wire_pbd(bead, wire_pos, wireRadius, wire_mass)
        bead.end_step(sdt)
        # Aktualizacja drutu na podstawie prędkości (prosta integracja)
        wire_vel = Vector2D()
        wire_vel.subtractVectors(wire_pos, wireCenter)
        wireCenter.set(wire_pos)

    force = abs(lam / (sdt * sdt)) if lam is not None else 0.0

    screen.fill((255, 255, 255))
    pygame.draw.circle(screen, (255, 0, 0), (int(wire_pos.x), int(cY(wire_pos.y))), wireRadius, 2)

    pygame.draw.circle(screen, (0, 0, 255), (int(bead.pos.x), int(cY(bead.pos.y))), bead_radius)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
