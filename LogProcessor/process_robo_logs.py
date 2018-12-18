from __future__ import absolute_import, division, print_function, unicode_literals
"""
Reads the log file from robo copy and summerizes the log in a database
Emails an admin when issues are found in the log file
"""

import datetime
import glob
import logging
import os
import re
import sqlite3
import time
import logging.config
import config_logger

LOG_ROOT = 'E:/XDrive/Logs'

logging.config.dictConfig(config_logger.config)
# Comment the next line during testing, uncomment in production
# logging.raiseExceptions = False # Ignore errors in the logging system
logger = logging.getLogger('main')
logger.info("Logging Started")


def process_summary(file_handle, filename, line_num):
    results = {}
    for key,text in [('dirs','Dirs :'), ('files', 'Files :'), ('bytes', 'Bytes :'), ('times', 'Times :')]:
        try:
            line = file_handle.next()
            line_num += 1
            results[key] = process_summary_line(line, text, filename, line_num)
        except Exception as ex:
            # overly broad ecception catching.  I don't care what happened, I want to log the error, and continue\
            logger.error('Unexpected exception processing summary, file: %s, line#: %d, key: %s, text: %s, line: %s, exception: %s',
                    filename, line_num, key, text, line, ex)
    return results,line_num


def process_summary_line(line, sentinal, filename, line_num):
    count_obj = {}
    count_obj['total'] = -1
    count_obj['copied'] = -1
    count_obj['skipped'] = -1
    count_obj['mismatch'] = -1
    count_obj['failed'] = -1
    count_obj['extra'] = -1

    if sentinal not in line:
        logger.error('Summary for "%s" is missing in line: %s, file: %s, line#: %d', sentinal, line, filename, line_num)
        return count_obj

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
        logger.error('Parsing summary for %s in line: %s, file: %s, line#: %d, excpetion: %s', sentinal, line, filename, line_num,  ex)

    return count_obj

""" Error Formating

NOMINAL (no error):
===================

	  			File1
                File2
                .....


NON-RETRYABLE ERROR:
====================
example: 2018-01-31_22-00-02-DENA-update-x-drive.log  (typically error 32 at DENA)

	  			File1
Timestamp ERROR ## (0xNN) Error Message
Error Code ## Description

                File2
                ....


RETRYABLE ERROR (fail):
=======================
example: 2018-05-15_22-00-03-DENA-update-x-drive.log (line 43), example without file at line 25

                File1
Timestamp ERROR ## (0xNN) Error Message
Error Code ## Description
Waiting 5 seconds... Retrying...              (The retry group may be repeated N times)
                File1
Timestamp ERROR ## (0xNN) Error Message
Error Code ## Description

ERROR: RETRY LIMIT EXCEEDED.

                File2


RETRYABLE ERROR (success):
==========================
example: 2018-05-15_22-00-03-DENA-update-x-drive.log (line 145), example without file at line 25

                File1
Timestamp ERROR ## (0xNN) Error Message
Error Code ## Description
Waiting 5 seconds... Retrying...              (The retry group may be repeated N times)
                File2


NOTE 1
======
The "Error Code ## Description" line ends in \r\r\n
  which results in an extra empty line in vscode, but not other text editors (that I tried)
  Python on mac and windows converts \r\n to \n when reading lines. So these lines end in \r\n in python


NOTE 2
======
The File may be missing for some errors,
example: 2018-02-06_22-00-02-LACL-update-x-drive.log

2018/02/08 22:00:51 ERROR 53 (0x00000035) Accessing Destination Directory E:\XDrive\RemoteServers\XDrive-LACL\
The network path was not found.
Waiting 5 seconds... Retrying...
2018/02/08 22:01:18 ERROR 53 (0x00000035) Accessing Destination Directory E:\XDrive\RemoteServers\XDrive-LACL\


NOTE 3
======
Robocopy may pause before finishing all error retries

NOTE 4
======
Robocopy may hit a new error when retrying an different error
example: 2018-03-28_22-00-02-NOME-update-x-drive.log

NOTE 5
======
Some errors are terminal and there is nothing after the error code description
example: 2018-01-30_22-00-01-LACL-update-x-drive.log

NOTE 6
======
Error 53 (The network path was not found.) and 21 (The device is not ready.)
have no File, and will retry, and if it fails it will try another set of retries before quiting with stats
This should only be reported as a single error.
example: 2018-02-06_22-00-02-LACL-update-x-drive.log
example: 2018-03-31_22-00-02-DENA-update-x-drive.log
"""

