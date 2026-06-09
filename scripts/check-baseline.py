#!/usr/bin/env python3
"""Static baseline checks for the legacy Swift iTunes sample."""

from __future__ import print_function

import json
import plistlib
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FAILURES = []


def rel(path):
    return ROOT / path


def expect(condition, message):
    if not condition:
        FAILURES.append(message)


def read_text(path):
    target = rel(path)
    expect(target.exists(), "{} is missing".format(path))
    if not target.exists():
        return ""
    return target.read_text(encoding="utf-8")


def parse_xml(path):
    target = rel(path)
    expect(target.exists(), "{} is missing".format(path))
    if not target.exists():
        return None
    try:
        return ET.parse(str(target))
    except ET.ParseError as exc:
        FAILURES.append("{} is not valid XML: {}".format(path, exc))
        return None


def parse_json(path):
    target = rel(path)
    expect(target.exists(), "{} is missing".format(path))
    if not target.exists():
        return None
    try:
        return json.loads(target.read_text(encoding="utf-8"))
    except ValueError as exc:
        FAILURES.append("{} is not valid JSON: {}".format(path, exc))
        return None


def parse_plist(path):
    target = rel(path)
    expect(target.exists(), "{} is missing".format(path))
    if not target.exists():
        return None
    try:
        with target.open("rb") as handle:
            return plistlib.load(handle)
    except Exception as exc:
        FAILURES.append("{} is not a valid plist: {}".format(path, exc))
        return None


def strip_swift_comments(text):
    lines = []
    for line in text.splitlines():
        if line.lstrip().startswith("//"):
            lines.append("")
        else:
            lines.append(line)
    return "\n".join(lines)


