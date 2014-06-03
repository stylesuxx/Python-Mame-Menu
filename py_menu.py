#!/usr/bin/python
import argparse

from menu import *

"Parse command line arguments or display usage"
parser = argparse.ArgumentParser(description = "Python framebuffer mame menu.")
parser.add_argument("xmlpath", metavar = "XML_PATH", help = "path to game xml file")
parser.add_argument("-f", "--fontsize", metavar = "SIZE", help = "set a font size", type = int)
parser.add_argument("-a", "--artwork", metavar = "PATH", help = "path to artwork directory")
parser.add_argument("-i", "--imagesize", nargs = 2, metavar = ("WIDTH", "HEIGHT"), help = "maximum image size", type = int)
args = parser.parse_args()

"Initialize games and menu"
games = Games(args.xmlpath)
menu = Menu(games)

"Menu settings depending on command line arguments"
if args.fontsize:
	menu.set_font_size(args.fontsize)
if args.imagesize:
	menu.set_max_image_size((args.imagesize[0], args.imagesize[1]))
if args.artwork:
	menu.set_artwork_path(args.artwork)

"Run the main loop until escape is pressed"
while menu.running:
    menu.draw_items()
    menu.draw_image()
    menu.draw_info()
    menu.update()

    menu.check_input()
