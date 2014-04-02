import os, shutil, errno
from pprint import pprint
import utils

class Migrater(object):
	_actions = {}

	def __init__(self, properties={}, actions={}):
		self._actions = self.parseactions(actions)
		self.p = properties
		defaults = {
			'type': 'local',
			'localroot': './local',
			'remoteroot': './remote'
		}
		self.p = utils.extend(defaults, properties)
		self.p['localroot'] = self.fixPath(self.p['localroot'])
		self.p['remoteroot'] = self.fixPath(self.p['remoteroot'])		
		self.m = self.getm(self.p)

	#### Properties

	# actions
	@property
	def actions(self):
		"""Get the current actions."""
		return self._actions

	# TODO: Not setting, apparently
	@actions.setter
	def actions(self, value):
		self._actions = self.parseactions(value)

	#stupid workaround hack
	# def set_actions(self, value):
	# 	self._actions = self.parseactions(value)	


	def backup(self, backuppath):
		p = dict(self.p)
		p['localroot'] = backuppath
		m = getm(p)
		for path in self._actions["D"]+self._actions["M"]:
		    d = os.path.dirname(m.local(path))
		    if not os.path.exists(d):
		    	os.makedirs(d)
		    if self.m.exists(rfile):
		        m.get(path)

	def migrate(self, opts={}):
		# defaults = {
		# 	'properties': self.p,
		# 	'actions': self._actions,
		# }
		# opts = utils.extend(defaults, opts)
		# config = opts['properties']
		# pprint()
		# # # # Delete
		for path in self._actions["D"]:
			# pprint('?')
			if self.m.exists(path):
				self.m.remove(path)
		# # # # Add/Modify
		for path in self._actions["A"]+self._actions["M"]:
		    if not self.m.exists(path):
		        self.m.makedirs(path)
		    self.m.put(path)		



	### helpers
	def getm(self, p):
		m = None
		p['localroot'] = self.fixPath(p['localroot'])
		p['remoteroot'] = self.fixPath(p['remoteroot'])
		if p['type'] == 'sftp':
			m = Sftp(p)
		elif p['type'] == 'ftp':
			m = Ftp(p)
		else:
			m = Local(p)		
		return m

	def parseactions(self, value):
		# dict
		if isinstance(value, dict):
			for a in ['A', 'M', 'D']:
				if a not in value:
					value[a] = []					
			return value
		path = self.fixPath(value)
		# file
		if os.path.isfile(path):
			lines = [line.strip() for line in open(value)]
		# raw text
		else:
			lines = path.split(os.linesep)
		actions = {
		    "A": [],   # add
		    "M": [],   # modify
		    "D": []    # delete
		}		
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
		return actions

	def fixPath(self, path):
		return path.replace('~', os.path.expanduser("~"), 1)			
	

class Migrate_Base:
	def __init__(self, properties):
		self.p = properties
	# implement these
	def get(self, path):
		raise NotImplementedError
	def put(self, path):
		raise NotImplementedError
	def exists(self, path):
		raise NotImplementedError
	def mkdir(self, path):
		raise NotImplementedError
	def remove(self, path):
		raise NotImplementedError	
	def makedirs(self, path):
		raise NotImplementedError
	def close(self):
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

	def mkdir(self, path):
		os.mkdir(self.remote(path))
	def remove(self, path):
		remotepath = self.remote(path)
		print(' - ', os.path.abspath(remotepath))
		print(os.path.exists(remotepath))
		try:
			os.remove(remotepath)
		except OSError as e: # name the Exception `e`
			print "Failed with:", e.strerror # look what it says
			print "Error code:", e.code
		print(os.path.exists(remotepath))

		
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
		port = properties['port'] if 'port' in properties else '22'
		# # Open a transport
		self.transport = paramiko.Transport((properties['host'], port))
		# # # Auth
		self.transport.connect(username = properties['username'], password = properties['password'])
		# # # Go!
		self.sftp = paramiko.SFTPClient.from_transport(transport)
		self.p = properties

	def get(self, path):
		self.sftp.get(self.remote(remotepath), self.local(localpath))
	def put(self, localpath, remotepath):
		self.sftp.put(self.local(localpath), self.remote(remotepath))
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
	def mkdir(self, remotepath):
		sftp.mkdir(self.remote(remotepath), 0755)
	def remove(self, remotepath):
		raise NotImplementedError	
	def makedirs(self, remotepath):
		path_array = remotepath.split(os.sep)
		chkpath = self.p['remoteroot']
		for part in path_array:
			chkpath = os.path.join(chkpath, part)
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
	m = Migrater()
	# m.set_actions({'A': ['test']})
	# m.actions = {'A': ['test']}
	# pprint(m.actions)
	os.remove('./remote/d.txt')