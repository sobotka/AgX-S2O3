#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Defines utility functions.
"""

import numpy


def calculateYfromXQuadratic(cP, inX):
    for inValue in inX:
        if (len(cP)) <= 0:
            raise ValueError(
                "Invalid number of control points for a quadratic curve."
            )

        for index, curCP in enumerate(cP):
            if len(curCP) != 3:
                raise ValueError(
                    "Invalid number of control points for a quadratic curve.\n"
                    "Quadratic curves require three control points per "
                    "section."
                )

            coefficients = [
                curCP[0][0] - (2. * curCP[1][0]) + curCP[2][0],
                (2. * curCP[1][0]) - (2. * curCP[0][0]),
                curCP[0][0] - inValue
            ]

            roots = numpy.roots(coefficients)
            correct_root = None

            for root in roots:
                if numpy.isreal(root) and 0 <= root <= 1:
                    correct_root = root

            if correct_root is not None:
                root_t = correct_root
                outY = (((1. - root_t)**2. * curCP[0][1]) +
                        (2. * (1. - root_t) * root_t * curCP[1][1]) +
                        (root_t**2. * curCP[2][1]))
                break

        if correct_root is None:
            raise ValueError(
                "No valid root found for coefficients. Invalid curve or "
                "input x value."
            )

        yield outY


def calculateYfromXCubic(cP, inX):
    for inValue in inX:
        if (len(cP)) <= 0:
            raise ValueError(
                "Invalid number of control points for a cubic curve."
            )

        for index, curCP in enumerate(cP):
            if len(curCP) != 4:
                raise ValueError(
                    "Invalid number of control points for a cubic curve.\n"
                    "Cubic curves require four control points per "
                    "section."
                )

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
                if numpy.isreal(root) and 0 <= root <= 1:
                    correct_root = root

            if correct_root is not None:
                root_t = correct_root
                outY = ((1. - root_t)**3. * curCP[0][1] + 3. *
                        (1. - root_t)**2. * root_t * curCP[1][1] + 3. *
                        (1. - root_t) * root_t**2. * curCP[2][1] + root_t**3.
                        * curCP[3][1])
                break

        if correct_root is None:
            raise ValueError(
                "No valid root found for coefficients. Invalid curve or "
                "input x value."
            )

        yield outY


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
    for inValue in inLin:
        if (inValue <= 0.):
            yield 0.

        lg2 = numpy.log2(inValue / middleGrey)
        logNorm = (lg2 - minExposure) / (maxExposure - minExposure)

        if(logNorm < 0.):
            yield 0.

        yield logNorm


def calculateLinToLog_f(inLin, middleGrey, minExposure, maxExposure):
    if (inLin <= 0.):
        return 0.

    lg2 = numpy.log2(inLin / middleGrey)
    logNorm = (lg2 - minExposure) / (maxExposure - minExposure)

    if(logNorm < 0.):
        return 0.

    return logNorm


def calculateLogToLin(inLogNorm, middleGrey, minExposure, maxExposure):
    for inValue in inLogNorm:
        if (inValue < 0.):
            yield 0.

        lg2 = inValue * (maxExposure - minExposure) + minExposure
        lin = pow(2., lg2) * middleGrey

        yield lin


def calculateLogToLin_f(inLogNorm, middleGrey, minExposure, maxExposure):
    if (inLogNorm < 0.):
        return 0.

    lg2 = inLogNorm * (maxExposure - minExposure) + minExposure
    lin = pow(2., lg2) * middleGrey

    return lin


def calculateStopsToLin(inStops, middleGrey):
    return pow(2., inStops) * middleGrey
