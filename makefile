.PHONY: all clean test deps

all: clean

clean:
	rm -rf MANIFEST
	rm -rf dist
	rm -rf venv
	rm -rf hyperspace.egg-info
	find . -iname '*.pyc' -delete

venv:
	virtualenv -p python3 venv

venv/bin/pip: venv

venv/bin/python: venv

deps: venv/bin/pip
	venv/bin/pip install -e .

test: venv/bin/python deps
	venv/bin/nosetests

dist: test
	venv/bin/python setup.py sdist
