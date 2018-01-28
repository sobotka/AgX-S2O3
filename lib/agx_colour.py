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

ILLUMINANT_E = numpy.array([
    [1./3., 1./3.]
])

ILLUMINANT_D65 = numpy.array([
    [0.3127, 0.3290]
])

PRIMARIES_sRGB = numpy.array([
    [0.6400, 0.3300],
    [0.3000, 0.6000],
    [0.1500, 0.0600],
])

CADAPT_BRADFORD = numpy.array([
    [0.8951, 0.2664, -0.1614],
    [-0.7502, 1.7135, 0.0367],
    [0.0389, -0.0685, 1.0296],
])


def calculatexyYtoXYZ(xyYPrimaries, valueY=1.):
    xyYPrimaries = numpy.asarray(xyYPrimaries)
    XYZOut = numpy.zeros([xyYPrimaries.shape[0], 3])

    XYZOut[:, 0] = (xyYPrimaries[:, 0] * valueY) / xyYPrimaries[:, 1]
    XYZOut[:, 1] = valueY
    XYZOut[:, 2] = (
        ((1. - xyYPrimaries[:, 0] - xyYPrimaries[:, 1]) * valueY) /
        xyYPrimaries[:, 1])

    return XYZOut


def calculateChromaticAdaptationMatrix(srcWhitePrimaries, destWhitePrimaries,
                                       cadaptMatrix=CADAPT_BRADFORD):
    srcXYZ = calculatexyYtoXYZ(ILLUMINANT_D65)
    srcXYZ = numpy.reshape(srcXYZ, [3, ])
    # srcXYZ = numpy.diag(srcXYZ)

    destXYZ = calculatexyYtoXYZ(destWhitePrimaries)
    destXYZ = numpy.reshape(destXYZ, [3, ])
    # destXYZ = numpy.diag(destXYZ)

    srcCone = numpy.dot(cadaptMatrix, srcXYZ)
    print("srcCone ", srcCone)
    # srcCone = numpy.diag(srcXYZ)

    destCone = numpy.dot(cadaptMatrix, destXYZ)
    print("destCone ", destCone)
    # destCone = numpy.diag(destXYZ)
    # print("destCone ", destCone)

    scaledCone = numpy.divide(destCone, srcCone)
    # scaledCone = numpy.reshape(scaledCone, [1, 3])
    print("scaledConeDivided ", scaledCone)

    scaledCone = numpy.diag(scaledCone)
    print("diagScaledCone\n", scaledCone)
    # scaledCone = numpy.reshape(scaledCone, [3, 1])

    outMatrix = numpy.dot(numpy.linalg.inv(cadaptMatrix), scaledCone)
    outMatrix = numpy.dot(outMatrix, cadaptMatrix)

    print(outMatrix)

    return outMatrix


def writeFilmlikeQuadraticLUT(subdirectory, prefix, LUTsize, curveParams):
    try:
        writeLUT = createFilmlikeQuadraticLUT(LUTsize, curveParams)
        currentDirectory = os.path.relpath(".")

        filename = prefix + "s" + str(numpy.rad2deg(
            numpy.arctan(curveParams["linearSlope"])))
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
    displayLinearIntercept = calculateIntercept(displayMiddleGrey,
                                                logMiddleGrey,
                                                linearSlope)
    logToe = calculateLog(displayToe, linearSlope, displayLinearIntercept)
    displayShoulder = displayMaximum - (maximumExposure / dynamicRangeStops *
                                        (dynamicRangeStops - latitudeStops) /
                                        dynamicRangeStops)
    logShoulder = calculateLog(displayShoulder, linearSlope,
                               displayLinearIntercept)

    quadraticControlPoints = numpy.array([
        [
            # Starting Point
            [logMinimum,  displayMinimum],
            # Quadratic Control Point
            [calculateLog(displayMinimum, linearSlope, displayLinearIntercept),
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
            [calculateLog(displayMaximum, linearSlope, displayLinearIntercept),
             displayMaximum],
            # Ending Point
            [logMaximum, displayMaximum]
        ]
    ])

    linearLUT = numpy.linspace(0., 1., LUTsize)
    outputLUT = calculateYfromXQuadratic(quadraticControlPoints, linearLUT)

    return outputLUT

# HDR-IPT
# f(w) = 246 * ((w^e)/(w^e + 2^e)) + 0.02
# e = 0.59 / (sf * lf)
# sf = 1.25 - 0.25 * (Y_surround / 0.184); 0 <= Y_suround <= 1.0
# lf = log(318) / log(Y_absolutediffusewhite)
# sf = 1.25 - 0.25 * (Y_surround / 0.184)
# LMS = XYZd65 *
# [ [0.4002,  0.7075,  -0.0807],
#   [-0.2280,   1.1500, 0.0612],
#   [0.0,   0.0,    0.9184] ]
# L' = f(L); L >= 0
# L' = -f(-L); L < 0
# M' = f(M)
# S' = f(S)
# IPThdr = L'M'S'*
# [ [0.4000, 0.4000, 0.2000],
#   [0.4550, -4.8510, 0.3960],
#   [0.8056, 0.3572, -1.1628] ]

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
