from database_connection import DatabaseConnection
from processing_server import ProcessingServer
from code_tree_analyzer import CodeTreeAnalyzer
from treeparser import BlocklyTreeParser
from clustering_analysis import ClusteringAnalysis
from sklearn.preprocessing import RobustScaler

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import datetime
import sys
import random
import colorsys
import collections
from matplotlib.colors import hsv_to_rgb

def init_database_connection():
    """Start processing the log data"""
    print("Start processing")
    conn = DatabaseConnection()
    return conn


def init_webserver(database_connection):
    pros = ProcessingServer()
    pros.run(database_connection)


def random_color():
    rgbl=[255,0,0]
    random.shuffle(rgbl)
    return tuple(rgbl)



def get_colors_for_freq_table(freq_table):
    colors=[]
    norms=[]
    hue_increment = 360./float(len(freq_table.keys()))
    for i, session_id in enumerate(freq_table.keys()):
        hue = float(i)*hue_increment
        lightness = 100.
        sat_increment = 100./float(freq_table[session_id])
        for tree_index in range(freq_table[session_id]):
            saturation = float(tree_index)*sat_increment
            #colors.append(hsv_to_rgb(np.array([hue/360., lightness/100., saturation/100.])))
            colors.append(hsv_to_rgb(np.array([hue / 360., 1, 1])))
    return colors

