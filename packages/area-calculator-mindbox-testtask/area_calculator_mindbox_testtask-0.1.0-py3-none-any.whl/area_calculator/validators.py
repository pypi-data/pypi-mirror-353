def validate_positive_numbers(*args):
    for value in args:
        if not isinstance(value, (int, float)):
            raise TypeError("Value must be a number")
        if value <= 0:
            raise ValueError("Value must be positive")


def is_valid_triangle(a_side, b_side, c_side):
    return (
        a_side + b_side > c_side
        and a_side + c_side > b_side
        and b_side + c_side > a_side
    )


def is_triangle_rectangular(a, b, c, tol=1e-9):
    sides = sorted([a, b, c])
    return abs(sides[0] ** 2 + sides[1] ** 2 - sides[2] ** 2) < tol
