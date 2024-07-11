
test::
	pytest tests/test*.py
	pytest tests/tests_flexdatetime
	pytest tests/tests_flextime

format::
	toml-sort pyproject.toml

build:: format
	poetry build

publish:: build
	poetry publish