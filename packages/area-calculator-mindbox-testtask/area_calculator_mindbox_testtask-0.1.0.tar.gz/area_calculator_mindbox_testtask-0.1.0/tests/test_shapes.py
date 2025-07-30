import pytest
from area_calculator.shapes.triangle import Triangle
from area_calculator.shapes.circle import Circle
from math import pi


def test_triangle_creation():
    # Test valid triangle
    triangle = Triangle(3, 4, 5)
    assert triangle.a_side == 3
    assert triangle.b_side == 4
    assert triangle.c_side == 5
    assert triangle.is_rectangular == True

    # Test invalid triangle (sum of two sides less than third)
    with pytest.raises(ValueError, match="Invalid triangle"):
        Triangle(1, 2, 10)

    # Test negative sides
    with pytest.raises(ValueError, match="Value must be positive"):
        Triangle(-1, 2, 3)

    # Test non-numeric sides
    with pytest.raises(TypeError, match="Value must be a number"):
        Triangle("a", 2, 3)


def test_triangle_area():
    # Test right triangle (3-4-5)
    triangle1 = Triangle(3, 4, 5)
    assert triangle1.area() == 6.0  # (3 * 4) / 2

    # Test equilateral triangle
    triangle2 = Triangle(5, 5, 5)
    expected_area = (5 * 5 * (3**0.5)) / 4  # Formula for equilateral triangle
    assert abs(triangle2.area() - expected_area) < 1e-10

    # Test regular triangle
    triangle3 = Triangle(7, 8, 9)
    s = (7 + 8 + 9) / 2
    expected_area = (s * (s - 7) * (s - 8) * (s - 9)) ** 0.5  # Heron's formula
    assert abs(triangle3.area() - expected_area) < 1e-10


def test_triangle_rectangular():
    # Test right triangle
    assert Triangle(3, 4, 5).is_rectangular == True
    assert Triangle(5, 12, 13).is_rectangular == True

    # Test non-right triangles
    assert Triangle(5, 5, 5).is_rectangular == False
    assert Triangle(7, 8, 9).is_rectangular == False


def test_circle_creation():
    # Test valid circle
    circle = Circle(5)
    assert circle.radius == 5

    # Test negative radius
    with pytest.raises(ValueError, match="Value must be positive"):
        Circle(-1)

    # Test non-numeric radius
    with pytest.raises(TypeError, match="Value must be a number"):
        Circle("a")


def test_circle_area():
    circle = Circle(5)
    assert circle.area() == pi * 25  # pi * r^2

    # Test circle with different radius
    circle2 = Circle(10)
    assert circle2.area() == pi * 100
