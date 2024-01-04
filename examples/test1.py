from numpy import log10
from rfbudget import *


# Inspired from https://fr.mathworks.com/help/rf/ug/superheterodyne-receiver-using-rf-budget-analyzer-app.html

center_freq=GHz(5.8)
bwpass = MHz(20)
Z = 132.986

tr_switch = Element(
    name='TR_Switch',
    gain=-1.3,
    nf=2.3,
    oip3=37
)

insertion_loss = 1

b1 = filter.Butterworth(
    name='RF_filter',
    filter_order=6,
    passband_attenuation=10*log10(2),
    center_freq=center_freq,
    bandwidth=bwpass,
    z_out=50,
)

a1 = Amplifier(
    name='LNA',
    gain=15-insertion_loss,
    nf=1.5,
    oip3=26,
    z_in=Z
)

a2 = Amplifier(
    name='Gain',
    gain=10.5,
    nf=3.5,
    oip3=23,
)

d = Modulator(
    name='Demod',
    gain=-7,
    nf=7,
    oip3=15,
    lo=GHz(5.4),
    converter_type=ConverterType.Down,
)

b2 = filter.Butterworth(
    name='IF_filter',
    filter_order=4,
    passband_attenuation=10*log10(2),
    center_freq=MHz(400),
    bandwidth=MHz(5),
    z_out=50,
)

a3 = Amplifier(
    name='IF_Amp',
    gain=40-insertion_loss,
    nf=2.5,
    oip3=37,
    z_in = Z
)

a4 = Amplifier(
    name='AGC',
    gain=17.5,
    nf=4.3,
    oip3=36,
)

superhet = budget(
    elements=[tr_switch, b1, a1, a2, d, b2, a3, a4],
    input_freq=GHz(5.8),
    available_input_power=-66,
    signal_bandwidth=MHz(20),
)

superhet.display()
d = superhet.schemdraw({'simplified': False})
d.draw()
# d.save('test1.svg')