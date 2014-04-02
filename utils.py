import os


# trying to bring jQuery.extend to Python
def extend(defaults, opts):
	"""Create a new dictionary with a's properties extended by b,
	without overwriting.

	>>> extend({'a':1,'b':2},{'b':3,'c':4})
	{'a': 1, 'c': 4, 'b': 2}
	http://stackoverflow.com/a/12697215
	"""
	return dict(defaults,**opts)

def fixPath(path):
	return path.replace('~', os.path.expanduser("~"), 1)