# -*- coding: utf-8 -*-
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
Paths manager.

"""

from math import pi, radians

from .helpers import (
    node_format, normalize, point, point_angle, preserve_ratio,
    quadratic_points, rotate, urls)
from .units import size


PATH_LETTERS = "achlmqstvzACHLMQSTVZ"
PATH_TAGS = (
    "circle", "ellipse", "line", "path", "polygon", "polyline", "rect")


def draw_marker(surface, marker_list, point, angle, scale):
    for marker in marker_list:
        # TODO: fix url parsing
        marker_node = surface.markers.get(marker[1:])

        if not marker_node:
            continue

        scale_x, scale_y, translate_x, translate_y = \
            preserve_ratio(surface, marker_node)

        width, height, viewbox = node_format(surface, marker_node)
        if viewbox:
            viewbox_width = viewbox[2]
            viewbox_height = viewbox[3]
        else:
            viewbox_width = width or 0
            viewbox_height = height or 0

        if 0 in (viewbox_width, viewbox_height):
            scale_x = scale_y = 1
        else:
            scale_x = scale / viewbox_width * float(scale_x)
            scale_y = scale / viewbox_width * float(scale_y)

        if marker_node:
            temp_path = surface.context.copy_path()
            surface.context.new_path()

            node_angle = marker_node.get("orient", "0")
            if node_angle != "auto":
                angle = radians(float(node_angle))

            for child in marker_node.children:
                surface.context.save()
                surface.context.translate(*point)
                surface.context.rotate(angle)
                surface.context.scale(scale_x, scale_y)
                surface.context.translate(translate_x, translate_y)
                surface.draw(child)
                surface.context.restore()

            surface.context.append_path(temp_path)


def draw_markers(surface, node):
    if not getattr(node, "vertices", None):
        return

    markers = {}
    common_markers = list(urls(node.get("marker", "")))
    for position in ("start", "mid", "end"):
        attribute = "marker-{}".format(position)
        if attribute in node:
            markers[position] = list(urls(node[attribute]))
        else:
            markers[position] = common_markers

    angle1, angle2 = None, None
    position = "start"

    if node.get("markerUnits") == "userSpaceOnUse":
        scale = 1
    else:
        scale = size(
            surface, surface.parent_node.get("stroke-width"))

    while node.vertices:
        point = node.vertices.pop(0)
        angles = node.vertices.pop(0) if node.vertices else None
        if angles:
            if position == "start":
                angle = pi - angles[0]
            else:
                angle = (angle2 + angles[0]) / 2
            angle1, angle2 = angles
        else:
            angle = angle2
            position = "end"

        draw_marker(surface, markers[position], point, angle, scale)

        position = "mid" if angles else "start"


def path(surface, node):
    """Draw a path ``node``."""
    string = node.get("d", "")

    node.vertices = []

    if not string.strip():
        # Don't draw empty paths at all
        return

    for letter in PATH_LETTERS:
        string = string.replace(letter, " %s " % letter)

    last_letter = None
    string = normalize(string)

    while string:
        string = string.strip()
        if string.split(" ", 1)[0] in PATH_LETTERS:
            letter, string = (string + " ").split(" ", 1)
            if last_letter in (None, "z", "Z") and letter not in "mM":
                node.vertices.append(surface.context.get_current_point())
        elif letter == "M":
            letter = "L"
        elif letter == "m":
            letter = "l"

        if letter in "aA":
            # Elliptic curve
            x1, y1 = surface.context.get_current_point()
            rx, ry, string = point(surface, string)
            rotation, string = string.split(" ", 1)
            rotation = radians(float(rotation))

            # The large and sweep values are not always separated from the
            # following values, here is the crazy parser
            large, string = string[0], string[1:].strip()
            while not large[-1].isdigit():
                large, string = large + string[0], string[1:].strip()
            sweep, string = string[0], string[1:].strip()
            while not sweep[-1].isdigit():
                sweep, string = sweep + string[0], string[1:].strip()

            large, sweep = bool(int(large)), bool(int(sweep))

            x3, y3, string = point(surface, string)

            if letter == "A":
                # Absolute x3 and y3, convert to relative
                x3 -= x1
                y3 -= y1

            # rx=0 or ry=0 means straight line
            if not rx or not ry:
                string = "l %f %f %s" % (x3, y3, string)
                continue

            radii_ratio = ry / rx

            # Cancel the rotation of the second point
            xe, ye = rotate(x3, y3, -rotation)
            ye /= radii_ratio

            # Find the angle between the second point and the x axis
            angle = point_angle(0, 0, xe, ye)

            # Put the second point onto the x axis
            xe = (xe ** 2 + ye ** 2) ** .5
            ye = 0

            # Update the x radius if it is too small
            rx = max(rx, xe / 2)

            # Find one circle centre
            xc = xe / 2
            yc = (rx ** 2 - xc ** 2) ** .5

            # Choose between the two circles according to flags
            if not (large ^ sweep):
                yc = -yc

            # Define the arc sweep
            arc = \
                surface.context.arc if sweep else surface.context.arc_negative

            # Put the second point and the center back to their positions
            xe, ye = rotate(xe, 0, angle)
            xc, yc = rotate(xc, yc, angle)

            # Find the drawing angles
            angle1 = point_angle(xc, yc, 0, 0)
            angle2 = point_angle(xc, yc, xe, ye)

            # Store the tangent angles
            node.vertices.append((-angle1, -angle2))

            # Draw the arc
            surface.context.save()
            surface.context.translate(x1, y1)
            surface.context.rotate(rotation)
            surface.context.scale(1, radii_ratio)
            arc(xc, yc, rx, angle1, angle2)
            surface.context.restore()

        elif letter == "c":
            # Relative curve
            x, y = surface.context.get_current_point()
            x1, y1, string = point(surface, string)
            x2, y2, string = point(surface, string)
            x3, y3, string = point(surface, string)
            node.vertices.append((
                point_angle(x2, y2, x1, y1), point_angle(x2, y2, x3, y3)))
            surface.context.rel_curve_to(x1, y1, x2, y2, x3, y3)

            # Save absolute values for x and y, useful if next letter is s or S
            x1 += x
            x2 += x
            x3 += x
            y1 += y
            y2 += y
            y3 += y

        elif letter == "C":
            # Curve
            x1, y1, string = point(surface, string)
            x2, y2, string = point(surface, string)
            x3, y3, string = point(surface, string)
            node.vertices.append((
                point_angle(x2, y2, x1, y1), point_angle(x2, y2, x3, y3)))
            surface.context.curve_to(x1, y1, x2, y2, x3, y3)

        elif letter == "h":
            # Relative horizontal line
            x, string = (string + " ").split(" ", 1)
            old_x, old_y = surface.context.get_current_point()
            angle = 0 if size(surface, x, "x") > 0 else pi
            node.vertices.append((pi - angle, angle))
            surface.context.rel_line_to(size(surface, x, "x"), 0)

        elif letter == "H":
            # Horizontal line
            x, string = (string + " ").split(" ", 1)
            old_x, old_y = surface.context.get_current_point()
            angle = 0 if size(surface, x, "x") > old_x else pi
            node.vertices.append((pi - angle, angle))
            surface.context.line_to(size(surface, x, "x"), old_y)

        elif letter == "l":
            # Relative straight line
            x, y, string = point(surface, string)
            angle = point_angle(0, 0, x, y)
            node.vertices.append((pi - angle, angle))
            surface.context.rel_line_to(x, y)

        elif letter == "L":
            # Straight line
            x, y, string = point(surface, string)
            old_x, old_y = surface.context.get_current_point()
            angle = point_angle(old_x, old_y, x, y)
            node.vertices.append((pi - angle, angle))
            surface.context.line_to(x, y)

        elif letter == "m":
            # Current point relative move
            x, y, string = point(surface, string)
            if surface.context.has_current_point():
                surface.context.rel_move_to(x, y)
            else:
                surface.context.move_to(x, y)

        elif letter == "M":
            # Current point move
            x, y, string = point(surface, string)
            surface.context.move_to(x, y)

        elif letter == "q":
            # Relative quadratic curve
            x1, y1 = 0, 0
            x2, y2, string = point(surface, string)
            x3, y3, string = point(surface, string)
            xq1, yq1, xq2, yq2, xq3, yq3 = quadratic_points(
                x1, y1, x2, y2, x3, y3)
            surface.context.rel_curve_to(xq1, yq1, xq2, yq2, xq3, yq3)
            node.vertices.append((0, 0))

        elif letter == "Q":
            # Quadratic curve
            x1, y1 = surface.context.get_current_point()
            x2, y2, string = point(surface, string)
            x3, y3, string = point(surface, string)
            xq1, yq1, xq2, yq2, xq3, yq3 = quadratic_points(
                x1, y1, x2, y2, x3, y3)
            surface.context.curve_to(xq1, yq1, xq2, yq2, xq3, yq3)
            node.vertices.append((0, 0))

        elif letter == "s":
            # Relative smooth curve
            x, y = surface.context.get_current_point()
            x1 = x3 - x2 if last_letter in "csCS" else 0
            y1 = y3 - y2 if last_letter in "csCS" else 0
            x2, y2, string = point(surface, string)
            x3, y3, string = point(surface, string)
            node.vertices.append((
                point_angle(x2, y2, x1, y1), point_angle(x2, y2, x3, y3)))
            surface.context.rel_curve_to(x1, y1, x2, y2, x3, y3)

            # Save absolute values for x and y, useful if next letter is s or S
            x1 += x
            x2 += x
            x3 += x
            y1 += y
            y2 += y
            y3 += y

        elif letter == "S":
            # Smooth curve
            x, y = surface.context.get_current_point()
            x1 = x3 + (x3 - x2) if last_letter in "csCS" else x
            y1 = y3 + (y3 - y2) if last_letter in "csCS" else y
            x2, y2, string = point(surface, string)
            x3, y3, string = point(surface, string)
            node.vertices.append((
                point_angle(x2, y2, x1, y1), point_angle(x2, y2, x3, y3)))
            surface.context.curve_to(x1, y1, x2, y2, x3, y3)

        elif letter == "t":
            # Relative quadratic curve end
            if last_letter not in "QqTt":
                x2, y2, x3, y3 = 0, 0, 0, 0
            elif last_letter in "QT":
                x2 -= x1
                y2 -= y1
                x3 -= x1
                y3 -= y1
            x2 = x3 - x2
            y2 = y3 - y2
            x1, y1 = 0, 0
            x3, y3, string = point(surface, string)
            xq1, yq1, xq2, yq2, xq3, yq3 = quadratic_points(
                x1, y1, x2, y2, x3, y3)
            node.vertices.append((0, 0))
            surface.context.rel_curve_to(xq1, yq1, xq2, yq2, xq3, yq3)

        elif letter == "T":
            # Quadratic curve end
            abs_x, abs_y = surface.context.get_current_point()
            if last_letter not in "QqTt":
                x2, y2, x3, y3 = abs_x, abs_y, abs_x, abs_y
            elif last_letter in "qt":
                x2 += x1
                y2 += y1
            x2 = 2 * abs_x - x2
            y2 = 2 * abs_y - y2
            x1, y1 = abs_x, abs_y
            x3, y3, string = point(surface, string)
            xq1, yq1, xq2, yq2, xq3, yq3 = quadratic_points(
                x1, y1, x2, y2, x3, y3)
            node.vertices.append((0, 0))
            surface.context.curve_to(xq1, yq1, xq2, yq2, xq3, yq3)

        elif letter == "v":
            # Relative vertical line
            y, string = (string + " ").split(" ", 1)
            old_x, old_y = surface.context.get_current_point()
            angle = pi / 2 if size(surface, y, "y") > 0 else -pi / 2
            node.vertices.append((-angle, angle))
            surface.context.rel_line_to(0, size(surface, y, "y"))

        elif letter == "V":
            # Vertical line
            y, string = (string + " ").split(" ", 1)
            old_x, old_y = surface.context.get_current_point()
            angle = pi / 2 if size(surface, y, "y") > 0 else -pi / 2
            node.vertices.append((-angle, angle))
            surface.context.line_to(old_x, size(surface, y, "y"))

        elif letter in "zZ":
            # End of path
            node.vertices.append(None)
            surface.context.close_path()

        if letter not in "zZ":
            node.vertices.append(surface.context.get_current_point())

        string = string.strip()
        last_letter = letter
