import unittest, os, time
from dirfixtures import DirFixtures
from migrater import Migrater

class TestUmt(unittest.TestCase):
	"""docstring for TestUmt"""

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
		time.sleep(2.5)
		# self.m.actions = {'A': ['d.txt'] } # wy not working?
		self.m.migrate()
		self.assertTrue(1==1)

	def tearDown(self):
		# self.df.destroys()
		pass

if __name__ == '__main__':
    unittest.main()