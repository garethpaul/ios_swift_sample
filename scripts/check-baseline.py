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


def markdown_section(text, heading):
    match = re.search(
        r"(?ms)^## {}\s*$\n(.*?)(?=^## |\Z)".format(re.escape(heading)),
        text,
    )
    return match.group(1).strip() if match else ""


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
        ".github/workflows/check.yml",
        "CHANGES.md",
        ".github/workflows/check.yml",
        "Makefile",
        "README.md",
        "SECURITY.md",
        "VISION.md",
        "docs/plans/2026-06-08-swift-sample-baseline.md",
        "docs/plans/2026-06-08-table-index-guard.md",
        "docs/plans/2026-06-08-artwork-url-tests.md",
        "docs/readme-overview.svg",
        "docs/plans/2026-06-09-api-completion-cleanup.md",
        "docs/plans/2026-06-09-make-gate-aliases.md",
        "docs/plans/2026-06-09-result-array-tests.md",
        "docs/plans/2026-06-09-ui-result-main-thread.md",
        "docs/plans/2026-06-09-async-artwork-loading.md",
        "docs/plans/2026-06-10-network-indicator-lifecycle.md",
        "docs/plans/2026-06-10-ci-baseline.md",
        "docs/plans/2026-06-10-hosted-project-validation.md",
        "docs/plans/2026-06-10-bounded-api-response.md",
        "docs/plans/2026-06-12-active-api-connection.md",
        "docs/plans/2026-06-13-artwork-result-identity-guard.md",
        "docs/plans/2026-06-13-bounded-artwork-response.md",
        "docs/plans/2026-06-13-location-independent-make.md",
        "docs/plans/2026-06-14-artwork-pixel-dimension-boundary.md",
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
    expect("let maximumResponseSize = 1024 * 1024" in api, "ApiController should cap API responses at 1 MiB")
    expect("var responseAccepted = false" in api and "var requestCompleted = false" in api,
           "ApiController should track accepted responses and idempotent completion")
    cancel_active_index = api.find("activeConnection?.cancel()")
    clear_before_search_index = api.find("activeConnection = nil", cancel_active_index)
    assign_connection_index = api.find("activeConnection = connection", clear_before_search_index)
    start_connection_index = api.find("connection.start()", assign_connection_index)
    complete_method_index = api.find("func completeWithResults(results: NSDictionary)")
    clear_on_completion_index = api.find("activeConnection = nil", complete_method_index)
    delegate_completion_index = api.find("delegate?.didRecieveAPIResults(results)", complete_method_index)
    expect("var activeConnection: NSURLConnection?" in api and
           cancel_active_index != -1 and clear_before_search_index != -1 and
           assign_connection_index != -1 and start_connection_index != -1 and
           cancel_active_index < clear_before_search_index < assign_connection_index < start_connection_index and
           clear_on_completion_index != -1 and delegate_completion_index != -1 and
           clear_on_completion_index < delegate_completion_index,
           "ApiController should cancel, assign, and clear active request ownership in order")
    expect("func isActiveConnection(connection: NSURLConnection) -> Bool" in api and
           "if let activeConnection = activeConnection" in api and
           "return connection === activeConnection" in api and
           api.count("if !isActiveConnection(connection)") == 4,
           "ApiController should ignore every delegate callback from non-active connections")
    expect("if requestCompleted" in api and "requestCompleted = true" in api,
           "ApiController should deliver at most one completion per request")
    expect("func isAcceptableResponse(response: NSURLResponse) -> Bool" in api and
           "httpResponse.statusCode >= 200 && httpResponse.statusCode < 300" in api and
           "contentLength > Int64(maximumResponseSize)" in api and
           'mimeType == "application/json" || mimeType == "text/javascript"' in api,
           "ApiController should require successful bounded JSON-compatible responses")
    expect("func canAppendResponseData(chunk: NSData) -> Bool" in api and
           "chunk.length <= maximumResponseSize - data.length" in api,
           "ApiController should bound streamed response accumulation")
    expect(api.count("connection.cancel()") >= 2,
           "ApiController should cancel rejected and oversized responses")
    expect("func connection(connection: NSURLConnection, didFailWithError error: NSError)" in api, "ApiController should implement the failure delegate")
    expect("func connection(connection: NSURLConnection, didReceiveResponse response: NSURLResponse)" in api, "ApiController should clear data on response")
    expect("try NSJSONSerialization.JSONObjectWithData" in api, "ApiController should parse JSON without try!")
    expect("catch {" in api, "ApiController should handle invalid JSON")
    for token in (
        "testAPIResponseValidationAcceptsBoundedJSONSuccess",
        "testAPIResponseValidationRejectsStatusTypeAndOversize",
        "testAPIResponseBufferRejectsOversizeChunks",
        "testAPICompletionIsIdempotent",
    ):
        expect(token in tests, "SwiftExampleTests should cover {}".format(token))

    expect("api.searchItunesFor(" in view, "ViewController should still start the sample search")
    expect("override func viewWillDisappear(animated: Bool)" in view and
           "super.viewWillDisappear(animated)" in view and
           "UIApplication.sharedApplication().networkActivityIndicatorVisible = false" in view,
           "ViewController should clear the network activity indicator when the view disappears")
    expect("if indexPath.row < self.tableData.count" in view, "ViewController should guard table indexes before reading results")
    expect("if let rowData = self.tableData[indexPath.row] as? NSDictionary" in view, "ViewController should optional-cast table rows")
    expect("func artworkURLForRow(indexPath: NSIndexPath) -> NSURL?" in view and
           "indexPath.row < tableData.count" in view and
           'urlString = rowData["artworkUrl60"] as? String' in view,
           "ViewController should resolve safe artwork URLs from the current row")
    expect("safeArtworkURLFromString(urlString)" in view, "ViewController should validate artwork URLs before loading them")
    expect("func safeArtworkURLFromString(urlString: String) -> NSURL?" in view, "ViewController should keep artwork URL validation local")
    expect("scheme == \"https\"" in view and "host.hasSuffix(\".mzstatic.com\")" in view,
           "ViewController should restrict artwork loading to HTTPS mzstatic.com URLs")
    expect("cell.imageView?.image = nil" in view,
           "ViewController should clear reused artwork image views before async artwork loading")
    expect("func loadArtworkFromURL(imgURL: NSURL, forCell cell: UITableViewCell, tableView: UITableView, indexPath: NSIndexPath)" in view,
           "ViewController should keep asynchronous artwork loading in a helper")
    expect("loadArtworkFromURL(imgURL, forCell: cell, tableView: tableView, indexPath: indexPath)" in view,
           "ViewController should route validated artwork URLs through the async loader")
    expect("class ArtworkRequest: NSObject, NSURLConnectionDataDelegate" in view and
           "let maximumResponseSize = 1024 * 1024" in view and
           "timeoutInterval: 15" in view,
           "ArtworkRequest should stream bounded artwork with a finite timeout")
    expect("func isAcceptableResponse(response: NSURLResponse) -> Bool" in view and
           "httpResponse.statusCode >= 200 && httpResponse.statusCode < 300" in view and
           "response.URL where ArtworkRequest.isTrustedURL(responseURL)" in view and
           "contentLength > Int64(maximumResponseSize)" in view and
           'mimeType == "image/jpeg" || mimeType == "image/png"' in view,
           "ArtworkRequest should require trusted successful bounded JPEG or PNG responses")
    expect("func canAppendArtworkData(chunk: NSData) -> Bool" in view and
           "chunk.length <= maximumResponseSize - data.length" in view and
           view.count("connection.cancel()") >= 2,
           "ArtworkRequest should stop rejected or oversized streamed bodies")
    expect("func completeWithData(result: NSData?)" in view and
           "if requestCompleted" in view and "requestCompleted = true" in view and
           "completeWithData(NSData(data: data))" in view,
           "ArtworkRequest should deliver accepted data at most once")
    expect("NSData(contentsOfURL: imgURL)" not in view and
           "ArtworkRequest(URL: imgURL" in view and "request.start()" in view,
           "ViewController should replace unbounded artwork buffering with ArtworkRequest")
    expect("dispatch_get_global_queue" in view and "dispatch_get_main_queue()" in view,
           "ViewController should fetch artwork off the main queue and update UI on the main queue")
    expect("let maximumArtworkDimension = 8192" in view and
           "let maximumArtworkPixelCount = 16 * 1024 * 1024" in view,
           "ViewController should retain reviewed artwork dimension limits")
    expect("func canDisplayArtworkDimensions(width: Int, height: Int) -> Bool" in view and
           "width > 0 && height > 0" in view and
           "width <= maximumArtworkDimension && height <= maximumArtworkDimension" in view and
           "width <= maximumArtworkPixelCount / height" in view and
           "width * height" not in view,
           "ViewController should validate artwork dimensions with overflow-safe arithmetic")
    expect("func isAcceptableArtworkImage(image: UIImage) -> Bool" in view and
           "CGImageGetWidth(cgImage)" in view and "CGImageGetHeight(cgImage)" in view,
           "ViewController should derive artwork dimensions from the constructed image")
    image_guard = view.find("guard let image = UIImage(data: data) where controller.isAcceptableArtworkImage(image)")
    main_publish = view.find("dispatch_async(dispatch_get_main_queue())", image_guard)
    cell_publish = view.find("targetCell.imageView?.image = image", main_publish)
    expect(-1 not in (image_guard, main_publish, cell_publish) and image_guard < main_publish < cell_publish,
           "ViewController should reject oversized artwork before main-thread cell publication")
    expect("targetTableView.indexPathForCell(targetCell)" in view and
           "visibleIndexPath.section == indexPath.section && visibleIndexPath.row == indexPath.row" in view and
           "currentArtworkURL = controller.artworkURLForRow(indexPath)" in view and
           "currentArtworkURL.isEqual(imgURL)" in view,
           "ViewController should only apply async artwork to cells still representing the same current result")
    expect("@testable import SwiftExample" in tests, "SwiftExampleTests should import app code testably")
    expect("testSafeArtworkURLAcceptsHTTPSMZStaticHosts" in tests, "SwiftExampleTests should cover allowed artwork URLs")
    expect("testSafeArtworkURLRejectsUntrustedSchemesAndHosts" in tests, "SwiftExampleTests should cover rejected artwork URLs")
    expect("testArtworkURLForRowTracksCurrentResultIdentity" in tests and
           "testArtworkURLForRowRejectsMissingAndUnsafeRows" in tests,
           "SwiftExampleTests should cover current-row artwork identity")
    for token in (
        "testArtworkResponseValidationAcceptsBoundedImages",
        "testArtworkResponseValidationRejectsStatusTypeAndOversize",
        "testArtworkResponseBufferRejectsOversizeChunks",
        "testArtworkCompletionIsIdempotent",
        "testArtworkDimensionsAcceptExactLimits",
        "testArtworkDimensionsRejectInvalidAxes",
        "testArtworkDimensionsRejectTotalPixelOverflow",
    ):
        expect(token in tests, "SwiftExampleTests should cover {}".format(token))
    for boundary in (
        "canDisplayArtworkDimensions(8192, height: 2048)",
        "canDisplayArtworkDimensions(4096, height: 4096)",
        "canDisplayArtworkDimensions(8193, height: 1)",
        "canDisplayArtworkDimensions(1, height: 8193)",
        "canDisplayArtworkDimensions(8192, height: 2049)",
        "canDisplayArtworkDimensions(Int.max, height: Int.max)",
    ):
        expect(boundary in tests,
               "SwiftExampleTests should preserve artwork dimension boundary {}".format(boundary))
    expect('URL: "https://example.com/artwork.png"' in tests,
           "SwiftExampleTests should reject artwork responses redirected to untrusted hosts")
    expect("XCTAssertNotNil" in tests and "XCTAssertNil" in tests, "SwiftExampleTests should assert artwork URL boundaries")
    expect("testAPIResultsReplaceTableDataWhenResultsArrayPresent" in tests,
           "SwiftExampleTests should cover accepted API result arrays")
    expect("testAPIResultsClearTableDataWhenResultsArrayMissing" in tests,
           "SwiftExampleTests should cover malformed API result payloads")
    expect("XCTAssertEqual(controller.tableData.count, 1)" in tests and
           "XCTAssertEqual(controller.tableData.count, 0)" in tests,
           "SwiftExampleTests should assert result-array table states")
    expect("XCTAssert(true" not in tests and "testPerformanceExample" not in tests,
           "SwiftExampleTests should replace generated placeholder tests")
    expect("if let imageView = cell.imageView" in view, "ViewController should guard image-view styling")
    expect("if let resultsArray = results[\"results\"] as? NSArray" in view, "ViewController should optional-cast result arrays")
    expect("if !NSThread.isMainThread()" in view and
           "dispatch_async(dispatch_get_main_queue())" in view and
           "self.didRecieveAPIResults(results)" in view,
           "ViewController should hop API result UI updates back to the main thread")
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
    make_gates_plan = read_text("docs/plans/2026-06-09-make-gate-aliases.md")
    result_array_tests_plan = read_text("docs/plans/2026-06-09-result-array-tests.md")
    ui_result_plan = read_text("docs/plans/2026-06-09-ui-result-main-thread.md")
    async_artwork_plan = read_text("docs/plans/2026-06-09-async-artwork-loading.md")
    network_indicator_plan = read_text("docs/plans/2026-06-10-network-indicator-lifecycle.md")
    ci_plan = read_text("docs/plans/2026-06-10-ci-baseline.md")
    hosted_validation_plan = read_text("docs/plans/2026-06-10-hosted-project-validation.md")
    bounded_response_plan = read_text("docs/plans/2026-06-10-bounded-api-response.md")
    active_connection_plan = read_text("docs/plans/2026-06-12-active-api-connection.md")
    artwork_identity_plan = read_text("docs/plans/2026-06-13-artwork-result-identity-guard.md")
    bounded_artwork_plan = read_text("docs/plans/2026-06-13-bounded-artwork-response.md")
    location_independent_make_plan = read_text("docs/plans/2026-06-13-location-independent-make.md")
    artwork_dimension_plan = read_text("docs/plans/2026-06-14-artwork-pixel-dimension-boundary.md")
    workflow = read_text(".github/workflows/check.yml")
    gitignore = read_text(".gitignore")
    makefile = read_text("Makefile")

    expect(".PHONY: build check lint test" in makefile and
           "ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))" in makefile and
           "lint test build: check" in makefile and
           'python3 "$(ROOT)/scripts/check-baseline.py"' in makefile and
           "python3 scripts/check-baseline.py" not in makefile,
           "Makefile should expose location-independent lint, test, build, and check verification gates")

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
        expect("main thread" in lowered, "{} should document main-thread UI result handling".format(text_name))
        expect("network activity indicator" in lowered, "{} should document network activity indicator lifecycle".format(text_name))
        expect("result array tests" in lowered, "{} should document result array tests".format(text_name))
        expect("async artwork" in lowered, "{} should document async artwork loading".format(text_name))
        expect("github actions" in lowered, "{} should document hosted static verification".format(text_name))
        expect("active connection" in lowered, "{} should document overlapping request ownership".format(text_name))
        expect("artwork result identity" in lowered, "{} should document stale artwork result rejection".format(text_name))
        expect("bounded artwork" in lowered, "{} should document bounded artwork responses".format(text_name))
        expect("artwork" in lowered and "megapixel" in lowered,
               "{} should document artwork pixel dimension limits".format(text_name))

    expect("make lint" in readme and "make test" in readme and "make build" in readme,
           "README should document the standard local verification gates")
    expect("absolute makefile path" in readme.lower() and
           "location-independent" in changes.lower(),
           "README and CHANGES should document location-independent Make verification")
    expect("make lint" in vision and "make test" in vision and "make build" in vision,
           "VISION should document the standard local verification gates")
    expect("make lint" in changes and "make test" in changes and "make build" in changes,
           "CHANGES should mention the standard local verification gates")
    expect("scripts/check-baseline.py" in readme, "README should name the baseline checker")
    expect("scripts/check-baseline.py" in vision, "VISION should name the baseline checker")
    expect("public HTTPS iTunes" in security, "SECURITY should call out the public HTTPS endpoint boundary")
    expect("mzstatic.com" in readme and "mzstatic.com" in vision and "mzstatic.com" in security,
           "docs should describe the artwork URL host boundary")
    expect("artwork URL tests" in readme, "README should mention artwork URL tests")
    expect("artwork URL tests" in vision, "VISION should mention artwork URL tests")
    expect("artwork URL tests" in security, "SECURITY should mention artwork URL tests")
    expect("result array tests" in readme.lower(), "README should mention result array tests")
    expect("result array tests" in vision.lower(), "VISION should mention result array tests")
    expect("result array tests" in security.lower(), "SECURITY should mention result array tests")
    expect("forced JSON" in changes, "CHANGES should mention forced JSON hardening")
    expect("artwork URL" in changes and "mzstatic.com" in changes, "CHANGES should mention artwork URL hardening")
    expect("artwork URL tests" in changes, "CHANGES should mention artwork URL tests")
    expect("result array tests" in changes.lower(), "CHANGES should mention result array tests")
    expect("response buffer" in changes, "CHANGES should mention API response buffer cleanup")
    expect("main-thread" in changes, "CHANGES should mention main-thread UI result handling")
    expect("network activity indicator" in changes.lower(), "CHANGES should mention network activity indicator lifecycle")
    expect("async artwork" in changes.lower(), "CHANGES should mention async artwork loading")
    expect("GitHub Actions" in changes, "CHANGES should mention hosted static verification")
    expect("table index" in changes, "CHANGES should mention table index hardening")
    expect("shared project data" in changes, "CHANGES should mention shared Xcode scheme cleanup")
    expect("make check" in changes, "CHANGES should mention the new verification command")
    expect("status: completed" in plan, "baseline plan should be marked completed")
    expect("status: completed" in artwork_plan, "artwork URL plan should be marked completed")
    expect("status: completed" in artwork_tests_plan, "artwork URL tests plan should be marked completed")
    expect("status: completed" in table_index_plan, "table index plan should be marked completed")
    expect("status: completed" in completion_cleanup_plan, "API completion cleanup plan should be marked completed")
    expect("status: completed" in make_gates_plan, "make gate aliases plan should be marked completed")
    expect("status: completed" in result_array_tests_plan, "result array tests plan should be marked completed")
    expect("status: completed" in ui_result_plan, "UI result main-thread plan should be marked completed")
    expect("status: completed" in async_artwork_plan, "async artwork loading plan should be marked completed")
    expect("status: completed" in network_indicator_plan, "network activity indicator lifecycle plan should be marked completed")
    expect("status: completed" in ci_plan and "make check" in ci_plan,
           "CI baseline plan should be marked completed with make check verification")
    expect("status: completed" in hosted_validation_plan and "make check" in hosted_validation_plan,
           "hosted validation plan should be marked completed")
    expect("status: completed" in bounded_response_plan and "1 MiB" in bounded_response_plan,
           "bounded API response plan should be marked completed")
    expect("status: completed" in artwork_identity_plan and "All four Make gates" in artwork_identity_plan and
           "hostile mutations" in artwork_identity_plan.lower(),
           "artwork result identity plan should record completed verification")
    artwork_dimension_verification = markdown_section(artwork_dimension_plan, "Verification Results")
    expect("status: completed" in artwork_dimension_plan and
           "all six isolated hostile mutations were rejected" in artwork_dimension_verification.lower() and
           "Xcode was unavailable" in artwork_dimension_verification and
           "No credentials or signing material" in artwork_dimension_verification,
           "artwork dimension plan should record completed local verification")
    expect("over-16-megapixel" in changes and
           "16-megapixel total" in security and
           "16 megapixels" in vision and
           "overflow-safe artwork dimension checks" in read_text("AGENTS.md"),
           "artwork dimension guidance should remain synchronized")
    bounded_artwork_status = re.findall(
        r"(?mi)^status:\s*(.+?)\s*$", bounded_artwork_plan
    )
    bounded_artwork_work = markdown_section(bounded_artwork_plan, "Work Completed")
    bounded_artwork_verification = markdown_section(
        bounded_artwork_plan, "Verification Completed"
    )
    expect(bounded_artwork_status == ["completed"] and bool(bounded_artwork_work),
           "bounded artwork plan should record one completed status and completed work")
    expect(bool(bounded_artwork_verification) and not re.search(
        r"(?i)\b(?:pending|todo|tbd|not run)\b", bounded_artwork_verification
    ), "bounded artwork plan should record finished verification without pending markers")
    for evidence in [
        "make lint",
        "make test",
        "make build",
        "make check",
        "python3 -m py_compile scripts/check-baseline.py",
        "git diff --check",
        "Eight isolated hostile mutations",
        "Xcode was unavailable",
    ]:
        expect(evidence in bounded_artwork_verification,
               "bounded artwork plan should preserve verification evidence: {}".format(evidence))
    location_make_status = re.findall(
        r"(?mi)^status:\s*(.+?)\s*$", location_independent_make_plan
    )
    location_make_verification = markdown_section(
        location_independent_make_plan, "Verification Completed"
    )
    expect(location_make_status == ["completed"] and
           "All four Make gates passed from the checkout" in location_make_verification and
           "All four Make gates passed from `/tmp` through the absolute Makefile path" in location_make_verification and
           "python3 -m py_compile scripts/check-baseline.py" in location_make_verification and
           "project metadata parsing" in location_make_verification and
           "git diff --check" in location_make_verification and
           "`xcodebuild` was unavailable" in location_make_verification and
           "Five isolated hostile mutations were rejected" in location_make_verification and
           re.search(r"(?i)\b(?:pending|todo|tbd|not run)\b", location_make_verification) is None,
           "location-independent Make plan should record completed status and actual local verification")
    active_connection_status = re.findall(
        r"(?mi)^status:\s*(.+?)\s*$", active_connection_plan
    )
    active_connection_work = markdown_section(active_connection_plan, "Work Completed")
    active_connection_verification = markdown_section(
        active_connection_plan, "Verification Completed"
    )
    expect(active_connection_status == ["completed"] and bool(active_connection_work),
           "active API connection plan should record one completed status and completed work")
    expect(bool(active_connection_verification) and not re.search(
        r"(?i)\b(?:pending|todo|tbd|not run)\b", active_connection_verification
    ), "active API connection plan should record finished verification without pending markers")
    for evidence in [
        "make check",
        "make lint",
        "make test",
        "make build",
        "python3 -m py_compile scripts/check-baseline.py",
        "git diff --check",
        "27395635063",
        "27395639989",
        "27395656424",
        "27402323954",
        "ffd99e770c2fcf3923af8a527b60c3f58274b52a",
        "5a179a2125db621355b8a9e062a9de20d1ac875d",
        "activeConnection?.cancel()",
        "if !isActiveConnection(connection)",
    ]:
        expect(evidence in active_connection_verification,
               "active API connection plan should preserve verification evidence: {}".format(evidence))
    expect("permissions:\n  contents: read" in workflow and "cancel-in-progress: true" in workflow and
           "runs-on: macos-15" in workflow and "timeout-minutes: 10" in workflow and
           "actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10" in workflow and
           "persist-credentials: false" in workflow and
           "run: make check" in workflow,
           "Check workflow should stay pinned, read-only, and bounded")
    expect(read_text(".github/CODEOWNERS").strip() == "* @garethpaul",
           "CODEOWNERS should assign repository-wide ownership")
    workflow_files = sorted(str(path.relative_to(ROOT)) for path in rel(".github/workflows").rglob("*") if path.is_file())
    expect(workflow_files == [".github/workflows/check.yml"],
           "check.yml should be the sole hosted workflow")

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
        result = subprocess.run(
            ["xcodebuild", "-list", "-project", "SwiftExample.xcodeproj"],
            cwd=str(ROOT),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
        )
        expect(result.returncode == 0,
               "xcodebuild could not parse SwiftExample.xcodeproj: {}".format(result.stderr.strip()))
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
