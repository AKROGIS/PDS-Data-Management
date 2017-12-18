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
            var mf = new MapFixer();
            foreach (string name in mf.BrokenDataSources)
            {
                msgBox.DoModal("Broken Data Source", name, "OK", "Cancel", ArcMap.Application.hWnd);
            }
        }
        protected override void OnUpdate()
        {
            Enabled = ArcMap.Application != null;
        }
    }

}