def parse_error_line(line, filename, line_num, error_sentinal):
    code = 0
    message = 'Message not defined'
    try:
        code = int(line.split(error_sentinal)[1].split()[0])
        message = line.split(') ')[1].strip()
    except Exception as ex:
        # overly broad ecception catching.  I don't care what happened, I want to log the error, and continue
        logger.error('Parsing error in log file: %s, line#: %d, line: %s, exception: %s',
            filename, line_num, line, ex)
    return code, message


def process_error(file_handle, filename, line, line_num, error_sentinal):
    code, message = parse_error_line(line, filename, line_num, error_sentinal)
    if not code:
        logger.error('Unable to get the error code from an error line, file: %s, line#: %d, line: %s',
                    filename, line_num, line)
    name = 'Name of error not defined'
    failed = None # True if all the retries failed, False if retry succeeds, None if unable to determine due to unexpected input
    done = False
    while not done and code:
        try:
            # read name of error
            # The name line ends with 0x0D0D0A (\r\r\n), which python interprets as one line
            # vscode interprets as 2 lines (for line counting), but notepad does not
            # but most text editors interpret as two lines
            line = file_handle.next()
            line_num += 1
            name = line.strip()
            # next line will be one of a) retry, or b) blank,
            # read retry line which ends with '... Retrying...'
            #   If we have exceeded the number of reties then it will be blank and followed with ERROR: RETRY LIMIT EXCEEDED.
            #   It may be a nor-retryable error, and we will have
            line = file_handle.next()
            line_num += 1
            retry = line.strip()
            if retry.endswith('... Retrying...'):
                # Next line should be a task (skip it), then next line should be the same error, or the retry worked.
                # The task must be the same as the task before the errror, but there is no way to check it now.
                line = file_handle.next()
                line_num += 1
                task = line.strip()
                code, message = parse_error_line(line, filename, line_num, error_sentinal)
                if not task:
                    logger.error('Unexpected blank line when expecting retry of failed task in log file: %s, line#: %d, line: %s',
                        filename, line_num, line)
                    done = True
                else:
                    line = file_handle.next()
                    line_num += 1
                    if error_sentinal in line:
                        code, message = parse_error_line(line, filename, line_num, error_sentinal)
                    else:
                        done = True
                        failed = False
                    # repeat while loop
            elif not retry:
                # blank line is ok, but next line must be ERROR: RETRY LIMIT EXCEEDED,
                #   or what appears to be a blank line(0x0D0D0A (\r\r\n)) - automatic fail (no retry)
                #   actually anything implies that the error has failed and we are done.
                line = file_handle.next()
                line_num += 1
                # limit = line.strip()
                # if limit == 'ERROR: RETRY LIMIT EXCEEDED.' or not limit:
                #     failed = True
                failed = True
                done = True
            else:
                # Not blank or Retry
                logger.error('Unexpected data on retry line after error in log file: %s, line#: %d, line: %s',
                    filename, line_num, line)
                done = True
        except StopIteration:
            # WARNING, it is possible that the robocopy may be killed while retrying a failure
            #          for example, see 2018-11-07_22-00-02-KLGO-update-x-drive.log
            done = True
            failed = False
        except Exception as ex:
            # overly broad ecception catching.  I don't care what happened, I want to log the error, and continue\
            logger.error('Unexpected exception processing error, file: %s, line#: %d, line: %s, exception: %s',
                    filename, line_num, line, ex)

    error = {'code': code, 'failed': failed, 'name': name, 'line_num': line_num, 'message': message}
    return error, line, line_num


