using System;
using System.Collections.Generic;
using ESRI.ArcGIS.Carto;
using ESRI.ArcGIS.Geodatabase;
using ESRI.ArcGIS.Catalog;

namespace MapFixer
{
    public class MapFixer
    {
        public void FixMap(Moves moves)
        {
            var brokenDataSources = GetBrokenDataSources();
            // We do not need to do anything if there was nothing to fix
            if (brokenDataSources.Count == 0) {
                return;
            }
            var alert = new AlertForm();
            var selector = new SelectionForm();
            var autoFixesApplied = 0;
            var unFixableLayers = 0;
            var intentionallyBroken = 0;
            foreach (var item in brokenDataSources)
            {
                var mapIndex = item.Key;
                foreach (IDataLayer2 dataLayer in item.Value)
                {
                    var dataset = dataLayer as IDataset;
                    var layerName = dataset != null ? dataset.Name : ((ILayer2)dataLayer).Name;
                    Moves.GisDataset oldDataset = GetDataset(dataLayer);
                    Moves.Solution? maybeSolution = moves.GetSolution(oldDataset);
                    if (maybeSolution == null)
                    {
                        unFixableLayers += 1;
                        continue;
                    }
                    Moves.Solution solution = maybeSolution.Value;
                    if (solution.NewDataset != null && solution.ReplacementDataset == null &&
                        solution.ReplacementLayerFilePath == null && solution.Remarks == null)
                    {
                        // This is the optimal action.
                        // The user is not prompted, since there is no good reason for a user not to click OK.
                        // The user will be warned that layers have been fixed, and they can choose to not save the changes.
                        autoFixesApplied += 1;
                        RepairWithDataset(dataLayer, oldDataset, solution.NewDataset.Value);
                    }
                    else
                    {
                        selector.LayerName = layerName;
                        selector.Solution = solution;
                        selector.ShowDialog(new WindowWrapper(new IntPtr(ArcMap.Application.hWnd)));
                        if (selector.UseLayerFile)
                        {
                            RepairWithLayerFile(mapIndex, dataLayer, selector.LayerFile, selector.KeepBrokenLayer, alert);
                        }
                        else if (selector.UseDataset && selector.Dataset.HasValue)
                        {
                            RepairWithDataset(dataLayer, oldDataset, selector.Dataset.Value);
                        }
                        else
                        {
                            intentionallyBroken += 1;
                        }
                    }
                }
            }

            // Refresh TOC
            ArcMap.Document.UpdateContents(); //update the TOC
            ArcMap.Document.ActivatedView.Refresh(); // refresh the view

            // Print a Summary
            brokenDataSources = GetBrokenDataSources();
            if (autoFixesApplied > 0 || unFixableLayers > 0 || brokenDataSources.Count > intentionallyBroken)
            {
                string msg = "";
                if (autoFixesApplied > 0) {
                    msg +=
                        $"{autoFixesApplied} broken layers were automatically fixed based on the new locations of known data sources. " +
                        "Close the document without saving if this is not what you want.";
                }
                if (autoFixesApplied > 0 && (unFixableLayers > 0 || brokenDataSources.Count > 0)) {
                    msg += "\n\n";
                }
                if (unFixableLayers > 0) {
                    msg +=
                        $"{unFixableLayers} broken layers could not be fixed; breakage is not due to changes on the PDS (X drive).";
                }
                if (unFixableLayers < brokenDataSources.Count - intentionallyBroken) {
                    // We know that brokenDataSources.Count must be >= unFixableLayers, therefore some of the fixes need fixing
                    if (unFixableLayers > 0) {
                        msg += "\n\n";
                    }
                    msg += "Additional fixes are possible and needed.  Please save, close and reopen your map.";
                }
                alert.Text = @"Map Fixer Summary";
                alert.msgBox.Text = msg;
                alert.ShowDialog(new WindowWrapper(new IntPtr(ArcMap.Application.hWnd)));
            }
        }

