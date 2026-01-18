from rfbudget import Cable, m, dB, watt_to_dBW
from pytest import approx

def test_cable_loss():
    # 10m cable with 0.05 dB/m loss should have 0.5 dB total loss (gain = -0.5 dB)
    c = Cable(length=m(10), loss_per_m=dB(0.05))
    assert c.gain == -0.5

def test_cable_loss_zero():
    c = Cable(length=m(0), loss_per_m=dB(0.05))
    assert c.gain == 0

def test_watt_to_dBW():
    assert watt_to_dBW(1) == 0
    assert watt_to_dBW(10) == 10
    assert watt_to_dBW(100) == 20
    assert watt_to_dBW(5) == approx(6.9897, 0.0001)
