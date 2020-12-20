# Render paper maps using Maperitive

This program renders an area with given boundaries using [Maperitive](http://maperitive.net/). It is designed to work with hikingmap but it can be used standalone as well if desired.

## Installation
Clone this repository and run the following command in the created directory.
```bash
python setup.py install
```

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

## Configuration file

Because most of the time you will want to use the same parameters, you can optionally override the defaults in a configuration file. hm-render-maperitive will search for a file hm-render-maperitive.config.xml in the current directory, if not found it will resort to ~/.hm-render-maperitive.config.xml

```
<?xml version="1.0" encoding="utf-8"?>
<hm-render-maperitive>
    <maperitive>/path/to/Maperitive.exe/or/Maperitive.sh</maperitive>
    <datasources>
        <datasource>/path/to/mapdata.osm.pbf</datasource>
        <!--datasource>/more/files/can/be/added.osm.pbf</datasource-->
    </datasources>
    <outputformat>png</outputformat>
    <dpi>300</dpi>
</hm-render-maperitive>
```

Options:

| Tag | Description
| --- | -----------
| maperitive | Full path and filename of the Maperitive startup script or executable. hm-render-maperitive will pass options so if you use a shell script, make sure all parameters are passed.
| datasources | Optional. Contains all map datasources to be rendered by Maperitive. Keep in mind that more and larger files require more memory, Maperitive may not be able to handle this.
| outputformat | Output format. Output format. Consult the documentation of the export-bitmap function in Maperitive for possible values.
| dpi | Amount of detail to render in dots per inch. This value is unrelated to the setting on your printer, a higher value will simply result in smaller icons, thinner roads and unreadable text.


## Prerequisites

To run this script you should have a working installation of [python 3](https://www.python.org/) and [Maperitive](http://maperitive.net/). 

