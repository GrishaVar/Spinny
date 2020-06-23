from matrix import Vector as V
from common import V3, M3
from colour import Colour


class Face:
    """
    Stores face's vertices as indices of parent object and centre, direction as vectors.

    move_by(self, pos) allows moving the face centre's position.
    transform(self, m) allows matrix transformation of the centre and direction.
    tri_iter(self) returns generator of face indices broken up into triangles.

    parent: Shape object.
    direction: 3-Vector, face direction (faces are one-sided).
    colour: str, hex colour.
    points: list of vertex indices.
    verts: int, number of vertices.
    centre: 3-Vector, centre of face.
    """
    def __init__(self, parent, direction, colour, *points):
        self.parent = parent
        self.direction = direction
        self.colour = colour
        self.points = points  # indices, not vectors

        self.verts = len(self.points)
        self.centre = 1/self.verts * sum(
            self.parent.points[p] for p in self.points
        )

    def __eq__(self, other):
        return set(self.points) == set(other.points)

    def add_offset(self, offset):
        """
        Offset all indices in self.points by a number.
        :param offset: int
        """
        self.points = [p + offset for p in self.points]

    def move_by(self, pos):
        """
        Move face by an offset vector.
        :param pos: Vector
        """
        self.centre += pos

    def transform(self, m):
        """
        Preform linear matrix transformation on face.
        :param m: Matrix
        """
        self.direction = m @ self.direction
        self.centre = m @ self.centre

    def tri_points(self, i):
        return (
            self.points[0],
            self.points[i+1],
            self.points[i+2]
        )

    def tri_iter(self):
        """Returns generator of face's triangles."""
        return (self.tri_points(i) for i in range(self.verts-2))
    
    def copy(self):
        return Face(
            self.parent,
            self.direction,
            self.colour,
            *self.points,
        )


class Shape:
    """
    Stores vertices as Vectors and combines them with Face objects.

    move_to(self, pos) moves Shape to a location (using achor point).
    move_by(self, pos) moves Shape by a vector.
    transform(self, m) allows matrix transformation of each vertex.
    optimise(self) removes redundant vertices/faces.

    points: list of 3-Vectors, vertices of shape.
    faces: list of Faces.
    """
    POINTS = ([0,0,0],)  # first point is the 'anchor'   Why are these not in the init?
    FACES = ()

    def __init__(self, shift=V3.z, trans=M3.e):
        self.reset()
        self.move_to(shift)
        self.transform(trans)

    @property
    def cur(self):  # anchor point
        return self.points[0]

    def reset(self):
        """Creates Vector and Face objects from given tuples."""
        self.points = [V(v) for v in self.POINTS]
        self.faces = [Face(self, V(d), Colour(c), *p) for d, c, p in self.FACES]

    def move_to(self, pos):
        """
        Move Shape to a position.
        :param pos: Vector
        """
        self.move_by(pos-self.cur)

    def move_by(self, pos):
        """
        Move Shape by an offset.
        :param pos: Vector
        """
        self.points = [v + pos for v in self.points]
        for f in self.faces:
            f.move_by(pos)

    def transform(self, m):
        """
        Preform linear matrix transformation on shape.
        :param m: Matrix
        """
        self.points = [m@v for v in self.points]
        for f in self.faces:
            f.transform(m)
        if m.det == 0:  # optimisation only needed if dimentions collapsed
            self.optimise()

    def optimise(self):
        """Removes duplicate points and faces in the shape."""
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
    """Subclasses Shape, allows combining several shapes into one."""
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
        [0,0,0], [1,0,0], [1,1,0], [0,1,0],
        [0,0,1], [1,0,1], [1,1,1], [0,1,1],
    )

    FACES = (
        ([0,0,-1], 'byz', (0,1,2,3)),
        ([0,-1,0], 'red', (0,4,5,1)),
        ([1,0,0], 'blue', (1,5,6,2)),
        ([0,1,0], 'orange', (2,6,7,3)),
        ([-1,0,0], 'green', (3,7,4,0)),
        ([0,0,1], 'byz', (4,7,6,5)),
    )


class SquarePyramid(Shape):
    POINTS = (
        [0,0,0], [1,0,0], [1,1,0], [0,1,0],
        [0.5, 0.5, 1],
    )
    FACES = (
        ([0,-1,1/2], 'red', (0,4,1)),
        ([1,0,1/2], 'blue', (1,4,2)),
        ([0,1,1/2], 'orange', (2,4,3)),
        ([-1,0,1/2], 'green', (3,4,0)),
        ([0,0,-1], 'byz', (0,1,2,3)),
    )


class Octagon(Shape):
    POINTS = (
        [1, 1, 0], [1, 2, 0], [2, 2, 0], [2, 1, 0],
        [0, 0, 1], [0, 3, 1], [3, 3, 1], [3, 0, 1],
        [1, 1, 2], [1, 2, 2], [2, 2, 2], [2, 1, 2],
    )
    FACES = (
        ([0, 0, -1], 'red', (0,1,2,3)),
        ([-1, 0, -1], 'blue', (0,1,4,5)),
        ([0, 1, -1], 'yellow', (1,2,6,5)),
        ([1, 0, -1], 'orange', (2,3,7,6)),
        ([0, -1, -1], 'green', (0,3,7,4)),
        ([-1, 0, 1], 'cyan', (4,8,9,5)),
        ([0, 1, 1], 'lime', (5,9,10,6)),
        ([1, 0, 1], 'grey', (6,7,11,10)),
        ([0, -1, 1], 'pink', (8,4,7,11)),
        ([0, 0, 1], 'byz', (8,9,10, 11)),
    )

