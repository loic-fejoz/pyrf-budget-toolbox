import io
from typing import List, Optional, Any
import schemdraw
from schemdraw import dsp
from .core import Element
from .elements import (
    Antenna,
    Amplifier,
    Loss,
    PathLoss,
    Modulator,
    Filter,
    BandpassFilter,
)
from .propagation import (
    FreeSpacePathLossFriis,
    RadarFreeSpaceBasicLoss,
    OkumuraHataPathLoss,
)


def schemdraw_label(
    elt: Element, options: dict, b: Any, lbl: Optional[str] = None
) -> Any:
    if lbl is None:
        lbl = ""
    else:
        lbl = str(lbl)
    if options.get("with_gain") and elt.gain is not None:
        lbl += "gain={0:.2f}dB\n".format(elt.gain)
    if options.get("with_nf") and elt.nf:
        lbl += "NF={0:.2f}dB\n".format(elt.nf)
    if options.get("with_iip") and elt.iip3:
        lbl += "IIP3={0:.2f}dB\n".format(elt.iip3)
    if options.get("with_oip") and elt.oip3:
        lbl += "OIP3={0:.2f}dB\n".format(elt.oip3)
    return b.label(lbl, "top", ofst=(-0.2, 0.6), fontsize=6)


def draw_element(elt: Element, d: Any, options: dict) -> Any:
    if isinstance(elt, Antenna):
        return schemdraw_label(elt, options, dsp.Antenna().label(elt.name, "bottom"))
    elif isinstance(elt, Amplifier):
        return schemdraw_label(
            elt, options, dsp.Amp().fill("lightblue").label(elt.name, "bottom")
        )
    elif isinstance(elt, FreeSpacePathLossFriis):
        return schemdraw_label(
            elt,
            options,
            dsp.Box(w=d.unit / 3, h=d.unit / 3)
            .fill("#eeeeff")
            .label(elt.name, "bottom"),
            lbl="d={0:.2f}m\n".format(elt.distance),
        )
    elif isinstance(elt, RadarFreeSpaceBasicLoss):
        return schemdraw_label(
            elt,
            options,
            dsp.Box(w=d.unit / 3, h=d.unit / 3)
            .fill("#eeeeff")
            .label(elt.name, "bottom"),
            lbl="d={0:.2f}m\nσ={0:.2f}m\n".format(
                elt.distance,
            ),
        )
    elif isinstance(elt, OkumuraHataPathLoss):
        return schemdraw_label(
            elt,
            options,
            dsp.Box(w=d.unit / 3, h=d.unit / 3)
            .fill("#eeeeff")
            .label(elt.name, "bottom"),
            lbl="d={0:.2f}m\nh_b={0:.2f}m\nh_m={0:.2f}m\n".format(
                elt.distance,
            ),
        )
    elif isinstance(elt, PathLoss):
        return schemdraw_label(
            elt,
            options,
            dsp.Box(w=d.unit / 3, h=d.unit / 3)
            .fill("#eeeeff")
            .label(elt.name, "bottom"),
        )
    elif isinstance(elt, Loss):
        return schemdraw_label(
            elt,
            options,
            dsp.Box(w=d.unit / 3, h=d.unit / 3)
            .fill("#ffeeee")
            .label(elt.name, "bottom"),
        )
    elif isinstance(elt, Modulator):
        mix = dsp.Mixer().anchor("W").fill("navajowhite").label(elt.name, "bottom")
        dsp.Line().at(mix.S).down(d.unit / 3)
        dsp.Oscillator().right().anchor("N").fill("navajowhite").label(
            "LO", "right", ofst=0.2
        )
        return schemdraw_label(elt, options, mix)
    elif isinstance(elt, BandpassFilter):
        return schemdraw_label(
            elt,
            options,
            dsp.Filter(response="bp")
            .anchor("W")
            .fill("thistle")
            .label(elt.name, "bottom", ofst=0.2),
        )
    elif isinstance(elt, Filter):
        return schemdraw_label(
            elt,
            options,
            dsp.Filter()
            .anchor("W")
            .fill("thistle")
            .label(elt.name, "bottom", ofst=0.2),
        )
    else:
        return schemdraw_label(
            elt,
            options,
            dsp.Box(w=d.unit / 3, h=d.unit / 3).label(elt.name, "bottom"),
        )


def into_schemdraw(
    elements: List[Element], options: Optional[dict] = None, as_html_table: bool = False
) -> Any:
    html = io.StringIO("")
    if options is None:
        options = {}
    options.setdefault("simplified", True)
    options.setdefault("with_gain", not options["simplified"])
    options.setdefault("with_nf", not options["simplified"])
    options.setdefault("with_iip", not options["simplified"])
    options.setdefault("with_oip", not options["simplified"])
    with schemdraw.Drawing() as d:
        if as_html_table:
            d.outfile = None
            d.fig = None
            d.show = False
            d = schemdraw.Drawing()
            d.__enter__()
            d.config(fontsize=12)
        d.config(fontsize=12)
        # Previous RfBudget Element
        prev = None
        # Previous SchemDraw Element
        previous = None
        for elt in elements:
            html.write("<td>")
            if previous is not None:
                try:
                    anchor = previous.E
                except AttributeError:
                    anchor = None
                if anchor and not as_html_table:
                    the_line = dsp.Line().at(previous.E).length(d.unit / 4)
                else:
                    the_line = dsp.Line().length(d.unit / 4)
                if isinstance(elt, PathLoss) or isinstance(prev, PathLoss):
                    the_line.color("#FFFFFF00")
            elif not isinstance(previous, Antenna):
                dsp.Line().length(d.unit / 4)
            previous = draw_element(elt, d, options)
            prev = elt
            if as_html_table:
                d.add(previous)
                d._drawsvg(None)
                svg_img = d._repr_svg_()
                html.write(svg_img)
                previous = None
                d.outfile = None
                d.fig = None
                d.show = False
                d.__exit__(None, None, None)
                d = schemdraw.Drawing()
                d.__enter__()
                d.config(fontsize=12)
                html.write("</td>")
        if as_html_table:
            return html.getvalue()
        if previous is not None and not isinstance(elements[-1], Antenna):
            dsp.Arrow().right(d.unit / 3)
        return d
