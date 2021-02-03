# -*- coding: utf-8 -*-
"""
Replaces old data source paths with new paths in a Theme Manager database (*.tml)
"""

from __future__ import absolute_import, division, print_function, unicode_literals

from io import open

import fix_file


def read(path):
    """Read the file as one giant string."""
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def save(data, path):
    """data is the entire contents of the file as one big string."""
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(data)


def read_paths(path):
    old_paths = []
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            old_paths.append(line.strip())
    return old_paths


def build_file_mapping(in_path, all_paths):
    old_paths = read_paths(in_path)
    moves = fix_file.read_csv_map(all_paths)
    results = []
    for old_path in old_paths:
        new_path = fix_file.find_replacement(old_path, moves)
        print(old_path, new_path)
        if new_path is not None and new_path != old_path:
            results.append((old_path, new_path))
    return results


def main():
    tml = read(
        r"c:\tmp\xxx\AKR Theme List.tml"
    )  # r"X:\GIS\ThemeMgr\AKR Theme List.tml")
    path_maps = build_file_mapping(
        "data/tmpaths.txt", "data/moves_extra.csv"
    )  # data/PDS Moves - inpakrovmdist%5Cgisdata.csv')
    for old, new in path_maps:
        print(old, new)
        tml = tml.replace(old, new)
    save(
        tml, r"c:\tmp\xxx\AKR Theme List1.tml"
    )  # r"X:\GIS\ThemeMgr\AKR Theme List.tml"))


if __name__ == "__main__":
    main()
