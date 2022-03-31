SHELL := /bin/bash #to be able to execute `source`

.PHONY: build clean test upload docs
build: clean
	python setup.py  sdist bdist_wheel

clean:
	rm -rf dist */*.egg-info *.egg-info  build
	rm -rf .test

test: build
	twine check dist/*
	# twine upload --repository-url https://test.pypi.org/legacy/ dist/* --verbose
	virtualenv .test
	source .test/bin/activate
	pip install pyxdf
	pip install -r tests/requirements.txt
	pip install git+https://github.com/labstreaminglayer/liblsl-Python.git
	pip install dist/*.whl
	pytest

upload: build
	twine check dist/*
	twine upload dist/* --verbose

docs:
	make -C docs html
