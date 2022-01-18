#!/usr/bin/env python
# -*- coding: utf-8 -*-
import arcpy, sys, os, unicodedata
reload(sys)
sys.setdefaultencoding('utf-8')

path_fr=r"C:\Users\JULIO\Documents\ArcGIS\Default.gdb\cuatro_frentes"
def flipLine(myFeatureClass, myQuery):

    try:
        lines = arcpy.da.UpdateCursor("cuatro_frentes3", ["SHAPE@"])
        for line in lines:
            lp = line[0].getPart(0)
            rPnts = arcpy.Array()
            print len(lp)
            for i in range(len(lp)):
                rPnts.add(lp[len(lp) - i - 1])
            rPoly = arcpy.Polyline(rPnts, arcpy.SpatialReference(4326))
            line[0] = rPoly
            lines.updateRow(line)
            del rPnts, rPoly
    except:
        print "Error:", sys.exc_info()[0]
    finally:
        if lines: del lines
        if line: del line

flipLine(path_fr,"")
