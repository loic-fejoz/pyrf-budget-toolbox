from numpy import log10
from rfbudget import *

the_filter = Loss(name="Filter's Loss", loss=1)

a1 = Amplifier(
    name='LNA',
    gain=10,
    nf=3,
)

b1 = budget(
    elements=[the_filter, a1],
    input_freq=MHz(144),
    available_input_power=0,
    signal_bandwidth=kHz(1),
    without_oip=True
)

b1.display()
opt = {'with_gain': True, 'with_nf': True, 'simplified': True}
d = b1.schemdraw(opt)
# d.draw()
d.save('test3-1.svg')

b2 = budget(
    elements=[a1, the_filter],
    input_freq=MHz(144),
    available_input_power=0,
    signal_bandwidth=kHz(1),
    without_oip=True
)

b2.display()

d = b2.schemdraw(opt)
# d.draw()
d.save('test3-2.svg')