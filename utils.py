

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