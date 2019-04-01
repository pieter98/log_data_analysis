from http.server import BaseHTTPRequestHandler, HTTPServer
from cgi import parse_header, parse_multipart
from urllib.parse import parse_qs, urlparse
from http.server import BaseHTTPRequestHandler
from my_enums import WorkshopType
import json
import numpy as np
from utils import AnalysisUtils


def makeProcessingServerHandler(database_connection):
    class ProcessingServerHandler(BaseHTTPRequestHandler):
        code_trees = []
        def __init__(self, *args, **kwargs):
            self.database_connection = database_connection
            print(database_connection.get_ordered_session_ids())
            self.code_trees.append(np.load("./files/xml_trees_for_session0.npy").tolist())
            self.code_trees.append(np.load("./files/xml_trees_for_session1.npy").tolist())
            super(ProcessingServerHandler, self).__init__(*args, **kwargs)

        def _set_headers(self):
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-type', 'text/html')
            self.end_headers()

        def do_GET(self):
            self._set_headers()
            print("GET")
            print(self.path)
            if self.path == "/sessionIdList":
                session_list = self.database_connection.get_ordered_session_ids()
                json_string_session_list = json.dumps(session_list)
                print(json_string_session_list)
                self.wfile.write(json_string_session_list.encode())
            elif urlparse(self.path).path == "/eventsfor":
                query = parse_qs(urlparse(self.path).query)
                kwargs = dict()
                keys = query.keys()
                if "start_date" in keys:
                    print(query["start_date"])
                    kwargs["start_date"] = int(query["start_date"][0])
                if "end_date" in keys:
                    kwargs["end_date"] = int(query["end_date"][0])
                if "workshop_type" in keys:
                    w_type = int(query["workshop_type"][0])
                    if w_type in [0, 1]:
                        kwargs["workshop_type"] = WorkshopType(int(query["workshop_type"][0]))
                if "session_id" in keys:
                    kwargs["session_id"] = query["session_id"][0]
                print(kwargs)
                query_result = self.database_connection.get_code_trees_for(**{k: v for k, v in kwargs.items() if v is not None})
                self.wfile.write(json.dumps(query_result).encode())
            # Load the clustering data results
            elif urlparse(self.path).path == "/evaluate_clustering":
                print("loading clustering results")
                query = parse_qs(urlparse(self.path).query)
                kwargs = dict()
                keys = query.keys()
                if "session" in keys:
                    print(query["session"])
                    kwargs["session"] = int(query["session"][0])
                print(kwargs)
                loaded_trees = np.load("./files/session" + str(kwargs["session"]) + ".npy").tolist()
                loaded_session_ids = np.load("./files/graph_session_ids_for_session" + str(kwargs["session"]) + ".npy").tolist()
                utils = AnalysisUtils()
                normalized_loaded_session_ids = utils.normalize_session_id_list(loaded_session_ids)
                print(len(set(normalized_loaded_session_ids)))
                packed_data = list(zip(loaded_trees, normalized_loaded_session_ids, loaded_session_ids))
                print("loaded trees")
                print(loaded_trees)
                json_string = json.dumps(packed_data).encode()
                self.wfile.write(json_string)
            elif urlparse(self.path).path == "/get_code_tree_for_index":
                print("loading clustering results")
                query = parse_qs(urlparse(self.path).query)
                kwargs = dict()
                keys = query.keys()
                if "index" in keys:
                    print(query["index"])
                    kwargs["index"] = int(query["index"][0])
                if "session" in keys:
                    print(query["session"])
                    kwargs["session"] = int(query["session"][0])
                print(kwargs)
                self.wfile.write(json.dumps(self.code_trees[kwargs["session"]][kwargs["index"]]).encode())
            else:
                self.wfile.write("<html><body><h1>hi!</h1></body></html>".encode())

        def do_HEAD(self):
            self._set_headers()

        def do_POST(self):
            postvars = self.parse_POST()
            self._set_headers()
            self.wfile.write("<html><body><h1>POST!</h1></body></html>".encode())

        def parse_POST(self):
            ctype, pdict = parse_header(self.headers['content-type'])
            if ctype == 'multipart/form-data':
                postvars = parse_multipart(self.rfile, pdict)
            elif ctype == 'application/x-www-form-urlencoded':
                length = int(self.headers['content-length'])
                postvars = parse_qs(
                    self.rfile.read(length),
                    keep_blank_values=1)
            else:
                postvars = {}
            return postvars
    return ProcessingServerHandler


class ProcessingServer:

    def run(self, database_connection, port=20042):
        server_address = ('', port)
        HandlerClass = makeProcessingServerHandler(database_connection)
        httpd = HTTPServer(server_address, HandlerClass)
        print('Starting httpd server to access blockly log database...')
        httpd.serve_forever()
