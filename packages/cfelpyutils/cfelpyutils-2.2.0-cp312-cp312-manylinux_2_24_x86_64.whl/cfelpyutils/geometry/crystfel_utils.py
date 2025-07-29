# This file is part of CFELPyUtils.
#
# CFELPyUtils is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
#
# CFELPyUtils is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with CFELPyUtils.
# If not, see <http://www.gnu.org/licenses/>.
#
# Copyright 2014-2021 Deutsches Elektronen-Synchrotron DESY,
# a research centre of the Helmholtz Association.
# pylint: disable=too-many-lines
"""
This module contains Python re-implementations of some functions from the `CrystFEL
<http://www.desy.de/~twhite/crystfel>`__ software package.
"""

import collections
import copy
import math
import re
import sys
from typing import Dict, List, NamedTuple, Tuple, Union
from io import StringIO, TextIOWrapper
from os import PathLike

from mypy_extensions import TypedDict

TypeBeam = TypedDict(  # pylint: disable=invalid-name
    "TypeBeam",
    {
        "photon_energy": float,
        "photon_energy_from": str,
        "photon_energy_scale": float,
    },
    total=True,
)


TypePanel = TypedDict(  # pylint: disable=invalid-name
    "TypePanel",
    {
        "cnx": float,
        "cny": float,
        "coffset": float,
        "clen": float,
        "clen_from": str,
        "mask": str,
        "mask_file": str,
        'mask0_data': str,
        'mask1_data': str,
        'mask2_data': str,
        'mask3_data': str,
        'mask4_data': str,
        'mask5_data': str,
        'mask6_data': str,
        'mask7_data': str,
        'mask0_file': str,
        'mask1_file': str,
        'mask2_file': str,
        'mask3_file': str,
        'mask4_file': str,
        'mask5_file': str,
        'mask6_file': str,
        'mask7_file': str,
        'mask0_goodbits': int,
        'mask1_goodbits': int,
        'mask2_goodbits': int,
        'mask3_goodbits': int,
        'mask4_goodbits': int,
        'mask5_goodbits': int,
        'mask6_goodbits': int,
        'mask7_goodbits': int,
        'mask0_badbits': int,
        'mask1_badbits': int,
        'mask2_badbits': int,
        'mask3_badbits': int,
        'mask4_badbits': int,
        'mask5_badbits': int,
        'mask6_badbits': int,
        'mask7_badbits': int,
        "satmap": str,
        "satmap_file": str,
        "res": float,
        "badrow": str,
        "no_index": bool,
        "adu_per_photon": float,
        "max_adu": float,
        "data": str,
        "adu_per_eV": float,
        "dim_structure": List[Union[int, str, None]],
        "fsx": float,
        "fsy": float,
        "fsz": float,
        "ssx": float,
        "ssy": float,
        "ssz": float,
        "rail_x": float,
        "rail_y": float,
        "rail_z": float,
        "clen_for_centering": float,
        "xfs": float,
        "yfs": float,
        "xss": float,
        "yss": float,
        "orig_min_fs": int,
        "orig_max_fs": int,
        "orig_min_ss": int,
        "orig_max_ss": int,
        "w": int,
        "h": int,
    },
    total=True,
)

TypeBadRegion = TypedDict(  # pylint: disable=invalid-name
    "TypeBadRegion",
    {
        "panel": str,
        "min_x": float,
        "max_x": float,
        "min_y": float,
        "max_y": float,
        "min_fs": int,
        "max_fs": int,
        "min_ss": int,
        "max_ss": int,
        "is_fsss": int,
    },
    total=True,
)

TypeDetector = TypedDict(  # pylint: disable=invalid-name
    "TypeDetector",
    {
        "panels": Dict[str, TypePanel],
        "bad": Dict[str, TypeBadRegion],
        "mask_good": int,
        "mask_bad": int,
        "rigid_groups": Dict[str, List[str]],
        "rigid_group_collections": Dict[str, List[str]],
        "furthest_out_panel": str,
        "furthest_out_fs": float,
        "furthest_out_ss": float,
        "furthest_in_panel": str,
        "furthest_in_fs": float,
        "furthest_in_ss": float,
    },
    total=True,
)


class CrystFELGeometry(NamedTuple):
    """Collection of objects as returned by load_crystfel_geometry"""

    detector: TypeDetector
    beam: TypeBeam
    hdf5_peak_path: Union[str, None]


def _assplode_algebraic(value):
    # type: (str) -> List[str]
    # Re-implementation of assplode_algegraic from libcrystfel/src/detector.c.
    items = [
        item for item in re.split("([+-])", string=value.strip()) if item != ""
    ]  # type: List[str]
    if items and items[0] not in ("+", "-"):
        items.insert(0, "+")
    return ["".join((items[x], items[x + 1])) for x in range(0, len(items), 2)]


