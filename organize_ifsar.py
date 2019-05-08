"""
Add helpful attributes to the list of IFSAR tif images
Need to save results with just LF (not CRLF) before importing to SQL Server
"""

from __future__ import absolute_import, division, print_function, unicode_literals
import re
import csv
import os
import glob

# must run this from a folder with a data directory

csv_file = 'data/ifsar_tif_2019c.csv'
out_file = 'data/ifsar_tif_2019c_supp.csv'

with open(out_file, 'wb') as o:
    csv_writer = csv.writer(o)
    csv_writer.writerow(['folder', 'filename', 'ext', 'size', 'legacy', 'nga', 'kind', 'edge',
                         'cell', 'lat', 'lon', 'tfw', 'xml', 'html', 'txt', 'tif_xml', 'ovr',
                         'aux', 'rrd', 'aux_old', 'crc', 'extras', 'skip'])
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
            #
            # Check for supplemental *.html, *.aux.xml, etc files
            #
            f = os.path.join(path,name)
            exts_found = [sup.replace(f, '').lower() for sup in glob.glob(f+'.*')]
            # exts_possible = ['.tif', '.tfw','.xml','.html','.txt','.tif.xml',
            #                  '.tif.ovr','.tif.aux.xml', '.rrd', '.aux', '.tif.crc']
            tfw, xml, html, txt, tif_xml, ovr, aux, rrd, aux_old, crc = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 
            if '.tfw' in exts_found:
                tfw = 1
            if '.xml' in exts_found:
                xml = 1
            if '.html' in exts_found:
                html = 1
            if '.txt' in exts_found:
                txt = 1
            if '.tif.xml' in exts_found:
                tif_xml = 1
            if '.tif.ovr' in exts_found:
                ovr = 1
            if '.tif.aux.xml' in exts_found:
                aux = 1
            if '.rrd' in exts_found:
                rrd = 1
            if '.aux' in exts_found:
                aux_old = 1
            if '.tif.crc' in exts_found:
                crc = 1
            extras = len(exts_found)-1-tfw-xml-html-txt-tif_xml-ovr-aux-rrd-aux_old-crc # 1 for the tif that must exist
            csv_writer.writerow([path, name, ext, size, legacy, nga, kind, edge, cell,
                                 lat, lon, tfw, xml, html, txt, tif_xml, ovr, aux,
                                 rrd, aux_old, crc, extras, 'N'])
