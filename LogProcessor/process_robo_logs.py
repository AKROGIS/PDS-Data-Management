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


def parse_error_line(line, filename, line_num):
    code = 0
    message = 'Message not defined'
    try:
        code = int(line.split(' ERROR ')[1].split()[0])
        message = line.split(') ')[1].strip()
    except Exception as ex:
        # overly broad ecception catching.  I don't care what happened, I want to log the error, and continue
        logger.error('Parsing error in log file: %s, line#: %d, line: %s, exception: %s',
            filename, line_num, line, ex)
    return code, message


def process_error(file_handle, filename, line, line_num):
    #TODO: Always check for error in new line
    error_sentinal = ' ERROR '
#    print(line_num, '|'+line+'|')
    code, message = parse_error_line(line, filename, line_num)
    name = 'Name of error not defined'
    failed = None # True if all the retries failed, False if retry succeeds, None if unable to determine due to unexpected input
    done = False
#    last_line_num = None # used to check for infinite loops
    while not done and code:
        try:
            # read name of error
            # The name line ends with 0x0D0D0A (\r\r\n), which python interprets as one line
            # but most text editors interpret as two lines
            line = file_handle.next()
            line_num += 1
#            print(line_num, '|'+line+'|')
            name = line.strip()
#            print('name |'+name+'|')
            # read blank line
#            line = file_handle.next()
            line_num += 1
#            print(line_num, '|'+line+'|')
#            content = line.strip()
#            print('content |'+content+'|',len(content))
#            if content:
#                print('WTF!!!!')
#                logger.error('Unexpected data on blank line after error in log file: %s, line#: %d, line: %s',
#                    filename, line_num, line)
#                done = True
#                continue
            # read retry line; could be blank if followed with RETRY FAILED
            line = file_handle.next()
            line_num += 1
#            print(line_num, '|'+line+'|')
            retry = line.strip()
#            print('retry |'+retry+'|')
            if retry.endswith('... Retrying...'):
                # Next line should be a task (skip it), then next line should be the same error, or the retry worked.
                # The task must be the same as the task before the errror, but there is no way to check it now.
                line = file_handle.next()
                line_num += 1
#                print(line_num, '|'+line+'|')
                task = line.strip()
#                print('task |'+task+'|')
                if not task:
                    logger.error('Unexpected blank line when expecting retry of failed task in log file: %s, line#: %d, line: %s',
                        filename, line_num, line)
                    done = True
                else:
                    line = file_handle.next()
                    line_num += 1
#                    print(line_num, '|'+line+'|')
                    if error_sentinal in line:
                        code, message = parse_error_line(line, filename, line_num)
                    else:
                        done = True
                        failed = False
                    # repeat while loop
            elif not retry:
                # blank line is ok, but next line must be ERROR: RETRY LIMIT EXCEEDED.
                line = file_handle.next()
                line_num += 1
#                print(line_num, '|'+line+'|')
                limit = line.strip()
#                print('limit |'+limit+'|')
                if limit == 'ERROR: RETRY LIMIT EXCEEDED.':
                    failed = True
                else:
                    logger.error('Unexpected data on blank line after retry in log file: %s, line#: %d, line: %s',
                        filename, line_num, line)
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
    """
                if last_line_num is None:
                    last_line_num = line_num
                else:
                    if last_line_num == line_num:
                        done = True
                    else:
                        last_line_num = line_num
    """

    error = {'code': code, 'failed': failed, 'name': name, 'line_num': line_num, 'message': message}
#    print(error, line, line_num)
    return error, line, line_num


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
                if error_sentinal in line:
                    error, line, line_num = process_error(file_handle, file_name, line, line_num)
                    results['errors'].append(error)
                    if error['failed'] is not None:
                        continue
                if line == summary_header:
                    summary, line_num = process_summary(file_handle, file_name, line_num)
                    results['stats'] = summary
                elif line.startswith(finished_sentinal):
                    results['finished'] = True
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
                        for attrib in ['code', 'failed', 'name', 'line_num', 'message']:
                            if attrib not in error:
                                logger.error('Bad errors object in log file %s, missing: %s in %s', filename, attrib, str(error))
                                continue
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
    q8 = "Select park, date, finished from logs where date = (SELECT max(date) from logs) ORDER BY Park;"
    q9 = "select filename from errors;"
    with sqlite3.connect(db_name) as conn:
        for q in [q9, q1, q2, q3, q4, q5, q6, q7, q8]:
            for row in db_get_rows(conn, q):
                # error = row[0].split(') ')[1].strip()
                # code = int(row[0].split(' ERROR ')[1].split()[0])
                # print('{0:3d}|{1}'.format(code,error))
                print(row)


if __name__ == '__main__':
    #db_testing(':memory:')
    #clean('data/logs.db')
    #main('data/logs.db', 'data/Logs')
    # main('data/logs.db', 'data/Logs/old')
    # test_queries('data/logs.db')
    #print(process_park('data/Logs/2018-11-07_22-00-02-KLGO-update-x-drive.log'))
    #res = process_park('data/Logs/2018-11-17_22-00-02-KLGO-update-x-drive.log')
    #res = process_park('data/Logs/2018-11-07_22-00-02-KLGO-update-x-drive.log')
    # process_park('data/Logs/2018-11-20_22-00-02-KLGO-update-x-drive.log')  # No retry after error, then success.
    # process_park('data/Logs/2018-10-25_22-00-02-KLGO-update-x-drive.log')  # retrying... Then stats (successful retry on last file))
    process_park('data/Logs/2018-10-17_22-00-13-DENA-update-x-drive.log')
    #process_park('data/Logs/2018-10-10_22-00-04-DENA-update-x-drive.log')
    #process_park('data/Logs/2018-10-16_22-00-03-KLGO-update-x-drive.log')
    #process_park('data/Logs/2018-10-11_22-00-03-DENA-update-x-drive.log')
    #process_park('data/Logs/2018-11-28_22-00-04-DENA-update-x-drive.log')
    #process_park('data/Logs/2018-10-02_22-00-03-DENA-update-x-drive.log')
    #process_park('data/Logs/2018-11-22_22-00-02-KLGO-update-x-drive.log')
    #print(res)

    # TODO: Option to clear/reprocess  a given day or day/park
    # TODO: Add command line options ?
