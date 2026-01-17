from typing import Optional, Any
from .core import Element
from .utils import Hz_t, dB_t, dBm_t, dB, Hz


class Antenna(Element):
    def __init__(
        self,
        name: Optional[str] = None,
        gain: dB_t = dB(0),
        nf: dB_t = dB(0),
        iip3: Optional[dBm_t] = None,
        oip3: Optional[dBm_t] = None,
        z: float = 50,
    ):
        Element.__init__(
            self, name=name or "Antenna", gain=gain, nf=nf, iip3=iip3, oip3=oip3
        )
        self.z: float = z

    def schemdraw(self, d: Any, options: dict) -> Any:
        from .visualizer import draw_element

        return draw_element(self, d, options)


class NPort(Element):
    def __init__(self):
        pass


class TwoPortsElement(Element):
    def __init__(
        self,
        name: Optional[str] = None,
        gain: dB_t = dB(0),
        nf: dB_t = dB(0),
        iip3: Optional[dBm_t] = None,
        oip3: Optional[dBm_t] = None,
        z_in: float = 50,
        z_out: float = 50,
    ):
        Element.__init__(self, name=name, gain=gain, nf=nf, iip3=iip3, oip3=oip3)
        self.z_in: float = z_in
        self.z_out: float = z_out


class Amplifier(TwoPortsElement):
    def __init__(
        self,
        name: Optional[str] = None,
        gain: dB_t = dB(0),
        nf: dB_t = dB(0),
        iip3: Optional[dBm_t] = None,
        oip3: Optional[dBm_t] = None,
        z_in: float = 50,
        z_out: float = 50,
    ):
        TwoPortsElement.__init__(
            self,
            name=name or "LNA",
            gain=gain,
            nf=nf,
            iip3=iip3,
            oip3=oip3,
            z_in=z_in,
            z_out=z_out,
        )

    def schemdraw(self, d: Any, options: dict) -> Any:
        from .visualizer import draw_element

        return draw_element(self, d, options)


class Loss(TwoPortsElement):
    def __init__(
        self,
        name: Optional[str] = None,
        loss: dB_t = dB(0),
        oip3: Optional[dBm_t] = None,
        z_in: float = 50,
        z_out: float = 50,
    ):
        TwoPortsElement.__init__(
            self,
            name=name or "Loss",
            gain=dB(-loss),
            nf=loss,
            oip3=oip3,
            z_in=z_in,
            z_out=z_out,
        )

    def schemdraw(self, d: Any, options: dict) -> Any:
        from .visualizer import draw_element

        return draw_element(self, d, options)


class PathLoss(Loss):
    def __init__(
        self,
        name: Optional[str] = None,
        loss: dB_t = dB(0),
        oip3: Optional[dBm_t] = None,
        z_in: float = 50,
        z_out: float = 50,
    ):
        Loss.__init__(
            self, name=name or "PathLoss", loss=loss, oip3=oip3, z_in=z_in, z_out=z_out
        )


class ConverterType:
    Down = "Down"
    Up = "Up"


class Modulator(TwoPortsElement):
    def __init__(
        self,
        name: Optional[str] = None,
        gain: dB_t = dB(0),
        nf: dB_t = dB(0),
        oip3: Optional[dBm_t] = None,
        lo: Hz_t = Hz(0),
        converter_type: str = "",
    ):
        TwoPortsElement.__init__(
            self, name=name or "Mixer", gain=gain, nf=nf, oip3=oip3
        )
        self.lo: Hz_t = lo
        assert converter_type is not None
        self.converter_type: str = converter_type

    def schemdraw(self, d: Any, options: dict) -> Any:
        from .visualizer import draw_element

        return draw_element(self, d, options)


class Filter(TwoPortsElement):
    Butterworth = None

    def __init__(
        self,
        name: Optional[str] = None,
        gain: dB_t = dB(0),
        nf: dB_t = dB(0),
        oip3: Optional[dBm_t] = None,
        z_in: float = 50,
        z_out: float = 50,
        filter_order: int = 0,
    ):
        TwoPortsElement.__init__(
            self,
            name=name or "Mixer",
            gain=gain,
            nf=nf,
            oip3=oip3,
            z_in=z_in,
            z_out=z_out,
        )
        self.filter_order: int = filter_order

    def schemdraw(self, d: Any, options: dict) -> Any:
        from .visualizer import draw_element

        return draw_element(self, d, options)


class BandpassFilter(Filter):
    def __init__(
        self,
        name: Optional[str] = None,
        gain: dB_t = dB(0),
        nf: dB_t = dB(0),
        oip3: Optional[dBm_t] = None,
        z_in: float = 50,
        z_out: float = 50,
        filter_order: int = 0,
        center_freq: Hz_t = Hz(0),
        bandwidth: Hz_t = Hz(0),
    ):
        Filter.__init__(
            self,
            name=name,
            gain=gain,
            nf=nf,
            oip3=oip3,
            z_in=z_in,
            z_out=z_out,
            filter_order=filter_order,
        )
        self.center_freq: Hz_t = center_freq
        self.bandwidth: Hz_t = bandwidth

    def schemdraw(self, d: Any, options: dict) -> Any:
        from .visualizer import draw_element

        return draw_element(self, d, options)


class ButterworthBandpassFilter(BandpassFilter):
    def __init__(
        self,
        name: Optional[str] = None,
        nf: dB_t = dB(0),
        oip3: Optional[dBm_t] = None,
        z_in: float = 50,
        z_out: float = 50,
        filter_order: int = 0,
        center_freq: Hz_t = Hz(0),
        bandwidth: Hz_t = Hz(0),
        passband_attenuation: dB_t = dB(0),
        gain: dB_t = dB(0),
    ):
        BandpassFilter.__init__(
            self,
            name=name,
            gain=gain,
            nf=nf,
            oip3=oip3,
            z_in=z_in,
            z_out=z_out,
            filter_order=filter_order,
            center_freq=center_freq,
            bandwidth=bandwidth,
        )
        self.passband_attenuation: dB_t = passband_attenuation


Filter.Butterworth = ButterworthBandpassFilter
filter = Filter
