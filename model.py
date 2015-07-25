import sqlite3

class Bird(object):
	""" I'm a bird. I have a unique taxon code, a scientific name, and a common name."""

	def __init__(self, taxon_id, species_name, common_name):
		self.taxon_id = taxon_id
		self.species_name = species_name
		self.common_name = common_name

	@classmethod
	def get_birds_from_ebird(cls):
