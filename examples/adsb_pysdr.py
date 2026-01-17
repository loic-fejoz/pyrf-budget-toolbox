#! python3
from rfbudget import (
    MHz,
    watt_to_dBm,
    Antenna,
    dB,
    FreeSpacePathLossFriis,
    km,
    Loss,
    budget,
)


# Inspired from https://pysdr.org/content/link_budgets.html

adsb_freq = MHz(1090)
adsb_bandwidth = MHz(2)
transmit_power_dbm = watt_to_dBm(100)

tx_antenna = Antenna(
    name="TxAnt",
    gain=dB(3),
)

freespace = FreeSpacePathLossFriis(
    distance=km(30),
    freq=adsb_freq,
)

rx_antenna = Antenna(
    name="RxAnt",
    gain=dB(0),
)

other_loss = Loss(name="Various Loss", loss=dB(6))

adbs_budget = budget(
    elements=[tx_antenna, freespace, rx_antenna, other_loss],
    input_freq=adsb_freq,
    available_input_power=transmit_power_dbm,
    signal_bandwidth=adsb_bandwidth,
    without_oip=True,
)

adbs_budget.display()
opt = {"with_gain": True, "with_nf": True, "simplified": True}
d = adbs_budget.schemdraw(opt)
# d.draw()
d.save("test_adsb.svg")
# print(adbs_budget.to_html(with_icons=True))
