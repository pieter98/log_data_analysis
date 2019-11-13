from pymongo import MongoClient
import re
from my_enums import WorkshopType
from my_enums import FunctionalDataset
from bson import ObjectId

client = None
fix_database = None
create_database = None
full_database = None
fix_log = None
create_log = None
full_log = None


class DatabaseConnection:
    db_logs = []

    def __init__(self):
        self.client = MongoClient('localhost:27017')
        self.fix_database = self.client["BlocklyLogDebug"]
        self.create_database = self.client["BlocklyLogCreate"]
        self.generated_data_log = self.client["GeneratedDataLog"]
        self.generated2_data_log = self.client["Generated2"]
        self.recorded_data_log = self.client["RecordedDataLog"]

        self.fix_log = self.fix_database.log
        self.create_log = self.create_database.log
        self.generated_data_log = self.generated_data_log.log
        self.generated2_data_log = self.generated2_data_log.log
        self.recorded_data_log_log = self.recorded_data_log.log

        self.functional_data = []
        self.functional_data.append(self.client["FunctionalData"])
        self.functional_data.append(self.client["FunctionalData2"])
        self.functional_data.append(self.client["FunctionalRealDataCreate"])
        self.functional_data.append(self.client["FunctionalData3"])
        self.functional_data.append(self.client["FunctionalData4"])
        self.functional_data.append(self.client["FunctionalDataRecorded"])
        self.functional_data.append(self.client["FunctionalData5"])
        self.functional_data.append(self.client["FunctionalRealDataCreate2"])
        self.functional_data.append(self.client["FunctionalRealDataCreateSplit"])
        self.functional_data.append(self.client["FunctionalDataInteractiveClustering"])
        self.functional_data.append(self.client["FunctionalDataCreateMicroseconds"])
        self.functional_data_log = []

        for i in range(len(self.functional_data)):
            self.functional_data_log.append(self.functional_data[i].log)

        self.db_logs.append(self.create_log)
        self.db_logs.append(self.fix_log)
        self.db_logs.append(self.generated_data_log)
        self.db_logs.append(self.generated2_data_log)
        self.db_logs.append(self.recorded_data_log_log)
        self.get_ordered_session_ids()


    '''
    @brief This function returns a dictionarry of all session ids. Each id has a key to easily identify the session.
    @returns A dictionary containing a human readable identifier key and matching session id as value.
    '''
    def get_ordered_session_ids(self):
        ordered_session_ids = {}
        pipeline = [{"$match": {"event.name": "changedWorkspace"}}, {"$sort": {"timestamp": 1}}, {"$group": { "_id": "$sessionId"}}]
        create_ids = list(self.create_log.aggregate(pipeline))
        fix_ids = list(self.fix_log.aggregate(pipeline))
        for index, element in enumerate(create_ids):
            key = "C" + str(index)
            ordered_session_ids.update({key: element['_id']})
        for index, element in enumerate(fix_ids):
            key = "F" + str(index)
            ordered_session_ids.update({key: element['_id']})

        return ordered_session_ids

    '''
    @brief gets all xml code trees from the database.
    @param log the log to get the trees from (either create or debug)
    @returns A dictionarry with keys the id of the session and value a list of code trees constructed during this session.
    '''

    def get_all_programs_per_session(self, log):
        code_edits = log.find({'event.name': "changedWorkspace"})
        count = 0
        sessions = {}
        for entry in code_edits:
            session_id = entry['sessionId']
            if session_id in sessions.keys():
                sessions[session_id].append(entry['event']['data'])
            else:
                sessions[session_id] = [entry['event']['data']]

        for k in sessions.keys():
            count += 1

        return sessions


    '''
    @brief This function returns a list all events for each session_id which meet the filter criteria.
    @param start_date only return events after this timestamp (unix epochs).
    @param end_data only return events before this timestamp (unix epochs).
    @param workshopType only return events for this workshop type.
    @param session_id only return events for this workshop id (regex)
    @returns A list of objects, each object contains an attribute which contains the sessionid 
    and an attribute which contains a list of events for that session. 
    '''
    def get_code_trees_for(self, start_date=0, end_date=9999999999999, workshop_type=WorkshopType.BOTH, session_id=".*"):
        session_id_regex = re.compile("^" + session_id + "$", re.IGNORECASE)
        pipeline = [
            {
                "$match": {
                    "$and": [
                        {
                            "timestamp": {
                                "$gt": start_date
                            }
                        },
                        {
                            "timestamp": {
                                "$lt": end_date
                            }
                        },
                        {
                            "event.name": "changedWorkspace"
                        },
                        {
                            "sessionId": session_id_regex
                        }
                    ]
                }
            },
            {
                "$sort": {
                    "timestamp": 1
                }
            },
            {
                "$group": {
                    "_id": "$sessionId",
                    "eventsForSession": {
                        "$push": "$event"
                    },
                    "labelsForSession": {
                        "$push": "$structureLabelString"
                    }
                }
            }
        ]

        if workshop_type == WorkshopType.BOTH:
            code_trees_create = list(self.db_logs[WorkshopType.CREATE.value].aggregate(pipeline, allowDiskUse=True))
            code_trees_fix = list(self.db_logs[WorkshopType.FIX.value].aggregate(pipeline, allowDiskUse=True))
            code_trees = code_trees_create + code_trees_fix
        else:
            print(self.db_logs[workshop_type.value].count({}))
            code_trees = list(self.db_logs[workshop_type.value].aggregate(pipeline, allowDiskUse=True))

        return code_trees

    '''
    @brief this function adds an entry to the functional database
    @param experiment_id the identifier of the experiment
    @param vector functional identifier of the program in vector format
    @param xml_blocks the program in xml format
    '''
    def add_functional_log_entry(self, experiment_id, vector, xml_blocks, label, log_nr, log_name="log"):
        self.functional_data[int(log_nr)][log_name].insert_one({"experiment_id": experiment_id, "vector": vector, "xml_blocks": xml_blocks, "label": label})

    def update_functional_log_entry(self, mongo_id, experiment_id, vector, xml_blocks, label, log_nr, log_name="log"):
        test = self.functional_data[int(log_nr)][log_name].find({"_id": ObjectId(mongo_id)})
        print(list(test))
        self.functional_data[int(log_nr)][log_name].update_one({"_id": ObjectId(mongo_id)},
                {"$set": {"experiment_id": experiment_id, "vector": vector, "xml_blocks": xml_blocks, "label": label}})

    def update_functional_log_entry_label(self, mongo_id, label, log_nr, log_name="log"):
        test = self.functional_data[int(log_nr)][log_name].find({"_id": ObjectId(mongo_id)})
        print(list(test))
        self.functional_data[int(log_nr)][log_name].update_one({"_id": ObjectId(mongo_id)},
                                                               {"$set": {"label": label}})

    def get_functional_log_data(self, log_nr, log_name="log"):
        return self.functional_data[int(log_nr)][log_name].find({})

    def get_functional_log_data_blocks_label_and_id(self, log_nr, log_name="log"):
        return self.functional_data[int(log_nr)][log_name].find({}, {"xml_blocks": 1, "_id": 1, "label": 1})

    def get_fid_vectors(self, log_nr, log_name="log"):
        return self.functional_data[int(log_nr)][log_name].find({}, {"vector": 1, "_id": 0})

    def get_f_programs(self, log_nr, log_name="log"):
        return self.functional_data[int(log_nr)][log_name].find({}, {"xml_blocks": 1, "_id": 0})

    def get_f_labels(self, log_nr, log_name="log"):
        return self.functional_data[int(log_nr)][log_name].find({}, {"label": 1, "_id": 0}) #pathlabel for new method

    def get_f_steplabels(self, log_nr, log_name="log"):
        return self.functional_data[int(log_nr)][log_name].find({}, {"steplabel": 1, "_id": 0})

    def get_create_log(self):
        return self.create_log

    def get_fix_log(self):
        return self.fix_log

    def add_to_interactive_data_log(self, collectionName, experiment_id, vector, xml_blocks, label, steplabel, pathlabel):
        col = self.functional_data[FunctionalDataset.INTERACTIVE_CLUSTERING][collectionName]
        col.insert_one({"experiment_id": experiment_id, "vector": vector, "xml_blocks": xml_blocks, "label": label, "steplabel": steplabel, "pathlabel": pathlabel})

    def get_interactive_clustering_collection_names(self):
        return self.functional_data[FunctionalDataset.INTERACTIVE_CLUSTERING].list_collection_names()


    def get_create_entry_count(self):
        nr = self.create_log.count({})
        return nr

    def get_create_entries(self):
        return list(self.create_log.find({"event.name": "changedWorkspace"}, {"event.data": 1, "_id": 0}))


    def insertIntoRecordedDataLog(self, data):
        """Insert an log element into the log collection."""
        print("saving data")
        coll = self.recorded_data_log_log
        coll.insert(data)



