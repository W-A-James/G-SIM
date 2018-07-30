import unittest
from backend import *

class TestVector(unittest.TestCase):
    def setUp(self):
        self.a = Vector(10, 9)
        self.b = Vector(6, 5)
        self.c = Vector(-3, -3)
        self.d = Vector(0, 0)

    def test_add(self):
        self.assertEqual(Vector(16, 14), self.a + self.b)
        self.assertEqual(Vector(7, 6), self.a + self.c)
        self.assertEqual(self.a, self.a + self.d)

    def test_sub(self):
        self.assertEqual(Vector(13, 12), self.a - self.c)
        self.assertEqual(Vector(4, 4), self.a - self.b)
        self.assertEqual(self.c, self.c - self.d)

    def test_rmul(self):
        self.assertEqual(Vector(20, 18), 2*self.a)
        self.assertEqual(Vector(-1, -1), (1/3)*self.c)

    def test_from_magnitude_and_direction(self):
        a = Vector(3, 4)
        b = Vector_from_magnitude_and_direction(5, math.atan2(4, 3))
        
        self.assertAlmostEqual(a.x_comp, b.x_comp)
        self.assertAlmostEqual(a.y_comp, b.y_comp)
        
class TestVelocity(unittest.TestCase):
    def setUp(self):
        self.a = Velocity(10, 9)
        self.b = Velocity(6, 5)
        self.c = Velocity(-3, -3)
        self.d = Velocity(0, 0)

    def test_add(self):
        self.assertEqual(Velocity(16, 14), self.a + self.b)
        self.assertEqual(Velocity(7, 6), self.a + self.c)
        self.assertEqual(self.a, self.a + self.d)

    def test_sub(self):
        self.assertEqual(Velocity(13, 12), self.a - self.c)
        self.assertEqual(Velocity(4, 4), self.a - self.b)
        self.assertEqual(self.c, self.c - self.d)

    def test_rmul(self):
        self.assertEqual(Velocity(20, 18), 2*self.a)
        self.assertEqual(Velocity(-1, -1), (1/3)*self.c)

    def test__str__(self):
        reg_ex = r"{} (x_comp=-?\d+\.?\d*?m/s), (y_comp=-?\d+\.?\d*?m/s), (direction=-?\d*\.?\d*?rad), (magnitude=-?\d+\.?\d*?m/s)".format(type(self.a))
        self.assertRegex(str(self.a), reg_ex)
        self.assertRegex(str(self.b), reg_ex)
        self.assertRegex(str(self.c), reg_ex)
        self.assertRegex(str(self.d), reg_ex)

class TestForce(unittest.TestCase):
    pass


class TestParticle(unittest.TestCase):
    def setUp(self):
        self.a = Particle(1, (0,0))

    def test_update(self):
        pass


class TestGravParticle(unittest.TestCase):
    def setUp(self):
        self.a = GravParticle(10, (0,0))
        self.b = GravParticle(2, (0, 10))
        self.c = GravParticle(1, (0, 3))
        self.d = GravParticle(1, (4, 0))

    def test_distance(self):
        self.assertAlmostEqual(self.c.distance(self.d), 5.0)
        self.assertAlmostEqual(self.b.distance(self.a), 10)

    def test_update_with_two_non_ghost_particles(self):
        self.sim = Simulation(*[self.a, self.b], sim_time=0, time_step=0)

        for particle in self.sim.particles:
            particle.update(0)
        
        # Check if magnitude of force being calculated is accurate
        self.assertAlmostEqual(self.sim.particles[0].force_acting.magnitude, 1.334e-11)
        self.assertEqual(self.sim.particles[0].force_acting.magnitude, self.sim.particles[1].force_acting.magnitude)
        
        # Check if gravitational forces are attractive or repulsive
        self.assertAlmostEqual(self.sim.particles[0].force_acting.direction, math.pi/2)
        try:
            self.assertAlmostEqual(self.sim.particles[1].force_acting.direction, 3*math.pi/2)
        except:
            self.assertAlmostEqual(self.sim.particles[1].force_acting.direction, -math.pi/2)

    def test_update_with_a_ghost_particle(self):
        self.sim = Simulation(*[self.b, NULL_PARTICLE], sim_time=0, time_step=0)
        for particle in self.sim.particles:
            particle.update(0)

        self.assertEqual(self.sim.particles[0].force_acting.magnitude, 0)
        
        self.assertEqual(self.sim.particles[0].force_acting.magnitude, self.sim.particles[1].force_acting.magnitude)
    

class TestSim(unittest.TestCase):
    pass
    
unittest.main(verbosity=5)