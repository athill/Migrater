import unittest, os, time
from dirfixtures import DirFixtures
from migrater import Migrater

class TestMigrater(unittest.TestCase):
	"""docstring for TestMigrater"""

	def setUp(self):
		self.df = DirFixtures()
		self.df.builds()
		self.m = Migrater({ 
			'type': 'local',
			'localroot': './local',
			'remoteroot': './remote'
		}, {})



	def test_add(self):
		with open('local/d.txt', 'w') as the_file:
			the_file.write('Hello\n')
		# time.sleep(2.5)
		self.m.actions = {'A': ['d.txt'] } # why not working?: class must inherit from object to work
		self.m.migrate()
		self.assertTrue(os.path.exists('remote/d.txt'))

	def test_modify(self):
		newcontent = 'Goodbye\n'
		with open('local/d.txt', 'w') as the_file:
			the_file.write(newcontent)
		self.m.actions = {'M': ['d.txt'] } 
		self.m.migrate()
		with open('remote/d.txt', 'r') as content_file:
			content = content_file.read()		
		self.assertTrue(content == newcontent)

	def test_delete(self):
		self.m.actions = {'D': ['d.txt'] } 
		self.m.migrate()
		self.assertTrue(not os.path.exists('./remote/d.txt'))


	# I guess I don't get how passing dicts works in python, reference by default?
	def test_actions(self):
		fixture = { 'A': ['e.txt'] }
		self.m.actions = fixture
		# fixture['Q'] = []
		# fixture['D'] = []
		# print(fixture)
		# print(self.m.actions)
		self.assertTrue(self.m.actions == fixture)

	def tearDown(self):
		# self.df.destroys()
		pass

if __name__ == '__main__':
    unittest.main()