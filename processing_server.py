from http.server import BaseHTTPRequestHandler, HTTPServer
from cgi import parse_header, parse_multipart
from urllib.parse import parse_qs, urlparse
from http.server import BaseHTTPRequestHandler
from my_enums import WorkshopType
import json
import numpy as np
from my_enums import FunctionalDataset
from utils import AnalysisUtils


def makeProcessingServerHandler(database_connection):
    class ProcessingServerHandler(BaseHTTPRequestHandler):
        cluster_pairs = []
        max_points = 6000
        def __init__(self, *args, **kwargs):
            self.database_connection = database_connection
            print(database_connection.get_ordered_session_ids())
            self.close_connection = True
            super(ProcessingServerHandler, self).__init__(*args, **kwargs)

        def get_eventsfor(self):
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
            query_result = self.database_connection.get_code_trees_for(
                **{k: v for k, v in kwargs.items() if v is not None})
            return json.dumps(query_result).encode()

        def get_session_id_list(self):
            session_list = self.database_connection.get_ordered_session_ids()
            json_string_session_list = json.dumps(session_list)
            print(json_string_session_list)
            return json_string_session_list.encode()

        def get_evaluate_clustering(self):
            print("loading clustering results")
            query = parse_qs(urlparse(self.path).query)
            kwargs = dict()
            keys = query.keys()
            if "experimentId" in query.keys():
                print(query["experimentId"])
                kwargs["experimentId"] = query["experimentId"][0]
            else:
                kwargs["experimentId"] = ""
            print(kwargs)

            # Load nearby cluster pair centroids
            if kwargs["experimentId"] == "real_data_27-06-2019":
                cluster_pairs = np.array([])
            else:
                cluster_pairs = np.load("./files/nearby_cluster_pair_points" + kwargs["experimentId"] + ".npy").tolist()
            # Load the t_sne embedding data points
            loaded_trees = np.load("./files/session" + kwargs["experimentId"] + ".npy").tolist()
            # Load the identifier for each code tree which determines which coding session it belongs to
            '''loaded_session_ids = np.load(
                "./files/graph_session_ids_for_session" + str(kwargs["experimentId"]) + ".npy").tolist()'''
            # Load the ground truth labels for each code tree.
            labels = np.load("./files/labels" + kwargs["experimentId"] + ".npy").tolist()

            if len(labels) == 0:
                labels = np.zeros(10000)

            '''utils = AnalysisUtils()
            normalized_loaded_session_ids = utils.normalize_session_id_list(loaded_session_ids)'''
            max_elements = self.max_points

            nr_of_trees = len(loaded_trees)
            packed_data = list(zip(loaded_trees[0:max_elements], labels[0:max_elements]))
            packed_data = [packed_data, cluster_pairs]
            print("loaded trees")
            print(loaded_trees)
            json_string = json.dumps(packed_data).encode()
            return json_string

        def get_nr_of_trees(self):
            query = parse_qs(urlparse(self.path).query)
            kwargs = dict()
            if "experimentId" in query.keys():
                kwargs["experimentId"] = query["experimentId"][0]
            else:
                kwargs["experimentId"] = ""

            code_trees = []
            code_trees.append(np.load("./files/xml_trees_for_session" + kwargs["experimentId"] + ".npy").tolist())
            print("We have the following number of code trees")
            print(len(code_trees[0]))
            return json.dumps(len(code_trees[0])).encode()

        def get_code_tree_for_index(self):
            query = parse_qs(urlparse(self.path).query)
            kwargs = dict()
            if "experimentId" in query.keys():
                kwargs["experimentId"] = query["experimentId"][0]
            else:
                kwargs["experimentId"] = ""
            if "index" in query.keys():
                kwargs["index"] = int(query["index"][0])
            else:
                kwargs["index"] = 0

            print("loading clustering results for index:")
            print(kwargs["index"])
            code_trees = []
            code_trees.append(np.load("./files/xml_trees_for_session" + kwargs["experimentId"] + ".npy").tolist())
            code_tree_data = code_trees[0][kwargs["index"]]
            labels = np.load("./files/labels" + kwargs["experimentId"] + ".npy").tolist()
            if len(labels) == 0:
                labels = [0 for i in range(len(code_trees[0]))]
            return json.dumps([code_tree_data, labels[kwargs["index"]]]).encode()

        def get_reduced_vector_for_index(self):
            query = parse_qs(urlparse(self.path).query)
            kwargs = dict()
            if "experimentId" in query.keys():
                kwargs["experimentId"] = query["experimentId"][0]
            else:
                kwargs["experimentId"] = ""
            if "index" in query.keys():
                kwargs["index"] = int(query["index"][0])
            else:
                kwargs["index"] = 0
            reduced_vects = []
            reduced_vects.append(np.load("./files/reduced_vectors" + kwargs["experimentId"] + ".npy").tolist())
            reduced_vects_data = reduced_vects[0][kwargs["index"]]
            return json.dumps(reduced_vects_data).encode()


        def _set_headers(self):
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-type', 'text/html')
            self.end_headers()

        def do_GET(self):
            self._set_headers()
            if self.path == "/sessionIdList":
                self.wfile.write(self.get_session_id_list())
            elif urlparse(self.path).path == "/eventsfor":
                self.wfile.write(self.get_eventsfor())
            # Load the clustering data results
            elif urlparse(self.path).path == "/evaluate_clustering":
                self.wfile.write(self.get_evaluate_clustering())

            elif urlparse(self.path).path == "/get_nr_of_trees":
                self.wfile.write(self.get_nr_of_trees())

            elif urlparse(self.path).path == "/get_code_tree_for_index":
                self.wfile.write(self.get_code_tree_for_index())
            elif urlparse(self.path).path == "/get_reduced_vector_for_index":
                self.wfile.write(self.get_reduced_vector_for_index())


            else:
                self.wfile.write("<html><body><h1>hi!</h1></body></html>".encode())

        def do_HEAD(self):
            self._set_headers()


        def do_POST(self):
            postvars = self.parse_POST()
            self._set_headers()
            self.wfile.write("<html><body><h1>POST!</h1></body></html>".encode())

            if urlparse(self.path).path == "/save_functional_vector":
                query = postvars
                kwargs = dict()
                if "experimentId" in query.keys():
                    kwargs["experimentId"] = query["experimentId"]
                else:
                    kwargs["experimentId"] = ""
                if "xml_blocks" in query.keys():
                    kwargs["xml_blocks"] = query["xml_blocks"]
                else:
                    kwargs["xml_blocks"] = ""
                if "vector" in query.keys():
                    kwargs["vector"] = json.loads(query["vector"])
                else:
                    kwargs["vector"] = []
                if "label" in query.keys():
                    kwargs["label"] = int(query["label"])
                else:
                    kwargs["label"] = -1

                print("New vector")
                print(kwargs["vector"])

                self.database_connection.add_functional_log_entry(kwargs["experimentId"], kwargs["vector"], kwargs["xml_blocks"], kwargs["label"], FunctionalDataset.GENERATED5)

            elif urlparse(self.path).path == "/record_event":
                print("recording event")
                query = postvars
                kwargs = dict()
                if "event" in query.keys():
                    kwargs["event"] = query["event"]
                else:
                    kwargs["event"] = ""

                print("saving data")
                print(postvars["event"]["name"])
                if postvars["event"]["name"] == "changedWorkspace":
                    self.database_connection.insertIntoRecordedDataLog(postvars)
                self._set_headers()




        def parse_POST(self):
            ctype, pdict = parse_header(self.headers['content-type'])
            if ctype == 'multipart/form-data':
                postvars = parse_multipart(self.rfile, pdict)
            elif ctype == 'application/x-www-form-urlencoded':
                length = int(self.headers['content-length'])
                postvars = self.rfile.read(length)
            else:
                postvars = {}
            return json.loads(postvars)
    return ProcessingServerHandler


class ProcessingServer:

    def run(self, database_connection, port=20042):
        server_address = ('', port)
        HandlerClass = makeProcessingServerHandler(database_connection)
        httpd = HTTPServer(server_address, HandlerClass)
        print('Starting httpd server to access blockly log database...')
        httpd.serve_forever()
