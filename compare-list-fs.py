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
import filecmp

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
    for file_num in files:
        root, map_path, hash_path = files[file_num]
        if map_path is not None:
            with open(map_path, 'rb') as fh:
                # ignore the first record (header)
                fh.readline()
                line_num = 1
                for row in csv.reader(fh):
                    line_num += 1
                    unicode_row = [unicode(item, 'utf-8') if item else None for item in row]
                    mappings[(file_num, line_num)] = tuple(unicode_row)
        if hash_path is not None:
            with open(hash_path, 'rb') as fh:
                # ignore the first record (header)
                fh.readline()
                for row in csv.reader(fh):
                    path = os.path.join(unicode(row[0], 'utf-8'), unicode(row[1], 'utf-8'))
                    file_hash[(file_num, path)] = row[2]
    if len(mappings) == 0:
        mappings = None
    if len(file_hash) == 0:
        file_hash = None
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
    for key in files:
        root = files[key][0]
        trees[root] = {}
    dest_root = files[1][0]
    for key in mappings:
        file_num, line_num = key
        old_path, int_path, ext_path = mappings[key][:3]
        if ext_path is None:
            ext_path = mappings[key][3]
        old_root, _, _ = files[file_num]
        trees[old_root][old_path] = (file_num, line_num)
        # if there is an internal and external destination, it will be flagged later
        if int_path is not None:
            trees[dest_root][int_path] = (file_num, line_num)
        if ext_path is not None:
            trees[dest_root][ext_path] = (file_num, line_num)
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
    items = [os.path.join(root, item) for item in paths if item]
    found, extra = search(root, items)
    missing = list(set(items).difference(set(found)))
    missing = [m.replace(root + os.path.sep, '') for m in missing]
    extra = [e.replace(root + os.path.sep, '') for e in extra]
    for item in missing:
        file_num, line_num = paths[item]
        errors.append((file_num, line_num, "'{}' was not found on the disk.".format(item)))
    line_num = -1  # extra errors do not have a line number, but they are in the same filesystem
    try:
        file_num, _ = paths[paths.keys()[0]]
    except IndexError:
        file_num = -1
    for item in extra:
        errors.append((file_num, line_num, "'{}' was found on the disk, but not listed.".format(item)))
    return errors


def make_maps(mappings, files):
    """
    Simplifies the mappings by creating a map from each source to a destination

    If there are duplicates in the list of sources, then the results are undefined.

    :param mappings: dict {(file#,line#):("old_path","int_path","ext_path",...)}
    :param files: dict {file#: ("root", "map_path", "hash_path")}
    :return: (errors list, maps dict)
    errors  list [(file#, line#, "Issue")]
    maps dict: {"old_path": ("new_path",file#,line#)}
    """
    errors = []
    maps = {}
    for key in mappings:
        file_num, line_num = key
        old_path, int_path, ext_path, ext2_path, status = mappings[key][:5]
        if ext_path is None:
            ext_path = ext2_path
        else:
            if ext2_path is not None:
                errors.append((file_num, line_num, "Line has two external destination"))
        if int_path is not None and ext_path is not None:
            errors.append((file_num, line_num, "Line has both an internal and external destination"))
            continue
        new_path = int_path if ext_path is None else ext_path
        if old_path is None and new_path is None:
            errors.append((file_num, line_num, "Line has both no source or destination"))
            continue
        if old_path is not None and new_path is None and status != 'trash':
            errors.append((file_num, line_num, "Source '{}' has no destination".format(old_path)))
            continue
        # ignore old_path is None and new_path is not None (new file on destination is ok
        if old_path is not None and new_path is not None:
            old = os.path.join(files[file_num][0], old_path)
            new = os.path.join(files[1][0], new_path)
            maps[old] = (new, file_num, line_num)
    return errors, maps


