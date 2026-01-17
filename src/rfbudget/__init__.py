import io
from numpy import log10, log2
import math
from math import sin, cos, sqrt
import schemdraw
from schemdraw import dsp
import matplotlib
matplotlib.use('Agg')
from typing import NewType, List, Optional, Union, Any
from typing import NewType

# Define "Unit Tags"
Hz_t = NewType('Hz', float)
dB_t = NewType('dB', float) # unitless ratio in decibell
dBm_t = NewType('dBm', float) # decibell milliwatt
m_t = NewType('m', float)
deg_t = NewType('°', float)
kelvin_t = NewType('K', float)

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

def distance_max(elevation: deg_t, orbit_radius: m_t, r: Optional[m_t] = None) -> m_t:
    """
    elevations in degrees
    """
    el = to_radians(elevation)
    if r is None:
        r = EARTH_RADIUS # Earth Radius
    # return -1 * r * sin(elevation) + sqrt((r * sin(elevation))**2 + height**2 + 2 * r * height)
    return m_t(r *(math.sqrt((((orbit_radius**2)/(r**2))-((math.cos(el))**2)))-math.sin(el)))

class Orbit:
    def __init__(self, apogee: m_t, perigee: Optional[m_t] = None, inclination: Optional[deg_t] = None, planet_radius: Optional[m_t] = None):
        if perigee is None:
            perigee = apogee
        if planet_radius is None:
            planet_radius = EARTH_RADIUS
        self.planet_radius: m_t = planet_radius
        self.apogee: m_t = apogee
        self.perigee: m_t = perigee
        self.inclination: Optional[deg_t] = inclination
        self.semi_major_axis: m_t = m_t((self.apogee + self.perigee + 2 * planet_radius) / 2)
        self.eccentricity: float = float(((self.apogee + planet_radius) - (self.perigee + planet_radius)) / ((self.apogee + planet_radius) + (self.perigee + planet_radius)))
        self.mean_altitude: m_t = m_t((self.apogee + self.perigee) / 2)
        self.mean_radius: m_t = m_t(planet_radius + self.mean_altitude)

    def slant_range(self, elevation: deg_t) -> m_t:
        return distance_max(elevation, self.mean_radius, self.planet_radius)

class Element:
    """
        nf is noise figure
    """
    def __init__(self, name: Optional[str] = None, gain: dB_t = dB(0), nf: dB_t = dB(0), oip3: Optional[dBm_t] = None, iip3: Optional[dBm_t] = None):
        self.name: str = name or ''
        self.gain: dB_t = gain
        self.nf: dB_t = nf
        self.iip3: Optional[dBm_t] = iip3
        self.oip3: Optional[dBm_t] = oip3
        if oip3 == None and iip3 != None and gain != None:
            self.oip3 = dBm(iip3 + gain)
        elif iip3 == None and oip3 != None and gain != None:
            self.iip3 = dBm(oip3 - gain)
        elif oip3 == None:
            self.oip3 = None

    def schemdraw(self, d: Any, options: dict) -> Any:
        return self.schemdraw_label(options, dsp.Box(w=d.unit/3, h=d.unit/3).label(self.name, 'bottom'))
    
    def schemdraw_label(self, options: dict, b: Any, lbl: Optional[str] = None) -> Any:
        if lbl is None:
            lbl = ''
        else:
            lbl = str(lbl)
        if options.get('with_gain') and self.gain != None:
            lbl += 'gain={0:.2f}dB\n'.format(self.gain)
        if options.get('with_nf') and self.nf:
            lbl += 'NF={0:.2f}dB\n'.format(self.nf)
        if options.get('with_iip') and self.iip3:
            lbl += 'IIP3={0:.2f}dB\n'.format(self.iip3)
        if options.get('with_oip') and self.oip3:
            lbl += 'OIP3={0:.2f}dB\n'.format(self.oip3)
        return b.label(lbl, 'top', ofst=(-0.2, 0.6), fontsize=6)

