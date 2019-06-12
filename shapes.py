class Shape():
	DEFAULT_POINTS = [(0,0,0)]  # first points is the 'anchor'
	LINES = []

	def __init__(self, pos, outlined=False):
		self.pos = pos
		self.points = [for x,y,z in DEFAULT_POINTS]
	
	def move_to(pos):
		dx, dy, dz = pos
		cx, cy, cz = self.points[0][:]
		self.points = [(dx-cx, dy-cy, dz-cz) for x,y,z in self.points]
	
	def move_by(pos):
		dx, dy, dz = pos
		self.points = [(x+nx, y+dy, z+dz) for x,y,z in self.points]


class Cube(Shape):
	DEFAULT_POINTS = [
		(0,0,0), (0,0,1), (1,0,1), (1,0,0),
		(0,1,0), (0,1,1), (1,1,1), (1,1,0)]
	LINES = [
		(0,1), (1,2), (2,3), (3,0),
		(4,5), (5,6), (6,7), (7,4),
		(0,4), (1,5), (2,6), (3,7)]


class SquarePyramid(Shape):
	DEFAULT_POINTS = [
		(0,0,0), (0,0,1), (1,0,1), (1,0,0),
		(0.5, 1, 0.5)]
	LINES = [
		(0,1), (1,2), (2,3), (3,0),
		(0,4), (1,4), (2,4), (3,4)]
		
