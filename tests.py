# import unittest
# from bs4 import BeautifulSoup

# import server
# from model import connect_to_db

# class serverTestCase(unittest.TestCase):

# 	def setUp(self):
# 		server.app.config['TESTING'] = True
# 		self.app = server.app.test_client()

# 	def tearDown(self):
# 		pass

# 	def test_first_bird(self):
# 		result = self.app.get('/')
# 		self.assertIn('Ostrich', result.data)

# 	# def test_taxonomy_structure(self):
# 	# 	result = self.app.get('/')
# 	# 	parsed_response = BeautifulSoup(result.data, 'html.parser')
# 	# 	for order in parsed_response.find_all(class_="taxon_order"):
# 	# 		if order['id'] == "Anseriformes":
# 	# 			duck_test = order
# 	# 			break
# 	# 	for duck in duck_test.contents:
# 	# 		if duck.get('class') == "taxon_family":
# 	# 			print duck

# 	def test_lifelist(self):
# 		# server.session['user_id'] = 4
# 		# result = self.app.get('/lifelist')
# 		print server.session['user_id']



# if __name__ == '__main__':
# 	connect_to_db(server.app)
# 	unittest.main()

