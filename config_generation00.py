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

    displayIntercept = calculate_line_y_intercept(
        displayGrey,
        logGrey,
        linearSlope
    )

    logToe = calculate_line_y(displayToe, linearSlope, displayIntercept)
    logShoulder = calculate_line_y(
        displayShoulder,
        linearSlope,
        displayIntercept
    )

    LUTsize = 4096
    linearLUT = numpy.linspace(0., 1., LUTsize)
    #
    # filmicLUT = numpy.linspace(calculate_line_yToLin_f(logMin, linMiddleGrey,
    #                            minimumExposure, maximumExposure),
    #                            calculate_line_yToLin_f(logMax, linMiddleGrey,
    #                            minimumExposure, maximumExposure), LUTsize)

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
            [calculate_line_y(displayMin, linearSlope, displayIntercept),
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
            [calculate_line_y(displayMax, linearSlope, displayIntercept),
                displayMax],
            [logMax, displayMax]
        ]
    ])

# Control1X = StartX + (.66 * (ControlX - StartX))
# Control2X = EndX + (.66 * (ControlX - EndX))
    cubicPoints = numpy.array([
        [
            [logMin, displayMin],
            [logMin + ((2. / 3.) * (calculate_line_y(displayMin, linearSlope,
             displayIntercept) - logMin)),
             displayMin],
            [logToe + ((2. / 3.) * (calculate_line_y(displayMin, linearSlope,
             displayIntercept) - logToe)),
             displayToe + ((2. / 3.) * (displayMin - displayToe))],
            # [calculate_line_y(displayMin, linearSlope, displayIntercept),
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
            [logShoulder + ((2. / 3.) * (calculate_line_y(
                displayMax, linearSlope, displayIntercept) - logShoulder)),
             displayShoulder + ((2. / 3.) * (displayMax - displayShoulder))],
            [logMax + ((2. / 3.) * (calculate_line_y(displayMax, linearSlope,
             displayIntercept) - logMax)),
             displayMax + ((2. / 3.) * (displayMax - displayMax))],
            # [calculate_line_y(displayMax, linearSlope, displayIntercept),
            #     displayMax],
            [logMax, displayMax]
        ]
    ])

    config = PyOpenColorIO.Config()

    LUT_SEARCH_PATH = ["luts", "looks"]
    config.setSearchPath(':'.join(LUT_SEARCH_PATH))

    config.setRole(PyOpenColorIO.Constants.ROLE_SCENE_LINEAR, "OpenAgX Linear")
    config.setRole(PyOpenColorIO.Constants.ROLE_REFERENCE, "OpenAgX Linear")
    config.setRole(PyOpenColorIO.Constants.ROLE_COLOR_TIMING,
                   "OpenAgX Log")
    config.setRole(PyOpenColorIO.Constants.ROLE_COMPOSITING_LOG,
                   "OpenAgX Log")
    config.setRole(PyOpenColorIO.Constants.ROLE_COLOR_PICKING,
                   "OpenAgX Log")
    config.setRole(PyOpenColorIO.Constants.ROLE_DATA, "Non-Colour Data")
    config.setRole(PyOpenColorIO.Constants.ROLE_DEFAULT,
                   "OpenAgX Log")
    config.setRole(PyOpenColorIO.Constants.ROLE_MATTE_PAINT,
                   "OpenAgX Log")
    config.setRole(PyOpenColorIO.Constants.ROLE_TEXTURE_PAINT,
                   "OpenAgX Log")

    config.addDisplay("sRGB 2.2 Standard", "OpenAgX Log",
                      "OpenAgX Log")

    colorspace = PyOpenColorIO.ColorSpace(family="Core",
                                          name="OpenAgX Linear")
    colorspace.setDescription("OpenAgX scene referred linear reference space")
    colorspace.setBitDepth(PyOpenColorIO.Constants.BIT_DEPTH_F32)
    colorspace.setAllocationVars([numpy.log2(calculate_ev_to_sr(
                                             minimumExposure,
                                             linMiddleGrey)),
                                  numpy.log2(calculate_ev_to_sr(
                                             maximumExposure,
                                             linMiddleGrey))])
    colorspace.setAllocation(PyOpenColorIO.Constants.ALLOCATION_LG2)
    config.addColorSpace(colorspace)

    colorspace = PyOpenColorIO.ColorSpace(family="Core",
                                          name="Non-Colour Data")
    colorspace.setDescription("Non-Colour Data")
    colorspace.setBitDepth(PyOpenColorIO.Constants.BIT_DEPTH_F32)
    colorspace.setIsData(True)
    config.addColorSpace(colorspace)

    configSlopes = [
        numpy.tan(numpy.deg2rad(50.0)),
        numpy.tan(numpy.deg2rad(52.5)),
        numpy.tan(numpy.deg2rad(55.0)),
        numpy.tan(numpy.deg2rad(57.5)),
        numpy.tan(numpy.deg2rad(60.0)),
        numpy.tan(numpy.deg2rad(62.5)),
        numpy.tan(numpy.deg2rad(65.0)),
        numpy.tan(numpy.deg2rad(67.5)),
        numpy.tan(numpy.deg2rad(70.0)),
        numpy.tan(numpy.deg2rad(72.5))
        ]

    for slope in configSlopes:
        curveParams = {"linearSlope": slope,
                       "minimumExposure": minimumExposure,
                       "maximumExposure": maximumExposure,
                       "displayPowerFunction": 2.2,
                       "latitudeStops": latitude,
                       "linearMiddleGrey": linMiddleGrey,
                       "logMinimum": logMin,
                       "displayMinimum": displayMin,
                       "logMaximum": logMax,
                       "displayMaximum": displayMax}

        outputLUT = createFilmlikeQuadraticLUT(4096, curveParams)

        filePrefix = "openagx_"
        writeFilmlikeQuadraticLUT("ocio/looks", filePrefix, LUTsize,
                                  curveParams)

        look = PyOpenColorIO.Look()
        look.setName("OpenAgX Contrast " + str(slope))
        look.setDescription("OpenAgX Contrast level " + str(slope))
        look.setProcessSpace("OpenAgX Log")
        lookName = filePrefix + str(slope)
        lookName.replace(".", "_")
        transform = PyOpenColorIO.FileTransform(
                        src=lookName,
                        interpolation=PyOpenColorIO.Constants.INTERP_LINEAR)
        look.setTransform(transform)
        config.addLook(look)
        pyplot.plot(7./17., (pow(0.18, 1./2.2)), "x", linearLUT,
                    list(outputLUT), '-')

    pyplot.savefig("OpenAgX.JPG")
    # Add base AgX shaper / log encoding
    colorspace = PyOpenColorIO.ColorSpace()
    colorspace.setAllocationVars([numpy.log2(calculate_ev_to_sr(
                                             minimumExposure,
                                             linMiddleGrey)),
                                  numpy.log2(calculate_ev_to_sr(
                                             maximumExposure,
                                             linMiddleGrey))])
    colorspace.setBitDepth(PyOpenColorIO.Constants.BIT_DEPTH_F32)
    colorspace.setDescription("OpenAgX Log")
    # setEqualityGroup()
    colorspace.setFamily("Transfer")
    # setIsData(False)
    colorspace.setIsData(False)
    colorspace.setName("OpenAgX Log")
    colorspace.setAllocationVars([numpy.log2(calculate_ev_to_sr(
                                             minimumExposure,
                                             linMiddleGrey)),
                                  numpy.log2(calculate_ev_to_sr(
                                             maximumExposure,
                                             linMiddleGrey))])
    colorspace.setAllocation(PyOpenColorIO.Constants.ALLOCATION_LG2)
    transform = OCIOCreateAllocationTransform(
        numpy.log2(calculate_ev_to_sr(minimumExposure, linMiddleGrey)),
        numpy.log2(calculate_ev_to_sr(maximumExposure, linMiddleGrey)),
        type=PyOpenColorIO.Constants.ALLOCATION_LG2
        )
    colorspace.setTransform(
        transform,
        PyOpenColorIO.Constants.COLORSPACE_DIR_FROM_REFERENCE)

    config.addColorSpace(colorspace)

    for name, colorspace in [["OpenAgX Log", "OpenAgX Log"]]:
        config.addDisplay("sRGB 2.2 Standard", name, colorspace)

    config.setActiveDisplays("sRGB 2.2 Standard")
    config.setActiveViews("OpenAgX Log")

    OCIOWriteConfig("ocio", config)
