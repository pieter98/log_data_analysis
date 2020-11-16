from .BaseVisualizer import BaseVisualizer
from ..DatabaseConnection.DataProxy import DataProxy
from matplotlib import pyplot as plt
from statsmodels.stats.weightstats import ztest
import numpy as np
import math
from matplotlib.lines import Line2D
from statistics import mean

from ..Utils.ClearLcdCountExtractor import ClearLcdCountExtractor
from ..Utils.DcMotorCountExtractor import DcMotorCountExtractor
from ..Utils.DelayCountExtractor import DelayCountExtractor
from ..Utils.DwenguinoLcdCountExtractor import DwenguinoLcdCountExtractor
from ..Utils.IfStatementCountExtractor import IfStatementCountExtractor
from ..Utils.LedsOnOffCountExtractor import LedsOnOffCountExtractor
from ..Utils.LedsRegCountExtractor import LedsRegCountExtractor
from ..Utils.LoopStatementCountExtractor import LoopStatementCountExtractor
from ..Utils.MetaDataExtractor import MetaDataExtractor
from ..Utils.NoToneOnPinCountExtractor import NoToneOnPinCountExtractor
from ..Utils.ServoCountExtractor import ServoCountExtractor
from ..Utils.SonarCountExtractor import SonarCountExtractor
from ..Utils.ToneOnPinCountExtractor import ToneOnPinCountExtractor
from ..Utils.WhileUnitlCountExtractor import WhileUntilCountExtractor


