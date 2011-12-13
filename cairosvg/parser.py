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
from xml.parsers import expat

ParseError = getattr(ElementTree, 'ParseError', expat.ExpatError)


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
    def __init__(self, file_or_url, parent=None):
        """Create the Tree from SVG ``text``."""
        if hasattr(file_or_url, "read"):
            # file_or_url is a file
            tree = ElementTree.parse(file_or_url).getroot()
            self.filename = getattr(file_or_url, "name", None)
        else:
            # file_or_url is an URL
            if "#" in file_or_url:
                url, element_id = file_or_url.split("#")
            else:
                url, element_id = file_or_url, None
            if parent and parent.filename:
                if url:
                    url = os.path.join(os.path.dirname(parent.filename), url)
                elif element_id:
                    url = parent.filename
            self.filename = url
            tree = ElementTree.parse(url).getroot()
            if element_id:
                iterator = (
                    tree.iter() if hasattr(tree, 'iter')
                    else tree.getiterator())
                for element in iterator:
                    if element.get("id") == element_id:
                        tree = element
                        break
        super(Tree, self).__init__(tree, parent)
        self.root = True
