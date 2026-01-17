from numpy import log10
from typing import Optional, Any
from .elements import PathLoss
from .utils import Hz_t, dBm_t, m_t, dB, MHz, km, m, Hz


class FreeSpacePathLossFriis(PathLoss):
    def __init__(
        self,
        name: Optional[str] = None,
        distance: m_t = m(0),
        freq: Hz_t = Hz(0),
        oip3: Optional[dBm_t] = None,
        z_in: float = 50,
        z_out: float = 50,
    ):
        self.distance: m_t = distance
        loss = dB(20 * log10(distance) + 20 * log10(freq) - 147.55)
        PathLoss.__init__(
            self, name=name or "FPSL", loss=loss, oip3=oip3, z_in=z_in, z_out=z_out
        )

    def schemdraw(self, d: Any, options: dict) -> Any:
        from .visualizer import draw_element

        return draw_element(self, d, options)


class RadarFreeSpaceBasicLoss(PathLoss):
    """
    https://www.itu.int/dms_pubrec/itu-r/rec/p/R-REC-P.525-2-199408-S!!PDF-E.pdf
    """

    def __init__(
        self,
        name: Optional[str] = None,
        distance: m_t = m(0),
        sigma: float = 1.0,
        freq: Hz_t = Hz(0),
        oip3: Optional[dBm_t] = None,
        z_in: float = 50,
        z_out: float = 50,
    ):
        """
        Two way loss of the signal of a radar.
        distance: distance from the radar to the target
        sigma: radar target cross-section (m²)
        """
        self.distance: m_t = distance
        self.sigma: float = sigma
        loss = dB(
            103.4
            + 20 * log10(freq / MHz(1))
            + 40 * log10(distance / km(1))
            - 10 * log10(sigma)
        )
        PathLoss.__init__(
            self, name=name or "FPSL", loss=loss, oip3=oip3, z_in=z_in, z_out=z_out
        )

    def schemdraw(self, d: Any, options: dict) -> Any:
        from .visualizer import draw_element

        return draw_element(self, d, options)


class OkumuraHataPathLoss(PathLoss):
    """See https://en.wikipedia.org/wiki/Hata_model"""

    SMALL_CITY = "small city"
    MEDIUM_CITY = "medium city"
    LARGE_CITY = "large city"
    SUBURBAN = "suburban environment"
    OPEN = "open environment"

    def __init__(
        self,
        name: Optional[str] = None,
        distance: m_t = m(0),
        freq: Hz_t = Hz(0),
        base_height: m_t = m(30),
        mobile_height: m_t = m(1),
        environment: str = "",
        oip3: Optional[dBm_t] = None,
        z_in: float = 50,
        z_out: float = 50,
    ):
        self.distance: m_t = distance
        self.mobile_height: m_t = mobile_height
        self.base_height: m_t = base_height
        self.freq: Hz_t = freq
        self.environment: str = environment
        f = freq / MHz(1)
        d = distance / km(1)
        hb = base_height / m(1)
        hm = mobile_height / m(1)
        if hb < 30 or hb > 200:
            raise ValueError("Expected height of base station to be in 30-200m range")
        if hm < 1 or hm > 10:
            raise ValueError("Expected height of mobile station to be in 1-10m range")
        if d < 1 or d > 10:
            raise ValueError("Expected distance to be in 1-10km range")
        # Compute ch, the Antenna height correction factor
        if environment in [
            OkumuraHataPathLoss.SMALL_CITY,
            OkumuraHataPathLoss.MEDIUM_CITY,
            OkumuraHataPathLoss.SUBURBAN,
            OkumuraHataPathLoss.OPEN,
        ]:
            ch = 0.8 + (1.1 * log10(f) - 0.7) * hm - 1.56 * log10(f)
        elif environment == OkumuraHataPathLoss.LARGE_CITY:
            if f < 150:
                raise ValueError("Expected frequency to be in 150MHz - 1.5GHz range")
            elif f <= 200:
                ch = 8.29 * log10(1.54 * hm) ** 2 - 1.1
            elif f <= 1500:
                ch = 3.2 * log10(11.75 * hm) ** 2 - 4.97
            else:
                raise ValueError("Expected frequency to be in 150MHz - 1.5GHz range")
        else:
            raise ValueError("Unexpected environment")
        # Path loss in urban areas. Unit: decibel (dB)
        loss = dB(
            69.55
            + 26.16 * log10(f)
            - 13.82 * log10(hb)
            - ch
            + (44.9 - 6.55 * log10(hb)) * log10(d)
        )
        if environment == OkumuraHataPathLoss.SUBURBAN:
            loss = dB(loss - 2 * log10(f / 28) ** 2 - 5.4)
        elif environment == OkumuraHataPathLoss.OPEN:
            loss = dB(loss - 4.78 * log10(f) ** 2 + 18.33 * log10(f) - 40.94)
        PathLoss.__init__(
            self,
            name=name or environment or "city",
            loss=loss,
            oip3=oip3,
            z_in=z_in,
            z_out=z_out,
        )

    def schemdraw(self, d: Any, options: dict) -> Any:
        from .visualizer import draw_element

        return draw_element(self, d, options)


class CostHataPathLoss(PathLoss):
    """See https://en.wikipedia.org/wiki/COST_Hata_model"""

    METROPOLITAN = "metropolitan"
    MEDIUM_CITY_SUBURBAN = "medium city or suburban"

    def __init__(
        self,
        name: Optional[str] = None,
        distance: m_t = m(0),
        freq: Hz_t = Hz(0),
        base_height: m_t = m(30),
        mobile_height: m_t = m(1),
        environment: str = MEDIUM_CITY_SUBURBAN,
        oip3: Optional[dBm_t] = None,
        z_in: float = 50,
        z_out: float = 50,
    ):
        self.distance: m_t = distance
        self.mobile_height: m_t = mobile_height
        self.base_height: m_t = base_height
        self.freq: Hz_t = freq
        self.environment: str = environment

        f = freq / MHz(1)
        d_km = distance / km(1)
        hb = base_height / m(1)
        hm = mobile_height / m(1)

        # Constraints (Wikipedia)
        if f < 1500 or f > 2000:
            raise ValueError("Expected frequency to be in 1500MHz - 2GHz range")
        if hb < 30 or hb > 200:
            raise ValueError("Expected height of base station to be in 30-200m range")
        if hm < 1 or hm > 10:
            raise ValueError("Expected height of mobile station to be in 1-10m range")
        if d_km < 1 or d_km > 20:
            raise ValueError("Expected distance to be in 1-20km range")

        # antenna height correction factor a(hm)
        ch = (1.1 * log10(f) - 0.7) * hm - (1.56 * log10(f) - 0.8)

        # Constant C
        if environment == CostHataPathLoss.METROPOLITAN:
            c = 3
        elif environment == CostHataPathLoss.MEDIUM_CITY_SUBURBAN:
            c = 0
        else:
            raise ValueError("Unexpected environment")

        loss = dB(
            46.3
            + 33.9 * log10(f)
            - 13.82 * log10(hb)
            - ch
            + (44.9 - 6.55 * log10(hb)) * log10(d_km)
            + c
        )

        PathLoss.__init__(
            self,
            name=name or f"COST Hata ({environment})",
            loss=loss,
            oip3=oip3,
            z_in=z_in,
            z_out=z_out,
        )

    def schemdraw(self, d: Any, options: dict) -> Any:
        from .visualizer import draw_element

        return draw_element(self, d, options)