def process_park(file_name):
    summary_header = 'Total    Copied   Skipped  Mismatch    FAILED    Extras'
    error_sentinal = ' ERROR '
    finished_sentinal = '   Ended : '
    paused_sentinal = '    Hours : Paused at 06:'

    results = {}
    basename = os.path.basename(file_name)
    park = basename[20:24]
    date = basename[:10]
    results['park'] = park
    results['date'] = date
    results['filename'] = file_name
    results['finished'] = None
    results['errors'] = []
    line_num = 0
    with open(file_name, 'r') as file_handle:
        for line in file_handle:
            try:
                line_num += 1
                if error_sentinal in line:
                    error, line, line_num = process_error(file_handle, file_name, line, line_num, error_sentinal)
                    results['errors'].append(error)
                    if error['failed'] is not None:
                        continue
                if line.strip() == summary_header:
                    summary, line_num = process_summary(file_handle, file_name, line_num)
                    results['stats'] = summary
                elif line.startswith(finished_sentinal):
                    results['finished'] = True
                elif line.startswith(paused_sentinal):
                    logger.warning('%s on %s: Robo copy not finished (paused then killed)', park, date)
                    results['finished'] = False
            except Exception as ex:
                # overly broad ecception catching.  I don't care what happened, I want to log the error, and continue
                logger.error('Unexpected exception processing log, file: %s, line#: %d, line: %s, exception: %s',
                    file_name, line_num, line, ex)
    return results


def db_clear(db, drop=True):
    try:
        cursor = db.cursor()
        if drop:
            cursor.execute('DROP INDEX IF EXISTS logs_date_ix')
            cursor.execute('DROP TABLE IF EXISTS logs')
            cursor.execute('DROP TABLE IF EXISTS stats')
            cursor.execute('DROP TABLE IF EXISTS errors')
        else:
            cursor.execute('DELETE FROM logs')
            cursor.execute('DELETE FROM stats')
            cursor.execute('DELETE FROM errors')
        db.commit()
    except sqlite3.OperationalError:
        pass


def db_get_rows(db, sql, header=True):
    cursor = db.cursor()
    rows = cursor.execute(sql).fetchall()
    if header:
        return [[item[0] for item in cursor.description]] + rows
    else:
        return rows


def db_write_stats(db, stats):
    cursor = db.cursor()
    cursor.executemany('''
        INSERT INTO stats (log_id, stat, copied, extra, failed, mismatch, skipped, total)
        VALUES (:log, :stat, :copied, :extra, :failed, :mismatch, :skipped, :total)
    ''', stats)
    db.commit()


def db_write_errors(db, errors):
    cursor = db.cursor()
    cursor.executemany("""
        INSERT OR IGNORE INTO error_codes(error_code, error_name)
        VALUES(:code, :name)
    """, errors)
    cursor.executemany('''
        INSERT INTO errors (error_code, log_id, line_num, failed, message)
        VALUES (:code, :log, :line_num, :failed, :message)
    ''', errors)
    db.commit()


def db_write_log(db, log):
    cursor = db.cursor()
    cursor.execute('''
        INSERT INTO logs (park, date, filename, finished)
        VALUES (:park, :date, :filename, :finished)
    ''', log)
    log_id = cursor.lastrowid
    db.commit()
    return log_id


