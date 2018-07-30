"""
Some default starting parameters for simulations
"""
import backend as b

DEFAULTS = {"Earth and Sun"     : [b.GravParticle(b.EARTH_MASS, (b.AU, 0), b.Velocity(0, b.EARTH_VEL), name="Earth", fixed=False, is_ghost=False),
                                   b.GravParticle(b.SUN_MASS, (0,0), name="Sun", fixed=False, is_ghost=False)],
            "Solar system"      : [],
            "Binary Stars"      : [],
            "Milky Way...?"     : [],
            "ISS"               : [],
            "Moon around Earth" : [],
            "Mars and Moons"    : [],
            "Jovian System"     : [],
}