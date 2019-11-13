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



class FunctionalAnalyzer:


    def __init__(self, database_connection, experimentId):
        self.experimentId = experimentId
        self.db_connection = database_connection
        self.timestep_size = 32 # The number of features logged in each timestep.
        self.nr_of_transforms = 0
        self.HMat = []


    def analyze(self, dataset_id, log_id="log", save_results=True, method="hadamard", embedding_dims=3, incremental=False):
        print("Starting functional analysis")

        if incremental:
            return self.analize_inc(dataset_id, log_id=log_id, save_results=save_results, method=method, embedding_dims=embedding_dims)

        vectorCursor = self.db_connection.get_fid_vectors(dataset_id, log_name=log_id)
        tmpLabels = self.db_connection.get_f_labels(dataset_id, log_name=log_id)
        tmpCodeTrees = self.db_connection.get_f_programs(dataset_id, log_name=log_id)
        tmpStepLabels = self.db_connection.get_f_steplabels(dataset_id, log_name=log_id)

        steplabels = []
        '''for label in tmpStepLabels:
            steplabels.append(label['steplabel'])'''

        labels = []
        for label in tmpLabels:
            labels.append(label['label']) # pathlabel for new method

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
        '''fVectors = fVectors[0:4000:5, :]
        fVectors, unique_indices = np.unique(fVectors, return_index=True, axis=0)
        labels = labels[0:4000:5]
        labels = np.array(labels)[unique_indices]'''

        fVectors = np.nan_to_num(fVectors)

        reducedVectors = np.array([])

        if method == "hadamard":
            rows = fVectors.shape[0]
            nr_of_parts = 10
            partsize = rows//nr_of_parts
            rest = rows % nr_of_parts
            # Perform hadamard analysis

            if rows >= nr_of_parts:
                part = np.nan_to_num(fVectors[0:partsize, :])
                reducedVectors = self.hadamard_analysis(part)
                for r in range(1, nr_of_parts):
                    part = np.nan_to_num(fVectors[r*partsize:(r+1)*partsize, :])
                    reducedVectors = np.vstack((reducedVectors, self.hadamard_analysis(part)))
                if rest > 0:
                    part = np.nan_to_num(fVectors[(nr_of_parts) * partsize:, :])
                    reducedVectors = np.vstack((reducedVectors, self.hadamard_analysis(part)))
            else:
                reducedVectors = self.hadamard_analysis(fVectors)

            fig, ax = plt.subplots(1, 1)
            plot = ax.matshow(reducedVectors[0:1000, :], norm=colors.SymLogNorm(linthresh=0.01, linscale=0.01,
                                                                                vmin=reducedVectors.min(),
                                                                                vmax=reducedVectors.max()),
                              cmap='PuBu_r')
            fig.colorbar(plot, ax=ax, extend='max')
            plt.show()
        elif method == "nnmf":
            # Perform NNMF
            reducedVectors = self.perform_nnmf(fVectors)
        elif method == "mssa":
            # Perform MSSA
            reducedVectors = self.perform_mssa(fVectors.T, 10)
        elif method == "fourier":
            # Perform fourier analysis
             reducedVectors = self.fourier_analysis(fVectors)
        elif method == "ssa":
            # Perform SSA on single time vector (assumes
            reducedVectors = self.SSA(fVectors)



        if save_results:
            np.save("./files/reduced_vectors" + "_functional" + self.experimentId, reducedVectors)

        if method == "autoencode":

            # fVectors = np.nan_to_num(fVectors)
            embedding = self.autoencode(fVectors, labels)
        else:
            embedding = self.cluster_tsne(reducedVectors, embedding_dims, 30)

        #self.plot_embedding(embedding, labels)

        if save_results:
            self.save_experiment(embedding, code_trees, labels)
        '''
        #self.plot_vectors(fVectors)
        reducedVectors = self.select_pricipal_components(fVectors, 5)
        self.plot_vectors(reducedVectors[0:500, :])

        embedding = self.cluster_tsne(reducedVectors, 3, 50)

        self.plot_embedding(embedding, labels)

        '''

        return embedding, code_trees, labels, steplabels, reducedVectors

    def analize_inc(self, dataset_id, log_id="log", save_results=True, method="hadamard", embedding_dims=3):
        print("incremental")

        vectorCursor = self.db_connection.get_fid_vectors(dataset_id, log_name=log_id)
        tmpLabels = self.db_connection.get_f_labels(dataset_id, log_name=log_id)
        tmpCodeTrees = self.db_connection.get_f_programs(dataset_id, log_name=log_id)

        reducedVectors = []
        labels = []
        code_trees = []
        for (vector, label, ct) in zip(vectorCursor, tmpLabels, tmpCodeTrees):
            tmpVectors = []
            print("next vector")
            code_trees.append(ct["xml_blocks"])
            labels.append(label['label'])
            if isinstance(vector["vector"], str):
                tmpVectors.append(json.loads(vector["vector"]))
            else:
                tmpVectors.append(vector["vector"])
            fVectors = np.array(tmpVectors, dtype=np.float32)
            fVectors = np.nan_to_num(fVectors)
            reducedVector = []

            if method == "hadamard":
                reducedVector = self.hadamard_analysis(fVectors)
                reducedVectors.append(reducedVector.reshape((reducedVector.shape[1],)))
            else:
                raise Exception("Incremental only supported on Hadamard method.")

        reducedVectors = np.array(reducedVectors)

        fig, ax = plt.subplots(1, 1)
        plot = ax.matshow(reducedVectors[0:1000, :], norm=colors.SymLogNorm(linthresh=0.01, linscale=0.01,
                                                                            vmin=reducedVectors.min(),
                                                                            vmax=reducedVectors.max()),
                          cmap='PuBu_r')
        fig.colorbar(plot, ax=ax, extend='max')
        plt.show()

        if save_results:
            np.save("./files/reduced_vectors" + "_functional" + self.experimentId, reducedVectors)

        if method == "autoencode":
            embedding = self.autoencode(fVectors, labels)
        else:
            embedding = self.cluster_tsne(reducedVectors, embedding_dims, 30)

        self.plot_embedding(embedding, labels)

        if save_results:
            self.save_experiment(embedding, code_trees, labels)
        '''
        #self.plot_vectors(fVectors)
        reducedVectors = self.select_pricipal_components(fVectors, 5)
        self.plot_vectors(reducedVectors[0:500, :])

        embedding = self.cluster_tsne(reducedVectors, 3, 50)

        self.plot_embedding(embedding, labels)

        '''

        return embedding, code_trees, labels, reducedVectors

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
        tsne = t_sne(n_components=n_components, perplexity=perplexity, metric='cosine')
        #tsne = t_sne(n_components=n_components, perplexity=perplexity, metric=self.hierarchcal_distance)
        embedding = tsne.fit_transform(fVectors)
        return embedding

    def hierarchcal_distance(self, A, B):
        distance = 0
        len_start = len(A)
        Ared = A
        Bred = B
        distance += euclidean(Ared, Bred)
        i = 2
        while len(Ared) > 1:
            C = np.ones(i)/i
            Ared = np.convolve(A, C, 'valid')
            Bred = np.convolve(B, C, 'valid')
            distance += euclidean(Ared, Bred)
            i+=1

        distance = distance / (len_start - 1)

        return distance


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


    def fourier_analysis(self, fVectors):
        N = 909
        L = 128
        K = N - L + 1
        fourier_vector = np.array(
            [np.concatenate([self.fourier_transform(fVectors[k, i:i + L]) for i in range(0, K, 128)]) for k in range(fVectors.shape[0])])
        model = PCA(n_components=15)
        embedding = model.fit_transform(fourier_vector)
        return embedding


    def hadamard_analysis(self, fVectors):
        state_vect_length = 32
        fVectors = fVectors.reshape((fVectors.shape[0], state_vect_length, int(fVectors.shape[1]/state_vect_length)))
        N = fVectors.shape[2]   # Number of elements per vector
        L = 512 # Length of the hadamard transform
        remainder = N % L
        padding_length = L - remainder
        fVectors = np.pad(fVectors, ((0, 0), (0, 0), (0, padding_length)), 'constant', constant_values=(0, 0))    # Add padding at the end to the nearest multiple of L
        fVectors = fVectors.reshape((fVectors.shape[0], fVectors.shape[1]*fVectors.shape[2]))
        N = fVectors.shape[1]  # Number of elements per vector
        K = int(N/L)
        self.nr_of_transforms = 0
        fourier_vector = np.array(
            [self.hadamard_vector_to_freq_energy_vector([self.hadamard_transform(fVectors[k, (i * L):(i * L) + L]) for i in range(0, K)]) for k in range(fVectors.shape[0])])

        embedding = fourier_vector
        return embedding

    def hadamard_vector_to_freq_energy_vector(self, hadamard_vector):
        hadamard_vector = np.abs(hadamard_vector)
        frequency_vect = np.sum(hadamard_vector, axis=0)
        norm = np.linalg.norm(frequency_vect)
        frequency_vect = frequency_vect/norm if norm != 0 else frequency_vect
        energy_vect = np.sum(np.absolute(hadamard_vector), axis=1, dtype="float32")
        norm = np.linalg.norm(energy_vect)
        energy_vect = energy_vect/norm if norm != 0 else energy_vect
        #energy_vect = energy_vect/256
        freq_energy_vect = np.concatenate((frequency_vect, energy_vect))
        #return energy_vect
        return freq_energy_vect

    def fourier_transform(self, vector):
        L = vector.shape[0]
        DFTMat = np.array([[cmath.exp(((-2 * cmath.pi * complex(0, 1)) / L) * (j * k)) for j in range(L)] for k in range(L)])
        fourier_vector = DFTMat.dot(vector)
        return fourier_vector

    def hadamard_transform(self, vector):
        self.nr_of_transforms += 1
        L = vector.shape[0]
        if (math.ceil(math.log2(L)) != math.floor(math.log2(L))):
            raise Exception("The vector length is not a power of 2")
        if len(self.HMat) == 0:
            HMat = scipy.linalg.hadamard(L)
            # Convert the hadamard matrix to a walsh matrix (same thing but with rows ordered by the number of sign changes)
            sign_changes = np.array(
                [np.sum([HMat[row][col - 1] != HMat[row][col] for col in range(1, len(HMat[row]))]) for row in range(len(HMat))])
            i = np.argsort(sign_changes)
            HMat = HMat[i, :]
            self.HMat = HMat

        HMat = self.HMat
        if np.sum(vector) != 0:
            print("not zero")
        hadamard_vector = HMat.dot(vector)
        if self.nr_of_transforms % 200 == 0:
            print("{} tranforms performed".format(self.nr_of_transforms))
        return hadamard_vector

    def SSA(self, fVectors):
        N = 909  # number of time steps
        L = 400   # Length of the time window
        K = N - L + 1  # Number of cols in the trajectory matrix
        u, vh = self.get_ssa_transformation_matrices(fVectors, N, L, K)

        #u, vh = self.get_uniform_ssa_transformation_matrices(N, L, K)


        # Try to decompose one of the fVectors based on the components extracted from SVD
        traj_matrix = np.array([np.column_stack(fVectors[k, i:i + L] for i in range(0, K)) for k in range(fVectors.shape[0])])



        '''for i in range(10):
            ax = plt.matshow(traj_matrix[50+i])
            plt.xlabel("$L$-Lagged Vectors")
            plt.ylabel("$K$-Lagged Vectors")
            plt.colorbar(ax.colorbar, fraction=0.025)
            ax.colorbar.set_label("$F(t)$")
            plt.title("The Trajectory Matrix for the Toy Time Series")
            plt.show()


        # Plot the variance-covariance matrix for the first 10 trajectory matrices
        for i in range(10):
            ax = plt.matshow(np.ma.cov(traj_matrix[50+i]))
            plt.xlabel("$L$-Lagged Vectors")
            plt.ylabel("$K$-Lagged Vectors")
            plt.colorbar(ax.colorbar, fraction=0.025)
            ax.colorbar.set_label("$F(t)$")
            plt.title("The variance covariance Matrix for the Toy Time Series")
            plt.show()'''



        singular_value_matrix = np.array([np.dot(np.dot(u.T, traj_matrix[k]), vh.T) for k in range(traj_matrix.shape[0])])
        comps = np.array([[singular_value_matrix[k][i][i] for i in range(singular_value_matrix.shape[1])] for k in range(singular_value_matrix.shape[0])])
        print("The reduced components:")
        print(comps)
        print(comps.shape)
        '''print("The component vectors of the recored programs are:")
        print(comps[-3])
        print(comps[-2])
        print(comps[-1])'''

        # Reconstruct trajectory matrix for last three components
        reduced_rec_comps = singular_value_matrix[-3:, :, :]
        # We can reduce the components even more by setting their respective values in the singular value matrix to zero
        # Here we try to reduce the number of components in the reduced_rec_comps vector
        val_to_keep = 50
        reduced_rec_comps[:, val_to_keep:, :] = 0
        reduced_rec_comps[:, :, val_to_keep:] = 0
        print(reduced_rec_comps)
        reconstructed_traj_mat = np.array([np.dot(np.dot(u, reduced_rec_comps[k]), vh) for k in range(reduced_rec_comps.shape[0])])


        # Visualize reconstructed trajectories (this only has meaning if the recorded programs are added at the end.
        for i in range(3):
            plt.subplot(1, 4, i + 1)
            t = "$\mathbf{X}_{" + str(i) + "}$"
            self.plot_2d(reconstructed_traj_mat[i], title=t)
        plt.subplot(1, 4, 4)
        t = "$\mathbf{X}_{" + str(4) + "}$"
        self.plot_2d(reconstructed_traj_mat[0] + reconstructed_traj_mat[2], title=t)
        plt.tight_layout()
        plt.show()

        # print the first rows of the trajectory matrix
        '''print("inverted feature vectors of the recorded programs")
        for i in range(3):
            print(reconstructed_traj_mat[i, 0, :])'''

        print("Normalized distance between inversion of sum and inversion of combined program id")
        traj_mat_size = reconstructed_traj_mat.shape[1] * reconstructed_traj_mat.shape[2]
        print((reconstructed_traj_mat[0, :, :] + reconstructed_traj_mat[2, :, :] - reconstructed_traj_mat[1, :, :]).sum()/traj_mat_size)

        print("shape of reconstructed trajectory matrix")
        print(reconstructed_traj_mat.shape)

        return np.real(comps[:, :val_to_keep])

    def get_ssa_transformation_matrices(self, fVectors, N, L, K):
        t = np.arange(0, N)
        # F = fVectors[7, :]  # For now only take one time series
        F = np.unique(fVectors, axis=0)
        F = np.nansum(F, axis=0)
        mi = F.min()
        F = F - mi
        ma = F.max()
        F = F / ma

        '''plt.plot(t, F, lw=2.5)
        plt.legend(["Toy Series ($F$)", "Trend", "Periodic #1", "Periodic #2", "Noise"])
        plt.xlabel("$t$")
        plt.ylabel("$F(t)$")
        plt.title("The Toy Time Series and its Components");
        plt.show()'''

        X = np.column_stack(F[i:i + L] for i in range(0, K))

        ax = plt.matshow(np.real(X))
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

        return u, vh


    def get_uniform_ssa_transformation_matrices(self, N, L, K):
        '''fVectors = np.array([[1 if (N//(j+1)) == 0 or (i % (N//(j+1))) < ((N // (j + 1))//2) else 0 for i in range(N)] for j in range(N)])
        #print(fVectors)
        fVectors = np.unique(fVectors, axis=0)
        maybe_identity = fVectors.dot(fVectors.T)
        self.plot_2d(maybe_identity)'''

        u = np.array([[cmath.exp(((-2*cmath.pi*complex(0, 1))/L) * (j * k)) for j in range(L)] for k in range(L)])
        d = np.linalg.matrix_rank(u)
        vh = np.identity(K)
        u = u * (1/cmath.sqrt(L))
        u_h = np.array(np.matrix(u).getH())
        maybe_identity = u_h.dot(u)
       # self.plot_2d(np.real(maybe_identity))
        #plt.show()

        #self.plot_2d(np.real(u), title="DFT matrix")
        W, v = np.linalg.eig(u)
        #self.plot_2d(np.real(v), title="Eigenvectors of DFT matrix")



        X_elem = np.array([W[i] * np.outer(v[:, i], vh[:, i]) for i in range(0, d)])

        n = min(32,
                d)  # In case d is less than 12 for the toy series. Say, if we were to exclude the noise component...
        for i in range(n):
            plt.subplot(4, 8, i + 1)
            t = "$\mathbf{X}_{" + str(i) + "}$"
            self.plot_2d(X_elem[i+50], title=t)
        plt.tight_layout()
        plt.show()

        return u, vh
        #return self.get_ssa_transformation_matrices(fVectors, N, L, K)

    # A simple little 2D matrix plotter, excluding x and y labels.
    def plot_2d(self, matrix, title=""):
        plt.imshow(np.real(matrix))
        plt.xticks([])
        plt.yticks([])
        plt.title(title)



    def autoencode(self, fVectors, labels):
        fVectors = (fVectors-fVectors.min())/(fVectors-fVectors.min()).max()
        avgFVectors = np.average(fVectors, 0)
        minibatch_size = 64
        batch_size = (fVectors.shape[0]//minibatch_size)*minibatch_size
        fVectors = fVectors[:batch_size, :]
        labels = labels[:batch_size]
        latent_dim = 3
        original_dim = fVectors.shape[1]
        intermediate_dim = 256
        epsilon_std = 1.0
        minibatch_size = 64
        epochs = 250

       # def kernel_init(shape):


        #encoder
        inputs = layers.Input(batch_shape=(minibatch_size, original_dim), name='encoder_input')
        resh = layers.Reshape((original_dim, 1))(inputs)
        conv_layer = layers.Conv1D(512, 512, strides=512, padding='same', activation='elu')(resh)
        flat = layers.Flatten()(conv_layer)
        #flat = layers.GlobalAveragePooling1D()(conv_layer)
        x = layers.Dense(intermediate_dim, activation='relu')(flat)
        z_mean = layers.Dense(latent_dim, name='z_mean')(x)
        z_log_var = layers.Dense(latent_dim, name='z_log_var', kernel_initializer='zeros')(x)

        def sampling(args):
            z_mean, z_log_var = args
            epsilon = K.random_normal(shape=(minibatch_size, latent_dim), mean=0.,
                                      stddev=epsilon_std)
            return z_mean + K.exp(z_log_var / 2) * epsilon

        z = layers.Lambda(sampling, output_shape=(latent_dim, ))([z_mean, z_log_var])

        #encoder = models.Model(inputs, [z_mean, z_log_var, z], name='encoder')
        #encoder.summary()

        # instantiate decoder model
        decoder_h = layers.Dense(intermediate_dim, activation='relu')
        decoder_mean = layers.Dense(original_dim, activation='sigmoid')
        h_decoded = decoder_h(z)
        x_decoded_mean = decoder_mean(h_decoded)

        def vae_loss(x, x_decoded_mean):
            print(x)
            print(x_decoded_mean)
            xent_loss = binary_crossentropy(x, x_decoded_mean)
            kl_loss = - 0.5 * K.sum(1 + z_log_var - K.square(z_mean) - K.exp(z_log_var), axis=-1)

            return xent_loss + kl_loss

        vae = models.Model(inputs, x_decoded_mean)
        adam = optimizers.adam(lr=0.1, decay=1e-2)
        vae.compile(optimizer='rmsprop', loss=vae_loss, metrics=["accuracy"])
        vae.summary()

        history = vae.fit(fVectors, fVectors, epochs=epochs, batch_size=minibatch_size, verbose=1)

        # Plot training & validation accuracy values
        plt.plot(history.history['accuracy'])
        plt.title('Model accuracy')
        plt.ylabel('Accuracy')
        plt.xlabel('Epoch')
        plt.legend(['Train', 'Test'], loc='upper left')
        plt.show()

        # Plot training & validation loss values
        plt.plot(history.history['loss'])
        plt.title('Model loss')
        plt.ylabel('Loss')
        plt.xlabel('Epoch')
        plt.legend(['Train', 'Test'], loc='upper left')
        plt.show()

        # build a model to project inputs on the latent space
        encoder = models.Model(inputs, z_mean)

        # display a 2D plot of the digit classes in the latent space
        x_test_encoded = encoder.predict(fVectors, batch_size=minibatch_size)
        self.plot_embedding(x_test_encoded, labels)
        return x_test_encoded

        '''lay.append(layers.Conv1D(100, 20, strides=1, padding='same', activation='relu', input_shape=(fVectors2.shape[1], 1)))
        lay.append(layers.GlobalAveragePooling1D())
        lay.append(layers.Dense(3))
        lay.append(layers.Dense(20))
        lay.append(layers.Dense(fVectors.shape[1]))

        for layer in lay:
            autoencoder.add(layer)
        print(autoencoder.summary())

        autoencoder.compile('adam', loss='binary_crossentropy')
        autoencoder.fit(x=fVectors2, y=fVectors, epochs=5)
        print("autoencoder fit")
        encoder = models.Sequential()
        for i in range(4):
            encoder.add(lay[i])
        encodings = encoder.predict(fVectors2)
        print("plotting")
        self.plot_embedding(encodings, labels)'''
