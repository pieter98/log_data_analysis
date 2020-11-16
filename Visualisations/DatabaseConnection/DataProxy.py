from .DatabaseConnection import DatabaseConnection
from bson.son import SON

class DataProxy:
    def __init__(self):
        self.databaseConnection = DatabaseConnection()

    def setDataSource(self, database, collection):
        self.databaseConnection.setDataSource(database, collection)

    def getAllWorkspaceEdits(self):
        query = {'event.name': "changedWorkspace"}
        return self.databaseConnection.queryCurrentCollection(query)

    def getNumberOfCodeEdits(self):
        return self.databaseConnection.queryCurrentCollection({'event.name': "changedWorkspace"}).count()

    def getNumberOfRuns(self):
        return self.databaseConnection.queryCurrentCollection({"$or": [{"event.name": {"$eq": "simStart"}}, {"event.name": {"$eq": "runClicked"}}]}).count()

    def getCodeTreesPerSession(self):
        # Query the create dataset
        # Extract changedWorkspace events and group them per day
        # Exclude the ones on the 20-03-2018 since this day two workshops were held at the same time so they are not seperable.
        '''filter = [
            {"$match": {"event.name": "changedWorkspace", "event.computerId": {"$ne": "-1"}}},
            {"$sort": {"timestamp": 1}},
            {"$project": {"timestamp": {"$toDate": "$timestamp"}, "computerId": "$event.computerId", "fields": "$$ROOT" }},
            {"$project": {"timestamp": {"$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}}, "computerId": "$computerId", "fields": "$fields"}},
            {"$group": {"_id": {"computerId": "$computerId", "timestamp": "$timestamp"}, "count": {"$sum": 1}, "code": {"$push": {"xml": "$fields.event.data", "epoch": "$fields.event.timestamp"}}}},
            {"$match": {"_id.timestamp": {"$ne": '2018-03-20'}}},
            {"$sort": {"_id.timestamp": 1, "_id.computerId": 1}}
            ]'''
        resultSet = []
        batchSize = 50
        for index in range(0, len(self.databaseConnection.getCurrentSessionIds()), batchSize):
            filter = [
                {"$match": {"event.name": "changedWorkspace", "sessionId": {"$in": self.databaseConnection.getCurrentSessionIds()[index:(index+batchSize)]}}},
                {"$sort": {"timestamp": 1}},
                {"$project": {"timestamp": {"$toDate": "$timestamp"}, "sessionId": "$sessionId",
                              "codeData": "$event.data", "epoch": "$event.timestamp"}},
                {"$project": {"timestamp": {"$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}},
                              "sessionId": "$sessionId", "codeData": "$codeData", "epoch": "$epoch"}},
                {"$group": {"_id": {"sessionId": "$sessionId", "timestamp": "$timestamp"}, "count": {"$sum": 1},
                            "code": {"$push": {"xml": "$codeData", "epoch": "$epoch"}}}},
                {"$match": {"_id.timestamp": {"$ne": '2018-03-20'}, "count": {"$gt": 100}}},
                {"$sort": {"_id.timestamp": 1, "_id.sessionId": 1}}
            ]
            #numberOfResults = self.databaseConnection.countQueryResults(filter)
            #print(numberOfResults)

            queryResults = self.databaseConnection.aggregateOnCurrentCollection(filter)
            resultSet = resultSet + list(queryResults)

        return resultSet

    def getEventsPerSession(self):
        # Extract all event types and group them per session
        # Exclude the ones on the 20-03-2018 since this day two workshops were held at the same time so they are not seperable.
        '''filter = [
            {"$match": {"event.computerId": {"$ne": "-1"}, "$and": [{"event.name": {"$ne": "simStop"}}, {"event.name": {"$ne": "blocklyUI"}}]}},
            {"$sort": {"timestamp": 1}},
            {"$project": {"timestamp": {"$toDate": "$timestamp"}, "computerId": "$event.computerId",
                          "fields": "$$ROOT"}},
            {"$project": {"timestamp": {"$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}},
                          "computerId": "$computerId", "fields": "$fields"}},
            {"$group": {"_id": {"computerId": "$computerId", "timestamp": "$timestamp"}, "count": {"$sum": 1},
                        "events": {"$push": {"name": "$fields.event.name", "epoch": "$fields.event.timestamp"}}}},
            {"$match": {"_id.timestamp": {"$ne": '2018-03-20'}}},
            {"$sort": {"_id.timestamp": 1, "_id.computerId": 1}}
        ]'''
        filter = [
            {"$match": {"$and": [{"event.name": {"$ne": "simStop"}}, {"event.name": {"$ne": "blocklyUI"}}]}},
            {"$sort": {"timestamp": 1}},
            {"$project": {"timestamp": {"$toDate": "$timestamp"}, "sessionId": "$sessionId",
                          "fields": "$$ROOT"}},
            {"$project": {"timestamp": {"$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}},
                          "sessionId": "$sessionId", "fields": "$fields"}},
            {"$group": {"_id": {"sessionId": "$sessionId", "timestamp": "$timestamp"}, "count": {"$sum": 1},
                        "events": {"$push": {"name": "$fields.event.name", "epoch": "$fields.event.timestamp"}}}},
            {"$match": {"_id.timestamp": {"$ne": '2018-03-20'}}},
            {"$sort": {"_id.timestamp": 1, "_id.sessionId": 1}}
        ]
        queryResults = self.databaseConnection.aggregateOnCurrentCollection(filter)
        return list(queryResults)

    def getRunEvents(self):
        filter = [
            {"$match": {"$or": [{"event.name": "runClicked"}, {"event.name": "simStart"}]}},
            {"$sort": {"timestamp": 1}},
            {"$project": {"timestamp": {"$toDate": "$timestamp"}, "sessionId": "$sessionId",
                          "codeData": "$event.data", "epoch": "$event.timestamp"}},
            {"$project": {"timestamp": {"$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}},
                          "sessionId": "$sessionId", "codeData": "$codeData", "epoch": "$epoch"}},
            {"$group": {"_id": {"sessionId": "$sessionId", "timestamp": "$timestamp"}, "count": {"$sum": 1},
                        "epoch": {"$push": "$epoch"}}},
            {"$match": {"_id.timestamp": {"$ne": '2018-03-20'}}},
            {"$sort": {"_id.timestamp": 1, "_id.sessionId": 1}}
        ]
        # numberOfResults = self.databaseConnection.countQueryResults(filter)
        # print(numberOfResults)

        '''filter = [
            {"$match": {"event.name": "runClicked", "event.computerId": {"$ne": "-1"}}},
            {"$sort": {"timestamp": 1}},
            {"$project": {"timestamp": {"$toDate": "$timestamp"}, "computerId": "$event.computerId",
                          "fields": "$$ROOT"}},
            {"$project": {"timestamp": {"$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}},
                          "computerId": "$computerId", "fields": "$fields"}},
            {"$group": {"_id": {"computerId": "$computerId", "timestamp": "$timestamp"}, "count": {"$sum": 1},
                        "epoch": {"$push": "$fields.event.timestamp"}}},
            {"$match": {"_id.timestamp": {"$ne": '2018-03-20'}}},
            {"$sort": {"_id.timestamp": 1, "_id.computerId": 1}}
        ]'''
        queryResults = self.databaseConnection.aggregateOnCurrentCollection(filter)
        return list(queryResults)