class Antenna(Element):
    def __init__(self, name: Optional[str] = None, gain: dB_t = dB(0), nf: dB_t = dB(0), iip3: Optional[dBm_t] = None, oip3: Optional[dBm_t] = None, z: float = 50):
        Element.__init__(self, name=name or 'Antenna', gain=gain, nf=nf, iip3=iip3, oip3=oip3)
        self.z: float = z

    def schemdraw(self, d: Any, options: dict) -> Any:
        return self.schemdraw_label(options, dsp.Antenna().label(self.name, 'bottom'))

class NPort(Element):
    def __init__(self):
        pass

class TwoPortsElement(Element):
    def __init__(self, name: Optional[str] = None, gain: dB_t = dB(0), nf: dB_t = dB(0), iip3: Optional[dBm_t] = None, oip3: Optional[dBm_t] = None, z_in: float = 50, z_out: float = 50):
        Element.__init__(self, name=name, gain=gain, nf=nf, iip3=iip3, oip3=oip3)
        self.z_in: float = z_in
        self.z_out: float = z_out

class Amplifier(TwoPortsElement):
    def __init__(self, name: Optional[str] = None, gain: dB_t = dB(0), nf: dB_t = dB(0), iip3: Optional[dBm_t] = None, oip3: Optional[dBm_t] = None, z_in: float = 50, z_out: float = 50):
        TwoPortsElement.__init__(self, name=name or 'LNA', gain=gain, nf=nf, iip3=iip3, oip3=oip3, z_in=z_in, z_out=z_out)

    def schemdraw(self, d: Any, options: dict) -> Any:
        return self.schemdraw_label(options, dsp.Amp().fill('lightblue').label(self.name, 'bottom'))

class Loss(TwoPortsElement):
    def __init__(self, name: Optional[str] = None, loss: dB_t = dB(0), oip3: Optional[dBm_t] = None, z_in: float = 50, z_out: float = 50):
        TwoPortsElement.__init__(self, name=name or 'Loss', gain=dB(-loss), nf=loss, oip3=oip3, z_in=z_in, z_out=z_out)

    def schemdraw(self, d: Any, options: dict) -> Any:
        return self.schemdraw_label(options, dsp.Box(w=d.unit/3, h=d.unit/3).fill('#ffeeee').label(self.name, 'bottom'))

class PathLoss(Loss):
    def __init__(self, name: Optional[str] = None, loss: dB_t = dB(0), oip3: Optional[dBm_t] = None, z_in: float = 50, z_out: float = 50):
        Loss.__init__(self, name=name or 'PathLoss', loss=loss, oip3=oip3, z_in=z_in, z_out=z_out)

class FreeSpacePathLossFriis(PathLoss):
    def __init__(self, name: Optional[str] = None, distance: m_t = m(0), freq: Hz_t = Hz(0), oip3: Optional[dBm_t] = None, z_in: float = 50, z_out: float = 50):
        self.distance: m_t = distance
        loss = dB(20 * log10(distance) + 20 * log10(freq) - 147.55)
        PathLoss.__init__(self, name=name or 'FPSL', loss=loss, oip3=oip3, z_in=z_in, z_out=z_out)

    def schemdraw(self, d: Any, options: dict) -> Any:
        return self.schemdraw_label(
            options,
            dsp.Box(w=d.unit/3, h=d.unit/3).fill('#eeeeff').label(self.name, 'bottom'),
            lbl='d={0:.2f}m\n'.format(self.distance))

