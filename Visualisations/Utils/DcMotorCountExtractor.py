from Visualisations.Utils.MetaDataExtractor import MetaDataExtractor


class DcMotorCountExtractor(MetaDataExtractor):
    def __init__(self):
        super().__init__()

    def extract(self, xmlString):
        return self.getBlockTypeCount(xmlString, 'dc_motor')