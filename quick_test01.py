#!/usr/bin/env python
# -*- coding: utf-8 -*-


import numpy
import PyOpenColorIO

from lib.agx_math import *
from lib.agx_file import *
from lib.agx_colour import *
from matplotlib import pyplot


if __name__ == "__main__":
    calculateChromaticAdaptationMatrix(ILLUMINANT_D65, ILLUMINANT_E)