def find_dups(mappings):
    """
    Searches the mappings for any duplicates in the source or destination paths

    An error is created for each line that is not unique.

    :param mappings: dict {(file#,line#):("old_path","int_path","ext_path",...)}
    :return: errors list [(file#, line#, "Issue")]
    """
    errors = []
    seen_sources = set()
    seen_destinations = set()
    src_dups = set()
    dest_dups = set()

    for mapping in mappings.values():
        source = mapping[0]
        if source is None:
            continue
        if source not in seen_sources:
            seen_sources.add(source)
        else:
            src_dups.add(source)

    for mapping in mappings.values():
        old_path, int_path, ext_path, ext2_path, status = mapping[:5]
        destination = int_path if int_path is not None else ext_path
        if destination is None:
            destination = ext2_path
        if destination is None:
            continue
        if status == 'duplicate' or status == 'similar':
            continue
        if destination not in seen_destinations:
            seen_destinations.add(destination)
        else:
            dest_dups.add(destination)

    for key in mappings:
        src, dest1, dest2, dest3 = mappings[key][:4]
        if src in src_dups:
            file_num, line_num = key
            errors.append((file_num, line_num, "Source '{0}' is a duplicate".format(src)))
        if dest1 in dest_dups:
            file_num, line_num = key
            errors.append((file_num, line_num, "Destination '{0}' is a duplicate".format(dest1)))
        if dest2 in dest_dups:
            file_num, line_num = key
            errors.append((file_num, line_num, "Destination '{0}' is a duplicate".format(dest2)))
        if dest3 in dest_dups:
            file_num, line_num = key
            errors.append((file_num, line_num, "Destination '{0}' is a duplicate".format(dest3)))

    return errors


def check_equivalence(maps, mappings, file_hash=None):
    """
    Checks if the source and destination in the map are equivalent

    The source/destination is a path to a file or a folder (source and destination must be the same type)
    Equivalence can be checked quickly (file_hash == None), by comparing the file count, and total byte count
    If file_hash is not None, then equivalence is check by looking up the precomputed hash value for both files
    if the source/destination are directories, then the file system is querried for all files contained within and
    all files are compared for equivalence by matching thier precomputed hash valies in file_hash.

    :param mappings: dict {(file#,line#):("old_path","int_path","ext_path",...)}
    :param maps: dict {"old_path": ("new_path",file#,line#)}
    :param file_hash: {(file#, "path"): hash}
    :return: errors list [(file#, line#, "Issue")]
    """
    errors = []
    if file_hash is None:
        for old_path in maps:
            new_path, file_num, line_num = maps[old_path]
            # print("{0}, {1}".format(old_path, new_path))
            if new_path.endswith('SDMI_IFSAR'):
                print("***  Skipping {} == {}".format(old_path, new_path))
            elif new_path.endswith('SDMI_SPOT'):
                print("***  Skipping {} == {}".format(old_path, new_path))
            elif new_path.startswith('Source_Data\\'):
                print("***  Skipping {} == {}".format(old_path, new_path))
            elif not paths_equal(old_path, new_path):
                # print("*************  Folders not equal ****************")
                status = mappings[(file_num, line_num)][4]
                if status != 'similar':
                    errors.append((file_num, line_num, "Folders not equal: {0} <> {1}".format(old_path, new_path)))
    else:
        for old_path in maps:
            new_path, file_num, line_num = maps[old_path]
            try:
                match = file_hash[(file_num, old_path)] == file_hash[(1, new_path)]
            except KeyError:
                match = False
            if not match:
                errors.append((file_num, line_num, "Folders not equal: {0} <> {1}".format(old_path, new_path)))
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
    errors.sort()
    if file_path is None:
        for file_num, line_num, issue in errors:
            if files is not None:
                root = files[file_num][0]
            else:
                root = file_num
            print('{0}, {1}, {2}'.format(root, line_num, issue))
    else:
        with open(file_path, 'wb') as fh:
            writer = csv.writer(fh)
            writer.writerow(['file', 'line', 'issue'])
            for file_num, line_num, issue in errors:
                if files is not None:
                    root = files[file_num]
                else:
                    root = file_num
                writer.writerow([root, line_num, issue])


