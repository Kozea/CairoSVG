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

import urllib.request

from . import VERSION


HTTP_HEADERS = {
    'User-Agent': 'CairoSVG {}'.format(VERSION),
    'Accept-Encoding': 'gzip, deflate',
}


def urls(string):
    """Parse a comma-separated list of ``url()`` strings."""
    if not string:
        return []

    # TODO: use a real parser
    string = string.strip()
    if string.startswith('url'):
        string = string[3:]
    return [
        link.strip('() \'"') for link in string.rsplit(')')[0].split(',')
        if link.strip('() \'"')]


def urlopen(url):
    """Get a file-like object corresponding to the given ``url``."""
    return urllib.request.urlopen(
        urllib.request.Request(url, headers=HTTP_HEADERS))
