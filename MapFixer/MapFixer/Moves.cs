using ESRI.ArcGIS.Geodatabase;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;

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
        public struct GisDataset: IEquatable<GisDataset>
        {
            // esriDatasetType: https://desktop.arcgis.com/en/arcobjects/latest/net/webframe.htm#esriDatasetType.htm
            // esriWorkspaceProgID: https://desktop.arcgis.com/en/arcobjects/latest/net/webframe.htm#IWorkspaceName_WorkspaceFactoryProgID.htm

            public GisDataset(string workspacePath, string workspaceProgID, string datasourceName, esriDatasetType datasourceType)
            {
                if (string.IsNullOrWhiteSpace(workspacePath))
                    throw new ArgumentException("Initial value must not be null, empty or whitespace", nameof(workspacePath));
                if (string.IsNullOrWhiteSpace(workspaceProgID))
                    throw new ArgumentException("Initial value must not be null, empty or whitespace", nameof(workspaceProgID));
                if (string.IsNullOrWhiteSpace(datasourceName))
                    throw new ArgumentException("Initial value must not be null, empty or whitespace", nameof(datasourceName));
                WorkspacePath = workspacePath;
                WorkspaceProgID = workspaceProgID;
                DatasourceName = datasourceName;
                DatasourceType = datasourceType;
            }

            public string WorkspacePath { get; }
            public string WorkspaceProgID { get; }
            public string DatasourceName { get; }
            public esriDatasetType DatasourceType { get; }

            public bool Equals(GisDataset other)
            {
                return WorkspacePath == other.WorkspacePath && WorkspaceProgID == other.WorkspaceProgID &&
                    DatasourceName == other.DatasourceName && DatasourceType == other.DatasourceType;
            }

            public bool IsOnPDS
            {
                get
                {
                    if (WorkspacePath.StartsWith(@"X:\", StringComparison.OrdinalIgnoreCase))
                        return true;
                    if (WorkspacePath.StartsWith(@"\\inpakrovmdist\gistata\", StringComparison.OrdinalIgnoreCase))
                        return true;
                    return WorkspacePath.StartsWith(@"\\inpakrovmdist\gistata2\", StringComparison.OrdinalIgnoreCase);
                }
            }

            public string WorkspaceWithoutVolume => WorkspacePath.Substring(Path.GetPathRoot(WorkspacePath).Length);

            public bool IsInTrash
            {
                get
                {
                    if (!IsOnPDS)
                        return false;
                    var path = WorkspaceWithoutVolume;
                    return path.StartsWith(@"\Trash\", StringComparison.OrdinalIgnoreCase) ||
                        path.StartsWith(@"\Extras\Trash\", StringComparison.OrdinalIgnoreCase) ||
                        path.StartsWith(@"\Extras2\Trash\", StringComparison.OrdinalIgnoreCase);
                }
            }

            public bool IsInArchive
            {
                get
                {
                    if (!IsOnPDS)
                        return false;
                    var path = WorkspaceWithoutVolume;
                    return path.StartsWith(@"\Archive\", StringComparison.OrdinalIgnoreCase) ||
                        path.StartsWith(@"\Extras\Archive\", StringComparison.OrdinalIgnoreCase) ||
                        path.StartsWith(@"\Extras2\Archive\", StringComparison.OrdinalIgnoreCase);
                }
            }

        }

        struct PartialGisDataset
        {
            public PartialGisDataset(string workspacePath, string workspaceProgID=null, string datasourceName=null, esriDatasetType? datasourceType=null)
            {
                if (string.IsNullOrWhiteSpace(workspacePath))
                    throw new ArgumentException("Initial value must not be null, empty or whitespace", nameof(workspacePath));
                WorkspacePath = workspacePath;
                WorkspaceProgID = string.IsNullOrWhiteSpace(workspaceProgID) ? null : workspaceProgID;
                DatasourceName = string.IsNullOrWhiteSpace(datasourceName) ? null : datasourceName;
                DatasourceType = datasourceType;
            }

            public string WorkspacePath { get; }
            public string WorkspaceProgID { get; }
            public string DatasourceName { get; }
            public esriDatasetType? DatasourceType { get; }

            public GisDataset ToGisDataset(GisDataset gisDataset)
            {
                return new GisDataset(
                    WorkspacePath,
                    WorkspaceProgID ?? gisDataset.WorkspaceProgID,
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
        /// NewDataset | replacement | layerfile | Comments
        /// not-null   | not-null    | not-null  | Not supported
        /// not-null   | not-null    | null      | Not supported
        /// not-null   | null        | not-null  | Prompt user to select choice
        /// not-null   | null        | null      | Typical case; Easy fix; no prompt
        /// null       | not-null    | not-null  | Not supported
        /// null       | not-null    | null      | Not supported
        /// null       | null        | not-null  | Easy fix, replace broken layer with new layer (prompt user?)
        /// null       | null        | null      | Not valid unless remarks provided (very unusual to not provide an upgrade option)
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

                var searchString = OldDataset.WorkspacePath;
                int positionOfSearchString = source.WorkspacePath.IndexOf(searchString, StringComparison.OrdinalIgnoreCase);
                if (positionOfSearchString < 0)
                {
                    return null;
                }
                var newWorkspace = source.WorkspacePath.Substring(0, positionOfSearchString) +
                    newDataset.WorkspacePath +
                    source.WorkspacePath.Substring(positionOfSearchString + searchString.Length);

                return new PartialGisDataset(
                    newWorkspace,
                    newDataset.WorkspaceProgID,
                    newDataset.DatasourceName,
                    newDataset.DatasourceType
                );
            }
        }

        private readonly List<Move>  _moves = new List<Move>();

        public Moves(string csvpath)
        {
            char delimeter = '|';
            var fieldCount = 15;
            //This is a very simple CSV parser, as the input is very simple.
            //The constructor is very forgiving on the input.  It ignores any record which isn't valid.  It doesn't throw any exceptions
            //It may contain an empty list of moves, which will is dealt with appropriately
            //The csv file used for input should be validated whenever it is edited.
            //Validation rules:
            //   Each row requires a timestamp, and the timestamp must be ordered from oldest to newest
            //   Workspace paths must not have volume information
            //   Replacement datasets are not supported - use replacement layer
            //   New and old datasets must not differ in workspace type or dataset type - use replacement layer
            //   If newDataset is null (i.e old is deleted), trash or archive, then a replacement layerfile should be provided.
            //      A remark is all that is mandatory when newDataset is null.
            //   Column 2 and 6 must be progID strings
            //   Columns 4 and 8must be datasetTypes

            //TODO: Add a boolean 'check' parameter, which will print the warning comments below
            try
            {
                int lineNum = 0;
                DateTime previousTimestamp = DateTime.MinValue;
                foreach (string line in File.ReadLines(csvpath))
                {
                    lineNum += 1;
                    var row = line.Split(delimeter);
                    if (row.Length != fieldCount)
                    {
                        continue;
                        //Warning: Wrong number of columns at line linNum; Skipping.
                    }

                    DateTime timestamp;
                    if (!DateTime.TryParse(row[0], out timestamp))
                    {
                        continue;
                        //Warning: First column at line linNum is not a DateTime; Skipping.
                    }
                    if (timestamp < previousTimestamp)
                    {
                        continue;
                        //Warning: Timestamp in column 1 must be increasing. Skipping line linNum for being out of order.
                    }
                    previousTimestamp = timestamp;

                    if (string.IsNullOrWhiteSpace(row[1]))
                    {
                        continue;
                        //Warning: Old Workspace Path (column 2) not provided at line lineNum; Skipping.
                    } else
                    {
                        //TODO: Verify row[1] does not start with a UNC or drive letter (no volume information)
                    }
                    esriDatasetType? dataSourceType = null;
                    esriDatasetType tempDataSourceType;
                    if (Enum.TryParse(row[4], out tempDataSourceType))
                    {
                        dataSourceType = tempDataSourceType;
                    }
                    if (dataSourceType == null && !string.IsNullOrWhiteSpace(row[4]))
                    {
                        //Warning: esriDatasetType provided at column 5 line lineNum is not valid; Using null
                    }
                    //TODO: Check that row[2] is a progID strings (https://desktop.arcgis.com/en/arcobjects/latest/net/webframe.htm#IWorkspaceName_WorkspaceFactoryProgID.htm)
                    var oldDataset = new PartialGisDataset(row[1], row[2], row[3], dataSourceType);

                    PartialGisDataset? newDataset = null;
                    if (!string.IsNullOrWhiteSpace(row[5]))
                    {
                        //TODO: Verify row[5] does not start with a UNC or drive letter (no volume information)
                        dataSourceType = null;
                        if (Enum.TryParse(row[8], out tempDataSourceType))
                        {
                            dataSourceType = tempDataSourceType;
                        }
                        if (dataSourceType == null && !string.IsNullOrWhiteSpace(row[8]))
                        {
                            //Warning: esriDatasetType provided at column 9 line lineNum is not valid; Using null
                        }
                        if ((row[6] != null && row[2] != row[6]) || (row[8] != null && row[4] != row[8]))
                        {
                            //Warning: You can't change the workspace or dataset types on line lineNum; Ignoring new values. Use a replacement layerfile instead
                            row[6] = null;
                            dataSourceType = null;
                        }
                        // We do not need to check that row[6] is a progID, because it must be null or the same as row[2]
                        newDataset = new PartialGisDataset(row[5], row[6], row[7], dataSourceType);
                    }

                    if (!string.IsNullOrWhiteSpace(row[9]))
                    {
                        // Warning: Replacement datasets are not supported (Column 10, line lineNum); Ignoring. Use a replacement layerfile instead
                    }
                    var layerFile = string.IsNullOrWhiteSpace(row[13]) ? null : row[13].Trim();
                    //TODO: verify that non-null layerFile is a valid file system object (ending in '.lyr')

                    var remarks = string.IsNullOrWhiteSpace(row[14]) ? null : row[14].Trim();
                    if (newDataset == null && layerFile == null && remarks == null)
                    {
                        continue;
                        //Warning: line lineNum is invalid. It must have a newdataset or a layerfile, or a remark
                    }
                    //TODO: if newDataset is null (deleted), trash or archive, then replacement layer must be provided.

                    _moves.Add(new Move(timestamp, oldDataset, newDataset, null, layerFile, remarks));
                }
            }
            catch { }
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
            // !!WARNING!! Assumes workspace paths in moves do not have volume information
            string movePath = moveFrom.WorkspacePath;
            string fullPath = dataset.WorkspaceWithoutVolume;
            if (moveFrom.WorkspaceProgID != null && moveFrom.WorkspaceProgID == dataset.WorkspaceProgID)
                return false;
            return string.Compare(fullPath, movePath, StringComparison.OrdinalIgnoreCase) == 0;
        }

        private bool IsPartialWorkspaceMatch(GisDataset dataset, PartialGisDataset moveFrom)
        {
            // !!WARNING!! Assumes workspace paths in moves do not have volume information
            string movePath = moveFrom.WorkspacePath;
            string fullPath = dataset.WorkspaceWithoutVolume;
            // Just searching for oldPath somewhere in newpath could yield some false positives.
            // Instead, strip the volume and only match the beginning of the string
            return fullPath.StartsWith(movePath, StringComparison.OrdinalIgnoreCase);
        }

        private Move? FindFirstMatchingMove(GisDataset dataset, DateTime since)
        {
            // !!WARNING!! Assumes moves list is in chronological order
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
            // ulimately, the user should not be given the option to use /d/e/f since it doesn't exist.
            // however this gets complicated.  For example
            // At time 1 /a/b/c is moved to the archive and a replcement of /d/e/f is offered
            // at time 2 archive/a/b/c is moved to the trash and replaced by /1/2/3
            // at time 3 /d/e/f is moved to archive and replaced by /4/5/6
            // The user with /a/b/c might want 1/2/3, 4/5/6, archive/d/e/f or trash/a/b/c.  To resolve this
            // The user should be given the choice from time 1, then the choice from time 2 or time 3 depending
            // on the first choice.

            // The timestamp is really not that helpful. It is only useful when doing a second search, and then
            // the moves that are known by date to be not applicable can be skipped.

            // IMPORTANT: the timestamp does not solve this problem:
            // at time 1 dataset /a/b/c is created (creates are not logged in the moves dataset)
            // at time 2 dataaset /a/b/c is moved to /d/e/f (and logged)
            // at time 3 a new dataset /a/b/c is created (not logged)
            // at time 4 new dsataset /a/b/c is moved to /g/h/i (logged)
            // GetSolution will always return the move at time 2 when first checking /a/b/c.
            // GetSolution could correctly return the move at time4 if given a start time after time 2.
            // However, we do not know if the map added data /a/b/c before time 2 or after time 3.
            // The date a layer is added is not stored in the map document.
            // We will try to discourage this kind of renaming situation.

            if (!oldDataset.IsOnPDS)
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
