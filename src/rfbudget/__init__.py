import io
from numpy import log10, log2
import math
from math import sin, cos, sqrt
import schemdraw
from schemdraw import dsp

def GHz(f):
    return f * 1e9

def MHz(f):
    return f * 1e6

def kHz(f):
    return f * 1e3

def dB(v):
    return v

def dBm(v):
    return v

def watt_to_dBm(v):
    return 10 * log10(v * 1000)

def m(v):
    return v

def dm(v):
    return 10 * v

def hm(v):
    return 100 * v

def km(v):
    return 1000 * v

def degree(v):
    return v

def radians(v):
    return math.degrees(v)

def to_radians(v):
    return math.radians(v)

def kelvin(v):
    return v

def celsius(v):
    return v + 273.15

def to_celsius(v):
    return v - 273.15

EARTH_RADIUS = km(6378.166)

def distance_max(elevation, orbit_radius, r=None):
    """
    elevations in degrees
    """
    el = math.radians(elevation)
    if r is None:
        r = EARTH_RADIUS # Earth Radius
    # return -1 * r * sin(elevation) + sqrt((r * sin(elevation))**2 + height**2 + 2 * r * height)
    return r *(math.sqrt((((orbit_radius**2)/(r**2))-((math.cos(el))**2)))-math.sin(el))

class Orbit:
    def __init__(self, apogee, perigee=None, inclination=None, planet_radius=None):
        if perigee is None:
            perigee = apogee
        if planet_radius is None:
            planet_radius = EARTH_RADIUS
        self.planet_radius = planet_radius
        self.apogee = apogee
        self.perigee = perigee
        self.inclination = inclination
        self.semi_major_axis = (self.apogee + self.perigee + 2 * planet_radius) / 2
        self.eccentricity = ((self.apogee + planet_radius) - (self.perigee + planet_radius)) / ((self.apogee + planet_radius) + (self.perigee + planet_radius))
        self.mean_altitude = (self.apogee + self.perigee) / 2
        self.mean_radius = planet_radius + self.mean_altitude

    def slant_range(self, elevation):
        return distance_max(elevation, self.mean_radius, self.planet_radius)

class Element:
    """
        nf is noise figure
    """
    def __init__(self, name=None, gain=0, nf=0, oip3=None, iip3=None):
        self.name = name or ''
        self.gain = gain
        self.nf = nf
        self.iip3 = iip3
        self.oip3 = oip3
        if oip3 == None and iip3 != None and gain != None:
            self.oip3 = iip3 + gain
        elif iip3 == None and oip3 != None and gain != None:
            self.iip3 = oip3 - gain
        else:
            self.oip3 = float('inf')

    def schemdraw(self, d, options):
        return self.schemdraw_label(options, dsp.Box(w=d.unit/3, h=d.unit/3).label(self.name, 'bottom'))
    
    def schemdraw_label(self, options, b, lbl=None):
        if lbl is None:
            lbl = ''
        else:
            lbl = str(lbl)
        if options['with_gain'] and self.gain != None:
            lbl += 'gain={0:.2f}dB\n'.format(self.gain)
        if options['with_nf'] and self.nf:
            lbl += 'NF={0:.2f}dB\n'.format(self.nf)
        if options['with_iip'] and self.iip3:
            lbl += 'IIP3={0:.2f}dB\n'.format(self.iip3)
        if options['with_oip'] and self.oip3:
            lbl += 'OIP3={0:.2f}dB\n'.format(self.oip3)
        return b.label(lbl, 'top', ofst=(-0.2, 0.6), fontsize=6)

class Antenna(Element):
    def __init__(self, name=None, gain=0, nf=0, iip3=None, oip3=None, z=50):
        Element.__init__(self, name=name or 'Antenna', gain=gain, nf=nf, iip3=iip3, oip3=oip3)
        self.z = z

    def schemdraw(self, d, options):
        return self.schemdraw_label(options, dsp.Antenna().label(self.name, 'bottom'))

