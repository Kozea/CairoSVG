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
SVG Parser.

"""

import os
from xml.etree import ElementTree


class Node(dict):
    """SVG node with dict-like properties and children."""
    def __init__(self, node, parent=None):
        """Create the Node from ElementTree ``node``, with ``parent`` Node."""
        super(Node, self).__init__()
        self.children = ()

        self.root = False
        self.tag = node.tag.split("}", 1)[-1]
        self.text = node.text

        # Inherits from parent properties
        if parent is not None:
            items = parent.copy()
            not_inherited = ("transform", )
            if self.tag == 'tspan':
                not_inherited += ('x', 'y')
            for attribute in not_inherited:
                if attribute in items:
                    del items[attribute]

            # TODO: drop other attributes that should not be inherited

            self.update(items)
            self.filename = parent.filename
            self.parent = parent

        # TODO: manage other attributes that should be multiplicated
        properties = dict(node.attrib.items())
        for key in properties:
            if "opacity" in key:
                if parent is not None:
                    properties[key] = str(
                        float(parent.get(key, 1.0)) * float(properties[key]))
        self.update(properties)

        # manage text by creating children
        if self.tag == "text" or self.tag == "textPath":
            self.children = self.text_children(node)

        if not self.children:
            self.children = tuple(Node(child, self) for child in node)


    def text_children(self, node):
        """Create children and return them."""
        children = []

        for child in (node):
            children.append(Node(child, parent=self))
            if child.tail:
                anonymous = ElementTree.Element('tspan')
                anonymous.text = child.tail
                children.append(Node(anonymous, parent=self))

        return list(children)

class Tree(Node):
    """SVG tree."""
    def __init__(self, text_or_url, parent=None):
        """Create the Tree from SVG ``text``."""
        try:
            tree = ElementTree.fromstring(text_or_url)
            self.filename = None
        except ElementTree.ParseError:
            if "#" in text_or_url:
                filename, element_id = text_or_url.split("#")
            else:
                filename, element_id = text_or_url, None
            if parent and parent.filename:
                if filename:
                    filename = os.path.join(
                        os.path.dirname(parent.filename), filename)
                else:
                    filename = parent.filename
            with open(filename) as file_descriptor:
                tree = ElementTree.fromstring(file_descriptor.read())
            if element_id:
                for element in tree.iter():
                    if element.get("id") == element_id:
                        tree = element
                        break
            self.filename = filename
        super(Tree, self).__init__(tree, parent)
        self.root = True
