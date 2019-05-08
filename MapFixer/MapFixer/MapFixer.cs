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
            var brokenDataSources = GetBrokenDataSources();
            // We do not need to do anything if there was nothing to fix
            if (brokenDataSources.Count == 0) {
                return;
            }
            ESRI.ArcGIS.Framework.IMessageDialog msgBox = new ESRI.ArcGIS.Framework.MessageDialogClass();
            var autoFixesApplied = 0;
            var unfixableLayers = 0;
            foreach (IDataLayer2 dataLayer in brokenDataSources)
            {
                var dataset = dataLayer as IDataset;
                var layerName = dataset != null ? dataset.Name : ((ILayer2)dataLayer).Name;
                Moves.GisDataset oldDataset = GetDataset(dataLayer);
                Moves.Solution? maybeSolution = moves.GetSolution(oldDataset);
                if (maybeSolution == null)
                {
                    unfixableLayers += 1;
                    continue;
                }
                Moves.Solution solution = maybeSolution.Value;
                if (solution.NewDataset == null && solution.ReplacementDataset == null && solution.ReplacementLayerFilePath == null)
                {
                    // This is a very unusual case.  We do not have a solution, only a note.
                    string msg =
                        $"The layer '{layerName}' has been removed and there is no replacement.\n\nNote: {solution.Remarks}";
                    //TODO: Remove Cancel button
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
                    // solution.ReplacementDataset != null is not supported; should be filtered out when moves loaded; IGNORE
                    // If we want to support this in the future, the code is similar to the newDataaset below, BUT
                    // we must check the symbology, labeling, definition query, and other layer properties for compatibility
                    // We should check that the old and replacement datasets are "compatible" i.e. it not possible to replace
                    // a raster with point feature class.
                    continue;
                }
                if (solution.NewDataset == null && solution.ReplacementDataset != null && solution.ReplacementLayerFilePath != null)
                {
                    // solution.ReplacementDataset != null is not supported; should be filtered out when moves loaded; IGNORE
                    // See notes above
                    continue;
                }
                if (solution.NewDataset != null && solution.ReplacementDataset == null && solution.ReplacementLayerFilePath == null)
                {
                    if (solution.Remarks == null)
                    {
                        // This is the optimal action.  The user is not prompted, since there is no good reason for a user not to click OK.
                        // The user will be warned that layers have been fixed, and they can choose to not save the changes.
                        autoFixesApplied += 1;
                        RepairLayer(dataLayer, oldDataset, solution.NewDataset.Value);
                    }
                    else
                    {
                        string msg =
                            $"The layer '{layerName}' is broken. The data has moved to a new location.  Do you want to fix the layer?";
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
                    // TODO: prompt user if they want the archive/trash version, or the new layer file (recommended)
                    // TODO: messageBox do you want to add layer (yes/no)  add solution.Remarks if not null
                    // TODO: if yes add layer
                    // TODO: messagebox do you want to delete the old layer (If you have customized this layer, you might want to inspect and apply by hand, then delete manually). Yes/no
                    // TODO: if yes, delete the broken layer
                    continue;
                }
                if (solution.NewDataset != null && solution.ReplacementDataset != null && solution.ReplacementLayerFilePath == null)
                {
                    // solution.ReplacementDataset != null is not supported; should be filtered out when moves loaded; IGNORE
                    continue;
                }
                if (solution.NewDataset != null && solution.ReplacementDataset != null && solution.ReplacementLayerFilePath != null)
                {
                    // solution.ReplacementDataset != null is not supported; should be filtered out when moves loaded; IGNORE
                }
            }

            //TODO: Refresh TOC
            ArcMap.Document.ActiveView.Refresh();
            ArcMap.Document.CurrentContentsView.Refresh(null);

            // Print a Summary
            brokenDataSources = GetBrokenDataSources();
            if (autoFixesApplied > 0 || unfixableLayers > 0 || brokenDataSources.Count > 0)
            {
                string msg = "";
                if (autoFixesApplied > 0) {
                    msg +=
                        $"{autoFixesApplied} broken layers were automatically fixed based on the new locations of known data sources. " +
                        "Close the document without saving if this is not what you want.";
                }
                if (autoFixesApplied > 0 && (unfixableLayers > 0 || brokenDataSources.Count > 0)) {
                    msg += "\n\n";
                }
                if (unfixableLayers > 0) {
                    msg +=
                        $"{unfixableLayers} broken layers could not be fixed; breakage is not due to changes on the PDS (X drive).";
                }
                if (unfixableLayers < brokenDataSources.Count) {
                    // We know that brokenDataSources.Count must be >= unfixableLayers, therefore some of the fixes need fixing
                    if (unfixableLayers > 0) {
                        msg += "\n\n";
                    }
                    msg += "Additional fixes are possible and needed.  Please save, close and reopen your map.";
                }
                msgBox.DoModal("Map Fixer Summary", msg, "OK", null, ArcMap.Application.hWnd);
            }
        }

        //FIXME: only need to deal with dataset name changes.  All other changes are not supported
        public void RepairLayer(IDataLayer2 dataLayer, Moves.GisDataset oldDataset, Moves.GisDataset newDataset)
        {
            // TODO: check and skip if (oldDataset.DatasourceType != newDataset.DatasourceType || oldDataset.WorkspaceProgID != newDataset.WorkspaceProgID)
            // This should be impossible by checks against the CSV and during the loading of the moves.
            // If it happens just do nothing and ignore it.
            // TODO: only check for if (oldDataset.DatasourceName == newDataset.DatasourceName)
            if (oldDataset.DatasourceName == newDataset.DatasourceName && oldDataset.DatasourceType == newDataset.DatasourceType && oldDataset.WorkspaceProgID == newDataset.WorkspaceProgID)
            {
                //TODO: This may fail in 10.6.1  See: https://community.esri.com/thread/221120-set-datasource-with-arcobjects
                IDataSourceHelperLayer helper = new DataSourceHelper() as IDataSourceHelperLayer;
                helper.FindAndReplaceWorkspaceNamePath((ILayer)dataLayer, oldDataset.WorkspacePath, newDataset.WorkspacePath, false);
            }
            else
            {
                // TODO: Rename the dataset
                // TODO: Maybe try: http://help.arcgis.com/en/sdk/10.0/arcobjects_net/componenthelp/index.html#/ReplaceName_Method/001200000ss3000000/
                //FIXME:  This is incomplete an maybe wrong
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
                // ReSharper disable once RedundantArgumentDefaultValue
                IEnumLayer layerEnumerator = map.Layers[null];
                ILayer layer;
                while((layer = layerEnumerator.Next()) != null)
                {
                    var layer2 = layer as ILayer2;
                    if (layer2 != null)
                    {
                        if (!layer2.Valid)
                        {
                            var dataLayer = layer2 as IDataLayer2;
                            if (dataLayer != null)
                            {
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
            IWorkspaceName workspaceName = new WorkspaceNameClass()
            {
                WorkspaceFactoryProgID = dataset.WorkspaceProgID, // "esriDataSourcesGDB.AccessWorkspaceFactory";
                PathName = dataset.WorkspacePath
            };
            IWorkspace workspace;
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
            IDatasetName datasetName;
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
                    // TODO: Log or messageBox the error;
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
                    // TODO: Log or messageBox the error;
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
                    // TODO: Log or messageBox the error;
                    return null;
                }
            }
            return null;
        }
    }
}
