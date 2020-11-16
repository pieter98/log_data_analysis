from Visualisations.Utils.MetaDataExtractor import MetaDataExtractor


class DwenguinoLcdCountExtractor(MetaDataExtractor):
    def __init__(self):
        super().__init__()

    def extract(self, xmlString):
        return self.getBlockTypeCount(xmlString, "dwenguino_lcd")