def git_ls_files():
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=str(ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if result.returncode != 0:
        FAILURES.append("git ls-files failed: {}".format(result.stderr.strip()))
        return set()
    return set(result.stdout.splitlines())


def check_required_files():
    required = [
        ".gitignore",
        "CHANGES.md",
        "Makefile",
        "README.md",
        "SECURITY.md",
        "VISION.md",
        "docs/plans/2026-06-08-swift-sample-baseline.md",
        "docs/plans/2026-06-08-table-index-guard.md",
        "docs/plans/2026-06-08-artwork-url-tests.md",
        "docs/readme-overview.svg",
        "docs/plans/2026-06-09-api-completion-cleanup.md",
        "SwiftExample.xcodeproj/project.pbxproj",
        "SwiftExample.xcodeproj/project.xcworkspace/contents.xcworkspacedata",
        "SwiftExample.xcodeproj/xcshareddata/xcschemes/SwiftExample.xcscheme",
        "SwiftExample/ApiController.swift",
        "SwiftExample/AppDelegate.swift",
        "SwiftExample/Base.lproj/Main.storyboard",
        "SwiftExample/Images.xcassets/AppIcon.appiconset/Contents.json",
        "SwiftExample/Images.xcassets/LaunchImage.launchimage/Contents.json",
        "SwiftExample/Info.plist",
        "SwiftExample/ViewController.swift",
        "SwiftExampleTests/Info.plist",
        "SwiftExampleTests/SwiftExampleTests.swift",
        "docs/plans/2026-06-08-artwork-url-boundary.md",
    ]

    for path in required:
        expect(rel(path).exists(), "{} is missing".format(path))


def check_parsable_resources():
    parse_xml("docs/readme-overview.svg")
    parse_xml("SwiftExample.xcodeproj/project.xcworkspace/contents.xcworkspacedata")
    parse_xml("SwiftExample.xcodeproj/xcshareddata/xcschemes/SwiftExample.xcscheme")
    parse_xml("SwiftExample/Base.lproj/Main.storyboard")

    app_plist = parse_plist("SwiftExample/Info.plist")
    test_plist = parse_plist("SwiftExampleTests/Info.plist")
    app_icon = parse_json("SwiftExample/Images.xcassets/AppIcon.appiconset/Contents.json")
    launch_image = parse_json("SwiftExample/Images.xcassets/LaunchImage.launchimage/Contents.json")

    if app_plist:
        expect(app_plist.get("CFBundlePackageType") == "APPL", "app Info.plist should describe an application")
        expect(app_plist.get("UIMainStoryboardFile") == "Main", "app Info.plist should point at Main storyboard")
        expect("NSLocation" not in "\n".join(app_plist.keys()), "app Info.plist should not request location usage")

    if test_plist:
        expect(test_plist.get("CFBundlePackageType") == "BNDL", "test Info.plist should describe a bundle")

    if app_icon:
        images = app_icon.get("images", [])
        idioms = {image.get("idiom") for image in images}
        expect("iphone" in idioms and "ipad" in idioms, "AppIcon asset should keep iPhone and iPad slots")

    if launch_image:
        images = launch_image.get("images", [])
        orientations = {image.get("orientation") for image in images}
        expect("portrait" in orientations, "LaunchImage asset should include portrait launch images")
        expect("landscape" in orientations, "LaunchImage asset should include landscape launch images")


def check_project_wiring():
    pbxproj = read_text("SwiftExample.xcodeproj/project.pbxproj")

    for source in ("AppDelegate.swift", "ViewController.swift", "ApiController.swift"):
        expect(source in pbxproj, "{} should remain in the Xcode project".format(source))
        expect("{} in Sources".format(source) in pbxproj, "{} should be compiled in the app target".format(source))

    expect("Main.storyboard in Resources" in pbxproj, "Main.storyboard should be an app resource")
    expect("Images.xcassets in Resources" in pbxproj, "Images.xcassets should be an app resource")
    expect("INFOPLIST_FILE = SwiftExample/Info.plist;" in pbxproj, "app plist should stay wired in project settings")
    expect("INFOPLIST_FILE = SwiftExampleTests/Info.plist;" in pbxproj, "test plist should stay wired in project settings")
    expect("IPHONEOS_DEPLOYMENT_TARGET = 8.0;" in pbxproj, "legacy deployment target should remain visible")
    expect("LastSwiftMigration = 0720;" in pbxproj, "legacy Swift migration marker should remain visible")

    scheme = read_text("SwiftExample.xcodeproj/xcshareddata/xcschemes/SwiftExample.xcscheme")
    expect('BlueprintName = "SwiftExample"' in scheme, "shared scheme should build the app target")
    expect('BlueprintName = "SwiftExampleTests"' in scheme, "shared scheme should include the test target")
    expect('allowLocationSimulation = "NO"' in scheme, "shared scheme should not simulate location for this sample")


def check_storyboard_contract():
    storyboard = read_text("SwiftExample/Base.lproj/Main.storyboard")
    expect('customClass="SearchResultsViewController"' in storyboard, "storyboard should use SearchResultsViewController")
    expect('outlet property="appsTableView"' in storyboard, "storyboard should wire the table view outlet")
    expect('outlet property="dataSource"' in storyboard, "storyboard should wire the table data source")
    expect('outlet property="delegate"' in storyboard, "storyboard should wire the table delegate")
    expect("<tableView " in storyboard, "storyboard should keep the table view")


def check_first_party_swift():
    swift_paths = sorted(rel("SwiftExample").glob("*.swift")) + sorted(rel("SwiftExampleTests").glob("*.swift"))
    raw_source_by_name = {}
    source_by_name = {}
    stripped_source = []
    for path in swift_paths:
        text = path.read_text(encoding="utf-8")
        stripped = strip_swift_comments(text)
        raw_source_by_name[path.name] = text
        source_by_name[path.name] = stripped
        stripped_source.append(stripped)

    all_source = "\n".join(stripped_source)
    api_raw = raw_source_by_name.get("ApiController.swift", "")
    api = source_by_name.get("ApiController.swift", "")
    view = source_by_name.get("ViewController.swift", "")
    tests = source_by_name.get("SwiftExampleTests.swift", "")

    expect("import CoreLocation" not in all_source, "first-party Swift should not import unused location APIs")
    expect(
        not re.search(r"\b(?:print|println|NSLog)\s*\(", all_source),
        "first-party Swift should not log network failure details",
    )
    for token in ("try!", "as!", "NSURL(string: urlPath)!", "NSData(contentsOfURL: imgURL)!", "appsTableView!", "cell.imageView!"):
        expect(token not in all_source, "first-party Swift should not use forced path {}".format(token))

    for term in ("apiKey", "APIKey", "token", "secret", "password", "Authorization"):
        expect(term not in all_source, "first-party Swift should not include credential term {}".format(term))

    expect("https://itunes.apple.com/search" in api_raw, "ApiController should keep the public HTTPS iTunes search endpoint")
    expect("NSCharacterSet(charactersInString:" in api, "ApiController should use an explicit search-term encoding allowlist")
    expect("if let escapedSearchTerm" in api, "ApiController should handle failed term encoding")
    expect("if let url = NSURL(string: urlPath)" in api, "ApiController should handle failed URL creation")
    expect("if let connection = NSURLConnection" in api, "ApiController should handle failed connection creation")
    expect("func completeWithResults(results: NSDictionary)" in api, "ApiController should centralize API completion")
    expect("delegate?.didRecieveAPIResults(results)" in api, "ApiController should deliver parsed results through completion helper")
    expect("completeWithResults(NSDictionary())" in api, "ApiController should return empty results on failure")
    expect("completeWithResults(jsonResult)" in api, "ApiController should deliver parsed JSON through completion helper")
    expect("self.data = NSMutableData()" in api, "ApiController should clear retained response data after completion")
    expect("func connection(connection: NSURLConnection, didFailWithError error: NSError)" in api, "ApiController should implement the failure delegate")
    expect("func connection(connection: NSURLConnection, didReceiveResponse response: NSURLResponse)" in api, "ApiController should clear data on response")
    expect("try NSJSONSerialization.JSONObjectWithData" in api, "ApiController should parse JSON without try!")
    expect("catch {" in api, "ApiController should handle invalid JSON")

    expect("api.searchItunesFor(" in view, "ViewController should still start the sample search")
    expect("if indexPath.row < self.tableData.count" in view, "ViewController should guard table indexes before reading results")
    expect("if let rowData = self.tableData[indexPath.row] as? NSDictionary" in view, "ViewController should optional-cast table rows")
    expect("if let urlString = rowData[\"artworkUrl60\"] as? String" in view, "ViewController should optional-cast artwork URL")
    expect("safeArtworkURLFromString(urlString)" in view, "ViewController should validate artwork URLs before loading them")
    expect("func safeArtworkURLFromString(urlString: String) -> NSURL?" in view, "ViewController should keep artwork URL validation local")
    expect("scheme == \"https\"" in view and "host.hasSuffix(\".mzstatic.com\")" in view,
           "ViewController should restrict artwork loading to HTTPS mzstatic.com URLs")
    expect("@testable import SwiftExample" in tests, "SwiftExampleTests should import app code testably")
    expect("testSafeArtworkURLAcceptsHTTPSMZStaticHosts" in tests, "SwiftExampleTests should cover allowed artwork URLs")
    expect("testSafeArtworkURLRejectsUntrustedSchemesAndHosts" in tests, "SwiftExampleTests should cover rejected artwork URLs")
    expect("XCTAssertNotNil" in tests and "XCTAssertNil" in tests, "SwiftExampleTests should assert artwork URL boundaries")
    expect("XCTAssert(true" not in tests and "testPerformanceExample" not in tests,
           "SwiftExampleTests should replace generated placeholder tests")
    expect("if let imageView = cell.imageView" in view, "ViewController should guard image-view styling")
    expect("if let resultsArray = results[\"results\"] as? NSArray" in view, "ViewController should optional-cast result arrays")
    expect("self.appsTableView?.reloadData()" in view, "ViewController should reload the table view safely")
    expect("networkActivityIndicatorVisible = false" in view, "ViewController should clear the network activity indicator")


def check_docs():
    readme = read_text("README.md")
    vision = read_text("VISION.md")
    security = read_text("SECURITY.md")
    changes = read_text("CHANGES.md")
    plan = read_text("docs/plans/2026-06-08-swift-sample-baseline.md")
    artwork_plan = read_text("docs/plans/2026-06-08-artwork-url-boundary.md")
    artwork_tests_plan = read_text("docs/plans/2026-06-08-artwork-url-tests.md")
    table_index_plan = read_text("docs/plans/2026-06-08-table-index-guard.md")
    completion_cleanup_plan = read_text("docs/plans/2026-06-09-api-completion-cleanup.md")
    gitignore = read_text(".gitignore")

    for text_name, text in (
        ("README.md", readme),
        ("VISION.md", vision),
        ("SECURITY.md", security),
    ):
        lowered = text.lower()
        expect("make check" in lowered, "{} should document the static verification command".format(text_name))
        expect("itunes" in lowered, "{} should document the iTunes Search API sample".format(text_name))
        expect("credential" in lowered or "secret" in lowered, "{} should document credential handling".format(text_name))
        expect("failure" in lowered, "{} should document network or JSON failure handling".format(text_name))

    expect("scripts/check-baseline.py" in readme, "README should name the baseline checker")
    expect("scripts/check-baseline.py" in vision, "VISION should name the baseline checker")
    expect("public HTTPS iTunes" in security, "SECURITY should call out the public HTTPS endpoint boundary")
    expect("mzstatic.com" in readme and "mzstatic.com" in vision and "mzstatic.com" in security,
           "docs should describe the artwork URL host boundary")
    expect("artwork URL tests" in readme, "README should mention artwork URL tests")
    expect("artwork URL tests" in vision, "VISION should mention artwork URL tests")
    expect("artwork URL tests" in security, "SECURITY should mention artwork URL tests")
    expect("forced JSON" in changes, "CHANGES should mention forced JSON hardening")
    expect("artwork URL" in changes and "mzstatic.com" in changes, "CHANGES should mention artwork URL hardening")
    expect("artwork URL tests" in changes, "CHANGES should mention artwork URL tests")
    expect("response buffer" in changes, "CHANGES should mention API response buffer cleanup")
    expect("table index" in changes, "CHANGES should mention table index hardening")
    expect("shared project data" in changes, "CHANGES should mention shared Xcode scheme cleanup")
    expect("make check" in changes, "CHANGES should mention the new verification command")
    expect("status: completed" in plan, "baseline plan should be marked completed")
    expect("status: completed" in artwork_plan, "artwork URL plan should be marked completed")
    expect("status: completed" in artwork_tests_plan, "artwork URL tests plan should be marked completed")
    expect("status: completed" in table_index_plan, "table index plan should be marked completed")
    expect("status: completed" in completion_cleanup_plan, "API completion cleanup plan should be marked completed")

    for pattern in ("DerivedData/", "xcuserdata/", "*.local.xcconfig", "*.secrets.xcconfig", ".env", ".env.*", "__pycache__/", "*.pyc"):
        expect(pattern in gitignore, ".gitignore should keep {} out of git".format(pattern))


def check_git_hygiene():
    tracked_files = git_ls_files()
    expect(
        not any("/xcuserdata/" in path or path.endswith(".xcuserstate") for path in tracked_files),
        "user-specific Xcode state should not be tracked",
    )


def main():
    check_required_files()
    check_parsable_resources()
    check_project_wiring()
    check_storyboard_contract()
    check_first_party_swift()
    check_docs()
    check_git_hygiene()

    if shutil.which("xcodebuild"):
        print("xcodebuild is available; run a simulator build separately for legacy Swift validation.")
    else:
        print("xcodebuild unavailable; skipping legacy iOS build/test and using static baseline checks.")

    if FAILURES:
        print("Static baseline failed:")
        for failure in FAILURES:
            print("- {}".format(failure))
        return 1

    print("Static baseline passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
