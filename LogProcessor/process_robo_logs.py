from __future__ import absolute_import, division, print_function, unicode_literals
import datetime
import glob
import logging
import os
import re
import sqlite3
import time
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
    if 'ERROR 2 (0x00000002)' in line:
        if 2 not in errors:
            errors.append(2)
            logger.error('%s: The system cannot find the file specified.', park)
    elif 'ERROR 5 (0x00000005)' in line:
        #TODO: if we do not find 'ERROR: RETRY LIMIT EXCEEDED.' in a future line, then ignore
        if 5 not in errors:
            errors.append(5)
            logger.error('%s: Access is denied.', park)
    # ERROR 19 (0x00000013) The media is write protected.
    # TODO: if we do not find 'ERROR: RETRY LIMIT EXCEEDED.' in a future line, then ignore
    # The happened on a KENNECOTT few files, then we got error 53 (unreachable)
    elif 'ERROR 21 (0x00000015)' in line:
        #TODO: if we do not find 'ERROR: RETRY LIMIT EXCEEDED.' in a future line, then ignore
        if 21 not in errors:
            errors.append(21)
            logger.error('%s: The device is not ready.', park)
    elif 'ERROR 32 (0x00000020)' in line:
        if 32 not in errors:
            errors.append(32)
            logger.warning('%s: File is locked', park)
    elif 'ERROR 53 (0x00000035)' in line:
        #TODO: if we do not find 'ERROR: RETRY LIMIT EXCEEDED.' in a future line, then ignore
        if 53 not in errors:
            errors.append(53)
            logger.error('Remote server %s unreachable', park)
    elif 'ERROR 59 (0x0000003B)' in line:
        if 59 not in errors:
            errors.append(59)
            logger.warning('%s: An unexpected network error occurred.', park)
    # ERROR 64 (0x00000040) The specified network name is no longer available.
    # Happened once at DENA (5/15/18) could not find folder.  Retried a few times, then ok
    # ERROR 67 (0x00000043) The network name cannot be found.
    # TODO: if we do not find 'ERROR: RETRY LIMIT EXCEEDED.' in a future line, then ignore
    # Happened when KLGO renamed the server without telling us.  Junction point had bad server name
    elif 'ERROR 121 (0x00000079)' in line:
        #TODO: if we do not find 'ERROR: RETRY LIMIT EXCEEDED.' in a future line, then ignore
        #TODO: This is often found with Error 32, consolidate, and write file name to log
        if 121 not in errors:
            errors.append(121)
            logger.warning('%s: The semaphore timeout period has expired.', park)
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

def db_clear(db, drop=True):
    try:
        cursor = db.cursor()
        if drop:
            cursor.execute('DROP INDEX IF EXISTS logs_date_ix')
            cursor.execute('DROP TABLE IF EXISTS logs')
            cursor.execute('DROP TABLE IF EXISTS stats')
        else:
            cursor.execute('DELETE FROM logs')
            cursor.execute('DELETE FROM stats')
        db.commit()
    except sqlite3.OperationalError:
        pass


def db_write_stats(db, stats):
    cursor = db.cursor()
    cursor.executemany('''
        INSERT INTO stats (log_id, stat, copied, extra, failed, mismatch, skipped, total)
        VALUES (:log, :stat, :copied, :extra, :failed, :mismatch, :skipped, :total)
    ''', stats)
    db.commit()


def db_write_log(db, log):
    cursor = db.cursor()
    cursor.execute('''
        INSERT INTO logs (park, date, finished, errors)
        VALUES (:name, :date, :finished, :errors)
    ''', log)
    log_id = cursor.lastrowid
    db.commit()
    return log_id


def db_get_rows(db, sql):
    cursor = db.cursor()
    rows = cursor.execute(sql).fetchall()
    return rows


