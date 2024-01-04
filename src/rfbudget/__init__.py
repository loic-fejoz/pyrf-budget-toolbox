from numpy import log10, log2
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
    
    def schemdraw_label(self, options, b):
        lbl = ''
        if options['with_gain'] and self.gain:
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

def into_schemdraw(elements, options=None):
    if options is None:
        options = {}
    options.setdefault('simplified', True)
    options.setdefault('with_gain', not options['simplified'])
    options.setdefault('with_nf', not options['simplified'])
    options.setdefault('with_iip', not options['simplified'])
    options.setdefault('with_oip', not options['simplified'])
    with schemdraw.Drawing() as d:
        d.config(fontsize=12)
        last_i = len(elements)
        previous = None
        for elt in elements:
            if previous != None:
                try:
                    anchor = previous.E
                except AttributeError:
                    anchor = None
                if anchor:
                    dsp.Line().at(previous.E).length(d.unit/4)
                else:
                    dsp.Line().length(d.unit/4)
            elif not isinstance(previous, Antenna):
                dsp.Line().length(d.unit/4)
            previous = elt.schemdraw(d, options)
        if previous != None and not isinstance(elements[-1], Antenna):
            dsp.Arrow().right(d.unit/3)
        return d

class Budget:
    def __init__(self, elements=[], input_freq=None, available_input_power=0, signal_bandwidth=1, without_oip=False):
        self.elements = elements
        self.input_freq = input_freq
        self.available_input_power = available_input_power
        self.signal_bandwidth = signal_bandwidth
        self.with_oip = not without_oip
        self.update()

    def schemdraw(self, options=None):
        return into_schemdraw(self.elements, options)

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
        T_receiver = 290 # Kelvin
        receiver_thermal_noise_W = k_boltzmann * T_receiver * self.signal_bandwidth
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

    def display(self):
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

budget = Budget