class ColorPlotVisualizer(BaseVisualizer):
    def __init__(self):
        self.dataProxy = DataProxy()
        self.dataProxy.setDataSource('BlocklyLogCreate', 'log')
        self.fontsize = "40"
        self.extractors = [DcMotorCountExtractor(),
                      IfStatementCountExtractor(),
                      LoopStatementCountExtractor(),
                      DwenguinoLcdCountExtractor(),
                      DelayCountExtractor(),
                      SonarCountExtractor(),
                      ClearLcdCountExtractor(),
                      ServoCountExtractor(),
                      ToneOnPinCountExtractor(),
                      NoToneOnPinCountExtractor(),
                      LedsOnOffCountExtractor(),
                      LedsRegCountExtractor(),
                      WhileUntilCountExtractor()]

        self.sessionDates = [
            ['2018-03-06', '2018-03-19', '2018-04-16', '2018-04-23'],
            ['2018-03-13', '2018-03-27', '2018-04-17', '2018-04-24'],
            ['2018-03-15', '2018-03-22', '2018-03-29', '2018-04-19', '2018-04-26']
        ]
        self.sessionDatesDebug = [
            ['2018-05-07', '2018-05-20', '2018-06-04'],
            ['2018-05-08', '2018-05-22', '2018-05-29', '2018-06-05'],
            ['2018-05-17', '2018-05-24', '2018-05-31', '2018-06-07']]

        self.allSessionDates = [
            self.sessionDates,
            self.sessionDatesDebug
        ]

        self.distractedSets = [
            [0,
             1,
             5,
             7,
             12],
            [1,
             2,
             3,
             4,
             5,
             6,
             7,
             8,
             9,
             10,
             11,
             12],
            [2,
             3,
             6,
             7,
             8,
             9,
             10,
             11,
             12]
        ]

        self.undistractedSets = [
            [3,
             4,
             6,
             8,
             9,
             10,
             11,
             2],
            [0,
             4],
            [0,
             1,
             4,
             5,
             ]
        ]

        self.distractorSets = [
            self.distractedSets,
            self.undistractedSets
        ]

    def visualizeTinkeringRatio(self):
        dataSources = ["BlocklyLogCreate", "BlocklyLogDebug"]
        resultSet = []
        for source in dataSources:
            self.dataProxy.setDataSource(source, 'log')
            codeEditsPerSession = self.dataProxy.getCodeTreesPerSession()
            runsPerSession = self.dataProxy.getRunEvents()
            filteredCodeEditsPerSession = []
            filteredRunsPerSession = []
            for session in codeEditsPerSession:
                sessionId = session["_id"]["sessionId"]
                correspondingRunsPerSession = None
                for runsInSession in runsPerSession:
                    runSessionId = runsInSession["_id"]["sessionId"]
                    if sessionId == runSessionId:
                        correspondingRunsPerSession = runsInSession
                if correspondingRunsPerSession:
                    filteredCodeEditsPerSession.append(session)
                    filteredRunsPerSession.append(correspondingRunsPerSession)

            codeEditsPerSession = list(map(lambda x: x['count'], filteredCodeEditsPerSession))
            runsPerSession = list(map(lambda x: x['count'], filteredRunsPerSession))
            codeEditsPerSession = np.array(codeEditsPerSession)
            runsPerSession = np.array(runsPerSession)
            tinkeringRatio = runsPerSession/codeEditsPerSession * 100
            resultSet.append(tinkeringRatio.tolist())

        print(mean(resultSet[0]))
        print(mean(resultSet[1]))
        fig = plt.figure()
        ax = fig.add_subplot(111)
        tstat, pvalue = ztest(resultSet[0], resultSet[1])
        ax.set_title(
            "Distribution of tinkering ratio " + " (tstat: " + str(round(tstat, 4)) + " p: " + str(round(pvalue * 10**15, 4)) + "e-15)",
            fontsize=self.fontsize)
        ax.hist(resultSet[0], range(0, int(max(resultSet[0])), 1), density=True,
                alpha=0.5, label="Create")
        ax.hist(resultSet[1], range(0, int(max(resultSet[1])), 1), density=True,
                alpha=0.5, label="Debug")
        ax.set_xlabel('Amount of tinkering (%)', fontsize=self.fontsize)
        ax.set_ylabel('Percentage of sessions', fontsize=self.fontsize)
        plt.legend(loc='upper right', fontsize=self.fontsize)
        plt.show()


    def visualizeBlocksChanged(self):
        print(plt.style.available)
        plt.style.use(['seaborn-poster'])
        dataSources = ["BlocklyLogCreate", "BlocklyLogDebug"]
        resultsets = []
        for source in range(2):
            self.dataProxy.setDataSource(dataSources[source], 'log')
            print(self.dataProxy.getNumberOfRuns())
            numberOfCodeEdits = self.dataProxy.getNumberOfCodeEdits()
            print(numberOfCodeEdits)
            print("tadaa")
            codeEditsPerSession = self.dataProxy.getCodeTreesPerSession()

            extractorNames = ["DC-motor", "if condition", "for loop", "DwenguinoLCD", "delay", "sonar", "Clear-lcd",
                              "Servo", "ToneOnPin", "NoToneOnPin", "Led-on-off", "LEDS", "whileuntil"]

            metadata = self.generateMetaDataForAllSessions(codeEditsPerSession, self.extractors)

            metadataNames = ["added", "removed", "added multiple times", "removed multiple times", "value edits"]
            globalSessionData = []
            for sessionData in metadata:
                newSessionData = []
                for sessionChangeDataSeries in sessionData[1:-1]:
                    singleBlocksAdded = 0
                    singleBlocksRemoved = 0
                    multiBlocksAdded = 0
                    multiBlocksRemoved = 0
                    valueEdits = 0
                    for index, value in enumerate(sessionChangeDataSeries[1:-1]):
                        if value - sessionChangeDataSeries[index - 1] == 1:
                            singleBlocksAdded += 1
                        elif value - sessionChangeDataSeries[index - 1] == -1:
                            singleBlocksRemoved += 1
                        elif value - sessionChangeDataSeries[index - 1] > 1:
                            multiBlocksAdded += value - sessionChangeDataSeries[index - 1]
                        elif value - sessionChangeDataSeries[index - 1] < -1:
                            multiBlocksRemoved += -1 * (value - sessionChangeDataSeries[index - 1])
                        else:
                            valueEdits += 1
                    newSessionData.append(
                        valueEdits)
                globalSessionData.append(sum(newSessionData))
            print(globalSessionData)

            globalSessionData = np.array(globalSessionData)
            resultsets.append(globalSessionData)

        datanames = ["Create", "Debug"]
        print(mean(resultsets[0]))
        print(mean(resultsets[1]))
        fig = plt.figure()
        ax = fig.add_subplot(111)
        tstat, pvalue = ztest(resultsets[0], resultsets[1])
        ax.set_title(
            "Value edit distribution " + " (tstat: " + str(round(tstat, 4)) + " p: " + str(round(pvalue, 4)) + ")", fontsize=self.fontsize)
        ax.hist(resultsets[0], range(0, max(resultsets[0]), 100), density=True,
                alpha=0.5, label="Create")
        ax.hist(resultsets[1], range(0, max(resultsets[1]), 100), density=True,
                alpha=0.5, label="Debug")
        # ax.scatter(changeVsRuns[:, 0], changeVsRuns[:, 1])
        ax.set_xlabel('Number of value edits', fontsize=self.fontsize)
        ax.set_ylabel('Percentage of sessions', fontsize=self.fontsize)
        plt.legend(loc='upper right', fontsize=self.fontsize)
        plt.show()


    def visualizeBlocksAddedRemovedChanged(self):
        dataSources = ["BlocklyLogCreate", "BlocklyLogDebug"]
        resultsets = []
        for source in range(2):
            self.dataProxy.setDataSource(dataSources[source], 'log')
            print(self.dataProxy.getNumberOfRuns())
            numberOfCodeEdits = self.dataProxy.getNumberOfCodeEdits()
            print(numberOfCodeEdits)
            print("tadaa")
            codeEditsPerSession = self.dataProxy.getCodeTreesPerSession()

            extractorNames = ["DC-motor", "if condition", "for loop", "DwenguinoLCD", "delay", "sonar", "Clear-lcd",
                              "Servo", "ToneOnPin", "NoToneOnPin", "Led-on-off", "LEDS", "whileuntil"]

            metadata = self.generateMetaDataForAllSessions(codeEditsPerSession, self.extractors)

            metadataNames = ["added", "removed", "added multiple times", "removed multiple times", "value edits"]
            globalSessionData = []
            for sessionData in metadata:
                newSessionData = []
                for sessionChangeDataSeries in sessionData[1:-1]:
                    singleBlocksAdded = 0
                    singleBlocksRemoved = 0
                    multiBlocksAdded = 0
                    multiBlocksRemoved = 0
                    valueEdits = 0
                    for index, value in enumerate(sessionChangeDataSeries[1:-1]):
                        if value - sessionChangeDataSeries[index - 1] == 1:
                            singleBlocksAdded += 1
                        elif value - sessionChangeDataSeries[index - 1] == -1:
                            singleBlocksRemoved += 1
                        elif value - sessionChangeDataSeries[index - 1] > 1:
                            multiBlocksAdded += value - sessionChangeDataSeries[index - 1]
                        elif value - sessionChangeDataSeries[index - 1] < -1:
                            multiBlocksRemoved += -1 * (value - sessionChangeDataSeries[index - 1])
                        else:
                            valueEdits += 1
                    newSessionData.append(
                        [singleBlocksAdded, singleBlocksRemoved, multiBlocksAdded, multiBlocksRemoved, valueEdits])
                globalSessionData.append(newSessionData)
            print(globalSessionData)

            globalSessionData = np.array(globalSessionData)
            resultsets.append(globalSessionData)

        for j in range(len(resultsets[0][0][0])):
            for i in range(len(resultsets[0][0])):
                fig = plt.figure()
                ax = fig.add_subplot(111)
                tstat, pvalue = ztest(resultsets[0][:, i, j], resultsets[1][:, i, j])
                ax.set_title(
                    extractorNames[i] + " " + metadataNames[j] + " tstat: " + str(tstat) + " p: " + str(pvalue))
                for k in range(len(resultsets)):
                    step = 5  # math.ceil(max(resultsets[k][:, i, j])/10)
                    maxValue = max(resultsets[k][:, i, j])
                    if maxValue > 0:
                        ax.hist(resultsets[k][:, i, j], range(0, maxValue, step if step > 0 else 1), density=True,
                                alpha=0.5, label=dataSources[k])
                        # ax.scatter(changeVsRuns[:, 0], changeVsRuns[:, 1])
                        ax.set_xlabel('Number of times the block ' + extractorNames[i] + "was " + metadataNames[j])
                        ax.set_ylabel('Percentage of sessions')
                        plt.legend(loc='upper right')
                        plt.savefig(
                            "/home/tneutens/Documents/UGent/Onderzoek/SIGCSE2021/distribution_plots/test/distribution_" +
                            extractorNames[i] + "_" + metadataNames[j])

    def visualizeDistractionRatio(self):
        dataSources = ["BlocklyLogCreate", "BlocklyLogDebug"]
        resultsets = []
        for source in range(2):
            self.dataProxy.setDataSource(dataSources[source], 'log')
            print(self.dataProxy.getNumberOfRuns())
            numberOfCodeEdits = self.dataProxy.getNumberOfCodeEdits()
            print(numberOfCodeEdits)
            print("tadaa")
            codeEditsPerSession = self.dataProxy.getCodeTreesPerSession()

            extractorNames = ["DC-motor", "if condition", "for loop", "DwenguinoLCD", "delay", "sonar", "Clear-lcd",
                              "Servo", "ToneOnPin", "NoToneOnPin", "Led-on-off", "LEDS", "whileuntil"]

            metadata = self.generateMetaDataForAllSessions(codeEditsPerSession, self.extractors)

            metadataNames = ["added", "removed", "added multiple times", "removed multiple times", "value edits"]
            globalSessionData = []
            for idx, sessionData in enumerate(metadata):
                newSessionData = []
                for sessionChangeDataSeries in sessionData[1:]:
                    singleBlocksAdded = 0
                    for index, value in enumerate(sessionChangeDataSeries[1:-1]):
                        if value - sessionChangeDataSeries[index - 1] == 1:
                            singleBlocksAdded += 1
                    newSessionData.append(
                        singleBlocksAdded)
                globalSessionData.append({'timestamp': codeEditsPerSession[idx]['_id']['timestamp'], 'data': newSessionData})
            print(globalSessionData)
            globalSessionData = np.array(globalSessionData)
            resultsets.append(globalSessionData)

        distractionResultSets = []
        for idx, resultset in enumerate(resultsets):
            sessionDistractionScores = []
            for index, session in enumerate(resultset):
                time = session['timestamp']
                data = session['data']
                distractionScore = 0

                undistractedScore = 0
                for sessionTypeNumber in range(len(self.allSessionDates[idx])):
                    if time in self.allSessionDates[idx][sessionTypeNumber]:
                        for index in self.distractedSets[sessionTypeNumber]:
                            distractionScore += data[index]
                        for index in self.undistractedSets[sessionTypeNumber]:
                            undistractedScore += data[index]
                ratioScore = distractionScore/(distractionScore+undistractedScore) if distractionScore+undistractedScore > 0 else 0
                sessionDistractionScores.append([distractionScore, undistractedScore, ratioScore])
            distractionResultSets.append(sessionDistractionScores)

        print(distractionResultSets)

        filteredDistractionResults = []
        for i in range(2):
            sessionDistractionScores = []
            totalblocksadded = 0
            for j in range(len(distractionResultSets[i])):
                if True or (distractionResultSets[i][j][0] + distractionResultSets[i][j][1] != 0 and distractionResultSets[i][j][0] + distractionResultSets[i][j][1] > 0):
                    sessionDistractionScores.append(int(distractionResultSets[i][j][2] * 100))
                    totalblocksadded += distractionResultSets[i][j][0] + distractionResultSets[i][j][1]
            filteredDistractionResults.append(sessionDistractionScores)
            print(totalblocksadded)

        print("mean create: " + str(mean(filteredDistractionResults[0])))
        print("mean debug: " + str(mean(filteredDistractionResults[1])))

        fig = plt.figure()
        ax = fig.add_subplot(111)
        tstat, pvalue = ztest(filteredDistractionResults[0], filteredDistractionResults[1])
        tstat = round(tstat, 4)
        pvalue = round(pvalue, 4)
        ax.set_title(
            "Distribution of distraction score " + " (tstat: " + str(round(tstat, 4)) + " p: " + str(round(pvalue, 2)) + ")", fontsize=self.fontsize)
        ax.hist(filteredDistractionResults[0], range(0, int(max(filteredDistractionResults[0])), 1), density=True,
                alpha=0.5, label="Create")
        ax.hist(filteredDistractionResults[1],
                range(0, int(max(filteredDistractionResults[1])), 1),
                density=True,
                alpha=0.5, label="Debug")
        ax.set_xlabel('Distraction score', fontsize=self.fontsize)
        ax.set_ylabel('Percentage of sessions', fontsize=self.fontsize)
        plt.legend(loc='upper right', fontsize=self.fontsize)
        plt.show()


    def visualizeDistractionRatioInTime(self):
        dataSources = ["BlocklyLogCreate", "BlocklyLogDebug"]
        resultsets = []
        for source in range(1):
            self.dataProxy.setDataSource(dataSources[source], 'log')
            print(self.dataProxy.getNumberOfRuns())
            numberOfCodeEdits = self.dataProxy.getNumberOfCodeEdits()
            print(numberOfCodeEdits)
            print("tadaa")
            codeEditsPerSession = self.dataProxy.getCodeTreesPerSession()

            extractorNames = ["DC-motor", "if condition", "for loop", "DwenguinoLCD", "delay", "sonar", "Clear-lcd",
                              "Servo", "ToneOnPin", "NoToneOnPin", "Led-on-off", "LEDS", "whileuntil"]

            metadata = self.generateMetaDataForAllSessions(codeEditsPerSession, self.extractors)

            metadataNames = ["added", "removed", "added multiple times", "removed multiple times", "value edits"]
            globalSessionData = []
            for idx, sessionData in enumerate(metadata):
                newSessionData = []
                for blockTypeIndex, sessionChangeDataSeries in enumerate(sessionData[1:]):
                    timeInterVals = []
                    blockIsInCode = False
                    # If the code goes from no instance of a block to an instance or from an instance to no instances, log the timestamp. Like this we can measure how long each block was in the code.
                    for index, value in enumerate(sessionChangeDataSeries):
                        if sessionChangeDataSeries[index] > 0 and not blockIsInCode:
                            timeInterVals.append(sessionData[0][index])
                            blockIsInCode = True
                        if (sessionChangeDataSeries[index] == 0 and blockIsInCode) or (index == len(sessionChangeDataSeries) - 1 and blockIsInCode):
                            timeInterVals.append(sessionData[0][index])
                            blockIsInCode = False
                    timeInterVals = [timeInterVals[x:x+2] for x in range(0, len(timeInterVals), 2)]
                    newSessionData += timeInterVals
                globalSessionData.append({'timestamp': codeEditsPerSession[idx]['_id']['timestamp'], 'data': newSessionData})
            print(globalSessionData)
            globalSessionData = np.array(globalSessionData)
            resultsets.append(globalSessionData)

        distractionResultSets = []
        for idx, resultset in enumerate(resultsets):
            sessionDistractionScores = []
            for index, session in enumerate(resultset):
                time = session['timestamp']
                data = session['data']
                distractedIntervals = []
                undistractedIntervals = []
                for sessionTypeNumber in range(len(self.allSessionDates[idx])):
                    if time in self.allSessionDates[idx][sessionTypeNumber]:
                        for i in self.distractedSets[sessionTypeNumber]:
                            distractedIntervals.append(data[i])
                        for i in self.undistractedSets[sessionTypeNumber]:
                            undistractedIntervals.append(data[i])
                sessionDistractionScores.append([distractedIntervals, undistractedIntervals])
            distractionResultSets.append(sessionDistractionScores)

        print(distractionResultSets)

        filteredDistractionResults = []
        for i in range(2):
            sessionDistractionScores = []
            totalblocksadded = 0
            for j in range(len(distractionResultSets[i])):
                if True or (distractionResultSets[i][j][0] + distractionResultSets[i][j][1] != 0 and distractionResultSets[i][j][0] + distractionResultSets[i][j][1] > 0):
                    sessionDistractionScores.append(int(distractionResultSets[i][j][2] * 100))
                    totalblocksadded += distractionResultSets[i][j][0] + distractionResultSets[i][j][1]
            filteredDistractionResults.append(sessionDistractionScores)
            print(totalblocksadded)

        print("mean create: " + str(mean(filteredDistractionResults[0])))
        print("mean debug: " + str(mean(filteredDistractionResults[1])))

        fig = plt.figure()
        ax = fig.add_subplot(111)
        tstat, pvalue = ztest(filteredDistractionResults[0], filteredDistractionResults[1])
        tstat = round(tstat, 4)
        pvalue = round(pvalue, 4)
        ax.set_title(
            "Distribution of distraction score for both sessions" + " tstat: " + str(tstat) + " p: " + str(pvalue))
        ax.hist(filteredDistractionResults[0], range(0, int(max(filteredDistractionResults[0])), 1), density=True,
                alpha=0.5, label="Create")
        ax.hist(filteredDistractionResults[1],
                range(0, int(max(filteredDistractionResults[1])), 1),
                density=True,
                alpha=0.5, label="Debug")
        ax.set_xlabel('Distraction score')
        ax.set_ylabel('Percentage of sessions')
        plt.legend(loc='upper right')
        plt.show()


    def visualize(self):
        #self.visualizeBlocksAddedRemovedChanged()
        #self.visualizeDistractionRatio()
        #self.visualizeDistractionRatioInTime()
        #self.visualizeBlocksChanged()
        self.visualizeTinkeringRatio()

        '''dataSources = ["BlocklyLogCreate", "BlocklyLogDebug"]
        extractorNames = ["DC-motor", "if condition", "for loop", "DwenguinoLCD", "delay", "sonar", "Clear-lcd",
                          "Servo", "ToneOnPin", "NoToneOnPin", "Led-on-off", "LEDS", "whileuntil"]
        resultsets = []
        for source in range(2):
            self.dataProxy.setDataSource(dataSources[source], 'log')
            print("tadaa")
            codeEditsPerSession = self.dataProxy.getCodeTreesPerSession()
            timestamps = None
            extractorOutputs = []
            for extractor in self.extractors:
                t, outputValues = self.generateMetaDataPerTimestamp(codeEditsPerSession, extractor)
                timestamps = t
                extractorOutputs.append(outputValues)

            self.plotOutputsInTime(timestamps, extractorOutputs, extractorNames)
            #for index, extractor in enumerate(self.extractors):
            #    self.plotOutputsPerSessionInTime(self.generateMetaDataForAllSessions(codeEditsPerSession, [extractor]), [extractorNames[index]])
'''

    def generateMetaDataPerTimestamp(self, codeEditsPerSession, extractor):
        timestamps = []
        outputValues = []
        for i in range(len(codeEditsPerSession)):
            t, o = self.generateMetaDataForSession(codeEditsPerSession[i], extractor)
            timestamps.append(t)
            outputValues.append(o)
        return timestamps, outputValues

    def generateMetaDataForSession(self, codeEditsInSession, extractor):
        timestamps = []
        outputValues = []
        starttime = codeEditsInSession['code'][0]['epoch']
        for i in range(len(codeEditsInSession['code'])):
            timestamps.append(codeEditsInSession['code'][i]['epoch'] - starttime)
            outputValues.append((extractor.extract(codeEditsInSession['code'][i]['xml'])))
        return timestamps, outputValues

    def generateMetaDataForAllSessions(self, codeEditsPerSession, extractorList):
        sessions = []
        for i in range(len(codeEditsPerSession)):
            session = []
            t = None
            o = None
            for extractor in extractorList:
                t, o = self.generateMetaDataForSession(codeEditsPerSession[i], extractor)
                session.append(o)
            session.insert(0, t)
            sessions.append(session)
        return sessions


    def plotOutputsPerSessionInTime(self, sessionInfo, outputNames):
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1, projection='3d')
        colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple', 'tab:brown', 'tab:pink', 'tab:gray',
                  'tab:olive', 'tab:cyan']
        index = 0
        for session in sessionInfo:
            for i in range(1, len(session)):
                sessionArray = [index for i in range(len(session[0]))]
                ax.plot(session[0], sessionArray, session[i], color=colors[i])
                index += 1
        ax.set_title("Number of code blocks in time per session")

        # Create legend
        custom_lines = []
        for i in range(len(sessionInfo[0]) - 1):
            custom_lines.append(Line2D([0], [0], color=colors[i], lw=4))
        ax.legend(custom_lines, outputNames)
        plt.show()

    def plotOutputsInTime(self, timestamps, outputValuesList, outputNames):
        if len(outputValuesList) > 9:
            raise Exception("Can only visualize 10 output types right now. Only 10 colors defined!")

        # Custom lines for custom legend
        custom_lines = []
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple', 'tab:brown', 'tab:pink', 'tab:gray', 'tab:olive', 'tab:cyan', 'blue', 'red', 'black']
        for timeseries in range(len(outputValuesList)):
            custom_lines.append(Line2D([0], [0], color=colors[timeseries], lw=4))
            for i in range(len(timestamps)):
                ax.plot(timestamps[i], outputValuesList[timeseries][i], color=colors[timeseries])

        ax.set_title("Number of blocks used in time for each session")
        ax.legend(custom_lines, outputNames)
        plt.show()