        private void RepairWithLayerFile(int mapIndex, IDataLayer2 dataLayer, string newLayerFile, bool keepBrokenLayer, AlertForm alert)
        {
            // Add Layer File to ActiveView Snippet: (http://help.arcgis.com/en/sdk/10.0/arcobjects_net/componenthelp/index.html#//004900000050000000)
            IGxLayer gxLayer = new GxLayer();
            IGxFile gxFile = (IGxFile)gxLayer;
            gxFile.Path = newLayerFile;
            if (gxLayer.Layer != null)
            {
                // AddLayer will add the new layer at the most appropriate point in the TOC.
                //   This is much easier and potentially less confusing than adding at the old data location. 
                ArcMap.Document.Maps.Item[mapIndex].AddLayer(gxLayer.Layer);
                if (!keepBrokenLayer)
                {
                    ArcMap.Document.Maps.Item[mapIndex].DeleteLayer((ILayer)dataLayer);
                }
            }
            else
            {
                // Notify the user that the LayerFile could not be opened (missing, corrupt, ...)
                alert.Text = @"Error";
                alert.msgBox.Text = $"The layer file '{newLayerFile}' could not be opened.";
                alert.ShowDialog(new WindowWrapper(new IntPtr(ArcMap.Application.hWnd)));
            }
        }

        //TODO: only need to deal with dataset name changes.  All other changes are not supported
        private void RepairWithDataset(IDataLayer2 dataLayer, Moves.GisDataset oldDataset, Moves.GisDataset newDataset)
        {
            // TODO: check and skip if (oldDataset.DatasourceType != newDataset.DatasourceType || oldDataset.WorkspaceProgId != newDataset.WorkspaceProgId)
            // This should be impossible by checks against the CSV and during the loading of the moves.
            // If it happens just do nothing and ignore it.
            // TODO: only check for if (oldDataset.DatasourceName == newDataset.DatasourceName)
            if (oldDataset.DatasourceName == newDataset.DatasourceName && oldDataset.DatasourceType == newDataset.DatasourceType && oldDataset.WorkspaceProgId == newDataset.WorkspaceProgId)
            {
                //TODO: This may fail in 10.6.1  See: https://community.esri.com/thread/221120-set-datasource-with-arcobjects
                var helper = (IDataSourceHelperLayer)new DataSourceHelper();
                helper.FindAndReplaceWorkspaceNamePath((ILayer)dataLayer, oldDataset.WorkspacePath, newDataset.WorkspacePath, false);
            }
            else
            {
                // TODO: Rename the dataset
                // TODO: Maybe try: http://help.arcgis.com/en/sdk/10.0/arcobjects_net/componenthelp/index.html#/ReplaceName_Method/001200000ss3000000/
                // TODO:  This is incomplete an maybe wrong
                // IDataset dataset = OpenDataset(newDataset);
                // Patch the layer, and trigger the TOC and map updates, etc...
                // see http://help.arcgis.com/en/sdk/10.0/arcobjects_net/componenthelp/index.html#//00490000002r000000
            }
        }

        private Dictionary<int,List<IDataLayer2>> GetBrokenDataSources()
        {
            var brokenDataSources = new Dictionary<int, List<IDataLayer2>>();
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
                                if (!brokenDataSources.ContainsKey(i))
                                {
                                    brokenDataSources[i] = new List<IDataLayer2>();
                                }
                                brokenDataSources[i].Add(dataLayer);
                            }
                        }
                    }
                }
            }
            return brokenDataSources;
        }

        private Moves.GisDataset GetDataset(IDataLayer2 dataLayer)
        {
            var datasetName = (IDatasetName)dataLayer.DataSourceName;
            IWorkspaceName workspaceName = datasetName.WorkspaceName;
            return new Moves.GisDataset(workspaceName.PathName, workspaceName.WorkspaceFactoryProgID,
                datasetName.Name, datasetName.Type);
        }

        /*
        public IDataset OpenDataset(Moves.GisDataset dataset)
        {
            IWorkspaceName workspaceName = new WorkspaceNameClass()
            {
                WorkspaceFactoryProgID = dataset.WorkspaceProgId, // "esriDataSourcesGDB.AccessWorkspaceFactory";
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

        [SuppressMessage("ReSharper", "SuspiciousTypeConversion.Global")]
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
        */
    }
}
