#!/usr/bin/env python2

import os
import fontforge

for filename in os.listdir("."):
    font, extension = os.path.splitext(filename)
    if extension == ".svg":
        print("Generating %s" % font)
        try:
            fontforge.open("%s.svg" % font).generate("%s.otf" % font)
        except:
            pass
