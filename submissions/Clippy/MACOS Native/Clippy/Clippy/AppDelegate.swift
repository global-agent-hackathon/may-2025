import Cocoa
import Carbon

@main
class AppDelegate: NSObject, NSApplicationDelegate {
    
    func applicationDidFinishLaunching(_ aNotification: Notification) {
        print("application did finish launching")
        
        launchClippyIfNeededAndThenWait()
    }

    func launchClippyIfNeededAndThenWait() {
        let runningApps = NSWorkspace.shared.runningApplications
        let isRunning = runningApps.contains { $0.bundleIdentifier == "com.smil.ClippyPython" } // <-- Correct your bundle ID

        if isRunning {
            print("Clippy.app is already running.")
        } else {
            let clippyAppURL = URL(fileURLWithPath: "/Applications/ClippyPython.app")
            let config = NSWorkspace.OpenConfiguration()
            config.activates = true
            config.allowsRunningApplicationSubstitution = false

            NSWorkspace.shared.openApplication(at: clippyAppURL, configuration: config) { (app, error) in
                if let error = error {
                    print("Failed to launch Clippy.app: \(error)")
                } else {
                    print("Successfully launched Clippy.app")
                }
                // After trying to launch, start waiting
            }
        }
    }

    func sendToggleSignalToClippy() {
        DistributedNotificationCenter.default().post(name: Notification.Name("toggleClippy"), object: nil)
    }

    func applicationWillTerminate(_ aNotification: Notification) {
        // Clean up if needed
    }

    func applicationSupportsSecureRestorableState(_ app: NSApplication) -> Bool {
        return true
    }
}
