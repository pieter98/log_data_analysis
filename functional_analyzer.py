from builtins import float

import numpy as np
import matplotlib.pyplot as plt
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



class FunctionalAnalyzer:


    def __init__(self, database_connection, experimentId):
        self.experimentId = experimentId
        self.db_connection = database_connection
        self.timestep_size = 53 # The number of features logged in each timestep.

    def get_fid_vectors(self, dataset_id):
        return self.db_connection.get_fid_vectors(dataset_id)

    def analyze(self, dataset_id):
        print("Starting functional analysis")

        vectorCursor = self.get_fid_vectors(dataset_id)
        tmpLabels = self.db_connection.get_f_labels(dataset_id)
        tmpCodeTrees = self.db_connection.get_f_programs(dataset_id)

        # Also get recored labeled data
        vectorCursorRecorded = self.db_connection.get_fid_vectors(FunctionalDataset.RECORDED)
        labelsRecorded = self.db_connection.get_f_labels(FunctionalDataset.RECORDED)
        codeTreesRecorded = self.db_connection.get_f_programs(FunctionalDataset.RECORDED)

        labels = []
        for label in tmpLabels:
            labels.append(label['label'])

        for label in labelsRecorded:
            labels.append(label['label'])

        code_trees = []
        for ct in tmpCodeTrees:
            code_trees.append(ct["xml_blocks"])
        for ct in codeTreesRecorded:
            code_trees.append(ct["xml_blocks"])

        tmpVectors = []
        for vector in vectorCursor:
            tmpVectors.append(vector["vector"])
        for vector in vectorCursorRecorded:
            tmpVectors.append(vector["vector"])

        fVectors = np.array(tmpVectors, dtype=np.float32)

        #Perform NNMF
        #reducedVectors = self.perform_nnmf(fVectors)

        # Perform MSSA
        #reducedVectors = self.perform_mssa(fVectors[4900:, 0:300].T, 30)

        # Perform SSA
        reducedVectors = self.SSA(fVectors)

        np.save("./files/reduced_vectors" + "_functional" + self.experimentId, reducedVectors)
        embedding = self.cluster_tsne(reducedVectors, 3, 50)

        #self.plot_embedding(embedding, labels)

        self.save_experiment(embedding, code_trees, labels)
        '''
        #self.plot_vectors(fVectors)
        reducedVectors = self.select_pricipal_components(fVectors, 5)
        self.plot_vectors(reducedVectors[0:500, :])

        embedding = self.cluster_tsne(reducedVectors, 3, 50)

        self.plot_embedding(embedding, labels)

        '''

    def save_experiment(self, embedding, code_trees, labels):
        # Save the embedded points in 3D space to a file
        np.save("./files/session" + "_functional" + self.experimentId, embedding)
        # Save the coresponding program xmls to a file
        np.save("./files/xml_trees_for_session" + "_functional" + self.experimentId, code_trees)
        # Save the coresponding labels to a file
        np.save("./files/labels" + "_functional" + self.experimentId, labels)
        # TODO: Calculate the centroid of the clusters and get the two closest clusters for each cluster
        np.save("./files/nearby_cluster_pair_points" + "_functional" + self.experimentId, [])



    def plot_embedding(self, embedding, labels):
        df = pd.DataFrame({'X': embedding[:, 0], 'Y': embedding[:, 1],
                           'Z': embedding[:, 2]})

        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(df['X'], df['Y'], df['Z'], c=labels, s=100)
        ax.view_init(30, 185)

        plt.show()

    def cluster_tsne(self, fVectors, n_components, perplexity):
        tsne = t_sne(n_components=n_components, perplexity=perplexity)
        embedding = tsne.fit_transform(fVectors)
        return embedding

    '''
    @brief generates a pca model for each timestep
    @param fVectors an n x m matrix with a vector for each program in the dataset. 
            The rows are stacked program states in time. Each program state has self.timestep_size features
    @param nComponents the number of components to reduce each timestamp to.
    
    '''
    def select_pricipal_components(self, fVectors, nComponents):
        pca_matrix = np.zeros((fVectors.shape[0], int(fVectors.shape[1]/self.timestep_size*nComponents)))
        self.timestep_pca_models = []
        for i in range(0, fVectors.shape[1], self.timestep_size):
            pca = PCA(n_components=nComponents)
            pca_matrix[:, int(i/self.timestep_size)*nComponents:int(i/self.timestep_size+1)*nComponents] = pca.fit_transform(fVectors[:, i:i+self.timestep_size])
            self.timestep_pca_models.append(pca)
        return pca_matrix


    def plot_vectors(self, fVectors):
        fig = plt.figure(figsize=(5, 5))

        ax = fig.add_subplot(111)
        ax.set_title('colorMap')
        plt.imshow(fVectors)
        ax.set_aspect('equal')

        cax = fig.add_axes([0.1, 0.1, 0.1, 0.1])
        cax.get_xaxis().set_visible(False)
        cax.get_yaxis().set_visible(False)
        cax.patch.set_alpha(0)
        cax.set_frame_on(False)
        plt.colorbar(orientation='vertical')
        plt.show()

    def set_plot_params(self):
        # Fiddle with figure settings here:
        plt.rcParams['figure.figsize'] = (10, 8)
        plt.rcParams['font.size'] = 14
        plt.rcParams['image.cmap'] = 'plasma'
        plt.rcParams['axes.linewidth'] = 2
        # Set the default colour cycle (in case someone changes it...)
        from cycler import cycler
        cols = plt.get_cmap('tab10').colors
        plt.rcParams['axes.prop_cycle'] = cycler(color=cols)

    def verify_linearity(self, H):
        print(H.shape)
        dis_functional_vect = np.array([0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0, 0, 0, 0, 0, 0, 0, 0, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0, 0, 0, 0, 0, 0, 0, 0, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0, 0, 0, 0, 0, 0, 0, 0, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0, 0, 0, 0, 0, 0, 0, 0, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0, 0, 0, 0, 0, 0, 0, 0, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0, 0, 0, 0, 0, 0, 0, 0, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0, 0, 0, 0, 0, 0, 0, 0, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0, 0, 0, 0, 0, 0, 0, 0, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0, 0, 0, 0, 0, 0, 0, 0, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0, 0, 0, 0, 0, 0, 0, 0, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0, 0, 0, 0, 0, 0, 0, 0, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0, 0, 0, 0, 0, 0, 0, 0, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0, 0, 0, 0, 0, 0, 0, 0, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0, 0, 0, 0, 0, 0, 0, 0, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0, 0, 0, 0, 0, 0, 0, 0, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0, 0, 0, 0, 0, 0, 0, 0, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0, 0, 0, 0, 0, 0, 0, 0, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0, 0, 0, 0, 0, 0, 0, 0, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0, 0, 0, 0, 0, 0, 0, 0, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0, 0, 0, 0, 0, 0, 0, 0, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0, 0, 0, 0, 0, 0, 0, 0, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0, 0, 0, 0, 0, 0, 0, 0, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0, 0, 0, 0, 0, 0, 0, 0, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0, 0, 0, 0, 0, 0, 0 ])
        blink_functional_vect = np.array([1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0 ])
        combined_functional_vect = np.array([1.8, 1.8, 1.8, 1.8, 1.8, 1.8, 1.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 1.8, 1.8, 1.8, 1.8, 1.8, 1.8, 1.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 1.8, 1.8, 1.8, 1.8, 1.8, 1.8, 1.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 1.8, 1.8, 1.8, 1.8, 1.8, 1.8, 1.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 1.8, 1.8, 1.8, 1.8, 1.8, 1.8, 1.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 1.8, 1.8, 1.8, 1.8, 1.8, 1.8, 1.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 1.8, 1.8, 1.8, 1.8, 1.8, 1.8, 1.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 1.8, 1.8, 1.8, 1.8, 1.8, 1.8, 1.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1.8, 1.8, 1.8, 1.8, 1.8, 1.8, 1.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 1.8, 1.8, 1.8, 1.8, 1.8, 1.8, 1.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 1.8, 1.8, 1.8, 1.8, 1.8, 1.8, 1.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 1.8, 1.8, 1.8, 1.8, 1.8, 1.8, 1.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 1.8, 1.8, 1.8, 1.8, 1.8, 1.8, 1.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 1.8, 1.8, 1.8, 1.8, 1.8, 1.8, 1.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 1.8, 1.8, 1.8, 1.8, 1.8, 1.8, 1.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 1.8, 1.8, 1.8, 1.8, 1.8, 1.8, 1.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0.8, 1.8, 1.8, 1.8, 1.8, 1.8, 1.8, 1.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 1.8, 1.8, 1.8, 1.8, 1.8, 1.8, 1.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 1.8, 1.8, 1.8, 1.8, 1.8, 1.8, 1.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 1.8, 1.8, 1.8, 1.8, 1.8, 1.8, 1.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 1.8, 1.8, 1.8, 1.8, 1.8, 1.8, 1.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 1.8, 1.8, 1.8, 1.8, 1.8, 1.8, 1.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 1.8, 1.8, 1.8, 1.8, 1.8, 1.8, 1.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 1.8, 1.8, 1.8, 1.8, 1.8, 1.8, 1.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1.8, 1.8, 1.8, 1.8, 1.8, 1.8, 1.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 1.8, 1.8, 1.8, 1.8, 1.8, 1.8, 1.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 1.8, 1.8, 1.8, 1.8, 1.8, 1.8, 1.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 1.8, 1.8, 1.8, 1.8, 1.8, 1.8, 1.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 1.8, 1.8, 1.8, 1.8, 1.8, 1.8, 1.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 1.8, 1.8, 1.8, 1.8, 1.8, 1.8, 1.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 1.8, 1.8, 1.8, 1.8, 1.8, 1.8, 1.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 1.8, 1.8, 1.8, 1.8, 1.8, 1.8, 1.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 1, 1, 1, 1, 1, 1, 1, 0, 0 ])
        combined_functional_calculated = np.add(dis_functional_vect, blink_functional_vect)
        print("absolute difference between the sum of the vectors of the individual program and the vector for the combined program")
        print(np.sum(np.absolute(np.subtract(combined_functional_calculated, combined_functional_vect))))

        dis_reduced_vect = np.array([0.21773304124725593, 0.15780079866750202, 0.5548162691158779, 2.0116191911800874, 0.3398289949085981, 0.2891221353272636, 0.16770114873581646, 0.029376218258233232, 0, 0.41414896080742447])
        blink_reduced_vect = np.array([0.6475729083360865, 0.3601037191734303, 0.23024349735078564, 0.45890073919051655, 0, 0.06911854335013824, 0.08466504690968028, 0.11907176629286395, 0.3783643495909749, 0.09686393213294524])
        combined_reduced_vect = np.array([1.0065418773569341, 0.5744285538603285, 0.3781890978465389, 0.5832577920970687, 0, 0.09027410294225965, 0.23327789828451942, 0.19846662063824042, 0.48679149718601095, 0.1691640084875151])
        combined_reduced_vect_calculated = np.add(dis_reduced_vect, blink_reduced_vect)


        dis_reduced_vect_inv = dis_reduced_vect.dot(H)
        blink_reduced_vect_inv = blink_reduced_vect.dot(H)
        combined_reduced_vect_inv = combined_reduced_vect.dot(H)
        combined_reduced_vect_calculated_inv = combined_reduced_vect_calculated.dot(H)

        print("absolute difference between inverse of sum of components and inverse of combined program")
        print(np.sum(np.absolute(np.subtract(combined_reduced_vect_calculated_inv, combined_reduced_vect_inv))))

        print("correlation between original and inverse")
        print(correlation(combined_functional_vect, combined_reduced_vect_inv))

        print("absolute distance beween sum of reduced components and reduced combined program")
        print(np.sum(np.absolute(np.subtract(combined_reduced_vect_calculated, combined_reduced_vect))))
        print("absolute distance between dis program and combined program")
        print(np.sum(np.absolute(np.subtract(dis_reduced_vect, combined_reduced_vect))))
        print("absolute distance between blink program and combined program")
        print(np.sum(np.absolute(np.subtract(blink_reduced_vect, combined_reduced_vect))))



    def perform_nnmf(self, fVectors):
        min = np.amin(fVectors, axis=None, out=None)
        offset = 0
        if min < 0:
            offset = abs(min)
        fVectors = fVectors + offset
        model = NMF(n_components=10)
        print("Fitting NMF model")
        print(fVectors.shape)
        W = model.fit_transform(fVectors)
        H = model.components_
        print(W.shape)
        print(H.shape)
        print(W)

        min = np.amin(W)
        max = np.amax(W)
        print(min)
        print(max)

        ax = plt.matshow(W[0:300, :].T)
        plt.ylabel("components")
        plt.xlabel("programs")
        plt.title("Reduced vectors");
        plt.show()

        self.verify_linearity(H)

        return W

    def perform_mssa(self, fVectors, n_components):
        L = 150  # Length of the time window
        mssa = MSSA(n_components='variance_threshold', variance_explained_threshold=0.99, window_size=L, verbose=True)
        mssa.fit(fVectors)
        idx = 3
        indexes = np.arange(mssa.components_.shape[1])
        '''for comp in range(10):
            fig, ax = plt.subplots(figsize=(18, 7))
            ax.plot(indexes, fVectors[:, idx], lw=3, alpha=0.2, c='k',
                    label="program 3")
            ax.plot(indexes, mssa.components_[idx, :, comp], lw=3, c='steelblue', alpha=0.8,
                    label='component={}'.format(comp))
            ax.legend()
            plt.show()'''

        base_dir = "./results/test3"
        self.create_directory(base_dir)

        for idx in [-1, -2, -3]:
            self.create_directory(base_dir + "/program{}".format(idx))
            cumulative_recon = np.zeros_like(fVectors[:, idx])
            for comp in range(mssa.components_.shape[2]):
                fig, ax = plt.subplots(figsize=(18, 7))
                current_component = mssa.components_[idx, :, comp]
                cumulative_recon = cumulative_recon + current_component

                ax.plot(indexes, fVectors[:, idx], lw=3, alpha=0.2, c='k',
                        label="program 3")
                ax.plot(indexes, cumulative_recon, lw=3, c='darkgoldenrod', alpha=0.6,
                        label='cumulative'.format(comp))
                ax.plot(indexes, current_component, lw=3, c='steelblue', alpha=0.8, label='component={}'.format(comp))

                ax.legend()
                plt.savefig("results/test3/program{}/cumulation_of_{}_components_for_index{}_2".format(idx, comp, idx))
                plt.show()

        print(mssa.component_ranks_[0:10])
        print(mssa.component_ranks_explained_variance_[0:10])

        total_comps = mssa.components_[0, :, :]
        print(total_comps.shape)

        total_wcorr = mssa.w_correlation(total_comps)
        total_wcorr_abs = np.abs(total_wcorr)
        fig, ax = plt.subplots(figsize=(12, 9))
        sns.heatmap(np.abs(total_wcorr_abs), cmap='coolwarm', ax=ax)
        ax.set_title('component w-correlations')

        plt.show()
        plt.savefig("results/test3/correlation_matrix")
        print(mssa.component_ranks_.shape)
        return mssa.component_ranks_.T

    def create_directory(self, dirName):
        if not os.path.exists(dirName):
            os.mkdir(dirName)
            print("Directory ", dirName, " Created ")
        else:
            print("Directory ", dirName, " already exists")


    def SSA(self, fVectors):
        N = 500  # number of time steps
        L = 250   # Length of the time window
        t = np.arange(0, N)
        #F = fVectors[7, :]  # For now only take one time series
        F = np.unique(fVectors, axis=0)
        F = F.sum(axis=0)
        mi = F.min()
        F = F - mi
        ma = F.max()
        F = F/ma
        K = N - L + 1   # Number of cols in the trajectory matrix

        '''plt.plot(t, F, lw=2.5)
        plt.legend(["Toy Series ($F$)", "Trend", "Periodic #1", "Periodic #2", "Noise"])
        plt.xlabel("$t$")
        plt.ylabel("$F(t)$")
        plt.title("The Toy Time Series and its Components");
        plt.show()'''

        X = np.column_stack(F[i:i+L] for i in range(0, K))

        ax = plt.matshow(X)
        plt.xlabel("$L$-Lagged Vectors")
        plt.ylabel("$K$-Lagged Vectors")
        plt.colorbar(ax.colorbar, fraction=0.025)
        ax.colorbar.set_label("$F(t)$")
        plt.title("The Trajectory Matrix for the Toy Time Series");
        plt.show()

        d = np.linalg.matrix_rank(X)
        print(d)
        U, Sigma, V = np.linalg.svd(X)
        u_invertable = np.dot(U, U.T)
        v_invertable = np.dot(V, V.T)
        u = U
        vh = V

        V = V.T
        # Calculate the elementary matrices of X, storing them in a multidimensional NumPy array.
        # This requires calculating sigma_i * U_i * (V_i)^T for each i, or sigma_i * outer_product(U_i, V_i).
        # Note that Sigma is a 1D array of singular values, instead of the full L x K diagonal matrix.
        X_elem = np.array([Sigma[i] * np.outer(U[:, i], V[:, i]) for i in range(0, d)])

        # Quick sanity check: the sum of all elementary matrices in X_elm should be equal to X, to within a
        # *very small* tolerance:
        if not np.allclose(X, X_elem.sum(axis=0), atol=1e-10):
            print("WARNING: The sum of X's elementary matrices is not equal to X!")

        n = min(16,
                d)  # In case d is less than 12 for the toy series. Say, if we were to exclude the noise component...
        for i in range(n):
            plt.subplot(4, 4, i + 1)
            t = "$\mathbf{X}_{" + str(i) + "}$"
            self.plot_2d(X_elem[i], title=t)
        plt.tight_layout()
        plt.show()

        sigma_sumsq = (Sigma ** 2).sum()
        fig, ax = plt.subplots(1, 2, figsize=(14, 5))
        ax[0].plot(Sigma ** 2 / sigma_sumsq * 100, lw=2.5)
        ax[0].set_xlim(0, 11)
        ax[0].set_title("Relative Contribution of $\mathbf{X}_i$ to Trajectory Matrix")
        ax[0].set_xlabel("$i$")
        ax[0].set_ylabel("Contribution (%)")
        ax[1].plot((Sigma ** 2).cumsum() / sigma_sumsq * 100, lw=2.5)
        ax[1].set_xlim(0, 11)
        ax[1].set_title("Cumulative Contribution of $\mathbf{X}_i$ to Trajectory Matrix")
        ax[1].set_xlabel("$i$")
        ax[1].set_ylabel("Contribution (%)");

        plt.show()

        # Try to decompose one of the fVectors based on the components extracted from SVD
        timeseries = fVectors[7, :]
        traj_matrix = np.array([np.column_stack(fVectors[k, i:i + L] for i in range(0, K)) for k in range(fVectors.shape[0])])

        for i in range(10):
            ax = plt.matshow(traj_matrix[i])
            plt.xlabel("$L$-Lagged Vectors")
            plt.ylabel("$K$-Lagged Vectors")
            plt.colorbar(ax.colorbar, fraction=0.025)
            ax.colorbar.set_label("$F(t)$")
            plt.title("The Trajectory Matrix for the Toy Time Series");
            plt.show()

        comps = np.array([np.dot(np.dot(u.T, traj_matrix[k]), vh.T) for k in range(traj_matrix.shape[0])])
        comps = np.array([[comps[k][i][i] for i in range(comps.shape[1])] for k in range(comps.shape[0])])
        print("The reduced components:")
        print(comps)
        print(comps.shape)
        return comps

    # A simple little 2D matrix plotter, excluding x and y labels.
    def plot_2d(self, matrix, title=""):
        plt.imshow(matrix)
        plt.xticks([])
        plt.yticks([])
        plt.title(title)



