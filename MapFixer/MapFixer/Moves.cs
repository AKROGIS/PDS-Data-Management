using ESRI.ArcGIS.Geodatabase;
using System;
using System.Collections.Generic;
using System.Diagnostics.CodeAnalysis;
using System.IO;

namespace MapFixer
{
    /// <summary>The <c>Moves</c> constructor must be given a file path to a CSV like file with a very specific format.
    /// See the constructor for details on the format and conventions.  During initialization, it will
    /// generate a private sequential <c>List{Move}</c>.  Each move represents singular action that moved a
    /// piece of gis data (a workspace/folder or a specific dataset) on the PDS from one file system
    /// location to another.
    /// The only public method on Moves is <c>GetSolution</c>, which takes a <c>GisDataset</c> (usually obtained from
    /// a map document), and returns an optional <c>Solution</c>, which if non-null represents the move for that
    /// <c>GisDataset</c>.  Look at the <c>Solution</c> sub class for details.</summary>
    /// <see cref="GetSolution"/>
    /// <see cref="GisDataset"/>
    /// <see cref="Solution"/>

    public class Moves
    {
        // Moves only deals with filesystem objects, so workspace is always a filesystem path
        public struct Workspace : IEquatable<Workspace>
        {
            public Workspace(string folder)
            {
                Folder = folder;
            }
            public string Folder { get; }

