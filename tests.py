import unittest, os, time
from dirfixtures import DirFixtures
from migrater import Migrater

class TestMigrater(unittest.TestCase):
	"""docstring for TestMigrater"""

	def setUp(self):
		self.df = DirFixtures()
		self.df.builds()
		with open('password.txt', 'r') as pw:
			password = pw.read()
		self.p = { 
			'type': 'sftp',
			'host': 'athill@localhost',
			'password': password
		}
		self.testpath = 'd.txt'
		self.testpath2 = 'q.txt'
		self.instances = ['local', 'remote']
		for instance in self.instances:
			self.p[instance+'root'] = os.path.join(os.getcwd(), instance)



	def test_add(self):
		actions = {'A': [self.testpath] }
		self.fix('local', self.testpath, 'local')
		# time.sleep(2.5)
		m = Migrater(self.p, actions)
		m.migrate()
		m.close()
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
		m.close()
		with open(os.path.join(self.p['remoteroot'], self.testpath), 'r') as f:
			content = f.read()		
		self.assertTrue(content == 'local')
		# revert
		for instance in self.instances:
			self.unfix(instance, self.testpath)

	def test_delete(self):
		actions = {'D': [self.testpath] } 
		self.fix('remote', self.testpath, 'remote')
		# quit()
		m = Migrater(self.p, actions)
		m.migrate()
		m.close()
		remotepath = os.path.join(self.p['remoteroot'], self.testpath)
		exists  = os.path.exists(remotepath)

		self.assertTrue(not exists)
		# no unfix required

	def test_backup(self):
		backupdir = './backup'
		actions = {'D': [self.testpath], 'M': [self.testpath2] } 
		self.fix('remote', self.testpath, 'um')
		self.fix('remote', self.testpath2, 'um')
		m = Migrater(self.p, actions)
		m.backup(backupdir)
		m.close()
		self.assertTrue(os.path.exists(os.path.join(backupdir, self.testpath)))
		self.assertTrue(os.path.exists(os.path.join(backupdir, self.testpath2)))
		self.unfix('remote', self.testpath)
		self.unfix('remote', self.testpath2)



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
		# print('path in fix', path)
		with open(path, 'w') as f:
			f.write(content)

	def unfix(self, instance, filepath):
		path = os.path.join(self.p[instance+'root'], filepath);
		os.remove(path)

if __name__ == '__main__':
    unittest.main()