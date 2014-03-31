Migrater
========================

Summary
-------
Migrater is a Python module to sync up Point B (remote) with Point A (local) based on a list of actions. 

SFTP? FTP? Local? Migrater don't care (just give it the proper configuration).

Concepts
--------

### Properties
`Properties` is a configuration dictionary: 

	{
		"type": "sftp",										# one of local, sftp, or ftp
		"localroot":  "/full/path/to/local/root",			# "Point A" root
		"remoteroot": "/full/path/to/remote/root",			# "Point B" root
		### extra config for ftp/sftp
		"host": "user@example.com",							# required
		"port": 22											# optional (sftp: 22; ftp: ??)
		"password": "secret"								# optional (prompt or keychain)
	}

### Actions
`Actions` are based on the output of 

	$ git diff --name-status ...

For example:

	$ git diff --name-status HEAD HEAD^
	M       README.md
	A       dirfixtures.py
	A       migrate.py
	A       migrater.py
	D       migrater/__init__.py
	D       migrater/migrater.py
	D       migrater/sftp.py
	M       sites/site_id/properties.json
	A       test.py

This shows the *difference* between my last Git commit (`HEAD`) and the previous, (`HEAD^`). In my last commit, for example, I: 

* [A]dded dirfixtures.py
* [D]eleted migrater/sftp.py
* [M]odified README.md

Migrater can accept `actions` in a few ways:

1. Raw text: 

	"M README.md\nA dirfixtures.py\nD migrater/sftp.py"

2. Path to file:

	'~/actions.txt'

3. Migrater compiles the results of either of the following into a dictionary of lists, so you can pass this in directly:


	{
		'A': [ 'dirfixtures.py', ... ],
		'D': [ 'migrater/sftp.py', ... ],
		'M': [ 'README.md', ... ]
	}

The idea being to accept direct Git output or user input conveying the same information. 

Usage
-----














