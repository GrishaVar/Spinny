#!/usr/bin/env python3

import time
from tkinter import Tk, Canvas, BOTH, EventType
from math import pi
from collections import OrderedDict

from shapes import ShapeCombination, Cube, SquarePyramid, Octagon
from matrix import Vector as V
from common import M3
from camera import Camera, projection
from colour import Shader


CURSOR_VIS = {False: 'none', True: ''}
PAUSE_TEXT = {False: '', True: 'PAUSED'}
obj_rotator = M3.z_rot(pi / 32)  # very small angle
SUN_VECTOR = V([1,0,-1]).unit


def draw_circle(v, r, canvas, colour='black'):
    """
    Draws circle on canvas using tk's oval method.
    :param v: vector of circle centre
    :param r: radius of circle in pixels
    :param canvas: canvas object
    :param colour: colour of circle
    :return: canvas oval object
    """
    x,y = v._value
    if r < 0:
        r = 0

    x0 = x - r
    y0 = y - r
    x1 = x + r
    y1 = y + r
    return canvas.create_oval(x0, y0, x1, y1, fill=colour, tag='clearable')


class InfoBox:
    """
    Draws box with runtime for debug information.

    add(self, item, default='', rounding=None) adds item to box.
    draw(self, *args) re-draws box with updated information.

    canvas: Given tk Canvas object.
    x, y: ints, top-left position of box.
    width: int, with of box in pixels.
    items: OrderedDict of given info lines.
    """
    def __init__(self, canvas, pos, width, fill='white', border='black'):
        self.canvas = canvas
        self.x, self.y = pos
        self.width = width

        self.items = OrderedDict()
        self.counter = 0

        self.text_box = self.canvas.create_polygon(
            0, 0,
            fill=fill,
            outline=border,
            width=2,
            tag='infobox',
        )

    def add(self, item, default='', rounding=None):
        """
        Add item to InfoBox.
        :param item: str, identifier
        :param default: str, text to display
        :param rounding: int, rounding
        """
        if item in self.items:
            return  # TODO: what should I do here?
        obj = self.canvas.create_text(
            self.x+2,
            self.y+2 + 17*self.counter,
            anchor='nw',
            font='Arial 13',
            tag='infobox',
        )
        self.items[item] = (default, obj, rounding)
        self.counter += 1
        self.resize_box()

    def draw(self, *args):
        """
        Draws/Updates InfoBox with given args.
        :param args: iterable of arguments for each item, in order
        """
        if len(args) != len(self.items):
            raise TypeError('Too many/few arguments')
        self.canvas.tag_raise(self.text_box)
        for item, value in zip(self.items, args):
            default, obj, rounding = self.items[item]
            if rounding is not None:
                value = round(value, rounding)
            self.canvas.itemconfig(obj, text=default.format(value))
            self.canvas.tag_raise(obj)

    def resize_box(self):
        self.canvas.coords(
            self.text_box,
            self.x, self.y,
            self.x, self.y + 17*self.counter + 4,  # TODO: fix magic numbers
            self.x+self.width, self.y + 17*self.counter + 4,
            self.x+self.width, self.y
        )


class Window:
    KEY_BINDINGS = {
        'w': V([0,1,0]),
        'a': V([-1,0,0]),
        's': V([0,-1,0]),
        'd': V([1,0,0]),
        ' ': V([0,0,1]),
        'q': V([0,0,-1]),
        'i': V([1,0]),
        'j': V([0,1]),
        'k': V([-1,0]),
        'l': V([0,-1]),
    }

    def __init__(self, root, canvas, shape):
        self.root = root
        self.canvas = canvas
        self.shape = shape
        self.width = self.root.winfo_screenwidth()
        self.height = self.root.winfo_screenheight()
        self.w2 = self.width // 2
        self.h2 = self.height // 2

        self.root.title('3D Thing')
        self.root.geometry('{}x{}+0+0'.format(self.width, self.height))
        self.canvas.pack(fill=BOTH, expand=1)

        self.centre = V([self.w2, self.h2])
        self.refresh = 30
        self.camera = Camera()
        self.mouse = [0, 0]
        self.paused = False
        self.paused_text = self.canvas.create_text(
            self.w2,
            10,
            anchor='n',
            font='Arial 50'
        )
        self.pause_motion()
        self.shader = Shader()

        self.counter = 0
        self.time_one = 0
        self.time_min = float('inf')
        self.time_tot = 0
        self.time_max = 0

        self.infobox = InfoBox(self.canvas, (5,5), 100)
        self.infobox.add('x', default='X = {}', rounding=2)
        self.infobox.add('y', default='Y = {}', rounding=2)
        self.infobox.add('z', default='Z = {}', rounding=2)
        self.infobox.add('θx', default='θx = {}', rounding=2)
        self.infobox.add('θz', default='θz = {}', rounding=2)
        self.infobox.add('fps', default='FPS: {}', rounding=1)
        self.infobox.add('min', default='min {}ms', rounding=1)
        self.infobox.add('frame', default='avg {}ms', rounding=1)
        self.infobox.add('max', default='max {}ms', rounding=1)

        self.canvas.bind_all('<w>', self.move_input)
        self.canvas.bind_all('<a>', self.move_input)
        self.canvas.bind_all('<s>', self.move_input)
        self.canvas.bind_all('<d>', self.move_input)
        self.canvas.bind_all('<q>', self.move_input)
        self.canvas.bind_all('<space>', self.move_input)

        self.canvas.bind_all('<j>', self.turn_input)
        self.canvas.bind_all('<l>', self.turn_input)
        self.canvas.bind_all('<i>', self.turn_input)
        self.canvas.bind_all('<k>', self.turn_input)
        self.canvas.bind('<Motion>', self.turn_input)

        self.canvas.bind_all('<p>', self.toggle_motion)
        self.canvas.bind_all('<Escape>', self.toggle_motion)
        self.canvas.bind_all('<Leave>', self.pause_motion)
        self.canvas.bind_all('<Control-r>', self.reset_camera)
        self.canvas.bind_all('<Control-q>', self.quit)

    @property
    def fps(self):
        return 1000 / (self.time_one + self.refresh)

    def start(self):
        self.draw()
        self.root.mainloop()

    def draw(self):
        t = time.time()
        self.canvas.delete('clearable')

        self.camera.turn(*self.mouse_to_angles())  # stick mouse in the middle
        self.root.event_generate(
            '<Motion>',
            warp=True,
            x=self.w2,
            y=self.h2
        )
        self.mouse = [0, 0]

        converted_points = []

        for v in self.shape.points:
            converted = projection(v, self.camera, self.centre)
            converted_points.append(converted)
