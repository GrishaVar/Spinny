from tkinter import Tk, Canvas, Frame, BOTH
from math import sin, cos, pi

width = 1024
height = 576
c = (width/2, height/2)
pos = [0,0,0]
movement = {
    'w': (0,0,1),
    'a': (-1,0,0),
    's': (0,0,-1),
    'd': (1,0,0),
    ' ': (0,1,0),
    'q': (0,-1,0),
    }

def vector_add(v1, v2):
    if len(v1) != len(v2):
        raise ValueError('not cool man')
    return [x1+x2 for x1,x2 in zip(v1,v2)]

def scalar_multiply(a, matr):
    if isinstance(matr[0], list) or isinstance(matr[0], tuple):  # is matrix
        return [[a*j for j in matr] for i in matr]
    return [a*i for i in matr]  # else: is vector
 
def matrix_multiply(matr, vect):
    if len(matr[0]) != len(vect):  # pretend vector is vertical
        raise ValueError('wtf yo')
    res = [0 for x in range(len(matr))]
    for i in range(len(matr)):
        thiscoord = 0
        for j in range(len(vect)):
            thiscoord += matr[i][j]*vect[j]
        res[i] = thiscoord
    #print(str(vect) + ' => ' + str(res) + '\n')
    return res

# normal square pyramid
start_points = [(1,0,0), (0,0,-1), (-1,0,0), (0,0, 1), (0,1,0)]
start_lines = [
    (0,1), (1,2), (2,3), (3,0),  # base
    (0,4), (1,4), (2,4), (3,4)]  # top

angle = pi/32  # very small angle
rotator = [  # y unchanged, x and z move along a circle
    [cos(angle), 0, -sin(angle)],
    [0, 1, 0],
    [sin(angle), 0, cos(angle)],
]

grower = [  # x,z unchanged, y gets a little smaller
    [1, 0, 0],
    [0, 0.95, 0],
    [0, 0, 1],
]

# LA skript: matrix multiplication is associative!
# You can multiply these matrices to get both effects.

root = Tk()
root.geometry('{}x{}'.format(width, height))

canvas = Canvas(root)
canvas.pack(fill=BOTH, expand=1)

def draw_circle(x, y, r, canvas_name, color='black'):  # stolen code
    x0 = x - r
    y0 = y - r
    x1 = x + r
    y1 = y + r
    return canvas_name.create_oval(x0, y0, x1, y1, fill=color)

def projection(x,y,z):  #https://en.wikipedia.org/wiki/3D_projection

    x -= pos[0]
    y -= pos[1]
    z -= pos[2]
    
    sx = 1/(z+5)  # shift z forwards, away from the view. Use reciprocal to scale down with increased z
    sy = 1/(z+5)
    sx *= 800  # zoom way in (original pyramid is tiny)
    sy *= -800  # tk has height wrong way around I think
    res = matrix_multiply([[sx,0,0],[0,sy,0]], (x,y,z))  # different from wiki one because z is my depth
    res = vector_add(res, c)  # move to the middle
    return res

def myDraw(points, lines):
    canvas.delete('all')
    
    converted_points = []
    
    for x,y,z in points:
        converted = projection(x,y,z)
        converted_points.append(converted)

        draw_circle(*converted, 2, canvas, 'red')

    for p1, p2 in lines:
        p1_coords = converted_points[p1]
        p2_coords = converted_points[p2]

        canvas.create_line(*p1_coords, *p2_coords)

    p = canvas.create_polygon(*converted_points[0], *converted_points[1], *converted_points[4])
    canvas.itemconfigure(p, fill='#603')

    new_points = [matrix_multiply(rotator, i) for i in points]  # yo linear algebra works

    root.after(50, lambda: myDraw(new_points, lines))

def move(event):
    global pos
    dx = scalar_multiply(0.05, movement[event.char])
    pos = vector_add(pos, dx)

#root.after(400, myDraw)
canvas.bind_all('<w>', move)
canvas.bind_all('<a>', move)
canvas.bind_all('<s>', move)
canvas.bind_all('<d>', move)
canvas.bind_all('<space>', move)
canvas.bind_all('<q>', move)
myDraw(start_points, start_lines)
root.mainloop()
