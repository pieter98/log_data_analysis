from matplotlib import pyplot as plt


class BaseVisualizer:

    def __init__(self):
        plt.style.use('seaborn-talk')

    def visualize(self):
        pass