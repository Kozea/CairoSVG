# -*- coding: utf-8 -*-
# This file is part of CairoSVG
# Copyright © 2010-2012 Kozea
#
# This library is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This library is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with CairoSVG.  If not, see <http://www.gnu.org/licenses/>.

"""
Units functions.

"""


UNITS = {
    "mm": 1 / 25.4,
    "cm": 1 / 2.54,
    "in": 1,
    "pt": 1 / 72.,
    "pc": 1 / 6.,
    "px": None,
    "em": NotImplemented,
    "ex": NotImplemented,
    "%": NotImplemented}


class NotImplementedUnitError(ValueError, NotImplementedError):
    """Exception raised when an unit is not implemented."""


def size(surface, string=None):
    """Replace a string with units by a float value."""
    if not string:
        return 0

    if string.replace(".", "", 1).lstrip(" -").isdigit():
        return float(string)

    for unit, coefficient in UNITS.items():
        if unit in string:
            number = float(string.strip(" " + unit))
            if coefficient == NotImplemented:
                raise NotImplementedUnitError
            else:
                return number * (
                    surface.dpi * coefficient if coefficient else 1)

    # Unknown size or multiple sizes
    return 0
