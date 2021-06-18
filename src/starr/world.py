"""
A class that sets the boundaries of the 2D world for a physics based simulation
"""
import sys
import numpy as np
#from starr.geometry_component import Circle, Rectangle
from starr.object_factory import generate_object, object_from_polygon
from starr.simulation_object import SimulationObject
from starr.object_factory import clone

class World():

    def __init__(self, kwds, shape='Rectangle', boundary_type='Physical'):
        #self.shape = shape
        #self.boundary = self.create_geometrical_boundary(shape, kwds)
        if 'shape' not in kwds:
            kwds['shape'] = shape
        if 'boundary_type' not in kwds:
            kwds['boundary_type'] = boundary_type
        self.origin = np.zeros(2)
        self.buffer = None
        self.boundary = generate_object(kwds)
        self.boundary.static = True
        if 'color' not in kwds:
            self.boundary.graphics.color = 'w'
        else:
            self.boundary.graphics.color = kwds['color']
        self.boundary_type = boundary_type
        if boundary_type == "Physical":
            if 'buffer_thickness' not in kwds:
                kwds['buffer_thickness'] = 5.
            thickness = kwds['buffer_thickness']
            self.create_buffer(thickness)
        elif boundary_type == 'Periodic':
            self.set_periodic_conditions(kwds)
            #self.boundary.physics = None
            #self.create_physical_boundary(kwds)

    def create_buffer(self, thickness):
        buffer = self.boundary.geometry.make_buffer(thickness)
        self.buffer = object_from_polygon({'color':self.boundary.graphics.color}, buffer)        
        self.buffer.physics.mass = 1e21
        self.buffer.physics.static = True

    def plot(self, canvas):
        if self.buffer is not None:
            self.buffer.graphics.update(self.buffer.geometry,
                                        canvas)
        self.boundary.graphics.update(self.boundary.geometry,
                                      canvas)

    def update(self, object_groups):
        if self.boundary_type == 'Physical':
            pass
        elif self.boundary_type == 'Periodic':
            for group in object_groups:
                self.cleanup_group(group)
                    #continue
                #new_objects = []
                #for obj in group.objects:
                obj = group.objects[0]
                if self.out_of_bounds(obj):
                    #group.periodic = True
                    self.periodify_group(group)
                else:
                    pass
                #group.objects += new_objects
                """
                if len(group.objects) > 1:
                    positions = []
                    for obj in group.objects:
                        positions.append(obj.position)
                """
        #self.snap_edges(object_groups)

    def snap_edges(self, object_groups):
        overlaps = True
        pass

    def cleanup_group(self, group):

        for obj in group.objects:
            if obj.geometry.polygon.disjoint(self.boundary.geometry.polygon):
                center_vector = obj.position-self.origin
                if obj.physics.velocity.dot(center_vector) > 0.0:
                    group.remove(obj)
        if len(group.objects) == 1:
            group.periodic = False


    def out_of_bounds(self, obj):
        return not obj.geometry.polygon.within(self.boundary.geometry.polygon)

    def clone_exists(self, group, condition):
        obj_base = group.objects[0]
        for i_obj, obj in enumerate(group.objects):
            if i_obj == 0:
                continue
            new_pos = obj_base.position + condition
            if np.linalg.norm(new_pos - obj.position)< 1e-3:
                return True
        return False



    def periodify_group(self, group):
        obj = group.objects[0]
        diff = obj.geometry.polygon.difference(self.boundary.geometry.polygon)
        bounds = diff.bounds

        clones = []
        if bounds[0] < self.conditions['left']:
            if not self.clone_exists(group, self.conditions['left_to_right']):
                new = clone(obj)
                new.translate(self.conditions['left_to_right'])
                new.geometry.update(new)
                clones.append(new)
        elif bounds[2] > self.conditions['right']:
            if not self.clone_exists(group, -self.conditions['left_to_right']):
                new = clone(obj)
                new.translate(-self.conditions['left_to_right'])
                new.geometry.update(new)
                clones.append(new)

        if bounds[1] < self.conditions['down']:
            if not self.clone_exists(group, self.conditions['down_to_up']):
                new = clone(obj)
                new.translate(self.conditions['down_to_up'])
                new.geometry.update(new)
                clones.append(new)
        elif bounds[3] > self.conditions['up']:
            if not self.clone_exists(group, -self.conditions['down_to_up']):
                new = clone(obj)
                new.translate(-self.conditions['down_to_up'])
                new.geometry.update(new)
                clones.append(new)

        if (bounds[0] < self.conditions['left'] and
            bounds[1] < self.conditions['down']):
            if not self.clone_exists(group, self.conditions['left_to_right']+
                                            self.conditions['down_to_up']):
                new = clone(obj)
                new.translate(self.conditions['left_to_right']+
                              self.conditions['down_to_up'])
                new.geometry.update(new)
                clones.append(new)
        if (bounds[2] > self.conditions['right'] and
            bounds[1] < self.conditions['down']):
            if not self.clone_exists(group, -self.conditions['left_to_right']+
                                            self.conditions['down_to_up']):
                new = clone(obj)
                new.translate(-self.conditions['left_to_right']+
                            self.conditions['down_to_up'])
                new.geometry.update(new)
                clones.append(new)
        if (bounds[0] < self.conditions['left'] and
            bounds[3] > self.conditions['up']):
            if not self.clone_exists(group, self.conditions['left_to_right']-
                                            self.conditions['down_to_up']):
                new = clone(obj)
                new.translate(self.conditions['left_to_right']-
                          self.conditions['down_to_up'])
                new.geometry.update(new)
                clones.append(new)
        if (bounds[2] > self.conditions['right'] and
            bounds[3] > self.conditions['up']):
            if not self.clone_exists(group, -self.conditions['left_to_right']-
                                            self.conditions['down_to_up']):
                new = clone(obj)
                new.translate(-self.conditions['left_to_right']-
                            self.conditions['down_to_up'])
                new.geometry.update(new)
                clones.append(new)

        group.objects += clones


    def set_periodic_conditions(self, keys):
        sla = keys['side_length_a']
        slb = keys['side_length_b']
        self.conditions = {}
        self.conditions['left'] = -0.5*sla
        self.conditions['right'] = 0.5*sla
        self.conditions['left_to_right'] = np.array([sla, 0.])
        self.conditions['up'] = 0.5*slb
        self.conditions['down'] = -0.5*slb
        self.conditions['down_to_up'] = np.array([0., slb])


        """
            def create_geometrical_boundary(self, shape, kwds):


                boundary_shapes = {'Rectangle': Rectangle}

                boundary = boundary_shapes[shape](kwds)
                boundary.create_polygon(np.zeros(2), 0.0)
                return boundary
        """

        """
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
        """


        #self.objects += [r1, r2, r3, r4]





class PeriodicBody():

    def __init__(self, rigid_body, boundary):
        self.boundary = boundary
        self.base = rigid_body
