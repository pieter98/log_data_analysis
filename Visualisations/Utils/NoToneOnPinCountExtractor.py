from Visualisations.Utils.MetaDataExtractor import MetaDataExtractor


class NoToneOnPinCountExtractor(MetaDataExtractor):

    def __init__(self):
        super().__init__()
        pass

    def extract(self, xmlString):
        return self.getBlockTypeCount(xmlString, 'dwenguino_no_tone_on_pin')