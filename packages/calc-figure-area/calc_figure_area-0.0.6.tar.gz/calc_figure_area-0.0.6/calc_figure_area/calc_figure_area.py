from abc import ABC, abstractmethod
from math import pi, sqrt
from typing import Type


class Figure(ABC):
    @abstractmethod
    def area(self) -> float:
        pass

    def is_rectangular(self) -> bool:
        return False

class Circle(Figure):
    def __init__(self, radius: float):
        self.radius = radius

    def area(self):
        return pi * (self.radius ** 2)

class Triangle(Figure):
    def __init__(self, side1: float, side2: float, side3: float):
        self.side1 = side1
        self.side2 = side2
        self.side3 = side3
        if not self._is_triangle():
            raise ValueError("A triangle with current sides does not exist.")

    def _is_triangle(self) -> bool:
        return ( self.side1 + self.side2 > self.side3
                 and self.side1 + self.side3 > self.side2
                 and self.side2 + self.side3 > self.side1)

    def area(self) -> float:
        p: float = (self.side1 + self.side2 + self.side3) / 2
        s: float = sqrt( p * (p - self.side1) * (p - self.side2) * (p - self.side3))
        return s

    def is_rectangular(self) -> bool:
        a, b, c = sorted([self.side1, self.side2, self.side3])
        legs_square: float = a ** 2 + b ** 2
        hypotenuse_square: float = c ** 2
        return round(legs_square, 3) == round(hypotenuse_square, 3)


class FigureFactory:
    _registry = {}

    @classmethod
    def register_figure(cls, figure_name: str, figure_cls: Type[Figure]):
        cls._registry[figure_name] = figure_cls

    @classmethod
    def create(cls, figure_name: str, *args, **kwargs) -> Figure:
        if figure_name not in cls._registry:
            raise ValueError(f"A figure '{figure_name}' is not registered.")
        return cls._registry[figure_name](*args, **kwargs)


FigureFactory.register_figure('circle', Circle)
FigureFactory.register_figure('triangle', Triangle)


def get_figure_area(figure: Figure) -> float:
    return figure.area()

def is_figure_rectangle(figure: Figure) -> bool:
    return figure.is_rectangular()