class NPort(Element):
    def __init__(self):
        pass

class TwoPortsElement(Element):
    def __init__(self, name=None, gain=0, nf=0, iip3=None, oip3=None, z_in=50, z_out=50):
        Element.__init__(self, name=name, gain=gain, nf=nf, iip3=iip3, oip3=oip3)
        self.z_in = z_in
        self.z_out = z_out

class Amplifier(TwoPortsElement):
    def __init__(self, name=None, gain=0, nf=0, iip3=None, oip3=None, z_in=50, z_out=50):
        TwoPortsElement.__init__(self, name=name or 'LNA', gain=gain, nf=nf, iip3=iip3, oip3=oip3, z_in=z_in, z_out=z_out)

    def schemdraw(self, d, options):
        return self.schemdraw_label(options, dsp.Amp().fill('lightblue').label(self.name, 'bottom'))

class Loss(TwoPortsElement):
    def __init__(self, name=None, loss=None, oip3=None, z_in=50, z_out=50):
        TwoPortsElement.__init__(self, name=name or 'Loss', gain=-loss, nf=loss, oip3=oip3, z_in=z_in, z_out=z_out)

    def schemdraw(self, d, options):
        return self.schemdraw_label(options, dsp.Box(w=d.unit/3, h=d.unit/3).fill('#ffeeee').label(self.name, 'bottom'))

class PathLoss(Loss):
    def __init__(self, name=None, loss=None, oip3=None, z_in=50, z_out=50):
        Loss.__init__(self, name=name or 'PathLoss', loss=loss, oip3=oip3, z_in=z_in, z_out=z_out)

class FreeSpacePathLossFriis(PathLoss):
    def __init__(self, name=None, distance=None, freq=None, oip3=None, z_in=50, z_out=50):
        self.distance = distance
        loss = 20 * log10(distance) + 20 * log10(freq) - 147.55
        PathLoss.__init__(self, name=name or 'FPSL', loss=loss, oip3=oip3, z_in=z_in, z_out=z_out)

    def schemdraw(self, d, options):
        return self.schemdraw_label(
            options,
            dsp.Box(w=d.unit/3, h=d.unit/3).fill('#eeeeff').label(self.name, 'bottom'),
            lbl='d={0:.2f}m\n'.format(self.distance))

class RadarFreeSpaceBasicLoss(PathLoss):
    """
    https://www.itu.int/dms_pubrec/itu-r/rec/p/R-REC-P.525-2-199408-S!!PDF-E.pdf
    """
    def __init__(self, name=None, distance=None, sigma=None, freq=None, oip3=None, z_in=50, z_out=50):
        """
        Two way loss of the signal of a radar.
        distance: distance from the radar to the target
        sigma: radar target cross-section (m²)
        """
        self.distance = distance
        self.sigma = sigma
        loss = 103.4 + 20 * log10(freq / MHz(1)) + 40 * log10(distance / km(1)) - 10 * log10(sigma)
        PathLoss.__init__(self, name=name or 'FPSL', loss=loss, oip3=oip3, z_in=z_in, z_out=z_out)

    def schemdraw(self, d, options):
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

    def __init__(self, name=None,
                 distance=None,
                 freq=None,
                 base_height=None,
                 mobile_height=None,
                 environment = None,
                 oip3=None, z_in=50, z_out=50):
        self.distance = distance
        self.mobile_height = mobile_height
        self.base_height = base_height
        self.freq = freq
        self.environment = environment
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
        if environment in [OkumuraHataPathLoss.SMALL, OkumuraHataPathLoss.MEDIUM, OkumuraHataPathLoss.SUBURBAN, OkumuraHataPathLoss.OPEN]:
            ch = 0.8 + (1.1 * log10(f) - 0.7) * hm - 1.56 * log10(f)
        elif environment == OkumuraHataPathLoss.LARGE:
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
        loss = 69.55 + 26.16 * log10(f) - 13.82 * log10(hb) - ch + (44.9 - 6.55 * log10(hb)) * log10(d)
        if environment == OkumuraHataPathLoss.SUBURBAN:
            loss = loss - 2 * log10(f/28)**2 - 5.4
        elif environment == OkumuraHataPathLoss.OPEN:
            loss = loss - 4.78 * log10(f)**2 + 18.33 * log10(f) - 40.94
        PathLoss.__init__(self, name=name or environment or 'city', loss=loss, oip3=oip3, z_in=z_in, z_out=z_out)

    def schemdraw(self, d, options):
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
    def __init__(self, name=None, gain=0, nf=0, oip3=None, lo=0, converter_type=None):
        TwoPortsElement.__init__(self, name=name or 'Mixer', gain=gain, nf=nf, oip3=oip3)
        self.lo = lo
        assert converter_type != None
        self.converter_type = converter_type

    def schemdraw(self, d, options):
        mix = dsp.Mixer().anchor('W').fill('navajowhite').label(self.name, 'bottom')
        dsp.Line().at(mix.S).down(d.unit/3)
        dsp.Oscillator().right().anchor('N').fill('navajowhite').label('LO', 'right', ofst=.2)
        return self.schemdraw_label(options, mix)

