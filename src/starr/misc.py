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

def create_regular_grid(origin, spacing, ranges, gradient=0., debug=False):
    if np.abs(gradient) > 0.:
        return _create_regular_grid_with_gradient(origin, spacing, ranges,
                                                gradient, debug=debug)
    else:
        return _create_regular_grid(origin, spacing, ranges)

def calc_lattice_sites(origin, range, scaling):
    return np.arange(range[0], range[1]+1)+origin/scaling

def calc_local_unit_cell_width(lattice_sites, spacing, gradient):
    #lattice_sites = np.arange(range[0], range[1]+1)+origin
    nominal_pitch = np.ones(lattice_sites.size)*spacing
    stretch_factor = (1.0+np.abs(lattice_sites)*gradient)
    stretch_factor[stretch_factor<0.] = 0.
    return nominal_pitch*stretch_factor

def calc_pitch_from_unit_cells(unit_cell_widths):
    local_pitches = np.zeros(unit_cell_widths.size-1)
    for i, unit_celL_with in enumerate(unit_cell_widths[:-1]):
        local_pitches[i] = 0.5*(unit_celL_with+unit_cell_widths[i+1])
    return local_pitches

def accumulate_local_pitch(lattice_sites, local_pitch):
    start_site = lattice_sites[0]
    start_pos = 0.
    for i, site in enumerate(lattice_sites):
        if site >= 0.:
            break
        if lattice_sites.size % 2 == 0 and np.abs(site)<1.0:
            start_pos -= local_pitch[i]*0.5
        else:
            start_pos -= local_pitch[i]

    position = np.zeros(lattice_sites.size)
    position[0] = start_pos
    for i, lp in enumerate(local_pitch):
        position[i+1] = position[i]+lp
    return position

    """
    position = np.zeros(lattice_sites.size)
    for half_space in ['negative', 'positive']:
        position = _accumulate_half_space(position, lattice_sites, local_pitch, half_space)
    return position
    """

def _accumulate_half_space(position, lattice_sites, local_pitch, half_space):
    cum_pos = 0.
    if half_space == 'positive':
        iterator = enumerate(lattice_sites)
    else:
        iterator = enumerate(lattice_sites[::-1])
    print("half_space")
    print("local_pitch: {}".format(local_pitch))
    for i_site, site in iterator:
        print(i_site, site)
        if site <= 0:
            if half_space == 'positive':
                continue
            else:
                cum_pos -= (local_pitch[i_site] + local_pitch[i_site-1])*0.5
                print(-i_site-1, cum_pos)
                position[-i_site-1] = cum_pos
        elif site >= -1e-9:
            if half_space == 'negative':
                continue
            else:
                cum_pos += (local_pitch[i_site] + local_pitch[i_site-1])*0.5
                print(i_site, cum_pos)
                #print(i_site, cum_pos)
                position[i_site] = cum_pos
    return position

def _create_regular_grid_with_gradient(origin, spacing, ranges,
                                       gradient, debug=False):

    lattice_sites_x = calc_lattice_sites(origin[0], ranges[0], spacing)
    lattice_sites_y = calc_lattice_sites(origin[1], ranges[1], spacing)
    if debug:
        print("lattice_sites_x: {}".format(lattice_sites_x))
    local_unit_cell_width_x = calc_local_unit_cell_width(lattice_sites_x, spacing, gradient)
    local_unit_cell_width_y = calc_local_unit_cell_width(lattice_sites_y, spacing, gradient)
    if debug:
        print("local_unit_cell_width_x: {}".format(local_unit_cell_width_x))

    local_pitch_x = calc_pitch_from_unit_cells(local_unit_cell_width_x)
    local_pitch_y = calc_pitch_from_unit_cells(local_unit_cell_width_y)
    if debug:
        print("local_pitch_x: {}".format(local_pitch_x))

    x = accumulate_local_pitch(lattice_sites_x, local_pitch_x)
    y = accumulate_local_pitch(lattice_sites_y, local_pitch_y)
    if debug:
        print("x: {}".format(np.round(x,2)))

    X, Y = np.meshgrid(x,y)
    grid_points = np.vstack([X.flatten(),Y.flatten()]).T
    return grid_points

