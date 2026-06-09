//
//  SwiftExampleTests.swift
//  SwiftExampleTests
//
//  Created by Gareth Paul Jones on 6/3/14.
//  Copyright (c) 2014 Gareth Paul Jones. All rights reserved.
//

import XCTest
@testable import SwiftExample

class SwiftExampleTests: XCTestCase {

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
