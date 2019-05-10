PROJECT = jikca
USE = development,logger

.PHONY: all develop clean veryclean test start stop restart status backup freeze thaw vip public release

all: clean develop test

develop: ${PROJECT}.egg-info/PKG-INFO

clean:
	find . -name __pycache__ -exec rm -rfv {} +
	find . -iname \*.pyc -exec rm -fv {} +
	find . -iname \*.pyo -exec rm -fv {} +
	rm -rvf build htmlcov

veryclean: clean
	rm -rvf *.egg-info .packaging/*

test: develop
	@clear
	@pytest

start:
	echo "NOP"

stop:
	echo "NOP"

restart: stop start

status:
	echo "NOP"

backup:
	echo "NOP"

restore:
	echo "NOP"

freeze:
	# Prevent account/character creation.
	echo "NOP"

thaw:
	# Permit account/character creation.
	echo "NOP"

vip:
	# Only allow access by accounts with status.
	echo "NOP"

public:
	# Allow access by all accounts.
	echo "NOP"

release:
	./setup.py sdist bdist_wheel ${RELEASE_OPTIONS}

${PROJECT}.egg-info/PKG-INFO: setup.py setup.cfg jikca/release.py
	@mkdir -p ${VIRTUAL_ENV}/lib/pip-cache
	pip install --cache-dir "${VIRTUAL_ENV}/lib/pip-cache" -Ue ".[${USE}]"