//
//  ViewController.swift
//
//

import UIKit
import QuartzCore

class ArtworkRequest: NSObject, NSURLConnectionDataDelegate {
    let maximumResponseSize = 1024 * 1024
    var data = NSMutableData()
    var responseAccepted = false
    var requestCompleted = false
    var connection: NSURLConnection?
    let completion: (NSData?) -> Void

    init?(URL: NSURL, completion: (NSData?) -> Void) {
        self.completion = completion
        super.init()

        let request = NSURLRequest(
            URL: URL,
            cachePolicy: NSURLRequestCachePolicy.ReloadIgnoringLocalCacheData,
            timeoutInterval: 15
        )
        guard let connection = NSURLConnection(request: request, delegate: self, startImmediately: false) else {
            return nil
        }

        self.connection = connection
    }

    func start() {
        connection?.start()
    }

    class func isTrustedURL(URL: NSURL) -> Bool {
        guard URL.user == nil && URL.password == nil && URL.port == nil else {
            return false
        }

        if let scheme = URL.scheme?.lowercaseString,
            host = URL.host?.lowercaseString {
                return scheme == "https" && (host == "mzstatic.com" || host.hasSuffix(".mzstatic.com"))
        }

        return false
    }

    func isAcceptableResponse(response: NSURLResponse) -> Bool {
        guard let httpResponse = response as? NSHTTPURLResponse where
            httpResponse.statusCode >= 200 && httpResponse.statusCode < 300 else {
                return false
        }

        guard let responseURL = response.URL where ArtworkRequest.isTrustedURL(responseURL) else {
            return false
        }

        let contentLength = response.expectedContentLength
        if contentLength > Int64(maximumResponseSize) {
            return false
        }

        guard let mimeType = response.MIMEType?.lowercaseString else {
            return false
        }

        return mimeType == "image/jpeg" || mimeType == "image/png"
    }

    func canAppendArtworkData(chunk: NSData) -> Bool {
        return responseAccepted && chunk.length <= maximumResponseSize - data.length
    }

    func completeWithData(result: NSData?) {
        if requestCompleted {
            return
        }

        requestCompleted = true
        connection = nil
        data = NSMutableData()
        completion(result)
    }

    func connection(connection: NSURLConnection, didFailWithError error: NSError) {
        completeWithData(nil)
    }

    func connection(connection: NSURLConnection, didReceiveResponse response: NSURLResponse) {
        data = NSMutableData()
        responseAccepted = isAcceptableResponse(response)
        if !responseAccepted {
            connection.cancel()
            completeWithData(nil)
        }
    }

    func connection(connection: NSURLConnection, didReceiveData chunk: NSData) {
        if !canAppendArtworkData(chunk) {
            connection.cancel()
            completeWithData(nil)
            return
        }

        data.appendData(chunk)
    }

    func connectionDidFinishLoading(connection: NSURLConnection) {
        if !responseAccepted {
            completeWithData(nil)
            return
        }

        completeWithData(NSData(data: data))
    }
}

class SearchResultsViewController: UIViewController, UITableViewDataSource, UITableViewDelegate, APIControllerProtocol {
    
    var api: APIController = APIController()
    @IBOutlet var appsTableView : UITableView?
    var tableData: NSArray = NSArray()
    let maximumArtworkDimension = 8192
    let maximumArtworkPixelCount = 16 * 1024 * 1024
    
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
        if let url = NSURL(string: urlString) {
            if ArtworkRequest.isTrustedURL(url) {
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

    func canDisplayArtworkDimensions(width: Int, height: Int) -> Bool {
        guard width > 0 && height > 0 &&
            width <= maximumArtworkDimension && height <= maximumArtworkDimension else {
            return false
        }

        return width <= maximumArtworkPixelCount / height
    }

    func isAcceptableArtworkImage(image: UIImage) -> Bool {
        guard let cgImage = image.CGImage else {
            return false
        }

        return canDisplayArtworkDimensions(
            CGImageGetWidth(cgImage),
            height: CGImageGetHeight(cgImage)
        )
    }

    func loadArtworkFromURL(imgURL: NSURL, forCell cell: UITableViewCell, tableView: UITableView, indexPath: NSIndexPath) {
        if let request = ArtworkRequest(URL: imgURL, completion: { [weak self, weak cell, weak tableView] imgData in
            guard let controller = self,
                targetCell = cell,
                targetTableView = tableView,
                data = imgData else {
                    return
            }

            dispatch_async(dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0)) {
                guard let image = UIImage(data: data) where controller.isAcceptableArtworkImage(image) else {
                    return
                }

                dispatch_async(dispatch_get_main_queue()) {
                    if let visibleIndexPath = targetTableView.indexPathForCell(targetCell)
                        where visibleIndexPath.section == indexPath.section && visibleIndexPath.row == indexPath.row,
                        currentArtworkURL = controller.artworkURLForRow(indexPath)
                        where currentArtworkURL.isEqual(imgURL) {
                            targetCell.imageView?.image = image
                            targetCell.setNeedsLayout()
                    }
                }
            }
        }) {
            request.start()
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
