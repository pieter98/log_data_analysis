import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN as dbs
from sklearn.cluster import AffinityPropagation as afp
from sklearn.cluster import SpectralClustering as spc
from sklearn.manifold import TSNE as t_sne
from sklearn.preprocessing import RobustScaler
from sklearn import metrics as m
import numpy as np



class ClusteringAnalysis:

    def __init__(self):
        None


    def cluster_programs(self, affinity_matrix, true_labels):
        #print("Clustering using DBSCAN")
        #self.cluster_DBSCAN(distance_matrix)
        print("Clustering using Affinity prop")
        self.cluster_Affinity(affinity_matrix, true_labels)


    def cluster_DBSCAN(self, affinity_matrix, true_labels):
        eps = 0.8
        print("eps = {}".format(eps))
        clustering = dbs(eps=eps, metric="precomputed").fit(affinity_matrix)
        labels = clustering.labels_
        n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
        n_noise_ = list(labels).count(-1)
        print('Estimated number of clusters: %d' % n_clusters_)
        print('Estimated number of noise points: %d' % n_noise_)

    def cluster_Affinity(self, affinity_matrix, true_labels):
        clustering = afp(affinity="precomputed").fit(affinity_matrix)
        labels = clustering.labels_
        centers = clustering.cluster_centers_
        n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
        n_noise_ = list(labels).count(-1)
        print('Estimated number of clusters: %d' % n_clusters_)
        print('Estimated number of noise points: %d' % n_noise_)
        print("Homogeneity: %0.3f" % metrics.homogeneity_score(true_labels, labels))
        print("Completeness: %0.3f" % metrics.completeness_score(true_labels, labels))
        print("V-measure: %0.3f" % metrics.v_measure_score(true_labels, labels))
        print("Adjusted Rand Index: %0.3f"
              % metrics.adjusted_rand_score(true_labels, labels))
        print("Adjusted Mutual Information: %0.3f"
              % metrics.adjusted_mutual_info_score(true_labels, labels))

    def cluster_spectral(self, affinity_matrix, true_labels):
        spectral  = spc(n_clusters=50, affinity="precomputed")
        clustering = spectral.fit(affinity_matrix)
        labels = clustering.labels_
        n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
        print('Estimated number of clusters: %d' % n_clusters_)
        return (labels, n_clusters_)

    def cluster_tsne(self, affinity_matrix, color_labels, title="TSNE", n_components=2, perplexity=30):
        tsne = t_sne(n_components=n_components, metric="precomputed", perplexity=perplexity)
        embedding = tsne.fit_transform(affinity_matrix)
        return embedding


    def affinity_to_distance_matrix_normalized(self, affinity_matrix):
        print(affinity_matrix)
        max = np.amax(affinity_matrix)
        print(max)
        distance_matrix = (affinity_matrix - max) * -1  # convert affinity matrix to distance matrix
        print(distance_matrix)
        transformer = RobustScaler(with_centering=True).fit(distance_matrix)
        normalized_distance_matrix = transformer.transform(distance_matrix)

        #normalized_distance_matrix = distance_matrix / max  # normalize distance matrix
        print(normalized_distance_matrix)
        min = np.amin(normalized_distance_matrix)
        normalized_distance_matrix = normalized_distance_matrix - min
        plt.imshow(normalized_distance_matrix, cmap='rainbow', interpolation='none')
        plt.show()
        return normalized_distance_matrix


    def cluster_t_sne_result(self, embedding, true_labels):
        clustering = dbs(eps=2.5, metric="euclidean").fit(embedding)

        core_sample_indices = clustering.core_sample_indices_
        cluster_centers_for_each_sample = clustering.components_
        labels = clustering.labels_

        n_clusters = len(set(labels))
        noise = list(labels).count(-1)

        cluster_centers = np.unique(cluster_centers_for_each_sample, axis=0)

        print('Estimated number of clusters: %d' % n_clusters)
        print('Estimated number of noise points: %d' % noise)
        print("Homogeneity: %0.3f" % m.homogeneity_score(true_labels, labels))
        print("Completeness: %0.3f" % m.completeness_score(true_labels, labels))
        print("V-measure: %0.3f" % m.v_measure_score(true_labels, labels))
        print("Adjusted Rand Index: %0.3f"
              % m.adjusted_rand_score(true_labels, labels))
        print("Adjusted Mutual Information: %0.3f"
              % m.adjusted_mutual_info_score(true_labels, labels))
        print("Silhouette Coefficient: %0.3f"
              % m.silhouette_score(embedding, labels, metric='sqeuclidean'))

        return labels, n_clusters






