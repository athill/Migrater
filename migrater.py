import os, shutil, errno,paramiko
from pprint import pprint
import utils

class Migrater(object):
	_actions = {}
	_p = {}

	def __init__(self, properties={}, actions={}):
		self.actions = actions
		self.p = properties	
		self.m = self.getm(self.p)

	#### Properties

	# actions
	@property
	def actions(self):
		"""Get the current actions."""
		return self._actions

	@actions.setter
	def actions(self, value):
		# print('in setter')
		actions = {
		    "A": [],   # add
		    "M": [],   # modify
		    "D": []    # delete
		}		
		# dict
		if isinstance(value, dict):
			for a in actions.keys():
				if a in value.keys():
					actions[a] = value[a]
		else:
			path = self.fixPath(value)
			# file
			if os.path.isfile(path):
				lines = [line.strip() for line in open(value)]
			# raw text
			else:
				lines = path.split(os.linesep)
			# parse
			for line in lines:
			    if line == '':
			         continue
			    # print line
			    action = line[0]
			    filen = line[1:].strip()
			    if action in actions.keys():
			        actions[action].append(filen)
			    else:
			        raise Exception("Unknown action: '%s'" % (action))


		self._actions = actions

	# properties (p)
	@property
	def p(self):
		"""Get the current p."""
		return self._p

	@p.setter
	def p(self, value):
		defaults = {
			'type': 'local',
			'localroot': './local',
			'remoteroot': './remote'
		}
		p = utils.extend(defaults, value)
		p['localroot'] = self.fixPath(p['localroot'])
		p['remoteroot'] = self.fixPath(p['remoteroot'])		
		self._p = p


	#### Methods

	def backup(self, backuppath):
		"""Backup modified and deleted files to to backuppath"""
		p = dict(self.p)
		p['localroot'] = backuppath
		m = self.getm(p)
		for path in self.actions["D"]+self.actions["M"]:
			print(path)
			d = os.path.dirname(m.local(path))
			if not os.path.exists(d):
				os.makedirs(d)
			if self.m.exists(path):
				m.get(path)

	def migrate(self, opts={}):
		"""Act on file paths in self.actions from localroot to remoteroot based on action type:
			A: Add
			M: Modify (overwrite)
			D: Delete. These are based on Git name-status output
		In practice, A and M copy from local to remote and D deletes from remote.
		"""
		actions = opts['actions'] if 'actions' in opts.keys() else self.actions
		# # # # Delete
		for path in self.actions["D"]:
			if self.m.exists(path):
				self.m.remove(path)
		# # # # Add/Modify
		for path in self.actions["A"]+self.actions["M"]:
		    if not self.m.exists(path):
		        self.m.makedirs(os.path.dirname(path))
		    self.m.put(path)

	def close(self):
		self.m.close()	



	### helpers
	def getm(self, p=None):
		"""Get a migrater instance based on p (properties)""". 
		if p == None:
			p = self.p
		else:
			p['localroot'] = self.fixPath(p['localroot'])
			p['remoteroot'] = self.fixPath(p['remoteroot'])
		m = None
		if p['type'] == 'sftp':
			m = Sftp(p)
		elif p['type'] == 'ftp':
			m = Ftp(p)
		else:
			m = Local(p)		
		return m

	def fixPath(self, path):
		return path.replace('~', os.path.expanduser("~"), 1)			
	

class Migrate_Base:
	"""Abstract class. Mostly an interface with some basic, overridable functionality. 
	Local and SFTP are current implementations. 
	"""
	def __init__(self, properties):
		"""Override any of the default properties (e.g., type, localroot, remoteroot, etc.)"""
		self.p = properties
	#### implement these

	def put(self, path):
		"""Copy path from localroot to remoteroot"""
		raise NotImplementedError
	def get(self, path):
		"""Copy path from remoteroot to localroot"""
		raise NotImplementedError
	def exists(self, path):
		"""Whether path exists on remoteroot"""
		raise NotImplementedError
	def remove(self, path):
		"""Remove file from path on remoteroot"""
		raise NotImplementedError	
	def makedirs(self, path):
		"""Create necessary directories under remoteroot"""
		raise NotImplementedError
	def close(self):
		"""Close any remote connections"""
		raise NotImplementedError

	# shared functionality
	def local(self, path):
		return os.path.join(self.p['localroot'], path)
	def remote(self, path):
		return os.path.join(self.p['remoteroot'], path)	

class Local(Migrate_Base):
	import os, shutil
	def __init__(self, properties):
		self.p = properties
	def get(self, path):
		shutil.copyfile(self.remote(path), self.local(path))

	def put(self, path):
		shutil.copyfile(self.local(path), self.remote(path))

	def exists(self, path):
		return os.path.exists(self.remote(path))
	def remove(self, path):
		remotepath = self.remote(path)
		try:
			os.remove(remotepath)
		except OSError as e: # name the Exception `e`
			print "Failed with:", e.strerror # look what it says
			print "Error code:", e.code

		
	def makedirs(self, remotepath):
		directory = os.path.dirname(self.remote(remotepath))
		# pprint(directory)
		try:
			os.makedirs(directory)
		except OSError as exc: # Python >2.5
			if exc.errno == errno.EEXIST and os.path.isdir(directory):
				pass
			else: raise		

	def close(self):
		pass

class Sftp(Migrate_Base):
	import paramiko
	
	def __init__(self, properties):
		port = properties['port'] if 'port' in properties else 22
		# # Open a transport
		host = properties['host'].split('@')
		if len(host) > 1:
			[user, host] = [host[0], host[1]]
		else:
			userhome = os.path.expanduser('~')
			user = os.path.split(userhome)[-1]
		self.transport = paramiko.Transport((host, port))

		# # # Auth
		self.transport.connect(username = user, password = properties['password'])
		# # # Go!
		self.sftp = paramiko.SFTPClient.from_transport(self.transport)
		# self.sftp.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		self.p = properties

	def get(self, path):
		self.sftp.get(self.remote(remotepath), self.local(localpath))
	def put(self, path):
		localpath = self.local(path)
		remotepath = self.remote(path)
		# print(localpath, remotepath)
		self.sftp.put(localpath, remotepath)
	def exists(self, remotepath):
	    """os.path.exists for paramiko's SCP object
	       http://stackoverflow.com/questions/850749/check-whether-a-path-exists-on-a-remote-host-using-paramiko
	    """
	    try:
	        self.sftp.stat(remotepath)
	    except IOError, e:
	        if e.errno == errno.ENOENT:
	            return False
	        raise
	    else:
	        return True  
	def remove(self, path):
		remotepath = self.remote(path)
		print('remotepath: ', remotepath)
		print('exists', os.path.exists(remotepath))
		self.sftp.remove(remotepath)
	def makedirs(self, path):
		remotepath = self.remote(path)
		path_array = remotepath.split(os.sep)
		chkpath = '/'
		# pprint(path_array)
		for part in path_array:
			chkpath = os.path.join(chkpath, part)
			if chkpath == '':
				continue
			# create directory if it doesn't exist
			# somewhat convoluted. directory creation is in the except clause
			try:
				self.sftp.stat(chkpath)
			except IOError, e:
				if e.errno == errno.ENOENT:
					self.sftp.mkdir(chkpath, 0755)
	def close(self):
		self.sftp.close()
		self.transport.close()		

if __name__ == '__main__':
	properties = {
	}
	actions = { "A": ['test.py']}
	m = Migrater(properties, actions)
	pprint(m.p)
	# m.set_actions({'A': ['test']})
	# m.actions = {'A': ['test']}
	# pprint(m.actions)
	# os.remove('./remote/d.txt')