def _dir_conv(direction_x, direction_y, direction_z, value):
    # type: (float, float, float, str) -> List[float]
    # Re-implementation of dir_conv from libcrystfel/src/detector.c.
    direction = [
        direction_x,
        direction_y,
        direction_z,
    ]  # type: List[float]
    items = _assplode_algebraic(value)
    if not items:
        raise RuntimeError("Invalid direction: {}.".format(value))
    for item in items:
        axis = item[-1]  # type: str
        if axis not in ("x", "y", "z"):
            raise RuntimeError("Invalid Symbol: {} (must be x, y or z).".format(axis))
        if item[:-1] == "+":
            value = "1.0"
        elif item[:-1] == "-":
            value = "-1.0"
        else:
            value = item[:-1]
        if axis == "x":
            direction[0] = float(value)
        elif axis == "y":
            direction[1] = float(value)
        elif axis == "z":
            direction[2] = float(value)

    return direction

def _bits_to_int(value: str) -> int:
    """Convert mask bits to integer."""
    try:
        value_int = int(value)
    except ValueError:
        value_int = int(value, base=16)
    return value_int

def _set_dim_structure_entry(key, value, panel):
    # type: (str, str, TypePanel) -> None
    # Re-implementation of set_dim_structure_entry from libcrystfel/src/events.c.
    if panel["dim_structure"] is not None:
        dim = panel["dim_structure"]  # type: List[Union[int, str, None]]
    else:
        dim = []
    try:
        dim_index = int(key[3])  # type: int
    except IndexError:
        raise RuntimeError("'dim' must be followed by a number, e.g. 'dim0')")
    except ValueError:
        raise RuntimeError("Invalid dimension number {}".format(key[3]))
    if dim_index > len(dim) - 1:
        for _ in range(len(dim), dim_index + 1):
            dim.append(None)
    if value in ("ss", "fs", "%"):
        dim[dim_index] = value
    elif value.isdigit():
        dim[dim_index] = int(value)
    else:
        raise RuntimeError("Invalid dim entry: {}.".format(value))
    panel["dim_structure"] = dim


