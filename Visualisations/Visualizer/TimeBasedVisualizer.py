from .BaseVisualizer import BaseVisualizer
from ..DatabaseConnection.DataProxy import DataProxy
import statistics as stat
from sklearn.cluster import AffinityPropagation as Aprop
from matplotlib import pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from statsmodels.stats.weightstats import ztest
from statistics import mean
from statistics import variance

from ..Utils.DcMotorCountExtractor import DcMotorCountExtractor
from ..Utils.DelayCountExtractor import DelayCountExtractor
from ..Utils.DwenguinoLcdCountExtractor import DwenguinoLcdCountExtractor
from ..Utils.IfStatementCountExtractor import IfStatementCountExtractor
from ..Utils.LoopStatementCountExtractor import LoopStatementCountExtractor
from ..Utils.MetaDataExtractor import MetaDataExtractor
from ..Utils.SonarCountExtractor import SonarCountExtractor


class TimeBasedVisualizer(BaseVisualizer):
    def __init__(self):
        self.dataProxy = DataProxy()
        self.dataProxy.setDataSource('BlocklyLogDebug', 'log')
        self.fontsize = "40"
        #self.dataProxy.setDataSource('blocklyLogDebugNew', 'log')
        self.sessionDates = [
            ['2018-03-06', '2018-03-19', '2018-04-16', '2018-04-23'],
            ['2018-03-13', '2018-03-27', '2018-04-17', '2018-04-24'],
            ['2018-03-15', '2018-03-22', '2018-03-29', '2018-04-19', '2018-04-26']
        ]
        self.sessionDatesDebug = [
            ['2018-07-05', '2018-20-05', '2018-04-06'],
            ['2018-08-05', '2018-22-05', '2018-29-05', '2018-05-06'],
            ['2018-17-05', '2018-24-05', '2018-31-05', '2018-07-06']
        ]
        self.sessionNames = ["session1", "session2", "session3"]
        self.classGroupDates = [
            ['2018-03-06', '2018-03-13', '2018-03-15'],
            ['2018-03-19', '2018-03-22'],
            ['2018-03-27', '2018-03-29'],
            ['2018-04-16', '2018-04-17', '2018-04-19'],
            ['2018-04-23', '2018-04-24', '2018-04-26']
        ]
        self.classGroupNames = ["Group1", "Group2", "Group3", "Group4", "Group5"]

        self.colorMapSessions = {
            "session1": "tab:blue",
            "session2": "tab:green",
            "session3": "tab:orange",
            "other": "tab:olive",
            'highlight': 'tab:red'
        }

        self.colorMapDates = {
            "Group1": "tab:blue",
            "Group2": "tab:green",
            "Group3": "tab:orange",
            "Group4": "tab:brown",
            "Group5": "tab:purple",
            "other": "tab:olive",
            "highlight": "tab:red"
        }

        self.colorMapHighlight = {
            "Group1": "tab:blue",
            "Group2": "tab:blue",
            "Group3": "tab:blue",
            "Group4": "tab:blue",
            "Group5": "tab:blue",
            "other": "tab:blue",
            "highlight": "tab:red"
        }

    def visualize(self):
        #self.plotGroupedMeanVariance(self.sessionDates, self.sessionNames, self.colorMapSessions)
        #self.plotGroupedMeanVariance(self.classGroupDates, self.classGroupNames, self.colorMapDates)
        # Only color session 1
        '''self.plotGroupedMeanVariance([self.sessionDates[0]], [self.sessionNames[0]],
                                     {"session1": "tab:blue", "other": "tab:red"})
        self.plotGroupedMeanVariance([self.sessionDates[1]], [self.sessionNames[1]],
                                     {"session2": "tab:blue", "other": "tab:red"})
        self.plotGroupedMeanVariance([self.sessionDates[2]], [self.sessionNames[2]],
                                     {"session3": "tab:blue", "other": "tab:red"})'''

        #fig, ax = plt.subplots(1, 1)
        #self.plotGroupedMeanVariance(self.sessionDatesDebug, self.sessionNames, self.colorMapSessions, fig, ax)
        '''for i in range(3):
            for j in range(3):
                highlightGroup = {
                    'days': self.classGroupDates[2],
                    'computerIds': [str(i*3+j+1)]
                }
                self.plotGroupedMeanVariance(self.sessionDates, self.sessionNames, self.colorMapSessions, fig, ax[i, j], highlightGroup=highlightGroup)'''
        #plt.show()

        dataSources = ["BlocklyLogCreate", "BlocklyLogDebug"]
        dataNames = ["Create", "Debug"]
        resultSet = []
        fig = plt.figure()
        ax = fig.add_subplot(111)

        for index, source in enumerate(dataSources):
            self.dataProxy.setDataSource(source, 'log')
            codeEditsPerSession = self.dataProxy.getCodeTreesPerSession()
            timeDeltas = self.convertSessionsToTimeDeltas(codeEditsPerSession)
            timeSpentPerSession = list(map(lambda deltas: int(sum(deltas)/1000), timeDeltas))
            resultSet.append(timeSpentPerSession)
            ax.hist(timeSpentPerSession, range(min(timeSpentPerSession), max(timeSpentPerSession), 120), density=True, alpha=0.5,
                    label=dataNames[index])
            # ax.scatter(changeVsRuns[:, 0], changeVsRuns[:, 1])

        tstat, pvalue = ztest(resultSet[0], resultSet[1])
        print(tstat)
        print(pvalue)
        ax.set_title("Distribution of sessions with specific active programming time \n(t = " + str(round(tstat, 4)) + " p = " + str(round(pvalue, 4)) + ")", fontsize="32")
        ax.set_xlabel('Time spent in ms (buckets of 2 minutes)', fontsize=self.fontsize)
        ax.set_ylabel('Number of sessions', fontsize=self.fontsize)
        plt.legend(loc='upper right', fontsize=self.fontsize)
        plt.show()

        print("mean create:" + str(mean(resultSet[0])) + " variance create: " + str(variance(resultSet[0])))
        print("mean debug:" + str(mean(resultSet[1])) + " variance debug: " + str(variance(resultSet[1])))





    def plotGroupedMeanVariance(self, dates, names, colorMap, fig, ax, highlightGroup=None):
        codeEditsPerSession = self.dataProxy.getCodeTreesPerSession()
        namesPerSession = []
        for session in codeEditsPerSession:
            sessionName = "other"
            for index, sessionDateList in enumerate(dates):
                # if a specific set should be highlighted select them
                if highlightGroup and session["_id"]["timestamp"] in highlightGroup['days'] and session["_id"]["computerId"] in highlightGroup['computerIds']:
                    sessionName = "highlight"
                elif session["_id"]["timestamp"] in sessionDateList:
                    sessionName = names[index]
            namesPerSession.append(sessionName)

        timeDeltasPerSession = self.convertSessionsToTimeDeltas(codeEditsPerSession)
        timeDeltasMeanStd = map(lambda deltaList: [stat.mean(deltaList), stat.variance(deltaList)],
                                timeDeltasPerSession)
        timeDeltasMeanStd = list(timeDeltasMeanStd)
        timeDeltasMeanStd = np.array(list(timeDeltasMeanStd))

        # First scatter the data

        #fig, ax = plt.subplots()
        colorsPerSession = [colorMap[sn] for sn in namesPerSession]
        ax.scatter(timeDeltasMeanStd[:, 0], timeDeltasMeanStd[:, 1], c=colorsPerSession, label=namesPerSession)
        # Create a legend
        custom_lines = []
        custom_names = []
        for attr, value in colorMap.items():
            custom_names.append(attr)
            custom_lines.append(Line2D([0], [0], color=value, lw=4))
        ax.legend(custom_lines, custom_names)
        ax.set(xlabel="mean time between interactions in ms", ylabel="variance of time between interactions")
        if highlightGroup:
            ax.title.set_text("Computer" + highlightGroup['computerIds'][0])




    def convertSessionsToTimeDeltas(self, codeEditsPerSession):
        timeDeltasPerSession = []
        for session in codeEditsPerSession:
            timeDeltas = []
            time = session['code'][0]['epoch']
            # Skip the first element
            iterWSChanges = iter(session['code'])
            next(iterWSChanges)
            # Calculate deltas for this session
            for workspaceChange in iterWSChanges:
                currentTime = workspaceChange['epoch']
                delta = currentTime - time
                # if the interval is larger than two minutes ignore since not actively programming
                if delta < 120000:
                    timeDeltas.append(delta)
                time = currentTime
            timeDeltasPerSession.append(timeDeltas)
        return timeDeltasPerSession