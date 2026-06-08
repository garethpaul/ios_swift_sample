//
//  ViewController.swift
//
//

import UIKit
import QuartzCore

class SearchResultsViewController: UIViewController, UITableViewDataSource, UITableViewDelegate, APIControllerProtocol {
    
    var api: APIController = APIController()
    @IBOutlet var appsTableView : UITableView?
    var tableData: NSArray = NSArray()
    
    override func viewDidLoad() {
        super.viewDidLoad()
        api.delegate = self
        UIApplication.sharedApplication().networkActivityIndicatorVisible = true
        api.searchItunesFor("Angry Birds")
    }
    
    func tableView(tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        return tableData.count
    }
    
    
    func tableView(tableView: UITableView, cellForRowAtIndexPath indexPath: NSIndexPath) -> UITableViewCell {
        let cell: UITableViewCell = UITableViewCell(style: UITableViewCellStyle.Subtitle, reuseIdentifier: "MyTestCell")
        
        if let rowData = self.tableData[indexPath.row] as? NSDictionary {
            cell.textLabel?.text = rowData["trackName"] as? String

            if let urlString = rowData["artworkUrl60"] as? String,
                imgURL = safeArtworkURLFromString(urlString),
                imgData = NSData(contentsOfURL: imgURL) {
                    cell.imageView?.image = UIImage(data: imgData)
            }
        }

        // Circular image
        if let imageView = cell.imageView {
            imageView.layer.cornerRadius = 23
            imageView.layer.masksToBounds = true
            imageView.layer.borderWidth = 0
        }
        
        
        // Get the formatted price string for display in the subtitle
        //var formattedPrice: NSString = rowData["formattedPrice"] as NSString
        
        //cell.detailTextLabel.text = formattedPrice
        
        return cell
    }

    func safeArtworkURLFromString(urlString: String) -> NSURL? {
        if let url = NSURL(string: urlString),
            scheme = url.scheme?.lowercaseString,
            host = url.host?.lowercaseString {
                if scheme == "https" && (host == "mzstatic.com" || host.hasSuffix(".mzstatic.com")) {
                    return url
                }
        }

        return nil
    }
    
    func didRecieveAPIResults(results: NSDictionary) {
        // Store the results in our table data array
        if let resultsArray = results["results"] as? NSArray {
            self.tableData = resultsArray
        } else {
            self.tableData = NSArray()
        }

        self.appsTableView?.reloadData()
        UIApplication.sharedApplication().networkActivityIndicatorVisible = false
    }
    
}


