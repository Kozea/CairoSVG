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
Images manager.

"""

import cairo
from io import BytesIO
try:
    from urllib import urlopen
    import urlparse
except ImportError:
    from urllib.request import urlopen
    from urllib import parse as urlparse  # Python 3

from .helpers import size, preserve_ratio


def image(surface, node):
    """Draw an image ``node``."""
    url = node.get("{http://www.w3.org/1999/xlink}href")
    if not url:
        return
    if node.url:
        url = urlparse.urljoin(node.url, url)
    if urlparse.urlparse(url).scheme:
        input_ = urlopen(url)
    else:
        input_ = open(url)  # filename
    try:
        image_surface = cairo.ImageSurface.create_from_png(input_)
    except:
        # Failed to load image
        return

    x, y = size(surface, node.get("x"), "x"), size(surface, node.get("y"), "y")
    width = size(surface, node.get("width"), "x")
    height = size(surface, node.get("height"), "y")

    node.image_width = image_surface.get_width()
    node.image_height = image_surface.get_height()
    scale_x, scale_y, translate_x, translate_y = preserve_ratio(surface, node)

    surface.context.rectangle(x, y, width, height)
    pattern_pattern = cairo.SurfacePattern(image_surface)
    surface.context.save()
    surface.context.translate(*surface.context.get_current_point())
    surface.context.scale(scale_x, scale_y)
    surface.context.translate(translate_x, translate_y)
    surface.context.set_source(pattern_pattern)
    surface.context.fill()
    surface.context.restore()
