# Render paper maps using Maperitive

This program creates a [Maperitive](http://maperitive.net/) script which renders a given area to an image file. It is designed to work with hikingmap but it can be used standalone as well if desired.

## Prerequisites

To run this script you should have a working installation of [python 3](https://www.python.org/). To do something useful with the output script you also need [Maperitive](http://maperitive.net/). 

## Installation
The script is to be used in the current directory, no installation is required.

## Usage

`hm-render-maperitive [OPTION]... [gpxfiles]... bbox|center ...`

Options:

| Parameter | Description
| --------- | -----------
| `--pagewidth` | Page width in cm
| `--pageheight` | Page height in cm
| `-b, --basename` | Base filename without extension
| `-t` | Temp track file to render. This is used by hikingmap to draw the page boundaries of the overview map, the tracks will be saved as a temporary GPX file.
| `-y` | Temp waypoints file to render. This is used by hikingmap to render the distance each kilometer or mile, the waypoints will be saved as a temporary GPX file.
| `-v, --verbose` | Display extra information while processing.
| `-h, --help` | Display help
| `-m, --maperitive` | Full path to the Maperitive executable
| `-d, --dpi` | Amount of detail to render in dots per inch, default 300
| `-f, --format` | Output format. Consult the documentation of the export-bitmap function in Maperitive for possible values, default png
| `gpxfiles` | The GPX track(s) to render.

After these parameters you are required to make a choice between bbox and center. In bbox mode the rendered area will be a defined bounding box and in center mode you can specify a center coordinate and a scale.

Options for bbox mode:

| Parameter | Description
| --------- | -----------
| `-o, --minlon` | Minimum longitude of the page
| `-O, --maxlon` | Maximum longitude of the page
| `-a, --minlat` | Minimum latitude of the page
| `-A, --maxlat` | Maximum latitude of the page

Note that Maperitive will maintain the aspect ratio, the rendered area may not correspond exactly to the given boundary.

Options for center mode:

| Parameter | Description
| --------- | -----------
| `--lon` | Longitude of the center of the page
| `--lat` | Latitude of the center of the page
| `--scale` | Scale denominator, default 50000

