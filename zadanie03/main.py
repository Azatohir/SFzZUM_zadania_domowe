import math

from vpython import box, vector, color, rate
import random


class Box3D:
    def __init__(self, x, y, z, id=0, size=2, bounds=16):
        self.pos = vector(x, y, z)
        self.size = vector(size, size, size)
        self.v = vector(
            random.choice([-1, 1]) * random.uniform(0.05, 0.15),
            random.choice([-1, 1]) * random.uniform(0.05, 0.15),
            random.choice([-1, 1]) * random.uniform(0.05, 0.15)
        )
        self.color = color.yellow
        self.obj = box(pos=self.pos, size=self.size, color=self.color)

        self.id = id
        self.bounds = bounds
        self.morton = calculate_morton_code(self.pos.x, self.pos.y, self.pos.z, self.bounds)
        self.aabbMin = vector(0, 0, 0)
        self.aabbMax = vector(0, 0, 0)
        self.update_aabb()

    def morton_code(self):
        self.morton = calculate_morton_code(self.pos.x, self.pos.y, self.pos.z, self.bounds)
        return self.morton

    def update_aabb(self):
        halfx = self.size.x / 2
        halfy = self.size.y / 2
        halfz = self.size.z / 2
        self.aabbMin = vector(self.pos.x - halfx, self.pos.y - halfy, self.pos.z - halfz)
        self.aabbMax = vector(self.pos.x + halfx, self.pos.y + halfy, self.pos.z + halfz)

    def move(self, boundsX=16, boundsY=16, boundsZ=16):
        self.pos += self.v
        self.obj.pos = self.pos

        # bo ida od -a do a
        if abs(self.pos.x) > boundsX:
            self.v.x = -self.v.x
        if abs(self.pos.y) > boundsY:
            self.v.y = -self.v.y
        if abs(self.pos.z) > boundsZ:
            self.v.z = -self.v.z

        self.aabbMin = vector(
            min(self.pos.x - self.size.x / 2, self.pos.x + self.size.x / 2),
            min(self.pos.y - self.size.y / 2, self.pos.y + self.size.y / 2),
            min(self.pos.z - self.size.z / 2, self.pos.z + self.size.z / 2)
        )
        self.aabbMax = vector(
            max(self.pos.x - self.size.x / 2, self.pos.x + self.size.x / 2),
            max(self.pos.y - self.size.y / 2, self.pos.y + self.size.y / 2),
            max(self.pos.z - self.size.z / 2, self.pos.z + self.size.z / 2)
        )
        self.morton = calculate_morton_code(self.pos.x, self.pos.y, self.pos.z, self.bounds)

    def toggle_color(self):
        if self.color == color.yellow:
            self.color = color.red
        else:
            self.color = color.yellow
        self.obj.color = self.color


def check_collisions_Sweep_and_Prune(boxes):
    sorted_boxes = sorted(boxes, key=lambda box: box.pos.x)
    for i in range(len(sorted_boxes)):
        a = boxes[i]
        for j in range(i + 1, len(sorted_boxes)):
            b = boxes[j]

            if b.pos.x > a.pos.x + a.size.x:
                break
            if (
                    abs(a.pos.y - b.pos.y) * 2 < (a.size.y + b.size.y)
                    and abs(a.pos.z - b.pos.z) * 2 < (a.size.z + b.size.z)
            ):
                a.toggle_color()
                b.toggle_color()


def check_collisions_brute_force(boxes):
    for i in range(len(boxes)):
        a = boxes[i]
        for j in range(i + 1, len(boxes)):
            b = boxes[j]

            if (
                    abs(a.pos.x - b.pos.x) * 2 < (a.size.x + b.size.x)  # warunek kolizji 2 prostopadloscianow
                    and abs(a.pos.y - b.pos.y) * 2 < (a.size.y + b.size.y)
                    and abs(a.pos.z - b.pos.z) * 2 < (a.size.z + b.size.z)
            ):
                a.toggle_color()
                b.toggle_color()


# ------------------------------Morton Code
def expand_bits(v: int) -> int:
    v = (v * 0x00010001) & 0xFF0000FF
    v = (v * 0x00000101) & 0x0F00F00F
    v = (v * 0x00000011) & 0xC30C30C3
    v = (v * 0x00000005) & 0x49249249
    return v


def calculate_morton_code(x=0, y=0, z=0, bounds=32):
    def normalize_coord(val):
        return (val + bounds / 2) / bounds

    x = normalize_coord(x)
    y = normalize_coord(y)
    z = normalize_coord(z)

    x = min(max(x, 0.0), 1.0)
    y = min(max(y, 0.0), 1.0)
    z = min(max(z, 0.0), 1.0)

    x = min(int(x * 1023), 1023)  # liczba szescianow to 1024
    y = min(int(y * 1023), 1023)
    z = min(int(z * 1023), 1023)

    xx = expand_bits(x)
    yy = expand_bits(y)
    zz = expand_bits(z)

    return xx | (yy << 1) | (zz << 2)  # kod bitowy, ale zapis w int


