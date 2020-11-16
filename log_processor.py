from Visualisations.Visualizer.VisualizerControl import VisualizerControl
from Visualisations.Visualizer.VisualizerTypes import VisualizerTypes
from database_connection import DatabaseConnection
from processing_server import ProcessingServer
from code_tree_analyzer import CodeTreeAnalyzer
from structural_analyzer import StructuralAnalyzer
from treeparser import BlocklyTreeParser
from clustering_analysis import ClusteringAnalysis
from sklearn.preprocessing import RobustScaler
import threading
from data_logging_server import dataLoggerRequestHandler
from my_enums import WorkshopType
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 unused import
import datetime
import sys
import random
import collections
import pandas as pd
from my_enums import FunctionalDataset


def init_database_connection():
    """Start processing the log data"""
    print("Start processing")
    conn = DatabaseConnection()
    return conn


def init_webserver(database_connection):
    pros = ProcessingServer()
    pros.run(database_connection)


def random_color():
    rgbl=[255, 0, 0]
    random.shuffle(rgbl)
    return tuple(rgbl)



'''def get_colors_for_freq_table(freq_table):
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
    return colors'''

def analyze_on_all_code_trees(arguments, n_components=2, experiment_id="", data_source=WorkshopType.GENERATED):


    treeparser = BlocklyTreeParser()
    analyzer = CodeTreeAnalyzer(conn, treeparser)

    # Pass the parsetrees argument to the
    if "parsetrees" in arguments:
        print("Loading xml trees from the database and storing them into a file.")
        # This line for generated data
        (xml_trees, timestamps, session_ids, labels) = analyzer.get_all_xml_code_trees(workshop_type=data_source)
        # This is for real data
        #(xml_trees, timestamps, session_ids) = analyzer.get_all_xml_code_trees()
        # writing the session id for each tree to a file
        np.save("./files/xml_trees_for_session" + experiment_id, np.array(xml_trees)) # Save to file to be used in visualization server

        # convert string labels to unique number
        labelset = list(set(labels))
        converted_label_set = []
        for label in labels:
            converted_label_set.append(labelset.index(label))

        np.save("./files/labels" + experiment_id, np.array(converted_label_set))  # Save to file to be used in visualization server

        ast_trees = analyzer.convert_xml_trees_to_ast_trees(xml_trees)
        # Explicitly release memory for unused xml trees before kernel computation.
        del xml_trees[:]
        del xml_trees

        #igraph_ast_trees = analyzer.convert_ast_trees_to_igraph_ast_trees(ast_trees)
        igraph_ast_trees = analyzer.convert_ast_trees_to_igraph_ast_trees_connected_siblings(ast_trees)
        #
        # Explicitly release memory for unused ast_trees before kernel computation
        del ast_trees[:]
        del ast_trees

        print("Writing trees to file")
        # Write all igraph ast trees to a file
        np.save("./files/igraph_ast_trees" + experiment_id, np.array(igraph_ast_trees))
        # writing timestamps for each tree to a file
        np.save("./files/graph_timestamps" + experiment_id, np.array(timestamps))
        # writing the session id for each tree to a file
        np.save("./files/graph_session_ids_for_session" + experiment_id, np.array(session_ids))


    # Read trees from file
    print("Reading trees from file")
    loaded_trees = np.load("./files/igraph_ast_trees" + experiment_id + ".npy")

    # Load timestamps
    print("loading timestamps")
    timestamps = np.load("./files/graph_timestamps" + experiment_id + ".npy")

    # Load session ids for each code tree from a file
    print("loading session ids")
    session_ids = np.load("./files/graph_session_ids_for_session" + experiment_id + ".npy")

    # Load labels for each code tree from a file
    print("loading labels")
    similarTreeLabels = np.load("./files/labels" + experiment_id + ".npy")

    dates = []
    for time in timestamps:
        d = datetime.datetime.fromtimestamp(time / 1000)
        dates.append(d.day + d.month * 100)  # Convert to unique integer per day

    print(session_ids)

    code_trees = loaded_trees[0:10000]
    session_ids_ta = session_ids[0:10000]
    tree_labels = None
    if similarTreeLabels.size == 0:
        tree_labels = np.zeros(10000)
    else:
        tree_labels = similarTreeLabels[0:10000]
    freq_for_each_session = collections.Counter(session_ids_ta)

    kernel_names = ["EdgeHist", "VertexHist", "VertexEdgeHist", "VertexVertexEdgeHist", "VertexHistGauss",
                    "EdgeHistGauss"
        , "VertexEdgeHistGauss", "WL", "Graphlet", "ConnectedGraphlet"]

    '''kernel_names = ["EdgeHist", "VertexHist", "VertexEdgeHist", "VertexVertexEdgeHist", "VertexHistGauss",
                    "EdgeHistGauss"
        , "VertexEdgeHistGauss", "GeometricRandomWalk", "ExponentialRandomWalk", "KStepRandomWalk", "ShortestPath"
                        , "WL", "Graphlet", "ConnectedGraphlet"]'''

    ca = ClusteringAnalysis()
    sigma = 30
    if "kernel" in arguments:
        print("Calculating kernel")

        kernels = analyzer.get_kernel_function_list()
        kernel_number = 5
        print(kernel_names[kernel_number])
        affinity_matrix = kernels[kernel_number](code_trees, sigma) # The second parameter determines the with of the gaussian
        # Transform affinity matrix to distance matrix and reduce outliers and start at zero
        max = np.amax(affinity_matrix)
        print(max)
        distance_matrix = (affinity_matrix - max) * -1
        # plot distance matrix
        plt.title(kernel_names[kernel_number])
        plt.imshow(distance_matrix, cmap='gist_ncar', interpolation='none')
        plt.show()

        # Save kernel affinity matrix
        np.save("./files/distance_matrix_sigma_" + experiment_id + str(sigma), np.array(distance_matrix))

    
    if "t_sne" in arguments:
        distance_matrix = np.load("./files/distance_matrix_sigma_" + experiment_id + str(sigma) + ".npy")
        # Cluster using t-SNE
        tsne_embedding = ca.cluster_tsne(distance_matrix, tree_labels, kernel_names[5], n_components=n_components, perplexity=50)
        np.save("./files/tsne_embedding" + experiment_id, np.array(tsne_embedding))


    if "cluster_tsne" in arguments:
        tsne_embedding = np.load("./files/tsne_embedding" + experiment_id + ".npy")
        labels, n_labels = ca.cluster_t_sne_result(tsne_embedding, tree_labels)



        # now compute the distance between each cluster in the kernel space
        # for each element in a cluster, compute the average distance to each point in each other cluster.
        # First create a binary matrix which contains the elements for each cluster (row = cluster, column = element)
        # Repeat the label row n_labels times
        # replace noise labels with positive number of last cluster otherwise the cluster is empty.
        labels = np.where(labels == -1, n_labels-1, labels)
        rep_labels = np.array([labels, ]*n_labels)
        # Convert to binary matrix
        A = [np.where(element == index, 1, 0) for index, element in enumerate(rep_labels)]
        # Count the number of ones in each row


        #Test = np.bincount(labels)
        M = np.sum(A, axis=1)
        M = np.reshape(M, (len(M), 1))

        # now calculate the average distance between each cluster based on the kernel matrix
        D = distance_matrix
        cluster_distance = np.divide(np.transpose(np.dot(np.divide(np.dot(A, D), M), np.transpose(A))), M)
        # Normalize cluster distance matrix
        min = np.amin(cluster_distance[np.nonzero(cluster_distance)], axis=0)
        max = np.amax(cluster_distance[np.nonzero(cluster_distance)], axis=0)
        cluster_distance_norm = np.true_divide(cluster_distance - min, max - min)
        np.set_printoptions(threshold=np.inf, linewidth=np.inf)
        print(cluster_distance)
        print(cluster_distance_norm)
        np.set_printoptions(threshold=1000, linewidth=200)
        plt.title("normalized distance between clusters")
        plt.imshow(cluster_distance_norm, cmap='jet', interpolation='none')
        plt.show()

        # Now calculate the cluster centers within the embedded space (just take x, y and z average for each cluster)
        cluster_averages = np.divide(np.dot(A, tsne_embedding), M)
        # save cluster centers to file
        np.save("./files/cluster_centers_embedded_space" + experiment_id, np.array(cluster_averages))

        nr_of_closest_clusters = 2
        nearby_cluster_pairs = []  # Keeps a list of all cluster pairs which are near to eachother
        # Loop over every row in the cluster distance matrix
        for i in range(cluster_distance.shape[0]):
            closest_clusters = []  # Saves the "nr_of_closest_clusters" to cluster i
            # seach for "nr_of_closest_clusters" clusters closest to cluster i
            for k in range(nr_of_closest_clusters):
                current_closest_dist = float("inf")  # Start at infinite distance
                current_closest = None # No closest clusters yet
                # Loop over every other cluster in the cluster distance matrix
                for j in range(cluster_distance.shape[1]):
                    # If this cluster has not been added to the closest clusters yet and is not itself,
                    # update the closest cluster
                    if j not in closest_clusters and i != j:
                        if cluster_distance[i][j] < current_closest_dist:
                            current_closest = j
                            current_closest_dist = cluster_distance[i][j]
                closest_clusters.append(current_closest)  # Add closest cluster in this iteration to closest clusters
            # Add all closest clusters to cluster i to the list of closest clusters
            for cluster in closest_clusters:
                nearby_cluster_pairs.append((i, cluster))

        nearby_cluster_pair_points = []
        for (c1, c2) in nearby_cluster_pairs:
            nearby_cluster_pair_points.append([cluster_averages[c1], cluster_averages[c2]])

        np.save("./files/nearby_cluster_pair_points" + experiment_id, np.array(nearby_cluster_pair_points))


        df = pd.DataFrame({'X': tsne_embedding[:, 0], 'Y': tsne_embedding[:, 1],
                           'Z': tsne_embedding[:, 2]})

        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(df['X'], df['Y'], df['Z'], c=labels, s=100, cmap='tab20')
        # Draw lines between nearby clusters
        for (c1, c2) in nearby_cluster_pairs:
            ax.plot([cluster_averages[c1][0], cluster_averages[c2][0]],
                    [cluster_averages[c1][1], cluster_averages[c2][1]],
                    [cluster_averages[c1][2], cluster_averages[c2][2]])
        ax.view_init(30, 185)

        plt.show()

    return tsne_embedding



