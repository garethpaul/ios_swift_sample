.PHONY: build check lint test

lint test build: check

check:
	python3 scripts/check-baseline.py
