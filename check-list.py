from __future__ import absolute_import, division, print_function, unicode_literals
from io import open  # for python2/3 compatibility

import csv


def check_unique_sources(data):
    """
    All the text in the first column (source folders) must have a unique prefix.
    i.e.  images/dena is invalid if images/dena/ikonos is defined
    :param data: an iterable of lists
    :return: invalid source locations
    """
    # build a sorted list of (normalized) sources
    sources = [row[0].upper() for row in data]
    sources.sort()
    # shorter strings are listed first
    # for each item, I only need to check the next item in the list (do not check the last item)
    invalid = []
    for index, value in enumerate(sources[:-1]):
        if sources[index+1].startswith(value):
            invalid.append(value)
    # output to console
    problems = invalid
    if 0 < len(problems):
        print("{0} source prefixes are not unique".format(len(problems)))
        for problem in problems:
            print(problem)


def check_unusual(data):
    substitutions = [('ALBERS', 'AKR'), ('STATEWID', 'STATEWIDE')]
    for row in data:
        old = row[0].upper()
        new = row[1].upper()
        ext = row[2].upper()
        if new and ext:
            print("ERROR: multiple destinations old:{0}, new:{1}, ext:{2}".format(old, new, ext))
        else:
            match = False
            if new:
                if old == new:
                    continue
                for (s, r) in substitutions:
                    if old.replace(s, r) == new:
                        match = True
                        break
                if not match:
                    print("Moving old:{0} to new:{1}".format(old, new))
            if ext:
                if old == ext:
                    continue
                for (s, r) in substitutions:
                    if old.replace(s, r) == ext:
                        match = True
                        break
                if not match:
                    print("Moving old:{0} to ext:{1}".format(old, ext))


def main():
    filepath = r'data/reorg.csv'
    with open(filepath, 'r') as fh:
        # ignore the first record (header)
        fh.readline()
        data = csv.reader(fh)
        # check_unique_sources(data)
        check_unusual(data)


if __name__ == '__main__':
    main()
