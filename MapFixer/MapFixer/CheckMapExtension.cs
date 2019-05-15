namespace MapFixer
{
    // ReSharper disable once ClassNeverInstantiated.Global
    public class CheckMapExtension : ESRI.ArcGIS.Desktop.AddIns.Extension
    {
        private static Moves _moves;
        private static MapFixer _mapFixer; 

        public CheckMapExtension()
        {
            var dataPath = @"C:\tmp\DataMoves.csv";
            _moves = new Moves(dataPath);
            _mapFixer = new MapFixer();
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
            _mapFixer.FixMap(_moves);
        }
    }

}
