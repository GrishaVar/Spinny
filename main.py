#!/usr/bin/env python3

from tkinter import Tk, Canvas, Frame, BOTH
from math import sin, cos, pi

from shapes import ShapeCombination, Cube, SquarePyramid
from matrix import Matrix, Vector

width = 1024
height = 576
c = Vector(width/2, height/2)
pos = Vector(0,0,0)
movement = {
    'w': Vector(0,0,1),
    'a': Vector(-1,0,0),
    's': Vector(0,0,-1),
    'd': Vector(1,0,0),
    ' ': Vector(0,1,0),
    'q': Vector(0,-1,0),
    }

angle = pi/32  # very small angle
rotator = Matrix(  # y unchanged, x and z move along a circle
    [cos(angle), 0, -sin(angle)],
    [0, 1, 0],
    [sin(angle), 0, cos(angle)],
)
grower = Matrix(  # x,z unchanged, y gets a little smaller
    [1, 0, 0],
    [0, 0.95, 0],
    [0, 0, 1],
)
# You can multiply these matrices to get both effects.
both = rotator * grower

# LA skript: matrix multiplication is associative!

root = Tk()
root.geometry('{}x{}'.format(width, height))

canvas = Canvas(root)
canvas.pack(fill=BOTH, expand=1)

def draw_circle(v, r, canvas_name, color='black'):
    x,y = v.value

    x0 = x - r
    y0 = y - r
    x1 = x + r
    y1 = y + r
    return canvas_name.create_oval(x0, y0, x1, y1, fill=color)

def projection(v):  #https://en.wikipedia.org/wiki/3D_projection

    v -= pos
    z = v.value[2] # TODO: better way to do this?
    
    sx = 1/(z+5)  # shift z forwards, away from the view. Use reciprocal to scale down with increased z
    sy = 1/(z+5)
    sx *= 800  # zoom way in (original pyramid is tiny)
    sy *= -800  # tk has height wrong way around I think
    res = Matrix((sx,0,0), (0,sy,0)) * v  # different from wiki one because z is my depth
    res += c  # move to the middle
    return res

def myDraw(shape):
    canvas.delete('all')
    
    converted_points = []
    
    for v in shape.points:
        converted = projection(v)
        converted_points.append(converted)

        draw_circle(converted, 2, canvas, 'red')

    for p1, p2 in shape.lines:
        p1_vect = converted_points[p1]
        p2_vect = converted_points[p2]

        canvas.create_line(*p1_vect.value, *p2_vect.value)

    p = canvas.create_polygon(*converted_points[0].value, *converted_points[1].value, *converted_points[4].value)
    canvas.itemconfigure(p, fill='#603')

    shape.transform(rotator)  # yo linear algebra works

    root.after(50, lambda: myDraw(shape))

def move(event):
    global pos
    pos = pos + 0.05*movement[event.char]

#root.after(400, myDraw)
canvas.bind_all('<w>', move)
canvas.bind_all('<a>', move)
canvas.bind_all('<s>', move)
canvas.bind_all('<d>', move)
canvas.bind_all('<space>', move)
canvas.bind_all('<q>', move)

myShape = ShapeCombination(
    Cube(Vector(0,0,0)),
    Cube(Vector(0,0,1)),
    Cube(Vector(0,0,-1)),
    Cube(Vector(0,-1,-1)),
    Cube(Vector(0,-1,1)),
    SquarePyramid(Vector(0,1,1)),
    SquarePyramid(Vector(0,1,-1)),
    shift=Vector(-.5,-1.4,-.5),
)
#myShape = SquarePyramid(Vector(-.5,-.5,-.5))

myDraw(myShape)
root.mainloop()
