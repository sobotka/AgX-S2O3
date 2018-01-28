#!/usr/bin/env python
# -*- coding: utf-8 -*-


import numpy
import PyOpenColorIO

from lib.agx_math import *
from lib.agx_file import *
from lib.agx_colour import *
from matplotlib import pyplot


if __name__ == "__main__":
    minimumExposure = -7.
    maximumExposure = +10.
    linMiddleGrey = 0.18
    dynamicRange = maximumExposure - minimumExposure
    latitude = 10.
    logGrey = abs(minimumExposure) / dynamicRange
    logMin = 0.
    logMax = 1.
    displayMin = 0.
    displayMax = 1.
    displayGrey = pow(linMiddleGrey, 1./2.2)
    displayToe = displayMin + (abs(minimumExposure) / dynamicRange *
                               (dynamicRange - latitude) / dynamicRange)
    displayShoulder = displayMax - (maximumExposure / dynamicRange *
                                    (dynamicRange - latitude) / dynamicRange)

    linearSlope = 1.75

    displayIntercept = calculateIntercept(displayGrey, logGrey,
                                          linearSlope)

    logToe = calculateLog(displayToe, linearSlope, displayIntercept)
    logShoulder = calculateLog(displayShoulder, linearSlope,
                               displayIntercept)

    x_base = [
            logMin,
            logToe,
            logGrey,
            logShoulder,
            logMax,
        ]
    y_base = [
            displayMin,
            displayToe,
            displayGrey,
            displayShoulder,
            displayMax,
        ]

    controlPoints = numpy.array([
        [
            [logMin, displayMin],
            [calculateLog(displayMin, linearSlope, displayIntercept),
                displayMin],
            [logToe, displayToe]
        ],
        [
            [logToe, displayToe],
            [logGrey, displayGrey],
            [logShoulder, displayShoulder]
        ],
        [
            [logShoulder, displayShoulder],
            [calculateLog(displayMax, linearSlope, displayIntercept),
                displayMax],
            [logMax, displayMax]
        ]
    ])

    cubicPoints = numpy.array([
        [
            [logMin, displayMin],
            [logMin + ((2. / 3.) * (calculateLog(displayMin, linearSlope,
             displayIntercept) - logMin)),
             displayMin],
            [logToe + ((2. / 3.) * (calculateLog(displayMin, linearSlope,
             displayIntercept) - logToe)),
             displayToe + ((2. / 3.) * (displayMin - displayToe))],
            # [calculateLog(displayMin, linearSlope, displayIntercept),
            #     displayMin],
            [logToe, displayToe]
        ],
        [
            # Control1X = StartX + (.66 * (ControlX - StartX))
            # Control2X = EndX + (.66 * (ControlX - EndX))
            [logToe, displayToe],
            [logToe + ((2. / 3.) * (logGrey - logToe)),
             displayToe + ((2. / 3.) * (displayGrey - displayToe))],
            [logShoulder + ((2. / 3.) * (logGrey - logShoulder)),
             displayShoulder + ((2. / 3.) * (displayGrey - displayShoulder))],
            # [logGrey, displayGrey],
            [logShoulder, displayShoulder]
        ],
        [
            # Control1X = StartX + (.66 * (ControlX - StartX))
            # Control2X = EndX + (.66 * (ControlX - EndX))
            [logShoulder, displayShoulder],
            [logShoulder + ((2. / 3.) * (calculateLog(displayMax, linearSlope,
             displayIntercept) - logShoulder)),
             displayShoulder + ((2. / 3.) * (displayMax - displayShoulder))],
            [logMax + ((2. / 3.) * (calculateLog(displayMax, linearSlope,
             displayIntercept) - logMax)),
             displayMax + ((2. / 3.) * (displayMax - displayMax))],
            # [calculateLog(displayMax, linearSlope, displayIntercept),
            #     displayMax],
            [logMax, displayMax]
        ]
    ])

    linLUT = numpy.linspace(0., 1., 4096)
    outLUTQuad = calculateYfromXQuadratic(controlPoints, linLUT)
    outLUTCubic = calculateYfromXCubic(cubicPoints, linLUT)

    pyplot.plot(linLUT, outLUTQuad, "-")
    pyplot.plot(linLUT, outLUTCubic, "-")
    pyplot.show()

    inLog1Arr = numpy.array([0.5, 0.8, 0.9])
    inLog1 = calculateLinToLog(inLog1Arr, 0.18, -10., 10.)
    inLog2 = calculateLinToLog(0.8, 0.18, -10., 10.)
    print("CalculateLinToLog ", inLog1, inLog2)
    print("CalculateLogToLin ", calculateLogToLin(inLog1, 0.18, -10., 10.),
          calculateLogToLin(inLog2, 0.18, -10., 10.))

    print("Equal?: ", numpy.allclose(outLUTQuad, outLUTCubic))
    # x = numpy.array([1,2,3,4,5,6,7,8,9,10])
    # print(numpy.where(x > 5., x/5., x))
