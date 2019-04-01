import xml.etree.ElementTree as ET


class CodeGenerator:
    solution_file = "./code_trees/solution_drive_square.xml"

    def __init__(self):
        None

    def read_solution_tree(self):
        tree = ET.parse(self.solution_file)
        root = tree.getroot()
        for child in root:
            print(child.tag, child.attrib)
        print(root)