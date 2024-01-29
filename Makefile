# ----------------------------------
#          INSTALL & TEST
# ----------------------------------
pre-commit:
	@pre-commit run --file `find . -name "*.py"`
	@pre-commit run check-yaml --file `find . -name "*.y*ml"`