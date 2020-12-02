# from __future__ import absolute_import, division, print_function, unicode_literals
import os
import arcpy


def fix_file(path):
    doc = arcpy.mapping.Layer(path)
    broken_layers = arcpy.mapping.ListBrokenDataSources(doc)
    if not broken_layers:
        print('  OK: ' + path)
    else:
        for layer in broken_layers:
            print('  *** BROKEN: ' + path+ ' -> ' + layer.workspacePath + ' + ' + layer.datasetName)

def find_and_fix_all_in_folder(start):
    for root, _, files in os.walk(start):
        for name in files:
            if os.path.splitext(name)[1].lower() == '.lyr':
                old_path = os.path.join(root, name)
                fix_file(old_path)

root1 = r'X:\GIS\ThemeMgr\WRST Themes'
root2 = os.path.join(root1, 'Basemap')
root3 = os.path.join(root2, 'Image Map')
filepath = os.path.join(root3, 'WRST Satellite Image Map Annotation 250K.lyr')
print('Check File: Always gets check right.')
# commented in or out, makes no difference, last check give wrong results
fix_file(filepath)

print('Check parent folder: Always gets check right.')
# commented in or out, makes no difference, last check give wrong results
find_and_fix_all_in_folder(root3)

print('Check grandparent folder: Always gets check right (one other broken layer found).')
# ****
# **** uncomment and it parent check works correctly
# **** comment out and the check on the parent folder fails
# ****
find_and_fix_all_in_folder(root2)

print('Check great-grandparent folder, Always fails, unless basemap folder checked first')
# This will print erroneous results for WRST Satellite Image Map Annotation 250K.lyr
# unless the search is done at the child folder first, but not two children down
find_and_fix_all_in_folder(root1)

