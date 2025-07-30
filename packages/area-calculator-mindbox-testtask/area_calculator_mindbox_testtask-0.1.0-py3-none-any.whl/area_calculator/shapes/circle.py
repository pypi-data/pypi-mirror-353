from .base import Shape
from math import pi
from ..validators import validate_positive_numbers


class Circle(Shape):
    def __init__(self, radius):
        validate_positive_numbers(radius)
        self.radius = radius

    def area(self):
        return pi * self.radius**2
