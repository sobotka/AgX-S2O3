#!/usr/bin/env python
# -*- coding: utf-8 -*-

import PyOpenColorIO
import numpy
import colour
import pathlib
import AgX

####
# Global Configuration Variables
####
output_config_directory = "./config/"
output_config_name = "config.ocio"
output_LUTs_directory = "./LUTs/"
LUT_search_paths = ["LUTs"]

AgX_min_EV = -10.0
AgX_max_EV = +6.5
AgX_x_pivot = numpy.abs(AgX_min_EV / (AgX_max_EV - AgX_min_EV))
AgX_y_pivot = 0.50

if __name__ == "__main__":
    config = PyOpenColorIO.Config()
    config.setMinorVersion(0)

    config.setSearchPath(":".join(LUT_search_paths))

    ####
    # Colourspaces
    ####

    identity_transform = PyOpenColorIO.BuiltinTransform("IDENTITY")

    # Define a generic tristimulus linear working space, with assumed
    # BT.709 primaries and a D65 achromatic point, as well as the closed
    # domain equivalent.
    config, colourspace = AgX.add_colourspace(
        config=config,
        family="Colourspaces",
        name="Linear BT.709",
        description="Open Domain Linear BT.709 Tristimulus",
        aliases=["Linear", "Linear Tristimulus", "Linear Open Domain"],
        referencespace=PyOpenColorIO.REFERENCE_SPACE_SCENE
    )

    config, colourspace = AgX.add_colourspace(
        config=config,
        family="Colourspaces",
        name="Linear BT.709 Closed Domain",
        description="Closed Domain Linear BT.709 Tristimulus",
        aliases=["Linear Closed Domain", "Linear Tristimulus Closed Domain"],
        referencespace=PyOpenColorIO.REFERENCE_SPACE_DISPLAY
    )

    transform_list = [
        identity_transform
    ]
    config, view = AgX.add_view(
        config=config,
        name="Identity View",
        family="Utilities",
        description="Identity view transform",
        transforms=transform_list
    )

    # AgX Log
    transform_list = [
        PyOpenColorIO.RangeTransform(
            minInValue=0.0,
            minOutValue=0.0
        ),
        PyOpenColorIO.MatrixTransform(
            AgX.shape_OCIO_matrix(AgX.AgX_compressed_matrix())
        ),
        PyOpenColorIO.AllocationTransform(
            allocation=PyOpenColorIO.Allocation.ALLOCATION_LG2,
            vars=[
                AgX.calculate_OCIO_log2(AgX_min_EV),
                AgX.calculate_OCIO_log2(AgX_max_EV)
            ]
        )
    ]

    config, colourspace = AgX.add_colourspace(
        config=config,
        family="Log Encodings",
        name="AgX Log",
        description="AgX Log",
        aliases=["Log"],
        transforms=transform_list
    )

    transform_list = [
        PyOpenColorIO.ColorSpaceTransform(
            src="Linear BT.709",
            dst="AgX Log"
        ),
        PyOpenColorIO.ColorSpaceTransform(
            src="2.2 EOTF Encoding",
            dst="Linear BT.709 Closed Domain"
        )
    ]

    # Reuse the transform_list
    config, view = AgX.add_view(
        config=config,
        name="AgX Log View",
        family="Log Encodings",
        description="AgX Base Log View",
        transforms=transform_list,
        referencespace=PyOpenColorIO.ReferenceSpaceType.REFERENCE_SPACE_DISPLAY
    )

    ####
    # Utilities
    ####

    # Define a generic 2.2 Electro Optical Transfer Function
    transform_list = [
        PyOpenColorIO.ExponentTransform(
            value=[2.2, 2.2, 2.2, 1.0],
            direction=PyOpenColorIO.TransformDirection.TRANSFORM_DIR_INVERSE
        )
    ]

    config, colourspace = AgX.add_colourspace(
        config=config,
        family="Utilities/Curves",
        name="2.2 EOTF Encoding",
        description="2.2 Exponent EOTF Encoding",
        aliases=["2.2 EOTF Encoding", "sRGB EOTF Encoding"],
        transforms=transform_list
    )

    ####
    # Displays
    ####

    # Define the specification sRGB Display colourspace
    transform_list = [
        PyOpenColorIO.ColorSpaceTransform(
            src="Linear BT.709 Closed Domain",
            dst="2.2 EOTF Encoding"
        )
    ]

    config, colourspace = AgX.add_colourspace(
        config=config,
        family="Displays/SDR",
        name="sRGB",
        description="sRGB IEC 61966-2-1 2.2 Exponent Reference EOTF Display",
        transforms=transform_list,
        referencespace=PyOpenColorIO.ReferenceSpaceType.REFERENCE_SPACE_DISPLAY
    )

    ####
    # Views
    ####

    transform_list = [
        PyOpenColorIO.FileTransform(
            src="AgX_Default_Contrast.spi1d"
        )
    ]

    config, look = AgX.add_look(
        config=config,
        name="Look AgX Base",
        description="AgX Base image appearance.",
        processspace="AgX Log",
        transforms=transform_list
    )

    # Add AgX Kraken aesthetic image base.
    transform_list = [
        PyOpenColorIO.LookTransform(
            src="Linear BT.709",
            dst="AgX Log",
            looks="Look AgX Base",
            skipColorSpaceConversion=False
        )
    ]

    config, view = AgX.add_view(
        config=config,
        family="Imagery",
        name="AgX Base",
        description="AgX Base Image Encoding",
        transforms=transform_list,
        referencespace=PyOpenColorIO.ReferenceSpaceType.REFERENCE_SPACE_DISPLAY
    )

    # TODO: Move all of this away.
    config.addDisplayView(
        display="sRGB",
        view="AgX",
        viewTransform="AgX Base",
        displayColorSpaceName="sRGB",
        description="AgX Base Image Encoding for sRGB displays"
    )

    config.addDisplayView(
        display="sRGB",
        view="sRGB",
        # viewTransform="AgX Log View",
        # displayColorSpaceName="sRGB",
        colorSpaceName="sRGB",
        looks="Look AgX Base",
        # description="AgX Base Image Encoding for sRGB displays"
    )

    ####
    # Data
    ####

    config, colourspace = AgX.add_colourspace(
        config=config,
        family="Data/Generic Data",
        name="Generic Data",
        aliases=["Non-Color", "Raw"],
        description="Generic data encoding",
        isdata=True
    )

    ####
    # Creative Looks LUTs
    ###

    x_input = numpy.linspace(0.0, 1.0, 4096)
    limits_contrast = [1.0, 1.0]
    general_contrast = 3.25
    y_LUT = AgX.equation_full_curve(
        x_input,
        AgX_x_pivot,
        AgX_y_pivot,
        general_contrast,
        limits_contrast
    )

    aesthetic_LUT_name = "AgX Default Contrast"
    aesthetic_LUT_safe = aesthetic_LUT_name.replace(" ", "_")
    aesthetic_LUT = colour.LUT1D(
        table=y_LUT,
        name="AgX Default Contrast"
    )

    try:
        output_directory = pathlib.Path(output_config_directory)
        LUTs_directory = output_directory / output_LUTs_directory
        LUT_filename = pathlib.Path(
            LUTs_directory / "{}.spi1d".format(aesthetic_LUT_safe)
        )
        LUTs_directory.mkdir(parents=True, exist_ok=True)
        colour.io.luts.write_LUT(aesthetic_LUT, LUT_filename, method="Sony SPI1D")

    except Exception as ex:
        raise ex

    ####
    # Config Generation
    ####

    roles = {
        # "cie_xyz_d65_interchange":,
        "color_picking": "sRGB",
        "color_timing": "sRGB",
        "compositing_log": "sRGB",
        "data": "Generic Data",
        "default": "sRGB",
        "default_byte": "sRGB",
        "default_float": "Linear BT.709",
        "default_sequencer": "sRGB",
        "matte_paint": "sRGB",
        "reference": "Linear BT.709",
        "scene_linear": "Linear BT.709",
        "texture_paint": "sRGB"
    }

    for role, transform in roles.items():
        config.setRole(role, transform)

    all_displays = {}
    all_views = {}

    # print(displays.items())
    # for display, views in displays.items():
    #     # all_displays.add(display)
    #     for view, transform in views.items():
    #         all_displays.update({display: {view: transform}})
    #         print("Adding {} {} {}".format(display, view, transform))
    #         config.addDisplayView(
    #             display=display,
    #             view=view,
    #             viewTransform=transform
    #         )

    try:
        output_directory = pathlib.Path(output_config_directory)
        output_directory.mkdir(parents=True, exist_ok=True)
        output_file = output_directory / output_config_name

        write_file = open(output_file, "w")
        write_file.write(config.serialize())
        write_file.close()
        print("Wrote config \"{}\"".format(output_config_name))
        config.validate()
    except Exception as ex:
        raise ex

    # print(config)
