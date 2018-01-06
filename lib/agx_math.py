#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Defines utility functions.
"""

import numpy


def as_numeric(obj, as_type=numpy.float64):
    try:
        return as_type(obj)
    except TypeError:
        return obj


def calculateYfromXQuadratic(cP, inValues):
    inValues = numpy.asarray(inValues)
    outY = numpy.zeros(inValues.size)
    cP = numpy.asarray(cP)

    for index, inValue in numpy.ndenumerate(inValues):
        if len(cP) <= 0:
            raise ValueError(
                "Invalid number of control points for a quadratic curve.\n"
                "\tQuadratic curves must have at least one set of three "
                "control points."
            )

        for curCP in cP:
            if len(curCP) != 3:
                raise ValueError(
                    "Invalid number of control points for a quadratic curve.\n"
                    "\tQuadratic curves require three control points per "
                    "section."
                )

            if curCP[0][0] <= inValue <= curCP[2][0]:
                coefficients = [
                    curCP[0][0] - (2. * curCP[1][0]) + curCP[2][0],
                    (2. * curCP[1][0]) - (2. * curCP[0][0]),
                    curCP[0][0] - inValue
                ]

                roots = numpy.roots(coefficients)
                correct_root = None

                for root in roots:
                    if numpy.isreal(root) and (0. <= root < 1.):
                        correct_root = root
                    elif inValue == 1.:
                        correct_root = 1.

                if correct_root is not None:
                    root_t = correct_root
                    outV = (((1. - root_t)**2. * curCP[0][1]) +
                            (2. * (1. - root_t) * root_t * curCP[1][1]) +
                            (root_t**2. * curCP[2][1]))
                    outY[index] = outV
                    break

                if correct_root is None:
                    print("*** ERROR ***: inValue[", index, "]: ", inValue)
                    raise ValueError(
                        "No valid root found for coefficients. Invalid curve "
                        "or input x value."
                    )
    return as_numeric(outY)


def calculateYfromXCubic(cP, inValues):
    inValues = numpy.asarray(inValues)
    outY = numpy.zeros(inValues.size)
    cP = numpy.asarray(cP)

    for index, inValue in numpy.ndenumerate(inValues):
        if len(cP) <= 0:
            raise ValueError(
                "Invalid number of control points for a cubic curve."
            )

        for curCP in cP:
            if len(curCP) != 4:
                raise ValueError(
                    "Invalid number of control points for a cubic curve.\n"
                    "\tCubic curves require four control points per "
                    "section."
                )

            if curCP[0][0] <= inValue <= curCP[3][0]:
                coefficients = [
                    -curCP[0][0] + 3. * curCP[1][0] - 3. * curCP[2][0] +
                    curCP[3][0],
                    3. * curCP[0][0] - 6 * curCP[1][0] + 3 * curCP[2][0],
                    -3 * curCP[0][0] + 3 * curCP[1][0],
                    curCP[0][0] - inValue
                ]

                roots = numpy.roots(coefficients)
                correct_root = None

                for root in roots:
                    if numpy.isreal(root) and (0. <= root <= 1.):
                        correct_root = root

                if correct_root is not None:
                    root_t = correct_root
                    outY[index] = (
                        (1. - root_t)**3. * curCP[0][1] + 3. *
                        (1. - root_t)**2. * root_t * curCP[1][1] + 3. *
                        (1. - root_t) * root_t**2. * curCP[2][1] + root_t**3.
                        * curCP[3][1])
                    break

                if correct_root is None:
                    raise ValueError(
                        "No valid root found for coefficients. Invalid curve "
                        "or input x value. Control Point: ", curCP,
                        " Index Value[", index, "]: ", inValue[index]
                    )

    return as_numeric(outY)


def calculateIntercept(dispIn, logIn, slope):
    # y = mx + b, b = y - mx
    return (dispIn - (slope * logIn))


def calculateSlope(startX, startY, endX, endY):
    return (endY - startY) / (endX - startX)


def calculateLog(dispIn, slope, intercept):
    # y = mx + b, x = (y - b) / m
    return (dispIn - intercept) / slope


def calculateDisplay(logIn, slope, intercept):
    # y = mx + b
    return (slope * logIn) + intercept


def calculateRatio(start, end, ratio):
    return (end - start) * ratio + start


def calculateLinToLog(inLin, middleGrey, minExposure, maxExposure):
    # 2^stops * middleGrey = linear
    # log(2)*stops * middleGrey = log(linear)
    # stops = log(linear)/log(2)*middleGrey
    inLin = numpy.asarray(inLin)
    outLog = numpy.zeros(inLin.size)

    for index, inValue in numpy.ndenumerate(inLin):
        if (inValue <= 0.):
            outLog[index] = 0.

        lg2 = numpy.log2(inValue / middleGrey)
        outLog[index] = (lg2 - minExposure) / (maxExposure - minExposure)

        if(outLog[index] < 0.):
            outLog[index] = 0.

    return as_numeric(outLog)


def calculateLogToLin(inLogNorm, middleGrey, minExposure, maxExposure):
    inLogNorm = numpy.asarray(inLogNorm)
    outLin = numpy.zeros(inLogNorm.size)

    for index, inValue in numpy.ndenumerate(inLogNorm):
        if (inValue < 0.):
            outLin[index] = 0.

        lg2 = inValue * (maxExposure - minExposure) + minExposure
        outLin[index] = pow(2., lg2) * middleGrey

    return as_numeric(outLin)


def calculateStopsToLin(inStops, middleGrey):
    return pow(2., inStops) * middleGrey
