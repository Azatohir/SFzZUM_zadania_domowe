# przeszkoda
import numpy as np
import math
import random

import pygame
import sys


def kernel(r, rmax, leftBorder, rightBorder):
    if r >= rmax or r <= 0.0:
        return 0.0
    if r < leftBorder:
        return r / leftBorder
    if r <= rmax - rightBorder:
        return 1.0
    return (rmax - r) / rightBorder


class Fluid:
    def __init__(self, numX, numY, h, dt):
        self.numX = numX + 2
        self.numY = numY + 2
        self.h = h
        self.dt = dt
        self.numCells = self.numX * self.numY

        self.v = np.zeros(self.numCells)
        self.u = np.zeros(self.numCells)
        self.newV = np.zeros(self.numCells)
        self.newU = np.zeros(self.numCells)

        self.s = np.ones(self.numCells)  # czy moga sie ruszyc
        self.temp = np.zeros(self.numCells)
        self.newT = np.zeros(self.numCells)

        self.numSwirls = 0
        self.maxNumSwirls = 100
        self.swirlsTime = 50
        self.swirlX = np.zeros(self.maxNumSwirls)
        self.swirlY = np.zeros(self.maxNumSwirls)
        self.swirlOmega = np.zeros(self.maxNumSwirls)
        self.swirlRadius = np.zeros(self.maxNumSwirls)
        self.swirlTime = np.zeros(self.maxNumSwirls)

    def integrate(self, gravity):  # wplyw grawitacji (u nas brak)
        n = self.numY
        for i in range(1, self.numX):
            for j in range(1, self.numY - 1):
                if self.s[i * n + j] != 0.0 and self.s[i * n + j - 1] != 0.0:  # sprawdzamy pod aby ogien nie "polecial"
                    self.v[i * n + j] += gravity * self.dt

    def solveIncompressibility(self, numIters):  # niescisliwosc
        n = self.numY
        overRelaxation = 1.9

        for iter in range(numIters):
            for i in range(1, self.numX - 1):
                for j in range(1, self.numY - 1):
                    if self.s[i * n + j] == 0.0:
                        continue

                    sx0 = self.s[(i - 1) * n + j]
                    sx1 = self.s[(i + 1) * n + j]
                    sy0 = self.s[i * n + j - 1]
                    sy1 = self.s[i * n + j + 1]
                    s = sx0 + sx1 + sy0 + sy1

                    if s == 0:
                        continue
                    div = self.u[(i + 1) * n + j] - self.u[i * n + j] + self.v[i * n + j + 1] - self.v[i * n + j]

                    p = - div / s
                    p *= overRelaxation

                    self.u[i * n + j] -= sx0 * p
                    self.u[(i + 1) * n + j] += sx1 * p
                    self.v[i * n + j] -= sy0 * p
                    self.v[i * n + j + 1] += sy1 * p

    def extrapolate(self):  # predkosc na brzegu
        n = self.numY
        for i in range(self.numX):
            self.u[i * n + 0] = self.u[i * n + 1]
            self.u[i * n + self.numY - 1] = self.u[i * n + self.numY - 2]

        for j in range(self.numY):
            self.v[0 * n + j] = self.v[1 * n + j]
            self.v[(self.numX - 1) * n + j] = self.v[(self.numX - 2) * n + j]

    def sampleField(self, x, y, field):
        n = self.numY
        h = self.h
        h1 = 1.0 / h
        h2 = 0.5 * h

        x = max(min(x, self.numX * h), h)
        y = max(min(y, self.numY * h), h)

        dx = 0.0
        dy = 0.0

        if field == u_field:
            f = self.u
            dy = h2
        if field == v_field:
            f = self.v
            dx = h2
        if field == t_field:
            f = self.temp
            dx = h2
            dy = h2

        x0 = min(math.floor((x - dx) * h1), self.numX - 1)
        tx = ((x - dx) - x0 * h) * h1
        x1 = min(x0 + 1, self.numX - 1)

        y0 = min(math.floor((y - dy) * h1), self.numY - 1)
        ty = ((y - dy) - y0 * h) * h1
        y1 = min(y0 + 1, self.numY - 1)

        sx = 1.0 - tx
        sy = 1.0 - ty

        val = sx * sy * f[x0 * n + y0] + tx * sy * f[x1 * n + y0] + tx * ty * f[x1 * n + y1] + sx * ty * f[x0 * n + y1]

        return val

    def avgU(self, i, j):
        n = self.numY
        u = (self.u[i * n + j - 1] + self.u[i * n + j] + self.u[(i + 1) * n + j - 1] + self.u[(i + 1) * n + j]) * 0.25
        return u

    def avgV(self, i, j):
        n = self.numY
        u = (self.v[(i - 1) * n + j] + self.v[i * n + j] + self.v[(i - 1) * n + j + 1] + self.v[i * n + j + 1]) * 0.25
        return u

    def advectVel(self):
        self.newU = np.array(self.u)
        self.newV = np.array(self.v)

        n = self.numY
        h = self.h
        h2 = 0.5 * h

        for i in range(1, self.numX):
            for j in range(1, self.numY):
                # dla u
                if self.s[i * n + j] != 0.0 and self.s[(i - 1) * n + j] != 0.0 and j < n - 1:
                    x = i * h
                    y = j * h + h2
                    u = self.u[i * n + j]
                    v = self.avgV(i, j)
                    x = x - self.dt * u
                    y = y - self.dt * v
                    u = self.sampleField(x, y, u_field)
                    self.newU[i * n + j] = u

                # dla v
                if self.s[i * n + j] != 0.0 and self.s[i * n + j - 1] != 0.0 and i < self.numX - 1:
                    x = i * h + h2
                    y = j * h
                    u = self.avgU(i, j)
                    v = self.v[i * n + j]
                    x = x - self.dt * u
                    y = y - self.dt * v
                    v = self.sampleField(x, y, v_field)
                    self.newV[i * n + j] = v

        self.v = np.array(self.newV)
        self.u = np.array(self.newU)

    def advectTemperature(self):
        self.newT = np.array(self.temp)

        n = self.numY
        h = self.h
        h2 = 0.5 * h

        for i in range(1, self.numX - 1):
            for j in range(1, self.numY - 1):
                if self.s[i * n + j] != 0.0:
                    u = (self.u[i * n + j] + self.u[(i + 1) * n + j]) * 0.5
                    v = (self.v[i * n + j] + self.v[i * n + j + 1]) * 0.5
                    x = i * h + h2 - self.dt * u
                    y = j * h + h2 - self.dt * v

                    self.newT[i * n + j] = self.sampleField(x, y, t_field)

        self.temp = np.array(self.newT)

    def updateFire(self):
        for i in range(self.numX):
            for j in range(4):
                self.temp[i * self.numY + j] = 1.0

        h = self.h
        swirlTimeSpan = 1.0
        swirlOmega = 20.0
        swirlDamping = 10.0 * self.dt
        swirlProbability = prob * h * h

        fireCooling = 2 * self.dt    # 1.2
        smokeCooling = 0.9 * self.dt     # 0.3
        lift = 2.0
        acceleration = 6.0 * self.dt
        kernelRadius = swirlmaxR

        # update swirl

        n = self.numY
        maxX = (self.numX - 1) * h
        maxY = (self.numY - 1) * h

        # kill swirls

        num = 0
        for nr in range(self.numSwirls):
            self.swirlTime[nr] -= self.dt
            if self.swirlTime[nr] > 0.0:
                self.swirlTime[num] = self.swirlTime[nr]
                self.swirlX[num] = self.swirlX[nr]
                self.swirlY[num] = self.swirlY[nr]
                self.swirlOmega[num] = self.swirlOmega[nr]
                num += 1
        self.numSwirls = num

        # advect and modify velocity field

        for nr in range(self.numSwirls):
            ageScale = self.swirlTime[nr] / swirlTimeSpan
            x = self.swirlX[nr]
            y = self.swirlY[nr]
            swirlU = (1.0 - swirlDamping) * self.sampleField(x, y, u_field)
            swirlV = (1.0 - swirlDamping) * self.sampleField(x, y, v_field)
            x += swirlU * self.dt
            y += swirlV * self.dt
            x = min(max(x, h), maxX)
            y = min(max(y, h), maxY)

            self.swirlX[nr] = x
            self.swirlY[nr] = y
            omega = self.swirlOmega[nr]

            # update surrounding velocity field

            x0 = max(math.floor((x - kernelRadius) / h), 0)
            y0 = max(math.floor((y - kernelRadius) / h), 0)
            x1 = min(math.floor((x + kernelRadius) / h) + 1, self.numX - 1)
            y1 = min(math.floor((y + kernelRadius) / h) + 1, self.numY - 1)

            for i in range(x0, x1 + 1):
                for j in range(y0, y1 + 1):
                    for dim in range(2):
                        vx = i * h if dim == 0 else (i + 0.5) * h
                        vy = (j + 0.5) * h if dim == 0 else j * h

                        rx = vx - x
                        ry = vy - y
                        r = math.sqrt(rx * rx + ry * ry)

                        if r < kernelRadius:
                            s = 1.0
                            if r > 0.8 * kernelRadius:
                                s = 5.0 - 5.0 / kernelRadius * r

                            if dim == 0:
                                target = ry * omega + swirlU
                                u = self.u[i * n + j]
                                self.u[i * n + j] += (target - u) * s
                            else:
                                target = - rx * omega + swirlV
                                v = self.v[i * n + j]
                                self.v[i * n + j] += (target - v) * s

        for i in range(self.numX):
            for j in range(self.numY):
                t = self.temp[i * n + j]

                cooling = smokeCooling if t < 0.3 else fireCooling
                self.temp[i * n + j] = max(t - cooling, 0)
                u = self.u[i * n + j]
                v = self.v[i * n + j]
                targetV = t * lift
                self.v[i * n + j] += (targetV - v) * acceleration

                numNewSwirls = 0

                # floor burning

                if j < 4:
                    self.temp[i * n + j] = 1.0
                    self.u[i * n + j] = 0.0
                    self.v[i * n + j] = 0.0
                    if random.uniform(0, 1) < swirlProbability:
                        numNewSwirls += 1

                for k in range(numNewSwirls):
                    if self.numSwirls >= self.maxNumSwirls:
                        break
                    nr = self.numSwirls
                    self.swirlX[nr] = i * h
                    self.swirlY[nr] = j * h
                    self.swirlOmega[nr] = (-1.0 + 2.0 * random.uniform(0, 1)) * swirlOmega
                    self.swirlTime[nr] = swirlTimeSpan #* random.uniform(0, 1)
                    self.numSwirls += 1

            # smooth temperatures

        for i in range(1, self.numX - 1):
            for j in range(1, self.numY - 1):
                t = self.temp[i * n + j]
                if t == 1.0:
                    avg = (self.temp[(i - 1) * n + (j - 1)] +
                           self.temp[(i + 1) * n + (j - 1)] +
                           self.temp[(i + 1) * n + (j + 1)] +
                           self.temp[(i - 1) * n + (j + 1)]) * 0.25
                    self.temp[i * n + j] = avg

    def simulate(self, gravity, numIters):
        self.integrate(gravity)

        self.solveIncompressibility(numIters)
        self.extrapolate()
        self.advectVel()
        self.advectTemperature()
        self.updateFire()


