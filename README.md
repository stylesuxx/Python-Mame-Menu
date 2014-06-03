### Python Mame Menu
Python based framebuffer mame menu for linux.

#### Features
* Shows only available games on your system
* Tracks played time per game
* Shows games screenshot if available
* Intuitive handling

#### Dependencies
* python 2.7.x
* pygame

```
usage: py_menu.py [-h] [-f SIZE] [-a PATH] [-i WIDTH HEIGHT] XML_PATH

Python framebuffer mame menu.

positional arguments:
  XML_PATH              path to game xml file

optional arguments:
  -h, --help            show this help message and exit
  -f SIZE, --fontsize SIZE
                        set a font size
  -a PATH, --artwork PATH
                        path to artwork directory
  -i WIDTH HEIGHT, --imagesize WIDTH HEIGHT
                        maximum image size

```