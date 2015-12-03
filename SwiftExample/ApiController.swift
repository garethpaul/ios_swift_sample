//
//  ApiController.swift
//  SwiftExample
//
//  Created by Gareth Paul Jones on 6/3/14.
//  Copyright (c) 2014 Gareth Paul Jones. All rights reserved.
//

import UIKit
import CoreLocation

protocol APIControllerProtocol {
    func didRecieveAPIResults(results: NSDictionary)
}

class APIController: NSObject {
    
    var data: NSMutableData = NSMutableData()
    
    
    var delegate: APIControllerProtocol?
    
    func searchItunesFor(searchTerm: String) {
        
        // The iTunes API wants multiple terms separated by + sym[bols, so replace spaces with + signs
        let itunesSearchTerm = searchTerm.stringByReplacingOccurrencesOfString(" ", withString: "+", options: NSStringCompareOptions.CaseInsensitiveSearch, range: nil)
        
        // Now escape anything else that isn't URL-friendly

        let escapedSearchTerm = itunesSearchTerm.stringByAddingPercentEscapesUsingEncoding(NSUTF8StringEncoding)
        let urlPath = "https://itunes.apple.com/search?term=\(escapedSearchTerm)&media=software"
        let url: NSURL = NSURL(string: urlPath)!
        let request: NSURLRequest = NSURLRequest(URL: url)
        let connection: NSURLConnection = NSURLConnection(request: request, delegate: self, startImmediately: false)!
        
        connection.start()
    }
    
    
    func connection(connection: NSURLConnection!, didFailWithError error: NSError!) {
        print("Connection failed.\(error.localizedDescription)")
    }
    
    
    func connection(didReceiveResponse: NSURLConnection!, didReceiveResponse response: NSURLResponse!) {
        // Recieved a new request, clear out the data object
        self.data = NSMutableData()
    }
    
    func connection(connection: NSURLConnection!, didReceiveData data: NSData!) {
        // Append the recieved chunk of data to our data object
        self.data.appendData(data)
    }
    
    func connectionDidFinishLoading(connection: NSURLConnection!) {
        // Request complete, self.data should now hold the resulting info
        // Convert the retrieved data in to an object through JSON deserialization
        let jsonResult: NSDictionary?
        do {
            jsonResult = try! NSJSONSerialization.JSONObjectWithData(data, options: NSJSONReadingOptions.MutableContainers) as! NSDictionary
        }
            

        
        // Now send the JSON result to our delegate object
        delegate?.didRecieveAPIResults(jsonResult!)
    }
    
    
}
