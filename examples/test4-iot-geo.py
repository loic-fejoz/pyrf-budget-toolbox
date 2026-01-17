from rfbudget import (
    GHz,
    Antenna,
    dB,
    FreeSpacePathLossFriis,
    km,
    Loss,
    budget,
    watt_to_dBm,
    kHz,
)

tx_freq = GHz(2.4)

tx_antenna = Antenna(
    name="TxAnt",
    gain=dB(2),
)

freespace_up = FreeSpacePathLossFriis(
    distance=km(36000),
    freq=tx_freq,
)

rx_sat_antenna = Antenna(
    name="RxSatAnt",
    gain=dB(3),
)

# a1 = Amplifier(
#     name='LNA',
#     gain=,
# )

tx_sat_antenna = Antenna(
    name="TxSatAnt",
    gain=dB(3),
)

freespace_down = FreeSpacePathLossFriis(
    distance=km(36000),
    freq=tx_freq,
)

other_loss = Loss(name="Various Loss", loss=dB(6))

opt = {"with_gain": True, "with_nf": True, "simplified": True}

b = budget(
    elements=[
        tx_antenna,
        freespace_up,
        rx_sat_antenna,
        tx_sat_antenna,
        freespace_down,
        other_loss,
    ],
    input_freq=tx_freq,
    available_input_power=watt_to_dBm(1),
    signal_bandwidth=kHz(10),
    without_oip=True,
)

b.display()

d = b.schemdraw(opt)
# d.draw()
d.save("test4-iot-geo.svg")