class RadarFreeSpaceBasicLoss(PathLoss):
    """
    https://www.itu.int/dms_pubrec/itu-r/rec/p/R-REC-P.525-2-199408-S!!PDF-E.pdf
    """
    def __init__(self, name: Optional[str] = None, distance: m_t = m(0), sigma: float = 1.0, freq: Hz_t = Hz(0), oip3: Optional[dBm_t] = None, z_in: float = 50, z_out: float = 50):
        """
        Two way loss of the signal of a radar.
        distance: distance from the radar to the target
        sigma: radar target cross-section (m²)
        """
        self.distance: m_t = distance
        self.sigma: float = sigma
        loss = dB(103.4 + 20 * log10(freq / MHz(1)) + 40 * log10(distance / km(1)) - 10 * log10(sigma))
        PathLoss.__init__(self, name=name or 'FPSL', loss=loss, oip3=oip3, z_in=z_in, z_out=z_out)

    def schemdraw(self, d: Any, options: dict) -> Any:
        return self.schemdraw_label(
            options,
            dsp.Box(w=d.unit/3, h=d.unit/3).fill('#eeeeff').label(self.name, 'bottom'),
            lbl='d={0:.2f}m\nσ={0:.2f}m\n'.format(self.distance, self.sigma))

class OkumuraHataPathLoss(PathLoss):
    """See https://en.wikipedia.org/wiki/Hata_model
    """
    SMALL_CITY = 'small city'
    MEDIUM_CITY = 'medium city'
    LARGE_CITY = 'large city'
    SUBURBAN = 'suburban environment'
    OPEN = 'open environment'

    def __init__(self, name: Optional[str] = None,
                 distance: m_t = m(0),
                 freq: Hz_t = Hz(0),
                 base_height: m_t = m(30),
                 mobile_height: m_t = m(1),
                 environment: str = '',
                 oip3: Optional[dBm_t] = None, z_in: float = 50, z_out: float = 50):
        self.distance: m_t = distance
        self.mobile_height: m_t = mobile_height
        self.base_height: m_t = base_height
        self.freq: Hz_t = freq
        self.environment: str = environment
        f = freq / MHz(1)
        d = distance / km(1)
        hb = base_height / m(1)
        hm = mobile_height / m(1)
        if hb < 30 or hb > 200:
            raise ValueError('Expected height of base station to be in 30-200m range')
        if hm < 1 or hm > 10:
            raise ValueError('Expected height of mobile station to be in 1-10m range')
        if d < 1 or d > 10:
            raise ValueError('Expected distance to be in 1-10km range')
        # Compute ch, the Antenna height correction factor
        if environment in [OkumuraHataPathLoss.SMALL_CITY, OkumuraHataPathLoss.MEDIUM_CITY, OkumuraHataPathLoss.SUBURBAN, OkumuraHataPathLoss.OPEN]:
            ch = 0.8 + (1.1 * log10(f) - 0.7) * hm - 1.56 * log10(f)
        elif environment == OkumuraHataPathLoss.LARGE_CITY:
            if f < 150:
                raise ValueError('Expected frequency to be in 150MHz - 1.5GHz range')
            elif f <= 200:
                ch = 8.29 * log10(1.54 * hm)**2 - 1.1
            elif f <= 1500:
                ch = 3.2 * log10(11.75 * hm)**2 - 4.97
            else:
                raise ValueError('Expected frequency to be in 150MHz - 1.5GHz range')
        else:
            raise ValueError('Unexpected environment')
        # Path loss in urban areas. Unit: decibel (dB)
        loss = dB(69.55 + 26.16 * log10(f) - 13.82 * log10(hb) - ch + (44.9 - 6.55 * log10(hb)) * log10(d))
        if environment == OkumuraHataPathLoss.SUBURBAN:
            loss = dB(loss - 2 * log10(f/28)**2 - 5.4)
        elif environment == OkumuraHataPathLoss.OPEN:
            loss = dB(loss - 4.78 * log10(f)**2 + 18.33 * log10(f) - 40.94)
        PathLoss.__init__(self, name=name or environment or 'city', loss=loss, oip3=oip3, z_in=z_in, z_out=z_out)

    def schemdraw(self, d: Any, options: dict) -> Any:
        return self.schemdraw_label(
            options,
            dsp.Box(w=d.unit/3, h=d.unit/3).fill('#eeeeff').label(self.name, 'bottom'),
            lbl='d={0:.2f}m\nh_b={0:.2f}m\nh_m={0:.2f}m\n'.format(self.distance, self.base_height, self.mobile_height))

