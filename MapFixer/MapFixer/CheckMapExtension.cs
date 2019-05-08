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
            ArcMap.Events.OpenDocument += ArcMap_OpenDocument;
        }

        void ArcMap_OpenDocument()
        {
            CheckDocument();
        }

        public static void CheckDocument()
        {
            mapFixer.FixMap(moves);
        }
    }

}
