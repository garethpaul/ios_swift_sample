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
        api.searchItunesFor("Angry Birds");
    }
    
    func tableView(tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        return tableData.count
    }
    
    
    func tableView(tableView: UITableView, cellForRowAtIndexPath indexPath: NSIndexPath) -> UITableViewCell {
        let cell: UITableViewCell = UITableViewCell(style: UITableViewCellStyle.Subtitle, reuseIdentifier: "MyTestCell")
        
        let rowData: NSDictionary = self.tableData[indexPath.row] as! NSDictionary
        
        cell.textLabel?.text = rowData["trackName"] as? String
        
        // Grab the artworkUrl60 key to get an image URL for the app's thumbnail
        let urlString: NSString = rowData["artworkUrl60"] as! NSString
        let imgURL: NSURL = NSURL(string: urlString as String)!
        
        // Download an NSData representation of the image at the URL
        let imgData: NSData = NSData(contentsOfURL: imgURL)!
        cell.imageView?.image = UIImage(data: imgData)

        // Circular image
        cell.imageView!.layer.cornerRadius = 23
        cell.imageView!.layer.masksToBounds = true
        cell.imageView!.layer.borderWidth = 0
        
        
        // Get the formatted price string for display in the subtitle
        //var formattedPrice: NSString = rowData["formattedPrice"] as NSString
        
        //cell.detailTextLabel.text = formattedPrice
        
        return cell
    }
    
    func didRecieveAPIResults(results: NSDictionary) {
        // Store the results in our table data array
        if results.count>0 {
            self.tableData = results["results"] as! NSArray
            self.appsTableView!.reloadData()
            UIApplication.sharedApplication().networkActivityIndicatorVisible = false
        }
    }
    
}




