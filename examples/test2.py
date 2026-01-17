from rfbudget import NPort, Amplifier, Modulator, GHz, ConverterType, budget

# Inspired from https://fr.mathworks.com/help/rf/ug/visualizing-rf-budget-analysis-over-bandwidth.html
f1 = NPort(datafile="RFBudget_RF.s2p", name="RFBandpassfilter")

a1 = Amplifier(name="RFAmplifier", gain=11.53, nf=1.3, oip3=35)

d = Modulator(
    name="Demodulator",
    gain=-6,
    nf=4,
    oip3=50,
    lo=GHz(2.03),
    converter_type=ConverterType.Down,
)

f2 = NPort(datafile="RFBudget_IF.s2p", name="IFBandpassfilter")

a2 = Amplifier(name="IFAmplifier", gain=30, nf=8, oip3=37)

b = budget(
    elements=[f1, a1, d, f2, a2],
    input_freq=2.1e9,
    available_input_power=-30,
    signal_bandwidth=45e6,
)
