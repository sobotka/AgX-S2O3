#!/usr/bin/env python
# -*- coding: utf-8 -*-


import numpy
import PyOpenColorIO

from lib.agx_math import *
from lib.agx_file import *
from lib.agx_colour import *
from matplotlib import pyplot


if __name__ == "__main__":
    ICC_D50XYZ = numpy.array([
        [0.964200000, 1.000000000, 0.824900000]
    ])

    ICC_D50xyY = calculateXYZtoxyY(ICC_D50XYZ)
    print("ICC_D50xyY\n", ICC_D50xyY)
    print("ICC_D50XYZ\n", calculatexyYtoXYZ(ICC_D50xyY))
    calculateChromaticAdaptationMatrix(ILLUMINANT_D65, ICC_D50xyY)
