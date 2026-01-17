import math
from typing import Optional
from .utils import m_t, deg_t, EARTH_RADIUS, to_radians


def distance_max(elevation: deg_t, orbit_radius: m_t, r: Optional[m_t] = None) -> m_t:
    """
    elevations in degrees
    """
    el = to_radians(elevation)
    if r is None:
        r = EARTH_RADIUS  # Earth Radius
    # return -1 * r * sin(elevation) + sqrt((r * sin(elevation))**2 + height**2 + 2 * r * height)
    return m_t(
        r
        * (
            math.sqrt((((orbit_radius**2) / (r**2)) - ((math.cos(el)) ** 2)))
            - math.sin(el)
        )
    )


class Orbit:
    def __init__(
        self,
        apogee: m_t,
        perigee: Optional[m_t] = None,
        inclination: Optional[deg_t] = None,
        planet_radius: Optional[m_t] = None,
    ):
        if perigee is None:
            perigee = apogee
        if planet_radius is None:
            planet_radius = EARTH_RADIUS
        self.planet_radius: m_t = planet_radius
        self.apogee: m_t = apogee
        self.perigee: m_t = perigee
        self.inclination: Optional[deg_t] = inclination
        self.semi_major_axis: m_t = m_t(
            (self.apogee + self.perigee + 2 * planet_radius) / 2
        )
        self.eccentricity: float = float(
            ((self.apogee + planet_radius) - (self.perigee + planet_radius))
            / ((self.apogee + planet_radius) + (self.perigee + planet_radius))
        )
        self.mean_altitude: m_t = m_t((self.apogee + self.perigee) / 2)
        self.mean_radius: m_t = m_t(planet_radius + self.mean_altitude)

    def slant_range(self, elevation: deg_t) -> m_t:
        return distance_max(elevation, self.mean_radius, self.planet_radius)
