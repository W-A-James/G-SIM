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
import time

import datetime

# CONSTANTS 1e10 = 1 * 10^10
G = 6.67e-11 # Universal Gravitational constant
SUN_MASS = 1.993e30 # Solar mass in kilograms
EARTH_MASS = 6e24   # Earth mass in kilograms
EARTH_VEL = 29806.079463282156  #Earth orbital velocity in metres per second
AU = 1.496e11       # Average distance of earth from sun in metres
EARTH_YEAR = 31536e3    # an earth year in seconds
MOON_ORBIT_RADIUS = 3844e5 # Average distance of moon from earth in metres
ISS_MASS = 417289
ISS_VEL = 7666.6667
ISS_ORBIT_RADIUS = 382.5e3
###############################################################################
TEST_DIRECTORY = "TestData" + os.sep

def find_magnitude(x_comp, y_comp):
    return (x_comp**2 + y_comp**2)**0.5

def find_direction(x, y):
    return math.atan2(y, x)

def timer(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        rv = func(*args, **kwargs)
        end = time.time()
        print(str(func) + " took " + str(end - start) + "s to run.")
        return rv
    return wrapper

class Vector(object):
    """Base class for all vector Quantities"""
    def __init__(self, x_comp, y_comp):
        self.x_comp = x_comp
        self.y_comp = y_comp
        self.magnitude = find_magnitude(x_comp, y_comp)
        self.direction = find_direction(x_comp, y_comp)
        self.unit = ""

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
        return type(self) == type(other) and self.x_comp == other.x_comp and self.y_comp == other.y_comp

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
        self.file_name = TEST_DIRECTORY + self.name + "_" + str(datetime.datetime.now())

    def update(self, d_time):
        self.x_coord += self.velocity.x_comp * d_time
        self.y_coord += self.velocity.y_comp * d_time

        self.velocity += ((1/self.mass)*self.force_acting).get_dv(d_time)
        self.update_data_set()
        self.update_csv()

        self.current_time += d_time

    def __str__(self):
        return "{} mass={}kg, pos=({}, {}), velocity=({}m/s @ {}rad), force_acting={}N @ {}rad".format(self.name, self.mass, self.x_coord, self.y_coord, self.velocity.magnitude, self.velocity.direction, self.force_acting.magnitude, self.force_acting.direction)

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
        self.force_queue = {} # Entries in this queue are in the form {<GravParticle>:<Force between particles>}

    def distance(self, other):
        return ((self.x_coord - other.x_coord)**2 + (self.y_coord - other.y_coord)**2)**0.5

    def set_master(self, master):
        self.master = master

    def update(self, d_time):
        if not self.is_ghost:
            if not self.fixed:
                self.x_coord += self.velocity.x_comp * d_time
                self.y_coord += self.velocity.y_comp * d_time

                self.velocity += self.force_acting.get_dv(self.mass, d_time)

            self.force_acting = Force(0,0) # Initialize force acting on particle as zero before calculations of instantaneous force on particle
            for particle in self.master.particles:
                if (particle is not self) and (particle not in self.force_queue) and (not particle.is_ghost): 
                    # Find gravitational force between the two particles
                    force_between = Force_from_magnitude_and_direction((G*self.mass*particle.mass)/(self.distance(particle)**2), find_direction(particle.x_coord-self.x_coord, particle.y_coord-self.y_coord))
                    self.force_acting += force_between
                    particle.force_queue[self] = -1 * force_between

            for entry in self.force_queue:
                self.force_acting += self.force_queue[entry]

            self.update_data_set()
            self.update_csv()

            self.current_time += d_time

            # Reset force_queue for next iteration
            self.force_queue.clear()

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
            particle.set_master(self)
        self.sim_time = sim_time
        self.time_step = time_step
        self.log = ""
        self.log_name = TEST_DIRECTORY + "Simulation_ {}.log".format((str(datetime.datetime.now())))
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

                self.log += str(self.particles[i]) + "\n"
            self.log += "\n"
            # Print out progress of simulation after every iteration
            print("{} particles updated at t = {}".format(particles_updated, instant))
            print("{}% of calculations complete\n".format(round(((instant/self.time_step)*100/num_iters), 3)))

        for particle in self.particles:
            if not particle.is_ghost:
                # particle.write_to_csv()

                # Append list of x and y positions of each particle as recorded over the entire simulation
                self.plot_data.append([data["x"] for data in particle.data_set])
                self.plot_data.append([data["y"] for data in particle.data_set])

        with open(self.log_name, "w") as fp:
            fp.write(self.log)
            
        # Plot paths of all particles over total duration of simulation
        pylab.grid()
        pylab.plot(*self.plot_data)
        pylab.show()

# A ghost particle appended to particle list to work around issue whereby last particle in list is not updated
NULL_PARTICLE = GravParticle(1, (0,0), is_ghost=True, name="NULL")

if __name__ == "__main__":
    from defaults import DEFAULTS
    particles = DEFAULTS["Solar system"]

    print(particles)

    sim = Simulation(*particles, sim_time=0.25*EARTH_YEAR, time_step=0.025*EARTH_YEAR)
    sim.main_loop()