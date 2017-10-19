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
import hashlib


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


def hash_file(path):
    BLOCKSIZE = 65536
    hasher = hashlib.sha1()
    with open(path, 'rb') as afile:
        buf = afile.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(BLOCKSIZE)
    return hasher.hexdigest()


if __name__ == '__main__':
    # test_csv()
    print(hash_file(r'data\reorg.csv'))