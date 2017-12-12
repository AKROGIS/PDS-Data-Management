using System;
using System.Collections.Generic;
using System.Text;
using System.IO;

namespace MapFixer
{
    public class CheckMapButton : ESRI.ArcGIS.Desktop.AddIns.Button
    {
        public CheckMapButton()
        {
        }

        protected override void OnClick()
        {
            ArcMap.Application.CurrentTool = null;
            ESRI.ArcGIS.Framework.IMessageDialog msgBox = new ESRI.ArcGIS.Framework.MessageDialogClass();
            msgBox.DoModal("Check Map", "The button has been pushed.", "OK", "Really?", ArcMap.Application.hWnd);
        }
        protected override void OnUpdate()
        {
            Enabled = ArcMap.Application != null;
        }
    }

}
