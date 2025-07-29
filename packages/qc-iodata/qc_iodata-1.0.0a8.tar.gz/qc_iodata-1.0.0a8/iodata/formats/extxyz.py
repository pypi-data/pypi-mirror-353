# IODATA is an input and output module for quantum chemistry.
# Copyright (C) 2011-2019 The IODATA Development Team
#
# This file is part of IODATA.
#
# IODATA is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# IODATA is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>
# --
"""Extended XYZ file format.

The extended XYZ file format is defined in the
`ASE documentation <https://wiki.fysik.dtu.dk/ase/ase/io/formatoptions.html#xyz>`_.

Usually, the different frames in a trajectory describe different geometries of the same
molecule, with atoms in the same order. The ``load_many`` function below can also
handle an XYZ with different molecules, e.g. a molecular database.

"""

import shlex
from collections.abc import Iterator

import numpy as np

from ..docstrings import document_load_many, document_load_one
from ..periodic import num2sym, sym2num
from ..utils import LineIterator, LoadError, amu, angstrom, strtobool
from .xyz import load_one as load_one_xyz

__all__ = ()


PATTERNS = ["*.extxyz"]


def _convert_title_value(value: str):
    """Search for the correct dtype and convert the string."""
    list_of_splits = value.split()
    # If it is just one item, first try int, then float and finally return a bool or str
    if len(list_of_splits) == 1:
        value = value.strip()
        if value.isdigit():
            converted_value = int(value)
        else:
            try:
                converted_value = float(value)
            except ValueError:
                try:
                    converted_value = strtobool(value)
                except ValueError:
                    converted_value = value
    else:
        # Do the same but return it as a numpy array
        try:
            converted_value = np.array(list_of_splits, dtype=int)
        except ValueError:
            try:
                converted_value = np.array(list_of_splits, dtype=float)
            except ValueError:
                try:
                    converted_value = np.array(
                        [strtobool(split) for split in list_of_splits], dtype=bool
                    )
                except ValueError:
                    converted_value = np.array(list_of_splits, dtype=str)
    return converted_value


def _parse_properties(properties: str, lit: LineIterator) -> list[tuple]:
    """Parse the properties listed in the title into atom_columns.

    Parameters
    ----------
    properties
        The part of the title of an XYZ file containing column definitions.
    lit
        The LineIterator reading the file, only used for error messages.

    Returns
    -------
    atom_columns
        A list of tuples specifying the columns in the extended XYZ file.
        For more details, see ``ATOM_COLUMNS_DOC`` in ``iodata.formats.xyz``.
    """
    atom_columns = []
    # Maps the dtype to the atom_columns dtype, load_word and dump_word
    dtype_map = {
        "S": (np.dtype("U25"), str, "{:10s}".format),
        "R": (float, float, "{:15.10f}".format),
        "I": (int, int, "{:10d}".format),
        "L": (bool, strtobool, lambda boolean: "T" if boolean else "F"),
    }
    # Some predefined iodata attributes which can be mapped
    # pos is assumed to be in angstrom, masses in amu (ase convention)
    # No unit convertion takes place for the other attributes
    atom_column_map = {
        "pos": (
            "atcoords",
            None,
            (3,),
            float,
            (lambda word: float(word) * angstrom),
            (lambda value: f"{value / angstrom:15.10f}"),
        ),
        "masses": (
            "atmasses",
            None,
            (),
            float,
            (lambda word: float(word) * amu),
            (lambda value: f"{value / amu:15.10f}"),
        ),
        "force": (
            "atgradient",
            None,
            (3,),
            float,
            (lambda word: -float(word)),
            (lambda value: f"{-value:15.10f}"),
        ),
    }
    atnum_column = (
        "atnums",
        None,
        (),
        int,
        (lambda word: int(word) if word.isdigit() else sym2num[word.title()]),
        (lambda atnum: f"{num2sym[atnum]:2s}"),
    )
    splitted_properties = properties.split(":")
    if len(splitted_properties) % 3 != 0:
        raise LoadError(
            f"Cannot parse property from the title line: '{properties}'. "
            f"The expected format is name:dtype:shape.",
            lit,
        )
    # Each property has 3 values: its name, dtype and shape
    names = splitted_properties[::3]
    dtypes = splitted_properties[1::3]
    shapes = splitted_properties[2::3]
    if "Z" in names:
        # Try to map 'Z' to the 'atnums' attribute
        atom_column_map["Z"] = atnum_column
    elif "species" in names:
        # If 'Z' is not present, use 'species'
        atom_column_map["species"] = atnum_column
    for name, dtype, shape in zip(names, dtypes, shapes):
        if name in atom_column_map:
            atom_columns.append(atom_column_map[name])
        else:
            # Use the 'extra' attribute to store values which are not predefined in iodata
            shape_suffix = () if shape == "1" else (int(shape),)
            atom_columns.append(("extra", name, shape_suffix, *dtype_map[dtype]))
    return atom_columns