#     in_xy_D65 = models.sRGB_COLOURSPACE.whitepoint

#     sRGB_IE = colour.RGB_Colourspace(
#         "sRGB IE",
#         models.sRGB_COLOURSPACE.primaries,
#         [1./3., 1./3.],
#         whitepoint_name="Illuminant E",
#         cctf_decoding=models.sRGB_COLOURSPACE.cctf_decoding,
#         cctf_encoding=models.sRGB_COLOURSPACE.cctf_encoding,
#         use_derived_RGB_to_XYZ_matrix=True,
#         use_derived_XYZ_to_RGB_matrix=True)

#     ocioshape_IE_to_D65 = shape_OCIO_matrix(sRGB_IE.RGB_to_XYZ_matrix)
#     ociotransform_IE_to_D65 =\
#         PyOpenColorIO.MatrixTransform(ocioshape_IE_to_D65)

#     sRGB_domain = numpy.array([0.0, 1.0])
#     sRGB_tf_to_linear_LUT = colour.LUT1D(
#         table=models.sRGB_COLOURSPACE.cctf_decoding(
#             colour.LUT1D.linear_table(
#                 1024, sRGB_domain)),
#         name="sRGB to Linear",
#         domain=sRGB_domain,
#         comments=["sRGB CCTF to Display Linear"])
#     sRGB_linear_to_tf_LUT = colour.LUT1D(
#         table=models.sRGB_COLOURSPACE.cctf_encoding(
#             colour.LUT1D.linear_table(
#                 8192, sRGB_domain)),
#         name="Linear to sRGB",
#         domain=sRGB_domain,
#         comments=["sRGB Display Linear to CCTF"])

