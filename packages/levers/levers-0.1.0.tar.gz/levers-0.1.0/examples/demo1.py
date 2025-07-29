from levers import *
from levers.renderers import PyQtGraphRenderer


red_point = Style(visible=True, color='r', width=10)
green_line = Style(visible=True, color='#0A0', width=1)

p2 = Point(static(2, 2), style=red_point)
p4 = Point(static(7, 2), style=red_point)

p1 = Point(rotating(2, 2, 1.5, 0.25))
Line(p1, p2)
c1 = Circle(p1, 4)
c2 = Circle(p4, 3)
p5 = Point(on_intersection(c1, c2))
Line(p1, p5)
Line(p5, p4)

p3 = Point(on_line(p2, p1, -0.7))
Line(p2, p3, style=green_line)
p6 = Point(on_line(p3, p4, 6))
Line(p3, p6, style=green_line)

PyQtGraphRenderer(0, 9, -2, 5, 60).run(60)
# PyQtGraphRenderer(0, 9, -2, 5, 80).capture(60, 120, 'capture_folder')
