using System;
using MapFixer;

namespace verifier
{
    class Program
    {
        static void Main(string[] args)
        {
            var dataPath = args.Length > 0 ? args[0] : @"X:\GIS\ThemeMgr\DataMoves.csv";
            Console.WriteLine($"Checking file: {dataPath}");
            var _ = new Moves(dataPath,'|',true);
        }
    }
}
