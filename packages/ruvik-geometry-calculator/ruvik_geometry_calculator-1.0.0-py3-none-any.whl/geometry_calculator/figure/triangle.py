import math

from .ifigure import IFigure

class Triangle(IFigure):
    """Класс треугольника"""

    def __init__(self, side1: float, side2: float, side3: float):
        self.sides = sorted([side1, side2, side3])

    def area(self) -> float:
        if not self._is_valid():
            raise ValueError("Некорректные параметры треугольника")

        a, b, c = self.sides
        p = (a + b + c) / 2
        return math.sqrt(p * (p - a) * (p - b) * (p - c))

    def _is_valid(self) -> bool:
        a, b, c = self.sides
        return a > 0 and b > 0 and c > 0 and a + b > c and a + c > b and b + c > a

    def is_right(self) -> bool:
        """Проверяет, является ли треугольник прямоугольным"""
        if not self._is_valid():
            raise ValueError("Некорректные параметры треугольника")

        a, b, c = self.sides
        return math.isclose(a ** 2 + b ** 2, c ** 2, rel_tol=1e-9)
