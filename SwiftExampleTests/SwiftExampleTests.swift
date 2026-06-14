//
//  SwiftExampleTests.swift
//  SwiftExampleTests
//
//  Created by Gareth Paul Jones on 6/3/14.
//  Copyright (c) 2014 Gareth Paul Jones. All rights reserved.
//

import XCTest
@testable import SwiftExample

private class RecordingAPIDelegate: APIControllerProtocol {
    var completionCount = 0

    func didRecieveAPIResults(results: NSDictionary) {
        completionCount += 1
    }
}

class SwiftExampleTests: XCTestCase {

    func response(statusCode: Int, mimeType: String, contentLength: Int) -> NSHTTPURLResponse {
        return NSHTTPURLResponse(
            URL: NSURL(string: "https://itunes.apple.com/search")!,
            statusCode: statusCode,
            HTTPVersion: "HTTP/1.1",
            headerFields: ["Content-Type": mimeType, "Content-Length": "\(contentLength)"]
        )!
    }

    func testAPIResponseValidationAcceptsBoundedJSONSuccess() {
        let api = APIController()
        XCTAssertTrue(api.isAcceptableResponse(response(200, mimeType: "application/json", contentLength: 1024)))
        XCTAssertTrue(api.isAcceptableResponse(response(200, mimeType: "text/javascript", contentLength: 1024)))
    }

    func testAPIResponseValidationRejectsStatusTypeAndOversize() {
        let api = APIController()
        XCTAssertFalse(api.isAcceptableResponse(response(500, mimeType: "application/json", contentLength: 1024)))
        XCTAssertFalse(api.isAcceptableResponse(response(200, mimeType: "text/html", contentLength: 1024)))
        XCTAssertFalse(api.isAcceptableResponse(response(200, mimeType: "application/json", contentLength: api.maximumResponseSize + 1)))
    }

    func testAPIResponseBufferRejectsOversizeChunks() {
        let api = APIController()
        api.responseAccepted = true
        api.data = NSMutableData(length: api.maximumResponseSize - 1)!

        XCTAssertTrue(api.canAppendResponseData(NSData(length: 1)))
        XCTAssertFalse(api.canAppendResponseData(NSData(length: 2)))
    }

    func testAPICompletionIsIdempotent() {
        let api = APIController()
        let delegate = RecordingAPIDelegate()
        api.delegate = delegate

        api.completeWithResults(NSDictionary())
        api.completeWithResults(NSDictionary())

        XCTAssertEqual(delegate.completionCount, 1)
    }

    func testSafeArtworkURLAcceptsHTTPSMZStaticHosts() {
        let controller = SearchResultsViewController()
        XCTAssertNotNil(controller.safeArtworkURLFromString("https://mzstatic.com/artwork.png"))
        XCTAssertNotNil(controller.safeArtworkURLFromString("https://is1-ssl.mzstatic.com/artwork.png"))
    }

    func testSafeArtworkURLRejectsUntrustedSchemesAndHosts() {
        let controller = SearchResultsViewController()
        XCTAssertNil(controller.safeArtworkURLFromString("http://is1-ssl.mzstatic.com/artwork.png"))
        XCTAssertNil(controller.safeArtworkURLFromString("https://example.com/artwork.png"))
        XCTAssertNil(controller.safeArtworkURLFromString("not a url"))
    }

    func testArtworkURLForRowTracksCurrentResultIdentity() {
        let controller = SearchResultsViewController()
        let indexPath = NSIndexPath(forRow: 0, inSection: 0)
        controller.tableData = NSArray(object: NSDictionary(object: "https://is1-ssl.mzstatic.com/first.png", forKey: "artworkUrl60"))

        XCTAssertEqual(controller.artworkURLForRow(indexPath)?.absoluteString, "https://is1-ssl.mzstatic.com/first.png")

        controller.tableData = NSArray(object: NSDictionary(object: "https://is1-ssl.mzstatic.com/second.png", forKey: "artworkUrl60"))
        XCTAssertEqual(controller.artworkURLForRow(indexPath)?.absoluteString, "https://is1-ssl.mzstatic.com/second.png")
    }

    func testArtworkURLForRowRejectsMissingAndUnsafeRows() {
        let controller = SearchResultsViewController()
        XCTAssertNil(controller.artworkURLForRow(NSIndexPath(forRow: 0, inSection: 0)))

        controller.tableData = NSArray(object: NSDictionary(object: "http://example.com/image.png", forKey: "artworkUrl60"))
        XCTAssertNil(controller.artworkURLForRow(NSIndexPath(forRow: 0, inSection: 0)))
    }

