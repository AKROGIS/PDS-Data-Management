"""
Compare the file move list with the file system

This testing has many aspects
1) ensure that the list of source items is complete
   - find items in list that are not in file system
   - find items in filesystem that are not covered by the list (not a folder covers everything within it)
2) ensure that the lists of destination items (both internal and external) are complete
   - find items in list that are not in file system
   - find items in filesystem that are not covered by the list (not a folder covers everything within it)
3) ensure that there are no duplicates in the source list or each destination list
4) ensure that each source has one and only one mapping to an internal or external destination
5) ensure that where there is a one to one match, that the contents are the same
   - sameness can be checked by file count/size for a quick first check
   - sameness can only be guaranteed if the files have the same hash
"""

from __future__ import absolute_import, division, print_function, unicode_literals
from io import open  # for python2/3 compatibility
import csv
import os

"""
# configuration constants
int_root = ''
ext_root = ''
files = {file#: ("root", "map_path", "hash_path")}

# types
errors = [(file#, line#, "Issue")]
mappings = {(file#,line#): ("old_path", "int_path", "ext_path",...)}
file_hash = {(file#, "path"): hash} 
hash_file = {hash:[(file#, "path")]}
trees = {"root": paths dict}
paths = {"path": (file#,line#)}
maps = {"old_path": ("new_path",file#,line#)}
"""


def read_csv(files):
    """
    Read a group of CSV properly formated CSV files and create the program data structures

    :param files: dict {file#: ("root", "map_path", "hash_path")}
    :return: (mappings dict, file_hash dict)
    mappings dict: {(file#,line#): ("old_path", "int_path", "ext_path",...)}
    file_hash dict: {(file#, "path"): hash}
    """
    mappings = {}
    file_hash = {}
    return mappings, file_hash


def get_paths(mappings, files):
    """
    Simplifies the mappings by returning a collection of paths for each root in files

    The int paths are at index 1 in the mapping tuple
    The ext paths are at index 2 in the mapping tuple
    The int paths are always file #1 and the ext paths are file #2
    :param mappings: dict {(file#,line#):("old_path","int_path","ext_path",...)}
    :param files: dict {file#: ("root", "map_path", "hash_path")}
    :return: trees dict {"root": paths dict}
    paths dict: {path:(file#,line#)}
    """
    trees = {}
    return trees


def compare_list_to_files(root, paths):
    """
    Compares the list of paths to the file system at root, returning an errors

    An error is returned for each extra (path in fs is not found in paths) and
    missing (path in paths is not found in fs).

    :param root: string, the prefix to add to all paths in the files dict
    :param paths: dict {path:(file#,line#)}
    :return: errors list [(file#, line#, "Issue")]
    """
    errors = []
    items = [os.path.join(root, item) for item in paths]
    found, extra = search(root, items)
    missing = list(set(items).difference(set(found)))
    missing = [m.replace(root + os.path.sep, '') for m in missing]
    extra = [e.replace(root + os.path.sep, '') for e in extra]
    for item in missing:
        file_num, line_num = paths[item]
        errors.append((file_num, line_num, "`{}` was not found on the disk.".format(item)))
    line_num = -1  # extra errors do not have a line number, but they are in the same filesystem
    try:
        file_num, _ = paths[paths.keys()[0]]
    except IndexError:
        file_num = -1
    for item in extra:
        errors.append((file_num, line_num, "`{}` was found on the disk, but not listed.".format(item)))
    return errors


def make_maps(mappings):
    """
    Simplifies the mappings by creating a map from each source to a destination

    If there are duplicates in the list of sources, then the results are undefined.

    :param mappings: dict {(file#,line#):("old_path","int_path","ext_path",...)}
    :return: (errors list, maps dict)
    errors  list [(file#, line#, "Issue")]
    maps dict: {"old_path": ("new_path",file#,line#)}
    """
    errors = []
    maps = {}
    return errors, maps


def find_dups(mappings):
    """
    Searches the mappings for any duplicates in the source or destination paths

    An error is created for each line that is not unique.

    :param mappings: dict {(file#,line#):("old_path","int_path","ext_path",...)}
    :return: errors list [(file#, line#, "Issue")]
    """
    errors = []
    return errors


def check_equivalence(maps, file_hash=None):
    """
    Checks if the source and destination in the map are equivalent

    The source/destination is a path to a file or a folder (source and destination must be the same type)
    Equivalence can be checked quickly (file_hash == None), by comparing the file count, and total byte count
    If file_hash is not None, then equivalence is check by looking up the precomputed hash value for both files
    if the source/destination are directories, then the file system is querried for all files contained within and
    all files are compared for equivalence by matching thier precomputed hash valies in file_hash.

    :param maps: dict {"old_path": ("new_path",file#,line#)}
    :param file_hash: {(file#, "path"): hash}
    :return: errors list [(file#, line#, "Issue")]
    """
    errors = []
    return errors


