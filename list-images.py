"""
Lists all the tif images(with sizes) below a starting folder
"""

from __future__ import absolute_import, division, print_function, unicode_literals
import os


def check_folder(folder, ext, outputter=None):
    for current_folder, _, files in os.walk(folder):
        for filename in files:
            name, extension = os.path.splitext(filename)
            if extension.lower() == ext:
                size = -1
                try:
                    size = os.path.getsize(os.path.join(current_folder, filename))
                except os.error:
                    pass
                output = [current_folder, name, extension, str(size)]
                if outputter is None:
                    print(','.join(output))
                else:
                    outputter(output)


def main(folder, ext='tif', csv_file=None):
    if csv_file is None:
        print(','.join(['folder', 'filename', 'ext', 'size']))
        check_folder(folder, ext)
    else:
        import csv
        with open(csv_file, 'wb') as f:
            csv_writer = csv.writer(f)

            def put_in_csv(row):
                csv_writer.writerow(row)

            put_in_csv(['folder', 'filename', 'ext', 'size'])
            check_folder(folder, ext, put_in_csv)


if __name__ == '__main__':
    # Test
    # main('Z:\Worldview1\KLGO', '.ntf', 'data/test_images_z.csv')
    # SPOT5
    # main('X:\\SDMI\\SPOT5', '.tif', 'data/spot_images_x.csv')  # Subset of Z:\Spot5
    # main('Z:\\SPOT5', '.tif', 'data/spot_images_z.csv')
    # main('Y:\\Extras\\AKR\\Statewide\\Imagery\\SDMI_SPOT5', 'tif', 'data/spot_images_y.csv')  # Duplicate of Z:\SPOT5
    # IFSAR
    # main('X:\\SDMI\\IFSAR', '.tif') #, 'data/ifsar_images_x.csv')  # Subset of Z:\IFSAR
    # main('Z:\\IFSAR', '.tif', 'data/ifsar_images_z.csv')
    # main('Y:\\Extras\\AKR\\Statewide\\DEM\\SDMI_IFSAR', '.tif', 'data/spot_images_y.csv')  # Duplicate of Z:\IFSAR
    # IKONOS
    # main(r'X:\IKONOS\LACL\BGRN', '.tif')
    # main(r'X:\Extras\AKR\Statewide\DEM\SDMI_IFSAR', '.bil', 'c:/Users/RESarwas/Documents/GitHub/pds-reorg/data/ifsar_bil_new_x.csv')
    main(r'X:\Extras\AKR\Statewide\DEM\SDMI_IFSAR\2019_IFSAR\Summer_2017_Lot8_9', '.tif', 'data/ifsar_tif_2019b.csv')
