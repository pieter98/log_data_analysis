from .BaseVisualizer import BaseVisualizer
from .TimeBasedVisualizer import TimeBasedVisualizer
from ..DatabaseConnection.DataProxy import DataProxy
import statistics as stat
from sklearn.cluster import AffinityPropagation as Aprop
from matplotlib import pyplot as plt
import numpy as np
import math
from matplotlib.lines import Line2D
from sklearn import metrics
from sklearn.cluster import KMeans
from sklearn.datasets import load_digits
from sklearn.decomposition import PCA
from sklearn.preprocessing import scale

from sklearn.manifold import TSNE as t_sne

from ..Utils.DcMotorCountExtractor import DcMotorCountExtractor
from ..Utils.DelayCountExtractor import DelayCountExtractor
from ..Utils.DwenguinoLcdCountExtractor import DwenguinoLcdCountExtractor
from ..Utils.IfStatementCountExtractor import IfStatementCountExtractor
from ..Utils.LoopStatementCountExtractor import LoopStatementCountExtractor
from ..Utils.MetaDataExtractor import MetaDataExtractor
from ..Utils.SonarCountExtractor import SonarCountExtractor


class TimeBasedClusteringVisualizer(TimeBasedVisualizer):
    def __init__(self):
        TimeBasedVisualizer.__init__(self)
        self.colorMapSessions2 = {
            "session1": "tab:brown",
            "session2": "tab:pink",
            "session3": "tab:cyan",
            "other": "tab:olive",
            'highlight': 'tab:red'
        }




    def visualize(self):
        self.clusterBasedOnTime()
        #self.gaussianClustering(500)


    def gaussianClustering(self, sigma):
        codeEditsPerSession = self.dataProxy.getCodeTreesPerSession()
        runsPerSession = self.dataProxy.getRunEvents()

        codeEditTimestamps = []
        for session in codeEditsPerSession:
            redefSession = {}
            redefSession["day"] = session['_id']['timestamp']
            timestamps = [logEvent['epoch'] for logEvent in session['code']]
            redefSession["timestamps"] = timestamps
            codeEditTimestamps.append(redefSession)

        runTimestamps = []
        for session in runsPerSession:
            redefSession = {}
            redefSession['day'] = session['_id']['timestamp']
            redefSession["timestamps"] = session['epoch']
            runTimestamps.append(redefSession)

        startTimesForSession = []
        for codeEdits, runs in zip(codeEditTimestamps, runTimestamps):
            m1 = min(codeEdits['timestamps'])
            m2 = min(runs['timestamps'])
            startTimesForSession.append(min(m1, m2))

        print(runTimestamps)

        fig, ax = plt.subplots(8, 8)
        self.plotTimeSeriesForSessions(codeEditTimestamps, startTimesForSession, sigma, ax, self.colorMapSessions, 8, 8, offset=30)
        self.plotTimeSeriesForSessions(runTimestamps, startTimesForSession, sigma, ax, self.colorMapSessions2, 8, 8, offset=30)
        #generate Labels
        custom_lines = []
        custom_names = []
        for attr, value in self.colorMapSessions.items():
            custom_names.append(attr)
            custom_lines.append(Line2D([0], [0], color=value, lw=4))
        for attr, value in self.colorMapSessions2.items():
            custom_names.append(attr)
            custom_lines.append(Line2D([0], [0], color=value, lw=4))
        fig.legend(custom_lines, custom_names)
        fig.text(0.5, 0.04, 'time (s)', ha='center')
        fig.text(0.04, 0.5, 'probability', va='center', rotation='vertical')

        plt.show()

    def plotTimeSeriesForSessions(self, timeStampsPerSession, startTimes, sigma, ax, colorMapSessions, subPltsX, subPltsY, offset=0):
        codeEditsPerSession = timeStampsPerSession # self.dataProxy.getCodeTreesPerSession()
        # generate session labels
        dateLabelMap = {}
        for index, datesForSession in enumerate(self.sessionDates):
            for date in datesForSession:
                dateLabelMap[date] = list(self.colorMapSessions.keys())[index]
        colorLabels = [colorMapSessions[dateLabelMap[session["day"]]] if session["day"] in dateLabelMap.keys() else
                       colorMapSessions["other"] for session in codeEditsPerSession]


        for i in range(subPltsX):
            for j in range(subPltsY):
                self.plotEventProbabilityForSession(codeEditsPerSession[offset + i * subPltsY + j]['timestamps'], startTimes[offset + i * subPltsY + j], sigma, ax[i, j],
                                                    color=colorLabels[offset + i * subPltsY + j])


    def plotEventProbabilityForSession(self, timeStamps, startTime, sigma, ax, color='tab:blue'):
        x, y = self.convertTimeStampsToProbabilityDistribution(timeStamps, startTime, sigma)
        ax.plot(x, y, color=color)

        #ax.set(xlabel='time (ms)', ylabel='chance of event being present',
        #       title='Probabilistic event model')
        ax.grid()

    def convertTimeStampsToProbabilityDistribution(self, timestamps, startTime, sigma):
        scalefactor = sigma * math.sqrt(math.pi * 2)
        startTime = int(startTime / 1000)
        endTime = int(max(timestamps) / 1000)
        y = []
        for x in range(endTime - startTime):
            intY = 0
            for timestamp in timestamps:
                intY += (math.exp(-0.5 * ((x - ((timestamp / 1000) - startTime)) / sigma) ** 2)) / scalefactor
            y.append(intY/len(timestamps)) # make integral of curve = 1
        x = range(endTime - startTime)

        return x, y

    def clusterBasedOnTime(self):
        codeEditsPerSession = self.dataProxy.getCodeTreesPerSession()

        #codeEditsPerSession = self.dataProxy.getRunEvents()
        timeDeltasPerSession = self.convertSessionsToTimeDeltas(codeEditsPerSession)
        # Generate session labels
        dateLabelMap = {}
        for index, datesForSession in enumerate(self.sessionDates):
            for date in datesForSession:
                dateLabelMap[date] = list(self.colorMapSessions.keys())[index]
        colorLabels = [self.colorMapSessions[dateLabelMap[session["_id"]["timestamp"]]] if session["_id"]["timestamp"] in dateLabelMap.keys() else self.colorMapSessions["other"] for session in codeEditsPerSession]
        # Convert to time bins
        maxTimeDelta = max(map(max, timeDeltasPerSession))
        test = self.convertTimeDeltaListToBins(timeDeltasPerSession[0], maxTimeDelta, 100)
        print(test)
        binnedTimes = list(map(lambda x: self.convertTimeDeltaListToBins(x, maxTimeDelta, 100), timeDeltasPerSession))
        # Convert to equal size numpy array
        length = max(map(len, binnedTimes))
        binnedTimesPerSession = np.array(binnedTimes)
        tsne = t_sne(n_components=2, perplexity=8, metric='euclidean')
        embedding = tsne.fit_transform(binnedTimesPerSession)
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.scatter(embedding[:, 0], embedding[:, 1], s=100, c=colorLabels)

        plt.show()


    def convertTimeDeltaListToBins(self, timeDeltas, max, step):
        binList = []
        for binmin in range(1, max, step):
            binmax = binmin + step
            count = 0
            for timeDelta in timeDeltas:
                if timeDelta/binmin >= 1 and timeDelta/binmax < 1:
                    count += 1
            binList.append(count)
        return binList
