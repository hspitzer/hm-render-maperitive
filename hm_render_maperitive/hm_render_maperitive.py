#!/usr/bin/env python3

# hm-render-maperitive -- render maps on paper using maperitive
# Copyright (C) 2020  Roel Derickx <roel.derickx AT gmail>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os, argparse, math, subprocess
from xml.dom import minidom

# global constants
earthCircumference = 40041.44 # km (average, equatorial 40075.017 km / meridional 40007.86 km)
cmToKmFactor = 100000.0
inch = 2.54 # cm

def search_configfile():
    filename = 'hm-render-maperitive.config.xml'
    if os.path.exists(filename):
        return os.path.abspath(filename)
    elif os.path.exists(os.path.join(os.path.expanduser('~'), '.' + filename)):
        return os.path.join(os.path.expanduser('~'), '.' + filename)
    else:
        return None


def get_xml_subtag_value(xmlnode, sublabelname):
    elements = xmlnode.getElementsByTagName(sublabelname)
    return str(elements[0].firstChild.nodeValue) if elements and elements[0].childNodes else None


def parse_configfile():
    config = {}
    config['maperitive'] = 'Maperitive.exe'
    config['datasources'] = [ ]
    config['output_format'] = 'png'
    config['dpi'] = 300
    
    configfile = search_configfile()
    
    if configfile:
        xmldoc = None
        
        try:
            xmldoc = minidom.parse(configfile)
        except:
            pass
        
        if xmldoc:
            xmlmaperitive_element = xmldoc.getElementsByTagName('hm-render-maperitive')
            if xmlmaperitive_element:
                xmlmaperitive = xmlmaperitive_element[0]
        
        if xmlmaperitive:
            maperitive = get_xml_subtag_value(xmlmaperitive, 'maperitive')
            if maperitive:
                config['maperitive'] = maperitive
            
            xmldatasources = xmlmaperitive.getElementsByTagName('datasources')
            xmldatasourcelist = xmldatasources[0].getElementsByTagName('datasource')
            for xmldatasource in xmldatasourcelist:
                if xmldatasource and xmldatasource.childNodes:
                    datasource = str(xmldatasource.firstChild.nodeValue)
                    config['datasources'].append(os.path.abspath(datasource))
            
            output_format = get_xml_subtag_value(xmlmaperitive, 'outputformat')
            if output_format:
                config['output_format'] = output_format
            
            dpi = get_xml_subtag_value(xmlmaperitive, 'dpi')
            if dpi:
                config['dpi'] = int(dpi)
    
    return config


def parse_commandline():
    config = parse_configfile()

    parser = argparse.ArgumentParser(description = "Render a map on paper using Maperitive")
    parser.add_argument('--pagewidth', dest = 'pagewidth', type = float, default = 20.0, \
                        help = "page width in cm")
    parser.add_argument('--pageheight', dest = 'pageheight', type = float, default = 28.7, \
                        help = "page height in cm")
    parser.add_argument('-b', '--basename', dest = 'basefilename', default = "detail", \
                        help = "base filename without extension")
    parser.add_argument('-t', dest = 'temptrackfile', \
                        help = "temp track file to render")
    parser.add_argument('-y', dest = 'tempwaypointfile', \
                        help = "temp waypoints file to render")
    parser.add_argument('-v', dest = 'verbose', action = 'store_true')
    # hm-render-maperitive specific parameters
    parser.add_argument('-m', '--maperitive', dest = 'maperitive', default = config['maperitive'], \
                        help = "full path to the Maperitive executable (default: %(default)s)")
    parser.add_argument('-d', '--dpi', type=int, default=config['dpi'], \
                        help = "amount of detail to render in dots per inch (default: %(default)s)")
    parser.add_argument('-f', '--format', dest='output_format', default=config['output_format'], \
                        help = "an output format supported by the export-bitmap function in " + \
                               "Maperitive (default: %(default)s)")
    # --
    parser.add_argument('gpxfiles', nargs = '*')
    
    subparsers = parser.add_subparsers(dest='mode', required=True, \
                                       help='bounding box or center mode')
    
    # create the parser for the bbox command
    parser_bbox = subparsers.add_parser('bbox', help='define bounding box')
    parser_bbox.add_argument('-o', '--minlon', type=float, required = True, \
                        help = "minimum longitude")
    parser_bbox.add_argument('-O', '--maxlon', type=float, required = True, \
                        help = "maximum longitude")
    parser_bbox.add_argument('-a', '--minlat', type=float, required = True, \
                        help = "minimum latitude")
    parser_bbox.add_argument('-A', '--maxlat', type=float, required = True, \
                        help = "maximum latitude")

    # create the parser for the atlas command
    parser_atlas = subparsers.add_parser('center', help='define center mode')
    parser_atlas.add_argument('--lon', type=float, required=True, \
                              help='longitude of the center of map')
    parser_atlas.add_argument('--lat', type=float, required=True, \
                              help='latitude of the center of map')
    parser_atlas.add_argument('--scale', type=int, default=50000, \
                              help='scale denominator')

    parameters = parser.parse_args()
    parameters.datasources = config['datasources']
    return parameters


