using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using ESRI.ArcGIS.ArcMapUI;
using ESRI.ArcGIS.Carto;
using ESRI.ArcGIS.esriSystem;
using ESRI.ArcGIS.Geodatabase;

namespace MapFixer
{
    class MapFixer
    {

        public MapFixer()
        {
        }

        public IEnumerable<string> BrokenDataSources
        {
            get
            {
                IMaps maps = ArcMap.Document.Maps;
                for (int i = 0; i < maps.Count; i++)
                {
                    IMap map = maps.Item[i];
                    for (int layerIndex = 0; layerIndex < map.LayerCount; layerIndex++)
                    {
                        ILayer layer = map.Layer[layerIndex];
                        if (layer is ILayer2)
                        {
                            ILayer2 layer2 = (ILayer2)layer;
                            if (!layer2.Valid)
                            {
                                if (layer2 is IDataLayer2)
                                {
                                    IDataLayer2 dataLayer = (IDataLayer2)layer2;
                                    IDatasetName datasetName = dataLayer.DataSourceName as IDatasetName;
                                    IWorkspaceName workspaceName = datasetName.WorkspaceName;
                                    yield return workspaceName.PathName + " - " + datasetName.Name;
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
