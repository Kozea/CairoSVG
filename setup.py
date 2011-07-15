#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Public Domain

"""
CairoSVG - A Simple SVG Converter for Cairo
===========================================

CairoSVG is a SVG converter based on Cairo. It can export SVG files to PDF,
PostScript and PNG files.

For further information, please visit the `CairoSVG Website
<http://www.cairosvg.org/>`_.

"""

import os
from distutils.core import setup
from distutils.command.build_scripts import build_scripts

import cairosvg


# build_scripts is known to have a lot of public methods
# pylint: disable=R0904
class BuildScripts(build_scripts):
    """Build the package."""
    def run(self):
        """Run building."""
        # These lines remove the .py extension from the cairosvg executable
        self.mkpath(self.build_dir)
        for script in self.scripts:
            root, _ = os.path.splitext(script)
            self.copy_file(script, os.path.join(self.build_dir, root))
# pylint: enable=R0904


# When the version is updated, ``cairosvg.VERSION`` must be modified.
# A new section in the ``NEWS`` file must be added too.
setup(
    name="CairoSVG",
    version=cairosvg.VERSION,
    description="A Simple SVG Converter for Cairo",
    long_description=__doc__,
    author="Kozea",
    author_email="guillaume.ayoub@kozea.fr",
    url="http://www.cairosvg.org/",
    download_url="http://www.cairosvg.org/src/cairosvg/CairoSVG-%s.tar.gz" % \
        cairosvg.VERSION,
    license="GNU GPL v3",
    platforms="Any",
    packages=["cairosvg"],
    provides=["cairosvg"],
    scripts=["cairosvg.py"],
    cmdclass={"build_scripts": BuildScripts},
    requires={"pycairo": ["pycairo>=1.8"]},
    keywords=["svg", "cairo", "pdf", "png", "postscript"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Topic :: Multimedia :: Graphics :: Graphics Conversion"])