def print_errors(errors, files=None, file_path=None):
    """
    Writes a list of errors to a CSV file, or prints to the console

    If files is provided, then the root of the file data is printed, instead of the file number.

    :param errors: list [(file#, line#, "Issue")]
    :param files: dict {file#: ("root", "map_path", "hash_path")}
    :param file_path: string path to location to create a CSV file.  If None, print to console
    :return: None
    """


def known_prefix(path, items):
    for item in items:
        if item.startswith(path + os.path.sep):
            return True
    return False


def search(start, items):
    found = []
    extra = []
    for root, folders, files in os.walk(start):
        # print('walk', root, folders, files)
        for file_ in files:
            path = os.path.join(root, file_)
            # print(path)
            if path in items:
                found.append(path)
            else:
                extra.append(path)
        skip_folders = []
        for folder in folders:
            path = os.path.join(root, folder)
            # print(path)
            if path in items:
                found.append(path)
                skip_folders.append(folder)
            else:
                if not known_prefix(path, items):
                    extra.append(path)
                    skip_folders.append(folder)
        for folder in skip_folders:
            folders.remove(folder)
    return found, extra


def load_csv(filepath, col=0):
    with open(filepath, 'r') as fh:
        # ignore the first record (header)
        fh.readline()
        data = [row[col] for row in csv.reader(fh)]
    return data


def print_issues(root, items):
    new_items = [os.path.join(root, item) for item in items]
    found, extra = search(root, new_items)
    missing = list(set(new_items).difference(set(found)))

    print('found', sorted([f.replace(root + os.path.sep, '') for f in found]))
    print('missing', sorted([m.replace(root + os.path.sep, '') for m in missing]))
    print('extra', sorted([e.replace(root + os.path.sep, '') for e in extra]))


def test():
    test_root = os.path.join('data', 'test')
    test_list = ['a.txt', 'c.txt', r'a\b.txt', r'a\c.txt', 'b', r'd\c', 'e', 'f']  # use OS specific path separator
    # cd $test_root
    # mkdir a; mkdir b; mkdir c; mkdir d; mkdir d/b; mkdir d/c; mkdir e; mkdir e/a; mkdir g; mkdir g/a
    # touch a.txt; touch b.txt; touch a/a.txt; touch  a/b.txt
    #
    # test
    #    - a.txt  (listed/found file)
    #    - b.txt  (unlisted/extra file)
    #     (c.txt is a listed/missing file)
    #    - a  (unlisted dir but a prefix, so not extra)
    #      - a.txt  (unlisted/extra file in dir)
    #      - b.txt  (listed/found file in dir)
    #       (c.txt is a missing file)
    #    - b  (listed/found dir)
    #    - c  (unlisted/extra dir)
    #    - d  (unlisted dir but a prefix, so not extra)
    #      - b  (unlisted/extra dir)
    #      - c  (listed/found dir)
    #    - e (listed/found dir)
    #      - a (content in listed parent skipped, not extra/found/missing)
    #     (f is a listed/missing dir)
    #    - g  (unlisted/extra dir)
    #      - a (content in extra parent skipped, not extra/found/missing)
    #
    # found = [a.txt, a/b.txt, b, d/c, e]
    # missing = [c.txt, a/c.txt, f]
    # extra = [b.txt, a/a.txt, c, d/b, g]
    print_issues(test_root, test_list)


def test_csv():
    root = r'\\inpakrovmais\data'
    items = load_csv('data/ais_map.csv', 0)
    print_issues(root, items)


def main():
    errors = []
    # file_info = {file#: ("root", "map_path", "hash_path")}
    file_info = {
        1: (r'inpakrovmdist\gisdata2', None, r'data/int_hash'),  # column 2 of the map files
        2: (r'inpakrovmdist\gisdata3', None, r'data/ext_hash'),  # column 3 of the map files
        3: (r'inpakrovmdist\gisdata', r'data/dist_map', r'data/dist_hash'),
        4: (r'inpakrovmais\data', r'data/ais_map', r'data/ais_hash')
    }
    mappings, file_hashes = read_csv(file_info)
    trees = get_paths(mappings, file_info)
    for root, paths in trees.items():
        errors += compare_list_to_files(root, paths)
    errors += find_dups(mappings)
    errs, maps = make_maps(mappings)
    errors += errs
    errors += check_equivalence(maps, file_hashes)
    print_errors(errors, file_info)


if __name__ == '__main__':
    # test_csv()
    main()
