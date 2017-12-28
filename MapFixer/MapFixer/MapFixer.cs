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
    public class MapFixer
    {

        public MapFixer()
        {
        }

        public void FixMap(Moves moves)
        {
            ESRI.ArcGIS.Framework.IMessageDialog msgBox = new ESRI.ArcGIS.Framework.MessageDialogClass();

            foreach (IDataLayer2 dataLayer in BrokenDataSources)
            {
                Moves.GisDataset oldDataset = GetDataset(dataLayer);
                Moves.Solution? maybeSolution = moves.GetSolution(oldDataset);
                if (maybeSolution == null)
                {
                    //Unfixable layer; ignore or TODO: messageBox?
                    continue; 
                }
                Moves.Solution solution = maybeSolution.Value;
                if (solution.NewDataset == null && solution.ReplacementDataset == null && solution.ReplacementLayerFilePath == null)
                {
                    // TODO: messageBox solution.Remarks
                    continue;
                }
                if (solution.NewDataset == null && solution.ReplacementDataset == null && solution.ReplacementLayerFilePath != null)
                {
                    // TODO: messageBox do you want to add layer (yes/no)  add solution.Remarks if not null
                    // TODO: if yes add layer
                    // TODO: messagebox do you want to delete the old layer (If you have customized this layer, you might want to inspect and apply by hand, then delete manually). Yes/no
                    // TODO: if yes, delete the broken layer
                    continue;
                }
                if (solution.NewDataset == null && solution.ReplacementDataset != null && solution.ReplacementLayerFilePath == null)
                {
                    string msg = string.Format("The layer '{0}' is broken.  The data has been moved to a new locations.  Do you want to fix the layer?",
                        dataLayer.DataSourceName.NameString);
                    if (solution.Remarks != null)
                    {
                        msg = msg + "\nNote: " + solution.Remarks;
                    }
                    bool result = msgBox.DoModal("Broken Data Source", msg, "OK", "Cancel", ArcMap.Application.hWnd);
                    if (result)
                    {
                        RepairLayer(dataLayer, oldDataset, solution.ReplacementDataset.Value);
                    }
                    continue;
                }
                if (solution.NewDataset == null && solution.ReplacementDataset != null && solution.ReplacementLayerFilePath != null)
                {
                    continue;
                }
                if (solution.NewDataset != null && solution.ReplacementDataset == null && solution.ReplacementLayerFilePath == null)
                {
                    string msg = string.Format("The layer '{0}' is broken.  The data has been moved to a new locations.  Do you want to fix the layer?",
                        dataLayer.DataSourceName.NameString);
                    if (solution.Remarks != null)
                    {
                        msg = msg + "\nNote: " + solution.Remarks;
                    }
                    bool result = msgBox.DoModal("Broken Data Source", msg, "OK", "Cancel", ArcMap.Application.hWnd);
                    if (result)
                    {
                        RepairLayer(dataLayer, oldDataset, solution.NewDataset.Value);
                    }
                    continue;
                }
                if (solution.NewDataset != null && solution.ReplacementDataset == null && solution.ReplacementLayerFilePath != null)
                {
                    continue;
                }
                if (solution.NewDataset != null && solution.ReplacementDataset != null && solution.ReplacementLayerFilePath == null)
                {
                    continue;
                }
                if (solution.NewDataset != null && solution.ReplacementDataset != null && solution.ReplacementLayerFilePath != null)
                {
                    continue;
                }

            }
        }

        public void RepairLayer(IDataLayer2 dataLayer, Moves.GisDataset oldDataset, Moves.GisDataset newDataset)
        {
            if (oldDataset.DatasourceName == newDataset.DatasourceName && oldDataset.DatasourceType == newDataset.DatasourceType && oldDataset.WorkspaceProgID == newDataset.WorkspaceProgID)
            {
                IDataSourceHelperLayer helper = new DataSourceHelper() as IDataSourceHelperLayer;
                helper.FindAndReplaceWorkspaceNamePath((ILayer)dataLayer, oldDataset.WorkspacePath, newDataset.WorkspacePath, false);
            }
            else
            {
                // FIXME:  This is much more complicated
                IDataset dataset = OpenDataset(newDataset);
                // Patch the layer, and trigger the TOC and map updates, etc...
                // see http://help.arcgis.com/en/sdk/10.0/arcobjects_net/componenthelp/index.html#//00490000002r000000
            }
        }

        public IEnumerable<IDataLayer2> BrokenDataSources
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
                                    yield return dataLayer;
                                }
                            }
                        }
                    }
                }
            }
        }

        public Moves.GisDataset GetDataset(IDataLayer2 dataLayer)
        {
            IDatasetName datasetName = dataLayer.DataSourceName as IDatasetName;
            IWorkspaceName workspaceName = datasetName.WorkspaceName;
            return new Moves.GisDataset(workspaceName.PathName, workspaceName.WorkspaceFactoryProgID,
                datasetName.Name, datasetName.Type);
        }

        public IDataset OpenDataset(Moves.GisDataset dataset)
        {
            IWorkspaceName workspaceName = new WorkspaceNameClass();
            workspaceName.WorkspaceFactoryProgID = dataset.WorkspaceProgID; // "esriDataSourcesGDB.AccessWorkspaceFactory";
            workspaceName.PathName = dataset.WorkspacePath;
            IWorkspace workspace = null;
            try
            {
                workspace = workspaceName.WorkspaceFactory.Open(null, 0);
            }
            catch (Exception)
            {
                // This may fail for any number of reasons, bad input (progID or path), network or filesystem error permissions, ...
                // TODO: Log or messageBox the error;
                return null;
            }
            if (workspace == null)
                return null;

            var datasetNames = workspace.DatasetNames[dataset.DatasourceType];
            IDatasetName datasetName = null;
            while ((datasetName = datasetNames.Next()) != null)
            {
                if (datasetName.Type == dataset.DatasourceType && string.Compare(datasetName.Name, dataset.DatasourceName, StringComparison.OrdinalIgnoreCase) == 0)
                    return OpenDataset(dataset, workspace, datasetName);
            }
            return null;
        }

        private IDataset OpenDataset(Moves.GisDataset dataset, IWorkspace workspace, IDatasetName datasetName)
        {
            if (dataset.DatasourceType == esriDatasetType.esriDTFeatureClass)
            {
                try
                {
                    IFeatureWorkspace featureWorkspace = (IFeatureWorkspace)workspace;
                    IFeatureClass featureClass = featureWorkspace.OpenFeatureClass(datasetName.Name);
                    return (IDataset)featureClass;
                }
                catch (Exception)
                {
                    // TODO: Log or messageBox the error;\
                    return null;
                }
            }
            if (dataset.DatasourceType == esriDatasetType.esriDTRasterDataset)
            {
                try
                {
                    IRasterWorkspace2 rasterWorkspace = (IRasterWorkspace2)workspace;
                    IRasterDataset rasterDataset = rasterWorkspace.OpenRasterDataset(datasetName.Name);
                    return (IDataset)rasterDataset;
                }
                catch (Exception)
                {
                    // TODO: Log or messageBox the error;\
                    return null;
                }
            }
            if (dataset.DatasourceType == esriDatasetType.esriDTRasterCatalog || dataset.DatasourceType == esriDatasetType.esriDTMosaicDataset)
            {
                try
                {
                    IRasterWorkspaceEx rasterWorkspace = (IRasterWorkspaceEx)workspace;
                    IRasterDataset rasterDataset = rasterWorkspace.OpenRasterDataset(datasetName.Name);
                    return (IDataset)rasterDataset;
                }
                catch (Exception)
                {
                    // TODO: Log or messageBox the error;\
                    return null;
                }
            }
            return null;
        }
    }
}
