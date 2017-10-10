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


def main():
    filepath = r'data/reorg.csv'
    with open(filepath, 'r') as fh:
        # ignore the first record (header)
        fh.readline()
        data = csv.reader(fh)
        check_unique_sources(data)


if __name__ == '__main__':
    main()
