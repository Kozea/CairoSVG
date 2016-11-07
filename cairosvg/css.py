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
Handle CSS stylesheets.

"""

import cssselect
import tinycss

from .url import parse_url


def find_stylesheets(tree, url):
    """Find the stylesheets included in ``tree``."""
    # TODO: support contentStyleType on <svg>
    default_type = 'text/css'
    xml_tree = tree.xml_tree
    process = xml_tree.getprevious()
    while process is not None:
        if (getattr(process, 'target', None) == 'xml-stylesheet' and
                process.attrib.get('type', default_type) == 'text/css'):
            href = parse_url(process.attrib.get('href'), url)
            if href:
                href_string = href.geturl()
                stylesheet = tree.css_cache.get(href_string, None)
                if stylesheet is None:
                    stylesheet = tinycss.make_parser().parse_stylesheet_bytes(
                        tree.fetch_url(href))
                    # tree.fetch_url(href, 'css'))
                    tree.css_cache[href_string] = stylesheet
                yield stylesheet
        process = process.getprevious()
    for element in xml_tree.iter():
        # http://www.w3.org/TR/SVG/styling.html#StyleElement
        if (element.tag == 'style' and
                element.get('type', default_type) == 'text/css' and
                element.text):
            # TODO: pass href for relative URLs
            # TODO: support media types
            # TODO: what if <style> has children elements?
            yield tinycss.make_parser().parse_stylesheet(element.text)


def find_stylesheets_rules(tree, stylesheet, url):
    """Find the rules in a stylesheet."""
    for rule in stylesheet.rules:
        if isinstance(rule, tinycss.css21.ImportRule):
            css_url = parse_url(rule.uri, url)
            css_url_string = css_url.geturl()

            # Check if stylesheet is already present and if not fetch it
            stylesheet = tree.css_cache.get(css_url_string, None)
            if stylesheet is None:
                stylesheet = tinycss.make_parser().parse_stylesheet(
                    tree.fetch_url(css_url).decode('utf-8'))
                # tree.fetch_url(css_url, 'css').decode('utf-8'))
                tree.css_cache[css_url_string] = stylesheet

            # Find rules in stylesheet
            for rule in find_stylesheets_rules(tree, stylesheet,
                                               css_url_string):
                yield rule
        if not rule.at_keyword:
            yield rule


def find_style_rules(tree):
    """Find the style rules in ``tree``."""
    for stylesheet in find_stylesheets(tree, tree.url):
        # TODO: warn for each stylesheet.errors
        for rule in find_stylesheets_rules(tree, stylesheet, tree.url):
            yield rule


def get_declarations(rule):
    """Get the declarations in ``rule``."""
    for declaration in rule.declarations:
        # TODO: filter out invalid values
        yield (
            declaration.name,
            declaration.value.as_css(),
            bool(declaration.priority))


def match_selector(rule, tree):
    """Yield the ``(element, specificity)`` in ``tree`` matching ``rule``."""
    selector_list = cssselect.parse(rule.selector.as_css())
    translator = cssselect.GenericTranslator()
    for selector in selector_list:
        if not selector.pseudo_element:
            specificity = selector.specificity()
            for element in tree.xpath(translator.selector_to_xpath(selector)):
                yield element, specificity


def apply_stylesheets(tree):
    """Apply the stylesheet in ``tree`` to ``tree``."""
    style_by_element = {}
    for rule in find_style_rules(tree):
        declarations = list(get_declarations(rule))
        for element, specificity in match_selector(rule, tree.xml_tree):
            style = style_by_element.setdefault(element, {})
            for name, value, important in declarations:
                weight = important, specificity
                if name in style:
                    _old_value, old_weight = style[name]
                    if old_weight > weight:
                        continue
                style[name] = value, weight

    for element, style in style_by_element.items():
        values = [
            '{}: {}'.format(name, value)
            for name, (value, weight) in style.items()]
        element.set('_style', ';'.join(values))