def _parse_title(title: str, lit: LineIterator) -> tuple[list[tuple], dict[str]]:
    """Parse the title in an extended xyz file.

    Parameters
    ----------
    title
        The full title line.
    lit
        The LineIterator reading the file, only used for error messages.

    Returns
    -------
    atom_columns
        A list of tuples specifying the columns in the extended XYZ file.
        For more details, see ``ATOM_COLUMNS_DOC`` in ``iodata.formats.xyz``.
    data
        Attributes to be included in the ``IOData`` instance,
        taken from the title line.
    """
    key_value_pairs = shlex.split(title)
    # A dict of predefined iodata atrributes with their names and dtype convertion functions

    def load_cellvecs(word):
        return np.array(word.split(), dtype=float).reshape([3, 3]) * angstrom

    iodata_attrs = {
        "energy": ("energy", float),
        "Lattice": ("cellvecs", load_cellvecs),
        "charge": ("charge", float),
    }
    data = {}
    for key_value_pair in key_value_pairs:
        if "=" in key_value_pair:
            key, value = key_value_pair.split("=", 1)
            if key == "Properties":
                atom_columns = _parse_properties(value, lit)
            elif key in iodata_attrs:
                data[iodata_attrs[key][0]] = iodata_attrs[key][1](value)
            else:
                data.setdefault("extra", {})[key] = _convert_title_value(value)
        else:
            # If no value is given, set it True
            data.setdefault("extra", {})[key_value_pair] = True
    return atom_columns, data


@document_load_one(
    "EXTXYZ",
    ["title"],
    ["atcoords", "atgradient", "atmasses", "atnums", "cellvecs", "charge", "energy", "extra"],
)
def load_one(lit: LineIterator) -> dict:
    """Do not edit this docstring. It will be overwritten."""
    atom_line = next(lit)
    title_line = next(lit)
    # parse title
    atom_columns, title_data = _parse_title(title_line, lit)
    lit.back(title_line)
    lit.back(atom_line)
    xyz_data = load_one_xyz(lit, atom_columns)
    # If the extra attribute is present, prevent it from overwriting itself
    if "extra" in title_data and "extra" in xyz_data:
        xyz_data["extra"].update(title_data["extra"])
    title_data.update(xyz_data)
    return title_data


@document_load_many(
    "EXTXYZ",
    ["title"],
    ["atcoords", "atgradient", "atmasses", "atnums", "cellvecs", "charge", "energy", "extra"],
)
def load_many(lit: LineIterator) -> Iterator[dict]:
    """Do not edit this docstring. It will be overwritten."""
    # XYZ Trajectory files are a simple concatenation of individual XYZ files,'
    # making it trivial to load many frames.
    try:
        while True:
            # Check for and skip empty lines at the end of file
            line = next(lit)
            if line.strip() == "":
                return
            lit.back(line)
            yield load_one(lit)
    except StopIteration:
        return
