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


def dl_to_srgb_oetf(in_dl):
    return numpy.where(
        in_dl <= 0.0031308,
        in_dl * 12.92,
        numpy.power(1.055 * in_dl, 1./2.4) - 0.055
    )


def calculate_y_from_x_quadratic(cP, inValues):
    inValues = numpy.asarray(inValues)
    outY = numpy.zeros(inValues.shape[0])
    cP = numpy.asarray(cP)

    if cP.shape[0] <= 0:
        raise ValueError(
            "Invalid number of control points for a quadratic curve.\n"
            "\tQuadratic curves must have at least one set of three "
            "control points."
        )

    if cP.shape[1] != 3:
        raise ValueError(
            "Invalid number of control points for a quadratic curve.\n"
            "\tQuadratic curves require three control points per "
            "section."
        )

    for index in range(inValues.shape[0]):
        for curCP in cP:
            if curCP[0][0] <= inValues[index] <= curCP[2][0]:
                coefficients = [
                    curCP[0][0] - (2. * curCP[1][0]) + curCP[2][0],
                    (2. * curCP[1][0]) - (2. * curCP[0][0]),
                    curCP[0][0] - inValues[index]
                ]

                roots = numpy.roots(coefficients)
                correct_root = None

                for root in roots:
                    if numpy.isreal(root) and (0. <= root < 1.):
                        correct_root = root
                    elif inValues[index] == 1.:
                        correct_root = 1.

                if correct_root is not None:
                    root_t = correct_root
                    outY[index] = (
                        ((1. - root_t)**2. * curCP[0][1]) +
                        (2. * (1. - root_t) * root_t * curCP[1][1]) +
                        (root_t**2. * curCP[2][1]))
                    break

                if correct_root is None:
                    raise ValueError(
                        "No valid root found for coefficients. Invalid curve "
                        "or input x value."
                    )
    return as_numeric(outY)


def calculate_y_from_x_cubic(cP, inValues):
    inValues = numpy.asarray(inValues)
    outY = numpy.zeros(inValues.shape[0])
    cP = numpy.asarray(cP)

    if cP.shape[0] <= 0:
        raise ValueError(
            "Invalid number of control points for a cubic curve."
        )

    if cP.shape[1] != 4:
        raise ValueError(
            "Invalid number of control points for a cubic curve.\n"
            "\tCubic curves require four control points per "
            "section."
        )

    for index in range(inValues.shape[0]):
        for curCP in cP:
            if curCP[0][0] <= inValues[index] <= curCP[3][0]:
                coefficients = [
                    -curCP[0][0] + 3. * curCP[1][0] - 3. * curCP[2][0] +
                    curCP[3][0],
                    3. * curCP[0][0] - 6 * curCP[1][0] + 3 * curCP[2][0],
                    -3 * curCP[0][0] + 3 * curCP[1][0],
                    curCP[0][0] - inValues[index]
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
                        (1. - root_t) * root_t**2. * curCP[2][1] + root_t**3. *
                        curCP[3][1])
                    break

                if correct_root is None:
                    raise ValueError(
                        "No valid root found for coefficients. Invalid curve "
                        "or input x value."
                    )

    return as_numeric(outY)

# Scene referred middle grey encoding
base_middle_grey = 0.18

# Default dynamic range values
# Loosely based on Kodak Vision3 stocks
base_dr_ev = 17.0
base_dr_minimum_ev = -7.0
base_dr_maximum_ev = +10.0
base_dr_offset = abs(
    base_dr_minimum_ev / base_dr_ev
)

# Default latitude values
# Loosely based on Kodak Vision3 stocks
base_l_ev = 10.0
base_l_minimum_ev = -4.0
base_l_maximum_ev = +6.5
base_l_offset = abs(base_l_minimum_ev / base_l_ev)
base_l_ratio = base_l_ev / base_dr_ev


# Convert scene referred linear value to normalised log value.
def calculate_sr_to_log(
    in_sr,
    sr_middle_grey=base_middle_grey,
    minimum_ev=base_dr_minimum_ev,
    maximum_ev=base_dr_maximum_ev
):
    # 2^stops * middleGrey = linear
    # log(2)*stops * middleGrey = log(linear)
    # stops = log(linear)/log(2)*middleGrey
    total_exposure = maximum_ev - minimum_ev

    in_sr = numpy.asarray(in_sr)
    in_sr[in_sr <= 0.] = numpy.finfo(numpy.float).eps

    output_log = numpy.clip(
        numpy.log2(in_sr / sr_middle_grey),
        minimum_ev,
        maximum_ev
    )

    return as_numeric((output_log - minimum_ev) / total_exposure)


# Convert normalised log value to scene referred linear value.
def calculate_log_to_sr(
    in_log_norm,
    sr_middle_grey=base_middle_grey,
    minimum_ev=base_dr_minimum_ev,
    maximum_ev=base_dr_maximum_ev
):
    in_log_norm = numpy.asarray(in_log_norm)

    in_log_norm = numpy.clip(in_log_norm, 0., 1.) * (
        maximum_ev - minimum_ev) + minimum_ev

    return as_numeric(numpy.power(2., in_log_norm) * sr_middle_grey)


# Convert relative EV to scene referred linear value.
def calculate_ev_to_sr(
    in_ev,
    sr_middle_grey=base_middle_grey
):
    in_ev = numpy.asarray(in_ev)

    return as_numeric(numpy.power(2., in_ev) * sr_middle_grey)


# Convert scene referred linear value to relative EV
def calculate_sr_to_ev(
    in_sr,
    sr_middle_grey=base_middle_grey
):
    in_sr = numpy.asarray(in_sr)

    return as_numeric(numpy.log2(in_sr) - numpy.log2(sr_middle_grey))


# Convert film log 10 density to linear transmission
def calculate_density_to_transmission(
    in_density
):
    in_density = numpy.asarray(in_density)

    return as_numeric(numpy.power(10., in_density))


# Convert linear transmission to log 10 film density
def calculate_transmission_to_density(
    in_transmission
):
    in_transmission = numpy.asarray(in_transmission)

    return as_numeric(numpy.log10(in_transmission))


# Linearly interpolate from start to end by given ratio.
def calculate_linear_interpolate(start, end, ratio):
    return (end - start) * ratio + start


# Calculate the Y intercept based on slope and an
# X / Y coordinate pair.
def calculate_line_y_intercept(in_x, in_y, slope):
    # y = mx + b, b = y - mx
    return (in_y - (slope * in_x))


# Calculate the Y of a line given by slope and X coordinate.
def calculate_line_y(in_x, y_intercept, slope):
    # y = mx + b
    return (slope * in_x) + y_intercept


# Calculate the X of a line given by the slope and Y coordinate.
def calculate_line_x(in_y, y_intercept, slope):
    # y = mx + b, x = (y - b) / m
    return (in_y - y_intercept) / slope


# Calculate the slope of a line given by the Y intercept
# and an X / Y coordinate pair.
def calculate_line_slope(in_x, in_y, y_intercept):
    # y = mx + b, m = (y - b) / x
    return (in_y - y_intercept) / in_x