from levers import *
from levers.renderers import PyQtGraphRenderer


p1 = Point(rotating(x=0, y=0, r=2, f=0.25))
p2 = Point(static(x=4, y=0))
c1 = Circle(center=p1, radius=5)
c2 = Circle(center=p2, radius=5)
p3 = Point(on_intersection(c1, c2, select=upper_left))
p4 = Point(on_line(p3, p1, -5))
p5 = Point(static(x=0, y=0))
Line(p1, p4)
Line(p2, p3)
Line(p1, p5)
Trail(p4, 241)

PyQtGraphRenderer(-4, 11, -3, 12, 30).run(60)
# PyQtGraphRenderer(-4, 11, -3, 12, 30).capture(fps=60, frames=240, path='capture_folder')
