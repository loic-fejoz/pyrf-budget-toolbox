from rfbudget import Element, budget, kelvin, dB, nf_to_temp, temp_to_nf, Loss
from pytest import approx
import math

def test_nf_temp_conversions():
    # T = T0 * (F - 1)
    # For NF = 3dB, F ~ 2.0. T = 290 * (2 - 1) = 290K
    nf = dB(10 * math.log10(2.0))
    t = nf_to_temp(nf)
    assert t == approx(290.0, 0.1)
    
    # Reverse
    assert temp_to_nf(kelvin(290.0)) == approx(nf, 0.1)

def test_noise_regression_standard_t0():
    """
    Ensure that for T_receiver = 290K, the results match the previous implementation (T0 * F).
    """
    # NF = 3dB (F=2)
    # Previous: P_noise = k * 290 * 2 * B
    # New: P_noise = k * (290 + 290*(2-1)) * B = k * (290 + 290) * B = k * 580 * B
    # Both are equal.
    
    nf = dB(3)
    b = budget(
        elements=[Element("E1", gain=dB(10), nf=nf)],
        T_receiver=kelvin(290),
        signal_bandwidth=1000
    )
    
    k = 1.38e-23
    expected_noise_W = k * 580 * 1000
    expected_noise_dBm = 10 * math.log10(expected_noise_W * 1000)
    
    # In the library, total_noise_dBm is calculated in update() and used for SNR.
    # We can check SNR or infer from SNR.
    # SNR = P_out - P_noise_dBm - G
    p_in = 0 # dBm
    p_out = 10 # dBm
    # SNR = 10 - expected_noise_dBm - 10 = -expected_noise_dBm
    assert b.snr[0] == approx(p_out - expected_noise_dBm - 10, 0.01)

def test_noise_manual_formula_satellite():
    """
    Verify the satellite link formula from fosm-1.qmd: T_sys = Ta + Teff
    """
    Ta = kelvin(110)
    T_lna = kelvin(15)
    b = budget(
        elements=[Element("LNA", gain=dB(25), temp=T_lna)],
        T_receiver=Ta,
        signal_bandwidth=1000
    )
    
    # Tsys = Ta + T_lna = 110 + 15 = 125K
    # total_noise_temp[0] is referred to Antenna input.
    assert b.total_noise_temp[0] == approx(125.0, 0.01)

def test_loss_temp_to_nf():
    # Loss = 3dB (L=2). Physical temp = 290K.
    # Te = (L-1)*Tp = (2-1)*290 = 290K.
    # NF = 10*log10(1 + Te/290) = 10*log10(1 + 1) = 3dB.
    l = budget(
        elements=[Loss("L1", loss=dB(3), temp=kelvin(290))]
    )
    assert l.elements[0].nf == approx(3.0, 0.01)
