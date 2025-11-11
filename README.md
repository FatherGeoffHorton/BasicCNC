# BasicCNC

I couldn't find a simple program to take an SVG file and convert into gcode for use on a CNC router. I thought, "How hard can it be?" With the help of the Python ecosystem, the answer is, "Harder than I thought, but doable."

This progran does *only* engraving and cutting; it's not intended to handle 2.5D or 3D models.

## Installation

You'll need to install the svgpathtools library. 

'''
pip install svgpathtools
'''

or

'''
pip3 install svgpathtools
'''
Download the files from this repository and you're set.

## Use

There's no GUI. Everything is controlled by .cfg files. They should be commented enough for you to adapt them to your needs.

* The main .cfg is what I call the "jobfile." The sample is Jobfile.cfg
* The machine .cfg file has info specific to the router you want to use. Mine's called cubiko.cfg because that's what I have.
* The stock .cfg file has the info about the material you're carving. The sample file is stock.cfg.
* And the bit .cfg file has the info about the bit you're using. The sample file is VBit20.cfg

Run the program like this:
'''
python3 BasicCNC.py Jobfile.cfg
'''
