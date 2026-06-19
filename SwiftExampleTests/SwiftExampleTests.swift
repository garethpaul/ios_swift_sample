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

    func response(statusCode: Int, mimeType: String, contentLength: Int, URL: String = "https://itunes.apple.com/search") -> NSHTTPURLResponse {
        return NSHTTPURLResponse(
            URL: NSURL(string: URL)!,
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

    func testSearchRequestUsesBoundedUncachedPolicy() {
        let controller = APIController()
        let url = NSURL(string: "https://itunes.apple.com/search?term=weather&media=software")!

        let request = controller.requestForSearchURL(url)

        XCTAssertTrue(request.URL?.isEqual(url) == true)
        XCTAssertEqual(request.cachePolicy, NSURLRequestCachePolicy.ReloadIgnoringLocalCacheData)
        XCTAssertEqual(request.timeoutInterval, 15)
    }

    func testSearchTermValidationRejectsEmptyControlAndOversizedInput() {
        let controller = APIController()

        XCTAssertTrue(controller.isAcceptableSearchTerm("Angry Birds"))
        XCTAssertFalse(controller.isAcceptableSearchTerm(""))
        XCTAssertFalse(controller.isAcceptableSearchTerm("   \n"))
        XCTAssertFalse(controller.isAcceptableSearchTerm(String(count: controller.maximumSearchTermLength + 1, repeatedValue: Character("a"))))
        XCTAssertFalse(controller.isAcceptableSearchTerm("a" + String(count: controller.maximumSearchTermByteLength, repeatedValue: Character("\u{0301}"))))
    }

    func testAPIResponseValidationRejectsStatusTypeAndOversize() {
        let api = APIController()
        XCTAssertFalse(api.isAcceptableResponse(response(500, mimeType: "application/json", contentLength: 1024)))
        XCTAssertFalse(api.isAcceptableResponse(response(200, mimeType: "text/html", contentLength: 1024)))
        XCTAssertFalse(api.isAcceptableResponse(response(200, mimeType: "application/json", contentLength: api.maximumResponseSize + 1)))
    }

    func testAPIResponseValidationAcceptsTrustedSearchAuthority() {
        let api = APIController()

        XCTAssertTrue(api.isAcceptableResponse(response(200, mimeType: "application/json", contentLength: 1024, URL: "https://ITUNES.APPLE.COM/search?term=weather&media=software")))
    }

    func testAPIResponseValidationRejectsUntrustedSearchAuthorities() {
        let api = APIController()

        XCTAssertFalse(api.isAcceptableResponse(response(200, mimeType: "application/json", contentLength: 1024, URL: "http://itunes.apple.com/search")))
        XCTAssertFalse(api.isAcceptableResponse(response(200, mimeType: "application/json", contentLength: 1024, URL: "https://example.com/search")))
        XCTAssertFalse(api.isAcceptableResponse(response(200, mimeType: "application/json", contentLength: 1024, URL: "https://user@itunes.apple.com/search")))
        XCTAssertFalse(api.isAcceptableResponse(response(200, mimeType: "application/json", contentLength: 1024, URL: "https://user:credential@itunes.apple.com/search")))
        XCTAssertFalse(api.isAcceptableResponse(response(200, mimeType: "application/json", contentLength: 1024, URL: "https://itunes.apple.com:443/search")))
        XCTAssertFalse(api.isAcceptableResponse(response(200, mimeType: "application/json", contentLength: 1024, URL: "https://itunes.apple.com/lookup")))
        XCTAssertFalse(api.isAcceptableResponse(response(200, mimeType: "application/json", contentLength: 1024, URL: "https://itunes.apple.com/search#results")))
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

    func testSafeArtworkURLRejectsUserinfoAndExplicitPorts() {
        let controller = SearchResultsViewController()
        XCTAssertNil(controller.safeArtworkURLFromString("https://user@is1-ssl.mzstatic.com/artwork.png"))
        XCTAssertNil(controller.safeArtworkURLFromString("https://user:credential@is1-ssl.mzstatic.com/artwork.png"))
        XCTAssertNil(controller.safeArtworkURLFromString("https://is1-ssl.mzstatic.com:443/artwork.png"))
    }

    func testSafeArtworkURLRejectsFragmentsAndOversizedURLs() {
        let controller = SearchResultsViewController()

        XCTAssertNil(controller.safeArtworkURLFromString("https://is1-ssl.mzstatic.com/artwork.png#fragment"))
        XCTAssertNil(controller.safeArtworkURLFromString("https://is1-ssl.mzstatic.com/" + String(count: controller.maximumArtworkURLLength, repeatedValue: Character("a"))))
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
        XCTAssertFalse(request.isAcceptableResponse(artworkResponse(200, mimeType: "image/png", contentLength: 1024, URL: "https://user@is1-ssl.mzstatic.com/artwork.png")))
        XCTAssertFalse(request.isAcceptableResponse(artworkResponse(200, mimeType: "image/png", contentLength: 1024, URL: "https://is1-ssl.mzstatic.com:443/artwork.png")))
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

    func testArtworkMetadataRejectsPixelBombBeforeImageDecode() {
        let controller = SearchResultsViewController()
        let oversizedPNG = NSData(bytes: [
            0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a,
            0x00, 0x00, 0x00, 0x0d, 0x49, 0x48, 0x44, 0x52,
            0x00, 0x00, 0x23, 0x29, 0x00, 0x00, 0x23, 0x29,
            0x08, 0x02, 0x00, 0x00, 0x00
        ] as [UInt8], length: 29)

        XCTAssertFalse(controller.isAcceptableArtworkData(oversizedPNG))
    }

    func testResultArrayIsBounded() {
        let controller = SearchResultsViewController()
        let results = NSMutableArray()
        for index in 0...controller.maximumResultCount {
            results.addObject(NSDictionary(object: index, forKey: "trackId"))
        }

        controller.didRecieveAPIResults(NSDictionary(object: results, forKey: "results"))

        XCTAssertEqual(controller.tableData.count, controller.maximumResultCount)
    }

    func testArtworkCancellationCompletesWithoutData() {
        var completionCount = 0
        var completionData: NSData? = NSData()
        let request = artworkRequest {
            completionCount += 1
            completionData = $0
        }

        request.cancel()
        request.completeWithData(NSData())

        XCTAssertEqual(completionCount, 1)
        XCTAssertNil(completionData)
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
