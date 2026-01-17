from rfbudget import Orbit, km, degree
from pytest import approx

def test_orbit_amsat_xls():
    """
    Example from Amsat Excell Sheet
    """
    o = Orbit(
        apogee=km(805),
        perigee=km(795),
        inclination=degree(98.61))
    assert o.semi_major_axis == approx(km(7178.17), 0.01)
    assert o.mean_altitude == approx(km(800), 0.01)
    assert o.mean_radius == approx(km(7178.17), 0.01)
    assert o.eccentricity == approx(0.000697, abs=0.000001)
    assert o.planet_radius == approx(km(6378.166), 0.1)
    assert o.slant_range(degree(5)) == approx(km(2783.88), 0.1)