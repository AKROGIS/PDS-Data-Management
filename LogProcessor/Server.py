from __future__ import absolute_import, division, print_function, unicode_literals
import datetime
import json
import os
import sqlite3
# import ssl
import urlparse
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

LOG_DB = 'E:/XDrive/Logs/logs.db'
#LOG_DB = r'\\inpakrovmais\XDrive\Logs\logs.db'
#LOG_DB = 'data/logs.db'

class SyncHandler(BaseHTTPRequestHandler):
    db_name = LOG_DB
    name = "Xdrive RoboCopy Log Details"
    usage = "Usage:\n" + \
            "\tGET with /summary or summary?date=YYYY-MM-DD to get the log summary\n" + \
            "\tGET with /parks or parks?date=YYYY-MM-DD to get the log details for all parks\n" + \
            "\tGET with /plot1 or plot1?date=YYYY-MM-DD to get data for a speed comparison of all parks\n" + \
            "\tGET with /dates to get the min and max date of the logs in the database\n" +\
            "\tGET with /help for this message\n"

    def do_GET(self):
        path_parts = urlparse.urlparse(self.path)
        params = urlparse.parse_qs(path_parts.query)
        sql_params = []
        if path_parts.path == '/summary':
            sql = """
                SELECT l.date AS summary_date,
                MAX(sf.total) AS files_scanned, MAX(sd.total) AS dirs_scanned,
                MAX(sf.copied) AS files_copied, MAX(sf.extra) AS files_removed,
                MAX(sb.copied) AS bytes_copied, MAX(sb.extra) AS bytes_removed,
                SUM(e.count_errors) AS total_errors,
                COUNT(l1.park) AS count_complete,
                COUNT(l2.park) AS count_incomplete,
                COUNT(l3.park) AS count_unfinished
                FROM logs AS l
                LEFT JOIN stats AS sf ON l.log_id = sf.log_id and sf.stat = 'files' AND l.park <> 'DENA'
                LEFT JOIN stats AS sd ON l.log_id = sd.log_id and sd.stat = 'dirs' AND l.park <> 'DENA'
                LEFT JOIN stats AS st ON l.log_id = st.log_id and st.stat = 'times' AND l.park <> 'DENA'
                LEFT JOIN stats AS sb ON l.log_id = sb.log_id and sb.stat = 'bytes' AND l.park <> 'DENA'
                LEFT JOIN logs AS l1 ON l.log_id = l1.log_id and l1.finished = 1
                LEFT JOIN logs AS l2 ON l.log_id = l2.log_id and l2.finished = 0
                LEFT JOIN logs AS l3 ON l.log_id = l3.log_id and l3.finished IS NULL
                LEFT JOIN (SELECT log_id, COUNT(*) AS count_errors FROM errors where failed GROUP BY log_id) AS e ON l.log_id = e.log_id
                WHERE l.date = (SELECT MAX(date) FROM logs)
                GROUP BY l.date;
            """
            if 'date' in params and len(params['date']) == 1:
                date = params['date'][0]
                date = self.sanitize_date(date)
                if date:
                    sql = sql.replace('WHERE l.date = (SELECT MAX(date) FROM logs)','WHERE l.date = ?')
                    sql_params = [date]
                else:
                    self.err_response('Bad date request')
                    return
            with sqlite3.connect(self.db_name) as db:
                try:
                    resp = self.db_get_one(db, sql, sql_params)
                    self.std_response(resp)
                except Exception as ex:
                    self.err_response(ex.message)

        elif path_parts.path == '/parks':
            sql = """
                SELECT l.park, l.date, l.finished,
                COALESCE(e.count_errors, 0) AS count_errors,
                sf.copied AS files_copied, sf.extra AS files_removed, sf.total AS files_scanned,
                st.copied AS time_copying, st.extra AS time_scanning, sb.copied AS bytes_copied
                FROM logs AS l
                LEFT JOIN stats AS sf ON l.log_id = sf.log_id and sf.stat = 'files'
                LEFT JOIN stats AS st ON l.log_id = st.log_id and st.stat = 'times'
                LEFT JOIN stats AS sb ON l.log_id = sb.log_id and sb.stat = 'bytes'
                LEFT JOIN (select log_id, COUNT(*) AS count_errors FROM errors where failed group by log_id) AS e ON l.log_id = e.log_id
                WHERE l.date = (SELECT MAX(date) FROM logs)
                ORDER BY l.park;
            """
            if 'date' in params and len(params['date']) == 1:
                date = params['date'][0]
                date = self.sanitize_date(date)
                if date:
                    sql = sql.replace('WHERE l.date = (SELECT MAX(date) FROM logs)','WHERE l.date = ?')
                    sql_params = [date]
                else:
                    self.err_response('Bad date request')
                    return
            with sqlite3.connect(self.db_name) as db:
                try:
                    resp = self.db_get_rows(db, sql, sql_params)
                    self.std_response(resp)
                except Exception as ex:
                    self.err_response(ex.message)

        elif path_parts.path == '/logfile':
            sql = "SELECT filename FROM logs WHERE date = ? AND park = ?"
            date = None
            if 'date' in params and len(params['date']) == 1:
                date = params['date'][0]
                date = self.sanitize_date(date)
            park = None
            if 'park' in params and len(params['park']) == 1:
                park = params['park'][0]
            filename = None
            if park and date:
                sql_params = [date, park]
                with sqlite3.connect(self.db_name) as db:
                    try:
                        resp = self.db_get_one(db, sql, sql_params)
                        if resp and 'filename' in resp:
                            filename = resp['filename']
                    except Exception as ex:
                        self.err_response(ex.message)
                        return
            if filename:
                filename = os.path.basename(filename)
                folder = os.path.dirname(LOG_DB)
                archive = date[:4] + 'archive'
                filename = os.path.join(folder, archive, filename)
                if os.path.exists(filename):
                    self.file_response(filename)
                else:
                    msg = 'log file {0} not found'.format(filename)
                    self.err_response(msg)
            else:
                msg = 'No log file for date {0}, park {1}'.format(date, park)
                self.err_response(msg)

        elif path_parts.path == '/dates':
            sql = """
                SELECT
                MIN(date) as first_date,
                MAX(date) as last_date
                FROM logs;
            """
            with sqlite3.connect(self.db_name) as db:
                try:
                    resp = self.db_get_one(db, sql)
                    self.std_response(resp)
                except Exception as ex:
                    self.err_response(ex.message)

        elif path_parts.path == '/plot1':
            sql = """
                SELECT l.park,
                COALESCE(round(1.0*sf.total/st.extra, 1), 0) AS scan_speed,
                COALESCE(round(sb.copied/st.copied/1000.0, 1), 0) AS copy_speed
                FROM logs AS l
                LEFT JOIN stats AS sf ON l.log_id = sf.log_id and sf.stat = 'files'
                LEFT JOIN stats AS st ON l.log_id = st.log_id and st.stat = 'times'
                LEFT JOIN stats AS sb ON l.log_id = sb.log_id and sb.stat = 'bytes'
                WHERE l.date = (SELECT MAX(date) FROM logs)
                ORDER BY l.park;
            """
            if 'date' in params and len(params['date']) == 1:
                date = params['date'][0]
                date = self.sanitize_date(date)
                if date:
                    sql = sql.replace('WHERE l.date = (SELECT MAX(date) FROM logs)','WHERE l.date = ?')
                    sql_params = [date]
                else:
                    self.err_response('Bad date request')
                    return
            with sqlite3.connect(self.db_name) as db:
                try:
                    resp = self.db_get_rows(db, sql, sql_params, False)
                    self.std_response(resp)
                except Exception as ex:
                    self.err_response(ex.message)

        elif path_parts.path == '/scanavg':
            sql = """
                SELECT l.park,
                ROUND(AVG(1.0*sf.total/st.extra), 1) AS avg_scan_speed,
                COUNT(*) AS CNT
                FROM logs AS l
                LEFT JOIN stats AS sf ON l.log_id = sf.log_id and sf.stat = 'files'
                LEFT JOIN stats AS st ON l.log_id = st.log_id and st.stat = 'times'
                LEFT JOIN errors AS e ON l.log_id = e.log_id
                WHERE e.log_id IS NULL
                AND st.extra > 0 AND sf.total > 0
                AND l.date > ?
                GROUP BY l.park
                ORDER BY l.park;
            """
            if 'date' in params and len(params['date']) == 1:
                date = params['date'][0]
                date = self.sanitize_date(date)
                if date:
                    sql_params = [date]
                else:
                    self.err_response('Bad date request')
                    return
            else:
                sql = sql.replace('AND l.date > ?','')
            with sqlite3.connect(self.db_name) as db:
                try:
                    resp = self.db_get_rows(db, sql, sql_params, False)
                    self.std_response(resp)
                except Exception as ex:
                    self.err_response(ex.message)

        elif path_parts.path == '/copyavg':
            sql = """
                SELECT l.park,
                ROUND(AVG(1.0*sb.copied/st.copied/1000.0), 1) AS avg_copy_speed,
                COUNT(*) AS CNT
                FROM logs AS l
                LEFT JOIN stats AS st ON l.log_id = st.log_id and st.stat = 'times'
                LEFT JOIN stats AS sb ON l.log_id = sb.log_id and sb.stat = 'bytes'
                LEFT JOIN errors AS e ON l.log_id = e.log_id
                WHERE e.log_id IS NULL
                AND st.copied > 0 AND sb.copied > 0
                AND l.date > ?
                GROUP BY l.park
                ORDER BY l.park;
            """
            if 'date' in params and len(params['date']) == 1:
                date = params['date'][0]
                date = self.sanitize_date(date)
                if date:
                    sql_params = [date]
                else:
                    self.err_response('Bad date request')
                    return
            else:
                sql = sql.replace('AND l.date > ?','')
            with sqlite3.connect(self.db_name) as db:
                try:
                    resp = self.db_get_rows(db, sql, sql_params, False)
                    self.std_response(resp)
                except Exception as ex:
                    self.err_response(ex.message)

        elif path_parts.path == '/speed':
            sql = """
                SELECT l.park, l.date,
                ROUND(1.0*sf.total/st.extra, 1) AS scan_speed,
                ROUND(1.0*sb.copied/st.copied/1000.0, 1) AS copy_speed,
                ROUND(1.0*sb.copied/sf.copied/1000.0, 1) AS avg_size_kb,
                sf.copied as files,
                ROUND(sb.copied/1000.0/1000.0, 2) as MBytes
                FROM logs AS l
                LEFT JOIN stats AS sf ON l.log_id = sf.log_id and sf.stat = 'files'
                LEFT JOIN stats AS st ON l.log_id = st.log_id and st.stat = 'times'
                LEFT JOIN stats AS sb ON l.log_id = sb.log_id and sb.stat = 'bytes'
                LEFT JOIN errors AS e ON l.log_id = e.log_id
                WHERE e.log_id IS NULL
                AND l.date > ?
                AND l.date < ?
                AND l.park = ?
                ORDER BY l.park, l.date;
            """
            if 'start' in params and len(params['start']) == 1:
                date = params['start'][0]
                date = self.sanitize_date(date)
                if date:
                    sql_params.append(date)
                else:
                    self.err_response('Bad start date parameter')
                    return
            else:
                sql = sql.replace('AND l.date > ?','')
            if 'end' in params and len(params['end']) == 1:
                date = params['end'][0]
                date = self.sanitize_date(date)
                if date:
                    sql_params.append(date)
                else:
                    self.err_response('Bad end date parameter')
                    return
            else:
                sql = sql.replace('AND l.date < ?','')
            if 'park' in params and len(params['park']) == 1:
                park = params['park'][0]
                park = self.sanitize_park(park)
                if park:
                    sql_params.append(park)
                else:
                    self.err_response('Bad park parameter')
                    return
            else:
                sql = sql.replace('AND l.park = ?','')
            with sqlite3.connect(self.db_name) as db:
                try:
                    resp = self.db_get_rows(db, sql, sql_params, False)
                    self.std_response(resp)
                except Exception as ex:
                    self.err_response(ex.message)

        elif path_parts.path == '/help':
            self.std_response({'help': self.usage})
        else:
            self.err_response(self.usage)


    def std_response(self, obj):
        data = json.dumps(obj)
        self.send_response(200)
        self.send_header('Content-type', 'json')
        self.send_header('Content-length', len(data))
        self.end_headers()
        self.wfile.write(data)

    def file_response(self, filename):
        try:
            f = open(filename, 'rb')
            self.send_response(200)
            self.send_header('Content-type',    'text')
            self.end_headers()
            self.wfile.write(f.read())
            f.close()
        except IOError:
            self.send_error(404,'File Not Found: {0}'.format(filename))

    def err_response(self, message):
        data = json.dumps({'error': message})
        self.send_response(500)
        self.send_header('Content-type', 'json')
        self.send_header('Content-length', len(data))
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        if self.path == '/sync':
            self.err_response("not implemented")

    def end_headers (self):
        self.send_header('Access-Control-Allow-Origin', '*')
        BaseHTTPRequestHandler.end_headers(self)

    def db_get_rows(self, db, sql, params, header=True):
        cursor = db.cursor()
        rows = cursor.execute(sql, params).fetchall()
        if header:
            return [[item[0] for item in cursor.description]] + rows
        else:
            return rows

    def db_get_one(self, db, sql,params=[]):
        cursor = db.cursor()
        row = cursor.execute(sql, params).fetchone()
        header = [item[0] for item in cursor.description]
        # types = [item[1] for item in cursor.description]
        results = {}
        if row:
            for i in range(len(row)):
                results[header[i]] = row[i]
        return results


    def sanitize_date(self, s):
        try:
            date = datetime.datetime.strptime(s,'%Y-%m-%d')
        except ValueError:
            return None
        return date.strftime('%Y-%m-%d')


    def sanitize_park(self, s):
        parks = ['DENA','GLBA','KATM','KEFJ','KENN','KLGO','KOTZ','LACL','NOME',u'SEAN','SITK','WRST','YUGA']
        try:
            park = s.upper()
            if park not in parks:
                return None
        except ValueError:
            return None
        return park


# Next line is for an insecure (http) service
server = HTTPServer(('', 8080), SyncHandler)
# Next two lines are for a secure (https) service
#server = HTTPServer(('', 8443), SyncHandler)
#server.socket = ssl.wrap_socket (server.socket, keyfile='key.pem', certfile='cert.pem', server_side=True)
# For more info on https see: https://gist.github.com/dergachev/7028596
server.serve_forever()