def db_create(db):
    cursor = db.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs(
            log_id INTEGER PRIMARY KEY,
            park TEXT,
            date TEXT,
            filename TEXT,
            finished INTEGER);
    ''')
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS logs_date_ix ON logs(date);
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stats(
            stat_id INTEGER PRIMARY KEY,
            log_id INTEGER NOT NULL,
            stat TEXT,
            copied INTEGER,
            extra INTEGER,
            failed INTEGER,
            mismatch INTEGER,
            skipped INTEGER,
            total INTEGER,
            FOREIGN KEY(log_id) REFERENCES logs(log_id));
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS error_codes(
            error_code INTEGER NOT NULL,
            error_name TEXT,
            UNIQUE(error_code));
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS errors(
            error_id INTEGER PRIMARY KEY,
            error_code INTEGER NOT NULL,
            log_id INTEGER NOT NULL,
            line_num INTEGER,
            failed INTEGER,
            message TEXT,
            FOREIGN KEY(error_code) REFERENCES error_codes(error_code),
            FOREIGN KEY(log_id) REFERENCES logs(log_id));
    ''')
    db.commit()


def main(db_name, log_folder):
    # TODO: if yesterdays logs are not found, then log an email error
    #filelist = ['data/Logs/old/2018-02-12_22-00-01-DENA-update-x-drive.log']
    filelist = glob.glob(os.path.join(log_folder, '*-update-x-drive.log'))
    with sqlite3.connect(db_name) as conn:
        for filename in filelist:
            try:
                no_errors = True
                no_fails = True
                no_mismatch = True
                logger.info("Processing %s", filename)
                log = process_park(filename)
                # TODO: Move file into archive directory
                if not log:
                    logger.error('The log object for %s is empty', filename)
                    continue
                for item in ['park', 'date', 'filename', 'finished']:
                    if item not in log:
                        logger.error('The log object for %s is bad; "%s" is missing', filename, item)
                        continue
                if log['finished'] is None:
                    logger.warning('%s on %s: Robo copy had to be killed (it was copying a very large file when asked to pause)', log['park'], log['date'])
                try:
                    log_id = db_write_log(conn, log)
                except sqlite3.Error as ex:
                    logger.error('Writing log %s to DB; %s', filename, ex)
                if not log_id:
                    logger.error("No Log ID returned from DB for log file %s", filename)
                    continue
                if 'errors' in log:
                    for error in log['errors']:
                        error['log'] = log_id
                        for attrib in ['code', 'failed', 'name', 'line_num', 'message']:
                            if attrib not in error:
                                logger.error('Bad errors object in log file %s, missing: %s in %s', filename, attrib, str(error))
                                continue
                        no_errors = False
                    try:
                        db_write_errors(conn, log['errors'])
                    except sqlite3.Error as ex:
                        logger.error('Writing errors for log %s to DB; %s', filename, ex)
                if 'stats' in log:
                    stats = []
                    for stat in ['dirs','files','bytes','times']:
                        if stat not in log['stats']:
                            logger.error('Bad stats object in log file %s, missing: %s', filename, stat)
                            continue
                        obj = log['stats'][stat]
                        for item in ['copied', 'extra', 'failed', 'mismatch', 'skipped', 'total']:
                            if item not in obj:
                                logger.error('Bad stats object in log file %s, missing: %s/%s', filename, stat, item)
                                continue
                        obj['log'] = log_id
                        obj['stat'] = stat
                        stats.append(obj)
                        if obj['failed']:
                            no_fails = False
                        if obj['mismatch']:
                            no_mismatch = False
                    try:
                        db_write_stats(conn, stats)
                    except sqlite3.Error as ex:
                        logger.error('Writing stats for log %s to DB; %s', filename, ex)
                else:
                    # We do not expect to get stats when robo didn't finish (finished == False or None)
                    if log['finished']:
                        logger.error('No stats for log %s', filename)

                # In daily processing, I want an error email when there are issues in a log file
                #  currently even recovered errors send an error
                if not no_errors or not no_fails or not no_mismatch:
                    print(no_errors, no_fails, no_mismatch)
                    logger.warning('The log file %s has errors', filename)

            except Exception as ex:
                # overly broad ecception catching.  I don't care what happened, I want to log the error, and continue
                logger.error('Unexpected exception processing log file: %s, exception: %s',
                    filename, ex)
    clean_folder(log_folder)


