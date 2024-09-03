import random
import math


def get_larger_random(self):
    y = 0
    while abs(y) < 0.2 or abs(y) > 0.9:
        y = random.uniform(-1, 1)
    return y


def normalize_vector(self, x, y):
    magnitude = math.sqrt(x**2 + y**2)
    return {"x": x / magnitude, "y": y / magnitude}
