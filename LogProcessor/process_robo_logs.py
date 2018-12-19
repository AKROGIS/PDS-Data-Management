from __future__ import absolute_import, division, print_function, unicode_literals
"""
Reads the log files from robocopy and summerizes them in a database
Emails an admin when issues are found in the log file
"""

import datetime
import glob
import logging
import os
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


def process_error(file_handle, filename, line, line_num, error_sentinal):
    code, message = parse_error_line(line, filename, line_num, error_sentinal)
    error_line_num = line_num
    if not code:
        logger.error('Unable to get the error code from an error line, file: %s, line#: %d, line: %s',
                    filename, line_num, line)
    name = 'Name of error not defined'
    retry = False
    eof = False
    try:
        # next line is the name of the error (always valid in 1 year of log data)
        # The name line ends with 0x0D0D0A (\r\r\n), which python (win and mac) interprets as one line
        # vscode interprets as 2 lines (for line counting), but notepad and other editors do not
        # we will not double count this line, so line numbers will NOT match vscode line numbers.
        name = file_handle.next().strip()
        line_num += 1
        # From known log files: next lines will be one of a) retry, b) blank, or c) error (EOF)
        #   EOF occurs if robocopy is killed while recovering/waiting for an error
        #   for example, see 2018-11-07_22-00-02-KLGO-update-x-drive.log
        # Use try/except to catch StopIteration exception (EOF)
        try:
            line = file_handle.next()
            line_num += 1
        except StopIteration:
            eof = True
            line = ''
        clean_line = line.strip()
        if clean_line.endswith('... Retrying...'):
            retry = True
        elif clean_line:
            # Not blank or Retry
            # log as an error an treat as a blank line (throw this line away)
            logger.error('Unexpected data on retry line after error in log file: %s, line#: %d, line: %s',
                filename, line_num, line)
    except Exception as ex:
        # overly broad ecception catching.  I don't care what happened, I want to log the error, and continue\
        logger.error('Unexpected exception processing error lines in log file: %s, line#: %d, line: %s, exception: %s',
                filename, line_num, line, ex)

    # Error has failed unless we get a retry message
    error = {'code': code, 'failed': not retry, 'name': name, 'line_num': error_line_num, 'message': message}
    return error, eof, retry, line_num  # ignore the last line read (blank or retry), caller can read the next line to continue 


def parse_error_line(line, filename, line_num, error_sentinal):
    code = 0
    message = 'Message not defined'
    try:
        code = int(line.split(error_sentinal)[1].split()[0])
        message = line.split(') ')[1].strip()
    except Exception as ex:
        # overly broad ecception catching.  I don't care what happened, I want to log the error, and continue
        logger.error('Parsing error line in log file: %s, line#: %d, line: %s, exception: %s',
            filename, line_num, line, ex)
    return code, message


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
    error_line_num = line_num
    saved_error = None   # used when we are retrying an error.
    with open(file_name, 'r') as file_handle:
        for line in file_handle:
            try:
                line_num += 1
                if error_sentinal in line:
                    error, eof, retry, line_num = process_error(file_handle, file_name, line, line_num, error_sentinal)
                    if saved_error and saved_error['message'] != error['message']:
                        saved_error['failed'] = True
                        results['errors'].append(saved_error)
                        saved_error = None
                    if eof:
                        # Nothing comes next
                        results['errors'].append(error)
                        break
                    if not retry:
                        # We don't care what comes next, we will treat it all the same.
                        # This includes the failing after the last retry (next line will be RETRY LIMIT EXCEEDED)
                        saved_error = None  # this will only be non null when saved_error['message'] == error['message']
                        results['errors'].append(error)
                    else: # error is retrying
                        # if not saved_error then saved_error['message'] == error['message'], so assigment is redundant but harmless
                        saved_error = error
                        error_line_num = line_num
                        # Options for what comes next:
                        #   1) same error repeats as a fail: clear saved_error, log new error, continue
                        #   2) same error repeats with a new retry: (re)set saved_error, continue
                        #   3) new error: save saved_error as fail, process new error based on retry status
                        #   4) retry succeeds: log this error: status should be non-fail
                    continue
                else:
                    if saved_error is not None:
                        # this line is not an error and the last error we saw was retrying
                        #   1) this is a repeat of the file name before the error, which means nothing, need to check following line
                        #   2) this is a new filename
                        retry_worked = (line_num - error_line_num > 1)
                        if retry_worked:
                            results['errors'].append(saved_error)  # logs a non-failing error
                            saved_error = None
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
        if saved_error:
            # could happen if there was a error retrying that was not resolved before the file ended
            results['errors'].append(saved_error)  # logs a non-failing error
    return results


def clean_db(db_name):
    with sqlite3.connect(db_name) as conn:
        db_clear(conn, drop=False)
        db_create(conn)


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


def db_write_log(db, log):
    cursor = db.cursor()
    cursor.execute('''
        INSERT INTO logs (park, date, filename, finished)
        VALUES (:park, :date, :filename, :finished)
    ''', log)
    log_id = cursor.lastrowid
    db.commit()
    return log_id


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


def main(db_name, log_folder):
    filelist = glob.glob(os.path.join(log_folder, '*-update-x-drive.log'))
    if not filelist:
        logger.error('No robocopy log files were found')
    with sqlite3.connect(db_name) as conn:
        for filename in filelist:
            try:
                no_errors = True
                no_fails = True
                no_mismatch = True
                logger.info("Processing %s", filename)
                log = process_park(filename)
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


if __name__ == '__main__':
    try:
        db = LOG_ROOT + '/logs.db'
        folder = LOG_ROOT
        # clean_db(db)
        # main(db, folder)
    except Exception as ex:
        # overly broad ecception catching.  I don't care what happened, I need to log the exception for debugging
        logger.error('Unexpected exception: %s', ex)

    # TODO: read head of \\inpakrovmdist\GISData2\GIS\ThemeMgr\PDS_ChangeLog.txt to get last update
    # TODO: copy \\inpakrovmdist\GISData2\PDS_ChangeLog.html to \\inpakrovmgis\inetapps\robo