def test_file_structure(log_folder):
    """
Line types (in body, i.e. not header or stats):
* blank: not line.strip()
* file: whitespace then either E:\.... or \\inpak....
* error: contains ERROR sentinal
* error name: follows error line
* retry: ...retry...
* retry fail:
* pause: starts with "    Hours : Paused at"
* divider: "--------------.... at end of header before stats (and around title)
    """
    errors = {}
    """ Expecting: {
        2 => The system cannot find the file specified.
        5 => Access is denied.
        19 => The media is write protected.
        21 => The device is not ready.
        32 => The process cannot access the file because it is being used by another process.
        53 => The network path was not found.
        59 => An unexpected network error occurred.
        64 => The specified network name is no longer available.
        67 => The network name cannot be found.
        121 => The semaphore timeout period has expired.
    }"""
    relations = {}
    """Expecting:
        (u'blank', u'blank') => 2520
        (u'blank', u'divider2') => 3233
        (u'blank', u'error') => 793
        (u'blank', u'fail') => 1171
        (u'blank', u'file') => 2151
        (u'blank', u'pause') => 11
        (u'blank', u'retry') => 73
        (u'divider1', u'blank') => 3345
        (u'divider2', u'EOF') => 3233
        (u'error', u'EOF') => 1
        (u'error', u'blank') => 2189
        (u'error', u'retry') => 5868
        (u'fail', u'blank') => 1171
        (u'file', u'EOF') => 15
        (u'file', u'blank') => 725
        (u'file', u'error') => 4201
        (u'file', u'file') => 291043
        (u'file', u'pause') => 85
        (u'pause', u'EOF') => 96
        (u'retry', u'blank') => 2
        (u'retry', u'error') => 3064
        (u'retry', u'file') => 2875
    """
    filelist = glob.glob(os.path.join(log_folder, '2018-*-update-x-drive.log'))
    for filename in filelist:
        try:
            with open(filename, 'r') as file_handle:
                previous_line = 'unknown'
                in_header = True
                # first 3 lines are always the same
                file_handle.readline()  #
                file_handle.readline()  #-------------------------------------------------------------------------------
                file_handle.readline()  #   ROBOCOPY     ::     Robust File Copy for Windows
                file_handle.readline()  #-------------------------------------------------------------------------------
                line_num = 3
                for line in file_handle:
                    line_type = 'unknown'
                    try:
                        line_num += 1
                        clean_line = line.strip()
                        divider_line = clean_line.startswith('-------------')
                        if in_header and not divider_line:
                            continue  #skip the variable length header
                        if in_header and divider_line:
                            in_header = False
                            previous_line = 'divider1'
                            continue
                        if not in_header and divider_line:
                            # start stats (verify)
                            file_handle.next() # blankline
                            stats_line = file_handle.next().strip()
                            if not stats_line.startswith('Total'):
                                print('fail in stats in {0}'.format(filename))
                            line_type = 'divider2'
                            if (previous_line,line_type) not in relations:
                                relations[(previous_line,line_type)] = 0
                            relations[(previous_line,line_type)] += 1
                            previous_line = line_type
                            break
                        blank_line = not clean_line
                        if blank_line:
                            if line_type != 'unknown':
                                print('line is already defined {0} to {1} at {2} in {3}'.format(line_type, 'blank', line_num, filename))
                            line_type = 'blank'
                        file_line = clean_line.startswith('E:\\') or clean_line.startswith(r'\\inpak')
                        if file_line:
                            if line_type != 'unknown':
                                print('line is already defined {0} to {1} at {2} in {3}'.format(line_type, 'file', line_num, filename))
                            line_type = 'file'
                        retry_line = clean_line.endswith('... Retrying...')
                        if retry_line:
                            if line_type != 'unknown':
                                print('line is already defined {0} to {1} at {2} in {3}'.format(line_type, 'retry', line_num, filename))
                            line_type = 'retry'
                        fail_line = clean_line == 'ERROR: RETRY LIMIT EXCEEDED.'
                        if fail_line:
                            if line_type != 'unknown':
                                print('line is already defined {0} to {1} at {2} in {3}'.format(line_type, 'fail', line_num, filename))
                            line_type = 'fail'
                        pause_line = clean_line.startswith('Hours : Paused at')
                        if pause_line:
                            if line_type != 'unknown':
                                print('line is already defined {0} to {1} at {2} in {3}'.format(line_type, 'pause', line_num, filename))
                            line_type = 'pause'
                        error_line = ' ERROR ' in clean_line
                        if error_line:
                            if line_type != 'unknown':
                                print('line is already defined {0} to {1} at {2} in {3}'.format(line_type, 'error', line_num, filename))
                            line_type = 'error'
                            code = int(line.split(' ERROR ')[1].split()[0])
                            desc = file_handle.next().strip()
                            line_num += 1
                            if code in errors:
                                if errors[code] != desc:
                                    print('error code mismatch got {2} expecting {3} for {4} at line {0} in {1}'.format(line_num, filename, desc, errors[code], code))
                            else:
                                errors[code] = desc
                        if line_type == 'unknown':
                            print('Line type is unknown in {0}'.format(filename))
                        if (previous_line,line_type) not in relations:
                            relations[(previous_line,line_type)] = 0
                        relations[(previous_line,line_type)] += 1
                        previous_line = line_type
                    except Exception as ex:
                        print('exception {2} at line {0} in {1}'.format(line_num, filename, ex))
                if (previous_line,'EOF') not in relations:
                    relations[(previous_line,'EOF')] = 0
                relations[(previous_line, 'EOF')] += 1
        except Exception as ex:
            print('exception {1} in {0}'.format(filename, ex))
    keys = sorted(errors.keys())
    for key in keys:
        print('  {0} => {1}'.format(key, errors[key]))
    keys = sorted(relations.keys())
    for key in keys:
        print('  {0} => {1}'.format(key, relations[key]))


