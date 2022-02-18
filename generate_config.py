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

supported_displays = {
    "Display P3": {
        "Display Native": "Display P3 Display",
        "AgX": "AgX Display P3 Display"
    },
    "sRGB": {
        "Display Native": "sRGB Display",
        "AgX": "AgX sRGB Display"
    },
    "BT.1886": {
        "Display Native": "Display P3 Display",
        "AgX": "AgX BT.1886 Display"
    },
    "HDR 1000": {
        "Display Native": "Display P3 Display",
        "AgX": "AgX HDR 1000 Display"
    }
}

AgX_min_EV = -10.0
AgX_max_EV = +10.0
AgX_x_pivot = numpy.abs(AgX_min_EV / (AgX_max_EV - AgX_min_EV))
AgX_y_pivot = 0.50

if __name__ == "__main__":
    config = PyOpenColorIO.Config()
    config.setMinorVersion(0)

    config.setSearchPath(":".join(LUT_search_paths))

    # Establish a displays dictionary to track the displays. Append
    # the respective display at each of the display colourspace definitions
    # for clarity.
    displays = {}

    # Establish a colourspaces dictionary for fetching colourspace objects.
    colourspaces = {}

    ####
    # Colourspaces
    ####

    # Define a generic tristimulus linear working space, with assumed
    # BT.709 primaries and a D65 achromatic point.
    config, colourspace = AgX.add_colourspace(
        config=config,
        family="Colourspaces",
        name="Linear BT.709",
        description="Open Domain Linear BT.709 Tristimulus",
        aliases=["Linear", "Linear Tristimulus"]
    )

    # AgX
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
        name="AgX Log (Kraken)",
        description="AgX Log, (Kraken)",
        aliases=["Log", "AgX Log", "Kraken", "AgX Kraken Log"],
        transforms=transform_list
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

    # Define a generic 2.4 Electro Optical Transfer Function
    transform_list = [
        PyOpenColorIO.ExponentTransform(
            value=[2.4, 2.4, 2.4, 1.0],
            direction=PyOpenColorIO.TransformDirection.TRANSFORM_DIR_INVERSE
        )
    ]

    config, colourspace = AgX.add_colourspace(
        config=config,
        family="Utilities/Curves",
        name="2.4 EOTF Encoding",
        description="2.4 Exponent EOTF Encoding",
        aliases=["2.4 EOTF Encoding", "BT.1886 EOTF Encoding"],
        transforms=transform_list
    )

    ####
    # Displays
    ####

    # Define the specification sRGB Display colourspace
    transform_list = [
        PyOpenColorIO.ColorSpaceTransform(
            src="Linear BT.709",
            dst="2.2 EOTF Encoding"
        )
    ]

    config, colourspace = AgX.add_colourspace(
        config=config,
        family="Displays/SDR",
        name="sRGB",
        description="sRGB IEC 61966-2-1 2.2 Exponent Reference EOTF Display",
        transforms=transform_list,
        referencespace=PyOpenColorIO.ReferenceSpaceType.REFERENCE_SPACE_SCENE
    )

    # TODO: Move this to a different section.
    AgX.add_view(
        displays, "sRGB", "Display Native", "sRGB"
    )

    # Add Display P3.
    Display_P3_Colourspace = colour.RGB_COLOURSPACES["Display P3"]
    sRGB_Colourspace = colour.RGB_COLOURSPACES["sRGB"]
    D_P3_RGB_to_sRGB_matrix = colour.matrix_RGB_to_RGB(
        sRGB_Colourspace, Display_P3_Colourspace
    )

    transform_list = [
        PyOpenColorIO.MatrixTransform(AgX.shape_OCIO_matrix(D_P3_RGB_to_sRGB_matrix)),
        PyOpenColorIO.ColorSpaceTransform(
            src="Linear BT.709",
            dst="2.2 EOTF Encoding"
        )
    ]

    config, colourspace = AgX.add_colourspace(
        config=config,
        family="Displays/SDR",
        name="Display P3",
        description="Display P3 2.2 Exponent EOTF Display",
        transforms=transform_list,
        referencespace=PyOpenColorIO.ReferenceSpaceType.REFERENCE_SPACE_SCENE
    )

    # TODO: Move this to a different section.
    AgX.add_view(
        displays, "Display P3", "Display Native", "Display P3"
    )

    # Add BT.1886.
    transform_list = [
        PyOpenColorIO.ColorSpaceTransform(
            src="Linear BT.709",
            dst="2.4 EOTF Encoding"
        )
    ]

    config, colourspace = AgX.add_colourspace(
        config=config,
        family="Displays/SDR",
        name="BT.1886",
        description="BT.1886 2.4 Exponent EOTF Display",
        transforms=transform_list,
        referencespace=PyOpenColorIO.ReferenceSpaceType.REFERENCE_SPACE_SCENE
    )

    # TODO: Move this to a different section.
    AgX.add_view(
        displays, "BT.1886", "Display Native", "BT.1886"
    )

    ####
    # Views
    ####

    # Add AgX Kraken aesthetic image base.
    transform_list = [
        PyOpenColorIO.ColorSpaceTransform(
            src="Linear BT.709",
            dst="AgX Log (Kraken)"
        ),
        PyOpenColorIO.FileTransform(
            src="AgX_Default_Contrast.spi1d"
        )
    ]

    config, colourspace = AgX.add_colourspace(
        config=config,
        family="Imagery",
        name="AgX Base",
        description="AgX Base Image Encoding",
        transforms=transform_list,
        referencespace=PyOpenColorIO.ReferenceSpaceType.REFERENCE_SPACE_SCENE
    )

    # TODO: Move this to a different section.
    AgX.add_view(
        displays, "sRGB", "AgX", "AgX Base"
    )

    # Add BT.1886 AgX Kraken aesthetic image base.
    transform_list = [
        PyOpenColorIO.ColorSpaceTransform(
            src="Linear BT.709",
            dst="AgX Base"
        ),
        PyOpenColorIO.ColorSpaceTransform(
            src="2.2 EOTF Encoding",
            dst="2.4 EOTF Encoding"
        )
    ]

    config, colourspace = AgX.add_colourspace(
        config=config,
        family="Views/AgX BT.1886",
        name="AgX Base BT.1886",
        description="AgX Base Image Encoding for BT.1886 Displays",
        transforms=transform_list,
        referencespace=PyOpenColorIO.ReferenceSpaceType.REFERENCE_SPACE_SCENE
    )

    # TODO: Move this to a different section.
    AgX.add_view(
        displays, "BT.1886", "AgX", "AgX Base BT.1886"
    )

    # Add Display P3 AgX Kraken aesthetic image base.
    transform_list = [
        PyOpenColorIO.ColorSpaceTransform(
            src="Linear BT.709",
            dst="AgX Base"
        ),
        PyOpenColorIO.ColorSpaceTransform(
            src="2.2 EOTF Encoding",
            dst="Display P3"
        )
    ]

    config, colourspace = AgX.add_colourspace(
        config=config,
        family="Views/AgX Display P3",
        name="AgX Base Display P3",
        description="AgX Base Image Encoding for Display P3 Displays",
        transforms=transform_list,
        referencespace=PyOpenColorIO.ReferenceSpaceType.REFERENCE_SPACE_SCENE
    )

    # TODO: Move this to a different section.
    AgX.add_view(
        displays, "Display P3", "AgX", "AgX Base Display P3"
    )

