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

if __name__ == "__main__":
    config = PyOpenColorIO.Config()
    config.setMinorVersion(0)

    config.setSearchPath(":".join(LUT_search_paths))

    transforms = {}
    colorspaces = {}
    inactive_colourspaces = []
    views = {}

    ####
    # Utilities
    ####

    # PyOpenColorIO.NamedTransform,
    #   name: str = ‘’,
    #   aliases: List[str] = [],
    #   family: str = ‘’,
    #   description: str = ‘’,
    #   forwardTransform: PyOpenColorIO.Transform = None,
    #   inverseTransform: PyOpenColorIO.Transform = None,
    #   categories: List[str] = []) -> None

    # Define a generic 2.2 Electro Optical Transfer Function
    named_transform = PyOpenColorIO.NamedTransform(
        name="2.2 EOTF Encoding",
        aliases=["sRGB EOTF Encoding"],
        family="Utilities/Curves",
        description="2.2 Exponent Inverse EOTF Encoding",
        forwardTransform=PyOpenColorIO.ExponentTransform(
            value=[2.2, 2.2, 2.2, 1.0],
            direction=PyOpenColorIO.TransformDirection.TRANSFORM_DIR_INVERSE
        )
    )
    config.addNamedTransform(named_transform)
    transforms.update({"2.2 EOTF Encoding": named_transform})

    # PyOpenColorIO.BuiltinTransform,
    #   style: str = ‘IDENTITY’,
    #   direction: PyOpenColorIO.TransformDirection =
    #       <TransformDirection.TRANSFORM_DIR_FORWARD
    # To list all BuiltinTransforms, use
    #   print(dict(ocio.BuiltinTransformRegistry().getBuiltins()).keys())
    named_transform = PyOpenColorIO.NamedTransform(
        name="Identity Transform",
        aliases=["No Operation Transform"],
        family="Utilities",
        description="No Operation Transform",
        forwardTransform=PyOpenColorIO.BuiltinTransform()
    )
    config.addNamedTransform(named_transform)
    transforms.update({"Identity": named_transform})

    ####
    # Colourspaces
    ####

    # PyOpenColorIO.ColorSpace,
    #   referenceSpace: PyOpenColorIO.ReferenceSpaceType =
    #       <ReferenceSpaceType.REFERENCE_SPACE_SCENE: 0>,
    #   name: str = ‘’,
    #   aliases: List[str] = [],
    #   family: str = ‘’,
    #   encoding: str = ‘’,
    #   equalityGroup: str = ‘’,
    #   description: str = ‘’,
    #   bitDepth: PyOpenColorIO.BitDepth = <BitDepth.BIT_DEPTH_UNKNOWN: 0>,
    #   isData: bool = False,
    #   allocation: PyOpenColorIO.Allocation = <Allocation.ALLOCATION_UNIFORM: 1>,
    #   allocationVars: List[float] = [],
    #   toReference: PyOpenColorIO.Transform = None,
    #   fromReference: PyOpenColorIO.Transform = None,
    #   categories: List[str]

    # Define a generic tristimulus linear working space, with assumed
    # BT.709 primaries and a D65 achromatic point.
    colorspace = PyOpenColorIO.ColorSpace(
        name="Linear BT.709",
        aliases=["Linear", "Linear Open Domain", "Linear Tristimulus Open Domain"],
        family="Colourspaces",
        description="Open Domain Linear BT.709 Tristimulus"
    )
    config.addColorSpace(colorspace)
    colorspaces.update({"Linear BT.709": colorspace})

    # Shared views require a REFERENCE_SPACE_DISPLAY defined colourspace, so we
    # will define one as above, and make it inactive to avoid confusing folks.
    colorspace = PyOpenColorIO.ColorSpace(
        referenceSpace=
            PyOpenColorIO.ReferenceSpaceType.REFERENCE_SPACE_DISPLAY,
        name="Linear BT.709 Closed Domain",
        aliases=["Linear Closed Domain", "Linear Tristimulus Closed Domain"],
        family="Colourspaces",
        description="Closed Domain Linear BT.709 Tristimulus"
    )
    config.addColorSpace(colorspace)
    colorspaces.update({"Linear BT.709 Closed Domain": colorspace})
    inactive_colourspaces.append("Linear BT.709 Closed Domain")

    ####
    # Views
    ####

    # PyOpenColorIO.ViewTransform,
    #   referenceSpace: PyOpenColorIO.ReferenceSpaceType =
    #       <ReferenceSpaceType.REFERENCE_SPACE_SCENE: 0>,
    #   name: str = ‘’, family: str = ‘’,
    #   description: str = ‘’,
    #   toReference: PyOpenColorIO.Transform = None,
    #   fromReference: PyOpenColorIO.Transform = None,
    #   categories: List[str] = []

    # PyOpenColorIO.Config.addSharedView
    #   view: str,
    #   viewTransformName: str,
    #   colorSpaceName: str,
    #   looks: str = '',
    #   ruleName: str = '',
    #   description: str = ''
    # May use PyOpenColorIO.OCIO_VIEW_USE_DISPLAY_NAME for colorSpaceName

    # PyOpenColorIO.Config.addDisplaySharedView
    #   display: str,
    #   view: str
    # The shared view must be part of the config. See Config::addSharedView above.

    # First view transform is used as the bridging interchange between
    # "scene" and "display". Fuck OpenColorIO V2 has falled down the idiot
    # ACES hole.
    view_transform = PyOpenColorIO.ViewTransform(
        name="No Operation View",
        description="Default No Operation View Transform",
        fromReference=PyOpenColorIO.BuiltinTransform()
    )

    config.addViewTransform(view_transform)
    views.update({"No Operation View": view_transform})

    # Define the specification sRGB Display colourspace
    # view_transform = PyOpenColorIO.ViewTransform(
    #     name="sRGB Display View",
    #     description="IEC 61966-2-1:1999 Reference sRGB Display",
    #     fromReference=transforms.get("2.2 EOTF Encoding")
    # )
    # config.addViewTransform(view_transform)
    # views.update({"sRGB Display View": view_transform})

    config.addSharedView(
      view="No Encoding",
      viewTransformName="No Operation View",
      colorSpaceName="Linear BT.709 Closed Domain",
      description="No Encoding Operation View"
    )

    config.addDisplaySharedView(
        display="sRGB",
        view="No Encoding"
    )

    ####
    # Display Colourspaces
    ####

    # Sadly have to define one for the roles.
    colorspace = PyOpenColorIO.ColorSpace(
        referenceSpace=
            PyOpenColorIO.ReferenceSpaceType.REFERENCE_SPACE_DISPLAY,
        name="sRGB Display",
        family="Displays",
        description="IEC 61966-2-1:1999 Reference sRGB Display"
    )
    config.addColorSpace(colorspace)
    colorspaces.update({"sRGB Display": colorspace})
    inactive_colourspaces.append("sRGB Display")

    ####
    # Data
    ####

    # Define a generic data colorspace.
    colorspace = PyOpenColorIO.ColorSpace(
        name="Generic Data",
        aliases=["Non-Color", "Raw"],
        family="Data",
        description="Generic Data Encoding",
        isData=True
    )
    config.addColorSpace(colorspace)
    colorspaces.update({"Generic Data": colorspace})

    ####
    # Config Generation
    ####

    default_closed_domain = "sRGB Display"
    default_open_domain = "Linear BT.709"
    default_closed_open_domain = "sRGB Display"
    default_data = "Generic Data"
    default_log = "sRGB Display"

    roles = {
        # "cie_xyz_d65_interchange":,
        "color_picking": default_closed_domain,
        "color_timing": default_log,
        "compositing_log": default_log,
        "data": default_data,
        "default": default_closed_domain,
        "default_byte": default_closed_domain,
        "default_float": default_open_domain,
        "default_sequencer": default_closed_domain,
        "matte_paint": default_closed_open_domain,
        "reference": default_open_domain,
        "scene_linear": default_open_domain,
        "texture_paint": default_closed_domain
    }

    for role, transform in roles.items():
        config.setRole(role, transform)

    delineator = ", "
    inactive_colourspaces_string = delineator.join(inactive_colourspaces)
    config.setInactiveColorSpaces(inactive_colourspaces_string)

    try:
        config.validate()

        output_directory = pathlib.Path(output_config_directory)
        output_directory.mkdir(parents=True, exist_ok=True)
        output_file = output_directory / output_config_name

        write_file = open(output_file, "w")
        write_file.write(config.serialize())
        write_file.close()
        print("Successfully wrote config \"{}\"".format(output_config_name))
    except Exception as ex:
        raise ex
