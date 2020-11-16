from builtins import float

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
import tensorflow as tf
from keras import layers
from keras import models
from keras import optimizers
from numpy import newaxis
from keras import backend as K
from keras.losses import mse, binary_crossentropy


class SimplifiedFunctionalAnalyzer:
    def __init__(self):
        pass

    def analyze(self, dataset_id, log_id="log", save_results=True, method="hadamard", embedding_dims=3,
                incremental=False):
        vectorCursor = self.db_connection.get_fid_vectors(dataset_id, log_name=log_id)
        tmpLabels = self.db_connection.get_f_labels(dataset_id, log_name=log_id)
        tmpCodeTrees = self.db_connection.get_f_programs(dataset_id, log_name=log_id)
        tmpStepLabels = self.db_connection.get_f_steplabels(dataset_id, log_name=log_id)

        steplabels = []
        '''for label in tmpStepLabels:
            steplabels.append(label['steplabel'])'''

        labels = []
        for label in tmpLabels:
            labels.append(label['label'])  # pathlabel for new method

        code_trees = []
        for ct in tmpCodeTrees:
            code_trees.append(ct["xml_blocks"])

        tmpVectors = []
        for vector in vectorCursor:
            if isinstance(vector["vector"], str):
                tmpVectors.append(json.loads(vector["vector"]))
            else:
                tmpVectors.append(vector["vector"])

        fVectors = np.array(tmpVectors, dtype=np.float32)

        fVectors = np.nan_to_num(fVectors)

        # split concatenated states into matrix with for each state component one row.
        state_vect_length = 32
        fVectors = fVectors.reshape((fVectors.shape[0], state_vect_length, int(fVectors.shape[1] / state_vect_length)))