using System;
using System.Collections.Generic;
using System.Text;
using System.IO;

namespace MapFixer
{
    public class CheckMapExtension : ESRI.ArcGIS.Desktop.AddIns.Extension
    {
        public static Moves moves;
        public static MapFixer mapFixer; 

        public CheckMapExtension()
        {
            var dataPath = @"X:\GIS\ThemeMgr\DataMoves.csv";
            moves = new Moves(dataPath);
            mapFixer = new MapFixer();
        }

        protected override void OnStartup()
        {
            WireDocumentEvents();
            CheckDocument();
        }

        private void WireDocumentEvents()
        {
            ArcMap.Events.NewDocument += delegate () { ArcMap_NewDocument(); };
        }

        void ArcMap_NewDocument()
        {
            CheckDocument();
        }

        public static void CheckDocument()
        {
            mapFixer.FixMap(moves);
        }
    }

}
