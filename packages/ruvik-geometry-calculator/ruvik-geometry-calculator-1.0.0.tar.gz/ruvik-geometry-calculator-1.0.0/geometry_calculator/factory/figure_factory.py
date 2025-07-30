from geometry_calculator.figure.circle import Circle
from geometry_calculator.figure.ifigure import IFigure
from geometry_calculator.figure.triangle import Triangle


class FigureFactory:
    """Фабрика для создания геометрических фигур"""

    @staticmethod
    def create_circle(radius: float) -> Circle:
        """Создает круг с заданным радиусом"""
        return Circle(radius)

    @staticmethod
    def create_triangle(side1: float, side2: float, side3: float) -> Triangle:
        """Создает треугольник с заданными сторонами"""
        return Triangle(side1, side2, side3)

    @staticmethod
    def create_figure(figure_type: str, *args) -> IFigure:
        """Универсальный фабричный метод"""
        if figure_type.lower() == "circle":
            return FigureFactory.create_circle(*args)
        elif figure_type.lower() == "triangle":
            return FigureFactory.create_triangle(*args)
        else:
            raise ValueError(f"Неизвестный тип фигуры: {figure_type}")