#            draw_circle(converted, 3-v._value[2], canvas, 'red')

        faces = []
        for face in self.shape.faces:
            cam_to_face = face.centre - self.camera.pos
            if self.camera.view.dot(cam_to_face) <= 0:
                # skip if face behind the camera
                continue
            if face.direction.dot(-cam_to_face) <= 0:
                # skip if camera is behind face
                continue
            faces.append(face)
        faces = sorted(  # sort faces by distance of centre from camera
            faces,
            key=lambda f: (f.centre - self.camera.pos).length,
            reverse=True
        )

        for face in faces:
            for tri in face.tri_iter():
                shade_rating = -(SUN_VECTOR @ face.direction)
                shade_adj = self.shader.shade(shade_rating)
                self.canvas.create_polygon(
                    *(converted_points[p]._value for p in tri),
                    tag='clearable',
                    fill=face.colour.adjust_value(shade_adj).hx
                    #outline='black',
                )

            continue
            draw_circle(projection(face.centre,self.camera,self.centre),2,self.canvas, face.colour)
            self.canvas.create_line(
                *projection(face.centre, self.camera, self.centre)._value,
                *projection(face.centre+face.direction, self.camera, self.centre)._value,
                tag='clearable',
            )

        self.shape.transform(obj_rotator)  # yo linear algebra works

        self.counter += 1
        self.update_text()
        dur = (time.time() - t) * 1000
        self.time_tot += dur
        if dur < self.time_min:
            self.time_min = dur
        elif dur > self.time_max:
            self.time_max = dur

        if self.counter%5 == 0:
            self.time_one = dur

        if not self.paused:
            self.root.after(self.refresh, self.draw)

    def turn_input(self, event):
        """Handles tk events for turning (mouse and keyboard)."""
        if self.paused:
            return
        if event.type == EventType.Motion:  # handle mouse movement
            if (event.x, event.y) != self.centre._value:
                self.mouse[0] += event.x - self.centre._value[0]
                self.mouse[1] += event.y - self.centre._value[1]
        elif event.type == EventType.Key:  # handle key presses
            v = self.KEY_BINDINGS.get(event.char)
            v *= pi / 64  # TODO make sensitivity?
            self.camera.turn(*v._value)

    def move_input(self, event):
        """Handles tk events for moving."""
        if self.paused:
            return
        v = self.KEY_BINDINGS.get(event.char)
        self.camera.move(v)

    def mouse_to_angles(self):  # move to Camera? Doesn't use tk.
        """Converts mouse position to x and z angles in radians."""
        mx, my = self.mouse
        self.mouse = [0,0]
        x_angle = -my * pi / 1000  # TODO make denominator the sensitivity?
        z_angle = -mx * pi / 1000  # mx < 0  <=>  delta θz > 0
        return x_angle, z_angle

    def update_text(self):
        """Updates InfoBox."""
        self.infobox.draw(  # fill these lines automatically?
            self.camera.pos._value[0],
            self.camera.pos._value[1],
            self.camera.pos._value[2],
            self.camera.x_angle,
            self.camera.z_angle,
            self.fps,
            self.time_min,
            self.time_tot / self.counter,
            self.time_max,
        )

    def pause_motion(self, *args):
        """Pauses app. Allows tk Event arguments."""
        if not self.paused:
            self.toggle_motion()  # keep the pause code in one place

    def toggle_motion(self, *args):
        """Toggles app pause. Allows tk Event arguments."""
        self.paused = not self.paused
        self.root.config(cursor=CURSOR_VIS[self.paused])
        self.canvas.itemconfig(self.paused_text, text=PAUSE_TEXT[self.paused])
        if not self.paused:
            self.draw()

    def quit(self, *args):
        self.root.destroy()

    def reset_camera(self, *args):
        """Creates new Camera, resetting position and angles. Allows tk Event arguments."""
        self.camera = Camera()  # TODO add a way of resetting to non-standard camera?


myShape = ShapeCombination(
    Cube(V([0,0,0])),
    Cube(V([0,0,1])),
    SquarePyramid(V([0,0,2])),
    Cube(V([2,0,0])),
    Cube(V([2,0,1])),
    SquarePyramid(V([2,0,2])),
    Cube(V([1,0,1])),
    shift=V([-1.5,-0.5,-1.5]),
)
myShape_ = Octagon(V([0,0,0]))  # v pretty

if __name__ == '__main__':
    root = Tk()
    canvas = Canvas(root)

    window = Window(root, canvas, myShape)
    window.start()
