using System;
using System.Runtime.InteropServices;
using System.Windows;
using System.Windows.Interop;
using Microsoft.Web.WebView2.Core;

namespace ClippyWindowNative
{
    public partial class MainWindow : Window
    {
        private const int HOTKEY_ID = 9000; // Arbitrary ID
        private const uint MOD_CONTROL = 0x0002;
        private const uint VK_SPACE = 0x20;

        [DllImport("user32.dll")]
        private static extern bool RegisterHotKey(IntPtr hWnd, int id, uint fsModifiers, uint vk);

        [DllImport("user32.dll")]
        private static extern bool UnregisterHotKey(IntPtr hWnd, int id);

        public MainWindow()
        {
            InitializeComponent();
            this.Height = 110;
            this.Topmost = true; // Always on top
        }

        private async void Window_Loaded(object sender, RoutedEventArgs e)
        {
            await webView.EnsureCoreWebView2Async();
            webView.CoreWebView2.DocumentTitleChanged += CoreWebView2_DocumentTitleChanged;
            UpdateWindowHeight(webView.CoreWebView2.DocumentTitle);

            // Register global hotkey
            var hwnd = new WindowInteropHelper(this).Handle;
            RegisterHotKey(hwnd, HOTKEY_ID, MOD_CONTROL, VK_SPACE);

            // Hook up Hwnd source for hotkey messages
            HwndSource source = HwndSource.FromHwnd(hwnd);
            source.AddHook(HwndHook);
        }

        private IntPtr HwndHook(IntPtr hwnd, int msg, IntPtr wParam, IntPtr lParam, ref bool handled)
        {
            const int WM_HOTKEY = 0x0312;
            if (msg == WM_HOTKEY && wParam.ToInt32() == HOTKEY_ID)
            {
                ToggleVisibility();
                handled = true;
            }
            return IntPtr.Zero;
        }

        private void ToggleVisibility()
        {
            if (this.Visibility == Visibility.Visible)
            {
                this.Hide();
            }
            else
            {
                this.Show();
                this.Activate();
                this.Topmost = true;
            }
        }

        private void CoreWebView2_DocumentTitleChanged(object sender, object e)
        {
            var newTitle = webView.CoreWebView2.DocumentTitle;
            UpdateWindowHeight(newTitle);
        }

        private void UpdateWindowHeight(string title)
        {
            if (double.TryParse(title, out double h))
            {
                this.Height = h + 10;
            }
            else
            {
                this.Height = 110;
            }
        }

        protected override void OnClosed(EventArgs e)
        {
            // Clean up
            var hwnd = new WindowInteropHelper(this).Handle;
            UnregisterHotKey(hwnd, HOTKEY_ID);
            base.OnClosed(e);
        }
    }
}