"""
    x = np.arange(ranges[0][0], (ranges[0][1]+1))*spacing + origin[0]
    if debug:
        print("x before stretch: {}".format(x))
    y = np.arange(ranges[1][0], (ranges[1][1]+1))*spacing + origin[1]

        #cumulative_x = np.zeros(x.size)
    max_grad_steps = int(np.abs(1./gradient))
    print("max_grad_steps: {}".format(max_grad_steps))
    #max_range_x = np.min((ranges[0][1], max_grad_steps))
    #min_range_x = np.max((ranges[0][0], -max_grad_steps))
    #max_range_y = np.min((ranges[1][1], max_grad_steps))
    #min_range_y = np.max((ranges[1][0], -max_grad_steps))

    max_range_x = ranges[0][1]
    min_range_x = ranges[0][0]
    max_range_y = ranges[1][1]
    min_range_y = ranges[1][0]

    print(min_range_x, max_range_x, min_range_y, max_range_y)
    all_lattice_sites_x = np.arange(ranges[0][0], ranges[0][1], dtype=np.double)
    all_lattice_sites_y = np.arange(ranges[1][0], ranges[1][1], dtype=np.double)
    all_lattice_sites_x += origin[0]/spacing
    all_lattice_sites_y += origin[1]/spacing


    masked_lattice_sites_x = np.arange(min_range_x, max_range_x, dtype=np.double)
    masked_lattice_sites_y = np.arange(min_range_y, max_range_y, dtype=np.double)
    masked_lattice_sites_x += origin[0]/spacing
    masked_lattice_sites_y += origin[1]/spacing

    if debug:
        print("lattice sites: {}".format(masked_lattice_sites_x))
    stretch_factor_x = (1.0+np.abs(masked_lattice_sites_x)*gradient)
    stretch_factor_y = (1.0+np.abs(masked_lattice_sites_y)*gradient)

    local_pitch_x = stretch_factor_x*spacing
    local_pitch_y = stretch_factor_y*spacing

    if debug :
        print("stretch factor x: {}".format(stretch_factor_x))
        print("local pitch x: {}".format(local_pitch_x))
    #stretch_factor_x = 1.0+np.abs(np.linspace(ranges[0][0], ranges[0][1], x.size)*gradient)
    #stretch_factor_y = 1.0+np.abs(np.linspace(ranges[1][0], ranges[1][1], y.size)*gradient)
    start_index_x = np.where(all_lattice_sites_x==np.min(masked_lattice_sites_x))[0][0]
    end_index_x = np.where(all_lattice_sites_x==np.max(masked_lattice_sites_x))[0][0]

    start_index_y = np.where(all_lattice_sites_y==np.min(masked_lattice_sites_y))[0][0]
    end_index_y = np.where(all_lattice_sites_y==np.max(masked_lattice_sites_y))[0][0]

    x = stretch_factor_x*x[start_index_x:end_index_x+1]
    y = stretch_factor_y*y[start_index_y:end_index_y+1]

    #print(start_index_x, end_index_x, start_index_y, end_index_y)
    x = np.zeros(masked_lattice_sites_x.size)
    y = np.zeros(masked_lattice_sites_y.size)
    cum_pos = 0.
    for i_site, site in enumerate(masked_lattice_sites_x):
        print(i_site, site)
        if site <= 0:
            continue
        else:
            cum_pos += (local_pitch_x[i_site] + local_pitch_x[i_site-1])*0.5
            print(i_site, cum_pos)
            x[i_site] = cum_pos
    cum_pos = 0.
    for i_site, site in enumerate(masked_lattice_sites_x[::-1]):
        print(i_site, site)
        if site >= -1e-9:
            continue
        else:
            print(i_site, cum_pos)
            print("local_pitch: {}, local_pitch+1: {}".format(local_pitch_x[i_site], local_pitch_x[i_site-1]))
            cum_pos -= (local_pitch_x[i_site] + local_pitch_x[i_site-1])*0.5
            x[-i_site-1] = cum_pos

    cum_pos = 0.
    for i_site, site in enumerate(masked_lattice_sites_y):
        if site <= 0:
            continue
        else:
            cum_pos += (local_pitch_y[i_site] + local_pitch_y[i_site-1])*0.5
            y[i_site] = cum_pos
    cum_pos = 0.
    for i_site, site in enumerate(masked_lattice_sites_y[::-1]):
        if site >= -1e-9:
            continue
        else:
            cum_pos -= (local_pitch_y[i_site] + local_pitch_y[i_site-1])*0.5
            y[-i_site-1] = cum_pos

    #x = stretch_factor_x*x[start_index_x:end_index_x+1]
    #y = stretch_factor_y*y[start_index_y:end_index_y+1]
    if debug:
        print("x:{}".format(np.round(x,3)))
        print("grad[x]: {}".format((x[1:]-x[:-1])))
#x = np.linspace(x0, y1, n_rows)
    #y = np.linspace(x0, y1, n_rows)
"""



def _create_regular_grid(origin, spacing, ranges):
    x = np.arange(ranges[0][0], (ranges[0][1]+1))*spacing + origin[0]
    y = np.arange(ranges[1][0], (ranges[1][1]+1))*spacing + origin[1]
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
