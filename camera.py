from math import pi, atan

from matrix import Matrix as M, Vector as V
from common import M3


def projection(v, camera, centre):
    v -= camera.pos  # camera is basically the origin after this
    v = M3.z_rot(-camera.z_angle) * v  # rotate points on z-axis around camera
    v = M3.x_rot(-camera.x_angle) * v  # in the opposite direction

    sx = 1/v.length  # more distance => point closer to middle (?)
    sy = 1/v.length
    sx *= 800  # zoom way in (original pyramid is tiny)
    sy *= -800  # tk has y pointing down
    res = M((sx,0,0), (0,0,sy)) * v  # Apply transform from Q3 to Q2
    res += centre  # move to the middle
    return res


class Camera:
    def __init__(
        self,
        pos=V(0,-10,0),
        view=V(0,1,0),
        speed=0.1,
        rot_speed=pi/64,
    ):
        self.pos = pos
        self.view = view
        self.speed = speed
        self.rot_speed = rot_speed

    @property
    def x(self):
        return self.view.value[0]

    @property
    def y(self):
        return self.view.value[1]

    @property
    def z(self):
        return self.view.value[2]

    @property
    def z_angle(self):
        if not self.y:
            return pi  # think of better solution
        return atan(-self.x/self.y)  # negative x view is positive z rotation

    @property
    def x_angle(self):
        if not self.y:
            return pi
        return atan(self.z/self.y)

    def move(self, v):
        self.pos += v*self.speed

    def turn(self, rad_x, rad_z):
        # two M*v would be (3x) faster, but this is waay cooler
        rot_matrix = M3.x_rot(rad_x) * M3.z_rot(rad_z)
        self.view = rot_matrix * self.view

