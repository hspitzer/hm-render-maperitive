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

import os, argparse, math, shutil

# global constants
earthCircumference = 40041.44 # km (average, equatorial 40075.017 km / meridional 40007.86 km)
cmToKmFactor = 100000.0
inch = 2.54 # cm


def parse_commandline():
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
    parser.add_argument('-d', '--dpi', type=int, default=300, \
                        help = "amount of detail to render in dots per inch (default: %(default)s)")
    parser.add_argument('-p', '--ppi', type=int, default=200, \
                        help = "resolution of scree to determine correct scale when exporting as svg (default: %(default)s)")
    parser.add_argument('-f', '--format', dest='output_format', default='png', \
                        help = "an output format supported by the export-bitmap function in " + \
                               "Maperitive (default: %(default)s)")
    parser.add_argument('--download-data', action='store_true', dest='download_data', help='download data using osm overpass api')
    parser.add_argument('-c', '--contours', action='store_true', help='generate contours')
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

    return parser.parse_args()


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
    script_name = os.path.abspath('hm-render-maperitive-%d.maperi.py' % os.getppid())
    is_new_script = not os.path.isfile(script_name)
    
    track_dest_filename = None
    if parameters.temptrackfile:
        track_dest_filename = os.path.abspath(os.path.basename(parameters.temptrackfile))
        if not os.path.isfile(track_dest_filename):
            shutil.copyfile(parameters.temptrackfile, track_dest_filename)

    waypt_dest_filename = None
    if parameters.tempwaypointfile:
        waypt_dest_filename = os.path.abspath(os.path.basename(parameters.tempwaypointfile))
        if not os.path.isfile(waypt_dest_filename):
            shutil.copyfile(parameters.tempwaypointfile, waypt_dest_filename)

    with open(script_name, 'a') as f:
        if is_new_script:
            f.write('# -*- coding: utf-8 -*-\n\nfrom maperipy import *\n\n')
            
            # load (temp) gpx files as datasources
            for gpxfile in parameters.gpxfiles:
                f.write('App.run_command(\'load-source "%s"\')\n' % gpxfile)
            f.write('\n')

        output_filename = parameters.basefilename + '.' + parameters.output_format
        f.write('# generating file %s\n' % output_filename)
        
        if track_dest_filename:
            f.write('App.run_command(\'load-source "%s"\')\n' % track_dest_filename)
        if waypt_dest_filename:
            f.write('App.run_command(\'load-source "%s"\')\n' % waypt_dest_filename)
        
        # set the page boundaries
        f.write('App.run_command(\'set-print-bounds-geo %.8f, %.8f, %.8f, %.8f\')\n' % \
                (parameters.minlon, parameters.minlat, parameters.maxlon, parameters.maxlat))
        
        # set paper size - orientation follows from width and height
        width = int(parameters.pagewidth * 10)
        height = int(parameters.pageheight * 10)
        f.write('App.run_command(\'set-paper width=%d height=%d orientation=portrait\')\n' % \
                (width, height))
        
        if parameters.download_data:
            # download the data
            f.write('App.run_command(\'download-osm-overpass bounds=%.8f,%.8f,%.8f,%.8f\')\n' % \
                    (parameters.minlon, parameters.minlat, parameters.maxlon, parameters.maxlat))
        if parameters.contours:
            f.write('App.run_command(\'generate-contours bounds=%.8f,%.8f,%.8f,%.8f\')\n' % \
                    (parameters.minlon, parameters.minlat, parameters.maxlon, parameters.maxlat))
        
        # set correct scale
        f.write('App.run_command(\'set-setting name=display.ppi value=%d\')\n' % \
                parameters.ppi)
        f.write('App.run_command(\'zoom-map-scale 50000\')\n')
        
        if parameters.output_format == 'svg':
            # export the map as svg
            f.write('App.run_command(\'export-svg file="%s"\')\n' % \
                    os.path.abspath(output_filename))
        else:
            # export the map as bitmap
            imgwidth = math.trunc(parameters.pagewidth / inch * parameters.dpi)
            # Maperitive does not allow setting height if print boundaries are already set
            #imgheight = math.trunc(parameters.pageheight / inch * parameters.dpi)
            f.write('App.run_command(\'export-bitmap file="%s" width=%d scale=2\')\n' % \
                (os.path.abspath(output_filename), imgwidth))
        
        # remove gpx datasources to prepare for the next page
        if waypt_dest_filename:
            f.write('App.run_command(\'remove-source %d\' % len(Map.layers))\n')
        if track_dest_filename:
            f.write('App.run_command(\'remove-source %d\' % len(Map.layers))\n')
        if parameters.download_data:
            f.write('App.run_command(\'remove-source %d\' % len(Map.layers))\n')
        if parameters.contours:
            f.write('App.run_command(\'remove-source %d\' % len(Map.layers))\n')


def main():
    parameters = parse_commandline()
    assure_bbox_mode(parameters)
    
    render(parameters)


if __name__ == '__main__':
    main()

