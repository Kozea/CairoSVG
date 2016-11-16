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

    def fetch(self, url, resource_type):
        """Fetch the content of ``url``.

        ``resource_type`` is the mimetype of the resource (currently one of
        image/*, image/svg+xml, text/css).

        """
        return urlopen(Request(url, headers=HTTP_HEADERS)).read()


class CachingURLFetcher(URLFetcher):

    def __init__(self, resource_type_mask):
        """Initialize the receiver with the specified ``resource_type_mask``"""
        super().__init__()
        self.cached_content, self.cached_format =\
            resource_type_mask.split('/', 1)
        self.cache = {}

    @staticmethod
    def is_data_url(url):
        return url.startswith('data:')

    def is_cached_type(self, resource_type):
        """Answer whether ``resource_type`` matches the receivers cached
        content type and format.
        """
        resource_content, resource_format = resource_type.split('/', 1)
        return self.cached_content in ('*', resource_content) and \
               self.cached_format in ('*', resource_format)

    def fetch(self, url, resource_type):
        """Fetch the content of ``url``.

        If ``resource_type`` matches the cached resource types, use cache to
        retrieve/store the content (if ``url`` does not contain data itself).
        """
        if not self.is_data_url(url) and self.is_cached_type(resource_type):
            content = self.cache.get(url, None)
            if content is None:
                content = super().fetch(url, resource_type)
                self.cache[url] = content
            return content

        return super().fetch(url, resource_type)


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


def read_url(url, url_fetcher, resource_type):
    """Get bytes in a parsed ``url`` using ``url_fetcher``.

    If ``url_fetcher`` is None a default (no limitations) URLFetcher is used.
    """
    if url.scheme:
        url = url.geturl()
    else:
        url = 'file://{}'.format(os.path.abspath(url.geturl()))
    return url_fetcher.fetch(url, resource_type)


"""Create singleton URL fetcher which can be used as default fetcher."""
DEFAULT_URL_FETCHER = URLFetcher()