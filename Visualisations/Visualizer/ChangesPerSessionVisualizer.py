from .BaseVisualizer import BaseVisualizer
from ..DatabaseConnection.DataProxy import DataProxy
from matplotlib import pyplot as plt
import numpy as np
from matplotlib.lines import Line2D

from ..Utils.DcMotorCountExtractor import DcMotorCountExtractor
from ..Utils.DelayCountExtractor import DelayCountExtractor
from ..Utils.DwenguinoLcdCountExtractor import DwenguinoLcdCountExtractor
from ..Utils.IfStatementCountExtractor import IfStatementCountExtractor
from ..Utils.LoopStatementCountExtractor import LoopStatementCountExtractor
from ..Utils.MetaDataExtractor import MetaDataExtractor
from ..Utils.SonarCountExtractor import SonarCountExtractor


class ChangesPerSessionVisualizer(BaseVisualizer):
    def __init__(self):
        self.dataProxy = DataProxy()
        self.dataProxy.setDataSource('BlocklyLogCreate', 'log')
        self.extractors = [DcMotorCountExtractor(),
                      IfStatementCountExtractor(),
                      LoopStatementCountExtractor(),
                      DwenguinoLcdCountExtractor(),
                      DelayCountExtractor(),
                      SonarCountExtractor()]
        self.extractorNames = ["DC Motor",
                               "If statement",
                               "LoopStatement",
                               "LCD",
                               "Delay",
                               "Sonar"]


    def visualize(self):
        #codeEditsPerSession = self.dataProxy.getCodeTreesPerSession()
        codeEditCountPerSession = [session['count'] for session in codeEditsPerSession]
        sessionNumbers = range(len(codeEditCountPerSession))
        ax = plt.subplot(1, 1, 1)
        ax.bar(sessionNumbers, codeEditCountPerSession)
        plt.title("Number of code edits for each session")
        plt.show()

        statementCountsPerSession = []
        for extractor in self.extractors:
            statementsPerSessionCount = [sum(map(lambda x: extractor.extract(x['xml']), session['code'])) for session in codeEditsPerSession]
            statementCountsPerSession.append(statementsPerSessionCount)

        # normalize per session
        for index in range(len(statementCountsPerSession[0])):
            s = 0
            for extractorNumber in range(len(statementCountsPerSession)):
                s += statementCountsPerSession[extractorNumber][index]
            for extractorNumber in range(len(statementCountsPerSession)):
                if s != 0:
                    statementCountsPerSession[extractorNumber][index] = statementCountsPerSession[extractorNumber][index] / s * 100


        fig, ax = plt.subplots()
        bottom = [0 for i in range(len(statementCountsPerSession[0]))]
        for index, statementCount in enumerate(statementCountsPerSession):
            ax.bar(sessionNumbers, statementCount, 0.5, bottom=bottom, label=self.extractorNames[index])
            bottom = [sum(x) for x in zip(bottom, statementCount)]

        ax.set_ylabel('Total occurences of a code element')
        ax.set_title('Code element count for all logged programs per session')
        ax.legend()

        plt.show()

