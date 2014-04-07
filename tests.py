import unittest, os, time
from dirfixtures import DirFixtures
from migrater import Migrater

class TestMigrater(unittest.TestCase):
	"""docstring for TestMigrater"""

	def setUp(self):
		self.df = DirFixtures()
		self.df.builds()
		# with open('password.txt', 'r') as pw:
		# 	password = pw.read()
		self.p = { 
			'type': 'local',
		}
		self.testpath = 'd.txt'
		self.instances = ['local', 'remote']
		for instance in self.instances:
			self.p[instance+'root'] = './'+instance



	def test_add(self):
		actions = {'A': [self.testpath] }
		self.fix('local', self.testpath, 'local')
		# time.sleep(2.5)
		m = Migrater(self.p, actions)
		m.migrate()
		self.assertTrue(os.path.exists(os.path.join('remote', self.testpath)))
		# revert
		for instance in self.instances:
			self.unfix(instance, self.testpath)

	def test_modify(self):
		actions = {'M': [self.testpath] } 
		for instance in self.instances:
			self.fix(instance, self.testpath, instance)
		m = Migrater(self.p, actions)
		m.migrate()
		with open(os.path.join(self.p['remoteroot'], self.testpath), 'r') as f:
			content = f.read()		
		self.assertTrue(content == 'local')
		# revert
		for instance in self.instances:
			self.unfix(instance, self.testpath)

	def test_delete(self):
		actions = {'D': [self.testpath] } 
		self.fix('remote', self.testpath, 'remote')
		m = Migrater(self.p, actions)
		m.migrate()
		exists  = os.path.exists(os.path.join('remote', self.testpath))
		self.assertTrue(not exists)
		# no unfix required

	def test_backup(self):
		m = Migrater(self.p)
		m.backup('backup');



	# # I guess I don't get how passing dicts works in python, reference by default?
	# def test_actions(self):
	# 	fixture = { 'A': ['e.txt'] }
	# 	self.m.actions = fixture # class must inherit from object to work
	# 	# fixture['Q'] = []
	# 	# fixture['D'] = []
	# 	# print(fixture)
	# 	# print(self.m.actions)
	# 	self.assertTrue(self.m.actions == fixture)

	def tearDown(self):
		# self.df.destroys()
		pass

	def fix(self, instance, filepath, content):
		path = os.path.join(self.p[instance+'root'], filepath);
		directory = os.path.dirname(path)
		if directory != '':
			if not os.path.exists(directory):
				os.makedirs(directory)
		path = os.path.join(self.p[instance+'root'], filepath);
		with open(path, 'w') as f:
			f.write(content)

	def unfix(self, instance, filepath):
		path = os.path.join(self.p[instance+'root'], filepath);
		os.remove(path)

if __name__ == '__main__':
    unittest.main()