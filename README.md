# Render paper maps using Maperitive

This program creates a Maperitive script which renders the map for a given area to a bitmap file.

Running this application standalone does not make much sense, since it will only create a Maperitive script from the given input parameters. If your goal is to generate a map for a known area, then you can just use the existing functionality in Maperitive to do so.
However, [hikingmap](https://github.com/roelderickx/hikingmap) allows you to pipe its output to a third-party application such as hm-render-maperitive, resulting in a Maperitive script rendering all pages around a given gpx track.

## Prerequisites

There are no special requirements apart from a working installation of [python 3](https://www.python.org/) and of course [Maperitive](http://maperitive.net/).

## Usage

Assuming you have hikingmap installed, you can run the following command to pipe its output to hm-render-maperitive:

`hikingmap [HIKINGMAPOPTIONS] --gpx hikingtrack.gpx -- ./hm_render_maperitive.py [OPTIONS]`

(the actual command may differ depending on which operating system you run and where hikingmap and hm_render_maperitive.py can be found on disk)

Please consult the documentation of hikingmap for more information about its options. Options to hm-render-maperitive can be:

| Parameter | Description
| --------- | -----------
| `-d, --dpi` | Amount of detail to render in dots per inch, default 300
| `-f, --format` | Output format. Consult the documentation of the export-bitmap function in Maperitive for possible values, default png

### Output files

Hm-render-maperitive will append bitmap generating commands to a script called hm-render-maperitive-PID.maperi.py, where PID is the process id of the parent process (being hikingmap). The temporary gpx files will be copied to the same location as the script.

Note: All files referenced in the generated script will include the full path, which means you can not move the script and/or the copied temporary gpx files once everything is saved.

### Maperitive workflow

First of all you need to add a map datasource in Maperitive, using the `add-web-map` or `load-source` command. Next you can run the generated script using `run-python [hm-render-maperitive-PID.maperi.py]`.