class Filter(TwoPortsElement):
    Butterworth = None
    def __init__(self, name=None, gain=0, nf=0, oip3=None, z_in=50, z_out=50, filter_order=0):
        TwoPortsElement.__init__(self, name=name or 'Mixer', gain=gain, nf=nf, oip3=oip3, z_in=z_in, z_out=z_out)
        self.filter_order = filter_order

    def schemdraw(self, d, options):
        return self.schemdraw_label(options, dsp.Filter().anchor('W').fill('thistle').label(self.name, 'bottom', ofst=.2))

filter = Filter

class BandpassFilter(Filter):
    def __init__(self, name=None, gain=0, nf=0, oip3=None, z_in=50, z_out=50, filter_order=0, center_freq=0, bandwidth=0):
        Filter.__init__(self, name=name, gain=gain, nf=nf, oip3=oip3, z_in=z_in, z_out=z_out, filter_order=filter_order)
        self.center_freq = center_freq
        self.bandwidth = bandwidth

    def schemdraw(self, d, options):
        return self.schemdraw_label(options, dsp.Filter(response='bp').anchor('W').fill('thistle').label(self.name, 'bottom', ofst=.2))

class ButterworthBandpassFilter(BandpassFilter):
    def __init__(self, name=None, nf=0, oip3=None, z_in=50, z_out=50, filter_order=0, center_freq=0, bandwidth=0, passband_attenuation=0, gain=0):
        BandpassFilter.__init__(self, name=name, gain=gain, nf=nf, oip3=oip3, z_in=z_in, z_out=z_out, filter_order=filter_order, center_freq=center_freq, bandwidth=bandwidth)
        self.passband_attenuation = passband_attenuation

filter.Butterworth = ButterworthBandpassFilter