####
# Appearances / Looks
####

    # Add a heavily tinted washed look.
    # Golden Kraken
    transform_list = [
        PyOpenColorIO.CDLTransform(
            slope=[1.0, 0.9, 0.5],
            power=[0.8, 0.8, 0.8],
            sat=1.3
        )
    ]

    config, look = AgX.add_look(
        config=config,
        name="Golden",
        description="A golden tinted, slightly washed look",
        transforms=transform_list
    )

    # Add a crunchier and more saturated look.
    # Punchy Kraken
    transform_list = [
        PyOpenColorIO.CDLTransform(
            slope=[1.0, 1.0, 1.0],
            power=[1.35, 1.35, 1.35],
            sat=1.4
        )
    ]

    config, colourspace = AgX.add_look(
        config=config,
        name="Punchy",
        description="A punchy and more chroma laden look",
        transforms=transform_list
    )

    # Add Golden for all displays.
    # sRGB
    transform_list = [
        PyOpenColorIO.LookTransform(
            src="Linear BT.709",
            dst="AgX Base",
            looks="Golden"
        )
    ]

    config, colourspace = AgX.add_colourspace(
        config=config,
        family="Appearances/Golden",
        name="Appearance Golden sRGB",
        description="A golden tinted, slightly washed look for sRGB displays",
        transforms=transform_list
    )

    AgX.add_view(
        displays, "sRGB", "Appearance Golden", "Appearance Golden sRGB"
    )

    # Display P3
    transform_list = [
        PyOpenColorIO.LookTransform(
            src="Linear BT.709",
            dst="AgX Base",
            looks="Golden"
        ),
        PyOpenColorIO.ColorSpaceTransform(
            src="2.2 EOTF Encoding",
            dst="Display P3"
        )
    ]

    config, colourspace = AgX.add_colourspace(
        config=config,
        family="Appearances/Golden",
        name="Appearance Golden Display P3",
        description="A golden tinted, slightly washed look for Display P3 displays",
        transforms=transform_list
    )

    AgX.add_view(
        displays, "Display P3", "Appearance Golden", "Appearance Golden Display P3"
    )

    # Display BT.1886
    transform_list = [
        PyOpenColorIO.LookTransform(
            src="Linear BT.709",
            dst="AgX Base",
            looks="Golden"
        ),
        PyOpenColorIO.ColorSpaceTransform(
            src="2.2 EOTF Encoding",
            dst="2.4 EOTF Encoding"
        )
    ]

    config, colourspace = AgX.add_colourspace(
        config=config,
        family="Appearances/Golden",
        name="Appearance Golden BT.1886",
        description="A golden tinted, slightly washed look for BT.1886 displays",
        transforms=transform_list
    )

    AgX.add_view(
        displays, "BT.1886", "Appearance Golden", "Appearance Golden BT.1886"
    )

    # Add Punchy for all displays.
    # sRGB
    transform_list = [
        PyOpenColorIO.LookTransform(
            src="Linear BT.709",
            dst="AgX Base",
            looks="Punchy"
        )
    ]

    config, colourspace = AgX.add_colourspace(
        config=config,
        family="Appearances/Punchy",
        name="Appearance Punchy sRGB",
        description="A punchy and more chroma laden look for sRGB displays",
        transforms=transform_list
    )

    AgX.add_view(
        displays, "sRGB", "Appearance Punchy", "Appearance Punchy sRGB"
    )

    # Display P3
    transform_list = [
        PyOpenColorIO.LookTransform(
            src="Linear BT.709",
            dst="AgX Base",
            looks="Punchy"
        ),
        PyOpenColorIO.ColorSpaceTransform(
            src="2.2 EOTF Encoding",
            dst="Display P3"
        )
    ]

    config, colourspace = AgX.add_colourspace(
        config=config,
        family="Appearances/Punchy",
        name="Appearance Punchy Display P3",
        description="A punchy and more chroma laden look for Display P3 displays",
        transforms=transform_list
    )

    AgX.add_view(
        displays, "Display P3", "Appearance Punchy", "Appearance Punchy Display P3"
    )

    # Display BT.1886
    transform_list = [
        PyOpenColorIO.LookTransform(
            src="Linear BT.709",
            dst="AgX Base",
            looks="Punchy"
        ),
        PyOpenColorIO.ColorSpaceTransform(
            src="2.2 EOTF Encoding",
            dst="2.4 EOTF Encoding"
        )
    ]

    config, colourspace = AgX.add_colourspace(
        config=config,
        family="Appearances/Punchy",
        name="Appearance Punchy BT.1886",
        description="A punchy and more chroma laden look for BT.1886 displays",
        transforms=transform_list
    )

    AgX.add_view(
        displays, "BT.1886", "Appearance Punchy", "Appearance Punchy BT.1886"
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
    general_contrast = 3.0
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

    print(displays.items())
    for display, views in displays.items():
        # all_displays.add(display)
        for view, transform in views.items():
            all_displays.update({display: {view: transform}})
            print("Adding {} {} {}".format(display, view, transform))
            config.addDisplayView(
                display=display,
                view=view,
                colorSpaceName=transform
            )

    try:
        config.validate()

        output_directory = pathlib.Path(output_config_directory)
        output_directory.mkdir(parents=True, exist_ok=True)
        output_file = output_directory / output_config_name

        write_file = open(output_file, "w")
        write_file.write(config.serialize())
        write_file.close()
        print("Wrote config \"{}\"".format(output_config_name))
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