def analyze_on_all_code_trees(arguments):


    treeparser = BlocklyTreeParser()
    analyzer = CodeTreeAnalyzer(conn, treeparser)

    # Pass the parsetrees argument to the
    if "parsetrees" in arguments:
        print("Loading xml trees from the database and storing them into a file.")
        (xml_trees, timestamps, session_ids) = analyzer.get_all_xml_code_trees()
        ast_trees = analyzer.convert_xml_trees_to_ast_trees(xml_trees)
        # Explicitly release memory for unused xml trees befor kernel computation.
        del xml_trees[:]
        del xml_trees

        igraph_ast_trees = analyzer.convert_ast_trees_to_igraph_ast_trees(ast_trees)
        # Explicitly release memory for unused ast_trees before kernel computation
        del ast_trees[:]
        del ast_trees

        print("Writing trees to file")
        # Write all igraph ast trees to a file
        np.save("./files/igraph_ast_trees", np.array(igraph_ast_trees))
        # writing timestamps for each tree to a file
        np.save("./files/graph_timestamps", np.array(timestamps))
        # writing the session id for each tree to a file
        np.save("./files/graph_session_ids", np.array(session_ids))

    # Read trees from file
    print("Reading trees from file")
    loaded_trees = np.load("./files/igraph_ast_trees.npy")

    # Load timestamps
    print("loading timestamps")
    timestamps = np.load("./files/graph_timestamps.npy")

    # Load session ids for each code tree from a file
    print("loading session ids")
    session_ids = np.load("./files/graph_session_ids.npy")

    dates = []
    for time in timestamps:
        d = datetime.datetime.fromtimestamp(time / 1000)
        dates.append(d.day + d.month * 100)  # Convert to unique integer per day

    # print("Caclulating kernels on set of igraph ast trees")
    # kernel_matrix = analyzer.calculate_WL_subtree_kernel(loaded_trees[0:76000:10])

    print(session_ids)

    # Filter out all last code trees from each session
    '''final_code_tees = []
    session_ids_unique = []
    for index in range(len(loaded_trees)):
        if (index + 1) == len(loaded_trees) or session_ids[index] != session_ids[index+1]:
            i = index
            while i >= 0 and i >= index - 10:
                final_code_tees.append(loaded_trees[i])
                session_ids_unique.append(session_ids[i])
    print(len(set(session_ids)))
    print(len(final_code_tees))'''

    # Calculate kernel matrix only on final trees in each session
    # kernel_matrix_final = analyzer.calculate_WL_subtree_kernel(final_code_tees)
    # print("clustering")
    # ca = ClusteringAnalysis()
    # tsne_embedding = ca.cluster_tsne(kernel_matrix_final, session_ids_unique)

    # Select which code trees to analyze
    # Only final code trees
    #    code_trees = final_code_tees
    #    session_ids_ta = session_ids_unique
    # Evenly distributed part of the dataset
    code_trees = loaded_trees[0:76000:10]
    session_ids_ta = session_ids[0:76000:10]
    freq_for_each_session = collections.Counter(session_ids_ta)
    print(freq_for_each_session)

    print("comparing different kernel methods")
    # Calculate distance matrices for all kernels in the graphkernel package.
    # kernel_matrices = analyzer.calculate_kernel_matrices(code_trees)
    kernel_names = ["EdgeHist", "VertexHist", "VertexEdgeHist", "VertexVertexEdgeHist", "VertexHistGauss",
                    "EdgeHistGauss"
        , "VertexEdgeHistGauss", "WL"]

    '''kernel_names = ["EdgeHist", "VertexHist", "VertexEdgeHist", "VertexVertexEdgeHist", "VertexHistGauss",
                    "EdgeHistGauss"
        , "VertexEdgeHistGauss", "GeometricRandomWalk", "ExponentialRandomWalk", "KStepRandomWalk", "ShortestPath"
                        , "WL", "Graphlet", "ConnectedGraphlet"]'''

    kernels = analyzer.get_kernel_function_list()

    color_labels_by_session_and_timestamp = get_colors_for_freq_table(freq_for_each_session)
    print(color_labels_by_session_and_timestamp)
    ca = ClusteringAnalysis()

    print(kernel_names[5])
    affinity_matrix = kernels[5](code_trees)
    # Transform affinity matrix to distance matrix and reduce outliers and start at zero
    max = np.amax(affinity_matrix)
    print(max)
    distance_matrix = (affinity_matrix - max) * -1
    # plot distance matrix
    plt.title(kernel_names[5])
    plt.imshow(distance_matrix, cmap='gist_ncar', interpolation='none')
    plt.show()
    # Cluster using t-SNE
    tsne_embedding = ca.cluster_tsne(distance_matrix, color_labels_by_session_and_timestamp, kernel_names[5])

    '''for index in range(len(kernel_names)):
        kernelname = kernel_names[index]
        print(kernelname)
        affinity_matrix = kernels[index](code_trees)
        # Transform affinity matrix to distance matrix and reduce outliers and start at zero
        max = np.amax(affinity_matrix)
        print(max)
        distance_matrix = (affinity_matrix - max) * -1
        # plot distance matrix
        plt.title(kernelname)
        plt.imshow(distance_matrix, cmap='gist_ncar', interpolation='none')
        plt.show()
        # Cluster using t-SNE
        tsne_embedding = ca.cluster_tsne(distance_matrix, session_ids_ta, kernelname)'''

    '''for kernelname, affinity_matrix in zip(kernel_names, kernel_matrices):
        print(kernelname)
        # Transform affinity matrix to distance matrix and reduce outliers and start at zero
        max = np.amax(affinity_matrix)
        print(max)
        distance_matrix = (affinity_matrix - max) * -1
        #transformer = RobustScaler(with_centering=True).fit(distance_matrix)
        #normalized_distance_matrix = transformer.transform(distance_matrix)
        #min = np.amin(normalized_distance_matrix)
        #normalized_distance_matrix = normalized_distance_matrix - min
        normalized_distance_matrix = distance_matrix
        # plot distance matrix
        plt.title(kernelname)
        plt.imshow(normalized_distance_matrix, cmap='gist_ncar', interpolation='none')
        plt.show()
        # Cluster using t-SNE
        tsne_embedding = ca.cluster_tsne(normalized_distance_matrix, session_ids_ta, kernelname)'''

    # This code runs spectral clustering and plots the clusters as color point on a 2d plot with axis for sessionId and timestamp
    '''
    cluster_labels, n_clusters = ca.cluster_spectral(kernel_matrix, session_ids[0:76000:10])

    prev_session_id = None
    start_timestamp = None
    session_index = -1
    datapoints = []
    for session_id, timestamp, label in zip(session_ids[0:76000:10], timestamps[0:76000:10], cluster_labels):
        if prev_session_id != session_id:
            prev_session_id = session_id
            session_index += 1
            start_timestamp = timestamp
        datapoints.append([session_index, timestamp - start_timestamp, label])

    datapoints = np.array(datapoints)

    colors = []
    for i in range(n_clusters):
        colors.append(random_color())

    fig = plt.figure(figsize=(8, 8))
    plt.scatter(datapoints[:, 1], datapoints[:, 0], c=datapoints[:, 2], marker='.')
    cb = plt.colorbar()
    loc = np.arange(0, max(datapoints[:, 2]), max(datapoints[:, 2]/float(len(colors))))
    cb.set_ticks(loc)
    cb.set_ticklabels(colors)
    plt.xlim(0, 10000000)
    plt.show()'''

