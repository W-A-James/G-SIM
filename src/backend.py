"""
Numerical simulation of orbital mechanics in two dimensions

Classes defined here:

    - Simulation
        - particles
    - Vector
        - Subclasses
            - Force    
            - Velocity
    - Particle
        - Attributes
            - Mass
            - Velocity
            - Net Force
            - Coordinates
        - Methods
            - update(time_step) -> updates velocity and position
"""
import math
import pylab
import numpy as np

import datetime

# CONSTANTS
G = 6.67e-11 # Universal Gravitational constant
SUN_MASS = 1.993e30 # Solar mass
EARTH_MASS = 6e24   # Earth mass
EARTH_VEL = 29806.079463282156  #Earth orbital velocity
AU = 1.496e11       # Average distance of earth from sun
EARTH_YEAR = 31536e3    # an earth year in seconds
MOON_ORBIT_RADIUS = 3844e5 # Average distance of moon from earth


class Vector(object):
    """Base class for all vector Quantities"""
    def __init__(self, x_comp, y_comp):
        self.x_comp = x_comp
        self.y_comp = y_comp
        self.magnitude = self.find_magnitude(x_comp, y_comp)
        self.direction = self.find_direction(x_comp, y_comp)
        self.unit = ""

    def find_direction(self, x_comp, y_comp):
        return math.atan2(y_comp, x_comp)

    def find_magnitude(self, x_comp, y_comp):
        return (x_comp**2 + y_comp**2)**0.5
    
    def from_magnitude_and_direction(self, magnitude, direction):
        x_comp = magnitude * math.cos(direction)
        y_comp = magnitude * math.sin(direction)

        return type(self)(x_comp, y_comp)

    def __add__(self, other):
        assert type(self) == type(other)
        return type(self)(self.x_comp + other.x_comp, self.y_comp + other.y_comp)

    def __sub__(self, other):
        assert type(self) == type(other)
        return type(self)(self.x_comp - other.x_comp, self.y_comp - other.y_comp)

    def __eq__(self, other):
        assert type(self) == type(other)
        return self.x_comp == other.x_comp and self.y_comp == other.y_comp

    def __rmul__(self, multiplier):
        return type(self)(multiplier*self.x_comp, multiplier*self.y_comp)

    def __mul__(self, multiplier):
        return type(self)(multiplier*self.x_comp, multiplier*self.y_comp)

    def __str__(self):
        return "{} x_comp={}{}, y_comp={}{}, direction={}rad, magnitude={}{}".format(type(self), self.x_comp, self.unit, self.y_comp, self.unit, round(self.direction, 3), round(self.magnitude, 3), self.unit)

class Velocity(Vector):
    """Subclass of Vector modeling velocity as a vector measured in m/s"""
    def __init__(self, x_comp, y_comp):
        Vector.__init__(self, x_comp, y_comp)
        self.unit = "m/s"

class Force(Vector):
    """Subclass of Vector modeling Force as a vector measured in N"""
    def __init__(self, x_comp, y_comp):
        Vector.__init__(self, x_comp, y_comp)
        self.unit = "N"
    
    def get_dv(self, mass, d_time):
        return (d_time/mass)*Velocity(self.x_comp, self.y_comp)

class Particle(object):
    """
    Base class for other particles.
    Models bodies as point masses

    mass -> float or int defining mass in kg
    initial_velocity -> Velocity object describing instantaneous velocity at t=0 
    force -> Force object describing the initial force acting on the particle
    name -> name assigned to this object used for titling csv file
    """
    def __init__(self, mass, position, initial_velocity=Velocity(0,0), force=Force(0,0), name="Particle"):
        assert type(position) is tuple and len(position) == 2 and type(position[0]) is int or float and type(position[1]) is int or float
        assert isinstance(initial_velocity, Velocity)
        self.x_coord, self.y_coord = position
        self.initial_velocity = initial_velocity
        self.velocity = initial_velocity
        self.force_acting = force
        self.mass = mass
        self.current_time = 0
        self.log = ""
        self.data_set = []
        self.csv_data = "Time, x, y, velocity_mag, velocity_dir, force_mag, force_dir\n"
        self.name = name
        self.file_name = self.name + "_" + str(datetime.datetime.now())

    def update(self, d_time):
        self.x_coord += self.velocity.x_comp * d_time
        self.y_coord += self.velocity.y_comp * d_time

        self.velocity += ((1/self.mass)*self.force_acting).get_dv(d_time)
        self.update_data_set()
        self.update_csv()

        self.current_time += d_time

    def __str__(self):
        return "{} mass={}kg, at ({}, {}), velocity=({}m/s @ {}rad)".format(self.name, self.mass, self.x_coord, self.y_coord, self.velocity.magnitude, self.velocity.direction)

    def update_csv(self):
        self.csv_data += "{}, {}, {}, {}, {}, {}, {}\n".format(self.current_time, self.x_coord, self.y_coord, self.velocity.magnitude, self.velocity.direction, self.force_acting.magnitude, self.force_acting.direction)

    def update_data_set(self):
        self.data_set.append({"time": self.current_time, "x": self.x_coord, "y":self.y_coord, "vel_mag":self.velocity.magnitude, "force_mag":self.force_acting.magnitude})

    def write_to_csv(self):
        file = open(self.file_name + ".csv", "w")
        file.write(self.csv_data)
        file.close()


