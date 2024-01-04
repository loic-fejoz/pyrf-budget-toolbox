from numpy import log10, log2

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
        self.name = name
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
        TwoPortsElement.__init__(self, name=name, gain=gain, nf=nf, iip3=iip3, oip3=oip3, z_in=z_in, z_out=z_out)

class Loss(TwoPortsElement):
    def __init__(self, name=None, loss=None, oip3=None, z_in=50, z_out=50):
        TwoPortsElement.__init__(self, name=name, gain=-loss, nf=loss, oip3=oip3, z_in=z_in, z_out=z_out)

class ConverterType:
    Down = 'Down'
    Up = 'Up'

class Modulator(TwoPortsElement):
    def __init__(self, name=None, gain=0, nf=0, oip3=None, lo=0, converter_type=None):
        TwoPortsElement.__init__(self, name=name, gain=gain, nf=nf, oip3=oip3)
        self.lo = lo
        assert converter_type != None
        self.converter_type = converter_type

class Filter(TwoPortsElement):
    Butterworth = None
    def __init__(self, name=None, gain=0, nf=0, oip3=None, z_in=50, z_out=50, filter_order=0):
        TwoPortsElement.__init__(self, name=name, gain=gain, nf=nf, oip3=oip3, z_in=z_in, z_out=z_out)
        self.filter_order = filter_order

filter = Filter

class BandpassFilter(Filter):
    def __init__(self, name=None, gain=0, nf=0, oip3=None, z_in=50, z_out=50, filter_order=0, center_freq=0, bandwidth=0):
        Filter.__init__(self, name=name, gain=gain, nf=nf, oip3=oip3, z_in=z_in, z_out=z_out, filter_order=filter_order)
        self.center_freq = center_freq
        self.bandwidth = bandwidth

class ButterworthBandpassFilter(BandpassFilter):
    def __init__(self, name=None, nf=0, oip3=None, z_in=50, z_out=50, filter_order=0, center_freq=0, bandwidth=0, passband_attenuation=0, gain=0):
        BandpassFilter.__init__(self, name=name, gain=gain, nf=nf, oip3=oip3, z_in=z_in, z_out=z_out, filter_order=filter_order, center_freq=center_freq, bandwidth=bandwidth)
        self.passband_attenuation = passband_attenuation

filter.Butterworth = ButterworthBandpassFilter

class Budget:
    def __init__(self, elements=[], input_freq=None, available_input_power=0, signal_bandwidth=1, without_oip=False):
        self.elements = elements
        self.input_freq = input_freq
        self.available_input_power = available_input_power
        self.signal_bandwidth = signal_bandwidth
        self.with_oip = not without_oip
        self.update()

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