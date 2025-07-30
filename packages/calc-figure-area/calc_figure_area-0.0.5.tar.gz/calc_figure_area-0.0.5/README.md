# Calc figure area Library #

## What is this? ##
This library is test library.
The library can calculate the area of a circle by its radius 
and a triangle by its three sides.

There is also a check to see if a triangle is right-angled.

### Using ###
Installation:
```
pip install calc-figure-area
```

Using the library is as simple and convenient as possible:

Let's import it first:
First, import everything from the library (use the `from calc_figure_area_package import *` construct).

Examples of all operations:
```
import calc_figure_area.calc_figure_area as my_lib

# Create new object
my_circle = my_lib.FigureFactory.create('circle', radius=5)
# Calc figure area
circle_area = my_lib.get_figure_area(my_circle)

# Print result
print(f"Circle area: {circle_area}")
print(f"Is triangle rectangle? {my_lib.is_figure_rectangle(my_circle)}")


# Create new object
my_triangle = my_lib.FigureFactory.create('triangle', side1=3, side2=4, side3=5)
# Calc figure area
triangle_area = my_lib.get_figure_area(my_triangle)

# Print result
print(f"Triangle area: {triangle_area}")
print(f"Is triangle rectangle? {my_lib.is_figure_rectangle(my_triangle)}")

```