# TODO https://en.wikipedia.org/wiki/Radio_propagation#Models
# TODO add https://en.wikipedia.org/wiki/COST_Hata_model

class ConverterType:
    Down = 'Down'
    Up = 'Up'

class Modulator(TwoPortsElement):
    def __init__(self, name: Optional[str] = None, gain: dB_t = dB(0), nf: dB_t = dB(0), oip3: Optional[dBm_t] = None, lo: Hz_t = Hz(0), converter_type: str = ''):
        TwoPortsElement.__init__(self, name=name or 'Mixer', gain=gain, nf=nf, oip3=oip3)
        self.lo: Hz_t = lo
        assert converter_type != None
        self.converter_type: str = converter_type

    def schemdraw(self, d: Any, options: dict) -> Any:
        mix = dsp.Mixer().anchor('W').fill('navajowhite').label(self.name, 'bottom')
        dsp.Line().at(mix.S).down(d.unit/3)
        dsp.Oscillator().right().anchor('N').fill('navajowhite').label('LO', 'right', ofst=.2)
        return self.schemdraw_label(options, mix)

class Filter(TwoPortsElement):
    Butterworth = None
    def __init__(self, name: Optional[str] = None, gain: dB_t = dB(0), nf: dB_t = dB(0), oip3: Optional[dBm_t] = None, z_in: float = 50, z_out: float = 50, filter_order: int = 0):
        TwoPortsElement.__init__(self, name=name or 'Mixer', gain=gain, nf=nf, oip3=oip3, z_in=z_in, z_out=z_out)
        self.filter_order: int = filter_order

    def schemdraw(self, d: Any, options: dict) -> Any:
        return self.schemdraw_label(options, dsp.Filter().anchor('W').fill('thistle').label(self.name, 'bottom', ofst=.2))

filter = Filter

class BandpassFilter(Filter):
    def __init__(self, name: Optional[str] = None, gain: dB_t = dB(0), nf: dB_t = dB(0), oip3: Optional[dBm_t] = None, z_in: float = 50, z_out: float = 50, filter_order: int = 0, center_freq: Hz_t = Hz(0), bandwidth: Hz_t = Hz(0)):
        Filter.__init__(self, name=name, gain=gain, nf=nf, oip3=oip3, z_in=z_in, z_out=z_out, filter_order=filter_order)
        self.center_freq: Hz_t = center_freq
        self.bandwidth: Hz_t = bandwidth

    def schemdraw(self, d: Any, options: dict) -> Any:
        return self.schemdraw_label(options, dsp.Filter(response='bp').anchor('W').fill('thistle').label(self.name, 'bottom', ofst=.2))

class ButterworthBandpassFilter(BandpassFilter):
    def __init__(self, name: Optional[str] = None, nf: dB_t = dB(0), oip3: Optional[dBm_t] = None, z_in: float = 50, z_out: float = 50, filter_order: int = 0, center_freq: Hz_t = Hz(0), bandwidth: Hz_t = Hz(0), passband_attenuation: dB_t = dB(0), gain: dB_t = dB(0)):
        BandpassFilter.__init__(self, name=name, gain=gain, nf=nf, oip3=oip3, z_in=z_in, z_out=z_out, filter_order=filter_order, center_freq=center_freq, bandwidth=bandwidth)
        self.passband_attenuation: dB_t = passband_attenuation

filter.Butterworth = ButterworthBandpassFilter

