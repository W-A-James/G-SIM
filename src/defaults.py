"""
Some default starting parameters for simulations
"""
import backend as b_end

DEFAULTS = {"Earth and Sun"     : [b_end.GravParticle(b_end.EARTH_MASS, (b_end.AU, 0), b_end.Velocity(0, b_end.EARTH_VEL), name="Earth", fixed=False, is_ghost=False),
                                   b_end.GravParticle(b_end.SUN_MASS, (0,0), name="Sun", fixed=False, is_ghost=False)],
            "Solar system"      : [],
            "Binary Stars"      : [],
            "Milky Way...?"     : [],
            "ISS"               : [],
            "Moon around Earth" : [],
            "Mars and Moons"    : [],
            "Jovian System"     : [],
}