def analyze_for_session(arguments, session, n_components=2):
    conn = init_database_connection()
    treeparser = BlocklyTreeParser()
    analyzer = CodeTreeAnalyzer(conn, treeparser)

    # Pass the parsetrees argument to the
    if "parsetrees" in arguments:
        print("Loading xml trees from the database and storing them into a file.")
        # this line for real data for one session:
        #(xml_trees, timestamps, session_ids) = analyzer.get_xml_code_trees_for_session(session)
        # This line for generated data
        (xml_trees, timestamps, session_ids) = analyzer.get_all_xml_code_trees(workshop_type=WorkshopType.GENERATED)
        ast_trees = analyzer.convert_xml_trees_to_ast_trees(xml_trees)
        used_trees = np.array(xml_trees)[0:20000:1]
        # Explicitly release memory for unused xml trees before kernel computation.
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

    code_trees = loaded_trees[0:20000:1]
    session_ids_ta = session_ids[0:20000:1]
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
    tsne_embedding = ca.cluster_tsne(distance_matrix, session_ids_ta, kernel_names[5], n_components=n_components)

    return tsne_embedding

from functional_analyzer import FunctionalAnalyzer
from program_analyzer import ProgramAnalyzer

if __name__ == '__main__':
    print(sys.executable)
    print(sys.version_info)
    conn = init_database_connection()
    exp_id = "_03-04-20_simplified_functional_base_structural_umap_100_0.99"

    if "program" in sys.argv:
        f_analyzer = FunctionalAnalyzer(conn, exp_id)
        s_analyzer = StructuralAnalyzer(conn, exp_id)
        p_analyzer = ProgramAnalyzer(exp_id)
        p_analyzer.analyze(FunctionalDataset.INTERACTIVE_CLUSTERING, f_analyzer, s_analyzer, log_id="new_gen_prog_compare", save_results=True,
                           clustering_method="umap")
        #p_analyzer.analyze(FunctionalDataset.FUNC_CREATE_MICRO, f_analyzer, s_analyzer, log_id="log", save_results=True, clustering_method="umap")

    if "functional" in sys.argv:
        fAnalyzer = FunctionalAnalyzer(conn, exp_id)
        #fAnalyzer.analyze(FunctionalDataset.FUNC_CREATE_MICRO)
        #fAnalyzer.analyze(FunctionalDataset.FUNC_CREATE_MICRO, method="hadamard", incremental=False)
        fAnalyzer.analyze(FunctionalDataset.FUNC_CREATE_MICRO, log_id="log", method="hadamard", incremental=False, clustering_method="umap")


    if "structural" in sys.argv:

        # Start a thread which runs the logging server for the artificial data generation
        threading.Thread(target=dataLoggerRequestHandler.run).start()

        embedding = analyze_on_all_code_trees(sys.argv, n_components=3, experiment_id=exp_id, data_source=WorkshopType.GENERATED)
        np.save("files/session" + exp_id, np.array(embedding))

        print("embedding saved - running server")


    if "runserver" in sys.argv:
        print("running server")
        init_webserver(conn)
        #analyze_on_all_code_trees(sys.argv)

        '''for s in range(2):
            session_embedding = analyze_for_session(sys.argv, s)
            np.save("files/session" + str(s), np.array(session_embedding))'''


    if "visualize" in sys.argv:
        vis = VisualizerControl()
        vis.showVisualisation(VisualizerTypes.COLORPLOTVISUALISATION1)

