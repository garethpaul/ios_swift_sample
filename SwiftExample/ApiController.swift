//
//  ApiController.swift
//  SwiftExample
//
//  Created by Gareth Paul Jones on 6/3/14.
//  Copyright (c) 2014 Gareth Paul Jones. All rights reserved.
//

import UIKit

protocol APIControllerProtocol {
    func didRecieveAPIResults(results: NSDictionary)
}

class APIController: NSObject {
    let maximumResponseSize = 1024 * 1024
    var data: NSMutableData = NSMutableData()
    var responseAccepted = false
    var requestCompleted = false
    var delegate: APIControllerProtocol?
    
    func searchItunesFor(searchTerm: String) {
        requestCompleted = false
        responseAccepted = false
        data = NSMutableData()
        let allowedCharacters = NSCharacterSet(charactersInString: "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~")

        if let escapedSearchTerm = searchTerm.stringByAddingPercentEncodingWithAllowedCharacters(allowedCharacters) {
            let urlPath = "https://itunes.apple.com/search?term=\(escapedSearchTerm)&media=software"
            if let url = NSURL(string: urlPath) {
                let request: NSURLRequest = NSURLRequest(URL: url)
                if let connection = NSURLConnection(request: request, delegate: self, startImmediately: false) {
                    connection.start()
                    return
                }
            }
        }

        completeWithResults(NSDictionary())
    }

    func completeWithResults(results: NSDictionary) {
        if requestCompleted {
            return
        }

        requestCompleted = true
        delegate?.didRecieveAPIResults(results)
        self.data = NSMutableData()
    }

    func isAcceptableResponse(response: NSURLResponse) -> Bool {
        guard let httpResponse = response as? NSHTTPURLResponse where
            httpResponse.statusCode >= 200 && httpResponse.statusCode < 300 else {
            return false
        }

        let contentLength = response.expectedContentLength
        if contentLength > Int64(maximumResponseSize) {
            return false
        }

        guard let mimeType = response.MIMEType?.lowercaseString else {
            return false
        }

        return mimeType == "application/json" || mimeType == "text/javascript"
    }

    func canAppendResponseData(chunk: NSData) -> Bool {
        return responseAccepted && chunk.length <= maximumResponseSize - data.length
    }
    
    
    func connection(connection: NSURLConnection, didFailWithError error: NSError) {
        completeWithResults(NSDictionary())
    }
    
    
    func connection(connection: NSURLConnection, didReceiveResponse response: NSURLResponse) {
        self.data = NSMutableData()
        responseAccepted = isAcceptableResponse(response)
        if !responseAccepted {
            connection.cancel()
            completeWithResults(NSDictionary())
        }
    }
    
    func connection(connection: NSURLConnection, didReceiveData data: NSData) {
        if !canAppendResponseData(data) {
            connection.cancel()
            completeWithResults(NSDictionary())
            return
        }

        self.data.appendData(data)
    }
    
    func connectionDidFinishLoading(connection: NSURLConnection) {
        if !responseAccepted {
            completeWithResults(NSDictionary())
            return
        }

        // Request complete, self.data should now hold the resulting info
        // Convert the retrieved data in to an object through JSON deserialization
        do {
            if let jsonResult = try NSJSONSerialization.JSONObjectWithData(data, options: NSJSONReadingOptions.MutableContainers) as? NSDictionary {
                completeWithResults(jsonResult)
            } else {
                completeWithResults(NSDictionary())
            }
        } catch {
            completeWithResults(NSDictionary())
        }
    }
    
    
}
