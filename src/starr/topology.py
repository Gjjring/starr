"""
reimplement the Simulation class for performing topology based simulations in
which the minimum side length of objects with dynamic toplogy is determined.
This can be used for preprocessing finite element meshes in order to avoid
generating meshes with unrealistically small features.
"""
import shapely
import numpy as np
from starr.simulation import Simulation
from starr.geometry_component import minimum_edge_length, make_union

def get_minimum_world_intersection(poly, world):
    obj2 = world.buffer
    poly1 = poly
    poly2 = obj2.geometry.polygon
    min_intersect = np.inf
    if poly1.intersects(poly2):
        difference = poly1.difference(poly2)
        if not difference.is_empty:
            boundary = difference.exterior
            min_intersect = minimum_edge_length(boundary)
    return min_intersect

class TopologySimulation(Simulation):


    def __init__(self, world_kws, fig=None, axes=None):
        super().__init__(world_kws, fig=fig, axes=axes)


    def get_minimum_feature_size_group(self, group):
        """
        For a group of objects, for all the members which interset the world
        boundary, get the minimum edge length of the difference between object
        world buffer.

        If the group does not intersect the     bondary, or the intersection lies
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
        if isinstance(union, shapely.geometry.polygon.Polygon):
            distance = get_minimum_world_intersection(union, self.world)
            if distance < min_size:
                min_size = distance
        elif isinstance(union, shapely.geometry.multipolygon.MultiPolygon):            
            for poly in union:
                distance = get_minimum_world_intersection(poly, self.world)
                if distance < min_size:
                    min_size = distance




        #all_groups = self.object_groups + [buffer_group]


        return min_size
