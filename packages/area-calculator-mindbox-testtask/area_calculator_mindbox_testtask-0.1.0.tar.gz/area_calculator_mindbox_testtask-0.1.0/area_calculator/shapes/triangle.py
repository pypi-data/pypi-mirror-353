from .base import Shape
from ..validators import (
    validate_positive_numbers,
    is_valid_triangle,
    is_triangle_rectangular,
)


class Triangle(Shape):
    def __init__(self, a_side, b_side, c_side):
        validate_positive_numbers(a_side, b_side, c_side)
        if not is_valid_triangle(a_side, b_side, c_side):
            raise ValueError("Invalid triangle")
        self.a_side = a_side
        self.b_side = b_side
        self.c_side = c_side
        self._rectangular = is_triangle_rectangular(a_side, b_side, c_side)

    @property
    def is_rectangular(self):
        return self._rectangular

    def area(self):
        if self.is_rectangular:
            sides = sorted([self.a_side, self.b_side, self.c_side])
            return (sides[0] * sides[1]) / 2
        s = (self.a_side + self.b_side + self.c_side) / 2
        return (s * (s - self.a_side) * (s - self.b_side) * (s - self.c_side)) ** 0.5
