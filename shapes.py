from matrix import Vector as V
from common import V3, M3


class Face:
    def __init__(self, parent, direction, colour, *points):
        self.parent = parent
        self.direction = direction
        self.colour = colour
        self.points = points

        self.verts = len(self.points)
        self.centre = 1/self.verts * sum(
            self.parent.points[p] for p in self.points
        )

    def __eq__(self, other):
        return set(self.points) == set(other.points)

    def add_offset(self, offset):
        self.points = [p + offset for p in self.points]

    def move_by(self, pos):
        self.centre += pos

    def transform(self, m):
        self.direction = m * self.direction
        self.centre = m * self.centre

    def tri_points(self, i):
        return (
            self.points[0],
            self.points[i+1],
            self.points[i+2]
        )

    def tri_iter(self):
        return (self.tri_points(i) for i in range(self.verts-2))
    
    def copy(self):
        return Face(
            self.parent,
            self.direction,
            self.colour,
            *self.points,
        )


class Shape:
    POINTS = ((0,0,0),)  # first points is the 'anchor'
    FACES = ()

    def __init__(self, shift=V3.z, trans=M3.e):
        self.reset()
        self.move_to(shift)
        self.transform(trans)

    @property
    def cur(self):  # anchor point
        return self.points[0]

    def reset(self):
        self.points = [V(*v) for v in self.POINTS]
        self.faces = [Face(self, V(*d), col, *p) for d, col, p in self.FACES]

    def move_to(self, pos):
        self.move_by(pos-self.cur)

    def move_by(self, pos):
        self.points = [v + pos for v in self.points]
        for f in self.faces:
            f.move_by(pos)

    def transform(self, m):  # apply matrix transform to all points
        self.points = [m * v for v in self.points]
        for f in self.faces:
            f.transform(m)
        if m.det == 0:  # optimisation only needed if dimentions collapsed
            self.optimise()

    def optimise(self):  # remove duplicate points
        seen_vects = []
        changes = {}
        offset = 0
        for i, v in enumerate(self.points):
            for j, w in enumerate(seen_vects):  # O(n^2)?
                if v == w:
                    changes[i] = j
                    offset += 1
                    break
            else:
                seen_vects.append(v)
                changes[i] = i - offset
        self.points = seen_vects  # replace list with duplicates

        new_faces = []
        for face in self.faces:
            face.points = list(map(changes.get, face.points))
            if len(set(face.points)) < 3:
                continue
            if face in new_faces:
                i = new_faces.index(face)
                if face.direction != new_faces[i].direction:
                    del new_faces[i]
                continue

            new_faces.append(face)
        self.faces = new_faces


class ShapeCombination(Shape):
    def __init__(self, *shapes, shift=V3.z, trans=M3.e):
        self.reset()
        for shape in shapes:
            offset = len(self.points)
            self.points += shape.points
            for f in shape.faces:
                f.parent = self
                f.add_offset(offset)
            self.faces += shape.faces

        self.optimise()
        self.move_to(shift)
        self.transform(trans)


class Cube(Shape):
    POINTS = (
        (0,0,0), (1,0,0), (1,1,0), (0,1,0),
        (0,0,1), (1,0,1), (1,1,1), (0,1,1),
    )

    FACES = (
        ((0,0,-1), '#603', (0,1,2,3)),
        ((0,-1,0), 'red', (0,4,5,1)),
        ((1,0,0), 'blue', (1,5,6,2)),
        ((0,1,0), 'orange', (2,6,7,3)),
        ((-1,0,0), 'green', (3,7,4,0)),
        ((0,0,1), '#603', (4,7,6,5)),
    )


class SquarePyramid(Shape):
    POINTS = (
        (0,0,0), (1,0,0), (1,1,0), (0,1,0),
        (0.5, 0.5, 1),
    )
    FACES = (
        ((0,-1,1/2), 'red', (0,4,1)),
        ((1,0,1/2), 'blue', (1,4,2)),
        ((0,1,1/2), 'orange', (2,4,3)),
        ((-1,0,1/2), 'green', (3,4,0)),
        ((0,0,-1), '#603', (0,1,2,3)),
    )

