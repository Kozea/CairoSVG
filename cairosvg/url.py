# This file is part of CairoSVG
# Copyright © 2010-2018 Kozea
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

import os.path
import re
from pathlib import Path
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

from . import VERSION

HTTP_HEADERS = {'User-Agent': 'CairoSVG {}'.format(VERSION)}

URL = re.compile(r'url\((.+)\)')


def normalize_url(url):
    """Normalize ``url`` for underlying NT/Unix operating systems.

    The input ``url`` may look like the following:

        - C:\\Directory\\zzz.svg
        - file://C:\\Directory\\zzz.svg
        - zzz.svg

    The output ``url`` on NT systems would look like below:

        - file:///C:/Directory/zzz.svg

    """
    if url and os.name == 'nt':
        # Match input ``url`` like the following:
        #   - C:\\Directory\\zzz.svg
        #   - Blah.svg
        if 'file:' not in url:
            url = os.path.abspath(url)
            url = Path(url).resolve().as_uri()

        # Match input ``url`` like the following:
        #   - file://C:\\Directory\\zzz.svg
        elif re.match(
                '^file://[a-z]:', url,
                re.IGNORECASE | re.MULTILINE | re.DOTALL):
            url = url.replace('//', '///')
            url = url.replace('\\', '/')

    return url


def nt_compatible_path(path):
    """Provide compatible NT file paths for ``os.path`` functions

    ``os.path`` expects NT paths with no ``/`` at the beginning. For
    example, ``/C:/Directory/zzz.svg`` would fail ``os.path.isfile()``,
    ``os.path.isdir()`` etc. where the expected input for `os.path`
    functions is ``/C:/Directory/zzz.svg``.

    Currently ``nt_compatible_path`` performs some basic checks and
    eliminates the unwanted ``/`` at the beginning.

    """
    if os.name == 'nt' and re.match(
            '^/[a-z]:/', path, re.IGNORECASE | re.MULTILINE | re.DOTALL):
        return re.sub('^/', '', path, re.IGNORECASE | re.MULTILINE | re.DOTALL)
    else:
        return path


def fetch(url, resource_type):
    """Fetch the content of ``url``.

    ``resource_type`` is the mimetype of the resource (currently one of
    image/*, image/svg+xml, text/css).

    """
    return urlopen(Request(url, headers=HTTP_HEADERS)).read()


def parse_url(url, base=None):
    """Parse an URL.

    The URL can be surrounded by a ``url()`` string. If ``base`` is not `None`,
    the "folder" part of it is prepended to the URL.

    """
    if url:
        match = URL.search(url)
        if match:
            url = match.group(1)
        if base:
            parsed_base = urlparse(base)
            parsed_url = urlparse(url)
            if parsed_base.scheme in ('', 'file'):
                if parsed_url.scheme in ('', 'file'):
                    parsed_base_path = nt_compatible_path(parsed_base.path)
                    parsed_url_path = nt_compatible_path(parsed_url.path)
                    # We are sure that `url` and `base` are both file-like URLs
                    if os.path.isfile(parsed_base_path):
                        if parsed_url_path:
                            # Take the "folder" part of `base`, as
                            # `os.path.join` doesn't strip the file name
                            url = os.path.join(
                                os.path.dirname(parsed_base_path),
                                parsed_url_path)
                        else:
                            url = parsed_base_path
                    elif os.path.isdir(parsed_base_path):
                        if parsed_url_path:
                            url = os.path.join(
                                parsed_base_path, parsed_url_path)
                        else:
                            url = ''
                    else:
                        url = ''
                    if parsed_url.fragment:
                        url = '{}#{}'.format(url, parsed_url.fragment)
            elif parsed_url.scheme in ('', parsed_base.scheme):
                # `urljoin` automatically uses the "folder" part of `base`
                url = urljoin(base, url)
        url = normalize_url(url.strip('\'"'))
    return urlparse(url or '')


def read_url(url, url_fetcher, resource_type):
    """Get bytes in a parsed ``url`` using ``url_fetcher``.

    If ``url_fetcher`` is None a default (no limitations) URLFetcher is used.
    """
    if url.scheme:
        url = url.geturl()
    else:
        url = 'file://{}'.format(os.path.abspath(url.geturl()))
        url = normalize_url(url)

    return url_fetcher(url, resource_type)
