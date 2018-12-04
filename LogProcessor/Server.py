__author__ = 'RESarwas'

import sqlite3
# import ssl
import json

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
        if self.path == '/summary':
            sql = """
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
            with sqlite3.connect(self.db_name) as db:
                try:
                    resp = self.db_get_one(db, sql)
                    self.std_response(resp)
                except Exception as ex:
                    self.err_response(ex.message)

        elif self.path == '/help':
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

    def db_get_rows(self, db, sql, header=True):
        cursor = db.cursor()
        rows = cursor.execute(sql).fetchall()
        if header:
            return [[item[0] for item in cursor.description]] + rows
        else:
            return rows

    def db_get_one(self, db, sql):
        cursor = db.cursor()
        row = cursor.execute(sql).fetchone()
        header = [item[0] for item in cursor.description]
        # types = [item[1] for item in cursor.description]
        results = {}
        for i in range(len(row)):
            results[header[i]] = row[i]
        return results


# Next line is for an insecure (http) service
server = HTTPServer(('', 8080), SyncHandler)
# Next two lines are for a secure (https) service
#server = HTTPServer(('', 8443), SyncHandler)
#server.socket = ssl.wrap_socket (server.socket, keyfile='key.pem', certfile='cert.pem', server_side=True)
# For more info on https see: https://gist.github.com/dergachev/7028596
server.serve_forever()
