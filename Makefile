.PHONY: build check lint test

override ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))

lint test build: check

check:
	python3 "$(ROOT)/scripts/check-baseline.py"
	python3 "$(ROOT)/scripts/test-make-root-override-contract.py"
