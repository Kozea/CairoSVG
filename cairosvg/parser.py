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

# Fallbacks for Python 2/3
# pylint: disable=E0611,F0401,W0611
from xml.etree import ElementTree
from xml.parsers import expat
# ElementTree's API changed between 2.6 and 2.7
# pylint: disable=C0103
ParseError = getattr(ElementTree, 'ParseError', expat.ExpatError)
# pylint: enable=C0103
HAS_LXML = False

try:
    from urllib import urlopen
    import urlparse
except ImportError:
    from urllib.request import urlopen
    from urllib import parse as urlparse  # Python 3
# pylint: enable=E0611,F0401,W0611


import re
import gzip
import uuid
import os.path

import cssselect2

from . import css
from .features import match_features
from .surface.helpers import urls, rotations, pop_rotation, flatten


# Python 2/3 compat
# pylint: disable=C0103,W0622
try:
    basestring
except NameError:
    basestring = str
# pylint: enable=C0103,W0622


def handle_white_spaces(string, preserve):
    """Handle white spaces in text nodes."""
    # http://www.w3.org/TR/SVG/text.html#WhiteSpace
    if not string:
        return ""
    if preserve:
        string = re.sub("[\n\r\t]", " ", string)
    else:
        string = re.sub("[\n\r]", "", string)
        string = re.sub("\t", " ", string)
        string = re.sub(" +", " ", string)
    return string


class Node(dict):
    """SVG node with dict-like properties and children."""
    def __init__(self, element, style, parent, parent_children=False,
                 url=None):
        """Create the Node from ElementTree ``node``, with ``parent`` Node."""
        super(Node, self).__init__()
        self.children = ()

        node = element.etree_element
        self.element = element
        self.style = style
        self.root = False
        self.tag = (
            element.local_name
            if element.namespace_url == 'http://www.w3.org/2000/svg' else
            '{%s}%s' % (element.namespace_url, element.local_name)
        )
        self.text = node.text
        self.node = node

        # Inherits from parent properties
        if parent is not None:
            items = parent.copy()
            not_inherited = (
                "transform", "opacity", "style", "viewBox", "stop-color",
                "stop-opacity", "width", "height", "filter", "mask", "rotate",
                "{http://www.w3.org/1999/xlink}href", "id", "x", "y",
                "overflow", "clip", "clip-path")
            for attribute in not_inherited:
                if attribute in items:
                    del items[attribute]

            self.update(items)
            self.url = url or parent.url
            self.parent = parent
        else:
            self.url = getattr(self, "url", None)
            self.parent = getattr(self, "parent", None)

        self.update(dict(self.node.attrib.items()))

        # Give an id for nodes that don't have one
        if "id" not in self:
            self["id"] = uuid.uuid4().hex

        # Apply CSS rules
        style_attr = node.get('style')
        if style_attr:
            normal_attr, important_attr = css.parse_declarations(style_attr)
        else:
            normal_attr = []
            important_attr = []
        normal_matcher, important_matcher = style
        for declaration_lists in (
            normal_matcher.match(element),
            [normal_attr],
            important_matcher.match(element),
            [important_attr],
        ):
            for declarations in declaration_lists:
                for name, value in declarations:
                    self[name] = value.strip()

        # Replace currentColor by a real color value
        color_attributes = (
            "fill", "stroke", "stop-color", "flood-color",
            "lighting-color")
        for attribute in color_attributes:
            if self.get(attribute) == "currentColor":
                self[attribute] = self.get("color", "black")

        # Replace inherit by the parent value
        for attribute, value in dict(self).items():
            if value == "inherit":
                if parent is not None and attribute in parent:
                    self[attribute] = parent.get(attribute)
                else:
                    del self[attribute]

        # Manage text by creating children
        if self.tag in ("text", "textPath", "a"):
            self.children, _ = self.text_children(element, True, True)

        if parent_children:
            self.children = [Node(child.element, style, parent=self)
                             for child in parent.children]
        elif not self.children:
            self.children = []
            for child in element.iter_children():
                if match_features(child.etree_element):
                    self.children.append(Node(child, style, self))
                    if self.tag == "switch":
                        break

    def text_children(self, element, trailing_space, text_root=False):
        """Create children and return them."""
        children = []
        space = "{http://www.w3.org/XML/1998/namespace}space"
        preserve = self.get(space) == "preserve"
        self.text = handle_white_spaces(element.etree_element.text, preserve)
        if trailing_space and not preserve:
            self.text = self.text.lstrip(" ")
        original_rotate = rotations(self)
        rotate = list(original_rotate)
        if original_rotate:
            pop_rotation(self, original_rotate, rotate)
        if self.text:
            trailing_space = self.text.endswith(" ")
        for child_element in element.iter_children():
            child = child_element.etree_element
            if child.tag == "{http://www.w3.org/2000/svg}tref":
                href = child.get("{http://www.w3.org/1999/xlink}href")
                tree_urls = urls(href)
                url = tree_urls[0] if tree_urls else None
                child_tree = Tree(url=url, parent=self)
                child_tree.clear()
                child_tree.update(self)
                child_node = Node(
                    child_element, self.style, parent=child_tree,
                    parent_children=True)
                child_node.tag = "tspan"
                # Retrieve the referenced node and get its flattened text
                # and remove the node children.
                child = child_tree.xml_tree
                child.text = flatten(child)
            else:
                child_node = Node(child_element, self.style, parent=self)
            child_preserve = child_node.get(space) == "preserve"
            child_node.text = handle_white_spaces(child.text, child_preserve)
            child_node.children, trailing_space = \
                child_node.text_children(child_element, trailing_space)
            trailing_space = child_node.text.endswith(" ")
            if original_rotate and "rotate" not in child_node:
                pop_rotation(child_node, original_rotate, rotate)
            children.append(child_node)
            if child.tail:
                anonymous = Node(
                    cssselect2.ElementWrapper.from_xml_root(
                        ElementTree.Element("tspan")),
                    self.style, parent=self)
                anonymous.text = handle_white_spaces(child.tail, preserve)
                if original_rotate:
                    pop_rotation(anonymous, original_rotate, rotate)
                if trailing_space and not preserve:
                    anonymous.text = anonymous.text.lstrip(" ")
                if anonymous.text:
                    trailing_space = anonymous.text.endswith(" ")
                children.append(anonymous)

        if text_root and not children and not preserve:
            self.text = self.text.rstrip(" ")

        return children, trailing_space


