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
Cairo surface types

"""

import os
import cairo

from . import surface


class PDFSurface(surface.Surface):
    """Cairo PDF surface."""
    def _create_surface(self, tree, width, height):
        """Create the surface from ``tree``."""
        if "svg" in tuple(child.tag for child in tree.children):
            # Real svg pages are in this root svg tag, create a fake surface
            self.context = cairo.Context(
                cairo.PDFSurface(os.devnull, width, height))
        else:
            self.cairo = cairo.PDFSurface(self.bytesio, width, height)
            self.context = cairo.Context(self.cairo)
            self._set_context_size(width, height, tree.get("viewBox"))
            self.cairo.set_size(width, height)
            self.context.move_to(0, 0)

    def svg(self, node):
        """Draw a svg ``node`` with multi-page support."""
        if not node.root:
            width = surface.size(node.get("width"))
            height = surface.size(node.get("height"))
            if hasattr(self, "cairo"):
                self.cairo.show_page()
            else:
                self.context.restore()
                self.cairo = cairo.PDFSurface(self.bytesio, width, height)
                self.context = cairo.Context(self.cairo)
                self.context.save()
            self._set_context_size(width, height, node.get("viewBox"))
            self.cairo.set_size(width, height)
