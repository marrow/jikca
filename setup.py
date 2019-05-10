#!/usr/bin/env python3
# encoding: utf-8

from setuptools import setup
from sys import argv, version_info as python_version
from pathlib import Path



if python_version < (3, 6):
	raise SystemExit("Python 3.6 or later is required.")

here = Path.cwd()
version = description = url = author = ''  # Actually loaded on the next line; be quiet, linter.
exec((here / "jikca" / "release.py").read_text('utf-8'))


tests_require = [
		'pytest',  # test collector and extensible runner
		'pytest-cov',  # coverage reporting
		'pytest-flakes',  # syntax validation
		'pytest-isort',  # import ordering
		'pytest-asyncio',  # asynchonous i/o support
		'pygments',  # Markdown field support
		'pytz', 'tzlocal>=1.4',  # timezone support, logger support
	]


setup(
	name = "jikca",
	version = version,
	description = description,
	long_description = (here / 'README.md').read_text('utf-8'),
	url = url,
	author = author.name,
	author_email = author.email,
	license = 'MIT',
	keywords = [
			'mush',
			'mux',
			'muck',
			'moo',
			'mud',
			'text adventure',
			'mutliplayer',
			'game',
			'server',
		],
	classifiers = [
			"Development Status :: 1 - Planning",
			"Intended Audience :: Developers",
			"License :: OSI Approved :: MIT License",
			"Operating System :: OS Independent",
			"Programming Language :: Python",
			"Programming Language :: Python :: 3.6",
			"Programming Language :: Python :: 3.7",
			"Programming Language :: Python :: Implementation :: CPython",
			"Programming Language :: Python :: Implementation :: PyPy",
			"Topic :: Software Development :: Libraries :: Python Modules",
			"Topic :: Utilities",
		],
	
	packages = ('jikca', ),
	include_package_data = True,
	package_data = {'': ['README.md', 'LICENSE.txt']},
	zip_safe = False,
	
	# ## Dependency Declaration
	
	setup_requires = [
			'pytest-runner',
		] if {'pytest', 'test', 'ptr'}.intersection(sys.argv) else [],
	
	install_requires = [
			'typeguard',  # Variable type annotation enforcement.
			'apscheduler',  # Scheduled and periodic event triggering.
			'anyio',  # Asyncronous I/O utilities and interop.
			'aiomonitor',  # Diagnostic utility to REPL running server.
			'asyncio_extras',  # Additional asynchornous utilities.
			'async-timeout',  # Timeouts on asynchronous requests.
			'marrow.mongo',  # Data modelling and database connectivity.
			'motor',  # Asynchonous MongoDB connectivity.
			'WebCore>=2.0',  # Web framework.
			'pygments',  # Syntax coloured output support.
		],
	
	extras_require = dict(
			development = tests_require + ['pre-commit', 'bandit', 'twine'],  # Development-time dependencies.
		),
	
	tests_require = tests_require,
	
	# ## Plugin Registration
	
	entry_points = {
			},
)
