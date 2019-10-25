import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from scipy.spatial.distance import euclidean
import matplotlib.cbook as cbook
from numpy import pi
from sklearn.decomposition import PCA
import matplotlib.image as mpimg
from sklearn.manifold import TSNE as t_sne
from sklearn.decomposition import NMF
import pandas as pd
from pymssa import MSSA
import scipy
from scipy.spatial.distance import euclidean
from scipy.spatial.distance import correlation
from my_enums import FunctionalDataset
import cmath
import seaborn as sns
import os
import math
import json
from code_tree_analyzer import CodeTreeAnalyzer
from treeparser import BlocklyTreeParser
from clustering_analysis import ClusteringAnalysis


class StructuralAnalyzer:
    def __init__(self, database_connection, experimentId):
        self.experimentId = experimentId
        self.db_connection = database_connection

    def analyze(self, dataset_id, log_id="log", save_results=False, embedding_dims=3, parsetrees=True, use_kernel=True, cluster=True):
       tree_parser = BlocklyTreeParser()
       tree_analyzer = CodeTreeAnalyzer(self.db_connection, tree_parser)
       if parsetrees:
           xml_code_trees = list(self.db_connection.get_f_programs(dataset_id, log_name=log_id))
           labels = list(self.db_connection.get_f_labels(dataset_id, log_name=log_id))

           ast_trees = tree_analyzer.convert_xml_trees_to_ast_trees(xml_code_trees)
           igraph_ast_trees = tree_analyzer.convert_ast_trees_to_igraph_ast_trees_connected_siblings(ast_trees)
           # Save to file to be used in visualization server
           np.save("./files/xml_trees_for_session" + self.experimentId, np.array(xml_code_trees))
           # Save to file to be used in visualization server
           np.save("./files/labels" + self.experimentId, np.array(labels))
           # Write all igraph ast trees to a file
           np.save("./files/igraph_ast_trees" + self.experimentId, np.array(igraph_ast_trees))
       else:
           # Read trees from file
           print("Reading trees from file")
           igraph_ast_trees = np.load("./files/igraph_ast_trees" + self.experimentId + ".npy")

           # Load labels for each code tree from a file
           print("loading labels")
           labels = np.load("./files/labels" + self.experimentId + ".npy")

       kernel_names = ["EdgeHist", "VertexHist", "VertexEdgeHist", "VertexVertexEdgeHist", "VertexHistGauss",
                       "EdgeHistGauss", "VertexEdgeHistGauss", "WL", "Graphlet", "ConnectedGraphlet"]

       ca = ClusteringAnalysis()

       sigma = 30
       distance_matrix = []
       if use_kernel:
           print("Calculating kernel")

           kernels = tree_analyzer.get_kernel_function_list()
           kernel_number = 5
           print(kernel_names[kernel_number])
           affinity_matrix = kernels[kernel_number](igraph_ast_trees,
                                                    sigma)  # The second parameter determines the with of the gaussian
           # Transform affinity matrix to distance matrix and reduce outliers and start at zero
           max = np.amax(affinity_matrix)
           print(max)
           distance_matrix = (affinity_matrix - max) * -1

           # Save kernel affinity matrix
           np.save("./files/distance_matrix_sigma_" + self.experimentId + str(sigma), np.array(distance_matrix))

       if cluster:
           distance_matrix = np.load("./files/distance_matrix_sigma_" + self.experimentId + str(sigma) + ".npy")
           # Cluster using t-SNE
           tsne_embedding = ca.cluster_tsne(distance_matrix, labels, kernel_names[5], n_components=embedding_dims,
                                            perplexity=50)
           np.save("./files/tsne_embedding" + self.experimentId, np.array(tsne_embedding))

       return tsne_embedding, distance_matrix
