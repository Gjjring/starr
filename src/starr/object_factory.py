from starr.simulation_object import SimulationObject, ObjectGroup
from starr.geometry_component import Circle, Rectangle, GeneralPolygon
from starr.physics_component import PhysicsComponent
from starr.graphics_component import GraphicsComponent
from starr.misc import is_iterable
import numpy as np
def insert_defaults(keys):
    default_keys = {'mass':1.0, 'color':'b', 'fill':True,
                    'edge_color':'k'}
    for key in default_keys:
        if key not in keys:
            keys[key] = default_keys[key]

def generate_object(keys):

    shape = keys['shape']

    insert_defaults(keys)

    factory_dict = {'Circle': circle,
                    'Rectangle': rectangle}
    return factory_dict[shape](keys)

def object_from_polygon(keys, polygon):
    insert_defaults(keys)
    geo = GeneralPolygon(polygon)
    phys = PhysicsComponent(keys['mass'])
    graph = GraphicsComponent(keys['color'], keys['fill'], keys['edge_color'])
    return SimulationObject(geo, phys, graph)

def circle(keys):
    geo = Circle(keys['radius'])
    phys = PhysicsComponent(keys['mass'])
    graph = GraphicsComponent(keys['color'], keys['fill'], keys['edge_color'])
    return SimulationObject(geo, phys, graph)

def rectangle(keys):
    geo = Rectangle(keys['side_length_a'],
                    keys['side_length_b'])
    phys = PhysicsComponent(keys['mass'])
    graph = GraphicsComponent(keys['color'], keys['fill'], keys['edge_color'])
    return SimulationObject(geo, phys, graph)

def clone(sim_object):
    keys = {}
    keys['mass'] = sim_object.physics.mass
    keys['color'] = sim_object.graphics.color
    pos = np.array(sim_object.position)
    rot = sim_object.rotation
    geo = sim_object.geometry
    if isinstance(geo, Circle):
        keys['radius'] = geo.radius
        clone_obj = circle(keys)
    elif isinstance(geo, Rectangle):
        keys['side_length_a'] = geo.side_length_a
        keys['side_length_b'] = geo.side_length_b
        clone_obj = rectangle(keys)
    elif isinstance(geo, GeneralPolygon):
        clone_obj = object_from_polygon(keys, geo._polygon)
    #clone_obj.physics.velocity = np.array(sim_object.physics.velocity)
    #clone_obj.physics.update_energy()
    #clone_obj.physics.update_momentum()
    #clone_obj.physics.static = sim_object.physics.static
    clone_obj.physics = sim_object.physics
    clone_obj.position = pos
    clone_obj.rotation = rot
    return clone_obj


def generate_group(keys):
    shape = keys['shape']

    factory_dict = {'Circle': circle,
                    'Rectangle': rectangle}

    insert_defaults(keys)
    group = ObjectGroup()
    n_obj = keys['n_objects']


    assert n_obj >= 0

    if n_obj > 1:
        for item in keys.items():
            if is_iterable(item[1]):
                assert len(item[1]) == n_obj

    for i_obj in range(n_obj):
        sliced_keys = {}
        for item in keys.items():
            if is_iterable(item[1]):
                sliced_keys[item[0]] = item[1][i_obj]
            else:
                sliced_keys[item[0]] = item[1]
        obj = factory_dict[shape](sliced_keys)
        group.append(obj)
    return group
