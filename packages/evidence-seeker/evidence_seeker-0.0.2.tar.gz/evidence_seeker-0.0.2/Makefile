build:
	cp pyproject.toml pyproject.toml.bak
	python tools/sync_deps.py
	hatch build
	mv pyproject.toml.bak pyproject.toml
	rm pyproject.toml.bak