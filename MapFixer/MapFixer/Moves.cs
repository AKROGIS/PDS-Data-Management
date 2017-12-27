using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;

namespace MapFixer
{
    
    class Moves
    {
        public struct GisDataset: IEquatable<GisDataset>
        {
            public GisDataset(string workspacePath, string workspaceType, string datasourceName, string datasourceType)
            {
                if (string.IsNullOrWhiteSpace(workspacePath))
                    throw new ArgumentException("Initial value must not be null, empty or whitespace", "workspacePath");
                if (string.IsNullOrWhiteSpace(workspaceType))
                    throw new ArgumentException("Initial value must not be null, empty or whitespace", "workspaceType");
                if (string.IsNullOrWhiteSpace(datasourceName))
                    throw new ArgumentException("Initial value must not be null, empty or whitespace", "datasourceName");
                if (string.IsNullOrWhiteSpace(datasourceType))
                    throw new ArgumentException("Initial value must not be null, empty or whitespace", "datasourceType");
                WorkspacePath = workspacePath;
                WorkspaceType = workspaceType;
                DatasourceName = datasourceName;
                DatasourceType = datasourceType;
            }

            public string WorkspacePath { get; }
            public string WorkspaceType { get; }
            public string DatasourceName { get; }
            public string DatasourceType { get; }

            public bool Equals(GisDataset other)
            {
                return WorkspacePath == other.WorkspacePath && WorkspaceType == other.WorkspaceType &&
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

            public string WorkspaceWithoutVolume
            {
                get
                {
                    return WorkspacePath.Substring(Path.GetPathRoot(WorkspacePath).Length);
                }
            }

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
            public PartialGisDataset(string workspacePath, string workspaceType=null, string datasourceName=null, string datasourceType=null)
            {
                if (string.IsNullOrWhiteSpace(workspacePath))
                    throw new ArgumentException("Initial value must not be null, empty or whitespace", "workspacePath");
                WorkspacePath = workspacePath;
                WorkspaceType = workspaceType;
                DatasourceName = datasourceName;
                DatasourceType = datasourceType;
            }

            public string WorkspacePath { get; }
            public string WorkspaceType { get; }
            public string DatasourceName { get; }
            public string DatasourceType { get; }

            public GisDataset ToGisDataset(GisDataset gisDataset)
            {
                return new GisDataset(
                    WorkspacePath,
                    WorkspaceType ?? gisDataset.WorkspaceType,
                    DatasourceName ?? gisDataset.DatasourceType,
                    DatasourceType ?? gisDataset.DatasourceType
                );
            }
        }

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

            public DateTime Timestamp { get; }
            public GisDataset? NewDataset { get; }
            public GisDataset? ReplacementDataset { get; }
            public string ReplacementLayerFilePath { get; }
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
            public PartialGisDataset? NewDataset { get; }
            public PartialGisDataset? ReplacementDataset { get; }
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
                int positionOfSearchString = source.WorkspacePath.IndexOf(searchString);
                if (positionOfSearchString < 0)
                {
                    return null;
                }
                var newWorkspace = source.WorkspacePath.Substring(0, positionOfSearchString) +
                    newDataset.WorkspacePath +
                    source.WorkspacePath.Substring(positionOfSearchString + searchString.Length);

                return new PartialGisDataset(
                    newWorkspace,
                    newDataset.WorkspaceType,
                    newDataset.DatasourceType,
                    newDataset.DatasourceType
                );
            }
        }

        private List<Move>  _moves = new List<Move>();

        public Moves(string csvpath)
        {
            char delimeter = '|';
            var fieldCount = 15;
            //This is a very simple CSV parser, as the input is very simple.
            //The constructor is very forgiving on the input.  It ignores any record which isn't valid.  It doesn't throw any exceptions
            //It may contain an empty list of moves, which will is dealt with appropriately
            //The csv file used for input should be validated whenever it is edited.
            //   do the same parsing below and print exceptions and/or warnings whenever the foreach loop continues (skips a line)
            //   Also need to check for chronological ordering
            //   Also check that workspace paths do not have volume information
            try
            {
                foreach (string line in File.ReadLines(csvpath))
                {
                    var row = line.Split(delimeter);
                    if (row.Count() != fieldCount)
                        continue;
                    DateTime timestamp;
                    if (!DateTime.TryParse(row[0], out timestamp))
                        continue;
                    if (string.IsNullOrWhiteSpace(row[1]))
                        continue;
                    var oldDataset = new PartialGisDataset(row[1], row[2], row[3], row[4]);
                    PartialGisDataset? newDataset = null;
                    if (!string.IsNullOrWhiteSpace(row[5]))
                        newDataset = new PartialGisDataset(row[5], row[6], row[7], row[8]);
                    PartialGisDataset? replacementDataset = null;
                    if (!string.IsNullOrWhiteSpace(row[9]))
                        replacementDataset = new PartialGisDataset(row[9], row[10], row[11], row[12]);
                    var layerFile = string.IsNullOrWhiteSpace(row[13]) ? null : row[13].Trim();
                    var remarks = string.IsNullOrWhiteSpace(row[14]) ? null : row[14].Trim();
                    if (newDataset == null && replacementDataset == null && layerFile == null && remarks == null)
                        continue;

                    _moves.Add(new Move(timestamp, oldDataset, newDataset, replacementDataset, layerFile, remarks));
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
            if (string.Compare(dataset.DatasourceName, moveFrom.DatasourceName, true) != 0)
                return false;
            return IsWorkspaceMatch(dataset, moveFrom);
        }

        private bool IsWorkspaceMatch(GisDataset dataset, PartialGisDataset moveFrom)
        {
            // !!WARNING!! Assumes workspace paths in moves do not have volume information
            string movePath = moveFrom.WorkspacePath;
            string fullPath = dataset.WorkspaceWithoutVolume;
            return string.Compare(fullPath, movePath, StringComparison.OrdinalIgnoreCase) == 0;
        }

        private bool IsPartialWorkspaceMatch(GisDataset dataset, PartialGisDataset moveFrom)
        {
            // !!WARNING!! Assumes workspace paths in moves do not have volume information
            string movePath = moveFrom.WorkspacePath;
            string fullPath = dataset.WorkspaceWithoutVolume;
            // Just searching for oldPath somewhere in newpath could yield some false positives.
            // Instead, strip the volume and only match if the beginning of the string
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
