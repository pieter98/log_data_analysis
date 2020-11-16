from .ChangesPerSessionVisualizer import ChangesPerSessionVisualizer
from .ColorPlotVisualizer import ColorPlotVisualizer
from Visualisations.Visualizer.VisualizerTypes import VisualizerTypes
from .ConvolutionDistanceClustering import ConvolutionDistanceClustering
from .TimeBasedClusteringVisualizer import TimeBasedClusteringVisualizer
from .TimeBasedVisualizer import TimeBasedVisualizer
from .EventPatternVisualizer import EventPatternVisualizer


class VisualizerControl:

    def __init__(self):
        self.visualizers = {}
        self.visualizers[VisualizerTypes.COLORPLOTVISUALISATION1] = ColorPlotVisualizer()
        self.visualizers[VisualizerTypes.CHANGESPERSESSION] = ChangesPerSessionVisualizer()
        self.visualizers[VisualizerTypes.TIMEBASEDCLUSERING] = TimeBasedClusteringVisualizer()
        self.visualizers[VisualizerTypes.TIMEBASEDVISUALIZER] = TimeBasedVisualizer()
        self.visualizers[VisualizerTypes.CONVOLUTIOCLUSTERING] = ConvolutionDistanceClustering()
        self.visualizers[VisualizerTypes.EVENTPATTERNEXTRACTOR] = EventPatternVisualizer()

    def showVisualisation(self, visualisationId):
        self.visualizers[visualisationId].visualize()
