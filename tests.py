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
		}, {'A': ['d.txt'] })



	def test_add(self):
		with open('local/d.txt', 'w') as the_file:
			the_file.write('Hello\n')
		# time.sleep(2.5)
		# self.m.actions = {'A': ['d.txt'] } # why not working?
		self.m.migrate()
		self.assertTrue(os.path.exists('remote/d.txt'))

	def tearDown(self):
		self.df.destroys()
		pass

if __name__ == '__main__':
    unittest.main()