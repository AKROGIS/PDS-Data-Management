# -*- coding: utf-8 -*-
"""
Walk the file system and build a CSV file with a hash for each file
"""

from __future__ import absolute_import, division, print_function, unicode_literals

import csv
import hashlib
from io import open
import os


def sha1_file(path):
    _blocksize_ = 65536
    hasher = hashlib.sha1()
    with open(path, "rb") as afile:
        buf = afile.read(_blocksize_)
        while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(_blocksize_)
    return hasher.hexdigest()


def sha1_folder(directory):
    _blocksize_ = 65536
    hasher = hashlib.sha1()
    if not os.path.exists(directory):
        return -1
    try:
        for root, dirs, files in os.walk(directory):
            for name in files:
                # print 'Hashing', name
                path = os.path.join(root, name)
                with open(path, "rb") as afile:
                    buf = afile.read(_blocksize_)
                    while len(buf) > 0:
                        hasher.update(buf)
                        buf = afile.read(_blocksize_)
    except Exception as ex:
        print(ex)
        return -2
    return hasher.hexdigest()


def get_file_hashes(start):
    hash_list = []
    try:
        for root, folders, files in os.walk(start):
            gdbs = [d for d in folders if d.upper().endswith(".GDB")]
            for gdb in gdbs:
                path = os.path.join(root, gdb)
                print("hashing " + path)
                try:
                    sha1 = sha1_folder(path)
                except Exception as ex:
                    print(ex)
                    sha1 = -1
                # print([root, name, sha1])
                hash_list.append([root, gdb, sha1])
                folders.remove(gdb)
            for name in files:
                path = os.path.join(root, name)
                print("hashing " + path)
                try:
                    sha1 = sha1_file(path)
                except Exception as ex:
                    print(ex)
                    sha1 = -1
                # print([root, name, sha1])
                hash_list.append([root, name, sha1])
    except Exception as ex:
        print(ex)
    return hash_list


def write_folder_to_file(folder, csv_file):
    hashlist = get_file_hashes(folder)
    mode = "wb"  # 'w' for python 3; 'wb' for python 2
    with open(csv_file, mode) as fh:
        writer = csv.writer(fh)
        writer.writerow(["path", "name", "hash"])
        for row in hashlist:
            writer.writerow(row)


if __name__ == "__main__":
    # print(sha1_file(r'data\reorg.csv'))
    write_folder_to_file(r"data\test", r"data\ais_hash.csv")
