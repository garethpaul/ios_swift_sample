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
    
    var data: NSMutableData = NSMutableData()
    
    
    var delegate: APIControllerProtocol?
    
    func searchItunesFor(searchTerm: String) {
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

        delegate?.didRecieveAPIResults(NSDictionary())
    }
    
    
    func connection(connection: NSURLConnection, didFailWithError error: NSError) {
        self.data = NSMutableData()
        delegate?.didRecieveAPIResults(NSDictionary())
    }
    
    
    func connection(connection: NSURLConnection, didReceiveResponse response: NSURLResponse) {
        // Recieved a new request, clear out the data object
        self.data = NSMutableData()
    }
    
    func connection(connection: NSURLConnection, didReceiveData data: NSData) {
        // Append the recieved chunk of data to our data object
        self.data.appendData(data)
    }
    
    func connectionDidFinishLoading(connection: NSURLConnection) {
        // Request complete, self.data should now hold the resulting info
        // Convert the retrieved data in to an object through JSON deserialization
        do {
            if let jsonResult = try NSJSONSerialization.JSONObjectWithData(data, options: NSJSONReadingOptions.MutableContainers) as? NSDictionary {
                delegate?.didRecieveAPIResults(jsonResult)
            } else {
                delegate?.didRecieveAPIResults(NSDictionary())
            }
        } catch {
            delegate?.didRecieveAPIResults(NSDictionary())
        }
    }
    
    
}
