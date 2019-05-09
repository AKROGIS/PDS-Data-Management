namespace MapFixer
{
    // ReSharper disable once UnusedMember.Global
    // Found by the ArcMap Add In Framework
    public class CheckMapButton : ESRI.ArcGIS.Desktop.AddIns.Button
    {
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
