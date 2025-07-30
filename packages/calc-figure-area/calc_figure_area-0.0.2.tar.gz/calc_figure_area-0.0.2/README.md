# Calc figure area Library #

## What is this? ##
This library is test library.
The library can calculate the area of a circle by its radius 
and a triangle by its three sides.

There is also a check to see if a triangle is right-angled.

### Using ###


Using the library is as simple and convenient as possible:

Let's import it first:
First, import everything from the library (use the `from calc_figure_area_package import *` construct).

Examples of all operations:
```
# Create new object - circle
my_circle = FigureFactory.create('circle', radius=5)
# Calc figure area
circle_area = get_figure_area(my_circle)

# Print result
print(f"Circle area: {circle_area}")
print(f"Is triangle rectangle? {is_figure_rectangle(my_circle)}")

# Create new object - triangle
my_triangle = FigureFactory.create('triangle', side1=3, side2=4, side3=5)
# Calc figure area
triangle_area = get_figure_area(my_triangle)

# Print result
print(f"Triangle area: {triangle_area}")
print(f"Is triangle rectangle? {is_figure_rectangle(my_triangle)}")
```
