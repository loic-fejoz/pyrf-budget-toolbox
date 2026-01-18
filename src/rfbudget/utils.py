import math
from numpy import log10
from typing import NewType

# Define "Unit Tags"
Hz_t = NewType("Hz", float)
dB_t = NewType("dB", float)  # unitless ratio in decibell
dBm_t = NewType("dBm", float)  # decibell milliwatt
dBW_t = NewType("dBW", float)  # decibell watt
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


def watt_to_dBW(v: float) -> dBW_t:
    return dBW_t(10 * log10(v))


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


def nf_to_temp(nf: dB_t, t0: kelvin_t = kelvin_t(290.0)) -> kelvin_t:
    return kelvin_t(t0 * (10 ** (nf / 10) - 1))


def temp_to_nf(t: kelvin_t, t0: kelvin_t = kelvin_t(290.0)) -> dB_t:
    if t == 0:
        return dB_t(0)
    return dB_t(10 * log10(1 + t / t0))


def loss_temp_to_nf(loss_dB: dB_t, tp: kelvin_t, t0: kelvin_t = kelvin_t(290.0)) -> dB_t:
    """
    Calculate the equivalent noise figure of a lossy element at physical temperature tp.
    """
    l_lin = 10 ** (loss_dB / 10)
    te = (l_lin - 1) * tp
    return temp_to_nf(te, t0)


EARTH_RADIUS = km(6378.166)
