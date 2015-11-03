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
Utils dealing with URLs.

"""

import re
from urllib import parse, request

from . import VERSION


HTTP_HEADERS = {
    'User-Agent': 'CairoSVG {}'.format(VERSION),
    'Accept-Encoding': 'gzip, deflate',
}


def url(string):
    """Parse a ``url()`` string."""
    if string:
        match = re.search(r'url\((.+)\)', string)
        if match:
            string = match.group(1)
    return parse.urlparse(string or '')


def urlopen(url):
    """Get a file-like object corresponding to the given ``url``."""
    return request.urlopen(request.Request(url, headers=HTTP_HEADERS))