            public bool IsOnPds
            {
                get
                {
                    if (Folder.StartsWith(@"X:\", StringComparison.OrdinalIgnoreCase))
                        return true;
                    if (Folder.StartsWith(@"\\inpakrovmdist\gisdata\", StringComparison.OrdinalIgnoreCase))
                        return true;
                    return Folder.StartsWith(@"\\inpakrovmdist\gisdata2\", StringComparison.OrdinalIgnoreCase);
                }
            }

            public bool IsInTrash
            {
                get
                {
                    if (Path.IsPathRooted(Folder) && !IsOnPds)
                        return false;
                    var path = WithoutVolume;
                    return path.StartsWith(@"Trash\", StringComparison.OrdinalIgnoreCase) ||
                           path.StartsWith(@"Extras\Trash\", StringComparison.OrdinalIgnoreCase) ||
                           path.StartsWith(@"Extras2\Trash\", StringComparison.OrdinalIgnoreCase);
                }
            }

            public bool IsInArchive
            {
                get
                {
                    if (Path.IsPathRooted(Folder) && !IsOnPds)
                        return false;
                    var path = WithoutVolume;
                    return path.StartsWith(@"Archive\", StringComparison.OrdinalIgnoreCase) ||
                           path.StartsWith(@"Extras\Archive\", StringComparison.OrdinalIgnoreCase) ||
                           path.StartsWith(@"Extras2\Archive\", StringComparison.OrdinalIgnoreCase);
                }
            }

            public string WithoutVolume => Folder.Substring(Path.GetPathRoot(Folder).Length);


            #region Equality

            public override bool Equals(object obj)
            {
                return obj is Workspace && Equals((Workspace)obj);
            }

            public bool Equals(Workspace other)
            {
                return Folder == other.Folder;
            }

            public override int GetHashCode()
            {
                return Folder.GetHashCode();
            }

            public static bool operator ==(Workspace lhs, Workspace rhs)
            {
                return lhs.Equals(rhs);
            }

            public static bool operator !=(Workspace lhs, Workspace rhs)
            {
                return !(lhs == rhs);
            }
            #endregion
        }

        public struct GisDataset: IEquatable<GisDataset>
        {
            // esriDatasetType: https://desktop.arcgis.com/en/arcobjects/latest/net/webframe.htm#esriDatasetType.htm
            // esriWorkspaceProgID: https://desktop.arcgis.com/en/arcobjects/latest/net/webframe.htm#IWorkspaceName_WorkspaceFactoryProgID.htm

            public GisDataset(string workspacePath, string workspaceProgId, string datasourceName, esriDatasetType datasourceType)
            {
                if (string.IsNullOrWhiteSpace(workspacePath))
                    throw new ArgumentException("Initial value must not be null, empty or whitespace", nameof(workspacePath));
                if (string.IsNullOrWhiteSpace(workspaceProgId))
                    throw new ArgumentException("Initial value must not be null, empty or whitespace", nameof(workspaceProgId));
                if (string.IsNullOrWhiteSpace(datasourceName))
                    throw new ArgumentException("Initial value must not be null, empty or whitespace", nameof(datasourceName));
                Workspace = new Workspace(workspacePath);
                WorkspaceProgId = workspaceProgId;
                DatasourceName = datasourceName;
                DatasourceType = datasourceType;
            }

            public Workspace Workspace { get; }
            public string WorkspaceProgId { get; }
            public string DatasourceName { get; }
            public esriDatasetType DatasourceType { get; }

            public bool Equals(GisDataset other)
            {
                return Workspace == other.Workspace && WorkspaceProgId == other.WorkspaceProgId &&
                    DatasourceName == other.DatasourceName && DatasourceType == other.DatasourceType;
            }

        }

        struct PartialGisDataset
        {
            public PartialGisDataset(string workspacePath, string workspaceProgId=null, string datasourceName=null, esriDatasetType? datasourceType=null)
            {
                if (string.IsNullOrWhiteSpace(workspacePath))
                    throw new ArgumentException("Initial value must not be null, empty or whitespace", nameof(workspacePath));
                Workspace = new Workspace(workspacePath);
                WorkspaceProgId = string.IsNullOrWhiteSpace(workspaceProgId) ? null : workspaceProgId;
                DatasourceName = string.IsNullOrWhiteSpace(datasourceName) ? null : datasourceName;
                DatasourceType = datasourceType;
            }

            public Workspace Workspace { get; }
            public string WorkspaceProgId { get; }
            public string DatasourceName { get; }
            public esriDatasetType? DatasourceType { get; }

            public GisDataset ToGisDataset(GisDataset gisDataset)
            {
                return new GisDataset(
                    Workspace.Folder,
                    WorkspaceProgId ?? gisDataset.WorkspaceProgId,
                    DatasourceName ?? gisDataset.DatasourceName,
                    DatasourceType ?? gisDataset.DatasourceType
                );
            }
        }

        /// <summary>A <c>Solution</c> represents the moved state of an input <c>GisDataset</c>.
        /// If a GIS dataset was moved, there is one required attribute <c>Timestamp</c> and 4 optional
        /// attributes. At least one of the optional attributes will be provided. A Solution with all
        /// 4 attributes null is invalid and will not be created (a null solution will be returned).
        ///</summary>
        ///
        /// <remarks>
        /// NewDataset | replacement | layer file | Comments
        /// not-null   | not-null    | not-null   | Not supported
        /// not-null   | not-null    | null       | Not supported
        /// not-null   | null        | not-null   | Prompt user to select choice
        /// not-null   | null        | null       | Typical case; Easy fix; no prompt
        /// null       | not-null    | not-null   | Not supported
        /// null       | not-null    | null       | Not supported
        /// null       | null        | not-null   | Easy fix, replace broken layer with new layer file (prompt user?)
        /// null       | null        | null       | Not valid unless remarks provided (very unusual to not provide an upgrade option)
        ///
        /// "Not supported" combinations will be skipped in CSV load; error in CSV check.
        /// When newDataset is not-null it can not differ from the old in workspace type or data type; skipped in CSV load; error in CSV check
        /// Remarks are optional for any valid combination, and will be shown to the user for additional context.
        /// In the last case the remarks must tell the user why no upgrade is available.
        /// </remarks>
        public struct Solution
        {
            public Solution(DateTime timestamp, GisDataset? newDataset = null, GisDataset? replacementDataset = null, string replacementLayerFilePath = null, string remarks = null)
            {
                if (newDataset == null && replacementDataset == null && string.IsNullOrWhiteSpace(replacementLayerFilePath) && string.IsNullOrWhiteSpace(remarks))
                    throw new NotSupportedException("At least one of the parameters must be non-null");
                Timestamp = timestamp;
                NewDataset = newDataset;
                ReplacementDataset = replacementDataset;
                ReplacementLayerFilePath = string.IsNullOrWhiteSpace(replacementLayerFilePath) ? null : replacementLayerFilePath;
                Remarks = string.IsNullOrWhiteSpace(remarks) ? null : remarks;
            }

            /// <summary>When the input GisDataset was moved</summary>
            // ReSharper disable once MemberCanBePrivate.Global
            // ReSharper disable once UnusedAutoPropertyAccessor.Global
            public DateTime Timestamp { get; }

            /// <summary>The new location of the input GisDataset.  This will almost always be non-null.
            /// It will be null if GisDataset is in the trash and was deleted on the timestamp.
            /// The new dataset MUST have the same format, schema and semantics as the input dataset.
            /// This generally means that the dataset is the same it was just moved or renamed.</summary>
            public GisDataset? NewDataset { get; }
            /// <summary>A replacement dataset is only used if the NewDataset is null. In which case,
            /// this is the new dataset. In general it is problematic to replace an dataset in a map with
            /// another arbitrary dataset.  Symbology, definition queries, labeling, etc could be broken
            /// unless the replacement dataset has the same schema and semantics as the original dataset.
            /// Replacement datasets are currently not supported. Use the layer file option instead</summary>
            public GisDataset? ReplacementDataset { get; }
            /// <summary>A dataset that has been moved to the Archive, Trash, or deleted from Trash should
            /// (must?) provide a new layer file that is the recommended replacement for the moved dataset.
            /// Users should be encouraged to use the new layer file in lieu of the obsolete data.</summary>
            public string ReplacementLayerFilePath { get; }
            ///<summary>A comment on the move. This is presented to the user to help understand unusual moves.</summary>
            public string Remarks { get; }
        }

        struct Move
        {
            public Move(DateTime timestamp, PartialGisDataset oldDataset, PartialGisDataset? newDataset,
                PartialGisDataset? replacementDataset = null, string replacementLayerFilePath = null,
                string remarks = null)
            {
                Timestamp = timestamp;
                OldDataset = oldDataset;
                NewDataset = newDataset;
                ReplacementDataset = replacementDataset;
                ReplacementLayerFilePath = string.IsNullOrWhiteSpace(replacementLayerFilePath) ? null : replacementLayerFilePath;
                Remarks = string.IsNullOrWhiteSpace(remarks) ? null : remarks;
            }

            public DateTime Timestamp { get; }
            public PartialGisDataset OldDataset { get; }
            private PartialGisDataset? NewDataset { get; }
            private PartialGisDataset? ReplacementDataset { get; }
            public string ReplacementLayerFilePath { get; }
            public string Remarks { get; }

            public PartialGisDataset? PatchNewDataset(GisDataset source)
            {
                if (NewDataset == null)
                    return null;
                return PatchDataset(source, NewDataset.Value);
            }

            public PartialGisDataset? PatchReplacementDataset(GisDataset source)
            {
                if (ReplacementDataset == null)
                    return null;
                return PatchDataset(source, ReplacementDataset.Value);
            }

            private PartialGisDataset? PatchDataset(GisDataset source, PartialGisDataset newDataset)
            {
                //A partial dataset must have a fully specified workspace, but a move may describe a parent folder
                //This method patches the new dataset by applying the move to the source workspace
                //The workspace in the move's old dataset must be a prefix of the input source for this method to return a non-null result

                var searchString = OldDataset.Workspace.Folder;
                int positionOfSearchString = source.Workspace.Folder.IndexOf(searchString, StringComparison.OrdinalIgnoreCase);
                if (positionOfSearchString < 0)
                {
                    return null;
                }
                var newWorkspace = source.Workspace.Folder.Substring(0, positionOfSearchString) +
                    newDataset.Workspace +
                    source.Workspace.Folder.Substring(positionOfSearchString + searchString.Length);

                return new PartialGisDataset(
                    newWorkspace,
                    newDataset.WorkspaceProgId,
                    newDataset.DatasourceName,
                    newDataset.DatasourceType
                );
            }
        }

        private readonly List<Move>  _moves = new List<Move>();

        public Moves(string csvPath, char delimiter='|', bool check=false)
        {
            const int fieldCount = 15;
            int lineNum = 0;
            //This is a very simple CSV parser, as the input is very simple.
            //The constructor is very forgiving on the input.  It ignores any record which isn't valid.  It doesn't throw any exceptions
            //It may contain an empty list of moves, which will is dealt with appropriately
            //The csv file used for input should be validated whenever it is edited.
            //Validation rules:
            //   Each row requires a timestamp, and the timestamp must be ordered from oldest to newest
            //   Workspace paths must not have volume information
            //   Replacement datasets are not supported - use replacement layer file
            //   New and old datasets must not differ in workspace type or dataset type - use replacement layer file
            //   If newDataset is null (i.e old is deleted), trash or archive, then a replacement layer file should be provided.
            //      A remark is all that is mandatory when newDataset is null.
            //   Column 2 and 6 must be progID strings
            //   Columns 4 and 8 must be datasetTypes
            //   workspace changes (i.e. dataSourceName is null) should be exclusive.
            //      i.e. if there is a move /a/b => /x/y, we should not have /a/b/c => ...

            try
            {
                DateTime previousTimestamp = DateTime.MinValue;
                foreach (string line in File.ReadLines(csvPath))
                {
                    lineNum += 1;
                    var row = line.Split(delimiter);
                    if (row.Length != fieldCount)
                    {
                        if (check)
                        {
                            Console.WriteLine($"Warning: Wrong number of columns ({row.Length} not {fieldCount}) at line {lineNum}; Skipping.");
                        }
                        continue;
                    }
                    if (lineNum == 1 && row[0] == "timestamp")
                    {
                        // Skip a header row if present
                        continue;
                    }

                    DateTime timestamp;
                    if (!DateTime.TryParse(row[0], out timestamp))
                    {
                        if (check)
                        {
                            Console.WriteLine($"Warning: Value in column #1 ({row[0]}) at line {lineNum} is not a DateTime; Skipping.");
                        }
                        continue;
                    }
                    if (timestamp < previousTimestamp)
                    {
                        if (check)
                        {
                            Console.WriteLine($"Warning: Timestamp in column #1 must be increasing. Line {lineNum} is out of order; Skipping.");
                        }
                        continue;
                    }
                    previousTimestamp = timestamp;

                    if (string.IsNullOrWhiteSpace(row[1]))
                    {
                        if (check)
                        {
                            Console.WriteLine($"Warning: No value provided for column #2 (Old Workspace Path) at line {lineNum}; Skipping.");
                        }
                        continue;
                    }
                    else if (!IsSimpleRelativePath(row[1]))
                    {
                        if (check)
                        {
                            Console.WriteLine($"Warning: Value in column #1 ({row[1]}) at line {lineNum} is not a simple relative path; Skipping.");
                        }
                        continue;
                    }
                    esriDatasetType? dataSourceType = null;
                    esriDatasetType tempDataSourceType;
                    if (Enum.TryParse(row[4], out tempDataSourceType))
                    {
                        dataSourceType = tempDataSourceType;
                    }
                    if (dataSourceType == null && !string.IsNullOrWhiteSpace(row[4]))
                    {
                        if (check)
                        {
                            Console.WriteLine($"Warning: Value in column #5 ({row[4]}) at line {lineNum} is not an esriDatasetType; Skipping.");
                        }
                        continue;
                    }

                    if (!string.IsNullOrWhiteSpace(row[2]) && !IsWorkspaceFactoryProgId(row[2]))
                    {
                        if (check)
                        {
                            Console.WriteLine($"Warning: Value in column #3 ({row[2]}) at line {lineNum} is not an esriProgID; Skipping.");
                        }
                        continue;
                    }

                    var oldDataset = new PartialGisDataset(row[1], row[2], row[3], dataSourceType);

                    PartialGisDataset? newDataset = null;
                    if (!string.IsNullOrWhiteSpace(row[5]))
                    {
                        if (!IsSimpleRelativePath(row[5]))
                        {
                            if (check)
                            {
                                Console.WriteLine($"Warning: Value in column #6 ({row[5]}) at line {lineNum} is not a simple relative path; Skipping.");
                            }
                            continue;
                        }
                        if (!string.IsNullOrWhiteSpace(row[6]) && row[2] != row[6])
                        {
                            if (check)
                            {
                                Console.WriteLine($"Warning: Column #7 does not match column #3 at line {lineNum} (new_workspace_type = {row[6]} <> old_workspace_type = {row[2]}); Skipping.");
                            }
                            continue;
                        }
                        // We do not need to check that row[6] is a progID, because it must be null or the same as row[2], which has already been checked.
                        dataSourceType = null;
                        if (!string.IsNullOrWhiteSpace(row[8]))
                        {
                            if (Enum.TryParse(row[8], out tempDataSourceType))
                            {
                                dataSourceType = tempDataSourceType;
                            }
                            if (dataSourceType == null)
                            {
                                if (check)
                                {
                                    Console.WriteLine($"Warning: Value in column #9 ({row[8]}) at line {lineNum} is not an esriDatasetType; Skipping.");
                                }
                                continue;
                            }
                            if (row[4] != row[8])
                            {
                                if (check)
                                {
                                    Console.WriteLine($"Warning: Column #9 does not match column #5 at line {lineNum} (new_dataset_type = {row[8]} <> old_dataset_type = {row[4]}); Skipping.");
                                }
                                continue;
                            }
                        }
                        newDataset = new PartialGisDataset(row[5], row[6], row[7], dataSourceType);
                    }

                    // replacement data source is not supported, so we ignore row[9] to row[12]
                    if (check)
                    {
                        if (!string.IsNullOrWhiteSpace(row[9]) || !string.IsNullOrWhiteSpace(row[10]) || 
                            !string.IsNullOrWhiteSpace(row[11]) || !string.IsNullOrWhiteSpace(row[12]))
                        {
                            Console.WriteLine($"Warning: Values in columns 10 to 13 (Replacement datasets) at line {lineNum} are not supported; Using null for replacement dataset.");
                        }
                    }

                    var layerFile = string.IsNullOrWhiteSpace(row[13]) ? null : row[13].Trim();
                    if (layerFile != null)
                    {
                        if (!IsSimilarToLayerFile(layerFile))
                        {
                            if (check)
                            {
                                Console.WriteLine($"Warning: Value in column #14 ({layerFile}) at line {lineNum} is not a valid layer file; Skipping.");
                            }
                            continue;
                        }
                    }

                    var remarks = string.IsNullOrWhiteSpace(row[14]) ? null : row[14].Trim();

                    if (newDataset == null && layerFile == null && remarks == null)
                    {
                        if (check)
                        {
                            Console.WriteLine($"Warning: Incomplete move at line {lineNum}. Neither a new dataset (column #6), nor a replacement layer file (column #14), nor a remark (column #15) was provided; Skipping.");
                        }
                        continue;
                    }
                    if (check)
                    {
                        if ((newDataset == null || newDataset.Value.Workspace.IsInTrash || newDataset.Value.Workspace.IsInArchive) && layerFile == null)
                        {
                            Console.WriteLine($"Warning: A value in column #14 (replacement_layerFile_path) at line {lineNum} is STRONGLY encouraged when column #5-8 (new_dataset) is null or in the Trash/Archive.");
                        }
                    }

                    _moves.Add(new Move(timestamp, oldDataset, newDataset, null, layerFile, remarks));
                }
                if (check)
                {
                    Console.WriteLine($"Scanned {lineNum} lines. Found {_moves.Count} moves.");
                    Console.WriteLine("Checking consistency of moves");
                    ConsistencyCheck(_moves);
                    Console.WriteLine("Done.");
                }
            }
            catch (Exception e)
            {
                if (check)
                {
                    Console.WriteLine($"Aborting due to error at line {lineNum}: {e.Message}.");
                }
            }
        }

        private bool IsSimpleRelativePath(string path)
        {
            // Verify path is a simple relative path, i.e. it does not start with a UNC or drive letter slash, or dot.
            // Could also check that it is a valid path
            // Assume that all ArcGIS work spaces appear to be file system objects
            // (This may not always be true, but is for all work spaces that we currently use.)
            if (path == null)
                return false;
            if (path.IndexOfAny(Path.GetInvalidPathChars()) != -1)
                return false;
            if (Path.IsPathRooted(path))
                return false;
            if (path.StartsWith("."))
                return false;
            if (path.StartsWith("/"))
                return false;
            return true;
        }

        [SuppressMessage("ReSharper", "InconsistentNaming")]
        [SuppressMessage("ReSharper", "IdentifierTypo")]
        [SuppressMessage("ReSharper", "UnusedMember.Global")]
        [SuppressMessage("ReSharper", "UnusedMember.Local")]
        // For examples, See https://desktop.arcgis.com/en/arcobjects/latest/net/webframe.htm#IWorkspaceName_WorkspaceFactoryProgID.htm)
        // To comply with C# enum member naming rules, the '.' in the progId has been replaced with a '_'
        // Derived from list of CoClasses at https://desktop.arcgis.com/en/arcobjects/10.5/net/webframe.htm#IWorkspaceFactory.htm
        private enum WellKnownWorkspaceProgIds
        {
            esriDataSourcesFile_ArcInfoWorkspaceFactory,
            esriDataSourcesFile_CadWorkspaceFactory,
            esriDataSourcesFile_GeoRSSWorkspaceFactory,
            esriDataSourcesFile_PCCoverageWorkspaceFactory,
            esriDataSourcesFile_SDCWorkspaceFactory,
            esriDataSourcesFile_ShapefileWorkspaceFactory,
            esriDataSourcesFile_StreetMapWorkspaceFactory,
            esriDataSourcesFile_TinWorkspaceFactory,
            esriDataSourcesFile_VpfWorkspaceFactory,

            esriDataSourcesGDB_AccessWorkspaceFactory,
            esriDataSourcesGDB_FileGDBScratchWorkspaceFactory,  //Not supported
            esriDataSourcesGDB_FileGDBWorkspaceFactory,
            esriDataSourcesGDB_InMemoryWorkspaceFactory,   //Not supported
            esriDataSourcesGDB_ScratchWorkspaceFactory,  //Not supported
            esriDataSourcesGDB_SdeWorkspaceFactory,  //Not supported
            esriDataSourcesGDB_SqlWorkspaceFactory,  //Not supported

            esriDataSourcesNetCDF_NetCDFWorkspaceFactory,  //Not supported

            esriDataSourcesOleDB_ExcelWorkspaceFactory,
            esriDataSourcesOleDB_OLEDBWorkspaceFactory,  //Not supported
            esriDataSourcesOleDB_TextFileWorkspaceFactory,

            esriDataSourcesRaster_RasterWorkspaceFactory,

            esriTrackingAnalyst_AMSWorkspaceFactory,
            esriCarto_FeatureServiceWorkspaceFactory,  //Not supported
            esriGISClient_IMSWorkspaceFactory,  //Not supported
            esriGeoDatabase_PlugInWorkspaceFactory,  //Not supported
            esriGeoDatabaseExtensions_LasDatasetWorkspaceFactory,
            esriGeoprocessing_ToolboxWorkspaceFactory
        }

        private bool IsWorkspaceFactoryProgId(string progId)
        {
            // Verify that progId is a valid WorkspaceFactoryProgID
            // There may be other valid progId that I have not identified, so this may produce some false positives
            WellKnownWorkspaceProgIds temp;
            return Enum.TryParse(progId.Replace('.','_'), out temp);
        }

        private bool IsSimilarToLayerFile(string layerFile)
        {
            // Verify layerFile appears to be a valid file system object ending in '.lyr'
            // Just check the string. Do not perform any IO as this is called in a loop
            if (layerFile == null)
                return false;
            if (layerFile.IndexOfAny(Path.GetInvalidPathChars()) != -1)
                return false;
            if (!layerFile.StartsWith("X:\\", StringComparison.OrdinalIgnoreCase))
                return false;
            return layerFile.EndsWith(".lyr", StringComparison.OrdinalIgnoreCase);
        }

        private void ConsistencyCheck(List<Move> moves)
        {
            // Checks each move in the list against all others moves to ensure
            // 1) There are no duplicates (Workspace.Folder/DatasourceName matches) in the oldDataset
            // 2) If moves have the same DatasourceName (null == null), then one Workspace.Folder cannot be a proper subset of the other
            int next = 0;
            foreach (Move move in moves)
            {
                string path = move.OldDataset.Workspace.Folder;
                string name = move.OldDataset.DatasourceName;
                next += 1;
                for (int i = next; i < moves.Count; i++)
                {
                    string otherPath = moves[i].OldDataset.Workspace.Folder;
                    string otherName = moves[i].OldDataset.DatasourceName;
                    //path and otherPath are guaranteed to be non-null
                    //name and otherName may be null, but not whitespace only
                    // from String.Compare: One or both comparands can be null. By definition, any string,
                    //   including the empty string (""), compares greater than a null reference;
                    //   and two null references compare equal to each other.

                    // If the names do not match, I do not care about the path, we are ok regardless
                    if (String.Compare(name, otherName, StringComparison.OrdinalIgnoreCase) != 0)
                    {
                        continue;
                    }
                    // We know the names match (including null == null)
                    if (String.Compare(path, otherPath, StringComparison.OrdinalIgnoreCase) == 0)
                    {
                        Console.WriteLine($"ERROR: Move {next - 1} has the same workspace/dataset ({path}\\{name}) as move {i}.");
                        continue;
                    }
                    // /a/b/name is different from /a/b/c/name, and ok.
                    // /a/b/{null} is a prefix for /a/b/c/{null} and will cause confusion.
                    if (name != null)
                        continue;
                    // We need to append a \ to avoid a match like
                    // A\B\C as a prefix for A\B\CDE  (it is a prefix for A\B\C\DE)
                    string prefix = otherPath.EndsWith("\\", StringComparison.OrdinalIgnoreCase) ? otherPath : otherPath + "\\";
                    if (path.StartsWith(prefix, StringComparison.OrdinalIgnoreCase))
                    {
                        Console.WriteLine($"ERROR: The workspace for Move {next} ({path}) starts with the workspace in move {i + 1} ({otherPath}).");
                        continue;
                    }
                    prefix = path.EndsWith("\\", StringComparison.OrdinalIgnoreCase) ? path : path + "\\";
                    if (otherPath.StartsWith(prefix, StringComparison.OrdinalIgnoreCase))
                    {
                        Console.WriteLine($"ERROR: The workspace for Move {i + 1} ({otherPath}) starts with the workspace in move {next} ({path}).");
                    }
                }

            }
        }

        private bool IsDataSourceMatch(GisDataset dataset, PartialGisDataset moveFrom)
        {
            if (dataset.DatasourceName == null)
                return false;
            if (moveFrom.DatasourceName == null)
                return false;
            if (String.Compare(dataset.DatasourceName, moveFrom.DatasourceName, StringComparison.OrdinalIgnoreCase) != 0)
                return false;
            if (moveFrom.DatasourceType != null && moveFrom.DatasourceType.Value != dataset.DatasourceType)
                return false;
            return IsWorkspaceMatch(dataset, moveFrom);
        }

        private bool IsWorkspaceMatch(GisDataset dataset, PartialGisDataset moveFrom)
        {
            // Assumes workspace paths in moves do not have volume information
            string movePath = moveFrom.Workspace.Folder;
            string fullPath = dataset.Workspace.WithoutVolume;
            if (moveFrom.WorkspaceProgId != null && moveFrom.WorkspaceProgId == dataset.WorkspaceProgId)
                return false;
            return string.Compare(fullPath, movePath, StringComparison.OrdinalIgnoreCase) == 0;
        }

        private bool IsPartialWorkspaceMatch(GisDataset dataset, PartialGisDataset moveFrom)
        {
            // A partial workspace match (i.e. the current or an ancestral folder has moved) is only valid
            // if the moveFrom.DatasourceName is null; if not null, then we must do a DataSourceMatch
            if (moveFrom.DatasourceName != null)
                return false;
            // Assumes workspace paths in moves do not have volume information
            string movePath = moveFrom.Workspace.Folder;
            string fullPath = dataset.Workspace.WithoutVolume;
            // Just searching for oldPath somewhere in newPath could yield some false positives.
            // Instead, strip the volume and only match the beginning of the string
            return fullPath.StartsWith(movePath, StringComparison.OrdinalIgnoreCase);
        }

        private Move? FindFirstMatchingMove(GisDataset dataset, DateTime since)
        {
            // Assumes moves list is in chronological order
            foreach (Move move in _moves)
            {
                if (move.Timestamp <= since)
                    continue;

                if (IsDataSourceMatch(dataset, move.OldDataset) ||
                    IsPartialWorkspaceMatch(dataset, move.OldDataset))
                {
                    return move;
                }
            }
            return null;
        }

        public Solution? GetSolution(GisDataset oldDataset, DateTime since = default(DateTime))
        {
            // default for since is the earliest possible DateTime, which will consider all moves in the database
            // Returns the first move in the database since the date given.  The solution will have a timestamp when the move was made
            // Be sure to call this again after the user has applied the given fix to see if there are subsequent moves that should be
            // applied to the fix.  Keep going until there are no more solutions.
            // Example: at time 1 /a/b/c is moved to /d/e/f
            // then at time 2 /d/e/f is moved to /g/h/i
            // then at time 3 /g/h/i is deleted and replaced by  /1/2/3.
            // ultimately, the user should not be given the option to use /d/e/f since it doesn't exist.
            // however this gets complicated.  For example
            // At time 1 /a/b/c is moved to the archive and a replacement of /d/e/f is offered
            // at time 2 archive/a/b/c is moved to the trash and replaced by /1/2/3
            // at time 3 /d/e/f is moved to archive and replaced by /4/5/6
            // The user with /a/b/c might want 1/2/3, 4/5/6, archive/d/e/f or trash/a/b/c.  To resolve this
            // The user should be given the choice from time 1, then the choice from time 2 or time 3 depending
            // on the first choice.

            // The timestamp is really not that helpful. It is only useful when doing a second search, and then
            // the moves that are known by date to be not applicable can be skipped.

            // IMPORTANT: the timestamp does not solve this problem:
            // at time 1 dataset /a/b/c is created (creates are not logged in the moves dataset)
            // at time 2 dataset /a/b/c is moved to /d/e/f (and logged)
            // at time 3 a new dataset /a/b/c is created (not logged)
            // at time 4 new dataset /a/b/c is moved to /g/h/i (logged)
            // GetSolution will always return the move at time 2 when first checking /a/b/c.
            // GetSolution could correctly return the move at time4 if given a start time after time 2.
            // However, we do not know if the map added data /a/b/c before time 2 or after time 3.
            // The date a layer is added is not stored in the map document.
            // We will try to discourage this kind of renaming situation.

            if (!oldDataset.Workspace.IsOnPds)
                return null;

            Move? maybeMove = FindFirstMatchingMove(oldDataset, since);
            if (maybeMove == null)
                return null;

            Move move = maybeMove.Value;
            var newDataset = move.PatchNewDataset(oldDataset);
            var replacementDataset = move.PatchReplacementDataset(oldDataset);
            var layerFile = move.ReplacementLayerFilePath;
            var remarks = move.Remarks;
            if (newDataset == null && replacementDataset == null && layerFile == null && remarks == null)
                return null;

            return new Solution(move.Timestamp, newDataset?.ToGisDataset(oldDataset), replacementDataset?.ToGisDataset(oldDataset), layerFile, remarks);
        }
    }
}
