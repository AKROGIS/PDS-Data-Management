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
            CheckMapExtension.CheckDocument();
        }

        protected override void OnUpdate()
        {
            Enabled = ArcMap.Application != null;
        }
    }

}