class GravParticle(Particle):
    """
    Subclass of Particle which takes into account gravitational forces between masses

    mass -> float or int defining mass in kg
    initial_velocity -> Velocity object describing instantaneous velocity at t=0 
    force -> Force object describing the initial force acting on the particle
    fixed -> bool; if true, particle position cannot be changed
    is_ghost -> bool; if true, particle is ignored in all calculations
    name -> name assigned to this object used for titling csv file
    """
    def __init__(self, mass, position, initial_velocity=Velocity(0,0), force=Force(0,0), fixed=False, is_ghost=False, name="Particle"):
        Particle.__init__(self, mass, position, initial_velocity, force, name=name)
        self.fixed = fixed
        self.is_ghost = is_ghost

    def distance(self, other):
        return ((self.x_coord - other.x_coord)**2 + (self.y_coord - other.y_coord)**2)**0.5

    def set_master(self, master):
        assert isinstance(master, Simulation)
        self.master = master

    def update(self, d_time):
        if not self.is_ghost:
            if not self.fixed:
                self.x_coord += self.velocity.x_comp * d_time
                self.y_coord += self.velocity.y_comp * d_time

                self.velocity += self.force_acting.get_dv(self.mass, d_time)

            self.force_acting = Force(0,0)
            for particle in self.master.particles:
                if particle is not self and not particle.is_ghost: 
                    self.force_acting += Force_from_magnitude_and_direction((G*self.mass*particle.mass)/(self.distance(particle)**2), find_direction(particle.x_coord-self.x_coord, particle.y_coord-self.y_coord))

            self.update_data_set()
            self.update_csv()

            self.current_time += d_time

def find_direction(x, y):
    return math.atan2(y, x)

def Force_from_magnitude_and_direction(magnitude, direction):
    x_comp = math.cos(direction) * magnitude
    y_comp = math.sin(direction) * magnitude

    return Force(x_comp, y_comp)

def Vector_from_magnitude_and_direction(magnitude, direction):
    x_comp = math.cos(direction) * magnitude
    y_comp = math.sin(direction) * magnitude

    return Vector(x_comp, y_comp)

def Velocity_from_magnitude_and_direction(magnitude, direction):
    x_comp = math.cos(direction) * magnitude
    y_comp = math.sin(direction) * magnitude

    return Velocity(x_comp, y_comp)


class Simulation:
    """
    Framework for interactions of Particle and GravParticle objects
    *particles -> iterable containing Particle or GravParticle Objects
    sim_time   -> total time in seconds for which the simulation will perform calculations
    time_step  -> time in seconds defining how much time is skipped over in each iteration
    """
    def __init__(self, *particles, sim_time, time_step):
        self.particles = particles + (NULL_PARTICLE, )
        for particle in self.particles:
            if isinstance(particle, GravParticle):
                particle.set_master(self)
        self.sim_time = sim_time
        self.time_step = time_step
        self.plot_data = []
        self.max_x, self.max_y, self.min_x, self.min_y = 0, 0, 0, 0

    def main_loop(self):
        time = np.arange(0, self.sim_time, self.time_step)
        num_iters = len(time)
        for instant in time:
            particles_updated = -1 # Ignoring NULL_PARTICLE

            # Update each particle being modeled
            for i in range(len(self.particles)):
                particles_updated += 1
                self.particles[i].update(self.time_step)
                
                # Update x and y bounds of simulation
                if self.particles[i].x_coord > self.max_x:
                    self.max_x = self.particles[i].x_coord

                if self.particles[i].y_coord > self.max_y:
                    self.max_y = self.particles[i].y_coord  

                if self.particles[i].x_coord < self.min_x:
                    self.min_x = self.particles[i].x_coord

                if self.particles[i].y_coord < self.min_y:
                    self.min_y = self.particles[i].y_coord

            # Print out progress of simulation after every iteration
            print("{} particles updated at t = {}".format(particles_updated, instant))
            print("{}% of calculations complete\n".format(round(((instant/self.time_step)*100/num_iters), 3)))

        for particle in self.particles:
            if not particle.is_ghost:
                particle.write_to_csv()

                # Append list of x and y positions of each particle as recorded over the entire simulation
                self.plot_data.append([data["x"] for data in particle.data_set])
                self.plot_data.append([data["y"] for data in particle.data_set])

        # Plot paths of all particles over total duration of simulation
        pylab.grid()
        pylab.plot(*self.plot_data)
        pylab.show()

# A ghost particle appended to particle list to work around issue whereby last particle in list is not
# updated
NULL_PARTICLE = GravParticle(1, (0,0), is_ghost=True)

if __name__ == "__main__":
    Earth = GravParticle(EARTH_MASS, (-2*AU, AU), 1.2*Velocity(EARTH_VEL, 0), name="Earth")
    Sun = GravParticle(SUN_MASS, (-AU,0), initial_velocity=0.75*Velocity(0, 21115.293390650815), fixed=False, name="Sun")
    Sun2 = GravParticle(SUN_MASS, (AU, 0), initial_velocity=0.75*Velocity(0, -21115.293390650815), fixed=False, name="Sun2")
    particles = [Earth, Sun, Sun2]
    
    sim = Simulation(*particles, sim_time=2*EARTH_YEAR, time_step=1000)
    sim.main_loop()