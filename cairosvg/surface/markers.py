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
Markers drawers.

"""

from math import radians

from .helpers import node_format, preserve_ratio, urls
from .units import size


def draw_marker(surface, node, position="mid"):
    """Draw a marker."""
    # TODO: manage markers for other tags than path
    if position == "start":
        node.markers = {
            "start": list(urls(node.get("marker-start", ""))),
            "mid": list(urls(node.get("marker-mid", ""))),
            "end": list(urls(node.get("marker-end", "")))}
        all_markers = list(urls(node.get("marker", "")))
        for markers_list in node.markers.values():
            markers_list.extend(all_markers)
    pending_marker = (
        surface.context.get_current_point(), node.markers[position])

    if position == "start":
        node.pending_markers.append(pending_marker)
        return
    elif position == "end":
        node.pending_markers.append(pending_marker)

    while node.pending_markers:
        next_point, markers = node.pending_markers.pop(0)

        if node.tangents != []:
            angle1 = node.tangents.pop(0)
        if node.tangents != []:
            angle2 = node.tangents.pop(0)

        for marker in markers:
            if not marker.startswith("#"):
                continue
            marker = marker[1:]
            if marker in surface.markers:
                marker_node = surface.markers[marker]

                angle = marker_node.get("orient", "0")
                if angle == "auto":
                    if angle1 is None:
                        angle1 = angle2
                    angle = float(angle1 + angle2) / 2
                else:
                    angle = radians(float(angle))

                temp_path = surface.context.copy_path()
                current_x, current_y = next_point

                if node.get("markerUnits") == "userSpaceOnUse":
                    base_scale = 1
                else:
                    base_scale = size(surface.parent_node.get("stroke-width"))

                # Returns 4 values
                scale_x, scale_y, translate_x, translate_y = \
                    preserve_ratio(surface, marker_node)

                viewbox = node_format(marker_node)[-1]
                viewbox_width = viewbox[2] - viewbox[0]
                viewbox_height = viewbox[3] - viewbox[1]

                surface.context.new_path()
                for child in marker_node.children:
                    surface.context.save()
                    surface.context.translate(current_x, current_y)
                    surface.context.rotate(angle)
                    surface.context.scale(
                        base_scale / viewbox_width * float(scale_x),
                        base_scale / viewbox_height * float(scale_y))
                    surface.context.translate(translate_x, translate_y)
                    surface.draw(child)
                    surface.context.restore()
                surface.context.append_path(temp_path)

    if position == "mid":
        node.pending_markers.append(pending_marker)


def marker(surface, node):
    """Store a marker definition."""
    surface._parse_def(node)
