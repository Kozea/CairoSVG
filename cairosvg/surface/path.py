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
Paths manager.

"""

from math import pi, radians

from .defs import draw_marker
from .helpers import normalize, point, point_angle, quadratic_points, rotate
from .units import size


PATH_LETTERS = "achlmqstvzACHLMQSTVZ"
PATH_TAGS = ("circle", "line", "path", "polyline", "polygon", "rect")


def path(surface, node):
    """Draw a path ``node``."""
    string = node.get("d", "")
    draw_marker(surface, node, "start")

    for letter in PATH_LETTERS:
        string = string.replace(letter, " %s " % letter)

    last_letter = None
    string = normalize(string)

    while string:
        string = string.strip()
        if string.split(" ", 1)[0] in PATH_LETTERS:
            letter, string = (string + " ").split(" ", 1)

        if letter in "aA":
            # Elliptic curve
            x1, y1 = surface.context.get_current_point()
            rx, ry, string = point(surface, string)
            radii_ratio = ry / rx
            rotation, large, sweep, string = string.split(" ", 3)
            rotation = radians(float(rotation))
            large, sweep = bool(int(large)), bool(int(sweep))
            x3, y3, string = point(surface, string)

            if letter == "A":
                # Absolute x3 and y3, convert to relative
                x3 -= x1
                y3 -= y1

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
            node.tangents.extend((-angle1, -angle2))

            # Draw the arc
            surface.context.save()
            surface.context.translate(x1, y1)
            surface.context.rotate(rotation)
            surface.context.scale(1, radii_ratio)
            arc(xc, yc, rx, angle1, angle2)
            surface.context.restore()

        elif letter == "c":
            # Relative curve
            x1, y1, string = point(surface, string)
            x2, y2, string = point(surface, string)
            x3, y3, string = point(surface, string)
            node.tangents.extend((
                point_angle(x2, y2, x1, y1), point_angle(x2, y2, x3, y3)))
            surface.context.rel_curve_to(x1, y1, x2, y2, x3, y3)

        elif letter == "C":
            # Curve
            x1, y1, string = point(surface, string)
            x2, y2, string = point(surface, string)
            x3, y3, string = point(surface, string)
            node.tangents.extend((
                point_angle(x2, y2, x1, y1), point_angle(x2, y2, x3, y3)))
            surface.context.curve_to(x1, y1, x2, y2, x3, y3)

        elif letter == "h":
            # Relative horizontal line
            x, string = string.split(" ", 1)
            angle = 0 if size(surface, x) > 0 else pi
            node.tangents.extend((-angle, angle))
            surface.context.rel_line_to(size(surface, x), 0)

        elif letter == "H":
            # Horizontal line
            x, string = string.split(" ", 1)
            old_x = surface.context.get_current_point()[1]
            angle = 0 if size(surface, x) > old_x else pi
            node.tangents.extend((-angle, angle))
            surface.context.line_to(size(surface, x), old_x)

        elif letter == "l":
            # Relative straight line
            x, y, string = point(surface, string)
            angle = point_angle(0, 0, x, y)
            node.tangents.extend((-angle, angle))
            surface.context.rel_line_to(x, y)

        elif letter == "L":
            # Straight line
            x, y, string = point(surface, string)
            old_x, old_y = surface.context.get_current_point()
            angle = point_angle(old_x, old_y, x, y)
            node.tangents.extend((-angle, angle))
            surface.context.line_to(x, y)

        elif letter == "m":
            # Current point relative move
            x, y, string = point(surface, string)
            surface.context.rel_move_to(x, y)

        elif letter == "M":
            # Current point move
            x, y, string = point(surface, string)
            surface.context.move_to(x, y)

        elif letter == "q":
            # Relative quadratic curve
            # TODO: manage next letter "T"
            # TODO: manage tangents
            string, next_string = string.split("t", 1)
            x1, y1 = 0, 0
            while string:
                x2, y2, string = point(surface, string)
                x3, y3, string = point(surface, string)
                xq1, yq1, xq2, yq2, xq3, yq3 = quadratic_points(
                    x1, y1, x2, y2, x3, y3)
                surface.context.rel_curve_to(xq1, yq1, xq2, yq2, xq3, yq3)
            node.tangents.extend((0, 0))
            string = "t" + next_string

        elif letter == "Q":
            # Quadratic curve
            # TODO: manage next letter "t"
            # TODO: manage tangents
            string, next_string = string.split("T", 1)
            x1, y1 = surface.context.get_current_point()
            while string:
                x2, y2, string = point(surface, string)
                x3, y3, string = point(surface, string)
                xq1, yq1, xq2, yq2, xq3, yq3 = quadratic_points(
                    x1, y1, x2, y2, x3, y3)
                surface.context.curve_to(xq1, yq1, xq2, yq2, xq3, yq3)
            node.tangents.extend((0, 0))
            string = "T" + next_string

        elif letter == "s":
            # Relative smooth curve
            # TODO: manage last_letter in "CS"
            # TODO: manage tangents
            x1 = x3 - x2 if last_letter in "cs" else 0
            y1 = y3 - y2 if last_letter in "cs" else 0
            x2, y2, string = point(surface, string)
            x3, y3, string = point(surface, string)
            node.tangents.extend((
                point_angle(x2, y2, x1, y1), point_angle(x2, y2, x3, y3)))
            surface.context.rel_curve_to(x1, y1, x2, y2, x3, y3)

        elif letter == "S":
            # Smooth curve
            # TODO: manage last_letter in "cs"
            # TODO: manage tangents
            x, y = surface.context.get_current_point()
            x2, y2, string = point(surface, string)
            x1 = x3 if last_letter in "CS" else x
            y1 = y2 if last_letter in "CS" else y
            x3, y3, string = point(surface, string)
            node.tangents.extend((
                point_angle(x2, y2, x1, y1), point_angle(x2, y2, x3, y3)))
            surface.context.curve_to(x1, y1, x2, y2, x3, y3)

        elif letter == "t":
            # Relative quadratic curve end
            # TODO: manage tangents
            x1, y1 = 0, 0
            x2 = 2 * x1 - x2
            y2 = 2 * y1 - y2
            x3, y3, string = point(surface, string)
            xq1, yq1, xq2, yq2, xq3, yq3 = quadratic_points(
                x1, y1, x2, y2, x3, y3)
            node.tangents.extend((0, 0))
            surface.context.rel_curve_to(xq1, yq1, xq2, yq2, xq3, yq3)

        elif letter == "T":
            # Quadratic curve end
            # TODO: manage tangents
            x1, y1 = surface.context.get_current_point()
            x2 = 2 * x1 - x2
            y2 = 2 * y1 - y2
            x3, y3, string = point(surface, string)
            xq1, yq1, xq2, yq2, xq3, yq3 = quadratic_points(
                x1, y1, x2, y2, x3, y3)
            node.tangents.extend((0, 0))
            surface.context.curve_to(xq1, yq1, xq2, yq2, xq3, yq3)

        elif letter == "v":
            # Relative vertical line
            y, string = string.split(" ", 1)
            angle = pi / 2 if size(surface, y) > 0 else -pi / 2
            node.tangents.extend((-angle, angle))
            surface.context.rel_line_to(0, size(surface, y))

        elif letter == "V":
            # Vertical line
            y, string = string.split(" ", 1)
            old_y = surface.context.get_current_point()[0]
            angle = pi / 2 if size(surface, y) > 0 else -pi / 2
            node.tangents.extend((-angle, angle))
            surface.context.line_to(old_y, size(surface, y))

        elif letter in "zZ":
            # End of path
            # TODO: manage tangents
            node.tangents.extend((0, 0))
            surface.context.close_path()

        else:
            # TODO: manage other letters
            raise NotImplementedError

        string = string.strip()

        if string and letter not in "mM":
            draw_marker(surface, node, "mid")

        last_letter = letter

    node.tangents.append(node.tangents[-1])
    draw_marker(surface, node, "end")
