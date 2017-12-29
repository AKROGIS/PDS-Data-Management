using System;
using System.Collections.Generic;
using ESRI.ArcGIS.Carto;
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
            var brokenDataSources = GetBrokenDataSources();
            var autoFixesApplied = 0;
            foreach (IDataLayer2 dataLayer in brokenDataSources)
            {
                string layerName;
                if (dataLayer is IDataset)
                {
                    layerName = ((IDataset)dataLayer).Name;
                }
                else
                {
                    layerName = ((ILayer2)dataLayer).Name;
                }
                Moves.GisDataset oldDataset = GetDataset(dataLayer);
                Moves.Solution? maybeSolution = moves.GetSolution(oldDataset);
                if (maybeSolution == null)
                {
                    string msg = string.Format("Sorry the layer '{0}' is broken, but it isn't due to the X drive reorganization. This addin does not have the information necessary to fix it.",
                        layerName);
                    msgBox.DoModal("Broken Data Source", msg, "OK", "Cancel", ArcMap.Application.hWnd);
                    continue; 
                }
                Moves.Solution solution = maybeSolution.Value;
                if (solution.NewDataset == null && solution.ReplacementDataset == null && solution.ReplacementLayerFilePath == null)
                {
                    string msg = string.Format("The layer '{0}' is broken, but it cannot be fixed automatically.",
                        layerName);
                    msg = msg + "\n\nNote: " + solution.Remarks;
                    msgBox.DoModal("Broken Data Source", msg, "OK", "Cancel", ArcMap.Application.hWnd);
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
                    string msg = string.Format("The layer '{0}' is broken. The data has moved to a new location.  Do you want to fix the layer?",
                        layerName);
                    if (solution.Remarks != null)
                    {
                        msg = msg + "\n\nNote: " + solution.Remarks;
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
                    //TODO
                    continue;
                }
                if (solution.NewDataset != null && solution.ReplacementDataset == null && solution.ReplacementLayerFilePath == null)
                {
                    if (solution.Remarks == null)
                    {
                        // This is the optimal action.  There is no good reason for a user not to click OK.
                        // The user will be warned that layers have been fixed, and they can choose to not save the changes.
                        autoFixesApplied += 1;
                        RepairLayer(dataLayer, oldDataset, solution.NewDataset.Value);
                    }
                    else
                    {
                        string msg = string.Format("The layer '{0}' is broken. The data has moved to a new location.  Do you want to fix the layer?",
                            layerName);
                        msg = msg + "\n\nNote: " + solution.Remarks;
                        bool result = msgBox.DoModal("Broken Data Source", msg, "OK", "Cancel", ArcMap.Application.hWnd);
                        if (result)
                        {
                            RepairLayer(dataLayer, oldDataset, solution.NewDataset.Value);
                        }
                    }
                    continue;
                }
                if (solution.NewDataset != null && solution.ReplacementDataset == null && solution.ReplacementLayerFilePath != null)
                {
                    //TODO
                    continue;
                }
                if (solution.NewDataset != null && solution.ReplacementDataset != null && solution.ReplacementLayerFilePath == null)
                {
                    //TODO
                    continue;
                }
                if (solution.NewDataset != null && solution.ReplacementDataset != null && solution.ReplacementLayerFilePath != null)
                {
                    //TODO
                    continue;
                }
            }
            //TODO: Refresh TOC
            ArcMap.Document.ActiveView.Refresh();
            ArcMap.Document.CurrentContentsView.Refresh(null);
            if (autoFixesApplied > 0)
            {
                string msg = String.Format("{0} broken layers were automatically fixed based on the new locations of known data sources. " +
                    "Close the document without saving if this is not what you want.", autoFixesApplied);
                msgBox.DoModal("Map has been modified", msg, "OK", null, ArcMap.Application.hWnd);
            }
            //Check for completeness
            brokenDataSources = GetBrokenDataSources();
            if (brokenDataSources.Count > 0)
            {
                string msg = "There are still some broken layers in your map. " +
                    "If this is unexpected, it may be because some of the datasources have moved multiple times. " +
                    "Try running the tool again.";
                msgBox.DoModal("Map Check", msg, "OK", "Cancel", ArcMap.Application.hWnd);
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

        public List<IDataLayer2> GetBrokenDataSources()
        {
            List<IDataLayer2> layerList = new List<IDataLayer2>();
            IMaps maps = ArcMap.Document.Maps;
            for (int i = 0; i < maps.Count; i++)
            {
                IMap map = maps.Item[i];
                IEnumLayer layerEnumerator = map.Layers[null, true];
                ILayer layer;
                while((layer = layerEnumerator.Next()) != null)
                {
                    if (layer is ILayer2)
                    {
                        ILayer2 layer2 = (ILayer2)layer;
                        if (!layer2.Valid)
                        {
                            if (layer2 is IDataLayer2)
                            {
                                IDataLayer2 dataLayer = (IDataLayer2)layer2;
                                layerList.Add(dataLayer);
                            }
                        }
                    }
                }
            }
            return layerList;
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