# ------------------------------ kod BVH

class BVHNode:
    def __init__(self, idB=-1, left=None, right=None):
        self.left = left
        self.right = right
        self.box_id = idB
        self.aabbMax = vector(0, 0, 0)
        self.aabbMin = vector(0, 0, 0)

    def is_leaf(self) -> bool:
        return self.box_id != -1

    def get_box_id(self):
        return self.box_id


def createTree(list_boxes_with_id):
    for i, box in enumerate(list_boxes_with_id):
        box.index = i
        box.morton_code()
    list_sorted_by_id = sorted(list_boxes_with_id, key=lambda box: box.morton)
    return createSubTree(list_sorted_by_id, 0, len(list_sorted_by_id) - 1)


def createSubTree(list_sorted, i, n):
    if i == n:
        # używamy index, nie morton!
        leaf = BVHNode(list_sorted[i].index)
        leaf.aabbMin = list_sorted[i].aabbMin
        leaf.aabbMax = list_sorted[i].aabbMax
        return leaf

    m = (i + n) // 2
    left = createSubTree(list_sorted, i, m)
    right = createSubTree(list_sorted, m + 1, n)

    parent = BVHNode(-1, left, right)
    parent.aabbMin.x = min(left.aabbMin.x, right.aabbMin.x)
    parent.aabbMin.y = min(left.aabbMin.y, right.aabbMin.y)
    parent.aabbMin.z = min(left.aabbMin.z, right.aabbMin.z)

    parent.aabbMax.x = max(left.aabbMax.x, right.aabbMax.x)
    parent.aabbMax.y = max(left.aabbMax.y, right.aabbMax.y)
    parent.aabbMax.z = max(left.aabbMax.z, right.aabbMax.z)
    return parent


def aabbIntersection(aabb1Min, aabb1Max, aabb2Min, aabb2Max):
    return aabb1Min.x <= aabb2Max.x and aabb1Max.x >= aabb2Min.x and aabb1Min.y <= aabb2Max.y \
           and aabb1Max.y >= aabb2Min.y and aabb1Min.z <= aabb2Max.z \
           and aabb1Max.z >= aabb2Min.z

# ------------------------------ collision detection for BVH tree 288


def findCollisions(boxIdx, box, node, boxes, collisions):
    if not aabbIntersection(box.aabbMin, box.aabbMax, node.aabbMin, node.aabbMax):
        return

    if node.is_leaf():
        other_idx = node.box_id
        if other_idx != boxIdx:
            other_box = boxes[other_idx]
            if aabbIntersection(box.aabbMin, box.aabbMax, other_box.aabbMin, other_box.aabbMax):
                a, b = sorted((boxIdx, other_idx))
                collisions.add((a, b))
        return

    if node.left:
        findCollisions(boxIdx, box, node.left, boxes, collisions)
    if node.right:
        findCollisions(boxIdx, box, node.right, boxes, collisions)


def checkCollisionsBVH(boxes, bvhRoot):
    collisions_pairs = set()
    for i, b in enumerate(boxes):
        findCollisions(i, b, bvhRoot, boxes, collisions_pairs)
    collided_indices = set()
    for a,b in collisions_pairs:
        collided_indices.add(a)
        collided_indices.add(b)
    return collisions_pairs, collided_indices


# ------------------------------ animacje / kod

num_boxes = 35
boxes = [Box3D(random.uniform(-5, 5), random.uniform(-5, 5), random.uniform(-5, 5)) for _ in range(num_boxes)]

import time

start = time.time()
ile_razy = 0

while True:
    rate(60)
    if time.time() - start > 5:  # dziala 10 s
        break

    ile_razy += 1

    for b in boxes:
        b.move()

    # ------------------------------------- BVH

    root = createTree(boxes)

    pairs, collided_indices = checkCollisionsBVH(boxes, root)
    changed_c = []

    for i, b in enumerate(boxes):
        if i in collided_indices:
            if not(i in changed_c):
                if b.obj.color == color.yellow:
                    b.obj.color = color.red
                else:
                    b.obj.color = color.yellow
                changed_c.append(i)

print(ile_razy)

start = time.time()
ile_razy = 0

while True:
    rate(60)
    if time.time() - start > 5:  # dziala 10 s
        break

    ile_razy += 1

    for b in boxes:
        b.move()

    # ------------------------------------- Sweep and Prune

    check_collisions_Sweep_and_Prune(boxes)

print(ile_razy)
start = time.time()
ile_razy = 0

while True:
    rate(60)
    if time.time() - start > 5:  # dziala 10 s
        break

    ile_razy += 1

    for b in boxes:
        b.move()
    # ------------------------------------- brute force

    check_collisions_brute_force(boxes)

print(ile_razy)