def analyze_for_session(arguments, session):
    conn = init_database_connection()
    treeparser = BlocklyTreeParser()
    analyzer = CodeTreeAnalyzer(conn, treeparser)

    # Pass the parsetrees argument to the
    if "parsetrees" in arguments:
        print("Loading xml trees from the database and storing them into a file.")
        (xml_trees, timestamps, session_ids) = analyzer.get_xml_code_trees_for_session(session)
        ast_trees = analyzer.convert_xml_trees_to_ast_trees(xml_trees)
        used_trees = np.array(xml_trees)[0:17000:2]
        # Explicitly release memory for unused xml trees befor kernel computation.
        del xml_trees[:]
        del xml_trees

        igraph_ast_trees = analyzer.convert_ast_trees_to_igraph_ast_trees(ast_trees)
        # Explicitly release memory for unused ast_trees before kernel computation
        del ast_trees[:]
        del ast_trees

        print("Writing trees to file")
        # Write all igraph ast trees to a file
        np.save("./files/igraph_ast_trees_for_session" + str(session), np.array(igraph_ast_trees))
        # writing timestamps for each tree to a file
        np.save("./files/graph_timestamps_for_session" + str(session), np.array(timestamps))
        # writing the session id for each tree to a file
        np.save("./files/graph_session_ids_for_session" + str(session), np.array(session_ids))
        #save the trees that are used
        np.save("./files/xml_trees_for_session" + str(session), used_trees)

    # Read trees from file
    print("Reading trees from file")
    loaded_trees = np.load("./files/igraph_ast_trees_for_session" + str(session) + ".npy")

    # Load timestamps
    print("loading timestamps")
    timestamps = np.load("./files/graph_timestamps_for_session" + str(session) + ".npy")

    # Load session ids for each code tree from a file
    print("loading session ids")
    session_ids = np.load("./files/graph_session_ids_for_session" + str(session) + ".npy")

    code_trees = loaded_trees[0:17000:2]
    session_ids_ta = session_ids[0:17000:2]
    freq_for_each_session = collections.Counter(session_ids_ta)
    print(freq_for_each_session)

    print("comparing different kernel methods")
    # Calculate distance matrices for all kernels in the graphkernel package.
    # kernel_matrices = analyzer.calculate_kernel_matrices(code_trees)
    kernel_names = ["EdgeHist", "VertexHist", "VertexEdgeHist", "VertexVertexEdgeHist", "VertexHistGauss",
                    "EdgeHistGauss"
        , "VertexEdgeHistGauss", "WL"]

    '''kernel_names = ["EdgeHist", "VertexHist", "VertexEdgeHist", "VertexVertexEdgeHist", "VertexHistGauss",
                    "EdgeHistGauss"
        , "VertexEdgeHistGauss", "GeometricRandomWalk", "ExponentialRandomWalk", "KStepRandomWalk", "ShortestPath"
                        , "WL", "Graphlet", "ConnectedGraphlet"]'''

    kernels = analyzer.get_kernel_function_list()

    ca = ClusteringAnalysis()

    print(kernel_names[5])
    affinity_matrix = kernels[5](code_trees)
    # Transform affinity matrix to distance matrix and reduce outliers and start at zero
    max = np.amax(affinity_matrix)
    print(max)
    distance_matrix = (affinity_matrix - max) * -1
    # plot distance matrix
    plt.title(kernel_names[5])
    plt.imshow(distance_matrix, cmap='gist_ncar', interpolation='none')
    plt.show()
    # Cluster using t-SNE
    tsne_embedding = ca.cluster_tsne(distance_matrix, session_ids_ta, kernel_names[5])

    return tsne_embedding

from code_generator import CodeGenerator

if __name__ == '__main__':
    #cg = CodeGenerator()
    #cg.read_solution_tree()

    conn = init_database_connection()
    if "runserver" in sys.argv:
        print("running server")
        init_webserver(conn)
    #analyze_on_all_code_trees(sys.argv)
    for s in range(2):
        session_embedding = analyze_for_session(sys.argv, s)
        np.save("files/session" + str(s), np.array(session_embedding))
