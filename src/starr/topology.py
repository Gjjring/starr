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

"""
def get_minimum_world_intersection(poly, world, plot_segements=False):
    obj2 = world.buffer
    poly1 = poly
    poly2 = obj2.geometry.polygon
    min_intersect = np.inf
    if poly1.intersects(poly2):
        difference = poly1.difference(poly2)
        if not difference.is_empty:
            boundary = difference.exterior
            min_intersect = minimum_edge_length(boundary, plot_segments=plot_segments)
    return min_intersect
"""

def get_minimum_intersection(poly1, poly2, plot_segments=False):
    min_intersect = np.inf
    if poly1.intersects(poly2):
        difference = poly1.difference(poly2)
        if not difference.is_empty:
            try:
                boundary = difference.exterior
            except AttributeError as exp:                
                raise exp
            min_intersect = minimum_edge_length(boundary, plot_segments=plot_segments)
    return min_intersect

#def get_minimum_side_length(poly):


class TopologySimulation(Simulation):


    def __init__(self, world_kws, fig=None, axes=None):
        super().__init__(world_kws, fig=fig, axes=axes)

    def group_intersects(self, group1, group2):
        union1 = make_union(self.object_groups[group1].objects)[0]
        union2 = make_union(self.object_groups[group2].objects)[0]
        valid_intersection = False
        if union1.intersects(union2):
            print(union1.intersection(union2))
            intersection = union1.intersection(union2)
            if (isinstance(intersection,shapely.geometry.Polygon) or
                isinstance(intersection,shapely.geometry.MultiPolygon)):
                valid_intersection = True
            elif isinstance(intersection, shapely.geometry.collection.GeometryCollection):
                all_poly = True
                for item in intersection:
                    if (not isinstance(intersection,shapely.geometry.Polygon) and
                        not isinstance(intersection,shapely.geometry.MultiPolygon)):
                        all_poly =False
                        break
                valid_intersection = all_poly
        return valid_intersection

    def get_minimum_feature_size_group(self, group):
        return self.get_minimum_feature_size_world_intersection(group)

    def get_minimum_feature_size_world_intersection(self, group='all', plot_segments=False):
        """
        For a group of objects, for all the members which interset the world
        boundary, get the minimum edge length of the difference between object
        and world buffer.

        If the group does not intersect the     bondary, or the intersection lies
        inside the boundary, returns np.inf

        This feature is not part of the physics simulation. It was written for
        screening finite element meshes for unphysically small values before
        they are attempted to be meshed.
        """
        if isinstance(group, int):
            obj_list = self.object_groups[group].objects
        else:
            obj_list = self.all_objects()
        #object_group = self.object_groups[group]
        min_size = np.inf
        union, multi_poly = make_union(obj_list)
        poly2 = self.world.buffer.geometry.polygon
        if multi_poly:
            for poly in union:
                distance = get_minimum_intersection(poly, poly2, plot_segments=plot_segments)
                if distance < min_size:
                    min_size = distance
        else:
            distance = get_minimum_intersection(union, poly2, plot_segments=plot_segments)
            min_size = distance
        return min_size

    def get_minimum_feature_size_union(self, group='all', plot_segments=False):
        """
        For a group of objects, for all the members which interset the world
        boundary, get the minimum edge length of the difference between object
        and world buffer.

        If the group does not intersect the     bondary, or the intersection lies
        inside the boundary, returns np.inf

        This feature is not part of the physics simulation. It was written for
        screening finite element meshes for unphysically small values before
        they are attempted to be meshed.
        """
        if isinstance(group, int):
            obj_list = self.object_groups[group].objects
        else:
            obj_list = self.all_objects()
        #object_group = self.object_groups[group]
        min_size = np.inf
        union, multi_poly = make_union(obj_list)
        if multi_poly:
            for poly in union:
                distance = minimum_edge_length(poly.exterior, plot_segments=plot_segments)
                if distance < min_size:
                    min_size = distance
        else:
            exterior = union.exterior
            distance_exterior = minimum_edge_length(exterior, plot_segments=plot_segments)
            #interiors = union.interiors
            min_size = np.inf
            distance_interior = np.inf
            for poly in union.interiors:
                distance_interior = minimum_edge_length(poly, plot_segments=plot_segments)
                if distance_interior < min_size:
                    min_size = distance_interior
            min_size = np.min([distance_exterior, distance_interior])
        return min_size


    def get_minimum_feature_size_all(self):
        return self.get_minimum_feature_size_self_intersection(group='all')


    def get_minimum_feature_size_self_intersection(self, group='all'):
        """
        Make a union of all objects and check for intersections with the world
        boundary, get the minimum edge length of the difference between union
        and world buffer.

        This feature is not part of the physics simulation. It was written for
        screening finite element meshes for unphysically small values before
        they are attempted to be meshed.
        """
        min_size = np.inf
        if isinstance(group, int):
            all_objects = self.object_groups[group].objects
        else:
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
