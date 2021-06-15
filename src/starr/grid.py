"""
a class for creating a regular grids
"""
import numpy as np
from starr.object_factory import generate_group

def calc_lattice_sites(origin, range, scaling):
    return np.arange(range[0], range[1]+1)+origin/scaling

def calc_local_unit_cell_width(lattice_sites, spacing, gradient, debug):
    #lattice_sites = np.arange(range[0], range[1]+1)+origin

    nominal_pitch = np.ones(lattice_sites.size)*spacing
    stretch_factor = (1.0+np.abs(lattice_sites)*gradient)
    stretch_factor[stretch_factor<0.] = 0.
    if debug:
        print("nominal_pitch: {}".format(nominal_pitch))
        print("stretch_factor: {}".format(stretch_factor))
        print("local uc: {}".format(nominal_pitch*stretch_factor))
    return nominal_pitch*stretch_factor

def calc_pitch_from_unit_cells(unit_cell_widths):
    local_pitches = np.zeros(unit_cell_widths.size-1)
    for i, unit_celL_with in enumerate(unit_cell_widths[:-1]):
        local_pitches[i] = 0.5*(unit_celL_with+unit_cell_widths[i+1])
    return local_pitches

def _accumulate_local_pitch(lattice_sites, local_pitch, nominal_pitch, debug=False):
    start_site = lattice_sites[0]
    start_pos = 0.
    if debug:
        print("local pitch: {}".format(local_pitch))
        print("lattice sites: {}".format(lattice_sites))
        print("lattice_sites size divisible by two:{}".format(lattice_sites.size % 2))
    for i, site in enumerate(lattice_sites):
        if site >= 0.:
            break
        if lattice_sites.size % 2 == 0 and np.abs(site)<1.0:
            if debug:
                print("minus half pitch")
            start_pos -= local_pitch[i]*0.5
            #start_pos -= nominal_pitch/8.
        else:
            if debug:
                print("minus full pitch")
            start_pos -= local_pitch[i]
        if debug:
            print("i: {}, site:{}, local_pitch:{}, start_pos:{}".format(i, site, local_pitch, start_pos))
    if debug:
        print("start pos: {}".format(start_pos))
    position = np.zeros(lattice_sites.size)
    position[0] = start_pos
    for i, lp in enumerate(local_pitch):
        position[i+1] = position[i]+lp
        if debug:
            print("position: {} ".format(position))
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

def convert_to_checkerboard(X, Y):
    checkers_x1 = X[::2, ::2]
    checkers_y1 = Y[::2, ::2]
    lattice_sites1 = np.vstack([checkers_x1.flatten(), checkers_y1.flatten()]).T

    checkers_x2 = X[1::2, 1::2]
    checkers_y2 = Y[1::2, 1::2]
    lattice_sites2 = np.vstack([checkers_x2.flatten(), checkers_y2.flatten()]).T

    lattice_sites = np.concatenate([lattice_sites1, lattice_sites2])
    return lattice_sites

