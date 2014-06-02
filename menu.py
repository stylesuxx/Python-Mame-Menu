import os
import sys
import subprocess
import re
import pygame
from lxml import etree
from pygame.locals import *
import math
import time
from game import *

class pymenu:
    alphabet = ['0', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    screen = None
    running = True
    items = []
    active_item = 0
    screen_size = None
    font_size = None
    max_image_width = None
    max_image_height = None
    game_xml_path = None
    
    def __init__(self, font_size = 20, (max_image_width, max_image_height) = (350, 768), game_xml_path = 'game.xml'):
        self.font_size = font_size
        self.max_image_width = max_image_width
        self.max_image_height = max_image_height
        self.game_xml_path = game_xml_path

        "Load game.xml or create one if it does not exist yet"
        if os.path.isfile(game_xml_path):
            self.load_game_xml()
        else:
            self.generate_game_xml()

        "Ininitializes a new pygame screen using the framebuffer"
        # Based on "Python GUI in Linux frame buffer"
        # http://www.karoltomala.com/blog/?p=679
        disp_no = os.getenv("DISPLAY")
        if disp_no:
            sys.stderr.write("I'm running under X display = {0}\n".format(disp_no))
        
        # Check which frame buffer drivers are available
        # Start with fbcon since directfb hangs with composite output
        drivers = ['fbcon', 'directfb', 'svgalib']
        found = False
        for driver in drivers:
            # Make sure that SDL_VIDEODRIVER is set
            if not os.getenv('SDL_VIDEODRIVER'):
                os.putenv('SDL_VIDEODRIVER', driver)
            try:
                pygame.display.init()
            except pygame.error:
                sys.stderr.write('Driver: {0} failed.\n'.format(driver))
                continue
            found = True
            break
    
        if not found:
            raise Exception('No suitable video driver found!')
        
        self.screen_size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
        self.screen = pygame.display.set_mode(self.screen_size, pygame.FULLSCREEN)
        # Clear the screen to start
        self.screen.fill((0, 0, 0))        
        # Initialise font support
        pygame.font.init()
        # Set key repeat
        pygame.key.set_repeat(75, 150)
        # Disable the mouse cursor
        pygame.mouse.set_visible(False)
        # Render the screen
        pygame.display.update()

    def __del__(self):
        "Destructor to make sure pygame shuts down, etc."

    def load_game_xml(self):
        context = etree.iterparse(self.game_xml_path, tag='game')
        for event, elem in context :
            keys = elem.keys()
            if not 'isdevice' in keys and not 'isbios' in keys:
                item = Game()
                item.cloneof = ''
                if 'cloneof' in keys:
                    item.cloneof = elem.get('cloneof')

                item.slug = elem.get('name')
                item.description = elem.xpath('description/text()')[0]
                item.year = elem.xpath('year/text()')[0]
                item.manufacturer = elem.xpath('manufacturer/text()')[0]
                item.state = elem.xpath('state/text()')[0]
                item.played = int(elem.xpath('played/text()')[0])
                item.time = int(elem.xpath('time/text()')[0])

                self.items.append(item)
                    
            elem.clear()

    def generate_game_xml(self):
        mame_xml_path = '/tmp/mame.xml'
        os.system('mame -listxml > ' + mame_xml_path)

        context = etree.iterparse(mame_xml_path, tag='game')
        for event, elem in context :
            keys = elem.keys()
            if not 'isdevice' in keys and not 'isbios' in keys:
                item = Game()
                item.cloneof = ''
                if 'cloneof' in keys:
                    item.cloneof = elem.get('cloneof')

                item.slug = elem.get('name')
                item.description = elem.xpath('description/text()')[0]
                item.year = elem.xpath('year/text()')[0]
                item.manufacturer = elem.xpath('manufacturer/text()')[0]

                self.items.append(item)
                    
            elem.clear()

        try:
            output = subprocess.check_output(['mame', '-verifyroms'])
        except Exception, e:
            output = str(e.output)

        output = output.split('\n')
        for line in output:
            if line.startswith('romset'):
                match = re.search('^romset ([a-zA-Z0-9]*) (\[[a-zA-Z0-9]*\] )?is (.*)$', line)
                if match:
                    slug = match.group(1) 
                    state = match.group(3)

                    counter = 0
                    for item in self.items:
                        if item.slug == slug:
                            self.items[counter].state = state

                        counter += 1

        # Remove all games with unknown state from the list
        tmp = []
        for item in self.items:
            if item.state != 'unknown':
                tmp.append(item)

        self.items = tmp
        self.save_game_xml()

    def save_game_xml(self):
        root = etree.Element("mame")
        root.set('last_game', self.items[self.active_item].slug)
        for item in self.items:
            game = etree.SubElement(root, "game")
            game.set('name', item.slug)
            if item.cloneof:
                game.set('cloneof', item.cloneof)

            description = etree.SubElement(game, "description")
            description.text = item.description
            year = etree.SubElement(game, "year")
            year.text = item.year
            manufacturer = etree.SubElement(game, "manufacturer")
            manufacturer.text = item.manufacturer
            state = etree.SubElement(game, "state")
            state.text = item.state
            played = etree.SubElement(game, "played")
            played.text = str(item.played)
            time = etree.SubElement(game, "time")
            time.text = str(item.time)

        element_tree = etree.ElementTree(root)
        element_tree.write(self.game_xml_path, pretty_print=True)

    def draw_text(self, text, (pos_x, pos_y), font_size = 20, color = (255, 255, 255)):
        font = pygame.font.SysFont('monospace', font_size)
        text = font.render(text, 1, color)
        self.screen.blit(text, (pos_x, pos_y))

    def draw_items(self):
        counter = 0
        items_per_page = (self.screen.get_size()[1] - 20) / (self.font_size)
        if len(self.items) < items_per_page:
            items_per_page = len(self.items)

        self.screen.fill((0, 0, 0))

        offset = (self.active_item / items_per_page) * items_per_page
        for i in range(0 + offset, items_per_page + offset):
            game = self.items[i]
            font = pygame.font.SysFont('monospace', self.font_size)
            color = (255, 255, 255)
            if counter + offset == self.active_item:
                color = (255, 0, 0)

            self.draw_text('{0: <12}'.format(game.slug) + game.description, (10, (10 + self.font_size * counter)), self.font_size, color)
            counter += 1

    def draw_info(self):
        font = pygame.font.SysFont('monospace', self.font_size)
        item = self.items[self.active_item]
        pos_x = self.screen_size[0] - self.max_image_width
        pos_y = self.screen_size[1] - 10
        
        # Clone of
        if self.items[self.active_item].cloneof:
            clone = 'Clone of ' + item.cloneof
            self.draw_text(clone, (pos_x, (pos_y - self.font_size * 3)))

        # Times played
        if item.played > 0:
            played = 'Played ' + str(item.played) + ' time'
            if item.played > 1:
                played += 's'
            if item.time > 0:
                played += ' - ' + time.strftime('%H:%M:%S', time.gmtime(item.time))
            self.draw_text(played, (pos_x, (pos_y - self.font_size * 4)))

        # Release year
        year = 'Year: ' + item.year + ' (' + item.state + ')'
        self.draw_text(year, (pos_x, (pos_y - self.font_size * 2)))

        # Manufacturer
        manufacturer = self.items[self.active_item].manufacturer
        self.draw_text(manufacturer, (pos_x, (pos_y - self.font_size)))

    def draw_image(self):
        image_path = 'snap/' + self.items[self.active_item].slug + '.png'
        if os.path.isfile(image_path):
            image = pygame.image.load(image_path)
            
            image_width, image_height = image.get_size()
            if image_width > image_height:
                # fit to width
                scale_factor = self.max_image_width/float(image_width)
                new_height = scale_factor * image_height
                if new_height > self.max_image_height:
                    scale_factor = by/float(image_height)
                    new_width = scale_factor * image_width
                    new_height = self.max_image_height
                else:
                    new_width = self.max_image_width
            else:
                # fit to height
                scale_factor = self.max_image_height/float(image_height)
                new_width = scale_factor * image_width
                if new_width > self.max_image_width:
                    scale_factor = self.max_image_width/float(image_width)
                    new_width = self.max_image_width
                    new_height = scale_factor * image_height
                else:
                    new_height = self.max_image_height

            new_width = int(math.ceil(new_width))
            new_height = int(math.ceil(new_height))

            image = pygame.transform.scale(image, (new_width, new_height))
            self.screen.blit(image, (self.screen_size[0] - image.get_width() - 10, 10))

    def items_with_letter(self, letter):
        for item in self.items:
            if item.slug[0] == letter:
                return True

        return False

    def next_letter(self):
        current_letter = self.current_letter()
        index = self.alphabet.index(current_letter)
        index += 1
        while index < len(self.alphabet) and not self.items_with_letter(self.alphabet[index]):
            index += 1

        if index >= len(self.alphabet):
            index = len(self.alphabet) - 1

        next_letter = self.alphabet[index]
        if self.items_with_letter(next_letter):
            self.jump_to_letter(next_letter)

    def prev_letter(self):
        current_letter = self.current_letter()
        index = self.alphabet.index(current_letter)
        index -= 1
        while index >= 0 and not self.items_with_letter(self.alphabet[index]):
            index -= 1

        if index < 0:
            index = 0
        
        prev_letter = self.alphabet[index]
        if self.items_with_letter(prev_letter):
            self.jump_to_letter(prev_letter)

    def current_letter(self):
        current_letter = self.items[self.active_item].slug[0]
        if current_letter.isdigit():
            current_letter = '0'

        return current_letter

    def jump_to_letter(self, letter):
        counter = 0
        for item in self.items:
            if item.slug[0] is letter:
                self.active_item = counter
                break

            counter +=1

    def increase_play_counter(self, time):
        self.items[self.active_item].played += 1
        self.items[self.active_item].time += time
        self.save_game_xml()

    def check_input(self):
        event = pygame.event.wait()
        if event.type == KEYDOWN and event.key == K_ESCAPE:
            "Exit menu"
            self.running = False
        elif event.type == KEYDOWN and event.key == K_UP:
            "Move item up"
            self.active_item -= 1
            if self.active_item < 0:
                self.active_item = 0
        elif event.type == KEYDOWN and event.key == K_DOWN:
            "Move item down"
            self.active_item += 1
            if self.active_item >= len(self.items):
                self.active_item = len(self.items) - 1
        elif event.type == KEYDOWN and event.key == K_LEFT:
            "Jump to previous letter"
            self.prev_letter()
        elif event.type == KEYDOWN and event.key == K_RIGHT:
            "Jump to next letter"
            self.next_letter()
        elif (event.type == KEYDOWN or event.type == KEYUP) and event.key == K_1:
            """
            Start mame with the chosen game

            Disable key repeat, otherwise mame will be started immideatly after one has quit.
            Key repeat is set again after mame returns so smooth scrolling in the menu is
            possible all the time.
            """
            pygame.key.set_repeat()
            output = subprocess.check_output('mame -video soft ' + self.items[self.active_item].slug, shell = True)
            match = re.search('^.*\(([0-9]*) .*$', output)
            if match:
                time = int(match.group(1))
                self.increase_play_counter(time)

            pygame.key.set_repeat(75, 150)

        elif event.type == KEYDOWN and event.key == K_SPACE:
            pass
        elif event.type == KEYDOWN and event.key == K_LSHIFT:
            pass
        elif event.type == KEYDOWN and event.key == K_LALT:
            pass
        elif event.type == KEYDOWN and event.key == K_LCTRL:
            pass

"""
The main loop:
* Draw the menu items
* Draw the current items image
* Draw the current items Info
* Update the display
* Process keyboard input
"""
menu = pymenu()
while menu.running:
    menu.draw_items()
    menu.draw_image()
    menu.draw_info()
    pygame.display.update()
    
    menu.check_input()