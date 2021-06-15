"""
Implements geometrical objects used for physics based mechanical simulations
Classes:
GeometryComponent(abstract)
Circle
Rectangle
GeneralPolygon

"""

import numpy as np
from abc import ABC, abstractmethod
import matplotlib.pyplot as plt
import shapely.geometry
from shapely.geometry.point import Point
from shapely.geometry.linestring import LineString
from shapely.geometry.polygon import LinearRing, Polygon
import shapely.affinity as affinity
from starr.misc import pairwise
from shapely.ops import unary_union

def plot_line_string(line_string, color='k'):
    x = [line_string.coords[0][0], line_string.coords[1][0]]
    y = [line_string.coords[0][1], line_string.coords[1][1]]
    plt.plot(x,y, lw=3.0, color=color, zorder=10)

def minimum_edge_length(polygon, plot_segments=False):
    min_size = np.inf
    #previous_point = Point(polygon.coords[-1])
    for ip, point_tuple in enumerate(polygon.coords):
        point = Point(point_tuple)
        if ip == 0:
            previous_point = point
            continue
        distance = point.distance(previous_point)
        if plot_segments:
            line_string = LineString([previous_point, point])
            plot_line_string(line_string, color='orange')
        if distance < min_size:
            min_size = distance
        previous_point = point
    return min_size

def make_union(object_list):
    all_polygons = []
    for obj in object_list:
        all_polygons.append(obj.geometry.polygon)
    union = unary_union(all_polygons)
    if isinstance(union, shapely.geometry.polygon.Polygon):
        multi_poly = False
    elif isinstance(union, shapely.geometry.multipolygon.MultiPolygon):
        multi_poly = True
    else:
        raise ValueError("unknown result of polygon union")
    return union, multi_poly



class GeometryComponent(ABC):

    def __init__(self):
        self._position = np.zeros(2)
        self._rotation = 0.0
        self.polygon = None

    def update(self, simulation_object):
        new_pos = simulation_object.position
        new_rot = simulation_object.rotation
        translation = new_pos-self._position
        rotation = new_rot-self._rotation
        self.polygon = affinity.translate(self.polygon,
                                          xoff=translation[0],
                                          yoff=translation[1])
        self.polygon = affinity.rotate(self.polygon,
                                       rotation)
        self._position = np.array(new_pos)
        self._rotation = new_rot

    @abstractmethod
    def create_polygon(self, position, rotation):
        pass

    def get_regular_grid_ranges(self, origin, spacing, include_edges=False):
        raise NotImplementedError("regular grid has not yet "+
                                  "been implemented")

    def intersects(self, other):
        return self.polygon.intersects(other.polygon)

    def intersection(self, other):
        return self.polygon.intersection(other.polygon)

    def make_buffer(self, thickness):
        inner = self.polygon
        outer = Polygon(inner.buffer(thickness).exterior)
        return outer.difference(inner)

    def area(self):
        return self.polygon.area

    def get_normal(self, collision):
        side = 0
        min_distance = np.inf
        collision_side = None
        for p0, p1 in pairwise(self.polygon.exterior.coords):
            line = LineString( [p0,p1])
            ring = LinearRing( [p0,p1,collision])
            poly = Polygon(ring)
            distance = poly.area/line.length
            if distance < min_distance:
                min_distance = distance
                collision_side = side
            side += 1

        points = self.polygon.exterior.coords[collision_side:collision_side+2]
        seg_vec = np.array(points[1])-np.array(points[0])
        seg_vec = seg_vec/np.linalg.norm(seg_vec)
        normal = np.array([-1*seg_vec[1], seg_vec[0]])
        return normal


class Circle(GeometryComponent):

    def __init__(self, radius):
        super().__init__()
        self.radius = radius

    def create_polygon(self, position, rotation):
        circ = Point(position).buffer(1)
        circ = affinity.rotate(circ, rotation)
        self.polygon = affinity.scale(circ, self.radius, self.radius)

    def get_normal(self, collision):
        normal_dir = collision-self._position
        return normal_dir / np.linalg.norm(normal_dir)


class Rectangle(GeometryComponent):

    def __init__(self, side_length_a, side_length_b):
        super().__init__()
        self.side_length_a = side_length_a
        self.side_length_b = side_length_b

    def create_polygon(self, position, rotation):
        minx = position[0]-self.side_length_a*0.5
        miny = position[1]-self.side_length_b*0.5
        maxx = position[0]+self.side_length_a*0.5
        maxy = position[1]+self.side_length_b*0.5
        box = shapely.geometry.box(minx, miny, maxx, maxy)
        box = affinity.rotate(box, rotation)
        self.polygon = box

    def get_regular_grid_ranges(self, origin, spacing):
        x0 = -(0.5*self.side_length_a)
        y0 = -(0.5*self.side_length_b)

        x1 = self.side_length_a*.5
        y1 = self.side_length_b*.5

        x_steps_left = np.ceil((x0-origin[0]) / spacing)
        #x_left = x_steps_left*spacing
        x_steps_right = np.floor((x1-origin[0]) / spacing)
        #x_right = x_steps_right*spacing
        y_steps_down = np.ceil((y0-origin[1]) / spacing)
        #y_down = y_steps_down*spacing
        y_steps_up = np.floor((y1-origin[1]) / spacing)

        return [[x_steps_left, x_steps_right], [y_steps_down, y_steps_up]]
        #y_up = y_steps_up*spacing
        #x = np.arange(x_left, x_right+spacing, spacing) + origin[0]
        #y = np.arange(y_down, y_up+spacing, spacing) + origin[1]

class GeneralPolygon(GeometryComponent):

    def __init__(self, polygon):
        super().__init__()
        self.polygon = polygon

    def create_polygon(self, position, rotation):
        pass
