from Visualisations.Utils.MetaDataExtractor import MetaDataExtractor


class WhileUntilCountExtractor(MetaDataExtractor):

    def __init__(self):
        super().__init__()
        pass

    def extract(self, xmlString):
        return self.getBlockTypeCount(xmlString, 'controls_whileUntil')