#!/usr/bin/env python3
"""Mutation checks for security-sensitive static Swift contracts."""

from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
MUTATIONS = [
    (
        "allow HTTP artwork",
        "SwiftExample/ViewController.swift",
        'return scheme == "https" && (host == "mzstatic.com" || host.hasSuffix(".mzstatic.com"))',
        'return (scheme == "https" || scheme == "http") && (host == "mzstatic.com" || host.hasSuffix(".mzstatic.com"))',
        "ViewController should restrict artwork loading to HTTPS mzstatic.com URLs",
    ),
    (
        "remove artwork generation guard",
        "SwiftExample/ViewController.swift",
        "if controller.artworkGeneration == generation,",
        "if true,",
        "ViewController should reject stale artwork from an earlier result generation",
    ),
    (
        "remove disappearance generation invalidation",
        "SwiftExample/ViewController.swift",
        "api.cancel()\n        artworkGeneration += 1\n        cancelArtworkRequests()",
        "api.cancel()\n        cancelArtworkRequests()",
        "ViewController should invalidate queued artwork publication before disappearance cancellation",
    ),
]


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def run_checker(checkout):
    runner = (
        "import runpy, shutil, sys; "
        "real_which = shutil.which; "
        "shutil.which = lambda name: None if name == 'xcodebuild' else real_which(name); "
        "runpy.run_path(sys.argv[1], run_name='__main__')"
    )
    return subprocess.run(
        [sys.executable, "-c", runner, str(checkout / "scripts/check-baseline.py")],
        cwd=str(checkout),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


def main():
    for name, relative_path, original, replacement, expected_failure in MUTATIONS:
        with tempfile.TemporaryDirectory(prefix="ios-swift-sample-mutation-") as temp_dir:
            checkout = Path(temp_dir) / "checkout"
            shutil.copytree(ROOT, checkout, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
            target = checkout / relative_path
            source = target.read_text(encoding="utf-8")
            require(source.count(original) == 1, "{} mutation target drifted".format(name))
            target.write_text(source.replace(original, replacement, 1), encoding="utf-8")

            result = run_checker(checkout)
            output = result.stdout + result.stderr
            require(result.returncode != 0, "{} mutation unexpectedly passed".format(name))
            require(expected_failure in output, "{} failed for the wrong reason".format(name))

    print("Rejected {} static contract mutations.".format(len(MUTATIONS)))


if __name__ == "__main__":
    main()