def getColor(val):
    val = min(max(val, 0.0), 1.0)
    if val < 0.3:
        s = val / 0.3
        r = 0.2 * s
        g = 0.2 * s
        b = 0.2 * s
        return [min(255 * r, 255), min(255 * g, 255), min(255 * b, 255), 255]
    if val < 0.5:
        s = (val - 0.3) / 0.2
        r = 0.2 + 0.8 * s
        g = 0.1
        b = 0.1
        return [min(255 * r, 255), min(255 * g, 255), min(255 * b, 255), 255]
    s = (val - 0.5) / 0.48
    r = 1.0
    g = s
    b = 0.0
    return [min(255 * r, 255), min(255 * g, 255), min(255 * b, 255), 255]


# def cY(y):
#     return height - y

prob = 40
swirlmaxR = 0.05

u_field = 0
v_field = 1
t_field = 2

# --------------------------------------------------------------------------------------------------------------

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fluid Fire Simulation")

clock = pygame.time.Clock()

simHeight = 1.0
cScale = HEIGHT / simHeight
simWidth = WIDTH / cScale

numCells = 9000
h = math.sqrt(simWidth * simHeight / numCells)

numX = int(simWidth / h)
numY = int(simHeight / h)

dt = 5.0 / 60.0
gravity = 0.0
numIters = 5

fluid = Fluid(numX, numY, h, dt)

cellSize = int(cScale * h) + 1


def draw():
    screen.fill((0, 0, 0))
    n = fluid.numY

    for i in range(fluid.numX):
        for j in range(fluid.numY):
            t = fluid.temp[i * n + j]
            r, g, b, _ = getColor(t)

            x = int(i * h * cScale)
            y = HEIGHT - int((j + 1) * h * cScale)

            pygame.draw.rect(
                screen,
                (int(r), int(g), int(b)),
                (x, y, cellSize, cellSize)
            )

    pygame.display.flip()


running = True

while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    fluid.simulate(gravity, numIters)
    draw()
    print(fluid.numSwirls)

pygame.quit()
sys.exit()

# --------------------------------------------------------------------------------------------------------------
# self.boundary_condition = (lambda t: 0.0, lambda t: 0.0)     # mozna dac funkcje ktora podnosi / opuszcza belke

# zmień warunki brzegowe (tez trzeba zmienic doklade rozwiazanie ale da sie zrobic)

# co zrobic aby pozbyc sie bledu
# krok czasowy, alfa

# odpal symulacje na dluzej niz 2 sekundy

# w 5
