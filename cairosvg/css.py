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


from .parser import HAS_LXML

try:
    import cssutils
    HAS_CSSUTILS = True
except ImportError:
    HAS_CSSUTILS = False

try:
    from lxml import cssselect
    HAS_CSSSELECT = True
except ImportError:
    HAS_CSSSELECT = False


CSS_CAPABLE = HAS_LXML and HAS_CSSUTILS and HAS_CSSSELECT


def remove_svg_namespace(tree):
    """
    lxml.cssselect does not support empty/default namespaces, so remove
    any SVG namespace.
    """
    prefix = '{http://www.w3.org/2000/svg}'
    prefix_len = len(prefix)
    for element in tree.iter():
        if element.tag.startswith(prefix):
            element.tag = element.tag[prefix_len:]


def find_stylesheets(tree):
    for element in tree.iter():
        # http://www.w3.org/TR/SVG/styling.html#StyleElement
        if (element.tag == 'style' and
                # TODO: support contentStyleType on <svg>
                element.get('type', 'text/css') == 'text/css'):
            # TODO: pass href for relative URLs
            yield cssutils.parseString(element.text, validate=False)


def find_style_rules(tree):
    for stylesheet in find_stylesheets(tree):
        for rule in stylesheet.cssRules:
            if rule.type == rule.STYLE_RULE:
                yield rule


def get_declarations(rule):
    for declaration in rule.style.getProperties(all=True):
        if declaration.name.startswith('-'):
            continue
        # TODO: filter out invalid values
        yield declaration.name, declaration.cssText


def match_selector(rule, tree):
    for selector in rule.selectorList:
        specificity = selector.specificity
        try:
            matcher = cssselect.CSSSelector(selector.selectorText)
        except cssselect.ExpressionError:
            # Unsupported selector
            # TODO: warn
            continue
        for element in matcher(tree):
            yield element, specificity


def apply_stylesheets(tree):
    if not CSS_CAPABLE:
        # TODO: warn?
        return
    remove_svg_namespace(tree)
    style_by_element = {}
    for rule in find_style_rules(tree):
        declarations = list(get_declarations(rule))
        for element, specificity in match_selector(rule, tree):
            style = style_by_element.setdefault(element, {})
            for name, value in declarations:
                if name in style:
                    _old_value, old_specificity = style[name]
                    if old_specificity > specificity:
                        continue
                style[name] = value, specificity

    for element, style in style_by_element.iteritems():
        values = [v for v, _ in style.itervalues()]
        values.append(element.get('style', ''))
        element.set('style', ';'.join(values))