def clean_folder(folder):
    year = datetime.date.today().year
    archive = str(year) + 'archive'
    archive_path = os.path.join(folder, archive)
    if not os.path.exists(archive_path):
        os.mkdir(archive_path)
    filelist = glob.glob(os.path.join(folder, '*-update-x-drive.log'))
    filelist += glob.glob(os.path.join(folder, '*-update-x-drive-output.log'))
    filelist += glob.glob(os.path.join(folder, '*-robo-morning-kill.log'))
    for filename in filelist:
        try:
            new_name = os.path.join(archive_path, os.path.basename(filename))
            os.rename(filename,new_name)
        except Exception as ex:
            # overly broad ecception catching.  I don't care what happened, I want to log the error, and continue
            logger.error('Unexpected exception moving log file: %s to archive %s, exception: %s',
                filename, new_name, ex)
    # These log files do not have a date stamp, so be sure to remove the previous copy
    filelist = glob.glob(os.path.join(folder, '*-cmd.log'))
    for filename in filelist:
        try:
            new_name = os.path.join(archive_path, os.path.basename(filename))
            if os.path.exists(new_name):
                os.remove(new_name)
            os.rename(filename,new_name)
        except Exception as ex:
            # overly broad ecception catching.  I don't care what happened, I want to log the error, and continue
            logger.error('Unexpected exception moving log file: %s to archive %s, exception: %s',
                filename, new_name, ex)


def clean(db_name):
    with sqlite3.connect(db_name) as conn:
        db_clear(conn, drop=False)
        db_create(conn)


