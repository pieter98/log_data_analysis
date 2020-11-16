from Visualisations.Utils.MetaDataExtractor import MetaDataExtractor


class ClearLcdCountExtractor(MetaDataExtractor):

    def __init__(self):
        super().__init__()
        pass

    def extract(self, xmlString):
        return self.getBlockTypeCount(xmlString, 'clear_lcd')