def _parse_field_for_panel(  # pylint: disable=too-many-branches, too-many-statements
    key,  # type: str
    value,  # type: str
    panel,  # type: TypePanel
    panel_name,  # type: str
    detector,  # type: TypeDetector
):
    # type: (...) -> None
    # Re-implementation of parse_field_for_panel from libcrystfel/src/detector.c.
    if key == "min_fs":
        panel["orig_min_fs"] = int(value)
    elif key == "max_fs":
        panel["orig_max_fs"] = int(value)
    elif key == "min_ss":
        panel["orig_min_ss"] = int(value)
    elif key == "max_ss":
        panel["orig_max_ss"] = int(value)
    elif key == "corner_x":
        panel["cnx"] = float(value)
    elif key == "corner_y":
        panel["cny"] = float(value)
    elif key == "rail_direction":
        try:
            panel["rail_x"], panel["rail_y"], panel["rail_z"] = _dir_conv(
                direction_x=panel["rail_x"],
                direction_y=panel["rail_y"],
                direction_z=panel["rail_z"],
                value=value,
            )
        except RuntimeError as exc:
            raise RuntimeError("Invalid rail direction. ", exc)
    elif key == "clen_for_centering":
        panel["clen_for_centering"] = float(value)
    elif key == "adu_per_eV":
        panel["adu_per_eV"] = float(value)
    elif key == "adu_per_photon":
        panel["adu_per_photon"] = float(value)
    elif key == "rigid_group":
        if value in detector["rigid_groups"]:
            if panel_name not in detector["rigid_groups"][value]:
                detector["rigid_groups"][value].append(panel_name)
        else:
            detector["rigid_groups"][value] = [
                panel_name,
            ]
    elif key == "clen":
        try:
            panel["clen"] = float(value)
            panel["clen_from"] = ""
        except ValueError:
            panel["clen"] = -1
            panel["clen_from"] = value
    elif key == "data":
        if not value.startswith("/"):
            raise RuntimeError("Invalid data location: {}".format(value))
        panel["data"] = value
    elif key == "mask":
        if not value.startswith("/"):
            raise RuntimeError("Invalid data location: {}".format(value))
        panel["mask"] = value
    elif key == "mask_file":
        panel["mask_file"] = value
    elif key == "mask0_data":
        panel["mask0_data"] = value
    elif key == "mask1_data":
        panel["mask1_data"] = value
    elif key == "mask2_data":
        panel["mask2_data"] = value
    elif key == "mask3_data":
        panel["mask3_data"] = value
    elif key == "mask4_data":
        panel["mask4_data"] = value
    elif key == "mask5_data":
        panel["mask5_data"] = value
    elif key == "mask6_data":
        panel["mask6_data"] = value
    elif key == "mask7_data":
        panel["mask7_data"] = value
    elif key == "mask0_file":
        panel["mask0_file"] = value
    elif key == "mask1_file":
        panel["mask1_file"] = value
    elif key == "mask2_file":
        panel["mask2_file"] = value
    elif key == "mask3_file":
        panel["mask3_file"] = value
    elif key == "mask4_file":
        panel["mask4_file"] = value
    elif key == "mask5_file":
        panel["mask5_file"] = value
    elif key == "mask6_file":
        panel["mask6_file"] = value
    elif key == "mask7_file":
        panel["mask7_file"] = value
    elif key == "mask0_goodbits":
        panel["mask0_goodbits"] = _bits_to_int(value)
    elif key == "mask1_goodbits":
        panel["mask1_goodbits"] = _bits_to_int(value)
    elif key == "mask2_goodbits":
        panel["mask2_goodbits"] = _bits_to_int(value)
    elif key == "mask3_goodbits":
        panel["mask3_goodbits"] = _bits_to_int(value)
    elif key == "mask4_goodbits":
        panel["mask4_goodbits"] = _bits_to_int(value)
    elif key == "mask5_goodbits":
        panel["mask5_goodbits"] = _bits_to_int(value)
    elif key == "mask6_goodbits":
        panel["mask6_goodbits"] = _bits_to_int(value)
    elif key == "mask7_goodbits":
        panel["mask7_goodbits"] = _bits_to_int(value)
    elif key == "mask0_badbits":
        panel["mask0_badbits"] = _bits_to_int(value)
    elif key == "mask1_badbits":
        panel["mask1_badbits"] = _bits_to_int(value)
    elif key == "mask2_badbits":
        panel["mask2_badbits"] = _bits_to_int(value)
    elif key == "mask3_badbits":
        panel["mask3_badbits"] = _bits_to_int(value)
    elif key == "mask4_badbits":
        panel["mask4_badbits"] = _bits_to_int(value)
    elif key == "mask5_badbits":
        panel["mask5_badbits"] = _bits_to_int(value)
    elif key == "mask6_badbits":
        panel["mask6_badbits"] = _bits_to_int(value)
    elif key == "mask7_badbits":
        panel["mask7_badbits"] = _bits_to_int(value)
    elif key == "saturation_map":
        panel["satmap"] = value
    elif key == "saturation_map_file":
        panel["satmap_file"] = value
    elif key == "coffset":
        panel["coffset"] = float(value)
    elif key == "res":
        panel["res"] = float(value)
    elif key == "max_adu":
        panel["max_adu"] = float(value)
    elif key == "badrow_direction":
        if value == "x":
            panel["badrow"] = "f"
        elif value == "y":
            panel["badrow"] = "s"
        elif value == "f":
            panel["badrow"] = "f"
        elif value == "s":
            panel["badrow"] = "s"
        elif value == "-":
            panel["badrow"] = "-"
        else:
            print("badrow_direction must be x, t, f, s, or '-'")
            print("Assuming '-'.")
            panel["badrow"] = "-"
    elif key == "no_index":
        panel["no_index"] = bool(value)
    elif key == "fs":
        try:
            panel["fsx"], panel["fsy"], panel["fsz"] = _dir_conv(
                direction_x=panel["fsx"],
                direction_y=panel["fsy"],
                direction_z=panel["fsz"],
                value=value,
            )
        except RuntimeError as exc:
            raise RuntimeError("Invalid fast scan direction.", exc)
    elif key == "ss":
        try:
            panel["ssx"], panel["ssy"], panel["ssz"] = _dir_conv(
                direction_x=panel["ssx"],
                direction_y=panel["ssy"],
                direction_z=panel["ssz"],
                value=value,
            )
        except RuntimeError as exc:
            raise RuntimeError("Invalid slow scan direction.", exc)
    elif key.startswith("dim"):
        _set_dim_structure_entry(key=key, value=value, panel=panel)
    else:
        RuntimeError("Unrecognized field: {}".format(key))


def _parse_toplevel(
    key,  # type: str
    value,  # type: str
    detector,  # type: TypeDetector
    beam,  # type: TypeBeam
    panel,  # type: TypePanel
    hdf5_peak_path,  # type: str
):  # pylint: disable=too-many-branches
    # type: (...) -> str
    # Re-implementation of parse_toplevel from libcrystfel/src/detector.c.
    if key == "mask_bad":
        detector["mask_bad"] = _bits_to_int(value)
    elif key == "mask_good":
        detector["mask_good"] = _bits_to_int(value)
    elif key == "coffset":
        panel["coffset"] = float(value)
    elif key == "photon_energy":
        if value.startswith("/"):
            beam["photon_energy"] = 0.0
            beam["photon_energy_from"] = value
        else:
            beam["photon_energy"] = float(value)
            beam["photon_energy_from"] = ""
    elif key == "photon_energy_scale":
        beam["photon_energy_scale"] = float(value)
    elif key == "peak_info_location":
        hdf5_peak_path = value
    elif key.startswith("rigid_group") and not key.startswith("rigid_group_collection"):
        detector["rigid_groups"][key[12:]] = value.split(",")
    elif key.startswith("rigid_group_collection"):
        detector["rigid_group_collections"][key[23:]] = value.split(",")
    else:
        _parse_field_for_panel(
            key=key, value=value, panel=panel, panel_name="", detector=detector
        )

    return hdf5_peak_path