class Tree(Node):
    """SVG tree."""
    def __new__(cls, **kwargs):
        tree_cache = kwargs.get("tree_cache")
        if tree_cache:
            if "url" in kwargs:
                url_parts = kwargs["url"].split("#", 1)
                if len(url_parts) == 2:
                    url, element_id = url_parts
                else:
                    url, element_id = url_parts[0], None
                parent = kwargs.get("parent")
                if parent and not url:
                    url = parent.url
                if (url, element_id) in tree_cache:
                    cached_tree = tree_cache[(url, element_id)]
                    new_tree = Node(
                        cached_tree.element, cached_tree.style, parent)
                    new_tree.xml_tree = cached_tree.xml_tree
                    new_tree.url = url
                    new_tree.tag = cached_tree.tag
                    new_tree.root = True
                    return new_tree
        return dict.__new__(cls)

    def __init__(self, **kwargs):
        """Create the Tree from SVG ``text``."""
        if getattr(self, "xml_tree", None) is not None:
            # The tree has already been parsed
            return

        # Make the parameters keyword-only:
        bytestring = kwargs.pop("bytestring", None)
        file_obj = kwargs.pop("file_obj", None)
        url = kwargs.pop("url", None)
        parent = kwargs.pop("parent", None)
        parent_children = kwargs.pop("parent_children", None)
        tree_cache = kwargs.pop("tree_cache", None)
        element_id = None

        if bytestring is not None:
            tree = ElementTree.fromstring(bytestring)
            self.url = url
        elif file_obj is not None:
            tree = ElementTree.parse(file_obj).getroot()
            if url:
                self.url = url
            else:
                self.url = getattr(file_obj, "name", None)
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
            if url:
                if url[1:3] == ":\\":
                    input_ = url  # win absolute filename
                elif urlparse.urlparse(url).scheme:
                    input_ = urlopen(url)
                else:
                    input_ = url  # filename
                if url.lower().endswith(".svgz"):
                    input_ = gzip.open(url)
                tree = ElementTree.parse(input_).getroot()
            else:
                root_parent = parent
                while root_parent.parent:
                    root_parent = root_parent.parent
                tree = root_parent.xml_tree
        else:
            raise TypeError(
                "No input. Use one of bytestring, file_obj or url.")
        self.xml_tree = tree
        root = cssselect2.ElementWrapper.from_xml_root(tree)
        style = parent.style if parent else css.parse_stylesheets(tree, url)
        if element_id:
            for element in root.iter_subtree():
                if element.id == element_id:
                    root = element
                    self.xml_tree = element.etree_element
                    break
            else:
                raise TypeError(
                    'No tag with id="%s" found.' % element_id)
        super(Tree, self).__init__(root, style, parent, parent_children, url)
        self.root = True
        if tree_cache is not None and url is not None:
            tree_cache[(self.url, self["id"])] = self