def into_schemdraw(elements, options=None, as_html_table=False):
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
    def __init__(self, elements=[], input_freq=None, available_input_power=0, signal_bandwidth=1, without_oip=False, T_receiver=None):
        self.elements = elements
        self.input_freq = input_freq
        self.available_input_power = available_input_power
        self.signal_bandwidth = signal_bandwidth
        self.with_oip = not without_oip
        self.T_receiver = T_receiver
        self.update()

    def schemdraw(self, options=None, as_html_table=False):
        return into_schemdraw(self.elements, options, as_html_table=as_html_table)

    def update(self):
        nb_elts = len(self.elements)
        # Use dictionnaries to ease getting default value forvfirst stage.
        # Will be converted back to list at the end
        self.output_freq = {}
        self.output_power = {}
        self.transducer_gain = {}
        self.f = {} # noise factor
        self.nf = {} # noise figure
        self.iip2 = {}
        self.oip2 = {}
        self.iip3 = {}
        self.oip3 = {}
        self.iip2 = {}
        self.snr = {}
        self.capacity = {}

        k_boltzmann = 1.38e-23
        if self.T_receiver is None:
            self.T_receiver = 290 # Kelvin
        receiver_thermal_noise_W = k_boltzmann * self.T_receiver * self.signal_bandwidth
        self.receiver_thermal_noise_dBm = 10 * log10(receiver_thermal_noise_W * 1000)

        oip3_parts = []

        for stage, elt in enumerate(self.elements):
            # Output power
            self.output_power[stage] = self.output_power.get(stage-1, self.available_input_power) + elt.gain

            self.transducer_gain[stage] = self.transducer_gain.get(stage-1, 0) + elt.gain

            # Noise factor & figure
            # See http://www.diva-portal.org/smash/get/diva2:1371826/FULLTEXT01.pdf
            # and https://en.wikipedia.org/wiki/Friis_formulas_for_noise
            # and https://www.microwaves101.com/encyclopedias/noise-figure-one-and-two-friis-and-ieee
            if stage == 0:
                self.f[stage] = 10**(elt.nf/10)
            else:
                self.f[stage] = self.f[stage - 1] + (10**(elt.nf/10) - 1) / (10**(self.transducer_gain[stage-1]/10))
            self.nf[stage] = 10 * log10(self.f[stage])

            # Output frequency
            prev_freq = self.output_freq.get(stage-1, self.input_freq)
            if isinstance(elt, Modulator):
                if elt.converter_type == ConverterType.Down:
                    self.output_freq[stage] = prev_freq - elt.lo
                else:
                    self.output_freq[stage] = prev_freq + elt.lo
            else:
                self.output_freq[stage] = prev_freq

            # SNR
            # See https://www.commagility.com/images/pdfs/white_papers/Introduction_to_RF_Link_Budgeting_CommAgility.pdf
            noise_at_stage = self.receiver_thermal_noise_dBm + self.nf[stage]
            self.snr[stage] = self.output_power[stage] - noise_at_stage - self.transducer_gain[stage]

            # Capacity
            snr = 10**(self.snr[stage]/10)
            self.capacity[stage] = self.signal_bandwidth * log2(1 + snr)

            # OIP3 partial computation
            if self.with_oip:
                if stage == 0:
                    oip3_parts.insert(stage, 10**(elt.oip3/10))
                    self.oip3[0] = elt.oip3
                else:
                    gain = 10**(elt.gain/10)
                    oip3 = 10**(elt.oip3/10)
                    oip3_parts = [gain * p for p in oip3_parts]
                    oip3_parts.insert(stage, oip3)
                    print(oip3_parts)
                    self.oip3[stage] = 10 * log10(1 / sum([1.0/p for p in oip3_parts]))

        # Convert back from dictionnary to list
        self.output_power = [self.output_power[stage] for stage, elt in enumerate(self.elements)]
        self.transducer_gain = [self.transducer_gain[stage] for stage, elt in enumerate(self.elements)]
        self.f = [self.f[stage] for stage, elt in enumerate(self.elements)]
        self.nf = [self.nf[stage] for stage, elt in enumerate(self.elements)]
        self.output_freq = [self.output_freq[stage] for stage, elt in enumerate(self.elements)]
        self.snr = [self.snr[stage] for stage, elt in enumerate(self.elements)]
        self.capacity = [self.capacity[stage] for stage, elt in enumerate(self.elements)]
        if self.with_oip:
            self.oip3 = [self.oip3[stage] for stage, elt in enumerate(self.elements)]
            self.iip3 = [self.oip3[stage] - self.transducer_gain[stage] for stage, elt in enumerate(self.elements)]

    def display(self, with_icons=False, options=None):
        try:
            from IPython.display import display, HTML
            return display(HTML(self.to_html(with_icons=with_icons, options=options)))
        except ImportError:
            self.print()
            return None

    def print(self):
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

    def html_cell_format(self, a_list):
        return "".join(map(lambda v: "<td>{0:.2f}</td>".format(v), a_list))

    def to_html(self, with_icons=False, options=None):
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