def _check_bad_fsss(bad_region, is_fsss):
    # type: (TypeBadRegion, int) -> None
    # Re-implementation of check_bad_fsss from libcrystfel/src/detector.c.
    if bad_region["is_fsss"] == 99:
        bad_region["is_fsss"] = is_fsss
        return

    if is_fsss != bad_region["is_fsss"]:
        raise RuntimeError("You can't mix x/y and fs/ss in a bad region")


def _parse_field_bad(key, value, bad):
    # type: (str, str, TypeBadRegion) -> None
    # Re-implementation of parse_field_bad from libcrystfel/src/detector.c.
    if key == "min_x":
        bad["min_x"] = float(value)
        _check_bad_fsss(bad_region=bad, is_fsss=False)
    elif key == "max_x":
        bad["max_x"] = float(value)
        _check_bad_fsss(bad_region=bad, is_fsss=False)
    elif key == "min_y":
        bad["min_y"] = float(value)
        _check_bad_fsss(bad_region=bad, is_fsss=False)
    elif key == "max_y":
        bad["max_y"] = float(value)
        _check_bad_fsss(bad_region=bad, is_fsss=False)
    elif key == "min_fs":
        bad["min_fs"] = int(value)
        _check_bad_fsss(bad_region=bad, is_fsss=True)
    elif key == "max_fs":
        bad["max_fs"] = int(value)
        _check_bad_fsss(bad_region=bad, is_fsss=True)
    elif key == "min_ss":
        bad["min_ss"] = int(value)
        _check_bad_fsss(bad_region=bad, is_fsss=True)
    elif key == "max_ss":
        bad["max_ss"] = int(value)
        _check_bad_fsss(bad_region=bad, is_fsss=True)
    elif key == "panel":
        bad["panel"] = value
    else:
        raise RuntimeError("Unrecognized field: {}".format(key))


def _check_point(  # pylint: disable=too-many-arguments
    panel_name,  # type: str
    panel,  # type: TypePanel
    fs_,  # type: int
    ss_,  # type: int
    min_d,  # type: float
    max_d,  # type: float
    detector,  # type: TypeDetector
):
    # type: (...) -> Tuple[float, float]
    # Re-implementation of check_point from libcrystfel/src/detector.c.
    xs_ = fs_ * panel["fsx"] + ss_ * panel["ssx"]  # type: float
    ys_ = fs_ * panel["fsy"] + ss_ * panel["ssy"]  # type: float
    rx_ = (xs_ + panel["cnx"]) / panel["res"]  # type: float
    ry_ = (ys_ + panel["cny"]) / panel["res"]  # type: float
    dist = math.sqrt(rx_ * rx_ + ry_ * ry_)  # type: float
    if dist > max_d:
        detector["furthest_out_panel"] = panel_name
        detector["furthest_out_fs"] = fs_
        detector["furthest_out_ss"] = ss_
        max_d = dist
    elif dist < min_d:
        detector["furthest_in_panel"] = panel_name
        detector["furthest_in_fs"] = fs_
        detector["furthest_in_ss"] = ss_
        min_d = dist

    return min_d, max_d


def _find_min_max_d(detector):
    # type: (TypeDetector) -> None
    # Re-implementation of find_min_max_d from libcrystfel/src/detector.c.
    min_d = float("inf")  # type: float
    max_d = 0.0  # type: float
    for panel_name, panel in detector["panels"].items():
        min_d, max_d = _check_point(
            panel_name=panel_name,
            panel=panel,
            fs_=0,
            ss_=0,
            min_d=min_d,
            max_d=max_d,
            detector=detector,
        )
        min_d, max_d = _check_point(
            panel_name=panel_name,
            panel=panel,
            fs_=panel["w"],
            ss_=0,
            min_d=min_d,
            max_d=max_d,
            detector=detector,
        )
        min_d, max_d = _check_point(
            panel_name=panel_name,
            panel=panel,
            fs_=0,
            ss_=panel["h"],
            min_d=min_d,
            max_d=max_d,
            detector=detector,
        )
        min_d, max_d = _check_point(
            panel_name=panel_name,
            panel=panel,
            fs_=panel["w"],
            ss_=panel["h"],
            min_d=min_d,
            max_d=max_d,
            detector=detector,
        )


