# -*- coding: utf-8 -*-
"""
Add helpful attributes to the list of IFSAR tif images
Need to save results with just LF (not CRLF) before importing to SQL Server
"""

from __future__ import absolute_import, division, print_function, unicode_literals

import csv
import glob
import os
import re

import csv23


class Config(object):
    """Namespace for configuration parameters. Edit as needed."""

    # pylint: disable=useless-object-inheritance,too-few-public-methods

    # Path to the input file.
    csv_path = "data/ifsar_tif_2021.csv"

    # Path to the output file.
    out_path = "data/ifsar_tif_2021_supp.csv"


def organize():
    """Add additional attributes to the ifsar file list."""

    # pylint: disable=too-many-locals,too-many-branches,too-many-statements

    with csv23.open(Config.out_path, "w") as out_file:
        csv_writer = csv.writer(out_file)
        header = [
            "folder",
            "filename",
            "ext",
            "size",
            "legacy",
            "nga",
            "kind",
            "edge",
            "cell",
            "lat",
            "lon",
            "tfw",
            "xml",
            "html",
            "txt",
            "tif_xml",
            "ovr",
            "aux",
            "rrd",
            "aux_old",
            "crc",
            "extras",
            "skip",
        ]
        csv23.write(csv_writer, header)

        with csv23.open(Config.csv_path, "r") as csv_file:
            csv_reader = csv.reader(csv_file)
            next(csv_reader)  # ignore the header
            for row in csv_reader:
                row = csv23.fix(row)
                path_in, name, ext, size = row
                name = name.lower()
                path = path_in.lower()
                legacy = "N"
                if "legacy" in path:
                    legacy = "Y"
                nga = "N"
                if "nga_30" in path:
                    nga = "Y"
                kind = ""
                if "ori" in name or ("ori" in path and "priority" not in path):
                    kind = "ori"
                if kind == "ori" and "_sup" in name:
                    kind = "ori_sup"
                if "dsm" in name or "dsm" in path:
                    kind = "dsm"
                if "dtm" in name or "dtm" in path:
                    kind = "dtm"
                edge = "N"
                if "edge" in path:
                    edge = "Y"
                cell = ""
                lat, lon = 0, 0
                match = re.search(r"\\cell_(\d*)\\", path)
                if match:
                    cell = match.group(1)
                match = re.search(
                    r"\\cell_([def])\\", path
                )  # path -> 196, e -> 197, f -> 198
                if match:
                    cell = ord(match.group(1)) - ord("d") + 196
                match = re.search(r"_n(\d*)w(\d*)", name)
                if match:
                    lat = int(match.group(1)) / 100
                    lon = int(match.group(2)) / 100
                #
                # Check for supplemental *.html, *.aux.xml, etc files
                #
                file_path = os.path.join(path_in, name)
                exts_found = [
                    sup.replace(file_path, "").lower()
                    for sup in glob.glob(file_path + ".*")
                ]
                # exts_possible = ['.tif', '.tfw','.xml','.html','.txt','.tif.xml',
                #                  '.tif.ovr','.tif.aux.xml', '.rrd', '.aux', '.tif.crc']
                tfw, xml, html, txt, tif_xml = 0, 0, 0, 0, 0
                ovr, aux, rrd, aux_old, crc = 0, 0, 0, 0, 0
                if ".tfw" in exts_found:
                    tfw = 1
                if ".xml" in exts_found:
                    xml = 1
                if ".html" in exts_found:
                    html = 1
                if ".txt" in exts_found:
                    txt = 1
                if ".tif.xml" in exts_found:
                    tif_xml = 1
                if ".tif.ovr" in exts_found:
                    ovr = 1
                if ".tif.aux.xml" in exts_found:
                    aux = 1
                if ".rrd" in exts_found:
                    rrd = 1
                if ".aux" in exts_found:
                    aux_old = 1
                if ".tif.crc" in exts_found:
                    crc = 1
                extras = (
                    len(exts_found)
                    - 1
                    - tfw
                    - xml
                    - html
                    - txt
                    - tif_xml
                    - ovr
                    - aux
                    - rrd
                    - aux_old
                    - crc
                )  # 1 for the tif that must exist
                out_row = [
                    path_in,
                    name,
                    ext,
                    size,
                    legacy,
                    nga,
                    kind,
                    edge,
                    cell,
                    lat,
                    lon,
                    tfw,
                    xml,
                    html,
                    txt,
                    tif_xml,
                    ovr,
                    aux,
                    rrd,
                    aux_old,
                    crc,
                    extras,
                    "N",
                ]
                csv23.write(csv_writer, out_row)
