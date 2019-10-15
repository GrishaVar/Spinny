from math import pi

from matrix import Matrix as M, Vector as V
from common import V3, M3


def projection(v, camera, centre):
    v -= camera.pos  # camera is basically the origin after this
    v = M3.z_rot(-camera.z_angle) * v  # rotate points on z-axis around camera
    v = M3.x_rot(-camera.x_angle) * v  # in the opposite direction

    sx = 1/v.length  # more distance => point closer to middle (?)
    sy = 1/v.length
    sx *= 800  # zoom way in (original pyramid is tiny)
    sy *= -800  # tk has y pointing down
    res = M((sx, 0, 0), (0, 0, sy)) * v  # Apply transform from Q3 to Q2
    res += centre  # move to the middle
    return res


class Camera:
    def __init__(
        self,
        pos=V(0, -10, 0),
        angles=(0, 0),
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
        if self.rot_matrix_outdated or self._rot_matrix is None:
            mz = M3.z_rot(self.z_angle)
            mx = M3.x_rot(self.x_angle)
            self._rot_matrix = mz * mx  # other way around doesn't work???
            self.rot_matrix_outdated = False
        return self._rot_matrix

    @property
    def view(self):  # returns camera viewing direction as a normalised vector
        if self.view_outdated or self._view is None:
            self._view = self.rot_matrix * V3.j  # j is the default orientation
            self.view_outdated = False
        return self._view

    def move(self, v):
        z = v.project((V3.k,))
        xy = v - z  # should be done in matrix but this is faster
        delta = (self.rot_matrix * xy) + z  # up/down independent of view direction
        self.pos += delta * self.speed

    def turn(self, rad_x, rad_z):
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

