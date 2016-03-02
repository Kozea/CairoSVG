# This file is part of CairoSVG
# Copyright © 2010-2016 Kozea
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
Calculate bounding box for SVG shapes and paths.

A bounding box is a dict with fields:
    minx
    maxx
    miny
    maxy

"""

from math import isinf, fmod, pi, radians, sin, cos, tan, acos, atan, sqrt

from .helpers import normalize, point
from .defs import parse_url
from .parser import Tree
from .features import match_features
from .path import PATH_LETTERS


EMPTY_BOUNDING_BOX = {
    'minx': float('inf'),
    'maxx': float('-inf'),
    'miny': float('inf'),
    'maxy': float('-inf')
}


def get_initial_bounding_box():
    return EMPTY_BOUNDING_BOX.copy()


def calculate_bounding_box(node):
    """
    Calculate bounding box (simple case) and return it

    :param node:   node from SVG file

    :returns: bounding box(dict)
    """

    # See for explanation of bounding box:
    #   https://www.w3.org/TR/SVG/coords.html#ObjectBoundingBox
    if 'bounding_box' not in node:
        if node.tag in BOUNDING_BOX_METHODS:
            bounding_box = BOUNDING_BOX_METHODS[node.tag](node)
            if is_non_empty_bounding_box(bounding_box):
                node['bounding_box'] = bounding_box

    return node['bounding_box'] if 'bounding_box' in node else None


def bounding_box_rect(node):
    """
    Return the bounding box of the rectangle

    :param node:   node of type <rect>

    :returns: bounding box(dict)
    """

    x = float(node.get('x', '0'))
    y = float(node.get('y', '0'))
    width = float(node.get('width', '0'))
    if width < 0.0:
        width = 0.0
    height = float(node.get('height', '0'))
    if height < 0.0:
        height = 0.0
    return {
        'minx': x,
        'maxx': x + width,
        'miny': y,
        'maxy': y + height
    }


def bounding_box_circle(node):
    """
    Return the bounding box of the circle

    :param node:   node of type <circle>

    :returns: bounding box(dict)
    """

    center_x = float(node.get('cx', '0'))
    center_y = float(node.get('cy', '0'))
    radius = float(node.get('r', '0'))
    if radius < 0.0:
        radius = 0.0
    return {
        'minx': center_x - radius,
        'maxx': center_x + radius,
        'miny': center_y - radius,
        'maxy': center_y + radius
    }


def bounding_box_ellipse(node):
    """
    Return the bounding box of the ellipse

    :param node:   node of type <ellipse>

    :returns: bounding box(dict)
    """

    center_x = float(node.get('cx', '0'))
    center_y = float(node.get('cy', '0'))
    radius_x = float(node.get('rx', '0'))
    if radius_x < 0.0:
        radius_x = 0.0
    radius_y = float(node.get('ry', '0'))
    if radius_y < 0.0:
        radius_y = 0.0
    return {
        'minx': center_x - radius_x,
        'maxx': center_x + radius_x,
        'miny': center_y - radius_y,
        'maxy': center_y + radius_y
    }


def bounding_box_line(node):
    """
    Return the bounding box of the line

    :param node:   node of type <line>

    :returns: bounding box(dict)
    """

    x1 = float(node.get('x1', '0'))
    y1 = float(node.get('y1', '0'))
    x2 = float(node.get('x2', '0'))
    y2 = float(node.get('y2', '0'))
    return {
        'minx': min(x1, x2),
        'maxx': max(x1, x2),
        'miny': min(y1, y2),
        'maxy': max(y1, y2)
    }


def bounding_box_polyline(node):
    """
    Return the bounding box of the polyline

    :param node:   node of type <polyline>

    :returns: bounding box(dict)
    """

    # Start with 'empty' bounding box
    bounding_box = get_initial_bounding_box()

    # Iterate all points adjusting bounding box for every coordinate
    points = normalize(node.get('points', ''))
    while points:
        x, y, points = point(None, points)
        extend_bounding_box(bounding_box, float(x), float(y))

    return bounding_box


def bounding_box_polygon(node):
    """
    Return the bounding box of the polygon

    :param node:   node of type <polygon>

    :returns: bounding box(dict)
    """

    # Polygon and polyline share same type of shape
    return bounding_box_polyline(node)


def bounding_box_path(node):
    """
    Return the bounding box of the path

    :param node:    node of type <path>

    :returns: bounding box(dict)
    """

    path_data = node.get('d', '')

    # Normalize path data for correct parsing
    for letter in PATH_LETTERS:
        path_data = path_data.replace(letter, ' {} '.format(letter))
    path_data = normalize(path_data)

    # Start with 'empty' bounding box
    bounding_box = get_initial_bounding_box()

    # Iterate all points adjusting bounding box for every coordinate
    previous_x = 0
    previous_y = 0
    letter = 'M'    # Move as default
    while path_data:
        path_data = path_data.strip()
        if path_data.split(' ', 1)[0] in PATH_LETTERS:
            letter, path_data = (path_data + ' ').split(' ', 1)

        if letter in 'aA':
            # Elliptical arc curve
            rx, ry, path_data = point(None, path_data)
            rotation, path_data = path_data.split(' ', 1)
            rotation = radians(float(rotation))

            # The large and sweep values are not always separated from the
            # following values, here is the crazy parser
            large, path_data = path_data[0], path_data[1:].strip()
            while not large[-1].isdigit():
                large, path_data = large + path_data[0], path_data[1:].strip()
            sweep, path_data = path_data[0], path_data[1:].strip()
            while not sweep[-1].isdigit():
                sweep, path_data = sweep + path_data[0], path_data[1:].strip()

            large, sweep = bool(int(large)), bool(int(sweep))

            x, y, path_data = point(None, path_data)

            # Relative coordinate, convert to absolute
            if letter == 'a':
                x += previous_x
                y += previous_y

            # Only extend bounding box with end coordinate
            arc_bounding_box = bounding_box_elliptical_arc(previous_x, previous_y, rx, ry, rotation, large, sweep, x, y)
            extend_bounding_box(bounding_box, arc_bounding_box['minx'], arc_bounding_box['miny'])
            extend_bounding_box(bounding_box, arc_bounding_box['maxx'], arc_bounding_box['maxy'])
            previous_x = x
            previous_y = y

        elif letter in 'cC':
            # Curve
            x1, y1, path_data = point(None, path_data)
            x2, y2, path_data = point(None, path_data)
            x, y, path_data = point(None, path_data)

            # Relative coordinates, convert to absolute
            if letter == 'c':
                x1 += previous_x
                y1 += previous_y
                x2 += previous_x
                y2 += previous_y
                x += previous_x
                y += previous_y

            # Extend bounding box with all coordinates
            extend_bounding_box(bounding_box, x1, y1)
            extend_bounding_box(bounding_box, x2, y2)
            extend_bounding_box(bounding_box, x, y)
            previous_x = x
            previous_y = y

        elif letter in 'hH':
            # Horizontal line
            x, path_data = (path_data + ' ').split(' ', 1)

            # Relative coordinate, convert to absolute
            if letter == 'h':
                x += previous_x

            # Extend bounding box with coordinate
            extend_bounding_box(bounding_box, x, previous_y)
            previous_x = x

        elif letter in 'lLmMtT':
            # Line/Move/Smooth quadratic curve
            x, y, path_data = point(None, path_data)

            # Relative coordinate, convert to absolute
            if letter in 'lmt':
                x += previous_x
                y += previous_y

            # Extend bounding box with coordinate
            extend_bounding_box(bounding_box, x, y)
            previous_x = x
            previous_y = y

        elif letter in 'qQsS':
            # Quadratic curve/Smooth curve
            x1, y1, path_data = point(None, path_data)
            x, y, path_data = point(None, path_data)

            # Relative coordinates, convert to absolute
            if letter in 'qs':
                x1 += previous_x
                y1 += previous_y
                x += previous_x
                y += previous_y

            # Extend bounding box with coordinates
            extend_bounding_box(bounding_box, x1, y1)
            extend_bounding_box(bounding_box, x, y)
            previous_x = x
            previous_y = y

        elif letter in 'vV':
            # Vertical line
            y, path_data = (path_data + ' ').split(' ', 1)

            # Relative coordinate, convert to absolute
            if letter == 'v':
                y += previous_y

            # Extend bounding box with coordinate
            extend_bounding_box(bounding_box, previous_x, y)
            previous_y = y

        path_data = path_data.strip()

    return bounding_box


def bounding_box_text(node):
    """
    Return the bounding box of the text

    :param node:    node of type <text>

    :returns: bounding box(dict)
    """

    return node['text_bounding_box'] if 'text_bounding_box' in node else None


def angle(bx, by):
    """
    Return the angle between vector (1,0) and vector (bx,by)

    :param bx:  x-coordinate of vector
    :param by:  y-coordinate of vector

    :returns: radians(float)
    """

    return fmod(2 * pi + (1.0 if by > 0.0 else -1.0) * acos(bx / sqrt(bx * bx + by * by)), 2 * pi)


def bounding_box_elliptical_arc(x1, y1, rx, ry, phi, large, sweep, x, y):
    """
    Return the bounding box of the elliptical arc described by the parameters

    See following website for original code:
        http://fridrich.blogspot.nl/2011/06/bounding-box-of-svg-elliptical-arc.html

    :param x1:      x-coordinate of start
    :param y1:      y-coordinate of start
    :param rx:      radius on horizontal (x) axis
    :param ry:      radius on vertical (y) axis
    :param phi:     rotation of arc
    :param large:   use long side of arc (bool)
    :param sweep:   grow in angle (bool)
    :param x:       x-coordinate of end
    :param y:       y-coordinate of end

    :returns: bounding box(dict)
    """

    if rx < 0.0:
        rx *= -1.0
    if ry < 0.0:
        ry *= -1.0

    if rx == 0.0 or ry == 0.0:
        return {
            'minx': x1 if x1 < x else x,
            'maxx': x1 if x1 > x else x,
            'miny': y1 if y1 < y else y,
            'maxy': y1 if y1 > y else y
        }

    x1prime = cos(phi) * (x1 - x) / 2 + sin(phi) * (y1 - y) / 2
    y1prime = -sin(phi) * (x1 - x) / 2 + cos(phi) * (y1 - y) / 2

    radicant = rx * rx * ry * ry - rx * rx * y1prime * y1prime - ry * ry * x1prime * x1prime
    radicant /= rx * rx * y1prime * y1prime + ry * ry * x1prime * x1prime
    cxprime = cyprime = 0.0

    if radicant < 0.0:
        ratio = rx / ry
        radicant = y1prime * y1prime + x1prime * x1prime / (ratio * ratio)
        if radicant < 0.0:
            return {
                'minx': x1 if x1 < x else x,
                'maxx': x1 if x1 > x else x,
                'miny': y1 if y1 < y else y,
                'maxy': y1 if y1 > y else y
            }
        ry = sqrt(radicant)
        rx = ratio * ry
    else:
        factor = (-1.0 if large == sweep else 1.0) * sqrt(radicant)

        cxprime = factor * rx * y1prime / ry
        cyprime = -factor * ry * x1prime / rx

    cx = cxprime * cos(phi) - cyprime * sin(phi) + (x1 + x) / 2
    cy = cxprime * sin(phi) + cyprime * cos(phi) + (y1 + y) / 2

    if phi == 0 or phi == pi:
        minx = cx - rx
        tminx = angle(-rx, 0)
        maxx = cx + rx
        tmaxx = angle(rx, 0)
        miny = cy - ry
        tminy = angle(0, -ry)
        maxy = cy + ry
        tmaxy = angle(0, ry)
    elif phi == pi / 2.0 or phi == 3.0 * pi / 2.0:
        minx = cx - ry
        tminx = angle(-ry, 0)
        maxx = cx + ry
        tmaxx = angle(ry, 0)
        miny = cy - rx
        tminy = angle(0, -rx)
        maxy = cy + rx
        tmaxy = angle(0, rx)
    else:
        tminx = -atan(ry * tan(phi) / rx)
        tmaxx = pi - atan(ry * tan(phi) / rx)
        minx = cx + rx * cos(tminx) * cos(phi) - ry * sin(tminx) * sin(phi)
        maxx = cx + rx * cos(tmaxx) * cos(phi) - ry * sin(tmaxx) * sin(phi)
        if minx > maxx:
            minx, maxx = maxx, minx
            tminx, tmaxx = tmaxx, tminx
        tmp_y = cy + rx * cos(tminx) * sin(phi) + ry * sin(tminx) * cos(phi)
        tminx = angle(minx - cx, tmp_y - cy)
        tmp_y = cy + rx * cos(tmaxx) * sin(phi) + ry * sin(tmaxx) * cos(phi)
        tmaxx = angle(maxx - cx, tmp_y - cy)

        tminy = atan(ry / (tan(phi) * rx))
        tmaxy = atan(ry / (tan(phi) * rx)) + pi
        miny = cy + rx * cos(tminy) * sin(phi) + ry * sin(tminy) * cos(phi)
        maxy = cy + rx * cos(tmaxy) * sin(phi) + ry * sin(tmaxy) * cos(phi)
        if miny > maxy:
            miny, maxy = maxy, miny
            tminy, tmaxy = tmaxy, tminy
        tmp_x = cx + rx * cos(tminy) * cos(phi) - ry * sin(tminy) * sin(phi)
        tminy = angle(tmp_x - cx, miny - cy)
        tmp_x = cx + rx * cos(tmaxy) * cos(phi) - ry * sin(tmaxy) * sin(phi)
        tmaxy = angle(tmp_x - cx, maxy - cy)

    angle1 = angle(x1 - cx, y1 - cy)
    angle2 = angle(x - cx, y - cy)

    if not sweep:
        angle1, angle2 = angle2, angle1

    other_arc = False
    if angle1 > angle2:
        angle1, angle2 = angle2, angle1
        other_arc = True

    if (not other_arc and (angle1 > tminx or angle2 < tminx)) or (other_arc and not (angle1 > tminx or angle2 < tminx)):
        minx = x1 if x1 < x else x
    if (not other_arc and (angle1 > tmaxx or angle2 < tmaxx)) or (other_arc and not (angle1 > tmaxx or angle2 < tmaxx)):
        maxx = x1 if x1 > x else x
    if (not other_arc and (angle1 > tminy or angle2 < tminy)) or (other_arc and not (angle1 > tminy or angle2 < tminy)):
        miny = y1 if y1 < y else y
    if (not other_arc and (angle1 > tmaxy or angle2 < tmaxy)) or (other_arc and not (angle1 > tmaxy or angle2 < tmaxy)):
        maxy = y1 if y1 > y else y

    return {
        'minx': minx,
        'maxx': maxx,
        'miny': miny,
        'maxy': maxy
    }


def bounding_box_group(node):
    """
    Return the bounding box of the group

    :param node:    node of type <g> or <marker>

    :returns: bounding box(dict)
    """

    bounding_box = get_initial_bounding_box()
    for child in node.children:
        combine_bounding_box(bounding_box, calculate_bounding_box(child))

    return bounding_box


def bounding_box_use(node):
    """
    Return the bounding box of the use(d element)

    :param node:    node of type <use>

    :returns: bounding box(dict)
    """

    href = parse_url(node.get('{http://www.w3.org/1999/xlink}href')).geturl()
    tree = Tree(url=href, parent=node)

    if not match_features(tree.xml_tree):
        return None

    return calculate_bounding_box(tree)


def extend_bounding_box(bounding_box, x, y):
    """
    Extend bounding_box by coordinate

    :param bounding_box:    current bounding box
    :param x:               x-value of coordinate
    :param y:               y-value of coordinate
    """

    if x < bounding_box['minx']:
        bounding_box['minx'] = x
    if x > bounding_box['maxx']:
        bounding_box['maxx'] = x
    if y < bounding_box['miny']:
        bounding_box['miny'] = y
    if y > bounding_box['maxy']:
        bounding_box['maxy'] = y


def combine_bounding_box(bounding_box, another_bounding_box):
    """
    Combine bounding_box with another bounding box

    :param bounding_box:            current bounding box
    :param another_bounding_box:    another bounding box
    """

    if is_valid_bounding_box(another_bounding_box):
        extend_bounding_box(bounding_box, another_bounding_box['minx'], another_bounding_box['miny'])
        extend_bounding_box(bounding_box, another_bounding_box['maxx'], another_bounding_box['maxy'])


def is_valid_bounding_box(bounding_box):
    """
    Return whether bounding box is initialized (has received a value)

    :param bounding_box:    bounding box to test for being valid

    :returns: bool
    """

    # If 'minx' or 'miny' is set, 'maxx' and 'maxy' will also be set (resulting in a valid bounding box)
    return bounding_box and \
           not isinf(bounding_box['minx']) and \
           not isinf(bounding_box['miny'])


def is_non_empty_bounding_box(bounding_box):
    """
    Return whether bounding box is valid and has a size (is not a horizontal or vertical line)

    :param bounding_box:    bounding box to test for being empty

    :returns: bool
    """

    return is_valid_bounding_box(bounding_box) and \
           bounding_box["minx"] != bounding_box["maxx"] and \
           bounding_box["miny"] != bounding_box["maxy"]


BOUNDING_BOX_METHODS = {
    'rect': bounding_box_rect,
    'circle': bounding_box_circle,
    'ellipse': bounding_box_ellipse,
    'line': bounding_box_line,
    'polyline': bounding_box_polyline,
    'polygon': bounding_box_polygon,
    'path': bounding_box_path,
    'text': bounding_box_text,
    'tspan': bounding_box_text,
    'textPath': bounding_box_text,
    'g': bounding_box_group,
    'use': bounding_box_use,
    'marker': bounding_box_group,
}
