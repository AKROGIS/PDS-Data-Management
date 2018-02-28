from __future__ import absolute_import, division, print_function, unicode_literals
import os
import time
import logging
# import logging.config
# import config_logger
# logging.config.dictConfig(config_logger.config)
# logging.raiseExceptions = False # Ignore errors in the logging system
logger = logging.getLogger('main')
logger.info("Logging Started")


def process_summary(file_handle, errors):
    results = {}
    results['dirs'], errors = process_summary_line(file_handle.next(), 'Dirs :', errors)
    results['files'], errors = process_summary_line(file_handle.next(), 'Files :', errors)
    results['bytes'], errors = process_summary_line(file_handle.next(), 'Bytes :', errors)
    results['times'], errors = process_summary_line(file_handle.next(), 'Times :', errors)
    return results, errors


def process_summary_line(line, sentinal, errors):
    count_obj = {}
    count_obj['total'] = -1
    count_obj['copied'] = -1
    count_obj['skipped'] = -1
    count_obj['mismatch'] = -1
    count_obj['failed'] = -1
    count_obj['extra'] = -1

    if sentinal not in line:
        logger.error('Error Sentinal missing from summary line; sentinal: %s; line: %s', sentinal, line)
        errors.append('Summary Parsing Error')
        return count_obj, errors

    try:
        clean_line = line.replace(sentinal, '')
        if sentinal == 'Bytes :':
            counts = [int(float(item)) for item in clean_line.replace(' g', 'e9')
                      .replace(' m', 'e6').replace(' k', 'e3').split()]
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
        errors.append('Summary Parsing Error')
        logger.error('Exception in Summary: %s; sentinal: %s; line: %s', ex, sentinal, line)

    return count_obj, errors


def process_error(line, errors, park):
    if 'ERROR 53 (0x00000035)' in line:
        #TODO: if we do not find 'ERROR: RETRY LIMIT EXCEEDED.' in a future line, then ignore
        if 53 not in errors:
            errors.append(53)
            logger.error('Remote server %s unreachable', park)
    elif 'ERROR 5 (0x00000005)' in line:
        #TODO: if we do not find 'ERROR: RETRY LIMIT EXCEEDED.' in a future line, then ignore
        if 5 not in errors:
            errors.append(5)
            logger.error('%s: Access is denied', park)
    elif 'ERROR 32 (0x00000020)' in line:
        if 32 not in errors:
            errors.append(32)
            logger.warning('%s: File is locked', park)
    else:
        logger.error('%s: Unexpected Error: %s', park, line)
        errors.append('Unknown ERROR')
    return errors


def process_park(file_name):
    summary_header = '               Total    Copied   Skipped  Mismatch    FAILED    Extras\r\n'
    results = {}
    basename = os.path.basename(file_name)
    results['name'] = basename[20:24]
    results['date'] = basename[:10]
    results['finished'] = True
    errors = []
    results['errors'] = errors
    line_num = 0
    try:
        file_handle = open(file_name)
        for line in file_handle:
            line_num += 1
            if line == summary_header:
                summary, errors = process_summary(file_handle, errors)
                results['stats'] = summary
            elif ' ERROR ' in line:
                errors = process_error(line, errors, results['name'])
            elif 'Hours : Paused at ' in line:
                logger.warning('%s: Robo copy not finished', results['name'])
                results['finished'] = False
    except Exception as ex:
        logger.error('Unexpected exception processing log file %s, on line %d, exception: %s', file_name, line_num, ex)
    finally:
        file_handle.close()
    return results


def main():
    # import glob
    # filelist = glob.glob('data/Logs/*-update-x-drive.log')
    filelist = ['data/Logs/2018-02-12_22-00-01-DENA-update-x-drive.log']
    for filename in filelist:
        print(filename)
        print('='*len(filename))
        res = process_park(filename)
        print(res)
        print()


if __name__ == '__main__':
    main()
