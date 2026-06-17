#!/usr/bin/env python3

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ASSIGNMENT = "override ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))"
CHECKER_ASSERTION = 'make_lines.count("override ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))") == 1'


def read(path):
    return (ROOT / path).read_text(encoding="utf-8")


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    makefile = read("Makefile")
    checker = read("scripts/check-baseline.py")
    plan = read("docs/plans/2026-06-17-002-fix-make-root-override-protection-plan.md")
    readme = read("README.md")
    changes = read("CHANGES.md")
    make_lines = [line.strip() for line in makefile.splitlines()]

    require(make_lines.count(ASSIGNMENT) == 1, "Makefile must contain one authoritative root assignment")
    require(not any(line.startswith("ROOT :=") for line in make_lines), "Makefile must reject a normal root assignment")
    require(CHECKER_ASSERTION in checker, "baseline must require the authoritative Make assignment")
    require("status: completed" in plan, "Make root override plan must be completed")
    require("hostile `ROOT=/tmp` override" in plan, "plan must record the hostile override boundary")
    require("hostile `ROOT` command-line override" in readme, "README must document root override protection")
    require("hostile `ROOT=/tmp` override" in changes, "changelog must document root override protection")
    print("Make root override contract passed.")


if __name__ == "__main__":
    main()
