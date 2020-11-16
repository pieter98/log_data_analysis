from .BaseVisualizer import BaseVisualizer
from .TimeBasedClusteringVisualizer import TimeBasedClusteringVisualizer
from .TimeBasedVisualizer import TimeBasedVisualizer
from ..DatabaseConnection.DataProxy import DataProxy
import statistics as stat
from sklearn.cluster import AffinityPropagation as Aprop
from matplotlib import pyplot as plt
import numpy as np
import scipy as sp
from scipy.signal import correlate as scor
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


class ConvolutionDistanceClustering(TimeBasedClusteringVisualizer):
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
        self.convolutionClustering(20)


    def convolutionClustering(self, sigma):
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
            m2 = 10000000000000000000 #min(runs['timestamps'])
            startTimesForSession.append(min(m1, m2))

        print(runTimestamps)

        probDists = []
        for index, cets in enumerate(codeEditTimestamps):
            probDists.append(self.convertTimeStampsToProbabilityDistribution(cets['timestamps'], startTimesForSession[index], sigma))

        print(probDists)

        '''sessionProbabilityDistributions = []
        for codeEditTimestamp, startTime in zip(codeEditTimestamps, startTimesForSession):
            x, y = self.convertTimeStampsToProbabilityDistribution(codeEditTimestamp['timestamps'], startTime, sigma)
            sessionProbabilityDistributions.append(y)'''

        '''fig, ax = plt.subplots(8, 8)

        for i in range(8):
            for j in range(8):
                x1, y1 = self.convertTimeStampsToProbabilityDistribution(codeEditTimestamps[30 + i]['timestamps'],
                                                                         startTimesForSession[30 + i], sigma)
                x2, y2 = self.convertTimeStampsToProbabilityDistribution(codeEditTimestamps[30 + j]['timestamps'],
                                                                         startTimesForSession[30 + j], sigma)
                y1 = np.array(y1)
                y2 = np.array(y2)
                out = scor(y1, y2, mode="full")
                #out = np.convolve(y1, y2, mode="full")
                x = range(len(out))
                ax[i, j].plot(x, out)
                ax[i, j].set(title="i" + str(i) + ", j" + str(j))

        plt.show()'''

    '''
        @brief calculates randomised cross correlation between random parts of both sequences
        @parm series1 the y values of time series 1
        @parm series2 the y values of time series 2
        @param locality the measure if small similarities (high locality) are more important than large ones (low locality).
    '''
    #def calculateRandomCrosCorDistanceBetweenTimeSeries(self, series1, series2, locality):





