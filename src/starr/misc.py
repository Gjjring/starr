import numpy as np
import itertools
from itertools import tee
import matplotlib.pyplot as plt


def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)

def square_number_ceil(number):
    root = np.sqrt(number)
    return int(np.floor(root))+1


def out_of_bounds(circle,rectangle):
    radius = circle.radius
    pos = rectangle.position
    outside = False
    sides = []
    # out of bounds in x
    if circle.position[0] + radius > pos[0] + rectangle.side_length_a:
        outside = True
        sides.append('right')
    elif circle.position[0] - radius < pos[0]:
        outside = True
        sides.append('left')
    # out of bounds in y
    if circle.position[1] + radius >pos[1] + rectangle.side_length_b:
        outside = True
        sides.append('upper')
    if circle.position[1] - radius < pos[1]:
        outside = True
        sides.append('lower')

    return (outside, sides)

def determine_collisions(test_circle,circle_list):
    collisions = []
    for circle in circle_list:
        if test_circle.touching(circle):
            collisions.append(circle)
    return collisions

def is_iterable(obj):
    return hasattr(type(obj), '__iter__') and not isinstance(obj, str)

def plot_vector(start, end, color):
    x = [start[0],end[0]]
    y = [start[1],end[1]]

    plt.plot(x,y,color=color,linewidth=2.0)

def create_regular_grid(origin, spacing, ranges):

    x = np.arange(ranges[0][0]*spacing, (ranges[0][1]+1)*spacing, spacing) + origin[0]
    y = np.arange(ranges[1][0]*spacing, (ranges[1][1]+1)*spacing, spacing) + origin[1]
    #x = np.linspace(x0, y1, n_rows)
    #y = np.linspace(x0, y1, n_rows)
    X, Y = np.meshgrid(x,y)
    grid_points = np.vstack([X.flatten(),Y.flatten()]).T
    return grid_points


def order_radially(points):
    R = np.zeros(len(points))
    angle = np.zeros(len(points))
    for ip, point in enumerate(points):
        R[ip] = np.sqrt(point[0]**2 +point[1]**2)
        angle[ip] = np.angle(point[0]+1j*point[1])+np.pi*0.5
    ind = np.lexsort((angle,R))
    return points[ind]

def order_blockwise_radially(points):
    R = np.zeros(len(points))
    angle = np.zeros(len(points))
    for ip, point in enumerate(points):
        R[ip] = np.max([np.abs(point[0]), np.abs(point[1])])
        angle[ip] = np.angle(point[0]+1j*point[1])+np.pi*(1./4.)-1e-5
        #print(point, R[ip], angle[ip])

    #print(angle)
    angle[angle<0.0] += 2*np.pi
    #print(angle)
    ind = np.lexsort((angle,R))
    return points[ind]
