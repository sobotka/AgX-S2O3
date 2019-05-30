#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Defines colour utility functions.
"""

import numpy
import os
import errno
from lib.agx_math import *
from lib.agx_file import *


def writeFilmlikeQuadraticLUT(subdirectory, prefix, LUTsize, curveParams):
    try:
        writeLUT = createFilmlikeQuadraticLUT(LUTsize, curveParams)
        currentDirectory = os.path.relpath(".")

        filename = prefix + str(curveParams["linearSlope"])
        filename.replace(".", "_")

        destinationFile = (currentDirectory + "/" + subdirectory + "/" +
                           filename)

        if not os.path.exists(os.path.dirname(destinationFile)):
            os.makedirs(os.path.dirname(destinationFile))

        OCIOWriteSPI1D(destinationFile, list(writeLUT))

    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise


def createFilmlikeQuadraticLUT(LUTsize, curveParams):
    linearSlope = curveParams["linearSlope"]
    minimumExposure = curveParams["minimumExposure"]
    maximumExposure = curveParams["maximumExposure"]
    displayPowerFunction = curveParams["displayPowerFunction"]
    dynamicRangeStops = maximumExposure - minimumExposure
    latitudeStops = curveParams["latitudeStops"]
    linearMiddleGrey = curveParams["linearMiddleGrey"]
    displayMiddleGrey = pow(linearMiddleGrey, 1. / displayPowerFunction)
    logMiddleGrey = abs(minimumExposure) / dynamicRangeStops
    logMinimum = curveParams["logMinimum"]
    displayMinimum = curveParams["displayMinimum"]
    logMaximum = curveParams["logMaximum"]
    displayMaximum = curveParams["displayMaximum"]
    displayToe = displayMinimum + (abs(minimumExposure) / dynamicRangeStops *
                                   (dynamicRangeStops - latitudeStops) /
                                   dynamicRangeStops)
    displayLinearIntercept = calculate_line_y_intercept(
        displayMiddleGrey,
        logMiddleGrey,
        linearSlope
    )
    logToe = calculate_line_y(displayToe, linearSlope, displayLinearIntercept)
    displayShoulder = displayMaximum - (maximumExposure / dynamicRangeStops *
                                        (dynamicRangeStops - latitudeStops) /
                                        dynamicRangeStops)
    logShoulder = calculate_line_y(
        displayShoulder,
        linearSlope,
        displayLinearIntercept
    )

    quadraticControlPoints = numpy.array([
        [
            # Starting Point
            [logMinimum,  displayMinimum],
            # Quadratic Control Point
            [calculate_line_y(
                displayMinimum,
                linearSlope,
                displayLinearIntercept
            ),
             displayMinimum],
            # Ending Point
            [logToe, displayToe]
        ],
        [
            # Starting Point
            [logToe, displayToe],
            # Quadratic Control Point
            [logMiddleGrey, displayMiddleGrey],
            # Ending Point
            [logShoulder, displayShoulder]
        ],
        [
            # Starting Point
            [logShoulder, displayShoulder],
            # Quadratic Control Point
            [calculate_line_y(
                displayMaximum,
                linearSlope,
                displayLinearIntercept
            ),
             displayMaximum],
            # Ending Point
            [logMaximum, displayMaximum]
        ]
    ])

    linearLUT = numpy.linspace(0., 1., LUTsize)
    outputLUT = calculate_y_from_x_quadratic(quadraticControlPoints, linearLUT)

    return outputLUT

# sf = 1.25 - 0.25 * (Y_surround / 0.184)
# lf = log(318)/log(Y_absolute)
# Michaelis-Menten modified function ε = 0.59 / (sf • lf )
# LMS =       0.4002  0.7075 -0.0807 X_D65
#            -0.2280  1.1500  0.0612 Y_D65
#             0.0000  0.0000  0.9184 Z_D65
# IPT_hdr =   0.4000  0.4000  0.2000 L'
#             0.4550 -4.8510  0.3960 M'
#             0.8056  0.3572 -1.1628 S'
# C_hdr_ipt = root(P_hdr^2, T_hdr^2)
# H_hdr_ipt = tan^-1(T_hdr / P_hdr)
