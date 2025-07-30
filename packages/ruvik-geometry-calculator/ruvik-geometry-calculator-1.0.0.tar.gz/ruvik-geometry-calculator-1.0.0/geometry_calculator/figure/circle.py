import math
from .ifigure import IFigure

class Circle(IFigure):
    """Класс круга"""

    def __init__(self, radius: float):
        self.radius = radius

    def area(self) -> float:
        if not self._is_valid():
            raise ValueError("Некорректные параметры круга")
        return math.pi * self.radius ** 2

    def _is_valid(self) -> bool:
        return self.radius > 0
