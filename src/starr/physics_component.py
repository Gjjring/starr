import numpy as np
import itertools
class PhysicsComponent():

    def __init__(self, mass, static=False):
        #self.parent = parent
        self.static = static
        self.mass = mass
        self.velocity = np.zeros((2))
        self.acceleration = np.zeros((2))
        self.previous_collisions = [None]
        self.memory = 1
        self.kinetic_energy = 0.0
        self.momentum = np.zeros(2)

    def update(self, simulation_object, world, time_step):
        self.update_kinematics(simulation_object, time_step)
        self.update_energy()

    def update_energy(self):
        v = np.linalg.norm(self.velocity)
        self.kinetic_energy = 0.5*self.mass*v**2

    def update_momentum(self):
        self.momentum = self.mass*self.velocity

    def apply_resistance(self):
        constant = 0.1
        v_norm = np.linalg.norm(self.velocity)
        if v_norm == 0.0:
            return
        v_dir = self.velocity/v_norm
        self.apply_force( -v_dir*constant*v_norm**2)

    def update_kinematics(self, simulation_object, time_step):
        #self.apply_resistance()
        self.velocity += self.acceleration
        simulation_object.translate(time_step * self.velocity)
        self.acceleration *= 0

    def apply_force(self, force):
        self.acceleration += force

    def collision(self, other, normal):
        if self.static:
            return
        m1 = self.mass
        m2 = other.mass

        v1_init = self.velocity
        v2_init = other.velocity

        v1c_init = v1_init
        v2c_init = v2_init

        v12_init = v1c_init - v2c_init
        j = self.get_impulse(0.90, v12_init, normal, m1, m2)
        self.apply_force((j*normal/m1))
        self.previous_collisions[0] = other


    def get_impulse(self, e, v12_init, normal, m1, m2):
        numerator = -(1+e)* v12_init.dot(normal)
        denom = 1/m1 + 1/m2
        return numerator/denom

    """
    def update_physics(self, time_step):
        self.velocity += time_step * self.acceleration
        self.parent.position += time_step * self.velocity
        self.acceleration *= 0


    def collision_allowed(self, other):
        truth_val= not other.number in self.previous_collisions
        partners = [3, 4]
        if self.number in partners and other.number in partners and False:
            print("collison {}-{}: {}".format(self.number,
                                            other.number,
                                            truth_val))

        return truth_val

    """
"""
class RigidBody(PhysicsComponent):

    def __init__(self, parent, parameters):
        super(RigidBody, self).__init__(parent, parameters)
"""