def paths_equal(path1, path2):
    """
    Test if two files are 'equal'

    files are equal if they have the same os_stat() values
    :param path1: path to a file
    :param path2: path to another file
    :return: bool
    """
    if path1 == path2:
        return True
    if os.path.isfile(path1) and os.path.isfile(path2):
        return files_equal(path1, path2)
    if os.path.isdir(path1) and os.path.isdir(path2):
        return folders_equal(path1, path2)
    return False


def files_equal(path1, path2):
    """
    Test if two files are 'equal'

    files are equal if they have the same os_stat() values 
    :param path1: path to a file
    :param path2: path to another file
    :return: bool
    """
    return filecmp.cmp(path1, path2)


def folders_equal(path1, path2):
    """
    Test if two folders are 'equal'

    folders all the files in each folder are equal. Each folder must have the same number of files and all
    sub folders must also be equal.  Assumes that the files and folders have the same names (actually that
    the order provided by os.walk() is the same
    :param path1: path to a folder
    :param path2: path to another folder
    :return: bool
    """
    compared = filecmp.dircmp(path1, path2)
    if 0 < len(compared.left_only):
        return False
    if 0 < len(compared.right_only):
        return False
    if 0 < len(compared.funny_files):
        return False
    if 0 < len(compared.common_funny):
        return False
    if 0 < len(compared.diff_files):
        return False
    for subdir in compared.common_dirs:
        if not folders_equal(os.path.join(path1, subdir), os.path.join(path2, subdir)):
            return False
    return True


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


def test_equivalence():
    test_map = {
        r'\\inpakrovmdist\gisdata\AHAP':
            (r'\\inpakrovmdist\gisdata\AHAP', 2, 1),
        r'\\inpakrovmdist\gisdata\AHAP\ANIA':
            (r'\\inpakrovmdist\gisdata2\Extras\ANIA\AHAP', 2, 2),
        r'\\inpakrovmdist\gisdata\AHAP\BELA':
            (r'\\inpakrovmdist\gisdata2\Extras\CAKR\AHAP', 2, 3),
        r'\\inpakrovmdist\gisdata\OrthoBase\ANCH/UA_ANCH.mdb':
            (r'\\inpakrovmdist\gisdata2\Extras\Anchorage\Imagery/UA_ANCH.mdb', 2, 4),
        r'\\inpakrovmdist\gisdata\Albers\base\Anno_GDB':
            (r'\\inpakrovmdist\gisdata2\akr\Statewide\anno', 2, 5),
    }
    errors = check_equivalence(test_map, None)
    print_errors(errors, None)


def main():
    errors = []
    # file_info = {file#: ("root", "map_path", "hash_path")}
    file_info = {
        1: (r'\\inpakrovmdist\gisdata2', None, None),  # r'data/int_hash'),  # Destination: column 2/3 of the map files
        2: (r'\\inpakrovmdist\gisdata', r'data\PDS Moves - inpakrovmdist%5Cgisdata.csv', None),  # r'data/dist_hash'),
        3: (r'\\inpakrovmais\data', r'data\PDS Moves - inpakrovmais%5Cdata.csv', None),  # r'data/ais_hash')
    }
    mappings, file_hashes = read_csv(file_info)
    trees = get_paths(mappings, file_info)
    for root, paths in trees.items():
        errors += compare_list_to_files(root, paths)
    errors += find_dups(mappings)
    errs, maps = make_maps(mappings, file_info)
    errors += errs
    errors += check_equivalence(maps, mappings, file_hashes)
    print_errors(errors, file_info)


def test_specific_folders():
    # print(paths_equal(r'\\inpakrovmdist\gisdata\GIS\ArcGIS10.3.1',
    #                   r'\\inpakrovmdist\gisdata2\Extras\Software\ArcGIS 10.3.1'))
    # for name in os.listdir(r'\\inpakrovmdist\gisdata\GIS\ThemeMgr\Alaska-wide - Multi Park Themes'):
    for name in ['GIS\ThemeMgr']:
        print(name, paths_equal(os.path.join(r'\\inpakrovmdist\gisdata', name),
                                os.path.join(r'\\inpakrovmdist\gisdata2', name)))


if __name__ == '__main__':
    # test_csv()
    # test_equivalence()
    # test_specific_folders()
    main()
