"""Lamina — metrics and weight-dependent parameters (UPM 1000).

`w` runs from 0 (400 Regular) to 1 (700 Bold).
"""
import os
from dataclasses import dataclass

# Principles can be switched off to show what each one does (specimen only):
#   flank - rounds without straight flanks (plain ovals)
#   bend  - hooks turn through a sharp corner instead of the bend
#   cut   - terminals cut square to the stroke instead of to the page
WITHOUT = set(filter(None, os.environ.get("LAMINA_WITHOUT", "").split(",")))

UPM = 1000
XH = 526      # x-height
CAP = 700     # cap height
ASC = 742     # ascender (b d h k l)
DESC = -210   # descender
OS = 10       # overshoot, lowercase rounds
OSC = 12      # overshoot, capital rounds

# weight positions of the four instances on the 0..1 scale (perceptually even)
WEIGHTS = {"Regular": (400, 0.0), "Medium": (500, 0.30), "SemiBold": (600, 0.64), "Bold": (700, 1.0)}


def mix(a, b, w):
    return a + (b - a) * w


@dataclass
class P:
    w: float

    # --- stroke weights -------------------------------------------------
    @property
    def V(self):            # lowercase vertical stem
        return mix(82, 142, self.w)

    @property
    def H(self):            # lowercase horizontal stroke (tops of bowls, bars)
        return self.V * mix(0.84, 0.77, self.w)

    @property
    def VC(self):           # capital vertical stem
        return self.V + mix(6, 12, self.w)

    @property
    def HC(self):           # capital horizontal stroke
        return self.VC * mix(0.83, 0.76, self.w)

    @property
    def VF(self):           # figure stem (between lowercase and capital)
        return self.V + mix(3, 8, self.w)

    @property
    def HF(self):
        return self.VF * mix(0.84, 0.77, self.w)

    # --- the lamella rhythm --------------------------------------------
    @property
    def C(self):            # lowercase counter: n, o, u, h, b, d, p, q
        return mix(292, 236, self.w)

    @property
    def CC(self):           # capital counter: H, O, U, N
        return mix(404, 352, self.w)

    # --- spacing (sidebearings) ---------------------------------------
    @property
    def sbS(self):          # lowercase straight side
        return mix(60, 52, self.w)

    @property
    def sbR(self):          # lowercase round side
        return mix(40, 34, self.w)

    @property
    def sbSC(self):         # capital straight side
        return mix(76, 66, self.w)

    @property
    def sbRC(self):         # capital round side
        return mix(44, 38, self.w)

    # --- the bend -------------------------------------------------------
    @property
    def R(self):            # vertical reach of the lowercase bend (skeleton)
        return mix(178, 172, self.w)

    @property
    def RC(self):           # vertical reach of the capital bend (skeleton)
        return mix(206, 206, self.w)

    def nib(self):
        from geom import nib
        return nib(self.V, self.H)

    def nibC(self):
        from geom import nib
        return nib(self.VC, self.HC)

    def nibF(self):
        from geom import nib
        return nib(self.VF, self.HF)
