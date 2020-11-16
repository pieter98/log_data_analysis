from .BaseVisualizer import BaseVisualizer
from ..DatabaseConnection.DataProxy import DataProxy
from matplotlib import pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from sklearn.manifold import TSNE as t_sne
from numpy.polynomial.polynomial import polyfit

from ..Utils.DcMotorCountExtractor import DcMotorCountExtractor
from ..Utils.DelayCountExtractor import DelayCountExtractor
from ..Utils.DwenguinoLcdCountExtractor import DwenguinoLcdCountExtractor
from ..Utils.IfStatementCountExtractor import IfStatementCountExtractor
from ..Utils.LoopStatementCountExtractor import LoopStatementCountExtractor
from ..Utils.MetaDataExtractor import MetaDataExtractor
from ..Utils.SonarCountExtractor import SonarCountExtractor


class EventPatternVisualizer(BaseVisualizer):
    def __init__(self):
        self.dataProxy = DataProxy()
        self.dataProxy.setDataSource('BlocklyLogDebug', 'log')


    def visualize(self):
        eventsPerSession = self.dataProxy.getEventsPerSession()
        self.calculateSessionStats(eventsPerSession)
        #self.timeplot(eventsPerSession)

    def timeplot(self, eventsPerSession):
        timesPerSession = list(map(lambda x: [event['epoch'] for event in x['events']], eventsPerSession))
        startTimes = list(map(lambda x: min(x), timesPerSession))
        timesPerSession = [[x - startTimes[i] for x in session] for i, session in enumerate(timesPerSession)]
        timesPerSession = list(filter(lambda x: len(x) > 100, timesPerSession))
        sub = 0
        compressedTimesPerSecond = []
        for i, session in enumerate(timesPerSession):
            sub = 0
            compressedTimesPerSecond.append([])
            for j, time in enumerate(session):
                if j == 0:
                    compressedTimesPerSecond[i].append(timesPerSession[i][j] - sub)
                    continue
                if time - session[j-1] > 1000000:
                    sub += time - session[j-1]
                compressedTimesPerSecond[i].append(timesPerSession[i][j] - sub)

        allEvents = []
        for session in timesPerSession:
            allEvents = allEvents + session
        weights = [1/len(timesPerSession) for e in allEvents]

        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.hist(allEvents, range(0, max(allEvents), 1000), weights=weights)
        # ax.scatter(changeVsRuns[:, 0], changeVsRuns[:, 1])
        ax.set_xlabel('Time (1 bar = 1 second)')
        ax.set_ylabel('Average # event logged')
        plt.show()

    def calculateSessionStats(self, eventsPerSession):
        stats = list(map(self.caclulateEventHistogramForSession, eventsPerSession))
        '''changeVsRuns = list(map(lambda hist: [hist["changedWorkspace"] if "changedWorkspace" in hist else 0, 
                                              hist["runClicked"] if "runClicked" in hist else 0], stats))'''
        '''changeVsRuns = list(map(lambda hist: [hist["changedWorkspace"] if "changedWorkspace" in hist else 0,
                                              hist["simStart"] if "simStart" in hist else 0], stats))'''
        changeVsRuns = list(map(lambda hist: [hist["changedWorkspace"] if "changedWorkspace" in hist else 0,
                                                hist["runClicked"] + hist["simStart"] if ("runClicked" in hist and "simStart" in hist) else
                                                hist["runClicked"] if "runClicked" in hist else
                                                hist["simStart"] if "simStart" in hist else
                                                0], stats))
        print(changeVsRuns)
        changeVsRuns = np.array([np.array(elem) for elem in changeVsRuns])

        eventNames = ["blocklyBlockCreate", "blocklyBlockDelete", "blocklyBlockMove", "blocklyChange",	"changedWorkspace", "runClicked", "simStart"]
        barColors = ["red", "green", "blue", "yellow", "orange", "purple", "brown"]

        # calculate regression line
        q, m = polyfit(changeVsRuns[:, 0], changeVsRuns[:, 1], 1)

        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.plot(changeVsRuns[:, 0], changeVsRuns[:, 1], '.')
        ax.plot(changeVsRuns[:, 0], q + m * changeVsRuns[:, 0], '-')
        #ax.scatter(changeVsRuns[:, 0], changeVsRuns[:, 1])
        ax.set_xlabel('#changedWorkspace')
        ax.set_ylabel('#runClicked')
        plt.show()

        fig, ax = plt.subplots(10, 13, sharey=True)

        freqtables = []

        for i in range(10):
            for j in range(13):
                index = i*13 + j
                freq_table = list(map(lambda name: stats[index][name] if name in stats[index] else 0, eventNames))
                freqtables.append(freq_table)
                x = range(len(freq_table))
                ax[i, j].bar(x, freq_table, color=barColors)

        custom_lines = list(map(lambda color: Line2D([0], [0], color=color, lw=4), barColors))
        fig.legend(custom_lines, eventNames)

        plt.show()

        freqtables = np.array([np.array(elem) for elem in freqtables])

        tsne = t_sne(n_components=2, perplexity=10, metric='euclidean')
        embedding = tsne.fit_transform(freqtables)
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.scatter(embedding[:, 0], embedding[:, 1], s=100)

        plt.show()


    def caclulateEventHistogramForSession(self, session):
        events = session['events']
        events.sort(key=(lambda a: a['epoch']))
        eventNames = list(map(lambda e: e['name'], events))
        eventHistogram = dict(zip(eventNames, [eventNames.count(i) for i in eventNames]))
        return eventHistogram



