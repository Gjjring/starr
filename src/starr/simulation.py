"""
A class for running physics based mechanics simulations
"""

import random
import itertools
import numpy as np
import matplotlib.colors
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from random import uniform, seed
from starr.canvas import Canvas
from starr.world import World
from starr.simulation_object import ObjectGroup
from starr.geometry_component import Circle, minimum_edge_length, make_union
from starr.object_factory import generate_group
from starr.misc import (square_number_ceil, plot_vector,
                                 order_blockwise_radially, create_regular_grid)


def get_color_list(n_colors):
    paired = cm.get_cmap('Paired', n_colors)
    color_list = []
    for row in range(n_colors):
        color_list.append(matplotlib.colors.to_hex(paired.colors[row, :]))
    return color_list

def get_color_map():
    return cm.get_cmap('magma')

class Simulation():

    def __init__(self, world_kws, fig=None, axes=None):
        self.object_groups = []
        self.world = self.make_world(world_kws)
        if fig is not None and axes is not None:
            self.canvas = self.make_canvas(fig, axes)
            self.world.plot(self.canvas)
        else:
            self.canvas = None
        #self.make_objects(object_kws)
        #self.arange_regular_grid(object_kws)
        self.simuset_number = 1



    def set_seed(self, seed):
        random.seed(seed)

    def make_canvas(self, fig, axes):
        return Canvas(fig, axes)

    def make_world(self, keys):
        world = World(keys, shape=keys['shape'], type= keys['type'])
        return world

    """
    def calc_n_particles(self, density, radius):
        domain_area = self.domain_area
        particle_area = np.pi*particle_radius**2
        n_particles = int(np.floor(density*domain_area/particle_area))
    """
    def make_objects(self, object_kws, group_objects=False):
        if "target_density" in object_kws:
            target_density = object_kws['target_density']
            density = 0.0
            n_particles = 0
            domain_area = self.world.boundary.geometry.area()
            object_kws['n_objects'] = 1
            colors = get_color_list(8)
            while density < target_density:
                object_kws['color'] = colors[n_particles]
                new_obj_group = generate_group(object_kws)
                new_obj_group.update(0.0, self.world, self.canvas)
                area = new_obj_group.objects[0].geometry.area()
                self.object_groups.append(new_obj_group)
                density += area/domain_area
                n_particles += 1
                if n_particles % 8 == 0:
                    colors += colors
            print(n_particles)
            print(density)
            self.n_particles = n_particles
        else:
            n_particles = object_kws['n_particles']
            colors = get_color_list(n_particles)
            self.n_particles = n_particles

            if group_objects:
                object_kws['n_objects'] = n_particles
                #for i_particle in range(n_particles):
                #object_kws['color'] = colors[i_particle]
                new_obj_group = generate_group(object_kws)
                new_obj_group.update(0.0, self.world, self.canvas)
                self.object_groups.append(new_obj_group)
            else:
                object_kws['n_objects'] = 1
                for i_particle in range(n_particles):
                    object_kws['color'] = colors[len(self.object_groups)]
                    new_obj_group = generate_group(object_kws)
                    new_obj_group.update(0.0, self.world, self.canvas)
                    self.object_groups.append(new_obj_group)


    def get_minimum_feature_size_group(self, group):
        """
        For a group of objects, for all the members which interset the world
        boundary, get the minimum edge length of the difference between object
        world buffer.

        If the group does not intersect the bondary, or the intersection lies
        inside the boundary, returns np.inf

        This feature is not part of the physics simulation. It was written for
        screening finite element meshes for unphysically small values before
        they are attempted to be meshed.
        """
        object_group = self.object_groups[group]
        min_size = np.inf
        for obj1 in object_group.objects:
            #buffer_group = ObjectGroup()
            #if self.world.buffer is not None:
            #    buffer_group.append(self.world.buffer)
            #all_groups = self.object_groups + [buffer_group]
            obj2 = self.world.buffer
            poly1 = obj1.geometry.polygon
            poly2 = obj2.geometry.polygon
            if poly1.intersects(poly2):
                save_pos1 = obj1.position
                save_pos2 = obj2.position
                difference = poly1.difference(poly2)
                if difference.is_empty:
                    continue
                boundary = difference.boundary
                distance = minimum_edge_length(boundary)
                if distance < min_size:
                    min_size = distance

        return min_size

    def get_minimum_feature_size_all(self):
        """
        Make a union of all objects and check for intersections with the world
        boundary, get the minimum edge length of the difference between union
        and world buffer.

        This feature is not part of the physics simulation. It was written for
        screening finite element meshes for unphysically small values before
        they are attempted to be meshed.
        """
        min_size = np.inf
        all_objects =[]
        for group in self.object_groups:
            all_objects += group.objects
        #object_group = self.object_groups[group]
        union = make_union(all_objects)
        #all_groups = self.object_groups + [buffer_group]
        obj2 = self.world.buffer
        poly1 = union
        poly2 = obj2.geometry.polygon
        if poly1.intersects(poly2):
            difference = poly1.difference(poly2)
            if difference.is_empty:
                return min_size
            boundary = difference.exterior
            distance = minimum_edge_length(boundary)
            if distance < min_size:
                min_size = distance

        return min_size


    def arange_regular_grid(self, grid_kws, group='all'):
        #n_rows = square_number_ceil(self.n_particles)
        spacing = grid_kws['grid_spacing']
        if "origin" in grid_kws:
            origin = grid_kws['origin']
        else:
            origin = (0., 0.)
        if 'range' in grid_kws:
            ranges = grid_kws['range']
        else:
            ranges = self.world.boundary.geometry.get_regular_grid_ranges(origin, spacing)
            #grid = self.world.boundary.geometry.create_regular_grid(origin, spacing)
        grid = create_regular_grid(origin, spacing, ranges)
        grid = order_blockwise_radially(grid)
        total_particles = 0
        if group == 'all':
            total_groups = np.inf
            current_group = 0
        else:
            total_groups = 1
            current_group = group
        total_area = 0.0
        for row in range(grid.shape[0]):
            if total_particles == self.n_particles:
                break
            group = self.object_groups[current_group]
            for ig, obj in enumerate(group.objects):
                #obj = self.object_groups[row].objects[0]
                obj.position = grid[total_particles, :]
                obj.update(0.0, self.world, self.canvas)
                total_area += obj.geometry.area()
                total_particles += 1
            if current_group == total_groups:
                break
            current_group += 1



    def init_velocity(self, object_kws):
        for group in self.object_groups:
            obj = group.objects[0]
            velocity = object_kws['velocity']
            angle = uniform(0.0, 2*np.pi)
            #angle = 0.0
            velocity_x = velocity*np.cos(angle)
            velocity_y = velocity*np.sin(angle)
            v_init = np.array([velocity_x, velocity_y])
            obj.physics.velocity = v_init

    def run(self, object_kws, sim_kws, seed=None):
        if seed is not None:
            self.set_seed(seed)
        self.init_velocity(object_kws)
        min_steps = sim_kws['min_steps']
        max_steps = sim_kws['max_steps']
        time_step = sim_kws['time_step']
        valid_finish = False
        self.i_step = 0
        distance = object_kws['velocity']*sim_kws['time_step']
        try:
            self.canvas.saving()
            self.canvas.write()
            while not valid_finish:
                if self.i_step % 10 == 0:
                    print(self.i_step)
                """
                collision_pair = self.detect_first_collision(time_step)
                if collision_pair is not None:
                    time_step = self.seek_collision_time()
                    #self.calculate_collisions()
                    self.calculate_collision(collision_pair)
                else:
                    time_step =
                """
                self.calculate_collisions()

                for group in self.object_groups:
                    group.update(time_step, self.world, self.canvas)

                self.world.update(self.object_groups)

                [time_step,v_max] = self.report_diags(distance)

                self.recolor_groups(v_max)
                #time_step = distance/max_v

                if self.i_step >= min_steps:
                    valid_finish = self.valid_configuration()
                if self.i_step == max_steps:
                    valid_finish = True

                self.canvas.write()
                self.i_step += 1
        finally:
            self.canvas.finish()

    def detect_first_collision(time_step):
        buffer_group = ObjectGroup()
        if self.world.buffer is not None:
            buffer_group.append(self.world.buffer)
        all_groups = self.object_groups + [buffer_group]
        test_time_step = time_step
        for group1, group2 in itertools.combinations(all_groups, 2):
            for obj1 in group1.objects:
                for obj2 in group2.objects:
                    poly1 = obj1.geometry.polygon
                    poly2 = obj2.geometry.polygon
                    if poly1.intersects(poly2):
                        save_pos1 = obj1.position
                        save_pos2 = obj2.position
                        intersection = poly1.intersection(poly2)
                        interestion_area = intersection.area
                        while interestion_area > obj1.area*1e-2:
                            test_time_step = -0.5* test_time_step
                            trans1 = test_time_step*obj1.physics.velocity
                            trans2 = test_time_step*obj2.physics.velocity
                            poly1 = poly1.affinity.translate()
                            obj1.translate( )
                            obj2.translate( test_time_step*obj2.physics.velocity)

                            new_area = poly1.intersection(poly2)


                        intersection = poly1.intersection(poly2)
                        center = intersection.centroid
                        collision = np.array([center.x, center.y])
                        normal1 = obj1.geometry.get_normal(collision)
                        normal2 = obj1.geometry.get_normal(collision)
                        """
                        if not self.valid_collision(normal1, normal2,
                                                    obj1.physics,
                                                    obj2.physics):
                            # not working well
                            continue
                        """

                        #for obj11 in group1.objects:
                        obj1.physics.collision(obj2.physics, normal1)
                        #for obj22 in group2.objects:
                        obj2.physics.collision(obj1.physics, normal2)


    def recolor_groups(self, v_max):
        cmap = get_color_map()
        for group in self.object_groups:
            v_group = np.linalg.norm(group.objects[0].physics.velocity)
            color = cmap( v_group/v_max )
            for obj in group.objects:
                obj.graphics.color = color




    def report_diags(self, distance):
        total_energy = 0.0
        total_momentum = np.zeros(2)
        n_groups = len(self.object_groups)
        max_v = 0.0
        for group in self.object_groups:
            total_energy += group.get_energy()/n_groups
            total_momentum += group.get_momentum()/n_groups
            group_v = group.get_velocity()
            if group_v > max_v:
                max_v = group_v
        time_step = distance / max_v
        self.canvas.report( [("i",self.i_step),
                             ('E',total_energy),
                             ('M_x',total_momentum[0]),
                             ('M_y', total_momentum[1]),
                             ('V_max',max_v),
                             ('t',time_step*1e6)])
        return [time_step, max_v]


    def calculate_collisions(self):
        buffer_group = ObjectGroup()
        if self.world.buffer is not None:
            buffer_group.append(self.world.buffer)
        all_groups = self.object_groups + [buffer_group]
        for group1, group2 in itertools.combinations(all_groups, 2):
            for obj1 in group1.objects:
                for obj2 in group2.objects:
                    poly1 = obj1.geometry.polygon
                    poly2 = obj2.geometry.polygon
                    if poly1.intersects(poly2):
                        intersection = poly1.intersection(poly2)
                        center = intersection.centroid
                        collision = np.array([center.x, center.y])
                        normal1 = obj1.geometry.get_normal(collision)
                        normal2 = obj1.geometry.get_normal(collision)
                        """
                        if not self.valid_collision(normal1, normal2,
                                                    obj1.physics,
                                                    obj2.physics):
                            # not working well
                            continue
                        """

                        #for obj11 in group1.objects:
                        obj1.physics.collision(obj2.physics, normal1)
                        #for obj22 in group2.objects:
                        obj2.physics.collision(obj1.physics, normal2)

    def valid_collision(self, normal1, normal2, physics1, physics2):

        #condition1 = not (np.dot(physics1.velocity, normal1) < 0.0 and
        #                  np.dot(physics2.velocity, normal2) < 0.0)

        condition1 = not (physics1.previous_collisions[0] == physics2 or
                          physics2.previous_collisions[0] == physics1)

        condition2 = physics1.static or physics2.static

        return condition1 or condition2


    def valid_configuration(self):
        for group1, group2 in itertools.combinations(self.object_groups, 2):
            for obj1 in group1.objects:
                for obj2 in group2.objects:
                    poly1 = obj1.geometry.polygon
                    poly2 = obj2.geometry.polygon
                    if poly1.intersects(poly2):
                        return False
        return True



