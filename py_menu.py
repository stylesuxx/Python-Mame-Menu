#!/usr/bin/python
from menu import *

"Parse arguments with argparse"

game_xml_path = 'game.xml'

"Check if font size was passed"

"Check if max size was passed"

"Initialize games and menu"
games = Games(game_xml_path)
menu = Menu(games)

"""
The main loop:
* Draw the menu items
* Draw the current items image
* Draw the current items Info
* Update the display
* Process keyboard input
"""
while menu.running:
    menu.draw_items()
    menu.draw_image()
    menu.draw_info()
    menu.update()
    menu.check_input()