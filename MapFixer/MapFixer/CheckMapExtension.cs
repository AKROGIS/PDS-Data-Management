using System;
using System.Collections.Generic;
using System.Text;
using System.IO;

namespace MapFixer
{
    public class CheckMapExtension : ESRI.ArcGIS.Desktop.AddIns.Extension
    {
        public CheckMapExtension()
        {
        }

        protected override void OnStartup()
        {
            WireDocumentEvents();
            //CheckDocument();
        }

        private void WireDocumentEvents()
        {
            ArcMap.Events.NewDocument += delegate () { ArcMap_NewDocument(); };
        }

        void ArcMap_NewDocument()
        {
            //CheckDOcument();
        }

    }

}
