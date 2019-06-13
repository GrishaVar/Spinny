#!/usr/bin/env python3

from tkinter import Tk, Canvas, Frame, BOTH
from math import sin, cos, pi

from shapes import ShapeCombination, Cube, SquarePyramid
from matrix import Matrix, Vector

angle = pi/32  # very small angle
rotator = Matrix(  # y unchanged, x and z move along a circle
    [cos(angle), 0, -sin(angle)],
    [0, 1, 0],
    [sin(angle), 0, cos(angle)],
)

# LA skript: matrix multiplication is associative!

def draw_circle(v, r, canvas_name, color='black'):
    x,y = v.value

    x0 = x - r
    y0 = y - r
    x1 = x + r
    y1 = y + r
    return canvas_name.create_oval(x0, y0, x1, y1, fill=color)

def projection(v, camera, centre):
    v -= camera.pos
    z = v.value[2] # TODO: better way to do this?
    
    sx = 1/(z+5)  # shift z forwards, away from the view. Use reciprocal to scale down with increased z
    sy = 1/(z+5)
    sx *= 800  # zoom way in (original pyramid is tiny)
    sy *= -800  # tk has height wrong way around I think
    res = Matrix((sx,0,0), (0,sy,0)) * v  # different from wiki one because z is my depth
    res += centre  # move to the middle
    return res

class Camera():
    KEY_BINDINGS = {
        'w': Vector(0,0,1),
        'a': Vector(-1,0,0),
        's': Vector(0,0,-1),
        'd': Vector(1,0,0),
        ' ': Vector(0,1,0),
        'q': Vector(0,-1,0),
    }
    def __init__(self, v=Vector(0,0,0), speed=0.05):
        self.pos = v
        self.speed = speed
    
    def move(self, event):
        self.pos += self.speed*self.KEY_BINDINGS.get(event.char, Vector(0,0,0))


class Window():
    def __init__(self, root, canvas, shape, width, height):
        self.root = root
        self.canvas = canvas
        self.shape = shape
        self.width = width
        self.height = height

        self.root.geometry('{}x{}'.format(width, height))
        self.canvas.pack(fill=BOTH, expand=1)
        
        self.centre = Vector(self.width/2, self.height/2)
        self.refresh = 50
        self.camera = Camera()

        self.canvas.bind_all('<w>', self.camera.move)
        self.canvas.bind_all('<a>', self.camera.move)
        self.canvas.bind_all('<s>', self.camera.move)
        self.canvas.bind_all('<d>', self.camera.move)
        self.canvas.bind_all('<space>', self.camera.move)
        self.canvas.bind_all('<q>', self.camera.move)
    
    def start(self):
        self.draw()
        self.root.mainloop()

    def draw(self):
        self.canvas.delete('all')
        
        converted_points = []
        
        for v in self.shape.points:
            converted = projection(v, self.camera, self.centre)
            converted_points.append(converted)

            #draw_circle(converted, 2, canvas, 'red')

        for p1, p2 in self.shape.lines:
            p1_vect = converted_points[p1]
            p2_vect = converted_points[p2]

            self.canvas.create_line(*p1_vect.value, *p2_vect.value)

        p = self.canvas.create_polygon(*converted_points[0].value, *converted_points[1].value, *converted_points[2].value, *converted_points[3].value)
        self.canvas.itemconfigure(p, fill='#603')

        self.shape.transform(rotator)  # yo linear algebra works

        self.root.after(self.refresh, self.draw)


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

if __name__ == '__main__':
    root = Tk()
    canvas = Canvas(root)
    
    window = Window(root, canvas, myShape, 1024, 576)
    window.start()