def convert_cm_to_degrees_lon(lengthcm, scale, latitude):
    lengthkm = lengthcm / cmToKmFactor * scale
    return lengthkm / ((earthCircumference / 360.0) * math.cos(math.radians(latitude)))


def convert_cm_to_degrees_lat(lengthcm, scale):
    lengthkm = lengthcm / cmToKmFactor * scale
    return lengthkm / (earthCircumference / 360.0)


def assure_bbox_mode(parameters):
    if parameters.mode == 'center':
        pagesize_lon = convert_cm_to_degrees_lon(parameters.pagewidth, \
                                                 parameters.scale, parameters.lat)
        pagesize_lat = convert_cm_to_degrees_lat(parameters.pageheight, parameters.scale)
        
        parameters.minlon = parameters.lon - pagesize_lon / 2
        parameters.minlat = parameters.lat - pagesize_lat / 2
        parameters.maxlon = parameters.lon + pagesize_lon / 2
        parameters.maxlat = parameters.lat + pagesize_lat / 2

    
def render(parameters):
    with open(parameters.basefilename + '.mscript', 'w') as f:
        # load datasources: osm file, gpx files and temp gpx files
        for datasource in parameters.datasources:
            f.write('load-source "%s"\n' % datasource)

        # parameters.gpxfiles, parameters.temptrackfile and parameters.tempwaypointfile are passed
        # from hikingmap, full path is given
        for gpxfile in parameters.gpxfiles:
            f.write('load-source "%s"\n' % gpxfile)

        if parameters.temptrackfile:
            f.write('load-source "%s"\n' % parameters.temptrackfile)
        if parameters.tempwaypointfile:
            f.write('load-source "%s"\n' % parameters.tempwaypointfile)
        
        # set the page boundaries
        f.write('set-print-bounds-geo %.8f, %.8f, %.8f, %.8f\n' % \
                (parameters.minlon, parameters.minlat, parameters.maxlon, parameters.maxlat))
        
        # set paper size - orientation follows from width and height
        width = int(parameters.pagewidth * 10)
        height = int(parameters.pageheight * 10)
        f.write('set-paper width=%d height=%d orientation=portrait\n' % (width, height))
        
        # export the map as bitmap
        imgwidth = math.trunc(parameters.pagewidth / inch * parameters.dpi)
        # Maperitive does not allow setting height if print boundaries are already set
        #imgheight = math.trunc(parameters.pageheight / inch * parameters.dpi)
        f.write('export-bitmap file="%s" width=%d\n' % \
                (os.path.abspath(parameters.basefilename + '.' + parameters.output_format), imgwidth))
        
        # quit Maperitive after rendering
        f.write('exit')

    # execute Maperitive
    args = [ parameters.maperitive,
             os.path.abspath(parameters.basefilename + '.mscript') ]

    try:
        process = subprocess.run(args, \
                                 cwd = os.path.dirname(parameters.maperitive),
                                 stdout = subprocess.PIPE, \
                                 check = True, \
                                 universal_newlines = True)
        process.check_returncode()
        print(process.stdout, end = '')
    except subprocess.CalledProcessError as e:
        print("Running Maperitive failed: %s" % e)


def main():
    parameters = parse_commandline()
    assure_bbox_mode(parameters)
    
    render(parameters)


if __name__ == '__main__':
    main()
