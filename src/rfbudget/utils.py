import math
from numpy import log10
from typing import NewType

# Define "Unit Tags"
Hz_t = NewType("Hz", float)
dB_t = NewType("dB", float)  # unitless ratio in decibell
dBm_t = NewType("dBm", float)  # decibell milliwatt
m_t = NewType("m", float)
deg_t = NewType("°", float)
kelvin_t = NewType("K", float)


def GHz(f: float) -> Hz_t:
    return Hz_t(f * 1e9)


def MHz(f: float) -> Hz_t:
    return Hz_t(f * 1e6)


def kHz(f: float) -> Hz_t:
    return Hz_t(f * 1e3)


def Hz(f: float) -> Hz_t:
    return Hz_t(f)


def dB(v: float) -> dB_t:
    return dB_t(v)


def dBm(v: float) -> dBm_t:
    return dBm_t(v)


def watt_to_dBm(v: float) -> dBm_t:
    return dBm_t(10 * log10(v * 1000))


def m(v: float) -> m_t:
    return m_t(v)


def dm(v: float) -> m_t:
    return m_t(10 * v)


def hm(v: float) -> m_t:
    return m_t(100 * v)


def km(v: float) -> m_t:
    return m_t(1000 * v)


def degree(v: float) -> deg_t:
    return deg_t(v)


def radians(v: float) -> deg_t:
    return deg_t(math.degrees(v))


def to_radians(v: deg_t) -> float:
    return math.radians(v)


def kelvin(v: float) -> kelvin_t:
    return kelvin_t(v)


def celsius(v: float) -> kelvin_t:
    return kelvin_t(v + 273.15)


def to_celsius(v: kelvin_t) -> float:
    return v - 273.15


EARTH_RADIUS = km(6378.166)