class Grid():

    def __init__(self, origin, spacing, ranges, gradient=0., checkerboard=False,
                 debug=False):
        self.origin = origin
        self.spacing = spacing
        self.ranges = ranges
        self.gradient = gradient
        self.checkerboard = checkerboard
        self.lattice = None
        self.debug = debug
        self.build_grid()

    def build_grid(self):
        if np.abs(self.gradient)>0.:
            self.build_gradient_grid()
        else:
            self.build_regular_grid()
        self.order_blockwise_radially()

    def build_regular_grid(self):
        x = np.arange(self.ranges[0][0], (self.ranges[0][1]+1))*self.spacing + self.origin[0]
        y = np.arange(self.ranges[1][0], (self.ranges[1][1]+1))*self.spacing + self.origin[1]
        X, Y = np.meshgrid(x,y)
        if self.checkerboard:
            lattice_sites = convert_to_checkerboard(X, Y)
        else:
            lattice_sites = np.vstack([X.flatten(), Y.flatten()]).T
        unit_cells = np.ones((lattice_sites.shape[0],2))*self.spacing
        self.lattice_sites = lattice_sites
        self.unit_cells = unit_cells

    def plot(self, canvas, lattice_sites=True, unit_cells=True):
        if self.lattice is None:
            self._make_lattice(lattice_sites, unit_cells)
        #print(self.lattice)
        if unit_cells:
            self.lattice['unit_cells'].update(0., None, canvas)
        if lattice_sites:
            self.lattice['sites'].update(0., None, canvas)

    def _make_lattice(self, make_lattice_sites, make_unit_cells,
                      unit_cell_kws={}, lattice_site_kws={}):
        n_sites = self.lattice_sites.shape[0]
        self.lattice = {}
        #print(make_lattice_sites, make_unit_cells)
        if make_unit_cells:
            #unit_cell_kws = {}
            defaults = {'shape':'Rectangle',
                        'color':None, 'fill':False}
            for key, val in defaults.items():
                if key not in unit_cell_kws:
                    unit_cell_kws[key] = val

            unit_cell_kws['side_length_a'] = self.unit_cells[:, 0]
            unit_cell_kws['side_length_b'] = self.unit_cells[:, 1]
            unit_cell_kws['n_objects'] = n_sites
            unit_cells = generate_group(unit_cell_kws)
            for i_obj, obj in enumerate(unit_cells.objects):
                obj.position = self.lattice_sites[i_obj, :]
                obj.physics = None
            self.lattice['unit_cells'] = unit_cells

        if make_lattice_sites:
            #lattice_site_kws = {}
            defaults = {'shape':'Circle',
                        'color':'k'}
            for key, val in defaults.items():
                if key not in lattice_site_kws:
                    lattice_site_kws[key] = val
            lattice_site_kws['n_objects'] = n_sites
            max_unit_cell_width = np.max(np.linalg.norm(self.unit_cells,axis=1))
            lattice_site_kws['radius'] = np.ones(self.unit_cells.shape[0])*max_unit_cell_width*0.02
            lattice_sites = generate_group(lattice_site_kws)
            for i_obj, obj in enumerate(lattice_sites.objects):
                obj.position = self.lattice_sites[i_obj, :]
                obj.physics = None
            self.lattice['sites'] = lattice_sites

    def build_gradient_grid(self):

        lattice_sites_x = calc_lattice_sites(self.origin[0], self.ranges[0], self.spacing)
        lattice_sites_y = calc_lattice_sites(self.origin[1], self.ranges[1], self.spacing)
        if self.debug:
            print("lattice_sites_x: {}".format(lattice_sites_x))
        local_unit_cell_width_x = calc_local_unit_cell_width(lattice_sites_x, self.spacing, self.gradient, self.debug)
        local_unit_cell_width_y = calc_local_unit_cell_width(lattice_sites_y, self.spacing, self.gradient, self.debug)

        UCX, UCY = np.meshgrid(local_unit_cell_width_x, local_unit_cell_width_y)
        unit_cells = np.vstack([UCX.flatten(), UCY.flatten()]).T
        if self.debug:
            print("local_unit_cell_width_x: {}".format(local_unit_cell_width_x))

        local_pitch_x = calc_pitch_from_unit_cells(local_unit_cell_width_x)
        local_pitch_y = calc_pitch_from_unit_cells(local_unit_cell_width_y)
        if self.debug:
            print("local_pitch_x: {}".format(local_pitch_x))

        x = _accumulate_local_pitch(lattice_sites_x, local_pitch_x, self.spacing, debug=self.debug)
        y = _accumulate_local_pitch(lattice_sites_y, local_pitch_y, self.spacing, debug=self.debug)
        if self.debug:
            print("x: {}".format(np.round(x,2)))

        X, Y = np.meshgrid(x,y)
        if self.checkerboard:
            lattice_sites = convert_to_checkerboard(X,Y)
        else:
            lattice_sites = np.vstack([X.flatten(), Y.flatten()]).T
        self.lattice_sites = lattice_sites
        self.unit_cells = unit_cells

    def order_radially(self):
        R = np.zeros(len(self.lattice_sites))
        angle = np.zeros(len(self.lattice_sites))
        for ip, point in enumerate(self.lattice_sites):
            R[ip] = np.sqrt(point[0]**2 +point[1]**2)
            angle[ip] = np.angle(point[0]+1j*point[1])+np.pi*0.5
        ind = np.lexsort((angle,R))
        self.lattice_sites =  self.lattice_sites[ind]
        self.unit_cells = self.unit_cells[ind]

    def order_blockwise_radially(self):
        R = np.zeros(len(self.lattice_sites))
        angle = np.zeros(len(self.lattice_sites))
        for ip, point in enumerate(self.lattice_sites):
            R[ip] = np.max([np.abs(point[0]), np.abs(point[1])])
            angle[ip] = np.angle(point[0]+1j*point[1])+np.pi*(1./4.)-1e-5
            #print(point, R[ip], angle[ip])

        #print(angle)
        angle[angle<0.0] += 2*np.pi
        #print(angle)
        ind = np.lexsort((angle,R))
        self.lattice_sites =  self.lattice_sites[ind]
        self.unit_cells = self.unit_cells[ind]