"""
    def write_objects(self):
        data_rows = []
        for object in self.objects:
            if isinstance(object, Rectangle):
                continue
            data = [object.hradius, object.position[0], object.position[1]]
            data_rows.append(data)
        #data_array = np.array(data_rows).T
        #data_transposed = zip(data_rows)
        df = pd.DataFrame(data_rows, columns=['radius','x','y'])
        df.to_csv("ParticlePositions_{}.csv".format(self.simuset_number))


    def make_boundary(self):
        thickness = self.pitch*0.1
        width = self.pitch
        height = self.pitch
        angle = np.radians(90.0)
        anti_angle = np.pi*0.5 - angle

        r1 = Rectangle(np.array([0.0, 0.0]),
                       [width+thickness*2, thickness])
        #r1 = affinity.rotate(r1,60, origin='centroid')
        r1.translate([-0.5*width*np.cos(angle), -(thickness+height)*0.5*np.sin(angle) ])

        r4 = Rectangle(np.array([0.0, 0.0]),
                       [width+thickness*2, thickness])
        #r4 = affinity.rotate(r1,60, origin='centroid')
        r4.translate([0.5*width*np.cos(angle), (thickness+height)*0.5*np.sin(angle)])


        r2 = Rectangle(np.array([0.0, 0.0]),
                       [thickness, height+thickness*2])


        r2.translate([0.5*(width+thickness), 0.0])
        r2.rotate(-(90.0-np.degrees(angle)))

        r3 = Rectangle(np.array([0.0, 0.0]),
                       [thickness, height+thickness*2])

        r3.translate([-0.5*(width+thickness), 0.0])
        r3.rotate(-(90-np.degrees(angle)))



        self.objects += [r1, r2, r3, r4]






    def plot_frame(self):

        #self.boundary.plot(self.axes)
        for index,object in enumerate(self.objects):
            object.plot(self.axes)
        plt.text(-self.pitch*0.6,-self.pitch*0.6,"{}".format(self.i_step))
        self.axes.set_xlim(-self.pitch*0.6, self.pitch*0.6)
        self.axes.set_ylim(-self.pitch*0.6, self.pitch*0.6)
        #plt.show()

    def update_physics(self, time_delta):
        for index, object in enumerate(self.objects):
            object.update_physics(time_delta)

    def valid_configuration(self):
        for obj1, obj2 in itertools.combinations(self.objects,2):
            p = obj1.polygon
            q = obj2.polygon
            if isinstance(obj1, Rectangle) and isinstance(obj2, Rectangle):
                continue
            if obj1.intersects(obj2):
                return False
        return True

    def update_collisions(self, time_delta):
        for obj1, obj2 in itertools.combinations(self.objects,2):
            p = obj1.polygon
            q = obj2.polygon
            if isinstance(obj1, Rectangle) and isinstance(obj2, Rectangle):
                continue
            #if not obj1.collision_allowed(obj2) and not obj2.collision_allowed(obj1):
            #continue
            if obj1.intersects(obj2):
                intersection = p.intersection(q)
                #GRAY = '#999999'
                #ppatch = PolygonPatch(intersection,fc=GRAY, ec=GRAY, alpha=0.5, zorder=2)
                #self.axes.add_patch(ppatch)
                center = intersection.centroid
                self.calculate_collision(obj1, obj2,
                                         np.array([center.x, center.y]),
                                         time_delta)
                #obj1.add_collision(obj2)
                #obj2.add_collision(obj1)

                #plt.scatter(center.x,center.y,c='r',marker='x')
            else:
                pass
            #print(obj1.polygon.distance(obj2.polygon))
            #print(obj1._polygon.centroid)


    def calculate_collision(self,object1,object2,collision, time_delta):

        normal1 = object1.get_normal(collision)
        normal2 = object2.get_normal(collision)

        m1 = object1.mass
        m2 = object2.mass
        v1_init = object1.velocity
        v2_init = object2.velocity

        v1c_init = v1_init
        v2c_init = v2_init

        v12_init = v1c_init - v2c_init

        if ((np.dot(v1_init, normal1) < 0.0 or isinstance(object1,Rectangle)) and
            (np.dot(v2_init, normal2) < 0.0 or isinstance(object2,Rectangle))):
            return



        j = self.get_impulse(1.0, v12_init, normal1, m1, m2)

        object1.apply_force(j*normal1/m1/time_delta)
        object2.apply_force(-j*normal1/m2/time_delta)


    def get_impulse(self, e, v12_init, normal, m1, m2):
        numerator = -(1+e)* v12_init.dot(normal)
        denom = 1/m1 + 1/m2
        return numerator/denom

    def get_components(self, vel, dir):
        c = np.dot(vel,dir)/np.linalg.norm(vel)/np.linalg.norm(dir) # -> cosine of the angle
        angle = np.arccos(np.clip(c, -1, 1)) # if you really want the angle
        v_para = np.cos(angle)*np.linalg.norm(vel)
        v_perp = np.sin(angle)*np.linalg.norm(vel)
        return v_para, v_perp





    def elastic_collision(self,v1,m1,v2,m2):
        u1 = (m1-m2)/(m1+m2)*v1 + (2*m2)/(m1+m2)*v2
        u2 = (2*m1)/(m1+m2)*v1 + (m2-m1)/(m1+m2)*v2
        return (u1,u2)

"""





if __name__ == "__main__":
    #circle = Circle(1.0, [0., 0.])
    #circle.velocity = np.array([10.,10.0])
    #circle.acceleration = np.array([0.,-9.81])
    #fig,ax = plt.subplots(1,1)
    #s = Simulation(fig,ax)
    #s.init()
    #s.objects.append(circle)
    #s.run()
    pass