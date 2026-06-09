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

}
