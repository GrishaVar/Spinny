from math import pi

from spinny.matrix import Matrix as M, Vector as V
from spinny.common import V3, M3


def projection(v, camera, centre):
    """
    Project 3D vector onto 2D screen.
    :param v: 3D Vector
    :param camera: Camera object
    :param centre: 2D Vector, centre of screen
    :return: 2D Vector, position on screen
    """
    v -= camera.pos  # camera is basically the origin after this
    v = M3.z_rot(-camera.z_angle) @ v  # rotate points on z-axis around camera
    v = M3.x_rot(-camera.x_angle) @ v  # in the opposite direction

    sx = 1/v._value[1]  # more distance => point closer to middle (?)
    sy = 1/v._value[1]
    sx *= 800  # zoom way in (original pyramid is tiny)
    sy *= -800  # tk has y pointing down
    res = M(((sx, 0, 0), (0, 0, sy))) @ v  # Apply transform from Q3 to Q2
    res += centre  # move to the middle
    return res


class Camera:
    """
    Stores camera position and angles.

    Supports turning on x and z axes and movement relative to view.

    rot_matrix(self) returns viewing direction as a rotation matrix.
    view(self) returns viewing direction as normalised vector.
    move(self, v) moves camera position relative viewing direction.
    turn(self, rad_x, rad_z) turns camera on x and z axes.

    pos: 3-Vector with position.
    x_angle: float, x rotation in radians.
    z_angle: float, z rotation in radians.
    speed: float, camera movement speed (arbitrary units).
    rot_speed: float, camera rotation speed (arbitrary units).
    """
    def __init__(
        self,
        pos=V((0.0, -10.0, 0.0)),
        angles=(0.0, 0.0),
        speed=0.1,
        rot_speed=pi/64,
    ):
        self.pos = pos
        self.x_angle, self.z_angle = angles
        self.speed = speed
        self.rot_speed = rot_speed

        self._rot_matrix = None
        self._view = None

        self.rot_matrix_outdated = False
        self.view_outdated = False

    @property
    def rot_matrix(self):
        """Return rotation matrix corresponding to camera's direction."""
        if self.rot_matrix_outdated or self._rot_matrix is None:
            mz = M3.z_rot(self.z_angle)
            mx = M3.x_rot(self.x_angle)
            self._rot_matrix = mz @ mx  # other way around doesn't work??? TODO
            self.rot_matrix_outdated = False
        return self._rot_matrix

    @property
    def view(self):
        """Return normalised vector pointing in camera's direction."""
        if self.view_outdated or self._view is None:
            self._view = self.rot_matrix @ V3.j  # j is the default orientation
            self.view_outdated = False
        return self._view

    def move(self, v):
        """
        Move camera position by a vector.

        Acts relative to camera direction.
        :param v: Vector
        """
        z = v.project((V3.k,))
        xy = v - z  # should be done in matrix but this is faster
        delta = (self.rot_matrix @ xy) + z  # up/down independent of view direction
        self.pos += self.speed * delta

    def turn(self, rad_x, rad_z):
        """
        Turns camera.
        :param rad_x: int, radians angle on x-axis (up-down)
        :param rad_z: int, radians angle on z-axis (left-right)
        """
        limit = pi/2
        if rad_z:
            self.z_angle += rad_z
            self.z_angle = self.z_angle % (2*pi)
            self.set_angle_update()
        if rad_x:
            self.x_angle += rad_x
            if self.x_angle > limit:
                self.x_angle = limit
            elif self.x_angle < -limit:
                self.x_angle = -limit
            self.set_angle_update()

    def set_angle_update(self):
        self.view_outdated = True
        self.rot_matrix_outdated = True

