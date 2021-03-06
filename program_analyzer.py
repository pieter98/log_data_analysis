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
from sklearn.metrics import pairwise_distances
import pandas as pd
from pymssa import MSSA
import scipy
import umap
from scipy.spatial.distance import euclidean
from scipy.spatial.distance import correlation
from my_enums import FunctionalDataset
import cmath
import seaborn as sns
import os
import math
import json
from functional_analyzer import FunctionalAnalyzer
from structural_analyzer import StructuralAnalyzer
from utils import AnalysisUtils


class ProgramAnalyzer:
    def __init__(self, experimentId):
        self.experimentId = experimentId

    def log_cosine_distance(self, a, b):
        azeros = np.count_nonzero(a)
        bzeros = np.count_nonzero(b)
        if azeros == 0 or bzeros == 0:
            return 0
        cosdist = scipy.spatial.distance.cosine(a, b)
        if cosdist == 0:
            return 0
        dist = math.log(cosdist)
        return dist

    def analyze(self, dataset_id, f_analyzer, s_analyzer, log_id="log", save_results=False, embedding_dims=2, func_method="hadamard", func_incremental=False, clustering_method="t-sne"):
        # Get functional embedding and distance matrix
        f_embedding, f_code_trees, f_labels, f_steplabels, f_vectors = f_analyzer.analyze(dataset_id, log_id=log_id, method=func_method, incremental=func_incremental, save_results=False, embedding_dims=embedding_dims, clustering_method=clustering_method)
        f_dmat = pairwise_distances(f_vectors, metric="cosine")
        f_dmat = np.divide(f_dmat, scipy.linalg.norm(f_dmat))
        # plot distance matrix
        plt.title("functional distance matrix")
        plt.imshow(f_dmat, cmap='gist_ncar', interpolation='none')
        plt.show()
        # get structural embedding and distance
        s_embedding, s_dmat = s_analyzer.analyze(dataset_id, log_id=log_id, save_results=False, embedding_dims=embedding_dims)
        s_dmat = np.divide(s_dmat, scipy.linalg.norm(s_dmat))
        # plot distance matrix
        plt.title("structural distance matrix")
        plt.imshow(s_dmat, cmap='gist_ncar', interpolation='none')
        plt.show()

        # Combine functional and structural distance matrix
        #dmat = np.divide(np.add(f_dmat, np.multiply(s_dmat, 1)), 2)
        #f_dmat = np.log(np.add(f_dmat, 1))
        #dmat = np.minimum(np.divide(f_dmat, scipy.linalg.norm(f_dmat)), s_dmat)
        #dmat = np.divide(np.add(np.log(np.add(np.multiply(f_dmat, 100), 1)), np.log(np.add(np.multiply(s_dmat, 100), 1))), 2)
        #dmat = np.divide(dmat, scipy.linalg.norm(dmat))  #normalize
        min_contrib = 100
        divisor = np.add(s_dmat, f_dmat)
        #f_weights = np.nan_to_num(np.divide(np.add(s_dmat, np.divide(divisor, min_contrib)), np.add(divisor, np.divide(divisor, min_contrib*2))))
        f_weights = np.nan_to_num(np.divide(s_dmat, divisor))
        #s_weights = np.nan_to_num(np.divide(np.add(f_dmat, np.divide(divisor, min_contrib)), np.add(divisor, np.divide(divisor, min_contrib*2))))
        s_weights = np.nan_to_num(np.divide(f_dmat, divisor))
        dmat = np.add(np.multiply(f_dmat, f_weights), np.multiply(s_dmat, s_weights))

        plt.title("combined dmat")
        plt.imshow(dmat, cmap='gist_ncar', interpolation='none')
        plt.show()

        if clustering_method == "t-sne":
            # Cluster using t-SNE
            tsne = t_sne(n_components=embedding_dims, metric="precomputed", perplexity=10)
            embedding = tsne.fit_transform(dmat)


        elif clustering_method == "umap":
            reducer = umap.UMAP(metric="precomputed", min_dist=0.99, n_neighbors=100)
            embedding = reducer.fit_transform(dmat)

        if save_results:
            utils = AnalysisUtils()
            utils.save_experiment(self.experimentId, embedding, f_code_trees, f_labels, f_steplabels)

        print("done")