#     sRGB_D65_to_IE_RGB_to_RGB_matrix = colour.RGB_to_RGB_matrix(
#         models.sRGB_COLOURSPACE,
#         sRGB_IE)

#     io.write_LUT(
#         LUT=sRGB_tf_to_linear_LUT,
#         path=path_prefix_luts + "sRGB_CCTF_to_Linear.spi1d",
#         decimals=10)
#     io.write_LUT(
#         LUT=sRGB_linear_to_tf_LUT,
#         path=path_prefix_luts + "sRGB_Linear_to_CCTF.spi1d",
#         decimals=10)

#     config = PyOpenColorIO.Config()

#     config.setSearchPath(":".join(LUT_search_paths))

#     # Define the radiometrically linear working reference space
#     colourspace = PyOpenColorIO.ColorSpace(
#         family="Colourspace",
#         name="Scene Linear BT.709 IE")
#     colourspace.setDescription("Scene Linear BT.709 with IE white point")
#     colourspace.setBitDepth(PyOpenColorIO.Constants.BIT_DEPTH_F32)
#     colourspace.setAllocationVars(
#         [
#             numpy.log2(calculate_ev_to_rl(-10.0)),
#             numpy.log2(calculate_ev_to_rl(15.0))
#         ])
#     colourspace.setAllocation(PyOpenColorIO.Constants.ALLOCATION_LG2)
#     config.addColorSpace(colourspace)

#     # Define the sRGB specification
#     colourspace = PyOpenColorIO.ColorSpace(
#         family="Colourspace",
#         name="sRGB Colourspace")
#     colourspace.setDescription("sRGB IEC 61966-2-1 Colourspace")
#     colourspace.setBitDepth(PyOpenColorIO.Constants.BIT_DEPTH_F32)
#     colourspace.setAllocationVars([0.0, 1.0])
#     colourspace.setAllocation(PyOpenColorIO.Constants.ALLOCATION_UNIFORM)
#     transform_to = PyOpenColorIO.GroupTransform()
#     transform_to.push_back(
#         PyOpenColorIO.FileTransform(
#             "sRGB_CCTF_to_Linear.spi1d",
#             interpolation=PyOpenColorIO.Constants.INTERP_NEAREST))