def db_testing(db_name):
    with sqlite3.connect(db_name) as conn:
        db_create(conn)
        log_id = db_write_log(conn,
            #{'name':'DENA', 'date':'2018-02-12', 'finished':True, 'errors':None}
            {'name':'DENA', 'date':'2018-02-12', 'finished':True, 'errors':str(['e1','e2']), 'junk':5}
        )
        db_write_stats(conn,
            [
                {'log':log_id, 'stat': u'dirs', u'skipped': 3, u'extra': 2, u'mismatch': 0, u'failed': 0, u'copied': 0, u'total': 4711},
                {'log':log_id, 'stat': u'files', u'skipped': 234433, u'extra': 0, u'mismatch': 0, u'failed': 0, u'copied': 0, u'total': 234433},
                {'log':log_id, 'stat': u'bytes', u'skipped': 557141000000, u'extra': 0, u'mismatch': 0, u'failed': 0, u'copied': 0, u'total': 557141000000},
                {'log':log_id, 'stat': u'times', u'skipped': 0, u'extra': 212, u'mismatch': 0, u'failed': 0, u'copied': 0, u'total': 212}
            ]
        )
        sql = 'SELECT * FROM stats JOIN logs on stats.log_id = logs.log_id;'
        print(db_get_rows(conn, sql))
        db_clear(conn)
        print(db_get_rows(conn, sql))


def test_queries(db_name):
    # Date of last scan
    q1 = "select max(date) as last_run from logs;"
    # Summary of last days scan
    #  NOTE: DENA typically differs from all other parks in counts, so it is omitted
    #  NOTE: the error/finished counts may be wrong if more than a single date is considered
    q2 = """
SELECT l.date,
  max(sf.total) as files_scanned, max(sd.total) as dirs_scanned,
  max(sf.copied) as files_copied, max(sf.extra) as files_removed,
  max(sb.copied) as bytes_copied, max(sb.extra) as bytes_removed,
  sum(e.count_errors) as total_errors,
  count(l1.park) as count_complete,
  count(l2.park) as count_incomplete,
  count(l3.park) as count_unfinished
from logs as l
left join stats as sf on l.log_id = sf.log_id and sf.stat = 'files' AND l.park <> 'DENA'
left join stats as sd on l.log_id = sd.log_id and sd.stat = 'dirs' AND l.park <> 'DENA'
left join stats as st on l.log_id = st.log_id and st.stat = 'times' AND l.park <> 'DENA'
left join stats as sb on l.log_id = sb.log_id and sb.stat = 'bytes' AND l.park <> 'DENA'
left join logs as l1 on l.log_id = l1.log_id and l1.finished = 1
left join logs as l2 on l.log_id = l2.log_id and l2.finished = 0
left join logs as l3 on l.log_id = l3.log_id and l3.finished IS NULL
left join (select log_id, count(*) as count_errors from errors group by log_id) as e on l.log_id = e.log_id
where l.date = (SELECT max(date) from logs)
GROUP BY l.date;
    """
    # Park details
    #   Could include some more failure stats, see q7 below
    q3 = """
select l.park, l.date, l.finished, e.count_errors,
  sf.copied as files_copied, sf.extra as files_removed, sf.total as files_scanned,
  st.copied as time_copying, st.extra as time_scanning, sb.copied as bytes_copied
from logs as l
left join stats as sf on l.log_id = sf.log_id and sf.stat = 'files'
left join stats as st on l.log_id = st.log_id and st.stat = 'times'
left join stats as sb on l.log_id = sb.log_id and sb.stat = 'bytes'
left join (select log_id, count(*) as count_errors from errors group by log_id) as e on l.log_id = e.log_id
where date = (SELECT max(date) from logs) ORDER BY Park;
"""
    # Logs that did not finish normally
    q4 = "select park, date from logs where finished = 0 or finished IS NULL order by date, park;"
    # Number of errors per log file
    q5 = "select log_id, count(*) as count_errors from errors group by log_id;"
    # Mismatch and Failed Stats per log file
    q6 = """
select l.date, l.park, l.finished, e.count_errors, s.stat, s.failed, s.mismatch
from stats as s
left join logs as l on l.log_id = s.log_id
left join (select log_id, count(*) as count_errors from errors group by log_id) as e on l.log_id = e.log_id
where (s.failed > 0 OR s.mismatch > 0)
order by l.date, l.park, s.stat;
    """
    # Count of logs per day
    q7 = "select date, count(*) from logs group by date order by date;"
    # When the robocopy fail count does not equal my failed error count
    q8 = """
select l.park, l.date, e.count, s.failed from logs as l
left join (select log_id, count(*) as count from errors where failed group by log_id) as e on e.log_id = l.log_id
--left join (select log_id, count(*) as count from errors where failed and error_code <> 32 group by log_id) as e on e.log_id = l.log_id
left join stats as s on l.log_id = s.log_id
where s.stat = 'files' and s.failed <> e.count
order by l.date, l.park;
    """
    # for logs without a failure, copied + extra times = total time, mismatch and skipped = 0
    q9 = """
select l.park, count(*), avg(s.copied), avg(s.extra), avg(s.skipped), avg(failed), avg(s.total), avg(s.copied)+avg(s.extra) from stats as s
left join logs as l on s.log_id = l.log_id
where s.stat = 'times' -- and s.log_id in (select log_id from stats where stat = 'bytes' and failed = 0)
group by l.park order by l.park;
    """
    # Other query ideas:
    #   Last error by Park
    #   All Errors by Park
    #   Speed Statistics by Park, last week, month, year, arbitrary period
    #   Speed Comparison by Park, no updates, small, medium and large updates

    with sqlite3.connect(db_name) as conn:
        for q in [q1, q2, q3, q4, q5, q6, q7, q8, q9]:
            for row in db_get_rows(conn, q):
                # error = row[0].split(') ')[1].strip()
                # code = int(row[0].split(' ERROR ')[1].split()[0])
                # print('{0:3d}|{1}'.format(code,error))
                print(row)


