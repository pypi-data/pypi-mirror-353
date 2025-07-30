from abc import ABC, abstractmethod

class IFigure(ABC):
    """Абстрактный базовый класс для геометрических фигур"""

    @abstractmethod
    def area(self) -> float:
        """Вычисляет площадь фигуры"""
        pass

    @abstractmethod
    def _is_valid(self) -> bool:
        """Проверяет, может ли фигура существовать с заданными параметрами"""
        pass
