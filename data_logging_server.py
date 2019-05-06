"""Module for Blockly data logging."""
from pymongo import MongoClient
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs
import uuid
import json


class dataLoggerRequestHandler(BaseHTTPRequestHandler):
    """Handle incomming requests."""

    PORT = 8000

    def _set_headers(self):
        """Set headers, response 200."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        """Handle get."""
        # Print querystring
        parsedURL = self.path.split('?')

        method = parsedURL[0]
        print(method)

        if method == "/sessions/newId":
            self.handleGetNewId()
        else:
            self.send_response(500)

    def handleGetNewId(self):
        """Generate new session id and return it."""
        randomSessionId = uuid.uuid4().int
        self._set_headers()
        # Write content as utf-8 data
        self.wfile.write(bytes(str(randomSessionId), 'utf-8'))

    def do_POST(self):
        """Handle post."""
        # Print querystring
        parsedURL = self.path.split('?')

        method = parsedURL[0]
        print(method)

        if method == "/sessions/update":
            self.handleUpdateSession()
        else:
            self.send_response(500)

    def handleUpdateSession(self):
        """Read post data and log to database."""
        # print(self.headers)
        # CITATION: http://stackoverflow.com/questions/4233218/python-basehttprequesthandler-post-variables
        # Extract and print the contents of the POST
        length = int(self.headers['Content-Length'])
        post_data = parse_qs(self.rfile.read(length).decode('utf-8'))
        print(post_data)
        data = json.loads(post_data['logEntry'][0])
        print(data)
        self._set_headers()
        self.insertUpdate(data)

    def getDatabase(self):
        """Get the connection to the mongodb database."""
        client = MongoClient('localhost:27017')
        db = client.GeneratedDataLog
        return db

    def insertUpdate(self, data):
        """Insert an log element into the log collection."""
        db = self.getDatabase()
        coll = db.log
        coll.insert(data)

    @staticmethod
    def run():
        """Run the server."""
        print("Starting server")

        # Server settings
        # Choose port 8080, for port 80,
        # which is normally used for a http server, you need root access
        server_address = ('127.0.0.1', 8081)
        httpd = HTTPServer(server_address, dataLoggerRequestHandler)
        print('running server...')
        httpd.serve_forever()