def load_crystfel_geometry(file: Union[str, PathLike, StringIO, TextIOWrapper]) -> CrystFELGeometry:
    """
    Loads a CrystFEL geometry file.

    This function is a re-implementation of the get_detector_geometry_2 function from
    CrystFEL. It reads information from a CrystFEL geometry file, which uses a
    key/value language, fully documented in the relevant
    `man page <http://www.desy.de/~twhite/crystfel/manual-crystfel_geometry.html>`_.
    This function returns objects whose content matches CrystFEL's internal
    representation of the information in the file (see the libcrystfel/src/detector.h
    and the libcrystfel/src/image.c files from CrystFEL's source code for more
    information).

    The code of this function is currently synchronized with the code of the function
    'get_detector_geometry_2' in CrystFEL at commit cff9159b4bc6.


    Arguments:

        file (Union[str, PathLike, StringIO, TextIOWrapper]):
                                     Either the path to a CrystFEL
                                     geometry file, or a text file handler object.

    Returns:

        Tuple[TypeDetector, TypeBeam, Union[str, None]]: a tuple with the information
        loaded from the file.

        The first entry in the tuple is a dictionary storing information strictly
        related to the detector geometry. The following is a brief description of the
        key/value pairs in the dictionary.

        **Detector-related key/pairs**

            **panels** the panels in the detector. The value corresponding to this key
            is a dictionary containing information about the panels that make up the
            detector. In the dictionary, the keys are the panel names, and the values
            are further dictionaries storing information about the panels.

            **bad**: the bad regions in the detector. The value corresponding to this
            key is a dictionary containing information about the bad regions in the
            detector. In the dictionary, the keys are the bad region names, and the
            values are further dictionaries storing information about the bad regions.

            **mask_bad**: the value used in a mask to label a pixel as bad.

            **mask_good**: the value used in a mask to label a pixel as good.

            **rigid_groups**: the rigid groups of panels in the detector. The value
            corresponding to this key is a dictionary containing information about the
            rigid groups in the detector. In the dictionary, the keys are the names
            of the rigid groups and the values are lists storing the names of the
            panels belonging to eachgroup.

            **rigid_groups_collections**: the collections of rigid groups of panels in
            the detector. The value corresponding to this key is a dictionary
            containing information about the rigid group collections in the detector.
            In the dictionary, the keys are the names of the rigid group collections
            and the values are lists storing the names of the rigid groups belonging to
            the collections.

            **furthest_out_panel**: the name of the panel where the furthest away pixel
            from the center of the reference system can be found.

            **furthest_out_fs**: the fs coordinate, within its panel, of the furthest
            away pixel from the center of the reference system.

            **furthest_out_ss**: the ss coordinate, within its panel, of the furthest
            away pixel from the center of the reference system.

            **furthest_in_panel**: the name of the panel where the closest pixel to the
            center of the reference system can be found.

            **furthest_in_fs**: the fs coordinate, within its panel, of the closest
            pixel to the center of the reference system.

            **furthest_in_ss**: the ss coordinate, within its panel, of the closest
            pixel to the center of the reference system.

        **Panel-related key/pairs**

            **cnx**: the x location of the corner of the panel in the reference system.

            **cny**: the y location of the corner of the panel in the reference system.

            **clen**: the distance, as reported by the facility, of the sample
            interaction point from the corner of the first pixel in the panel .

            **clen_from**: the location of the clen information in a data file, in
            case the information must be extracted from it.

            **coffset**: the offset to be applied to the clen value to determine the
            real distance of the panel from the interaction point.

            **mask**: the location of the mask data for the panel in a data file.

            **mask_file**: the data file in which the mask data for the panel can be
            found.

            **satmap**: the location of the per-pixel saturation map for the panel in a
            data file.

            **satmap_file**: the data file in which the per-pixel saturation map for
            the panel can be found.

            **res**: the resolution of the panel in pixels per meter.

            **badrow**: the readout direction for the panel, for filtering out clusters
            of peaks. The value corresponding to this key is either 'x' or 'y'.

            **no_index**: wether the panel should be considered entirely bad. The panel
            will be considered bad if the value corresponding to this key is non-zero.

            **adu_per_photon**: the number of detector intensity units per photon for
            the panel.

            **max_adu**: the detector intensity unit value above which a pixel of the
            panel should be considered unreliable.

            **data**: the location, in a data file, of the data block where the panel
            data is stored.

            **adu_per_eV**: the number of detector intensity units per eV of photon
            energy for the panel.

            **dim_structure**: a description of the structure of the data block for the
            panel. The value corresponding to this key is a list of strings describing
            the meaning of each axis in the data block. See the
            `crystfel_geometry \
            <http://www.desy.de/~twhite/crystfel/manual-crystfel_geometry.html>`__ man
            page for a detailed explanation.

            **fsx**: the fs->x component of the matrix transforming pixel indexes to
            detector reference system coordinates.

            **fsy**: the fs->y component of the matrix transforming pixel indexes to
            detector reference system coordinates.

            **fsz**: the fs->z component of the matrix transforming pixel indexes to
            detector reference system coordinates.

            **ssx**: the ss->x component of the matrix transforming pixel indexes to
            detector reference system coordinates.

            **ssy**: the ss->y component of the matrix transforming pixel indexes to
            detector reference system coordinates.

            **ssz**: the ss->z component of the matrix transforming pixel indexes to
            detector reference system coordinates.

            **rail_x**: the x component, with respect to the reference system, of the
            direction of the rail along which the detector can be moved.

            **rail_y**: the y component, with respect to the reference system, of the
            direction of the rail along which the detector can be moved.

            **rail_z**: the z component, with respect to the reference system, of the
            direction of the rail along which the detector can be moved.

            **clen_for_centering**: the value of clen at which the beam hits the
            detector at the origin of the reference system.

            **xfs**: the x->fs component of the matrix transforming detector reference
            system coordinates to pixel indexes.

            **yfs**: the y->fs component of the matrix transforming detector reference
            system coordinates to pixel indexes.

            **xss**: the x->ss component of the matrix transforming detector reference
            system coordinates to pixel indexes.

            **yss**: the y->ss component of the matrix transforming detector reference
            system coordinates to pixel indexes.

            **orig_min_fs**: the initial fs index of the location of the panel data in
            the data block where it is stored.

            **orig_max_fs**: the final fs index of the location of the panel data in
            the data block where it is stored.

            **orig_min_ss**: the initial ss index of the location of the panel data in
            the data block where it is stored.

            **orig_max_ss**: the final fs index of the location of the panel data in
            the data block where it is stored.

            **w**: the width of the panel in pixels.

            **h**: the width of the panel in pixels.

        **Bad region-related key/value pairs**

            **panel**: the name of the panel in which the bad region lies.

            **min_x**: the initial x coordinate of the bad region in the detector
            reference system.

            **max_x**: the final x coordinate of the bad region in the detector
            referencesystem.

            **min_y**: the initial y coordinate of the bad region in the detector
            reference system.

            **max_y**: the final y coordinate of the bad region in the detector
            reference system.

            **min_fs**: the initial fs index of the location of the bad region in the
            block where the panel data is stored.

            **max_fs**: the final fs index of the location of the bad region in the
            block where the panel data is stored.

            **min_ss**: the initial ss index of the location of the bad region in the
            block where the panel data is stored.

            **max_ss**: the final ss index of the location of the bad region in the
            block where the panel data is stored.

            **is_fsss**: whether the fs,ss definition of the bad region is the valid
            one (as opposed to the x,y-based one). If the value corresponding to this
            key is True, the fs,ss-based definition of the bad region should be
            considered the valid one. Otherwise, the definition in x,y coordinates must
            be honored.

        The second entry in the tuple is a dictionary storing information related to
        the beam properties. The following is a brief description of the key/value
        pairs in the dictionary.

            **photon_energy**: the photon energy of the beam in eV.

            **photon_energy_from**: the location of the photon energy information in a
            data file, in case the information must be extracted from it.

            **photon_energy_scale**: the scaling factor to be applied to the photon
            energy, in case the provided energy value is not in eV.

        The third entry in the tuple is a string storing the HDF5 path where
        information about detected Bragg peaks can be found in a data file. If the
        CrystFEL geometry file does not provide this information, an empty string is
        returned.
    """
    beam = {
        "photon_energy": 0.0,
        "photon_energy_from": "",
        "photon_energy_scale": 1.0,
    }  # type: TypeBeam
    detector = {
        "panels": collections.OrderedDict(),
        "bad": collections.OrderedDict(),
        "mask_good": 0,
        "mask_bad": 0,
        "rigid_groups": {},
        "rigid_group_collections": {},
        "furthest_out_panel": "",
        "furthest_out_fs": float("NaN"),
        "furthest_out_ss": float("NaN"),
        "furthest_in_panel": "",
        "furthest_in_fs": float("NaN"),
        "furthest_in_ss": float("NaN"),
    }  # type: TypeDetector
    default_panel = {
        "cnx": float("NaN"),
        "cny": float("NaN"),
        "coffset": 0.0,
        "clen": float("NaN"),
        "clen_from": "",
        "mask": "",
        "mask_file": "",
        "mask0_data": "",
        "mask1_data": "",
        "mask2_data": "",
        "mask3_data": "",
        "mask4_data": "",
        "mask5_data": "",
        "mask6_data": "",
        "mask7_data": "",
        "mask0_file": "",
        "mask1_file": "",
        "mask2_file": "",
        "mask3_file": "",
        "mask4_file": "",
        "mask5_file": "",
        "mask6_file": "",
        "mask7_file": "",
        "mask0_goodbits": 0,
        "mask1_goodbits": 0,
        "mask2_goodbits": 0,
        "mask3_goodbits": 0,
        "mask4_goodbits": 0,
        "mask5_goodbits": 0,
        "mask6_goodbits": 0,
        "mask7_goodbits": 0,
        "mask0_badbits": 0,
        "mask1_badbits": 0,
        "mask2_badbits": 0,
        "mask3_badbits": 0,
        "mask4_badbits": 0,
        "mask5_badbits": 0,
        "mask6_badbits": 0,
        "mask7_badbits": 0,
        "satmap": "",
        "satmap_file": "",
        "res": -1.0,
        "badrow": "-",
        "no_index": False,
        "adu_per_photon": float("NaN"),
        "max_adu": float("inf"),
        "data": "",
        "adu_per_eV": float("NaN"),
        "dim_structure": [],
        "fsx": 1.0,
        "fsy": 0.0,
        "fsz": 0.0,
        "ssx": 0.0,
        "ssy": 1.0,
        "ssz": 0.0,
        "rail_x": float("NaN"),
        "rail_y": float("NaN"),
        "rail_z": float("NaN"),
        "clen_for_centering": float("NaN"),
        "xfs": 0.0,
        "yfs": 1.0,
        "xss": 1.0,
        "yss": 0.0,
        "orig_min_fs": -1,
        "orig_max_fs": -1,
        "orig_min_ss": -1,
        "orig_max_ss": -1,
        "w": 0,
        "h": 0,
    }  # type: TypePanel
    default_bad_region = {
        "panel": "",
        "min_x": float("NaN"),
        "max_x": float("NaN"),
        "min_y": float("NaN"),
        "max_y": float("NaN"),
        "min_fs": 0,
        "max_fs": 0,
        "min_ss": 0,
        "max_ss": 0,
        "is_fsss": 99,
    }  # type: TypeBadRegion
    default_dim = ["ss", "fs"]  # type: List[Union[int, str, None]]
    hdf5_peak_path = ""  # type: str
    try:
        file_lines: List[str] = list()
        file_handle: Union[StringIO, TextIOWrapper]
        if isinstance(file, (str, PathLike)):
            with open(file, mode="r") as file_handle:
                file_lines += file_handle.readlines()
        elif isinstance(file, StringIO) or isinstance(file, TextIOWrapper):
            file_handle = file
            file_lines += file_handle.readlines()
        else:
            raise NotImplementedError(f"Received an input file that is neither "
                                      f"a path, nor a text file handler. Cannot read "
                                      f"from it. This is the object received: {file}.")

        for line in file_lines:
            if line.startswith(";"):
                continue
            line_without_comments = line.strip().split(";")[0]  # type: str
            line_items = re.split(
                pattern="([ \t])", string=line_without_comments
            )  # type: List[str]
            line_items = [
                item for item in line_items if item not in ("", " ", "\t")
            ]
            if len(line_items) < 3:
                continue
            value = "".join(line_items[2:])  # type: str
            if line_items[1] != "=":
                continue
            path = re.split("(/)", line_items[0])  # type: List[str]
            path = [item for item in path if item not in "/"]
            if len(path) < 2:
                hdf5_peak_path = _parse_toplevel(
                    key=line_items[0],
                    value=value,
                    detector=detector,
                    beam=beam,
                    panel=default_panel,
                    hdf5_peak_path=hdf5_peak_path,
                )
                continue
            if path[0].startswith("bad"):
                if path[0] in detector["bad"]:
                    curr_bad = detector["bad"][path[0]]
                else:
                    curr_bad = copy.deepcopy(default_bad_region)
                    detector["bad"][path[0]] = curr_bad
                _parse_field_bad(key=path[1], value=value, bad=curr_bad)
            else:
                if path[0] in detector["panels"]:
                    curr_panel = detector["panels"][path[0]]
                else:
                    curr_panel = copy.deepcopy(default_panel)
                    detector["panels"][path[0]] = curr_panel
                _parse_field_for_panel(
                    key=path[1],
                    value=value,
                    panel=curr_panel,
                    panel_name=path[0],
                    detector=detector,
                )
        if not detector["panels"]:
            raise RuntimeError("No panel descriptions in geometry file.")
        num_placeholders_in_panels = -1  # type: int
        for panel in detector["panels"].values():
            if panel["dim_structure"] is not None:
                curr_num_placeholders = panel["dim_structure"].count(
                    "%"
                )  # type: int
            else:
                curr_num_placeholders = 0

            if num_placeholders_in_panels == -1:
                num_placeholders_in_panels = curr_num_placeholders
            else:
                if curr_num_placeholders != num_placeholders_in_panels:
                    raise RuntimeError(
                        "All panels' data and mask entries must have the same "
                        "number of placeholders. Found {} placeholders in a previous panel, "
                        "but panel {} has {} placeholders.".format(num_placeholders_in_panels,
                            panel, curr_num_placeholders)
                    )
        num_placeholders_in_masks = -1  # type: int
        for panel in detector["panels"].values():
            if panel["mask"] is not None:
                curr_num_placeholders = panel["mask"].count("%")
            else:
                curr_num_placeholders = 0

            if num_placeholders_in_masks == -1:
                num_placeholders_in_masks = curr_num_placeholders
            else:
                if curr_num_placeholders != num_placeholders_in_masks:
                    raise RuntimeError(
                        "All panels' data and mask entries must have the same "
                        "number of placeholders. Found {} placeholders in a previous mask, "
                        "but mask for panel {} has {} placeholders.".format(num_placeholders_in_masks,
                            panel, curr_num_placeholders)
                    )
        if num_placeholders_in_masks > num_placeholders_in_panels:
            raise RuntimeError(
                "Number of placeholders in mask ({}) cannot be larger the number than "
                "for data ({}).".format(num_placeholders_in_masks, num_placeholders_in_panels)
            )
        dim_length = -1  # type: int
        for panel_name, panel in detector["panels"].items():
            if len(panel["dim_structure"]) == 0:
                panel["dim_structure"] = copy.deepcopy(default_dim)
            found_ss = 0  # type: int
            found_fs = 0  # type: int
            found_placeholder = 0  # type: int
            for dim_index, entry in enumerate(panel["dim_structure"]):
                if entry is None:
                    raise RuntimeError(
                        "Dimension {} for panel {} is undefined.".format(
                            dim_index, panel_name
                        )
                    )
                if entry == "ss":
                    found_ss += 1
                elif entry == "fs":
                    found_fs += 1
                elif entry == "%":
                    found_placeholder += 1
            if found_ss != 1:
                raise RuntimeError(
                    "Exactly one slow scan dim coordinate is needed (found {} for "
                    "panel {}).".format(found_ss, panel_name)
                )
            if found_fs != 1:
                raise RuntimeError(
                    "Exactly one fast scan dim coordinate is needed (found {} for "
                    "panel {}).".format(found_fs, panel_name)
                )
            if found_placeholder > 1:
                raise RuntimeError(
                    "Only one placeholder dim coordinate is allowed. Maximum one "
                    "placeholder dim coordinate is allowed "
                    "(found {} for panel {})".format(found_placeholder, panel_name)
                )
            if dim_length == -1:
                dim_length = len(panel["dim_structure"])
            elif dim_length != len(panel["dim_structure"]):
                raise RuntimeError(
                    "Number of dim coordinates must be the same for all panels."
                )
            if dim_length == 1:
                raise RuntimeError(
                    "Number of dim coordinates must be at least " "two."
                )
        for panel_name, panel in detector["panels"].items():
            if panel["orig_min_fs"] < 0:
                raise RuntimeError(
                    "Please specify the minimum fs coordinate for panel {}.".format(
                        panel_name
                    )
                )
            if panel["orig_max_fs"] < 0:
                raise RuntimeError(
                    "Please specify the maximum fs coordinate for panel {}.".format(
                        panel_name
                    )
                )
            if panel["orig_min_ss"] < 0:
                raise RuntimeError(
                    "Please specify the minimum ss coordinate for panel {}.".format(
                        panel_name
                    )
                )
            if panel["orig_max_ss"] < 0:
                raise RuntimeError(
                    "Please specify the maximum ss coordinate for panel {}.".format(
                        panel_name
                    )
                )
            if panel["cnx"] is None:
                raise RuntimeError(
                    "Please specify the corner X coordinate for panel {}.".format(
                        panel_name
                    )
                )
            if panel["clen"] is None and panel["clen_from"] is None:
                raise RuntimeError(
                    "Please specify the camera length for panel {}.".format(
                        panel_name
                    )
                )
            if panel["res"] < 0:
                raise RuntimeError(
                    "Please specify the resolution or panel {}.".format(panel_name)
                )
            if panel["adu_per_eV"] is None and panel["adu_per_photon"] is None:
                raise RuntimeError(
                    "Please specify either adu_per_eV or adu_per_photon for panel "
                    "{}.".format(panel_name)
                )
            if panel["clen_for_centering"] is None and panel["rail_x"] is not None:
                raise RuntimeError(
                    "You must specify clen_for_centering if you specify the rail "
                    "direction (panel {})".format(panel_name)
                )
            if panel["rail_x"] is None:
                panel["rail_x"] = 0.0
                panel["rail_y"] = 0.0
                panel["rail_z"] = 1.0
            if panel["clen_for_centering"] is None:
                panel["clen_for_centering"] = 0.0
            panel["w"] = panel["orig_max_fs"] - panel["orig_min_fs"] + 1
            panel["h"] = panel["orig_max_ss"] - panel["orig_min_ss"] + 1
        for bad_region_name, bad_region in detector["bad"].items():
            if bad_region["is_fsss"] == 99:
                raise RuntimeError(
                    "Please specify the coordinate ranges for bad "
                    "region {}.".format(bad_region_name)
                )
        for group in detector["rigid_groups"]:
            for name in detector["rigid_groups"][group]:
                if name not in detector["panels"]:
                    raise RuntimeError(
                        "Cannot add panel to rigid_group. Panel not "
                        "found: {}".format(name)
                    )
        for group_collection in detector["rigid_group_collections"]:
            for name in detector["rigid_group_collections"][group_collection]:
                if name not in detector["rigid_groups"]:
                    raise RuntimeError(
                        "Cannot add rigid_group to collection. Rigid group not "
                        "found: {}".format(name)
                    )
        for panel in detector["panels"].values():
            d__ = (
                panel["fsx"] * panel["ssy"] - panel["ssx"] * panel["fsy"]
            )  # type: float
            if d__ == 0.0:
                raise RuntimeError("Panel {} transformation is singular.".format(panel))
            panel["xfs"] = panel["ssy"] / d__
            panel["yfs"] = panel["ssx"] / d__
            panel["xss"] = panel["fsy"] / d__
            panel["yss"] = panel["fsx"] / d__
        _find_min_max_d(detector)
    except (IOError, OSError) as exc:
        exc_type, exc_value = sys.exc_info()[:2]
        raise RuntimeError(
            "The following error occurred while reading the {0} geometry"
            "file {1}: {2}".format(
                file,
                exc_type.__name__,  # type: ignore
                exc_value,  # type: ignore
            )
        ) from exc

    return CrystFELGeometry(detector=detector, beam=beam, hdf5_peak_path=hdf5_peak_path)
