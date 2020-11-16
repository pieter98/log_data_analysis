from Visualisations.Utils.MetaDataExtractor import MetaDataExtractor


class LedsOnOffCountExtractor(MetaDataExtractor):

    def __init__(self):
        super().__init__()
        pass

    def extract(self, xmlString):
        return self.getBlockTypeCount(xmlString, 'dwenguino_on_off')