#     ocio_sRGB_D65_to_sRGB_IE_matrix = shape_OCIO_matrix(
#         sRGB_D65_to_IE_RGB_to_RGB_matrix)
#     transform_sRGB_D65_to_sRGB_IE =\
#         PyOpenColorIO.MatrixTransform(ocio_sRGB_D65_to_sRGB_IE_matrix)
#     transform_to.push_back(transform_sRGB_D65_to_sRGB_IE)
#     transform_from = PyOpenColorIO.GroupTransform()

#     # The first object is the wrong direction re-used from above.
#     transform_sRGB_IE_to_sRGB_D65 =\
#         PyOpenColorIO.MatrixTransform(ocio_sRGB_D65_to_sRGB_IE_matrix)

#     # Flip the direction to get the proper output
#     transform_sRGB_IE_to_sRGB_D65.setDirection(
#         PyOpenColorIO.Constants.TRANSFORM_DIR_INVERSE)
#     transform_from.push_back(transform_sRGB_IE_to_sRGB_D65)
#     transform_from.push_back(
#         PyOpenColorIO.FileTransform(
#             "sRGB_Linear_to_CCTF.spi1d",
#             interpolation=PyOpenColorIO.Constants.INTERP_NEAREST))

#     colourspace.setTransform(
#         transform_to, PyOpenColorIO.Constants.COLORSPACE_DIR_TO_REFERENCE)
#     colourspace.setTransform(
#         transform_from, PyOpenColorIO.Constants.COLORSPACE_DIR_FROM_REFERENCE)

#     config.addColorSpace(colourspace)

#     # Define the commodity sRGB transform
#     colourspace = PyOpenColorIO.ColorSpace(
#         family="Colourspace",
#         name="BT.709 2.2 CCTF Colourspace")
#     colourspace.setDescription("Commodity BT.709 2.2 CCTF Colourspace")
#     colourspace.setBitDepth(PyOpenColorIO.Constants.BIT_DEPTH_F32)
#     colourspace.setAllocationVars([0.0, 1.0])
#     colourspace.setAllocation(PyOpenColorIO.Constants.ALLOCATION_UNIFORM)
#     transform_to = PyOpenColorIO.GroupTransform()
#     transform_to.push_back(
#         PyOpenColorIO.ExponentTransform([2.2, 2.2, 2.2, 1.0]))

#     transform_to.push_back(transform_sRGB_D65_to_sRGB_IE)
#     transform_from = PyOpenColorIO.GroupTransform()

#     transform_from.push_back(transform_sRGB_IE_to_sRGB_D65)
#     exponent_transform = PyOpenColorIO.ExponentTransform([2.2, 2.2, 2.2, 1.0])
#     exponent_transform.setDirection(
#         PyOpenColorIO.Constants.TRANSFORM_DIR_INVERSE)
#     transform_from.push_back(exponent_transform)

#     colourspace.setTransform(
#         transform_to, PyOpenColorIO.Constants.COLORSPACE_DIR_TO_REFERENCE)
#     colourspace.setTransform(
#         transform_from, PyOpenColorIO.Constants.COLORSPACE_DIR_FROM_REFERENCE)

#     config.addColorSpace(colourspace)

#     # Define the reference ITU-R BT.709 linear RGB to IE based
#     # reference transform
#     colourspace = PyOpenColorIO.ColorSpace(
#         family="Chromaticity",
#         name="sRGB Linear RGB")
#     colourspace.setDescription("sRGB IEC 61966-2-1 Linear RGB")
#     colourspace.setBitDepth(PyOpenColorIO.Constants.BIT_DEPTH_F32)
#     colourspace.setAllocationVars(
#         [
#             numpy.log2(calculate_ev_to_rl(-10.0)),
#             numpy.log2(calculate_ev_to_rl(15.0))
#         ])
#     colourspace.setAllocation(PyOpenColorIO.Constants.ALLOCATION_LG2)

#     transform_to = transform_sRGB_D65_to_sRGB_IE
#     transform_from = transform_sRGB_IE_to_sRGB_D65

#     colourspace.setTransform(
#         transform_to, PyOpenColorIO.Constants.COLORSPACE_DIR_TO_REFERENCE)
#     colourspace.setTransform(
#         transform_from, PyOpenColorIO.Constants.COLORSPACE_DIR_FROM_REFERENCE)

#     config.addColorSpace(colourspace)

