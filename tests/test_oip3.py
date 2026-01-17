from rfbudget import Amplifier, budget
from pytest import approx

def test_iip3_2_amp():
    """
    Example from https://www.youtube.com/watch?v=pYs3x4-2G2o&t=305s
    """
    a1 = Amplifier(gain=10, iip3=20, name='A1')
    assert a1.oip3 == 30
    a2 = Amplifier(gain=20, iip3=0, name='A2')
    assert a2.oip3 == 20

    budget1 = budget(elements=[a1, a2])
    assert budget1.output_power[-1] == approx(30, 0.1)
    assert budget1.oip3[-1] == approx(20, 0.1)
    assert budget1.iip3[-1] == approx(-10, 0.1)

    budget2 = budget(elements=[a2, a1])
    assert budget2.output_power[-1] == approx(30, 0.1)
    assert budget2.iip3[-1] == approx(-3, 0.1)


if __name__ == '__main__':
    test_iip3_2_amp()