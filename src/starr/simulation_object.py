import numpy as np
import copy
from starr.graphics_component import GraphicsComponent
class SimulationObject():
    #class for generating 2D regular objects
    def __init__(self, geometry, physics, graphics):
        self.name = ""
        self.position = np.zeros(2)
        self.rotation = 0.0
        self.geometry = geometry
        self.geometry.create_polygon(self.position, self.rotation)
        self.physics = physics
        self.graphics = graphics


    def update(self, time_step, world, canvas):
        if self.physics is not None:
            self.physics.update(self, world, time_step)
        if self.geometry is not None:
            self.geometry.update(self)
        if self.graphics is not None and canvas is not None:
            self.graphics.update(self.geometry, canvas)

    def copy(self):
        new_geo = copy.copy(self.geometry)
        new_phys = copy.copy(self.physics)
        new_graph = GraphicsComponent('g')
        print("own position: {}".format(self.position))
        print("own velocity: {}".format(self.physics.velocity))
        new = SimulationObject(new_geo, new_phys, new_graph)
        new.position = np.array(self.position)
        new.rotation = self.rotation
        print("new position: {}".format(new.position))
        print("new velocity: {}".format(new.physics.velocity))
        return new

    def translate(self, vector):
        self.position += vector
        """
        self._polygon.set(affinity.translate(self._polygon,
                                           xoff=vector[0],
                                           yoff=vector[1]))
        """

    def rotate(self, angle):
        self.rotation += angle
        """
        self._polygon = affinity.rotate(self._polygon, angle,
                                        origin='centroid')
        """


class ObjectGroup():
    """
    group of simulation objects which share a common physics component. These
    objects will not interact with each other, and an interaction with one of
    the objects will affect all of them.
    """

    def __init__(self):
        self.periodic = False
        self.objects = []

    def update(self, time_step, world, canvas):
        for i_obj, obj in enumerate(self.objects):
            obj.update(time_step, world, canvas)

    def append(self, obj):
        self.objects.append(obj)

    def remove(self, obj):
        self.objects.remove(obj)
        obj.graphics.remove()

    def get_energy(self):
        total_energy = 0.0
        n_objects = len(self.objects)
        for obj in self.objects:
            total_energy += obj.physics.kinetic_energy/n_objects
        return total_energy

    def get_momentum(self):
        total_momentum = 0.0
        n_objects = len(self.objects)
        for obj in self.objects:
            total_momentum += obj.physics.momentum/n_objects
        return total_momentum

    def get_velocity(self):
        return np.linalg.norm(self.objects[0].physics.velocity)
