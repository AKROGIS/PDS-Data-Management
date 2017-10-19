from __future__ import absolute_import, division, print_function, unicode_literals
# from io import open  # for python2/3 compatibility
# import csv
import os

ais_root = "data/ais"
ais_list = ['a', 'c/d', 'd/a/a', 'd/a/c', 'f']
#
# ais
#    - a
#      - a (do not check)
#    - b
#      - b
#    - d
#      - a
#         - a
#         - b
#         - c
#    - e
#
# found = [a, d/a/a, d/a/c]
# missing = [c/d, f]
# extra = [b, d/a/b, e]


extra = []
found = []


def mark_found(path):
    # print('found')
    found.append(path)


def mark_extra(path):
    # print('extra')
    extra.append(path)


def known_prefix(path, items):
    for item in items:
        if item.startswith(path):
            return True
    return False


def search(start, items):
    for root, folders, files in os.walk(start):
        # print('walk', root, folders, files)
        for file_ in files:
            path = os.path.join(root, file_)
            # print(path)
            if path in items:
                mark_found(path)
            else:
                mark_extra(path)
        skip_folders = []
        for folder in folders:
            path = os.path.join(root, folder)
            # print(path)
            if path in items:
                mark_found(path)
                skip_folders.append(folder)
            else:
                if not known_prefix(path, items):
                    mark_extra(path)
                    skip_folders.append(folder)
        for folder in skip_folders:
            folders.remove(folder)


def main(root, items):
    new_items = [os.path.join(ais_root, item) for item in items]
    search(root, new_items)
    missing = list(set(new_items).difference(set(found)))

    # print('original', new_items)
    # print('found', found)
    print('extra', [e.replace(root+'/', '') for e in extra])
    print('missing', [m.replace(root+'/', '') for m in missing])


main(ais_root, ais_list)
