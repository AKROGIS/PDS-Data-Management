"""
Add helpful attributes to the list of IFSAR tif images
Need to save results with just LF (not CRLF) before importing to SQL Server
"""

from __future__ import absolute_import, division, print_function, unicode_literals
import re
import csv

# must run this from a folder with a data directory

csv_file = 'data/ifsar_tif_new_x.csv'
out_file = 'data/ifsar_tif_new_x_supp.csv'

with open(out_file, 'w') as o:
    csv_writer = csv.writer(o)
    csv_writer.writerow(['folder', 'filename', 'ext', 'size','legacy', 'nga', 'kind','edge','cell','lat','lon'])
    with open(csv_file, 'r') as f:
        f.readline() # remove header
        csv_reader = csv.reader(f)
        for path,name,ext,size in csv_reader:
            n = name.lower()
            d = path.lower()
            legacy = 'N'
            if 'legacy' in d:
                legacy = 'Y'
            nga = 'N'
            if 'nga_30' in d:
                nga = 'Y'
            kind = ''
            if 'ori' in n or ('ori' in d and 'priority' not in d):
                kind = 'ori'
            if kind == 'ori' and '_sup' in n:
                kind = 'ori_sup'
            if 'dsm' in n or 'dsm' in d:
                kind = 'dsm'
            if 'dtm' in n or 'dtm' in d:
                kind = 'dtm'
            edge = 'N'
            if 'edge' in d:
                edge = 'Y'
            cell = ''
            lat,lon = 0,0
            m = re.search(r'\\cell_(\d*)\\', d)
            if m:
                cell = m.group(1)
            m = re.search(r'\\cell_([def])\\', d) # d -> 196, e -> 197, f -> 198
            if m:
                cell = ord(m.group(1)) - ord('d') + 196
            m = re.search(r'_n(\d*)w(\d*)', n)
            if m:
                lat,lon = int(m.group(1))/100,int(m.group(2))/100
            csv_writer.writerow([path,name,ext,size,legacy,nga,kind,edge,cell,lat,lon])
