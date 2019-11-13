from http.server import BaseHTTPRequestHandler, HTTPServer
from cgi import parse_header, parse_multipart
from urllib.parse import parse_qs, urlparse
from http.server import BaseHTTPRequestHandler
from my_enums import WorkshopType
import json
import numpy as np
from my_enums import FunctionalDataset
from functional_analyzer import FunctionalAnalyzer
from utils import AnalysisUtils


from bson import ObjectId

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)


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
            #load steplabels if existing
            steplabels = np.multiply(np.ones(len(labels)), 50)
            try:
                steplabels = np.load("./files/steplabels" + kwargs["experimentId"] + ".npy").tolist()
            except:
                print("No steplabels file")


            if len(labels) == 0:
                labels = np.zeros(10000)

            '''utils = AnalysisUtils()
            normalized_loaded_session_ids = utils.normalize_session_id_list(loaded_session_ids)'''
            max_elements = self.max_points

            nr_of_trees = len(loaded_trees)
            packed_data = list(zip(loaded_trees[0:max_elements], labels[0:max_elements], steplabels[0:max_elements]))
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

            #code_trees = []
            #code_trees.append(np.load("./files/xml_trees_for_session" + kwargs["experimentId"] + ".npy").tolist())
            count = database_connection.get_create_entry_count()
            #print("We have the following number of code trees")
            #print(len(code_trees[0]))
            #return json.dumps(len(code_trees[0])).encode()
            print("We have the following number of code trees: {}".format(count))
            return json.dumps(count).encode()

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
            '''code_trees = database_connection.get_create_entries()
            code_tree_data = code_trees[kwargs["index"]]["event"]["data"]'''
            #if len(labels) == 0:
                #labels = [0 for i in range(len(code_trees[0]))]
            return json.dumps([code_tree_data, 0]).encode()

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

        def get_interactive_clustering_collection_names(self):
            names = database_connection.get_interactive_clustering_collection_names()
            return json.dumps(names).encode()

        def get_labeler_data_count(self):
            labeler_data = list(database_connection.get_functional_log_data_blocks_label_and_id(FunctionalDataset.FUNC_CREATE_MICRO))
            print(len(labeler_data))
            return json.dumps(len(labeler_data)).encode()

        def get_labeler_data_element(self):
            query = parse_qs(urlparse(self.path).query)
            kwargs = dict()
            if "prog_number" in query.keys():
                kwargs["prog_number"] = int(query["prog_number"][0])
            else:
                kwargs["prog_number"] = 0
            labeler_data = list(database_connection.get_functional_log_data_blocks_label_and_id(FunctionalDataset.FUNC_CREATE_MICRO))
            data = labeler_data[kwargs["prog_number"]]
            json_data = JSONEncoder().encode(data)
            return json_data.encode()

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

            elif urlparse(self.path).path == "/get_interactive_clustering_collection_names":
                self.wfile.write(self.get_interactive_clustering_collection_names())
            elif urlparse(self.path).path == "/get_labeler_data_count":
                self.wfile.write(self.get_labeler_data_count())
            elif urlparse(self.path).path == "/get_labeler_data_element":
                self.wfile.write(self.get_labeler_data_element())

            else:
                self.wfile.write("<html><body><h1>hi!</h1></body></html>".encode())

        def do_HEAD(self):
            self._set_headers()


        def do_POST(self):
            postvars = self.parse_POST()


            if urlparse(self.path).path == "/save_functional_vector" \
                    or urlparse(self.path).path == "/update_functional_vector":

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
                    kwargs["vector"] = query["vector"]
                else:
                    kwargs["vector"] = []
                if "label" in query.keys():
                    kwargs["label"] = int(query["label"])
                else:
                    kwargs["label"] = -1

                if urlparse(self.path).path == "/update_functional_vector":
                    if "experiment_id" in query.keys():
                        kwargs["experiment_id"] = query["experiment_id"]
                    else:
                        kwargs["experimentId"] = ""
                    if "_id" in query.keys():
                        kwargs["_id"] = query["_id"]
                    else:
                        kwargs["_id"] = -1

                    self.database_connection.update_functional_log_entry_label(kwargs["_id"], kwargs["label"],
                                                                      FunctionalDataset.REAL_SPLIT)
                else:
                    print("New vector")
                    print(kwargs["vector"])

                    self.database_connection.add_functional_log_entry(kwargs["experimentId"], kwargs["vector"],
                                                                      kwargs["xml_blocks"], kwargs["label"],
                                                                      FunctionalDataset.FUNC_CREATE_MICRO)

                self._set_headers()
                self.wfile.write("<html><body><h1>POST!</h1></body></html>".encode())

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
                self.wfile.write("<html><body><h1>POST!</h1></body></html>".encode())

            elif (urlparse(self.path).path == "/recluster"):
                print("reclustering")
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
                    if query["label"] == "":
                        kwargs["label"] = -1
                    else:
                        kwargs["label"] = int(query["label"])
                if "steplabel" in query.keys():
                    if query["steplabel"] == "":
                        kwargs["steplabel"] = -1
                    else:
                        kwargs["steplabel"] = int(query["steplabel"])
                if "pathlabel" in query.keys():
                    if query["pathlabel"] == "":
                        kwargs["pathlabel"] = -1
                    else:
                        kwargs["pathlabel"] = int(query["pathlabel"])
                else:
                    kwargs["label"] = -1
                if "collection" in query.keys():
                    kwargs["collection"] = query["collection"]
                else:
                    kwargs["collection"] = "log"
                if "embedding_dims" in query.keys():
                    kwargs["embedding_dims"] = int(query["embedding_dims"])
                else:
                    kwargs["embedding_dims"] = 3

                if kwargs["xml_blocks"] != "":
                    self.database_connection.add_to_interactive_data_log(kwargs["collection"],
                                                                         kwargs["experimentId"],
                                                                         kwargs["vector"],
                                                                         kwargs["xml_blocks"],
                                                                         kwargs["label"],
                                                                         kwargs["steplabel"],
                                                                         kwargs['pathlabel'])

                fa = FunctionalAnalyzer(self.database_connection, kwargs["experimentId"])
                embedding, code_trees, labels, steplabels, reducedVectors = fa.analyze(FunctionalDataset.INTERACTIVE_CLUSTERING,
                                                           log_id=kwargs["collection"],
                                                           save_results=False,
                                                           embedding_dims=kwargs["embedding_dims"])
                packed_data = list((embedding.tolist(), code_trees, labels, reducedVectors.tolist()))

                print("New vector")
                print(kwargs["vector"])

                json_string = json.dumps(packed_data).encode()
                self.send_response(200)  # create header
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header("Content-Length", str(len(json_string)))
                self.send_header('Content-Type', 'text/plain')
                self.end_headers()
                self.wfile.write(json_string)




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
