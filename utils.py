import numpy as np

class AnalysisUtils:

    def normalize_session_id_list(self, session_id_list):
        nr_of_mappings = 0
        id_mapping = {}
        normalized_session_ids = []
        for session_id in session_id_list:
            if session_id not in id_mapping:
                id_mapping[session_id] = nr_of_mappings
                nr_of_mappings += 1
            normalized_session_ids.append(id_mapping[session_id])
        return normalized_session_ids

    def save_experiment(self, experimentId, embedding, code_trees, labels, steplabels):
        # Save the embedded points in 2D/3D space to a file
        np.save("./files/session" + "_program" + experimentId, embedding)
        # Save the coresponding program xmls to a file
        np.save("./files/xml_trees_for_session" + "_program" + experimentId, code_trees)
        # Save the coresponding labels to a file
        np.save("./files/labels" + "_program" + experimentId, labels)
        #save the steplabels
        np.save("./files/steplabels" + "_program" + experimentId, steplabels)
        # TODO: Calculate the centroid of the clusters and get the two closest clusters for each cluster
        np.save("./files/nearby_cluster_pair_points" + "_program" + experimentId, [])