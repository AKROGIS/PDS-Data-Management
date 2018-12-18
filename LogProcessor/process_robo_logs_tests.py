from __future__ import absolute_import, division, print_function, unicode_literals
"""
routines for testing the process for parsing and processing log files
"""

import glob
import os
import sqlite3
import process_robo_logs

#LOG_ROOT = 'E:/XDrive/Logs'
LOG_ROOT = 'data/Logs/old'

r"""
Error Formating

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

Other Weird files
=================
    Parsing errors:
        2018-10-22_22-00-02-KLGO-update-x-drive.log: line 23 was retying a semaphore error, and then printed stats
        2018-10-25_22-00-02-KLGO-update-x-drive.log: line 720 was retying a semaphore error, and then printed stats
    When robocopy fail file count does not equal my failed error count:
        All but the following cases are with error 32 not being counted as a fail by robocopy,
        but I count it (a remote file that can't be deleted); mostly this is lock files at DENA,
        or files at KLGO after a semaphore (121) error
      2018-11-20_22-00-02-KLGO-update-x-drive.log: line 147, a semaphore (121) error is not retried is not retired, so I call it a fail, robo does not
      2018-11-22_22-00-02-KLGO-update-x-drive.log: Got 357 hard (ERROR: RETRY LIMIT EXCEEDED.) fails (I only couned 351), but robo only counted 76 (and 14 dirs)
      NOME|2018-05-19|150|77
      KOTZ|2018-07-02|9|8
"""


def test_file_structure(log_folder):
    """
        Line types (in body, i.e. not header or stats):
        clean_line = line.strip()
        * blank: not clean_line
        * file: clean_line.startswith('E:\\') or clean_line.startswith(r'\\inpak')
        * error: ' ERROR ' in clean_line
        * error name: always follows error line
        * retry: clean_line.endswith('... Retrying...')
        * fail: clean_line == 'ERROR: RETRY LIMIT EXCEEDED.'
        * pause: clean_line.startswith('Hours : Paused at')
        * divider: clean_line.startswith('-------------')  # at end of header before stats (and around title)
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
                p2_line = previous_line
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
                            p2_line = previous_line
                            previous_line = 'divider1'
                            continue
                        if not in_header and divider_line:
                            # start stats (verify)
                            file_handle.next() # blankline
                            stats_line = file_handle.next().strip()
                            if not stats_line.startswith('Total'):
                                print('fail in stats in {0}'.format(filename))
                            line_type = 'divider2'
                            # key = (previous_line,line_type)
                            key = (p2_line, previous_line,line_type)
                            if key not in relations:
                                relations[key] = 0
                            relations[key] += 1
                            p2_line = previous_line
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
                        # key = (previous_line,line_type)
                        key = (p2_line, previous_line,line_type)
                        if key not in relations:
                            relations[key] = 0
                        relations[key] += 1
                        p2_line = previous_line
                        previous_line = line_type
                    except Exception as ex:
                        print('exception {2} at line {0} in {1}'.format(line_num, filename, ex))
                # key = (previous_line, 'EOF')
                key = (p2_line, previous_line, 'EOF')
                if key not in relations:
                    relations[key] = 0
                relations[key] += 1
        except Exception as ex:
            print('exception {1} in {0}'.format(filename, ex))
    keys = sorted(errors.keys())
    for key in keys:
        print('  {0} => {1}'.format(key, errors[key]))
    keys = sorted(relations.keys())
    for key in keys:
        print('  {0} => {1}'.format(key, relations[key]))




def db_testing(db_name):
    with sqlite3.connect(db_name) as conn:
        process_robo_logs.db_create(conn)
        log_id = process_robo_logs.db_write_log(conn,
            #{'name':'DENA', 'date':'2018-02-12', 'finished':True, 'errors':None}
            {'name':'DENA', 'date':'2018-02-12', 'finished':True, 'errors':str(['e1','e2']), 'junk':5}
        )
        process_robo_logs.db_write_stats(conn,
            [
                {'log':log_id, 'stat': u'dirs', u'skipped': 3, u'extra': 2, u'mismatch': 0, u'failed': 0, u'copied': 0, u'total': 4711},
                {'log':log_id, 'stat': u'files', u'skipped': 234433, u'extra': 0, u'mismatch': 0, u'failed': 0, u'copied': 0, u'total': 234433},
                {'log':log_id, 'stat': u'bytes', u'skipped': 557141000000, u'extra': 0, u'mismatch': 0, u'failed': 0, u'copied': 0, u'total': 557141000000},
                {'log':log_id, 'stat': u'times', u'skipped': 0, u'extra': 212, u'mismatch': 0, u'failed': 0, u'copied': 0, u'total': 212}
            ]
        )
        sql = 'SELECT * FROM stats JOIN logs on stats.log_id = logs.log_id;'
        print(db_get_rows(conn, sql))
        process_robo_logs.db_clear(conn)
        print(db_get_rows(conn, sql))


def db_get_rows(db, sql, header=True):
    cursor = db.cursor()
    rows = cursor.execute(sql).fetchall()
    if header:
        return [[item[0] for item in cursor.description]] + rows
    else:
        return rows


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
    #db_testing(':memory:')
    #test_queries(db)
    #test_file_structure(r"\\inpakrovmais\Xdrive\Logs\2018archive")
    test_file_structure(r"data/Logs/old")