#     # Define the reference ITU-R BT.709 Illuminant E white point basd
#     # reference space to linear XYZ transform
#     colourspace = PyOpenColorIO.ColorSpace(
#         family="Chromaticity",
#         name="XYZ IE")
#     colourspace.setDescription("XYZ transform with Illuminant E white point")
#     colourspace.setBitDepth(PyOpenColorIO.Constants.BIT_DEPTH_F32)
#     colourspace.setAllocationVars(
#         [
#             numpy.log2(calculate_ev_to_rl(-10.0)),
#             numpy.log2(calculate_ev_to_rl(15.0))
#         ])
#     colourspace.setAllocation(PyOpenColorIO.Constants.ALLOCATION_LG2)

#     ocio_sRGB_IE_to_XYZ_IE_matrix = shape_OCIO_matrix(
#         sRGB_IE.RGB_to_XYZ_matrix
#     )
#     transform_sRGB_IE_to_XYZ_IE =\
#         PyOpenColorIO.MatrixTransform(ocio_sRGB_IE_to_XYZ_IE_matrix)

#     transform_to = transform_sRGB_IE_to_XYZ_IE

#     # Initialize with the matrix the wrong direction
#     transform_from =\
#         PyOpenColorIO.MatrixTransform(ocio_sRGB_IE_to_XYZ_IE_matrix)
#     # Set the proper direction
#     transform_from.setDirection(PyOpenColorIO.Constants.TRANSFORM_DIR_INVERSE)

#     colourspace.setTransform(
#         transform_to, PyOpenColorIO.Constants.COLORSPACE_DIR_TO_REFERENCE)
#     colourspace.setTransform(
#         transform_from, PyOpenColorIO.Constants.COLORSPACE_DIR_FROM_REFERENCE)

#     config.addColorSpace(colourspace)

#     # Define the Non-Colour Data transform
#     colorspace = PyOpenColorIO.ColorSpace(
#         family="Data",
#         name="Float Data")
#     colorspace.setDescription("Float data that does not define a colour")
#     colorspace.setBitDepth(PyOpenColorIO.Constants.BIT_DEPTH_F32)
#     colorspace.setIsData(True)
#     config.addColorSpace(colorspace)

#     # Define the luminance coefficients for the configuration
#     config.setDefaultLumaCoefs(sRGB_IE.RGB_to_XYZ_matrix[1])

#     config.setRole(
#         PyOpenColorIO.Constants.ROLE_SCENE_LINEAR,
#         "Scene Linear BT.709 IE")
#     config.setRole(
#         PyOpenColorIO.Constants.ROLE_REFERENCE,
#         "Scene Linear BT.709 IE")
#     config.setRole(
#         PyOpenColorIO.Constants.ROLE_COLOR_TIMING,
#         "sRGB Colourspace")
#     config.setRole(
#         PyOpenColorIO.Constants.ROLE_COMPOSITING_LOG,
#         "sRGB Colourspace")
#     config.setRole(
#         PyOpenColorIO.Constants.ROLE_COLOR_PICKING,
#         "sRGB Colourspace")
#     config.setRole(
#         PyOpenColorIO.Constants.ROLE_DATA,
#         "Float Data")
#     config.setRole(
#         PyOpenColorIO.Constants.ROLE_DEFAULT,
#         "sRGB Colourspace")
#     config.setRole(
#         PyOpenColorIO.Constants.ROLE_MATTE_PAINT,
#         "sRGB Colourspace")
#     config.setRole(
#         PyOpenColorIO.Constants.ROLE_TEXTURE_PAINT,
#         "sRGB Colourspace")

#     # Define the Blender Role RGB to XYZ
#     config.setRole(
#         "XYZ",
#         "XYZ IE")

#     displays = {
#         "sRGB-Like Commodity Display": {
#             "Display Native": "BT.709 2.2 CCTF Colourspace"
#         },
#         "sRGB Display": {
#             "Display Native": "sRGB Colourspace"
#         }
#     }

#     all_displays = set()
#     all_views = set()

#     for display, views in displays.items():
#         all_displays.add(display)
#         for view, transform in views.items():
#             all_views.add(view)
#             config.addDisplay(display, view, transform)

#     config.setActiveDisplays(", ".join(all_displays))
#     config.setActiveViews(", ".join(all_views))

#     try:
#         config.sanityCheck()
#         write_file = open(output_config_name, "w")
#         write_file.write(config.serialize())
#         write_file.close()
#         print("Wrote config \"{}\"".format(output_config_name))
#     except Exception as ex:
#         raise ex