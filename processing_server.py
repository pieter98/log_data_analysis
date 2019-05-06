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
        cluster_pairs = []
        def __init__(self, *args, **kwargs):
            self.database_connection = database_connection
            print(database_connection.get_ordered_session_ids())
            self.close_connection = True
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
                else:
                    kwargs["session"] = ""
                if "experimentId" in query.keys():
                    print(query["experimentId"])
                    kwargs["experimentId"] = query["experimentId"][0]
                else:
                    kwargs["experimentId"] = ""
                print(kwargs)
                cluster_pairs = []
                # Load nearby cluster pair centroids
                cluster_pairs.append(np.load("./files/nearby_cluster_pair_points" + kwargs["experimentId"] + ".npy").tolist())
                # Load the t_sne embedding data points
                loaded_trees = np.load("./files/session" + kwargs["experimentId"] + ".npy").tolist()
                # Load the identifier for each code tree which determines which coding session it belongs to
                loaded_session_ids = np.load("./files/graph_session_ids_for_session" + str(kwargs["experimentId"]) + ".npy").tolist()
                # Load the ground truth labels for each code tree.
                labels = np.load("./files/labels" + kwargs["experimentId"] + ".npy").tolist()
                if len(labels) == 0:
                    labels = np.zeros(10000)

                utils = AnalysisUtils()
                normalized_loaded_session_ids = utils.normalize_session_id_list(loaded_session_ids)
                max_elements = 2400

                nr_of_trees = len(loaded_trees)
                packed_data = list(zip(loaded_trees[0:max_elements], normalized_loaded_session_ids[0:max_elements], loaded_session_ids[0:max_elements], labels[0:max_elements]))
                packed_data = [packed_data, cluster_pairs]
                print("loaded trees")
                print(loaded_trees)
                json_string = json.dumps(packed_data).encode()
                self.wfile.write(json_string)
            elif urlparse(self.path).path == "/get_code_tree_for_index":
                query = parse_qs(urlparse(self.path).query)
                kwargs = dict()
                if "experimentId" in query.keys():
                    print(query["experimentId"])
                    kwargs["experimentId"] = query["experimentId"][0]
                else:
                    kwargs["experimentId"] = ""
                if "index" in query.keys():
                    print(query["index"])
                    kwargs["index"] = query["index"][0]
                else:
                    kwargs["index"] = 0

                print("loading clustering results")
                code_trees = []
                code_trees.append(np.load("./files/xml_trees_for_session" + kwargs["experimentId"] + ".npy").tolist())
                self.wfile.write(json.dumps(code_trees[0][int(kwargs["index"])]).encode())
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
