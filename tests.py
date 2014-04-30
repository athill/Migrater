import unittest, os, time, shutil
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
		self.backupdir = './backup'
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
		
		actions = {'D': [self.testpath], 'M': [self.testpath2] } 
		self.fix('remote', self.testpath, 'um')
		self.fix('remote', self.testpath2, 'um')
		m = Migrater(self.p, actions)
		m.backup(self.backupdir)
		m.close()
		self.assertTrue(os.path.exists(os.path.join(self.backupdir, self.testpath)))
		self.assertTrue(os.path.exists(os.path.join(self.backupdir, self.testpath2)))
		self.unfix('remote', self.testpath)
		self.unfix('remote', self.testpath2)


	def tearDown(self):
		self.df.destroys()
		shutil.rmtree(self.backupdir)
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