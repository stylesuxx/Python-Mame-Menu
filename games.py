from lxml import etree
import os
import re
import subprocess

from game import *

"""
Load games from custom xml.

If the file does not exist yet, generate it.
First the mame.xml is generated, then mame checks for available games.
Information about the currently available games is written to the custom xml.
"""
class Games:
	items = None
	game_xml_path = None

	def __init__(self, game_xml_path):
		self.game_xml_path = game_xml_path
		self.items = []

		"Load game.xml or create one if it does not exist yet"
		if os.path.isfile(game_xml_path):
			self.load_xml()
		else:
			print "Building mame xml and checking available games."
			print "Lean back and relax, this may take some time..."
			self.generate_xml()

	def __del__(self):
		"Destructor"

	def get_all_items(self):
		return self.items

	def get_non_bad_items(self):
		return [item for item in self.items if item.state != "bad"]

	def get_bad_items(self):
		return [item for item in self.items if item.state == "bad"]

	def sort_ascending_by_alphabet(self):
		self.items = sorted(self.items, key=lambda item: item.slug, reverse=False)

	def sort_descending_by_alphabet(self):
		self.items = sorted(self.items, key=lambda item: item.slug, reverse=True)

	def sort_ascending_by_time(self):
		self.items = sorted(self.items, key=lambda item: item.time, reverse=False)

	def sort_descending_by_time(self):
		self.items = sorted(self.items, key=lambda item: item.time, reverse=True)

	def load_xml(self):
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

		sorted(self.items, key=lambda item: item.slug, reverse=False)

	def generate_xml(self):
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
		self.save_xml()

	def save_xml(self):
		root = etree.Element("mame")
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