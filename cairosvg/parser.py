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
SVG Parser.

"""

from xml.etree import ElementTree
from xml.parsers import expat

# Python 2/3 magic imports
# pylint: disable=E0611,F0401
try:
    from urllib import urlopen
    import urlparse
except ImportError:
    from urllib.request import urlopen
    from urllib import parse as urlparse  # Python 3
# pylint: enable=E0611,F0401


# ElementTree's API changed between 2.6 and 2.7
# pylint: disable=C0103
ParseError = getattr(ElementTree, 'ParseError', expat.ExpatError)
# pylint: enable=C0103


class Node(dict):
    """SVG node with dict-like properties and children."""
    def __init__(self, node, parent=None):
        """Create the Node from ElementTree ``node``, with ``parent`` Node."""
        super(Node, self).__init__()
        self.children = ()

        self.root = False
        self.tag = node.tag.split("}", 1)[-1]
        self.text = node.text

        # Handle the CSS
        style = node.attrib.get("style")
        if style:
            for attribute in style.split(";"):
                if ":" in attribute:
                    name, value = attribute.split(":", 1)
                    node.attrib[name.strip()] = value.strip()
            del node.attrib["style"]

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
            self.url = parent.url
            self.parent = parent

        # TODO: manage other attributes that should be multiplicated
        # TODO: handle opacity the right way (no transparency between plain
        # elements in a semi-transparent parent)
        properties = dict(node.attrib.items())
        for key in properties:
            if "opacity" in key:
                if parent is not None:
                    properties[key] = str(
                        float(parent.get(key, 1.0)) * float(properties[key]))
        self.update(properties)

        # Manage text by creating children
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
    def __init__(self, **kwargs):
        """Create the Tree from SVG ``text``."""
        # Make the parameters keyword-only:
        bytestring = kwargs.pop('bytestring', None)
        file_obj = kwargs.pop('file_obj', None)
        url = kwargs.pop('url', None)
        parent = kwargs.pop('parent', None)
        if kwargs:
            raise TypeError('Unexpected arguments', kwargs.keys())

        if bytestring is not None:
            tree = ElementTree.fromstring(bytestring)
            self.url = None
        elif url is not None:
            if "#" in url:
                url, element_id = url.split("#", 1)
            else:
                element_id = None
            if parent and parent.url:
                if url:
                    url = urlparse.urljoin(parent.url, url)
                elif element_id:
                    url = parent.url
            self.url = url
            if urlparse.urlparse(url).scheme:
                input_ = urlopen(url)
            else:
                input_ = url  # filename
            tree = ElementTree.parse(input_).getroot()
            if element_id:
                iterator = (
                    tree.iter() if hasattr(tree, 'iter')
                    else tree.getiterator())
                for element in iterator:
                    if element.get("id") == element_id:
                        tree = element
                        break
        elif file_obj is not None:
            tree = ElementTree.parse(file_obj).getroot()
            self.url = getattr(file_obj, 'name', url)
        else:
            raise TypeError(
                'No input. Use one of bytestring, file_obj or url.')
        super(Tree, self).__init__(tree, parent)
        self.root = True
