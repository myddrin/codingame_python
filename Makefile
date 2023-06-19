tests:
	pytest -m 'not slow'

check-style-python-ci:
	flake8

isort:
	isort -y
