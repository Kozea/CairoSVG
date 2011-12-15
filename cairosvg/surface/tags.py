# -*- coding: utf-8 -*-
# This file is part of CairoSVG
# Copyright © 2010-2011 Kozea
#
# This library is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with CairoSVG.  If not, see <http://www.gnu.org/licenses/>.

"""
SVG tags functions.

"""

from .defs import use
from .path import path
from .shapes import circle, ellipse, line, polygon, polyline, rect
from .svg import svg
from .text import text, text_path, tspan

TAGS = {
    "circle": circle,
    "ellipse": ellipse,
    "line": line,
    "path": path,
    "polyline": polyline,
    "polygon": polygon,
    "rect": rect,
    "svg": svg,
    "text": text,
    "textPath": text_path,
    "tref": use,
    "tspan": tspan,
    "use": use}
