from __future__ import absolute_import, division, print_function, unicode_literals
import datetime
import glob
import logging
import os
import re
import sqlite3
import time
import logging.config
import config_logger

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


def process_error(errors, line, file_handle, filename, line_num):
    # TODO, Simplify this with a list of potential errors, not a switch
    # TODO, Take as a configuration option, then number of retries, record if failed retries
    # TODO, Get the file name as part of the error
    if 'ERROR 2 (0x00000002)' in line:
        errors.append({'error_code': 2, 'failed': True,
            'error_name': 'The system cannot find the file specified.',
            'line_num': line_num, 'filename': line})
    elif 'ERROR 5 (0x00000005)' in line:
        errors.append({'error_code': 5, 'failed': True,
            'error_name': 'Access is denied.',
            'line_num': line_num, 'filename': line})
    elif 'ERROR 19 (0x00000013)' in line:
        errors.append({'error_code': 19, 'failed': True,
            'error_name': 'The media is write protected.',
            'line_num': line_num, 'filename': line})
        # The happened on a KENNECOTT few files, then we got error 53 (unreachable)
    elif 'ERROR 21 (0x00000015)' in line:
        errors.append({'error_code': 21, 'failed': True,
            'error_name': 'The device is not ready.',
            'line_num': line_num, 'filename': line})
    elif 'ERROR 32 (0x00000020)' in line:
        errors.append({'error_code': 32, 'failed': True,
            'error_name': 'File is locked.',
            'line_num': line_num, 'filename': line})
    elif 'ERROR 53 (0x00000035)' in line:
        errors.append({'error_code': 53, 'failed': True,
            'error_name': 'Remote server unreachable.',
            'line_num': line_num, 'filename': line})
    elif 'ERROR 59 (0x0000003B)' in line:
        errors.append({'error_code': 59, 'failed': True,
            'error_name': 'An unexpected network error occurred.',
            'line_num': line_num, 'filename': line})
    elif 'ERROR 64 (0x00000040)' in line:
        errors.append({'error_code': 64, 'failed': True,
            'error_name': 'The specified network name is no longer available.',
            'line_num': line_num, 'filename': line})
        # Happened once at DENA (5/15/18) could not find folder.  Retried a few times, then ok
    elif 'ERROR 67 (0x00000043)' in line:
        errors.append({'error_code': 67, 'failed': True,
            'error_name': 'The network name cannot be found.',
            'line_num': line_num, 'filename': line})
        # Happened when KLGO renamed the server without telling us.  Junction point had bad server name
    elif 'ERROR 121 (0x00000079)' in line:
        errors.append({'error_code': 121, 'failed': True,
            'error_name': 'The semaphore timeout period has expired.',
            'line_num': line_num, 'filename': line})
    else:
        errors.append({'error_code': 0, 'failed': True,
            'error_name': 'Unknown Error.',
            'line_num': line_num, 'filename': line})
    return errors, line_num


def process_park(file_name):
    summary_header = '               Total    Copied   Skipped  Mismatch    FAILED    Extras\r\n'
    error_sentinal = ' ERROR '
    finished_sentinal = '   Ended : '
    paused_sentinal = '    Hours : Paused at '

    results = {}
    basename = os.path.basename(file_name)
    park = basename[20:24]
    results['park'] = park
    results['date'] = basename[:10]
    results['filename'] = file_name
    results['finished'] = None
    results['errors'] = []
    line_num = 0
    with open(file_name, 'r') as file_handle:
        for line in file_handle:
            try:
                line_num += 1
                if line == summary_header:
                    summary, line_num = process_summary(file_handle, file_name, line_num)
                    results['stats'] = summary
                elif line.startswith(finished_sentinal):
                    results['finished'] = True
                elif error_sentinal in line:
                    results['errors'], line_num = process_error(results['errors'], line, file_handle, file_name, line_num)
                elif line.startswith(paused_sentinal):
                    logger.warning('%s: Robo copy not finished', park)
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


def db_get_rows(db, sql):
    cursor = db.cursor()
    rows = cursor.execute(sql).fetchall()
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
        VALUES(:error_code, :error_name)
    """, errors)
    # TODO: if error_code not in error_codes, then add it
    cursor.executemany('''
        INSERT INTO errors (error_code, log_id, line_num, failed, filename)
        VALUES (:error_code, :log, :line_num, :failed, :filename)
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
            filename TEXT,
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
                    logger.error('Unexpected end to logfile %s (not finished or paused)', filename)
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
                    try:
                        db_write_stats(conn, stats)
                    except sqlite3.Error as ex:
                        logger.error('Writing stats for log %s to DB; %s', filename, ex)
                else:
                    # We do not expect to get stats when robo didn't finish
                    if log['finished'] or log['finished'] is None:
                        logger.error('No stats for log %s', filename)
            except Exception as ex:
                # overly broad ecception catching.  I don't care what happened, I want to log the error, and continue
                logger.error('Unexpected exception processing log file: %s, exception: %s',
                    filename, ex)


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
    # Current Status
    # Last error by Park
    # All Errors by Park
    # Speed Statistics by Park, last week, month, year, arbitrary period
    # Speed Comparison by Park, no updates, small, medium and large updates
    # Files updated per date
    # ...

    q1 = "select l.park, l.date, s.* from stats as s join logs as l on l.log_id = s.log_id where s.stat = 'dirs' and l.park = 'DENA' and l.errors is null order by l.date;"
    q2 = "select date, count(*) from logs group by date order by date;"
    q3 = "select park,date,errors from logs where errors is not null order by park,date;"
    q4 = "select park,date,errors from logs where finished = 0 order by park,date;"
    q5 = "select l.date, s.total, count(*), min(l.park), max(l.park) from stats as s join logs as l on l.log_id = s.log_id where s.stat = 'files' group by l.date, s.total;"
    q6 = """select l.date, max(s.copied) as copied, max(s.extra) as deleted, max(s.failed) as failed,
            max(s.mismatch) as mismatch, count(*)
            from stats as s join logs as l on l.log_id = s.log_id
            where s.stat = 'files' and errors is null and finished = 1 group by l.date;"""
    q7 = """select l.date, l.park, l.finished, s.failed, s.mismatch, l.errors
            from stats as s join logs as l on l.log_id = s.log_id
            where s.stat = 'files' and (s.failed > 0 OR s.mismatch > 0) order by l.date, l.park;"""
    with sqlite3.connect(db_name) as conn:
        for q in [q1, q2, q3, q4, q5, q6, q7]:
            print(db_get_rows(conn, q))


if __name__ == '__main__':
    #db_testing(':memory:')
    #clean('data/logs.db')
    main('data/logs.db', 'data/Logs/old')
    #print(process_park('./LogProcessor/Logs/2018-11-07_22-00-02-KLGO-update-x-drive.log'))

    # TODO: collect log file name (for backup and error details)
    # TODO: Re-run data collection, check logging
    # TODO: Option to clear/reprocess  a given day or day/park
