import unittest
import math
import calc_figure_area.calc_figure_area as calc_figure_area

class TestParseContent(unittest.TestCase):
    def test_circle_area(self):
        c = calc_figure_area.Circle(1)
        self.assertEqual(c.area(), math.pi)

    def test_circle_is_rectangular(self):
        c = calc_figure_area.Circle(1)
        self.assertEqual(c.is_rectangular(), False)

    def test_triangle_area(self):
        t = calc_figure_area.Triangle(3, 4, 5)
        self.assertEqual(t.area(), 6.0)

    def test_invalid_triangle(self):
        with self.assertRaises(ValueError):
            t = calc_figure_area.Triangle(1, 2, 3)

    def test_triangle_is_rectangle(self):
        t = calc_figure_area.Triangle(3, 4, 5)
        self.assertTrue(t.is_rectangular())

    def test_triangle_is_not_rectangle(self):
        t = calc_figure_area.Triangle(2, 3, 4)
        self.assertFalse(t.is_rectangular())

    def test_factory_create_circle_and_use(self):
        circle = calc_figure_area.FigureFactory.create('circle', radius=2)
        circle_area = calc_figure_area.get_figure_area(circle)
        exp_area = math.pi * 4
        self.assertAlmostEqual(circle_area, exp_area)
        self.assertFalse(calc_figure_area.is_figure_rectangle(circle))

    def test_factory_create_triangle_and_use(self):
        triangle = calc_figure_area.FigureFactory.create('triangle', 3, 4, 5)
        triangle_area = calc_figure_area.get_figure_area(triangle)
        exp_area = 6.0
        self.assertAlmostEqual(triangle_area, exp_area)
        self.assertTrue(calc_figure_area.is_figure_rectangle(triangle))

    def test_add_new_figure(self):
        # Test for adding of new figure Square
        class Square(calc_figure_area.Figure):
            def __init__(self, side):
                self.side = side

            def area(self):
                return self.side ** 2

            def is_rectangular(self) -> bool:
                return True

        calc_figure_area.FigureFactory.register_figure('square', Square)
        square = calc_figure_area.FigureFactory.create('square', 5)
        self.assertEqual(square.area(), 25)
        self.assertTrue(calc_figure_area.is_figure_rectangle(square))


if __name__ == '__main__':
    unittest.main()