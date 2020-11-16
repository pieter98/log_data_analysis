import xml.etree.ElementTree as ET

class MetaDataExtractor:

    def __init__(self):
        pass

    def extract(self, xmlString):
        pass

    def getBlockTypeCount(self, xmlString, blockType):
        tree = ET.fromstring(xmlString)
        ifElements = tree.findall(".//{{http://www.w3.org/1999/xhtml}}block[@type='{0}']".format(blockType))
        return len(ifElements)

