#!/usr/bin/env python

from io import open
import math


class Shape:

    @staticmethod
    def unknown_shape(*args):
        """
        Функция вычисляет площадь фигуры не зная её тип
        3 аргумента - треугольник
        2 аргумента - прямоугольник (высота, ширина)
        1 аргумент - круг

        :param args: Параметры фигуры
        :return: Площадь фигуры
        :raises ValueError: Неизвестный тип фигуры
        """
        if len(args) == 1:
            return Shape.square_circle(args[0])
        elif len(args) == 2:
            return args[0] * args[1]
        elif len(args) == 3:
            return Shape.square_triangle(*args)
        else:
            raise ValueError('Неизвестный тип фигуры')

    @staticmethod
    def square_triangle(a: float, b: float, c: float) -> float:
        """
        Вычисляет площадь треугольника по трем известным сторонам

        :param a: Длина первой стороны треугольника
        :param b: Длина второй стороны треугольника
        :param c: Длина третьей стороны треугольника
        :return: Площадь треугольника
        :raises ValueError: В случае если стороны имеют не положительные числа или треугольник не существует
        """
        if a <= 0 or b <= 0 or c <= 0:
            raise ValueError('Все стороны должны быть положительным числом')

        if a + b <= c or a + c <= b or b + c <= a:
            raise ValueError("Треугольник с такими сторонами не существует")

        half_meter = (a + b + c) / 2
        return math.sqrt(half_meter * (half_meter - a) * (half_meter - b) * (half_meter - c))

    @staticmethod
    def is_right_triangle(a: float, b: float, c: float) -> float:
        """
        Проверка, является ли треугольник прямоугольным

        :param a: Длина первой стороны треугольника
        :param b: Длина второй стороны треугольника
        :param c: Длина третьей стороны треугольника
        :return: Проверяет, является ли треугольник прямоугольным
        :raises ValueError: В случае если стороны имеют не положительные числа
        """
        if a <= 0 or b <= 0 or c <= 0:
            raise ValueError('Все стороны должны быть положительным числом')

        if a + b <= c or a + c <= b or b + c <= a:
            raise ValueError("Треугольник с такими сторонами не существует")

        sides = sorted([a, b, c])
        return math.isclose(sides[2] ** 2,
                            sides[0] ** 2 + sides[1] ** 2)  # квадрат гипотенузы и сумма квадратов катетов

    @staticmethod
    def square_circle(radius: float) -> float:
        """
        Вычисляет площадь круга по радиусу

        :param radius: Радиус круга
        :return: Площадь круга
        :raises ValueError: В случае не положительного числа
        """
        if radius <= 0:
            raise ValueError('Радиус должен быть положительным числом')
        return math.pi * radius ** 2