    func artworkResponse(statusCode: Int, mimeType: String, contentLength: Int, URL: String = "https://is1-ssl.mzstatic.com/artwork.png") -> NSHTTPURLResponse {
        return NSHTTPURLResponse(
            URL: NSURL(string: URL)!,
            statusCode: statusCode,
            HTTPVersion: "HTTP/1.1",
            headerFields: ["Content-Type": mimeType, "Content-Length": "\(contentLength)"]
        )!
    }

    func artworkRequest(completion: (NSData?) -> Void = { _ in }) -> ArtworkRequest {
        return ArtworkRequest(
            URL: NSURL(string: "https://is1-ssl.mzstatic.com/artwork.png")!,
            completion: completion
        )!
    }

    func testArtworkResponseValidationAcceptsBoundedImages() {
        let request = artworkRequest()
        XCTAssertTrue(request.isAcceptableResponse(artworkResponse(200, mimeType: "image/jpeg", contentLength: 1024)))
        XCTAssertTrue(request.isAcceptableResponse(artworkResponse(200, mimeType: "image/png", contentLength: 1024)))
    }

    func testArtworkResponseValidationRejectsStatusTypeAndOversize() {
        let request = artworkRequest()
        XCTAssertFalse(request.isAcceptableResponse(artworkResponse(500, mimeType: "image/jpeg", contentLength: 1024)))
        XCTAssertFalse(request.isAcceptableResponse(artworkResponse(200, mimeType: "text/html", contentLength: 1024)))
        XCTAssertFalse(request.isAcceptableResponse(artworkResponse(200, mimeType: "image/png", contentLength: request.maximumResponseSize + 1)))
        XCTAssertFalse(request.isAcceptableResponse(artworkResponse(200, mimeType: "image/png", contentLength: 1024, URL: "https://example.com/artwork.png")))
    }

    func testArtworkResponseBufferRejectsOversizeChunks() {
        let request = artworkRequest()
        request.responseAccepted = true
        request.data = NSMutableData(length: request.maximumResponseSize - 1)!

        XCTAssertTrue(request.canAppendArtworkData(NSData(length: 1)))
        XCTAssertFalse(request.canAppendArtworkData(NSData(length: 2)))
    }

    func testArtworkDimensionsAcceptExactLimits() {
        let controller = SearchResultsViewController()

        XCTAssertTrue(controller.canDisplayArtworkDimensions(8192, height: 2048))
        XCTAssertTrue(controller.canDisplayArtworkDimensions(4096, height: 4096))
    }

    func testArtworkDimensionsRejectInvalidAxes() {
        let controller = SearchResultsViewController()

        XCTAssertFalse(controller.canDisplayArtworkDimensions(0, height: 1))
        XCTAssertFalse(controller.canDisplayArtworkDimensions(1, height: 0))
        XCTAssertFalse(controller.canDisplayArtworkDimensions(8193, height: 1))
        XCTAssertFalse(controller.canDisplayArtworkDimensions(1, height: 8193))
    }

    func testArtworkDimensionsRejectTotalPixelOverflow() {
        let controller = SearchResultsViewController()

        XCTAssertFalse(controller.canDisplayArtworkDimensions(8192, height: 2049))
        XCTAssertFalse(controller.canDisplayArtworkDimensions(Int.max, height: Int.max))
    }

    func testArtworkCompletionIsIdempotent() {
        var completionCount = 0
        let request = artworkRequest { _ in completionCount += 1 }

        request.completeWithData(NSData())
        request.completeWithData(nil)

        XCTAssertEqual(completionCount, 1)
    }

    func testAPIResultsReplaceTableDataWhenResultsArrayPresent() {
        let controller = SearchResultsViewController()
        let result = NSDictionary(object: "Angry Birds", forKey: "trackName")
        let results = NSArray(object: result)

        controller.didRecieveAPIResults(NSDictionary(object: results, forKey: "results"))

        XCTAssertEqual(controller.tableData.count, 1)
        if let firstResult = controller.tableData.firstObject as? NSDictionary {
            XCTAssertEqual(firstResult["trackName"] as? String, "Angry Birds")
        } else {
            XCTFail("Expected first API result")
        }
    }

    func testAPIResultsClearTableDataWhenResultsArrayMissing() {
        let controller = SearchResultsViewController()
        controller.tableData = NSArray(object: NSDictionary(object: "Stale", forKey: "trackName"))

        controller.didRecieveAPIResults(NSDictionary(object: "not an array", forKey: "results"))

        XCTAssertEqual(controller.tableData.count, 0)
    }

}
