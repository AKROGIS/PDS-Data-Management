using System;

namespace MapFixer
{
    // Needed to convert the int provided ArcMap.Application.hWnd to an IWin32Window required by WinForms
    // Thanks to http://ryanfarley.com/blog/archive/2004/03/23/465.aspx
    internal class WindowWrapper : System.Windows.Forms.IWin32Window
    {
        public WindowWrapper(IntPtr handle)
        {
            Handle = handle;
        }

        public IntPtr Handle { get; }
    }
}
