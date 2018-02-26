from __future__ import absolute_import, division, print_function, unicode_literals
import time


def process_summary(file_handle):
    results = {}
    results['dirs'] = process_summary_line(file_handle.next(), 'Dirs :')
    results['files'] = process_summary_line(file_handle.next(), 'Files :')
    results['bytes'] = process_summary_line(file_handle.next(), 'Bytes :')
    results['times'] = process_summary_line(file_handle.next(), 'Times :')
    return results


def process_summary_line(line, sentinal):
    # FIXME need to add errors to the results object; maybe throw parse exception and log in main
    if sentinal not in line:
        # FIXME log error
        print('Error: bad {0} line {1}'.format(sentinal, line))
        return None

    count_obj = {}
    try:
        clean_line = line.replace(sentinal, '')
        if sentinal == 'Bytes :':
            counts = [int(float(item)) for item in clean_line.replace(' g', 'e9').replace(' m', 'e6').replace(' k', 'e3').split()]
        elif sentinal == 'Times :':
            clean_line = clean_line.replace('          ', '   0:00:00')
            times = [time.strptime(item, '%H:%M:%S') for item in clean_line.split()]
            counts = [t.tm_hour*3600 + t.tm_min*60 + t.tm_sec for t in times]
        else:
            counts = [int(item) for item in clean_line.split()]

        count_obj['total'] = counts[0]
        count_obj['copied'] = counts[1]
        count_obj['skipped'] = counts[2]
        count_obj['mismatch'] = counts[3]
        count_obj['failed'] = counts[4]
        count_obj['extra'] = counts[5]
    except Exception as ex:
        #FIXME Log error
        print(ex)

    return count_obj


def process_park(file_name):
    summary_header = '               Total    Copied   Skipped  Mismatch    FAILED    Extras\r\n'
    results = {}
    with open(file_name) as fh:
        #TODO log error if unable to open file
        results['finished'] = True
        results['name'] = 'xxxx'  # TODO get from filename or contents
        results['date'] = 'xxxx'  # TODO get from filename or contents
        errors = []
        for line in fh:
            if line == summary_header:
                summary = process_summary(fh)
                results['stats'] = summary
            elif ' ERROR ' in line:
                if 'ERROR 53 (0x00000035)' in line:
                    #TODO: if we do not find 'ERROR: RETRY LIMIT EXCEEDED.' in a future line, then ignore
                    if 53 in errors:
                        continue
                    else:
                        errors.append(53)
                    #FIXME: Log Red alert
                    print('Remote server unreachable')
                elif 'ERROR 5 (0x00000005)' in line:
                    #TODO: if we do not find 'ERROR: RETRY LIMIT EXCEEDED.' in a future line, then ignore
                    if 5 in errors:
                        continue
                    else:
                        errors.append(5)
                    #FIXME: Log Red alert
                    print('Access is denied')
                elif 'ERROR 32 (0x00000020)' in line:
                    if 32 in errors:
                        continue
                    else:
                        errors.append(32)
                    #FIXME: Log Amber alert
                    print('File is locked')
                else:
                    #FIXME Log red alert
                    print('Unexpected error')
            elif 'Hours : Paused at ' in line:
                #FIXME Log Amber
                results['finished'] = False

        results['errors'] = errors
    return results


def main():
    dena = process_park('data/Logs/2018-02-12_22-00-01-DENA-update-x-drive.log')
    print(dena)


if __name__ == '__main__':
    main()
