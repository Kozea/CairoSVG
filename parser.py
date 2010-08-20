# -*- coding: utf-8 -*-
# This file is part of CairoSVG
# Copyright © 2010 Kozea
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
SVG Parser

"""

from xml.etree import ElementTree


class Node(dict):
    """SVG node with dict-like properties and children."""
    def __init__(self, node, parent=None):
        """Create the Node from ElementTree ``node``, with ``parent`` Node."""
        # Inherits from parent properties
        # TODO: use inheritence for some properties only
        if parent:
            items = dict(parent.items())
            for attribute in ("transform", ):
                if attribute in items:
                    del items[attribute]
            self.update(items)

        self.tag = node.tag.split("}", 1)[1] if "}" in node.tag else node.tag
        self.text = node.text
        self.update(node.attrib.items())
        self.children = tuple(Node(child, self) for child in node)


class Tree(Node):
    """SVG tree."""
    def __init__(self, text):
        """Create the Tree from SVG ``text``."""
        tree = ElementTree.fromstring(text)
        super(Tree, self).__init__(tree)
