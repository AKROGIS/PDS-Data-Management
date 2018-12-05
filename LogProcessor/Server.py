from __future__ import absolute_import, division, print_function, unicode_literals
import datetime
import json
import sqlite3
# import ssl
import urlparse
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer


class SyncHandler(BaseHTTPRequestHandler):
    db_name = 'data/logs.db'
    name = "Xdrive RoboCopy Log Details"
    usage = "Usage:\n" + \
            "\tPOST with /sync with a zip containing the protocol and CSV files\n" + \
            "\tGET with /dir to list the databases\n" + \
            "\tGET with /load to show a form to upload a zip file\n" + \
            "\tGET with /error to list the error log file\n" +\
            "\tGET with /help for this message\n"

    def do_GET(self):
        path_parts = urlparse.urlparse(self.path)
        params = urlparse.parse_qs(path_parts.query)
        sql_params = []
        if path_parts.path == '/summary':
            sql = """
                SELECT l.date,
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
                LEFT JOIN (SELECT log_id, COUNT(*) AS count_errors FROM errors GROUP BY log_id) AS e ON l.log_id = e.log_id
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
                LEFT JOIN (select log_id, COUNT(*) AS count_errors FROM errors group by log_id) AS e ON l.log_id = e.log_id
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


# Next line is for an insecure (http) service
server = HTTPServer(('', 8080), SyncHandler)
# Next two lines are for a secure (https) service
#server = HTTPServer(('', 8443), SyncHandler)
#server.socket = ssl.wrap_socket (server.socket, keyfile='key.pem', certfile='cert.pem', server_side=True)
# For more info on https see: https://gist.github.com/dergachev/7028596
server.serve_forever()