def db_create(db):
    cursor = db.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs(
            log_id INTEGER PRIMARY KEY,
            park TEXT,
            date TEXT,
            finished INTEGER,
            errors TEXT);
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
            FOREIGN KEY(log_id) REFERENCES logs(artistid));
    ''')
    db.commit()


def park(filename):
    pattern = '([A-Z]{4})'
    return re.search(pattern, filename).group()


def get_files(dir,year,month,day):
    template = '{0}-{1:02d}-{2:02d}*-update-x-drive.log'
    pattern = os.path.join(dir, template.format(year, month, day))
    #print(pattern)
    files = glob.glob(pattern)
    park_files = [(park(name), name) for name in files]
    return park_files


def main(db_name, log_folder):
    # TODO: if yesterdays logs are not found, then log an email error
    # import glob
    # filelist = glob.glob('data/Logs/*-update-x-drive.log')
    # today = datetime.date.today()
    # filelist = get_files('./LogProcessor/Logs', today.year, today.month, today.day-1)
    # filelist = ['data/Logs/2018-02-12_22-00-01-DENA-update-x-drive.log']
    filelist = glob.glob(os.path.join(log_folder, '*-update-x-drive.log'))
    with sqlite3.connect(db_name) as conn:
        for filename in filelist:
            print(filename)
            # TODO protect against Parsing errors
            log = process_park(filename)
            if not log:
                print("EEK, Programming Error! The log object is empty")
                #TODO email log
                continue
            for item in ['name', 'date', 'finished', 'errors']:
                if item not in log:
                    print("EEK, Programmingh Error! we got a bad log object " + item + " is missing")
                    #TODO email log
                    continue
            log['errors'] = str(log['errors']) if log['errors'] else None
            # TODO protect against DB errors
            log_id = db_write_log(conn, log)
            if not log_id:
                print("EEK, unable to write log to database")
                #TODO email log
                continue
            if log['finished']:
                # We do not expect to get stats when the robo didn't finish
                if 'stats' in log:
                    stats = []
                    for stat in ['dirs','files','bytes','times']:
                        if stat not in log['stats']:
                            print("EEK, Programming Error! We got a bad stats object, missing: " + stat)
                            #TODO email log
                            continue
                        obj = log['stats'][stat]
                        for item in ['copied', 'extra', 'failed', 'mismatch', 'skipped', 'total']:
                            if item not in obj:
                                print("EEK, Programming Error! we got a bad stats object " + stat + "/" + item + " is missing")
                                #TODO email log
                                continue
                        obj['log'] = log_id
                        obj['stat'] = stat
                        stats.append(obj)
                    # TODO protect against DB errors
                    db_write_stats(conn, stats)
                else:
                    print("EEK!  No stats for this file.")
                    # Example in ./LogProcessor/Logs/2018-11-07_22-00-02-KLGO-update-x-drive.log
                    # ./LogProcessor/Logs/2018-10-02_22-00-03-NOME-update-x-drive.log
                    # data/Logs/Old/2018-10-01_22-00-07-KATM-update-x-drive.log
                    # data/Logs/Old/2018-05-14_22-00-02-KATM-update-x-drive.log
                    # data/Logs/Old/2018-09-28_22-00-04-NOME-update-x-drive.log
                    # data/Logs/Old/2018-03-27_22-00-02-KOTZ-update-x-drive.log
                    # data/Logs/Old/2018-05-16_22-00-03-KATM-update-x-drive.log
                    # data/Logs/Old/2018-03-26_22-00-02-NOME-update-x-drive.log
                    #
                    #TODO: log an email error


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
        for q in [q1, q2, q3, q4, q5]:
            print(db_get_rows(conn, q))


if __name__ == '__main__':
    #db_testing(':memory:')
    #clean('logs.db')
    main('data/logs.db', 'data/Logs/Old')
    #print(process_park('./LogProcessor/Logs/2018-11-07_22-00-02-KLGO-update-x-drive.log'))

    # TODO: Add Logging
    # TODO: add all error cases
    # TODO: collect additional error details
    # TODO: collect log file name (for backup and error details)
    # TODO: Re-run data collection, check logging
    # TODO: Option to clear/reprocess  a given day or day/park
