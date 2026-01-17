from rfbudget import CostHataPathLoss, MHz, m, km
from pytest import approx


def test_cost_hata_medium_city():
    # Validation values calculated manually from Wikipedia formula
    # f=1800MHz, hb=30m, hm=1.5m, d=1km, C=0
    # L = 46.3 + 110.353 - 20.413 - 0.043 = 136.197
    model = CostHataPathLoss(
        freq=MHz(1800),
        base_height=m(30),
        mobile_height=m(1.5),
        distance=km(1),
        environment=CostHataPathLoss.MEDIUM_CITY_SUBURBAN,
    )
    assert model.gain == approx(-136.197, abs=0.01)


def test_cost_hata_metropolitan():
    # Same as above but C=3
    model = CostHataPathLoss(
        freq=MHz(1800),
        base_height=m(30),
        mobile_height=m(1.5),
        distance=km(1),
        environment=CostHataPathLoss.METROPOLITAN,
    )
    assert model.gain == approx(-139.197, abs=0.01)


def test_cost_hata_distance():
    # d=2km
    # L(2 km) = 136.197 + 10.603 = 146.8
    model = CostHataPathLoss(
        freq=MHz(1800),
        base_height=m(30),
        mobile_height=m(1.5),
        distance=km(2),
        environment=CostHataPathLoss.MEDIUM_CITY_SUBURBAN,
    )
    assert model.gain == approx(-146.8, abs=0.01)