def into_schemdraw(elements: List[Element], options: Optional[dict] = None, as_html_table: bool = False) -> Any:
    html = io.StringIO('')
    if options is None:
        options = {}
    options.setdefault('simplified', True)
    options.setdefault('with_gain', not options['simplified'])
    options.setdefault('with_nf', not options['simplified'])
    options.setdefault('with_iip', not options['simplified'])
    options.setdefault('with_oip', not options['simplified'])
    with schemdraw.Drawing() as d:
        if as_html_table:
            d.outfile = None
            d.fig = None
            d.show = False
            d = schemdraw.Drawing()
            d.__enter__()
            d.config(fontsize=12)
        d.config(fontsize=12)
        last_i = len(elements)
        # Previous RfBudget Element
        prev = None
        # Previous SchemDraw Element
        previous = None
        for elt in elements:
            html.write('<td>')
            if previous != None:
                try:
                    anchor = previous.E
                except AttributeError:
                    anchor = None
                if anchor and not as_html_table:
                    the_line = dsp.Line().at(previous.E).length(d.unit/4)
                else:
                    the_line = dsp.Line().length(d.unit/4)
                if isinstance(elt, PathLoss) or isinstance(prev, PathLoss):
                    the_line.color('#FFFFFF00')
            elif not isinstance(previous, Antenna):
                dsp.Line().length(d.unit/4)
            previous = elt.schemdraw(d, options)
            prev = elt
            if as_html_table:
                d.add(previous)
                d._drawsvg(None)
                svg_img = d._repr_svg_()
                html.write(svg_img)
                previous = None
                d.outfile = None
                d.fig = None
                d.show = False
                d.__exit__(None, None, None)
                d = schemdraw.Drawing()
                d.__enter__()
                d.config(fontsize=12)
                html.write('</td>')
        if as_html_table:
            return html.getvalue()            
        if previous != None and not isinstance(elements[-1], Antenna):
            dsp.Arrow().right(d.unit/3)
        return d

