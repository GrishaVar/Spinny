from matrix import Vector as V
from common import V3, M3


def conv(v):
    return V(*v)


class Shape():
    DEFAULT_POINTS = [V3.z]  # first points is the 'anchor'
    LINES = []
    FACES = []
    CENTRES = []
    COLOURS = []
    DIRECTIONS = []

    def __init__(self, shift=V3.z, trans=M3.e):
        self.reset()
        self.move_to(shift)
        self.transform(trans)

    @property
    def cur(self):  # anchor point
        return self.points[0]

    def reset(self):
        self.points = self.DEFAULT_POINTS[:]
        self.lines = self.LINES[:]
        self.faces = self.FACES[:]
        self.centres = self.CENTRES[:]
        self.colours = self.COLOURS[:]
        self.directions = self.DIRECTIONS[:]

    def move_to(self, pos):
        self.move_by(pos-self.cur)

    def move_by(self, pos):
        self.points = [v + pos for v in self.points]
        self.centres = [v + pos for v in self.centres]
        #self.directions = [v + pos for v in self.directions]

    def transform(self, m):  # apply matrix transform to all points
        self.points = [m * v for v in self.points]
        self.centres = [m * v for v in self.centres]
        self.directions = [m * v for v in self.directions]
        if m.det == 0:  # optimisation only needed if dimentions collapsed
            self.optimise()

    def optimise(self):  # remove duplicate points
        seen_vects = []
        changes = {}
        offset = 0
        for i, v in enumerate(self.points):
            for j, w in enumerate(seen_vects):  # O(n^2)?
                if v.value == w.value:
                    changes[i] = j
                    offset += 1
                    break
            else:
                seen_vects.append(v)
                changes[i] = i - offset
        self.points = seen_vects  # replace list with duplicates

        self.lines = [{changes[i], changes[j]} for i,j in self.lines]
        new_lines = []
        for l in self.lines:
            if len(l) == 2 and l not in new_lines:
                new_lines.append(l)
        self.lines = new_lines  # remove duplicate lines

        self.faces = [set(map(changes.get, f)) for f in self.faces]
        new_faces = []
        new_centres = []
        new_colours = []
        new_directions = []
        for f,c,col,d in zip(self.faces, self.centres, self.colours, self.directions):
            if len(f) > 2 and f not in new_faces:
                new_faces.append(f)
                new_centres.append(c)
                new_colours.append(col)
                new_directions.append(d)
        self.faces = new_faces
        self.centres = new_centres
        self.colours = new_colours
        self.directions = new_directions


class ShapeCombination(Shape):
    def __init__(self, *shapes, shift=V3.z, trans=M3.e):
        self.reset()
        for shape in shapes:
            offset = len(self.points)
            f = lambda a: a + offset
            self.points += shape.points
            self.lines += [(i1+offset, i2+offset) for i1,i2 in shape.lines]
            self.faces += [tuple(map(f,x)) for x in shape.faces]
            self.centres += shape.centres
            self.colours += shape.colours
            self.directions += shape.directions
        self.optimise()
        self.move_to(shift)
        self.transform(trans)


class Cube(Shape):
    DEFAULT_POINTS = list(map(conv, (
        (0,0,0), (0,1,0), (1,1,0), (1,0,0),
        (0,0,1), (0,1,1), (1,1,1), (1,0,1),
    )))
    LINES = [
        {0,1}, {1,2}, {2,3}, {3,0},
        {4,5}, {5,6}, {6,7}, {7,4},
        {0,4}, {1,5}, {2,6}, {3,7}]
    FACES = [
        {0,1,2}, {0,2,3},
        {0,3,7}, {0,4,7},
        {2,3,6}, {3,6,7},
        {1,2,6}, {1,5,6},
        {0,1,5}, {0,4,5},
        {4,5,6}, {4,6,7},
    ]
    CENTRES = list(map(conv, (
        (1/3, 2/3, 0), (2/3, 1/3, 0),
        (2/3, 0, 1/3), (1/3, 0, 2/3),
        (1, 2/3, 1/3), (1, 1/3, 2/3),
        (2/3, 1, 1/3), (1/3, 1, 2/3),
        (0, 2/3, 1/3), (0, 1/3, 2/3),
        (1/3, 2/3, 1), (2/3, 1/3, 1),
    )))
    COLOURS = [
        'white', 'white',
        'red', 'red',
        'blue', 'blue',
        'orange', 'orange',
        'green', 'green',
        '#603', '#603',
    ]
    DIRECTIONS = list(map(conv, (
        (0,0,-1), (0,0,-1),
        (0,-1,0), (0,-1,0),
        (1,0,0), (1,0,0),
        (0,1,0), (0,1,0),
        (-1,0,0), (-1,0,0),
        (0,0,1), (0,0,1),
    )))


class SquarePyramid(Shape):
    DEFAULT_POINTS = list(map(conv, (
        (0,0,0), (0,1,0), (1,1,0), (1,0,0),
        (0.5, 0.5, 1),
    )))
    LINES = [
        {0,1}, {1,2}, {2,3}, {3,0},
        {0,4}, {1,4}, {2,4}, {3,4}]
    FACES = [
        {0,3,4}, {2,3,4}, {1,2,4}, {0,1,4},
        {0,1,2}, {0,2,3},
    ]
    CENTRES = list(map(conv, (
        (1/2, 1/6, 1/3),
        (5/6, 1/2, 1/3),
        (1/2, 5/6, 1/3),
        (1/6, 1/2, 1/3),
        (1/3, 2/3, 0), (2/3, 1/3, 0),
    )))
    COLOURS = [
        'red', 'blue', 'orange','green', 
        'white', 'white',
    ]
    DIRECTIONS = list(map(conv, (
        (0,-1,1/2),
        (1,0,1/2),
        (0,1,1/2),
        (-1,0,1/2),
        (0,0,-1), (0,0,-1),
    )))