if __name__ == '__main__':
    try:
        db = LOG_ROOT + '/logs.db'
        folder = LOG_ROOT
        #main(db, folder)
        #test_queries(db)
    except Exception as ex:
        # overly broad ecception catching.  I don't care what happened, I need to log the exception for debugging
        logger.error('Unexpected exception: %s', ex)

    #test_file_structure(r"\\inpakrovmais\Xdrive\Logs\2018archive")
    test_file_structure(r"data/Logs/old")
    #print(process_park(r"\\inpakrovmais\Xdrive\Logs\2018archive\2018-12-16_18-00-01-LACL-update-x-drive.log"))
    #db_testing(':memory:')
    #clean(db)
    # main('data/logs.db', 'data/Logs/old')
    # test_queries('data/logs.db')
    #process_park('data/Logs/2018-11-22_22-00-02-KLGO-update-x-drive.log')

    # TODO: read head of \\inpakrovmdist\GISData2\GIS\ThemeMgr\PDS_ChangeLog.txt to get last update
    # TODO: copy \\inpakrovmdist\GISData2\PDS_ChangeLog.html to \\inpakrovmgis\inetapps\robo
    # TODO: Option to clear/reprocess  a given day or day/park
    # TODO: Add command line options ?

    # Weird Files:
    # Parsing errors:
    #   2018-10-22_22-00-02-KLGO-update-x-drive.log: line 23 was retying a semaphore error, and then printed stats
    #   2018-10-25_22-00-02-KLGO-update-x-drive.log: line 720 was retying a semaphore error, and then printed stats
    # When robocopy fail file count does not equal my failed error count:
    #     All but the following cases are with error 32 not being counted as a fail by robocopy,
    #     but I count it (a remote file that can't be deleted); mostly this is lock files at DENA,
    #     or files at KLGO after a semaphore (121) error
    #   2018-11-20_22-00-02-KLGO-update-x-drive.log: line 147, a semaphore (121) error is not retried is not retired, so I call it a fail, robo does not
    #   2018-11-22_22-00-02-KLGO-update-x-drive.log: Got 357 hard (ERROR: RETRY LIMIT EXCEEDED.) fails (I only couned 351), but robo only counted 76 (and 14 dirs)
    #   NOME|2018-05-19|150|77
    #   KOTZ|2018-07-02|9|8