class Budget:
    def __init__(self, elements: List[Element] = [], input_freq: Optional[Hz_t] = None, available_input_power: dBm_t = dBm(0), signal_bandwidth: Hz_t = Hz(1), without_oip: bool = False, T_receiver: Optional[kelvin_t] = None):
        self.elements: List[Element] = elements
        self.input_freq: Optional[Hz_t] = input_freq
        self.available_input_power: dBm_t = available_input_power
        self.signal_bandwidth: Hz_t = signal_bandwidth
        self.with_oip: bool = not without_oip
        self.T_receiver: Optional[kelvin_t] = T_receiver
        self.output_freq: List[Hz_t] = []
        self.output_power: List[dBm_t] = []
        self.transducer_gain: List[dB_t] = []
        self.f: List[float] = [] # noise factor
        self.nf: List[dB_t] = [] # noise figure
        self.iip2: List[dBm_t] = []
        self.oip2: List[dBm_t] = []
        self.iip3: List[dBm_t] = []
        self.oip3: List[dBm_t] = []
        self.snr: List[dB_t] = []
        self.capacity: List[float] = []
        self.receiver_thermal_noise_dBm: Optional[dBm_t] = None
        self.update()

    def schemdraw(self, options: Optional[dict] = None, as_html_table: bool = False) -> Any:
        return into_schemdraw(self.elements, options, as_html_table=as_html_table)

    def update(self) -> None:
        nb_elts = len(self.elements)
        # Use dictionnaries to ease getting default value forvfirst stage.
        # Will be converted back to list at the end
        output_freq_dict = {}
        output_power_dict = {}
        transducer_gain_dict = {}
        f_dict = {}
        nf_dict = {}
        snr_dict = {}
        capacity_dict = {}
        oip3_dict = {}

        k_boltzmann = 1.38e-23
        if self.T_receiver is None:
            self.T_receiver = kelvin(290)
        receiver_thermal_noise_W = k_boltzmann * self.T_receiver * self.signal_bandwidth
        self.receiver_thermal_noise_dBm = dBm(10 * log10(receiver_thermal_noise_W * 1000))

        oip3_parts = []

        for stage, elt in enumerate(self.elements):
            # Output power
            output_power_dict[stage] = output_power_dict.get(stage-1, self.available_input_power) + elt.gain
            transducer_gain_dict[stage] = transducer_gain_dict.get(stage-1, 0) + elt.gain

            # Noise factor & figure
            # See http://www.diva-portal.org/smash/get/diva2:1371826/FULLTEXT01.pdf
            # and https://en.wikipedia.org/wiki/Friis_formulas_for_noise
            # and https://www.microwaves101.com/encyclopedias/noise-figure-one-and-two-friis-and-ieee
            if stage == 0:
                f_dict[stage] = 10**(elt.nf/10)
            else:
                f_dict[stage] = f_dict[stage - 1] + (10**(elt.nf/10) - 1) / (10**(transducer_gain_dict[stage-1]/10))
            nf_dict[stage] = dB(10 * log10(f_dict[stage]))

            # Output frequency
            prev_freq = output_freq_dict.get(stage-1, self.input_freq)
            if isinstance(elt, Modulator):
                if elt.converter_type == ConverterType.Down:
                    output_freq_dict[stage] = Hz_t(prev_freq - elt.lo)
                else:
                    output_freq_dict[stage] = Hz_t(prev_freq + elt.lo)
            else:
                output_freq_dict[stage] = prev_freq

            # SNR
            # See https://www.commagility.com/images/pdfs/white_papers/Introduction_to_RF_Link_Budgeting_CommAgility.pdf
            noise_at_stage = self.receiver_thermal_noise_dBm + nf_dict[stage]
            snr_dict[stage] = dB(output_power_dict[stage] - noise_at_stage - transducer_gain_dict[stage])

            # Capacity
            snr_linear = 10**(snr_dict[stage]/10)
            capacity_dict[stage] = self.signal_bandwidth * log2(1 + snr_linear)

            # OIP3 partial computation
            if self.with_oip:
                if stage == 0:
                    oip3_linear = 10**(elt.oip3/10) if elt.oip3 is not None else float('inf')
                    oip3_parts.insert(stage, oip3_linear)
                    oip3_dict[0] = elt.oip3 if elt.oip3 is not None else dBm(float('inf'))
                else:
                    gain_linear = 10**(elt.gain/10)
                    oip3_linear = 10**(elt.oip3/10) if elt.oip3 is not None else float('inf')
                    oip3_parts = [gain_linear * p for p in oip3_parts]
                    oip3_parts.insert(stage, oip3_linear)
                    oip3_dict[stage] = dBm(10 * log10(1 / sum([1.0/p for p in oip3_parts])))

        # Convert back from dictionnary to list
        self.output_power = [dBm(output_power_dict[stage]) for stage, elt in enumerate(self.elements)]
        self.transducer_gain = [dB(transducer_gain_dict[stage]) for stage, elt in enumerate(self.elements)]
        self.f = [float(f_dict[stage]) for stage, elt in enumerate(self.elements)]
        self.nf = [dB(nf_dict[stage]) for stage, elt in enumerate(self.elements)]
        self.output_freq = [Hz_t(output_freq_dict[stage]) for stage, elt in enumerate(self.elements)]
        self.snr = [dB(snr_dict[stage]) for stage, elt in enumerate(self.elements)]
        self.capacity = [float(capacity_dict[stage]) for stage, elt in enumerate(self.elements)]
        if self.with_oip:
            self.oip3 = [dBm(oip3_dict[stage]) for stage, elt in enumerate(self.elements)]
            self.iip3 = [dBm(self.oip3[stage] - self.transducer_gain[stage]) for stage, elt in enumerate(self.elements)]

    def display(self, with_icons: bool = False, options: Optional[dict] = None) -> Any:
        try:
            from IPython.display import display, HTML
            return display(HTML(self.to_html(with_icons=with_icons, options=options)))
        except ImportError:
            self.print()
            return None

    def print(self) -> None:
        print("rfbudget with properties:")
        print("Elements: [1x{} rf.internal.rfbudget.Element]".format(len(self.elements)))
        print("InputFrequency:", self.input_freq, "Hz")
        print("AvailableInputPower:", self.available_input_power, " dBm")
        print("SignalBandwidth:", self.signal_bandwidth, "Hz")
        print("Solver: Friis")
        print("")
        print("Analysis Results")
        print("ThermalNoise:    (dBm)\t ", self.receiver_thermal_noise_dBm)
        print("OutputFrequency: (Hz)\t", self.output_freq)
        print("OutputPower:     (dBm)\t", self.output_power)
        print("TransducerGain:  (dB)\t", self.transducer_gain)
        print("Noisefigure:     (dB)\t", self.nf)
        if self.with_oip:
            print("IIP3:            (dBm)\t", self.iip3)
            print("OIP3:            (dBm)\t", self.oip3)
        print("SNR:             (dB)\t", self.snr)
        print("ChannelCapacity: (bps)\t", self.capacity)

    def html_cell_format(self, a_list: List[Any]) -> str:
        return "".join(map(lambda v: "<td>{0:.2f}</td>".format(v), a_list))

    def to_html(self, with_icons: bool = False, options: Optional[dict] = None) -> str:
        html = io.StringIO('')
        print("<div>\n", file=html)
        print("<h3>RF budget with properties</h3>", file=html)
        print("<table>", file=html)
        print("<tr><td>Elements:</td><td>[1x{} rf.internal.rfbudget.Element]</td></tr>".format(len(self.elements)), file=html)
        print("<tr><td>InputFrequency</td><td>", self.input_freq, "Hz</td></tr>", file=html)
        print("<tr><td>AvailableInputPower</td><td>", self.available_input_power, " dBm</td></tr>", file=html)
        print("<tr><td>SignalBandwidth</td><td>", self.signal_bandwidth, "Hz</td></tr>", file=html)
        print("<tr><td>Solver</td><td>Friis</td></tr>", file=html)
        print("</table>", file=html)
        print("<h3>Analysis Results</h3>", file=html)
        print("<table>", file=html)
        if with_icons:
            print("<tr><td></td><td></td>", self.schemdraw(options, as_html_table=True), "</tr>", file=html)
        print("<tr><td>ThermalNoise:</td><td>(dBm)</td>", "<td>{0:.2f}</td>".format(self.receiver_thermal_noise_dBm), "</tr>", file=html)
        print("<tr><td>OutputFrequency:</td><td>(Hz)</td>", self.html_cell_format(self.output_freq), "</tr>", file=html)
        print("<tr><td>OutputPower:</td><td>(dBm)</td>", self.html_cell_format(self.output_power), "</tr>", file=html)
        print("<tr><td>TransducerGain:</td><td>(dB)</td>", self.html_cell_format(self.transducer_gain), "</tr>", file=html)
        print("<tr><td>Noisefigure:</td><td>(dB)</td>", self.html_cell_format(self.nf), "</tr>", file=html)
        if self.with_oip:
            print("<tr><td>IIP3:</td><td>(dBm)</td>", self.html_cell_format(self.iip3), "</tr>", file=html)
            print("<tr><td>OIP3:</td><td>(dBm)</td>", self.html_cell_format(self.oip3), "</tr>", file=html)
        print("<tr><td>SNR:</td><td>(dB)</td>", self.html_cell_format(self.snr), "</tr>", file=html)
        print("<tr><td>ChannelCapacity:</td><td>(bps)</td>", self.html_cell_format(self.capacity), "</tr>", file=html)
        print("</table>", file=html)
        print("</div>\n", file=html)
        return html.getvalue()

budget = Budget