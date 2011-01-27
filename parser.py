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

import os
from xml.etree import ElementTree


class Node(dict):
    """SVG node with dict-like properties and children."""
    def __init__(self, node, parent=None):
        """Create the Node from ElementTree ``node``, with ``parent`` Node."""
        super(Node, self).__init__()
        self.filename = None

        # Inherits from parent properties
        if parent:
            items = parent.copy()
            for attribute in ("transform", ):
                if attribute in items:
                    del items[attribute]

            # Don't inherit x and y attributes if node is a tspan
            # TODO: drop other attributes that should not be inherited
            if node.tag == "tspan":
                if "x" in items:
                    del items["x"]
                if "y" in items:
                    del items["y"]

            self.update(items)
            self.filename = parent.filename

        self.root = False
        self.tag = node.tag.split("}", 1)[1] if "}" in node.tag else node.tag
        self.text = node.text
        self.update(node.attrib.items())
        self.children = tuple(Node(child, self) for child in node)


class Tree(Node):
    """SVG tree."""
    def __init__(self, text_or_url, parent=None):
        """Create the Tree from SVG ``text``."""
        try:
            tree = ElementTree.fromstring(text_or_url)
        except:
            if "#" in text_or_url:
                filename, element_id = text_or_url.split("#")
            else:
                filename, element_id = text_or_url, None
            if parent and parent.filename:
                filename = os.path.join(
                    os.path.dirname(parent.filename), filename)
            with open(filename) as file_descriptor:
                tree = ElementTree.fromstring(file_descriptor.read())
            if element_id:
                for element in tree:
                    if element.get("id") == element_id:
                        tree = element
                        break
            self.filename = filename
        super(Tree, self).__init__(tree, parent)
        self.root = True
