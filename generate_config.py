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

AgX_version = 0.1
AgX_name = "Kraken"

AgX_min_EV = -10.0
AgX_max_EV = +6.5
AgX_x_pivot = numpy.abs(AgX_min_EV / (AgX_max_EV - AgX_min_EV))
AgX_image_middle_grey = 0.18
AgX_y_pivot = 0.50
AgX_image_linear_exponent = numpy.log(AgX_image_middle_grey) / \
    numpy.log(numpy.abs(AgX_min_EV / (AgX_max_EV - AgX_min_EV)))

inactive_colourspaces = []

if __name__ == "__main__":
    config = PyOpenColorIO.Config()
    config.setMinorVersion(0)

    config.setSearchPath(":".join(LUT_search_paths))

    ####
    # Colourspaces
    ####

    # Define a generic tristimulus linear working space, with assumed
    # BT.709 primaries and a D65 achromatic point.
    config, colourspace = AgX.add_colourspace(
        config=config,
        family="Colourimetry",
        name="Linear BT.709",
        description="Open Domain Linear BT.709 Tristimulus",
        aliases=["Linear", "Linear Tristimulus"]
    )

    config, colourspace = AgX.add_colourspace(
        config=config,
        family="Colourimetry",
        name="Linear BT.709 Closed Domain",
        description="Closed Domain Linear BT.709 Tristimulus",
        aliases=["Linear Closed Domain", "Linear Closed Domain Tristimulus"],
        referencespace=PyOpenColorIO.ReferenceSpaceType.REFERENCE_SPACE_DISPLAY
    )

    # Display P3 Colourimetry
    Display_P3_Colourspace = colour.RGB_COLOURSPACES["Display P3"]
    sRGB_Colourspace = colour.RGB_COLOURSPACES["sRGB"]
    D_P3_RGB_to_sRGB_matrix = colour.matrix_RGB_to_RGB(
        sRGB_Colourspace, Display_P3_Colourspace
    )

    transform_list = [
        PyOpenColorIO.MatrixTransform(AgX.shape_OCIO_matrix(D_P3_RGB_to_sRGB_matrix))
    ]

    config, colourspace = AgX.add_colourspace(
        config=config,
        family="Colourimetry",
        name="Linear Display P3",
        description="Open Domain Linear Display P3 Tristimulus",
        aliases=["Linear Display P3", "Linear Display P3 Tristimulus"],
        transforms=transform_list
    )

    config, colourspace = AgX.add_colourspace(
        config=config,
        family="Colourimetry",
        name="Linear Display P3 Closed Domain",
        description="Closed Domain Linear Display P3 Tristimulus",
        aliases=[
            "Linear Closed Domain Display P3",
            "Linear Closed Domain Display P3 Tristimulus"
        ],
        transforms=transform_list,
        referencespace=PyOpenColorIO.ReferenceSpaceType.REFERENCE_SPACE_DISPLAY
    )

    # Define the core AgX Log based encoding.
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
        name="AgX Log ({}-{})".format(AgX_name, AgX_version),
        description="AgX Log ({}-{})".format(AgX_name, AgX_version),
        aliases=["Log", "AgX Log", "{}".format(AgX_name)],
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
    # Displays and Technical Transforms
    ####

    # Define the specification sRGB Display colourspace
    transform_list = [
        PyOpenColorIO.ColorSpaceTransform(
            src="Linear BT.709",
            dst="2.2 EOTF Encoding"
        )
    ]

    # Display - sRGB.
    config, colourspace = AgX.add_colourspace(
        config=config,
        family="Displays/SDR",
        name="Display - sRGB",
        description="sRGB IEC 61966-2-1 2.2 Exponent Reference EOTF Display",
        transforms=transform_list,
        referencespace=PyOpenColorIO.ReferenceSpaceType.REFERENCE_SPACE_DISPLAY
    )

    # # Display - Display P3.
    # Display_P3_Colourspace = colour.RGB_COLOURSPACES["Display P3"]
    # sRGB_Colourspace = colour.RGB_COLOURSPACES["sRGB"]
    # D_P3_RGB_to_sRGB_matrix = colour.matrix_RGB_to_RGB(
    #     sRGB_Colourspace, Display_P3_Colourspace
    # )

    # transform_list = [
    #     PyOpenColorIO.MatrixTransform(AgX.shape_OCIO_matrix(D_P3_RGB_to_sRGB_matrix)),
    #     PyOpenColorIO.ColorSpaceTransform(
    #         src="Linear BT.709",
    #         dst="2.2 EOTF Encoding"
    #     )
    # ]

    # config, colourspace = AgX.add_colourspace(
    #     config=config,
    #     family="Displays/SDR",
    #     name="Display - Display P3",
    #     description="Display P3 2.2 Exponent EOTF Display",
    #     transforms=transform_list,
    #     referencespace=PyOpenColorIO.ReferenceSpaceType.REFERENCE_SPACE_DISPLAY
    # )

    # # Display - BT.1886.
    # transform_list = [
    #     PyOpenColorIO.ColorSpaceTransform(
    #         src="Linear BT.709",
    #         dst="2.4 EOTF Encoding"
    #     )
    # ]

    # config, colourspace = AgX.add_colourspace(
    #     config=config,
    #     family="Displays/SDR",
    #     name="Display - BT.1886",
    #     description="BT.1886 2.4 Exponent EOTF Display",
    #     transforms=transform_list,
    #     referencespace=PyOpenColorIO.ReferenceSpaceType.REFERENCE_SPACE_DISPLAY
    # )

    ####
    # Imagery
    ####

    # sRGB Imagery
    # TODO: Properly conform to the specification for the two part OETF.
    transform_list = [
        PyOpenColorIO.ColorSpaceTransform(
            src="Linear BT.709",
            dst="2.2 EOTF Encoding"
        )
    ]
    config, colourspace = AgX.add_colourspace(
        config=config,
        family="Imagery",
        name="Image - sRGB",
        description="sRGB IEC 61966-2-1 2.2 Reference Image Encoding",
        aliases=["sRGB"],
        transforms=transform_list,
        referencespace=PyOpenColorIO.ReferenceSpaceType.REFERENCE_SPACE_DISPLAY
    )

    # AgX Flat Imagery
    # We need a basis for the core image, so we will define the base log
    # relative to a flat linear image encoding.
    transform_list = [
        PyOpenColorIO.ExponentTransform(
            value=[
                AgX_image_linear_exponent,
                AgX_image_linear_exponent,
                AgX_image_linear_exponent,
                1.0
            ]
        ),
        PyOpenColorIO.ColorSpaceTransform(
            src="AgX Log",
            dst="Linear BT.709 Closed Domain"
        )
    ]

    config, colourspace = AgX.add_colourspace(
        config=config,
        family="Imagery",
        name="Image - AgX Flat",
        description="Flat AgX image",
        transforms=transform_list,
        direction=PyOpenColorIO.ColorSpaceDirection.COLORSPACE_DIR_TO_REFERENCE,
        referencespace=PyOpenColorIO.ReferenceSpaceType.REFERENCE_SPACE_DISPLAY
    )

    ####
    # Views
    ####

    # The first view in a configuration is used as the bridging transformation
    # for converting between the open domain tristimulus (overloaded term "scene")
    # and the closed domain tristimulus (shoddy term "display").
    transform_list = [
        PyOpenColorIO.BuiltinTransform("IDENTITY")
    ]

    config, view = AgX.add_view(
        config=config,
        family="Views",
        name="Identity View",
        description="No operation identity view",
        transforms=transform_list,
        referencespace=PyOpenColorIO.REFERENCE_SPACE_SCENE
    )
    inactive_colourspaces.append("Identity View")

    transform_list = [
        PyOpenColorIO.ColorSpaceTransform(
            src="Linear BT.709 Closed Domain",
            dst="2.2 EOTF Encoding"
        )
    ]

    config, view = AgX.add_view(
        config=config,
        family="Views",
        name="2.2 EOTF Encoding",
        description="2.2 EOTF Encoding",
        transforms=transform_list,
        referencespace=PyOpenColorIO.REFERENCE_SPACE_DISPLAY
    )

    ####
    # Display Views
    ####

    config.addDisplayView(
        display="sRGB",
        view="Inverse EOTF Encoding",
        viewTransform="2.2 EOTF Encoding",
        displayColorSpaceName="Linear BT.709 Closed Domain",
        description="sRGB IEC 61966-2-1 2.2 Exponent Reference EOTF Display"
    )

    config.addDisplayView(
        display="Display P3",
        view="Inverse EOTF Encoding",
        viewTransform="2.2 EOTF Encoding",
        displayColorSpaceName="Linear Display P3 Closed Domain",
        description="Display P3 2.2 Exponent EOTF Display"
    )
    # # Add AgX Kraken aesthetic image base.
    # transform_list = [
    #     PyOpenColorIO.ColorSpaceTransform(
    #         src="Linear BT.709",
    #         dst="AgX Log"
    #     )
    # ]

    # config, colourspace = AgX.add_colourspace(
    #     config=config,
    #     family="Imagery",
    #     name="AgX Base",
    #     description="AgX Base Image Encoding",
    #     transforms=transform_list,
    #     referencespace=PyOpenColorIO.ReferenceSpaceType.REFERENCE_SPACE_SCENE
    # )

    # # Add BT.1886 AgX Kraken aesthetic image base.
    # transform_list = [
    #     PyOpenColorIO.ColorSpaceTransform(
    #         src="Linear BT.709",
    #         dst="AgX Base"
    #     ),
    #     PyOpenColorIO.ColorSpaceTransform(
    #         src="2.2 EOTF Encoding",
    #         dst="2.4 EOTF Encoding"
    #     )
    # ]

    # config, colourspace = AgX.add_colourspace(
    #     config=config,
    #     family="Views/AgX BT.1886",
    #     name="AgX Base BT.1886",
    #     description="AgX Base Image Encoding for BT.1886 Displays",
    #     transforms=transform_list,
    #     referencespace=PyOpenColorIO.ReferenceSpaceType.REFERENCE_SPACE_SCENE
    # )

    # # Add Display P3 AgX Kraken aesthetic image base.
    # transform_list = [
    #     PyOpenColorIO.ColorSpaceTransform(
    #         src="Linear BT.709",
    #         dst="AgX Base"
    #     ),
    #     PyOpenColorIO.ColorSpaceTransform(
    #         src="2.2 EOTF Encoding",
    #         dst="Display P3"
    #     )
    # ]

    # config, colourspace = AgX.add_colourspace(
    #     config=config,
    #     family="Views/AgX Display P3",
    #     name="AgX Base Display P3",
    #     description="AgX Base Image Encoding for Display P3 Displays",
    #     transforms=transform_list,
    #     referencespace=PyOpenColorIO.ReferenceSpaceType.REFERENCE_SPACE_SCENE
    # )

    ####
    # Appearances / Looks
    ####

    # Add a heavily tinted washed look.
    # Golden Kraken
    # transform_list = [
    #     PyOpenColorIO.CDLTransform(
    #         slope=[1.0, 0.9, 0.5],
    #         power=[0.8, 0.8, 0.8],
    #         sat=1.3
    #     )
    # ]

    # config, look = AgX.add_look(
    #     config=config,
    #     name="Golden",
    #     description="A golden tinted, slightly washed look",
    #     transforms=transform_list
    # )

    # # Add a crunchier and more saturated look.
    # # Punchy Kraken
    # transform_list = [
    #     PyOpenColorIO.CDLTransform(
    #         slope=[1.0, 1.0, 1.0],
    #         power=[1.35, 1.35, 1.35],
    #         sat=1.4
    #     )
    # ]

    # config, colourspace = AgX.add_look(
    #     config=config,
    #     name="Punchy",
    #     description="A punchy and more chroma laden look",
    #     transforms=transform_list
    # )

    # # Add Golden for all displays.
    # # sRGB
    # transform_list = [
    #     PyOpenColorIO.LookTransform(
    #         src="Linear BT.709",
    #         dst="AgX Base",
    #         looks="Golden"
    #     )
    # ]

    # config, colourspace = AgX.add_colourspace(
    #     config=config,
    #     family="Appearances/Golden",
    #     name="Appearance Golden sRGB",
    #     description="A golden tinted, slightly washed look for sRGB displays",
    #     transforms=transform_list
    # )

    # AgX.append_view(
    #     displays, "sRGB", "Appearance Golden", "Appearance Golden sRGB"
    # )

    # # Display P3
    # transform_list = [
    #     PyOpenColorIO.LookTransform(
    #         src="Linear BT.709",
    #         dst="AgX Base",
    #         looks="Golden"
    #     ),
    #     PyOpenColorIO.ColorSpaceTransform(
    #         src="2.2 EOTF Encoding",
    #         dst="Display P3"
    #     )
    # ]

    # config, colourspace = AgX.add_colourspace(
    #     config=config,
    #     family="Appearances/Golden",
    #     name="Appearance Golden Display P3",
    #     description="A golden tinted, slightly washed look for Display P3 displays",
    #     transforms=transform_list
    # )

    # AgX.append_view(
    #     displays, "Display P3", "Appearance Golden", "Appearance Golden Display P3"
    # )

    # # Display BT.1886
    # transform_list = [
    #     PyOpenColorIO.LookTransform(
    #         src="Linear BT.709",
    #         dst="AgX Base",
    #         looks="Golden"
    #     ),
    #     PyOpenColorIO.ColorSpaceTransform(
    #         src="2.2 EOTF Encoding",
    #         dst="2.4 EOTF Encoding"
    #     )
    # ]

    # config, colourspace = AgX.add_colourspace(
    #     config=config,
    #     family="Appearances/Golden",
    #     name="Appearance Golden BT.1886",
    #     description="A golden tinted, slightly washed look for BT.1886 displays",
    #     transforms=transform_list
    # )

    # AgX.append_view(
    #     displays, "BT.1886", "Appearance Golden", "Appearance Golden BT.1886"
    # )

    # # Add Punchy for all displays.
    # # sRGB
    # transform_list = [
    #     PyOpenColorIO.LookTransform(
    #         src="Linear BT.709",
    #         dst="AgX Base",
    #         looks="Punchy"
    #     )
    # ]

    # config, colourspace = AgX.add_colourspace(
    #     config=config,
    #     family="Appearances/Punchy",
    #     name="Appearance Punchy sRGB",
    #     description="A punchy and more chroma laden look for sRGB displays",
    #     transforms=transform_list
    # )

    # AgX.append_view(
    #     displays, "sRGB", "Appearance Punchy", "Appearance Punchy sRGB"
    # )

    # # Display P3
    # transform_list = [
    #     PyOpenColorIO.LookTransform(
    #         src="Linear BT.709",
    #         dst="AgX Base",
    #         looks="Punchy"
    #     ),
    #     PyOpenColorIO.ColorSpaceTransform(
    #         src="2.2 EOTF Encoding",
    #         dst="Display P3"
    #     )
    # ]

    # config, colourspace = AgX.add_colourspace(
    #     config=config,
    #     family="Appearances/Punchy",
    #     name="Appearance Punchy Display P3",
    #     description="A punchy and more chroma laden look for Display P3 displays",
    #     transforms=transform_list
    # )

    # AgX.append_view(
    #     displays, "Display P3", "Appearance Punchy", "Appearance Punchy Display P3"
    # )

    # # Display BT.1886
    # transform_list = [
    #     PyOpenColorIO.LookTransform(
    #         src="Linear BT.709",
    #         dst="AgX Base",
    #         looks="Punchy"
    #     ),
    #     PyOpenColorIO.ColorSpaceTransform(
    #         src="2.2 EOTF Encoding",
    #         dst="2.4 EOTF Encoding"
    #     )
    # ]

    # config, colourspace = AgX.add_colourspace(
    #     config=config,
    #     family="Appearances/Punchy",
    #     name="Appearance Punchy BT.1886",
    #     description="A punchy and more chroma laden look for BT.1886 displays",
    #     transforms=transform_list
    # )

    # AgX.append_view(
    #     displays, "BT.1886", "Appearance Punchy", "Appearance Punchy BT.1886"
    # )

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
        "color_picking": "Display - sRGB",
        "color_timing": "Display - sRGB",
        "compositing_log": "Display - sRGB",
        "data": "Generic Data",
        "default": "Display - sRGB",
        "default_byte": "Display - sRGB",
        "default_float": "Linear BT.709",
        "default_sequencer": "Display - sRGB",
        "matte_paint": "Display - sRGB",
        "reference": "Linear BT.709",
        "scene_linear": "Linear BT.709",
        "texture_paint": "Display - sRGB"
    }

    for role, transform in roles.items():
        config.setRole(role, transform)

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
