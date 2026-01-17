from numpy import log10, log2
from typing import List, Optional, Any
from .utils import Hz_t, dB_t, dBm_t, kelvin_t, dB, dBm, Hz, kelvin


class Element:
    """
    nf is noise figure
    """

    def __init__(
        self,
        name: Optional[str] = None,
        gain: dB_t = dB(0),
        nf: dB_t = dB(0),
        oip3: Optional[dBm_t] = None,
        iip3: Optional[dBm_t] = None,
    ):
        self.name: str = name or ""
        self.gain: dB_t = gain
        self.nf: dB_t = nf
        self.iip3: Optional[dBm_t] = iip3
        self.oip3: Optional[dBm_t] = oip3
        if oip3 is None and iip3 is not None and gain is not None:
            self.oip3 = dBm(iip3 + gain)
        elif iip3 is None and oip3 is not None and gain is not None:
            self.iip3 = dBm(oip3 - gain)
        elif oip3 is None:
            self.oip3 = None

    def schemdraw(self, d: Any, options: dict) -> Any:
        from .visualizer import draw_element

        return draw_element(self, d, options)

    def schemdraw_label(self, options: dict, b: Any, lbl: Optional[str] = None) -> Any:
        from .visualizer import schemdraw_label

        return schemdraw_label(self, options, b, lbl=lbl)


