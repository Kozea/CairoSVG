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

import os.path
import re
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

from . import __version__


HTTP_HEADERS = {'User-Agent': 'CairoSVG {}'.format(__version__)}

URL = re.compile(r'url\((.+)\)')


class URLFetcher(object):
    """Default implementation for URLFetcher.

    It will retrieve many scheme's by default like ftp, http, file and data.
    No specific restrictions (for size or location) will be applied.
    Subclass this class to implement restrictions or implement custom schemes
    (protocols).
    """

    def fetch(self, url):
        """Fetch the content of ``url``.

        Validates the URL before fetching the content.
        """
        self.__validate_url(url)
        return self.__read_url(url)

    def fetcher_for(self, url):
        """Answer URLFetcher to handle ``url``.

        Default implementation: answer self (ie all fetchers are same).

        Override this method to handle specific resource types (like images or
        CSSs) specifically. It may also be used to handle 'child' elements
        specifically.
        """
        return self

    def __validate_url(self, url):
        """Validate ``url`` and raise Error if url is invalid.

        Default implementation: accept all URLs.

        Override this method in a subclass for validating URLs.
        """
        return

    def __open_url(self, url):
        """Open ``url`` and answer instance which supports ``read()`` protocol.

        Default implementation: open URL using urllib.request.urlopen.

        Override this method in a subclass for opening URLs.
        If ``__read_url()`` is also overridden, this method might not be used
        anymore.
        """
        return urlopen(Request(url, headers=HTTP_HEADERS))

    def __read_url(self, url):
        """Read the content of ``url``.

        Default implementation: read URL response from urllib.response.

        Override this method in a subclass for reading the content of URLs.
        """
        return self.__open_url(url).read()


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
                    # We are sure that `url` and `base` are both file-like URLs
                    if os.path.isfile(parsed_base.path):
                        if parsed_url.path:
                            # Take the "folder" part of `base`, as
                            # `os.path.join` doesn't strip the file name
                            url = os.path.join(
                                os.path.dirname(parsed_base.path),
                                parsed_url.path)
                        else:
                            url = parsed_base.path
                    elif os.path.isdir(parsed_base.path):
                        if parsed_url.path:
                            url = os.path.join(
                                parsed_base.path, parsed_url.path)
                        else:
                            url = ''
                    else:
                        url = ''
                    if parsed_url.fragment:
                        url = '{}#{}'.format(url, parsed_url.fragment)
            elif parsed_url.scheme in ('', parsed_base.scheme):
                # `urljoin` automatically uses the "folder" part of `base`
                url = urljoin(base, url)
    return urlparse(url or '')


def read_url(url, url_fetcher):
    """Get bytes in a parsed ``url`` using ``url_fetcher``.

    If ``url_fetcher`` is None a default (no limitations) URLFetcher is used.
    """
    if url.scheme:
        url = url.geturl()
    else:
        url = 'file://{}'.format(os.path.abspath(url.geturl()))

    if url_fetcher is None:
        if not hasattr(read_url, 'default_url_fetcher'):
            read_url.default_url_fetcher = URLFetcher()
        url_fetcher = read_url.default_url_fetcher

    return url_fetcher.fetch(url)
