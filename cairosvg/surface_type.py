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
Cairo surface types.

"""

import abc
import cairo
import os

from . import surface


class MultipageSurface(surface.Surface):
    """Cairo abstract surface managing multi-page outputs.

    Classes overriding :class:`MultipageSurface` must have a ``surface_class``
    class attribute corresponding to the cairo surface class.

    """
    __metaclass__ = abc.ABCMeta
    surface_class = NotImplementedError

    def _create_surface(self, tree):
        width, height, viewbox = surface.node_format(tree)
        if "svg" in tuple(child.tag for child in tree.children):
            # Real svg pages are in this root svg tag, create a fake surface
            self.context = cairo.Context(
                self.surface_class(os.devnull, width, height))
        else:
            self.cairo = self.surface_class(self.bytesio, width, height)
            self.context = cairo.Context(self.cairo)
            self._set_context_size(width, height, viewbox)
            self.cairo.set_size(width, height)
            self.context.move_to(0, 0)

    def svg(self, node):
        """Draw a svg ``node`` with multi-page support."""
        if not node.root:
            width, height, viewbox = surface.node_format(node)
            if self.cairo:
                self.cairo.show_page()
            else:
                self.context.restore()
                self.cairo = surface_class(self.bytesio, width, height)
                self.context = cairo.Context(self.cairo)
                self.context.save()
            self._set_context_size(width, height, viewbox)
            self.cairo.set_size(width, height)


class PDFSurface(MultipageSurface):
    """Cairo PDF surface."""
    surface_class = cairo.PDFSurface


class PSSurface(MultipageSurface):
    """Cairo PostScript surface."""
    surface_class = cairo.PSSurface


class PNGSurface(surface.Surface):
    """Cairo PNG surface."""
    def _create_surface(self, tree):
        width, height, viewbox = surface.node_format(tree)
        self.cairo = cairo.ImageSurface(
            cairo.FORMAT_ARGB32, int(width), int(height))
        self.context = cairo.Context(self.cairo)
        self._set_context_size(width, height, viewbox)
        self.context.move_to(0, 0)

    def read(self):
        """Read the PNG surface content."""
        self.cairo.write_to_png(self.bytesio)
        return super(PNGSurface, self).read()
