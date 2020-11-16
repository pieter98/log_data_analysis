from Visualisations.Utils.MetaDataExtractor import MetaDataExtractor


class LoopStatementCountExtractor(MetaDataExtractor):
    def __init__(self):
        super().__init__()

    def extract(self, xmlString):
        return self.getBlockTypeCount(xmlString, "controls_for")