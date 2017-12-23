using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace MapFixer
{
    
    class Moves
    {
        public struct GisDataset : IEquatable<GisDataset>
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
                if (WorkspacePath == other.WorkspacePath && WorkspaceType == other.WorkspaceType && DatasourceName == other.DatasourceName && DatasourceType == other.DatasourceType)
                    return true;
                else
                    return false;
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
            public Solution(GisDataset? newDataset = null, GisDataset? replacementDataset = null, string replacementLayerFilePath = null, string remarks = null)
            {
                if (newDataset == null && replacementDataset == null && string.IsNullOrWhiteSpace(replacementLayerFilePath) && string.IsNullOrWhiteSpace(remarks))
                    throw new NotSupportedException("At least one of the parameters must be non-null");
                NewDataset = newDataset;
                ReplacementDataset = replacementDataset;
                ReplacementLayerFilePath = string.IsNullOrWhiteSpace(replacementLayerFilePath) ? null : replacementLayerFilePath;
                Remarks = string.IsNullOrWhiteSpace(remarks) ? null : remarks;
            }

            public GisDataset? NewDataset { get; }
            public GisDataset? ReplacementDataset { get; }
            public string ReplacementLayerFilePath { get; }
            public string Remarks { get; }
        }

        struct Move
        {
            public Move(DateTime timestamp, PartialGisDataset oldDataset, PartialGisDataset? newDataset, 
                PartialGisDataset? replacementDataset =null, string replacementLayerFilePath = null,
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

                    _moves.Add(new Move(timestamp, oldDataset, newDataset, replacementDataset, remarks));
                }
            }
            catch { }
        }

        private List<Move> GetMoves(DateTime since, GisDataset startingDataset)
        {
            var moves = new List<Move>();
            //FIXME: Implement
            return moves;
        }

        private PartialGisDataset? GetLastNewDataset(List<Move> moves)
        {
            PartialGisDataset? lastDataset = null;
            foreach (Move move in moves)
                if (move.NewDataset != null)
                    lastDataset = move.NewDataset;
            return lastDataset;
        }

        private PartialGisDataset? GetLastReplacementDataset(List<Move> moves)
        {
            PartialGisDataset? lastDataset = null;
            foreach (Move move in moves)
                if (move.ReplacementDataset != null)
                    lastDataset = move.ReplacementDataset;
            return lastDataset;
        }

        private string GetLastLayerFilePath(List<Move> moves)
        {
            string lastLayer = null;
            foreach (Move move in moves)
                if (move.ReplacementLayerFilePath != null)
                    lastLayer = move.ReplacementLayerFilePath;
            return lastLayer;
        }

        private string GetLastRemarks(List<Move> moves)
        {
            string lastRemark = null;
            foreach (Move move in moves)
                if (move.Remarks != null)
                    lastRemark = move.Remarks;
            return lastRemark;
        }

        public Solution? GetSolution(GisDataset oldDataset, DateTime since = default(DateTime))
        {
            // default for since is the earliest possible DateTime, which will consider all moves in the database
            var moves = GetMoves(since, oldDataset);
            if (moves.Count == 0)
                return null;
            var newDataset = GetLastNewDataset(moves);
            var replacementDataset = GetLastReplacementDataset(moves);
            var layerFile = GetLastLayerFilePath(moves);
            var remarks = GetLastRemarks(moves);
            if (newDataset == null && replacementDataset == null && layerFile == null && remarks == null)
                return null;
            return new Solution(newDataset?.ToGisDataset(oldDataset), replacementDataset?.ToGisDataset(oldDataset), layerFile, remarks);
        }
    }
}
