//
//  ViewController.swift
//  Clippy
//
//  Created by Smil on 26/04/25.
//

import Cocoa
import WebKit
import HotKey

class ViewController: NSViewController {
    // The web view that loads the local server
    @IBOutlet weak var webView: WKWebView!
    
    // Global hotkey handler
    var hotkey: HotKey?
    
    // Stores the last height before hiding the window, to restore it later
    var windowHeightBeforeHide: Double = 100

    // Timer to poll the local server periodically
    var pollingTimer: Timer?

    override func viewDidAppear() {
        super.viewDidAppear()
        
        if let window = self.view.window {
            // Keeps the window above normal app windows, like Spotlight
            window.level = .screenSaver
            
            // Allow the window to appear on all spaces (desktops)
            window.collectionBehavior = [
                .canJoinAllSpaces,
                .fullScreenAuxiliary
            ]
            
            // Set initial size of the window
            var frame = window.frame
            frame.size.height = windowHeightBeforeHide
            frame.size.width = 620
            window.setFrame(frame, display: true, animate: true)
            
            // Prevent resizing and minimizing
            window.styleMask.remove(.miniaturizable)
            window.styleMask.remove(.resizable)
            window.title = "Clippy"
        }
    }

    // Called when WKWebView’s title changes — used here to update height
    override func observeValue(forKeyPath keyPath: String?, of object: Any?, change: [NSKeyValueChangeKey : Any]?, context: UnsafeMutableRawPointer?) {
        if keyPath == "title" {
            if let newTitle = change?[.newKey] as? String {
                print("Title changed: \(newTitle)")
                changeWindowHeight(height: newTitle)
            }
        }
    }

    // Updates the window's height dynamically
    func changeWindowHeight(height: String) {
        if let window = self.view.window {
            if let heightValue = Double(height) {
                print("Changing window height to \(heightValue)")
                var frame = window.frame
                frame.size.height = heightValue
                window.setFrame(frame, display: true, animate: true)
                windowHeightBeforeHide = heightValue
            }
        }
    }

    // Loads the web view with local server URL
    func loadWebView() {
        // If the webView is nil (possibly deallocated), create a new one
        if webView == nil {
            print("webView was nil, creating a new one")
            webView = WKWebView(frame: self.view.bounds)
            self.view.addSubview(webView)
            webView.translatesAutoresizingMaskIntoConstraints = false
            NSLayoutConstraint.activate([
                webView.topAnchor.constraint(equalTo: self.view.topAnchor),
                webView.bottomAnchor.constraint(equalTo: self.view.bottomAnchor),
                webView.leadingAnchor.constraint(equalTo: self.view.leadingAnchor),
                webView.trailingAnchor.constraint(equalTo: self.view.trailingAnchor)
            ])
        }

        // Load local server
        if let url = URL(string: "http://127.0.0.1:8550/") {
            let request = URLRequest(url: url)
            webView.load(request)
        }

        // Observe title to handle height changes
        webView.addObserver(self, forKeyPath: "title", options: [.old, .new], context: nil)
    }

    // Periodically checks if local server is alive
    func startServerPolling() {
        pollingTimer = Timer.scheduledTimer(withTimeInterval: 3.0, repeats: true) { [weak self] _ in
            guard let url = URL(string: "http://127.0.0.1:8550/") else { return }
            var request = URLRequest(url: url)
            request.timeoutInterval = 1.5 // Short timeout for faster polling

            let task = URLSession.shared.dataTask(with: request) { _, response, error in
                // If server is up, reload if needed
                if let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode == 200 {
                    DispatchQueue.main.async {
                        if self?.webView?.url == nil {
                            print("Server is up and webview is empty, loading...")
                            self?.loadWebView()
                        }
                    }
                } else {
                    print("Server not reachable. Error: \(error?.localizedDescription ?? "Unknown")")
                }
            }
            task.resume()
        }
    }

    override func viewDidLoad() {
        super.viewDidLoad()

        // Try loading the web view initially
        loadWebView()

        // Start polling the server in background
        startServerPolling()

        // Register hotkey: Cmd + Ctrl + Option + Space
        hotkey = HotKey(key: .space, modifiers: [.command, .control, .option])
        hotkey?.keyDownHandler = { [weak self] in
            guard let self = self, let window = self.view.window else {
                print("❗️No window found.")
                return
            }

            if window.isVisible {
                print("🔻 Hiding Clippy")
                window.orderOut(nil)
            } else {
                print("🔺 Showing Clippy, restoring height to \(self.windowHeightBeforeHide)")
                window.makeKeyAndOrderFront(nil)
                self.changeWindowHeight(height: "\(self.windowHeightBeforeHide)")
                NSApp.activate(ignoringOtherApps: true)
            }
        }
    }

    override var representedObject: Any? {
        didSet {
            // Handle updates if necessary
        }
    }

    // Clean up observers when view is destroyed
    deinit {
        if webView != nil {
            webView.removeObserver(self, forKeyPath: "title")
        }
        pollingTimer?.invalidate()
    }
}
