"""
Print out the folder tree to a specified depth
"""

from __future__ import absolute_import, division, print_function, unicode_literals
import os


def print_dirs(start='.', depth=0, max_depth=3, leader='\t'):
    #  Can't use os.walk as it is a breadth first search,
    #  and I need a depth first solution
    if depth < max_depth:
        for folder in next(os.walk(start))[1]:
            print('{}{}'.format(leader * depth, folder))
            new_start = os.path.join(start, folder)
            print_dirs(start=new_start, depth=depth+1, max_depth=max_depth, leader=leader)


if __name__ == '__main__':
    print_dirs(r'\\inpakrovmdist\gisdata2\mosaics', max_depth=2)
