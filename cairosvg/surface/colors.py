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
SVG colors.

"""


COLORS = {  # Taken from Inkscape
    "black": "#000000",
    "dimgray": "#696969",
    "gray": "#808080",
    "darkgray": "#A9A9A9",
    "silver": "#C0C0C0",
    "lightgray": "#D3D3D3",
    "gainsboro": "#DCDCDC",
    "whitesmoke": "#F5F5F5",
    "white": "#FFFFFF",
    "rosybrown": "#BC8F8F",
    "indianred": "#CD5C5C",
    "brown": "#A52A2A",
    "firebrick": "#B22222",
    "lightcoral": "#F08080",
    "maroon": "#800000",
    "darkred": "#8B0000",
    "red": "#FF0000",
    "snow": "#FFFAFA",
    "mistyrose": "#FFE4E1",
    "salmon": "#FA8072",
    "tomato": "#FF6347",
    "darksalmon": "#E9967A",
    "coral": "#FF7F50",
    "orangered": "#FF4500",
    "lightsalmon": "#FFA07A",
    "sienna": "#A0522D",
    "seashell": "#FFF5EE",
    "chocolate": "#D2691E",
    "saddlebrown": "#8B4513",
    "sandybrown": "#F4A460",
    "peachpuff": "#FFDAB9",
    "peru": "#CD853F",
    "linen": "#FAF0E6",
    "bisque": "#FFE4C4",
    "darkorange": "#FF8C00",
    "burlywood": "#DEB887",
    "tan": "#D2B48C",
    "antiquewhite": "#FAEBD7",
    "navajowhite": "#FFDEAD",
    "blanchedalmond": "#FFEBCD",
    "papayawhip": "#FFEFD5",
    "moccasin": "#FFE4B5",
    "orange": "#FFA500",
    "wheat": "#F5DEB3",
    "oldlace": "#FDF5E6",
    "floralwhite": "#FFFAF0",
    "darkgoldenrod": "#B8860B",
    "goldenrod": "#DAA520",
    "cornsilk": "#FFF8DC",
    "gold": "#FFD700",
    "khaki": "#F0E68C",
    "lemonchiffon": "#FFFACD",
    "palegoldenrod": "#EEE8AA",
    "darkkhaki": "#BDB76B",
    "beige": "#F5F5DC",
    "lightgoldenrodyellow": "#FAFAD2",
    "olive": "#808000",
    "yellow": "#FFFF00",
    "lightyellow": "#FFFFE0",
    "ivory": "#FFFFF0",
    "olivedrab": "#6B8E23",
    "yellowgreen": "#9ACD32",
    "darkolivegreen": "#556B2F",
    "greenyellow": "#ADFF2F",
    "chartreuse": "#7FFF00",
    "lawngreen": "#7CFC00",
    "darkseagreen": "#8FBC8F",
    "forestgreen": "#228B22",
    "limegreen": "#32CD32",
    "lightgreen": "#90EE90",
    "palegreen": "#98FB98",
    "darkgreen": "#006400",
    "green": "#008000",
    "lime": "#00FF00",
    "honeydew": "#F0FFF0",
    "seagreen": "#2E8B57",
    "mediumseagreen": "#3CB371",
    "springgreen": "#00FF7F",
    "mintcream": "#F5FFFA",
    "mediumspringgreen": "#00FA9A",
    "mediumaquamarine": "#66CDAA",
    "aquamarine": "#7FFFD4",
    "turquoise": "#40E0D0",
    "lightseagreen": "#20B2AA",
    "mediumturquoise": "#48D1CC",
    "darkslategray": "#2F4F4F",
    "paleturquoise": "#AFEEEE",
    "teal": "#008080",
    "darkcyan": "#008B8B",
    "cyan": "#00FFFF",
    "lightcyan": "#E0FFFF",
    "azure": "#F0FFFF",
    "darkturquoise": "#00CED1",
    "cadetblue": "#5F9EA0",
    "powderblue": "#B0E0E6",
    "lightblue": "#ADD8E6",
    "deepskyblue": "#00BFFF",
    "skyblue": "#87CEEB",
    "lightskyblue": "#87CEFA",
    "steelblue": "#4682B4",
    "aliceblue": "#F0F8FF",
    "dodgerblue": "#1E90FF",
    "slategray": "#708090",
    "lightslategray": "#778899",
    "lightsteelblue": "#B0C4DE",
    "cornflowerblue": "#6495ED",
    "royalblue": "#4169E1",
    "midnightblue": "#191970",
    "lavender": "#E6E6FA",
    "navy": "#000080",
    "darkblue": "#00008B",
    "mediumblue": "#0000CD",
    "blue": "#0000FF",
    "ghostwhite": "#F8F8FF",
    "slateblue": "#6A5ACD",
    "darkslateblue": "#483D8B",
    "mediumslateblue": "#7B68EE",
    "mediumpurple": "#9370DB",
    "blueviolet": "#8A2BE2",
    "indigo": "#4B0082",
    "darkorchid": "#9932CC",
    "darkviolet": "#9400D3",
    "mediumorchid": "#BA55D3",
    "thistle": "#D8BFD8",
    "plum": "#DDA0DD",
    "violet": "#EE82EE",
    "purple": "#800080",
    "darkmagenta": "#8B008B",
    "magenta": "#FF00FF",
    "orchid": "#DA70D6",
    "mediumvioletred": "#C71585",
    "deeppink": "#FF1493",
    "hotpink": "#FF69B4",
    "lavenderblush": "#FFF0F5",
    "palevioletred": "#DB7093",
    "crimson": "#DC143C",
    "pink": "#FFC0CB",
    "lightpink": "#FFB6C1"}


def color(string=None, opacity=1):
    """Replace ``string`` representing a color by a RGBA tuple."""
    if not string or string == "none":
        return (0, 0, 0, 0)

    string = string.strip().lower()

    if string.startswith("rgba"):
        r, g, b, a = tuple(
            float(i) for i in string.strip(" rgba()").split(","))
        return r, g, b, a * opacity
    elif string.startswith("rgb"):
        r, g, b = tuple(float(i) for i in string.strip(" rgb()").split(","))
        return r, g, b, opacity

    if string in COLORS:
        string = COLORS[string]

    if len(string) in (4, 5):
        string = "#" + "".join(2 * char for char in string[1:])
    if len(string) == 9:
        opacity *= int(string[7:9], 16) / 255

    plain_color = tuple(
        int(value, 16) / 255. for value in (
            string[1:3], string[3:5], string[5:7]))
    return plain_color + (opacity,)
