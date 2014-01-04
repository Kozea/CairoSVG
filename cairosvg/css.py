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
Optionally handle CSS stylesheets.

"""

import os

import tinycss2
import cssselect2


def find_stylesheets(tree, url):
    """Find the stylesheets included in ``tree``."""
    # TODO: support contentStyleType on <svg>
    default_type = "text/css"
    # TODO: this only works with lxml:
    process = tree.getprevious() if hasattr(tree, 'getprevious') else None
    while process is not None:
        if (getattr(process, "target", None) == "xml-stylesheet" and
                process.attrib.get("type", default_type) == "text/css"):
            # TODO: handle web URLs
            filename = process.attrib.get("href")
            if filename:
                path = os.path.join(os.path.dirname(url), filename)
                if os.path.isfile(path):
                    with open(path, 'rb') as fd:
                        stylesheet, _ = tinycss2.parse_stylesheet_bytes(
                            fd.read())
                        yield stylesheet
        process = process.getprevious()
    for element in tree.iter():
        # http://www.w3.org/TR/SVG/styling.html#StyleElement
        if (element.tag == "{http://www.w3.org/2000/svg}style"
                and element.get("type", default_type) == "text/css"
                and element.text):
            # TODO: pass href for relative URLs
            # TODO: what if <style> has children elements?
            yield tinycss2.parse_stylesheet(element.text)


def find_stylesheets_rules(stylesheet_rules, url):
    """Find the rules in a stylesheet."""
    for rule in stylesheet_rules:
        if rule.type == 'at-rule':
            if rule.lower_at_keyword == 'import' and rule.content is None:
                # TODO: support media types in @import
                url_token = tinycss2.parse_one_component_value(rule.prelude)
                if url_token.type not in ('string', 'url'):
                    continue
                css_path = os.path.normpath(
                    os.path.join(os.path.dirname(url), url_token.value))
                if not os.path.exists(css_path):
                    continue
                with open(css_path, 'rb') as f:
                    stylesheet, _ = tinycss2.parse_stylesheet_bytes(f.read())
                    for rule in find_stylesheets_rules(stylesheet, css_path):
                        yield rule
            # TODO: support media types
            #if rule.lower_at_keyword == 'media':
        if rule.type == 'qualified-rule':
            yield rule
        # TODO: warn on error
        #if rule.type == 'error':


def parse_declarations(input):
    normal_declarations = []
    important_declarations = []
    for declaration in tinycss2.parse_declaration_list(input):
        # TODO: warn on error
        #if declaration.type == 'error':

        # Ignore vendor-prefixed properties
        # TODO: filter out invalid values
        if (declaration.type == 'declaration'
                and not declaration.name.startswith("-")):
            # Serializing perfectly good tokens just to re-parse them later :(
            value = tinycss2.serialize(declaration.value).strip().lower()
            (
                important_declarations if declaration.important
                else normal_declarations
            ).append((declaration.lower_name, value))
    return normal_declarations, important_declarations


def parse_stylesheets(tree, url):
    """Find and parse the stylesheets in ``tree``.

    Return two :class:`cssselect2.Matcher` objects,
    for normal and !important declarations.

    """
    normal_matcher = cssselect2.Matcher()
    important_matcher = cssselect2.Matcher()
    for stylesheet in find_stylesheets(tree, url):
        for rule in find_stylesheets_rules(stylesheet, url):
            normal_declarations, important_declarations = parse_declarations(
                rule.content)
            for selector in cssselect2.compile_selector_list(rule.prelude):
                if (selector.pseudo_element is None
                        and not selector.never_matches):
                    if normal_declarations:
                        normal_matcher.add_selector(
                            selector, normal_declarations)
                    if important_declarations:
                        important_matcher.add_selector(
                            selector, important_declarations)
    return normal_matcher, important_matcher
