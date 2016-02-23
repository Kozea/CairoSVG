# This file is part of CairoSVG
# Copyright © 2010-2015 Kozea
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

import os.path
from io import BytesIO

from PIL import Image

from .helpers import node_format, size, preserve_ratio, preserved_ratio
from .parser import Tree
from .surface import cairo
from .url import parse_url, read_url


def image(surface, node):
    """Draw an image ``node``."""
    base_url = node.get('{http://www.w3.org/XML/1998/namespace}base')
    if not base_url and node.url:
        base_url = os.path.dirname(node.url)
    url = parse_url(node.get('{http://www.w3.org/1999/xlink}href'), base_url)
    image_bytes = read_url(url)

    if len(image_bytes) < 5:
        return

    x, y = size(surface, node.get('x'), 'x'), size(surface, node.get('y'), 'y')
    width = size(surface, node.get('width'), 'x')
    height = size(surface, node.get('height'), 'y')
    surface.context.rectangle(x, y, width, height)
    surface.context.clip()

    if image_bytes[:4] == b'\x89PNG':
        png_file = BytesIO(image_bytes)
    elif (image_bytes[:5] in (b'<svg ', b'<?xml', b'<!DOC') or
            image_bytes[:2] == b'\x1f\x8b'):
        surface.context.save()
        surface.context.translate(x, y)
        if 'x' in node:
            del node['x']
        if 'y' in node:
            del node['y']
        tree = Tree(
            url=url.geturl(), bytestring=image_bytes,
            tree_cache=surface.tree_cache)
        tree_width, tree_height, viewbox = node_format(
            surface, tree, reference=False)
        if not viewbox:
            tree_width = tree['width'] = width
            tree_height = tree['height'] = height
        node.image_width = tree_width or width
        node.image_height = tree_height or height
        scale_x, scale_y, translate_x, translate_y = preserve_ratio(
            surface, node)
        surface.set_context_size(
            *node_format(surface, tree, reference=False),
            preserved_ratio=preserved_ratio(tree))
        surface.context.translate(*surface.context.get_current_point())
        surface.context.scale(scale_x, scale_y)
        surface.context.translate(translate_x, translate_y)
        surface.draw(tree)
        surface.context.restore()
        return
    else:
        png_file = BytesIO()
        Image.open(BytesIO(image_bytes)).save(png_file, 'PNG')
        png_file.seek(0)

    image_surface = cairo.ImageSurface.create_from_png(png_file)

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
