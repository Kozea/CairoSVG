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

import os
import re
from urllib.parse import urlparse, urljoin
from urllib.request import urlopen, Request

from . import VERSION


HTTP_HEADERS = {'User-Agent': 'CairoSVG {}'.format(VERSION)}


def parse_url(url, base=None):
    """Parse an URL.

    The URL can be surrounded by a ``url()`` string. If ``base`` is not `None`,
    it is prepended to the URL.

    """
    if url:
        match = re.search(r'url\((.+)\)', url)
        if match:
            url = match.group(1)
        if base:
            base_scheme = urlparse(base).scheme
            url_scheme = urlparse(url).scheme
            if base_scheme in ('', 'file'):
                if url_scheme in ('', 'file'):
                    url = os.path.join(base, url)
            elif base_scheme == url_scheme:
                url = urljoin(base, url)
    return urlparse(url or '')


def read_url(url):
    """Get bytes in a parsed ``url``."""
    if url.scheme:
        url = url.geturl()
    else:
        url = 'file://{}'.format(os.path.abspath(url.geturl()))
    return urlopen(Request(url, headers=HTTP_HEADERS)).read()
