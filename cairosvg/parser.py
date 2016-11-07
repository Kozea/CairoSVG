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
SVG Parser.

"""

import gzip
import re
from urllib.parse import urlunparse

import lxml.etree as ElementTree

from .css import apply_stylesheets
from .features import match_features
from .helpers import flatten, pop_rotation, rotations
from .url import fetch, parse_url, read_url

# 'display' is actually inherited but handled differently because some markers
# are part of a none-displaying group (see test painting-marker-07-f.svg)
NOT_INHERITED_ATTRIBUTES = frozenset((
    'clip',
    'clip-path',
    'display',
    'filter',
    'height',
    'id',
    'mask',
    'opacity',
    'overflow',
    'rotate',
    'stop-color',
    'stop-opacity',
    'style',
    'transform',
    'viewBox',
    'width',
    'x',
    'y',
    '{http://www.w3.org/1999/xlink}href',
))

COLOR_ATTRIBUTES = frozenset((
    'fill',
    'flood-color',
    'lighting-color',
    'stop-color',
    'stroke',
))


def remove_svg_namespace(tree):
    """Remove the SVG namespace from ``tree`` tags.

    ``lxml.cssselect`` does not support empty/default namespaces, so remove any
    SVG namespace.

    """
    prefix = '{http://www.w3.org/2000/svg}'
    prefix_len = len(prefix)
    for element in tree.iter():
        tag = element.tag
        if hasattr(tag, 'startswith') and tag.startswith(prefix):
            element.tag = tag[prefix_len:]


def handle_white_spaces(string, preserve):
    """Handle white spaces in text nodes.

    See http://www.w3.org/TR/SVG/text.html#WhiteSpace

    """
    if not string:
        return ''
    if preserve:
        return re.sub('[\n\r\t]', ' ', string)
    else:
        string = re.sub('[\n\r]', '', string)
        string = re.sub('\t', ' ', string)
        return re.sub(' +', ' ', string)


def normalize_style_declaration(name, value):
    """Normalize style declaration consisting of name/value pair.

    Names are always case insensitive, make all lowercase.
    Values are case insensitive in most cases. Adapt for 'specials':
        id - case sensitive identifier
        class - case sensitive identifier(s)
        font-family - case sensitive name(s)
        font - shorthand in which font-family is case sensitive
        any declaration with url in value - url is case sensitive

    """
    name = name.strip().lower()
    value = value.strip()
    if name in CASE_SENSITIVE_STYLE_METHODS:
        value = CASE_SENSITIVE_STYLE_METHODS[name](value)
    else:
        value = value.lower()

    return name, value


def normalize_noop_style_declaration(value):
    """No-operation for normalization where value is case sensitive.

    This is actually the exception to the rule. Normally value will be made
    lowercase (see normalize_style_declaration above).

    """
    return value


def normalize_url_style_declaration(value):
    """Normalize style declaration, but keep URL's as-is.

    Lowercase everything except for the URL.

    """
    regex_style = re.compile(r"""
        (.*?)                               # non-URL part (will be normalized)
        (?:
            url\(\s*                        # url(<whitespace>
                (?:
                      "(?:\\.|[^"])*"       # "<url>"
                    | \'(?:\\.|[^\'])*\'    # '<url>'
                    | (?:\\.|[^\)])*        # <url>
                )
            \s*\)                           # <whitespace>)
            |$
        )
    """, re.IGNORECASE | re.VERBOSE)
    for match in regex_style.finditer(value):
        value_start = value[:match.start()] if match.start() > 0 else ''
        normalized_value = match.group(1).lower()
        value_end = value[match.start() + len(normalized_value):]
        value = value_start + normalized_value + value_end
    return value


def normalize_font_style_declaration(value):
    """Make first part of font style declaration lowercase (case insensitive).

    Lowercase first part of declaration. Only the font name is case sensitive.
    The font name is at the end of the declaration and can be 'recognized'
    by being preceded by a size or line height. There can actually be multiple
    names. So the first part is 'calculated' by selecting everything up to and
    including the last valid token followed by a size or line height (both
    starting with a number). A valid token is either a size/length or an
    identifier.

    See http://www.w3.org/TR/css-fonts-3/#font-prop

    """
    return re.sub(r"""
        ^(
            (\d[^\s,]*|\w[^\s,]*)   # <size>, <length> or <identifier>
            (\s+|\s*,\s*)           # <whitespace> and/or comma
        )*                          # Repeat until last
        \d[^\s,]*                   # <size> or <line-height>
    """, lambda match: match.group().lower(), value, 0, re.VERBOSE)


class Node(dict):
    """SVG node with dict-like properties and children."""

    def __init__(self, node, url_fetcher, parent=None, parent_children=False,
                 url=None):
        """Create the Node from ElementTree ``node``, with ``parent`` Node."""
        super().__init__()
        self.children = ()

        self.root = False
        self.tag = node.tag
        self.text = node.text
        self.node = node
        self.url_fetcher = url_fetcher

        # Inherits from parent properties
        if parent is not None:
            self.update([
                (attribute, parent[attribute]) for attribute in parent
                if attribute not in NOT_INHERITED_ATTRIBUTES])
            self.url = url or parent.url
            self.parent = parent
        else:
            self.url = getattr(self, 'url', None)
            self.parent = getattr(self, 'parent', None)

        self.update(self.node.attrib)

        # Handle the CSS
        style = self.pop('_style', '') + ';' + self.pop('style', '')
        for declaration in style.split(';'):
            name, colon, value = declaration.partition(':')
            if not colon:
                continue
            name, value = normalize_style_declaration(name, value)
            self[name] = value

        # Replace currentColor by a real color value
        for attribute in COLOR_ATTRIBUTES:
            if self.get(attribute) == 'currentColor':
                self[attribute] = self.get('color', 'black')

        # Replace inherit by the parent value
        for attribute in [
                attribute for attribute in self
                if self[attribute] == 'inherit']:
            if parent is not None and attribute in parent:
                self[attribute] = parent.get(attribute)
            else:
                del self[attribute]

        # Manage text by creating children
        if self.tag in ('text', 'textPath', 'a'):
            self.children, _ = self.text_children(node, True, True)

        if parent_children:
            self.children = [
                Node(child.node, self.url_fetcher, parent=self)
                for child in parent.children]
        elif not self.children:
            self.children = []
            for child in node:
                if isinstance(child.tag, str):
                    if match_features(child):
                        self.children.append(Node(
                            child, self.url_fetcher, self))
                        if self.tag == 'switch':
                            break

    def fetch_url(self, url, get_child_fetcher=True):
        return read_url(url, self.url_fetcher)

    def text_children(self, node, trailing_space, text_root=False):
        """Create children and return them."""
        children = []
        space = '{http://www.w3.org/XML/1998/namespace}space'
        preserve = self.get(space) == 'preserve'
        self.text = handle_white_spaces(node.text, preserve)
        if trailing_space and not preserve:
            self.text = self.text.lstrip(' ')
        original_rotate = rotations(self)
        rotate = list(original_rotate)
        if original_rotate:
            pop_rotation(self, original_rotate, rotate)
        if self.text:
            trailing_space = self.text.endswith(' ')
        for child in node:
            if child.tag == 'tref':
                url = parse_url(child.get(
                    '{http://www.w3.org/1999/xlink}href')).geturl()
                # No reference to tree or surface here to retrieve css_cache.
                # TODO: decide whether to leave it (ie no caching here) or try
                # to obtain css_cache from one of the parent nodes. The tref
                # tag is not supported in SVG 1.2 or beyond, so usage might be
                # limited.
                child_tree = Tree(
                    url=url, url_fetcher=self.url_fetcher, parent=self)
                child_tree.clear()
                child_tree.update(self)
                child_node = Node(
                    child, self.url_fetcher, parent=child_tree,
                    parent_children=True)
                child_node.tag = 'tspan'
                # Retrieve the referenced node and get its flattened text
                # and remove the node children.
                child = child_tree.xml_tree
                child.text = flatten(child)
            else:
                child_node = Node(child, self.url_fetcher, parent=self)
            child_preserve = child_node.get(space) == 'preserve'
            child_node.text = handle_white_spaces(child.text, child_preserve)
            child_node.children, trailing_space = child_node.text_children(
                child, trailing_space)
            trailing_space = child_node.text.endswith(' ')
            if original_rotate and 'rotate' not in child_node:
                pop_rotation(child_node, original_rotate, rotate)
            children.append(child_node)
            if child.tail:
                anonymous = Node(
                    ElementTree.Element('tspan'), self.url_fetcher,
                    parent=self)
                anonymous.text = handle_white_spaces(child.tail, preserve)
                if original_rotate:
                    pop_rotation(anonymous, original_rotate, rotate)
                if trailing_space and not preserve:
                    anonymous.text = anonymous.text.lstrip(' ')
                if anonymous.text:
                    trailing_space = anonymous.text.endswith(' ')
                children.append(anonymous)

        if text_root and not children and not preserve:
            self.text = self.text.rstrip(' ')

        return children, trailing_space


class Tree(Node):
    """SVG tree."""
    def __new__(cls, **kwargs):
        tree_cache = kwargs.get('tree_cache')
        if tree_cache and kwargs.get('url'):
            parsed_url = parse_url(kwargs['url'])
            element_id = parsed_url.fragment
            parent = kwargs.get('parent')
            if any(parsed_url[:-1]):
                url = urlunparse(parsed_url[:-1] + ('',))
            elif parent:
                url = parent.url
            else:
                url = None
            if url and (url, element_id) in tree_cache:
                cached_tree = tree_cache[(url, element_id)]
                new_tree = Node(
                    cached_tree.xml_tree, cached_tree.url_fetcher, parent)
                new_tree.xml_tree = cached_tree.xml_tree
                new_tree.url = url
                new_tree.tag = cached_tree.tag
                new_tree.root = True
                return new_tree
        return super().__new__(cls)

    def __init__(self, **kwargs):
        """Create the Tree from SVG ``text``."""
        bytestring = kwargs.get('bytestring')
        file_obj = kwargs.get('file_obj')
        url = kwargs.get('url')
        unsafe = kwargs.get('unsafe')
        parent = kwargs.get('parent')
        parent_children = kwargs.get('parent_children')
        tree_cache = kwargs.get('tree_cache')
        element_id = None

        self.url_fetcher = kwargs.get('url_fetcher', fetch)
        self.css_cache = kwargs.get('css_cache', {})

        if bytestring is not None:
            self.url = url
        elif file_obj is not None:
            bytestring = file_obj.read()
            self.url = getattr(file_obj, 'name', None)
        elif url is not None:
            parent_url = parent.url if parent else None
            parsed_url = parse_url(url, parent_url)
            if parsed_url.fragment:
                self.url = urlunparse(parsed_url[:-1] + ('',))
                element_id = parsed_url.fragment
            else:
                self.url = parsed_url.geturl()
                element_id = None
        else:
            raise TypeError(
                'No input. Use one of bytestring, file_obj or url.')
        if parent and self.url and self.url == parent.url:
            root_parent = parent
            while root_parent.parent:
                root_parent = root_parent.parent
            tree = root_parent.xml_tree
        else:
            if not bytestring:
                bytestring = self.fetch_url(parse_url(self.url), False)
            if len(bytestring) >= 2 and bytestring[:2] == b'\x1f\x8b':
                bytestring = gzip.decompress(bytestring)
            parser = ElementTree.XMLParser(
                resolve_entities=unsafe, huge_tree=unsafe)
            tree = ElementTree.fromstring(bytestring, parser)
        remove_svg_namespace(tree)
        self.xml_tree = tree
        apply_stylesheets(self)
        if element_id:
            self.xml_tree = tree.find(".//*[@id='{}']".format(element_id))
            if self.xml_tree is None:
                raise TypeError(
                    'No tag with id="{}" found.'.format(element_id))
        super().__init__(
            self.xml_tree, self.url_fetcher, parent, parent_children, self.url)
        self.root = True
        if tree_cache is not None and self.url:
            tree_cache[(self.url, self.get('id'))] = self


CASE_SENSITIVE_STYLE_METHODS = {
    'id': normalize_noop_style_declaration,
    'class': normalize_noop_style_declaration,
    'font-family': normalize_noop_style_declaration,
    'font': normalize_font_style_declaration,
    'clip-path': normalize_url_style_declaration,
    'color-profile': normalize_url_style_declaration,
    'cursor': normalize_url_style_declaration,
    'fill': normalize_url_style_declaration,
    'filter': normalize_url_style_declaration,
    'marker-start': normalize_url_style_declaration,
    'marker-mid': normalize_url_style_declaration,
    'marker-end': normalize_url_style_declaration,
    'mask': normalize_url_style_declaration,
    'stroke': normalize_url_style_declaration,
}
