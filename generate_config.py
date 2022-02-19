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
AgX_y_pivot = 0.5

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
        aliases=["Linear Closed", "Linear Closed Tristimulus", "Linear Closed Domain"],
        referencespace=PyOpenColorIO.REFERENCE_SPACE_DISPLAY
    )

    transform_list = [
        identity_transform
    ]
    config, view = AgX.add_view(
        config=config,
        name="Identity View",
        family="Views",
        description="Identity view transform bridge",
        transforms=transform_list
    )

    transform_list = [
        PyOpenColorIO.ExponentTransform(
            value=[2.2, 2.2, 2.2, 1.0],
            direction=PyOpenColorIO.TransformDirection.TRANSFORM_DIR_INVERSE
        )
    ]
    config, colourspace = AgX.add_colourspace(
        config=config,
        family="Colourspaces",
        name="sRGB",
        description="BT.709 Encoded",
        transforms=transform_list,
        referencespace=PyOpenColorIO.REFERENCE_SPACE_DISPLAY
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
        name="Log",
        description="Log",
        aliases=["Log"],
        transforms=transform_list
    )

    transform_list = [
        PyOpenColorIO.ColorSpaceTransform(
            src="Linear BT.709",
            dst="Log"
        ),
        PyOpenColorIO.ExponentTransform(
            value=[2.2, 2.2, 2.2, 1.0],
            direction=PyOpenColorIO.TransformDirection.TRANSFORM_DIR_FORWARD
        )
    ]

    config, colourspace = AgX.add_colourspace(
        config=config,
        family="Imagery",
        name="Image Log",
        description="Reference image",
        transforms=transform_list,
        referencespace=PyOpenColorIO.REFERENCE_SPACE_DISPLAY
    )

    transform_list = [
        PyOpenColorIO.ColorSpaceTransform(
            src="Linear BT.709",
            dst="Image Log"
        )
    ]

    config, colourspace = AgX.add_view(
        config=config,
        family="Imagery",
        name="Image Log View",
        description="Reference image",
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

    config, colourspace = AgX.add_view(
        config=config,
        family="Views/Curves",
        name="2.2 EOTF Encoding",
        description="2.2 Exponent EOTF Encoding View",
        transforms=transform_list
    )

    ####
    # Displays
    ####

    # Define the specification sRGB Display colourspace
    # transform_list = [
    #     PyOpenColorIO.ColorSpaceTransform(
    #         src="Linear Closed Domain",
    #         dst="2.2 EOTF Encoding"
    #     )
    # ]

    # config, colourspace = AgX.add_colourspace(
    #     config=config,
    #     family="Displays/SDR",
    #     name="sRGB",
    #     description="sRGB IEC 61966-2-1 2.2 Exponent Reference EOTF Display",
    #     transforms=transform_list,
    #     referencespace=PyOpenColorIO.ReferenceSpaceType.REFERENCE_SPACE_DISPLAY
    # )

    # config, view = AgX.add_view(
    #     config=config,
    #     family="Utilities",
    #     name="EOTF 2.2 Encoding View",
    #     description="EOTF 2.2 Encoding View",
    #     transforms=transform_list,
    #     referencespace=PyOpenColorIO.ReferenceSpaceType.REFERENCE_SPACE_DISPLAY
    # )
    ####
    # Views
    ####

    # Add AgX Kraken aesthetic image base.
    # transform_list = [
    #     PyOpenColorIO.ColorSpaceTransform(
    #         src="Linear Open Domain",
    #         dst="AgX Log"
    #     ),
    #     PyOpenColorIO.ExponentTransform(
    #         value=[2.2, 2.2, 2.2, 1.0],
    #         direction=PyOpenColorIO.TransformDirection.TRANSFORM_DIR_FORWARD
    #     )
    # ]

    # config, view = AgX.add_view(
    #     config=config,
    #     family="Imagery",
    #     name="AgX Log View",
    #     description="AgX Base Image Encoding",
    #     transforms=transform_list,
    #     referencespace=PyOpenColorIO.ReferenceSpaceType.REFERENCE_SPACE_DISPLAY
    # )

    transform_list = [
        PyOpenColorIO.ColorSpaceTransform(
            src="Linear BT.709",
            dst="Image Log"
        ),
        PyOpenColorIO.ExponentTransform(
            value=[2.2, 2.2, 2.2, 1.0],
            direction=PyOpenColorIO.TransformDirection.TRANSFORM_DIR_INVERSE
        ),
        PyOpenColorIO.FileTransform(
            src="AgX_Default_Contrast.spi1d"
        ),
        PyOpenColorIO.ExponentTransform(
            value=[2.2, 2.2, 2.2, 1.0],
            direction=PyOpenColorIO.TransformDirection.TRANSFORM_DIR_FORWARD
        )
    ]

    config, look = AgX.add_look(
        config=config,
        name="Look Base",
        description="Base image look.",
        processspace="Linear BT.709 Closed Domain",
        transforms=transform_list
    )

    # # TODO: Move all of this away.
    config.addDisplayView(
        display="sRGB",
        view="Display Native",
        viewTransform="2.2 EOTF Encoding",
        displayColorSpaceName="Linear BT.709 Closed Domain",
        description="sRGB Encoding"
    )

    config.addDisplayView(
        display="sRGB",
        view="Image",
        viewTransform="Image Log View",
        displayColorSpaceName="sRGB",
        description="Default image view"
    )

    config.addDisplayView(
        display="sRGB",
        view="Image Look",
        viewTransform="Identity View",
        displayColorSpaceName="sRGB",
        looks="Look Base",
        description="Default image view"
    )

    # config.addDisplayView(
    #     display="sRGB",
    #     view="AgX",
    #     viewTransform="AgX Log View",
    #     displayColorSpaceName="sRGB",
    #     looks="Look AgX Base",
    #     description="AgX Base Image Encoding for sRGB displays"
    # )

    # ####
    # # Data
    # ####

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
    limits_contrast = [3.0, 3.25]
    general_contrast = 2.0
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