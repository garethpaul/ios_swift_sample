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

    override func viewWillDisappear(animated: Bool) {
        super.viewWillDisappear(animated)
        UIApplication.sharedApplication().networkActivityIndicatorVisible = false
    }
    
    func tableView(tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        return tableData.count
    }
    
    
    func tableView(tableView: UITableView, cellForRowAtIndexPath indexPath: NSIndexPath) -> UITableViewCell {
        let cell: UITableViewCell = UITableViewCell(style: UITableViewCellStyle.Subtitle, reuseIdentifier: "MyTestCell")
        
        if indexPath.row < self.tableData.count {
            if let rowData = self.tableData[indexPath.row] as? NSDictionary {
                cell.textLabel?.text = rowData["trackName"] as? String
                cell.imageView?.image = nil

                if let imgURL = artworkURLForRow(indexPath) {
                        loadArtworkFromURL(imgURL, forCell: cell, tableView: tableView, indexPath: indexPath)
                }
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

    func artworkURLForRow(indexPath: NSIndexPath) -> NSURL? {
        guard indexPath.row < tableData.count,
            let rowData = tableData[indexPath.row] as? NSDictionary,
            urlString = rowData["artworkUrl60"] as? String else {
                return nil
        }

        return safeArtworkURLFromString(urlString)
    }

    func loadArtworkFromURL(imgURL: NSURL, forCell cell: UITableViewCell, tableView: UITableView, indexPath: NSIndexPath) {
        dispatch_async(dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0)) {
            guard let imgData = NSData(contentsOfURL: imgURL),
                image = UIImage(data: imgData) else {
                    return
            }

            dispatch_async(dispatch_get_main_queue()) {
                if let visibleIndexPath = tableView.indexPathForCell(cell)
                    where visibleIndexPath.section == indexPath.section && visibleIndexPath.row == indexPath.row,
                    currentArtworkURL = self.artworkURLForRow(indexPath)
                    where currentArtworkURL.isEqual(imgURL) {
                        cell.imageView?.image = image
                        cell.setNeedsLayout()
                }
            }
        }
    }
    
    func didRecieveAPIResults(results: NSDictionary) {
        if !NSThread.isMainThread() {
            dispatch_async(dispatch_get_main_queue()) {
                self.didRecieveAPIResults(results)
            }
            return
        }

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