class Budget:
    def __init__(
        self,
        elements: List[Element] = [],
        input_freq: Optional[Hz_t] = None,
        available_input_power: dBm_t = dBm(0),
        signal_bandwidth: Hz_t = Hz(1),
        without_oip: bool = False,
        T_receiver: Optional[kelvin_t] = None,
    ):
        self.elements: List[Element] = elements
        self.input_freq: Optional[Hz_t] = input_freq
        self.available_input_power: dBm_t = available_input_power
        self.signal_bandwidth: Hz_t = signal_bandwidth
        self.with_oip: bool = not without_oip
        self.T_receiver: Optional[kelvin_t] = T_receiver
        self.output_freq: List[Hz_t] = []
        self.output_power: List[dBm_t] = []
        self.transducer_gain: List[dB_t] = []
        self.f: List[float] = []  # noise factor
        self.nf: List[dB_t] = []  # noise figure
        self.iip2: List[dBm_t] = []
        self.oip2: List[dBm_t] = []
        self.iip3: List[dBm_t] = []
        self.oip3: List[dBm_t] = []
        self.snr: List[dB_t] = []
        self.capacity: List[float] = []
        self.receiver_thermal_noise_dBm: Optional[dBm_t] = None
        self.update()

    def schemdraw(
        self, options: Optional[dict] = None, as_html_table: bool = False
    ) -> Any:
        from .visualizer import into_schemdraw

        return into_schemdraw(self.elements, options, as_html_table=as_html_table)

    def update(self) -> None:
        # Use dictionnaries to ease getting default value forvfirst stage.
        # Will be converted back to list at the end
        output_freq_dict = {}
        output_power_dict = {}
        transducer_gain_dict = {}
        f_dict = {}
        nf_dict = {}
        snr_dict = {}
        capacity_dict = {}
        oip3_dict = {}

        k_boltzmann = 1.38e-23
        if self.T_receiver is None:
            self.T_receiver = kelvin(290)
        receiver_thermal_noise_W = k_boltzmann * self.T_receiver * self.signal_bandwidth
        self.receiver_thermal_noise_dBm = dBm(
            10 * log10(receiver_thermal_noise_W * 1000)
        )

        oip3_parts = []

        from .elements import Modulator, ConverterType

        for stage, elt in enumerate(self.elements):
            # Output power
            output_power_dict[stage] = (
                output_power_dict.get(stage - 1, self.available_input_power) + elt.gain
            )
            transducer_gain_dict[stage] = (
                transducer_gain_dict.get(stage - 1, 0) + elt.gain
            )

            # Noise factor & figure
            # See http://www.diva-portal.org/smash/get/diva2:1371826/FULLTEXT01.pdf
            # and https://en.wikipedia.org/wiki/Friis_formulas_for_noise
            # and https://www.microwaves101.com/encyclopedias/noise-figure-one-and-two-friis-and-ieee
            if stage == 0:
                f_dict[stage] = 10 ** (elt.nf / 10)
            else:
                f_dict[stage] = f_dict[stage - 1] + (10 ** (elt.nf / 10) - 1) / (
                    10 ** (transducer_gain_dict[stage - 1] / 10)
                )
            nf_dict[stage] = dB(10 * log10(f_dict[stage]))

            # Output frequency
            prev_freq = output_freq_dict.get(stage - 1, self.input_freq)
            if isinstance(elt, Modulator):
                if elt.converter_type == ConverterType.Down:
                    output_freq_dict[stage] = Hz_t(prev_freq - elt.lo)
                else:
                    output_freq_dict[stage] = Hz_t(prev_freq + elt.lo)
            else:
                output_freq_dict[stage] = prev_freq

            # SNR
            # See https://www.commagility.com/images/pdfs/white_papers/Introduction_to_RF_Link_Budgeting_CommAgility.pdf
            noise_at_stage = self.receiver_thermal_noise_dBm + nf_dict[stage]
            snr_dict[stage] = dB(
                output_power_dict[stage] - noise_at_stage - transducer_gain_dict[stage]
            )

            # Capacity
            snr_linear = 10 ** (snr_dict[stage] / 10)
            capacity_dict[stage] = self.signal_bandwidth * log2(1 + snr_linear)

            # OIP3 partial computation
            if self.with_oip:
                if stage == 0:
                    oip3_linear = (
                        10 ** (elt.oip3 / 10) if elt.oip3 is not None else float("inf")
                    )
                    oip3_parts.insert(stage, oip3_linear)
                    oip3_dict[0] = (
                        elt.oip3 if elt.oip3 is not None else dBm(float("inf"))
                    )
                else:
                    gain_linear = 10 ** (elt.gain / 10)
                    oip3_linear = (
                        10 ** (elt.oip3 / 10) if elt.oip3 is not None else float("inf")
                    )
                    oip3_parts = [gain_linear * p for p in oip3_parts]
                    oip3_parts.insert(stage, oip3_linear)
                    s = sum([1.0 / p for p in oip3_parts])
                    if s == 0:
                        oip3_dict[stage] = dBm(float("inf"))
                    else:
                        oip3_dict[stage] = dBm(10 * log10(1 / s))

        # Convert back from dictionnary to list
        self.output_power = [
            dBm(output_power_dict[stage]) for stage, elt in enumerate(self.elements)
        ]
        self.transducer_gain = [
            dB(transducer_gain_dict[stage]) for stage, elt in enumerate(self.elements)
        ]
        self.f = [float(f_dict[stage]) for stage, elt in enumerate(self.elements)]
        self.nf = [dB(nf_dict[stage]) for stage, elt in enumerate(self.elements)]
        self.output_freq = [
            Hz_t(output_freq_dict[stage]) for stage, elt in enumerate(self.elements)
        ]
        self.snr = [dB(snr_dict[stage]) for stage, elt in enumerate(self.elements)]
        self.capacity = [
            float(capacity_dict[stage]) for stage, elt in enumerate(self.elements)
        ]
        if self.with_oip:
            self.oip3 = [
                dBm(oip3_dict[stage]) for stage, elt in enumerate(self.elements)
            ]
            self.iip3 = [
                dBm(self.oip3[stage] - self.transducer_gain[stage])
                for stage, elt in enumerate(self.elements)
            ]

    def print(self) -> None:
        print("rfbudget with properties:")
        print(
            "Elements: [1x{} rf.internal.rfbudget.Element]".format(len(self.elements))
        )
        print("InputFrequency:", self.input_freq, "Hz")
        print("AvailableInputPower:", self.available_input_power, " dBm")
        print("SignalBandwidth:", self.signal_bandwidth, "Hz")
        print("Solver: Friis")
        print("")
        print("Analysis Results")
        print("ThermalNoise:    (dBm)\t ", self.receiver_thermal_noise_dBm)
        print("OutputFrequency: (Hz)\t", self.output_freq)
        print("OutputPower:     (dBm)\t", self.output_power)
        print("TransducerGain:  (dB)\t", self.transducer_gain)
        print("Noisefigure:     (dB)\t", self.nf)
        if self.with_oip:
            print("IIP3:            (dBm)\t", self.iip3)
            print("OIP3:            (dBm)\t", self.oip3)
        print("SNR:             (dB)\t", self.snr)
        print("ChannelCapacity: (bps)\t", self.capacity)

    def to_html(self, with_icons: bool = False, options: Optional[dict] = None) -> str:
        import io

        html = io.StringIO("")
        print("<div>\n", file=html)
        print("<h3>RF budget with properties</h3>", file=html)
        print("<table>", file=html)
        print(
            "<tr><td>Elements:</td><td>[1x{} rf.internal.rfbudget.Element]</td></tr>".format(
                len(self.elements)
            ),
            file=html,
        )
        print(
            "<tr><td>InputFrequency</td><td>",
            self.input_freq,
            "Hz</td></tr>",
            file=html,
        )
        print(
            "<tr><td>AvailableInputPower</td><td>",
            self.available_input_power,
            " dBm</td></tr>",
            file=html,
        )
        print(
            "<tr><td>SignalBandwidth</td><td>",
            self.signal_bandwidth,
            "Hz</td></tr>",
            file=html,
        )
        print("<tr><td>Solver</td><td>Friis</td></tr>", file=html)
        print("</table>", file=html)
        print("<h3>Analysis Results</h3>", file=html)
        print("<table>", file=html)
        if with_icons:
            from .visualizer import into_schemdraw

            print(
                "<tr><td></td><td></td>",
                into_schemdraw(self.elements, options, as_html_table=True),
                "</tr>",
                file=html,
            )
        print(
            "<tr><td>ThermalNoise:</td><td>(dBm)</td>",
            "<td>{0:.2f}</td>".format(self.receiver_thermal_noise_dBm),
            "</tr>",
            file=html,
        )
        print(
            "<tr><td>OutputFrequency:</td><td>(Hz)</td>",
            self.html_cell_format(self.output_freq),
            "</tr>",
            file=html,
        )
        print(
            "<tr><td>OutputPower:</td><td>(dBm)</td>",
            self.html_cell_format(self.output_power),
            "</tr>",
            file=html,
        )
        print(
            "<tr><td>TransducerGain:</td><td>(dB)</td>",
            self.html_cell_format(self.transducer_gain),
            "</tr>",
            file=html,
        )
        print(
            "<tr><td>Noisefigure:</td><td>(dB)</td>",
            self.html_cell_format(self.nf),
            "</tr>",
            file=html,
        )
        if self.with_oip:
            print(
                "<tr><td>IIP3:</td><td>(dBm)</td>",
                self.html_cell_format(self.iip3),
                "</tr>",
                file=html,
            )
            print(
                "<tr><td>OIP3:</td><td>(dBm)</td>",
                self.html_cell_format(self.oip3),
                "</tr>",
                file=html,
            )
        print(
            "<tr><td>SNR:</td><td>(dB)</td>",
            self.html_cell_format(self.snr),
            "</tr>",
            file=html,
        )
        print(
            "<tr><td>ChannelCapacity:</td><td>(bps)</td>",
            self.html_cell_format(self.capacity),
            "</tr>",
            file=html,
        )
        print("</table>", file=html)
        print("</div>\n", file=html)
        return html.getvalue()

    def html_cell_format(self, a_list: List[Any]) -> str:
        return "".join(map(lambda v: "<td>{0:.2f}</td>".format(v), a_list))

    def display(self, with_icons: bool = False, options: Optional[dict] = None) -> Any:
        try:
            from IPython.display import display, HTML

            return display(HTML(self.to_html(with_icons=with_icons, options=options)))
        except ImportError:
            self.print()
            return None
