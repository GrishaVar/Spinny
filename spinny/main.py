#!/usr/bin/env python3

import time
from tkinter import Tk, Canvas, BOTH
from math import pi

from spinny.shapes import ShapeCombination, Cube, SquarePyramid, Octagon, StickMan
from spinny.matrix import Vector as V
from spinny.common import M3
from spinny.camera import Camera, projection
from spinny.colour import Shader
from spinny.infobox import InfoBox


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


class Spinny:
    KEY_BINDINGS = {  # TODO make dynamic?
        'w': V([0,1,0]),
        'a': V([-1,0,0]),
        's': V([0,-1,0]),
        'd': V([1,0,0]),
        'space': V([0,0,1]),
        'q': V([0,0,-1]),
    }

    def __init__(self, root, shape):
        self.root = root
        self.shape = shape

        self.canvas = Canvas(self.root)
        self.camera = Camera()
        self.shader = Shader()

        self.root.title('Spinny')
        self.root.attributes('-fullscreen', True)
        self.root.update_idletasks()
        #self.root.geometry('{}x{}+0+0'.format(self.width, self.height))
        self.canvas.pack(fill=BOTH, expand=1)
        self.canvas.configure(background='black')

        self.width = self.root.winfo_width()
        self.height = self.root.winfo_height()

        self.centre = V([self.width//2, self.height//2])
        self.refresh = 30
        self.mouse = [0, 0]
        self.paused = False
        self.paused_text = self.canvas.create_text(
            self.centre[0],
            10,
            anchor='n',
            font='Arial 50',
            fill='white',
        )
        self.pause_motion()

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

        self._key_repeat_freq = 10
        self._key_repeat_pressed = {}
        for key in self.KEY_BINDINGS:
            self._key_repeat_pressed[key] = True
            self.canvas.bind_all('<KeyPress-{} >'.format(key), self.move_key_press)
            self.canvas.bind_all('<KeyRelease-{}>'.format(key), self.move_key_release)

        self.canvas.bind('<Motion>', self.turn_input)  # mouse
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
            x=self.centre[0],
            y=self.centre[1],
        )
        self.mouse = [0, 0]

        converted_points = []

        for v in self.shape.points:
            converted = projection(v, self.camera, self.centre)
            converted_points.append(converted)
            # draw_circle(converted, 3-v._value[2], canvas, 'red')

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
        """Handles tk events for mouse turning."""
        if self.paused:
            return

        if (event.x, event.y) != self.centre._value:
            self.mouse[0] += event.x - self.centre._value[0]
            self.mouse[1] += event.y - self.centre._value[1]

    def move_key_press(self, event):
        """Handles tk events for moving with keyboard."""
        # deals with keyboard repeat delay
        if self.paused:
            return

        key = event.keysym
        self.camera.move(self.KEY_BINDINGS[key])  # TODO .get with default zero maybe?

        if self._key_repeat_pressed[key]:
            self.root.after(self._key_repeat_freq, self.move_key_press, event)

    def move_key_release(self, event):
        key = event.keysym
        if self._key_repeat_pressed[key]:
            self._key_repeat_pressed[key] = False
            self.root.after(self._key_repeat_freq+1, self.move_key_release, event)
        else:
            self._key_repeat_pressed[key] = True

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
myShape = StickMan(V([-1/4,0,0]))

def start():
    root = Tk()
    spinny = Spinny(root, myShape)
    spinny.start()

