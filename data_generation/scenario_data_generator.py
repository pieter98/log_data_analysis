import os, sys
import igraph
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import copy
import random
from yaspin import yaspin
from xml.etree import ElementTree as ET
from treeparser import BlocklyTreeParser
from code_tree_analyzer import CodeTreeAnalyzer
ET.register_namespace("","https://developers.google.com/blockly/xml")

# SCENARIO DATA GENERATOR

class ScenarioDataGenerator:

    def __init__(self, debug):
        self.debug = debug
        
        with yaspin(color='blue', text='Loading blocks') as spinner:
            spinner.write("LOADING BLOCKS:")

            spinner.write("  > Loading base")
            self.base_tree = self.__load_base_tree__()

            spinner.write("  > Loading DC motors")
            self.dc_motors = self.__load_dc_motors__()

            spinner.write("  > Loading Directions")
            self.directions = self.__load_directions__()

            spinner.write("  > Loading While Loops")
            self.while_loops = self.__load_while_loops__()
            
            spinner.write("  > Loading For Loops")
            self.for_loops = self.__load_for_loops__()

            spinner.write("  > Loading variable increments")
            self.variable_increment = self.__load_variable_increment__()

            spinner.ok("✔")

    def generate_code_test(self, file_path):
        new_tree = copy.deepcopy(self.base_tree)
        setup_loop = new_tree.getroot()[1]
        root = self.__add_loop__(setup_loop[1],False)
        root = self.__add_loop__(root, True)
        # root = self.add_loop(root, True)
        self.__add_dc_motors_in_loop__(root)
        with open(file_path + '.xml', 'wb') as f:
            new_tree.write(f)
        
        return new_tree.getroot()
    
    def generate_code(self):
        new_tree = copy.deepcopy(self.base_tree)
        setup_loop = new_tree.getroot()[1]
        root = setup_loop[1]
        if random.randint(0,100) < 80:
            root = self.__add_loop__(root, False)
            chance = 80
            generate = True
            while(generate):
                if random.randint(0,100) < chance and chance > 0:
                    root = self.__add_loop__(root, True)
                    chance = chance - 20
                else:
                    generate = False
        
        return ET.tostring(new_tree.getroot())


    #=========== LOAD BLOCKS FROM XML FILES ===========#
    def __load_base_tree__(self):
        base_tree = ET.parse("./data_generation/Blocks/base.xml")
        return base_tree

    def __load_dc_motors__(self):        
        dc_motors = []
        dc_motors_tree = ET.parse("data_generation/Blocks_scenario/driving robot dc motors.xml")
        for child in list(dc_motors_tree.getroot()):
            if '}block' in child.tag:
                dc_motors.append(child)
        return dc_motors
    
    def __load_directions__(self):
        directions = []
        drive_straight = ET.parse("data_generation/Blocks_scenario/driving robot drive straight.xml")
        turn_left = ET.parse("data_generation/Blocks_scenario/driving robot turn left.xml")
        turn_right = ET.parse("data_generation/Blocks_scenario/driving robot turn right.xml")
        for child in list(drive_straight.getroot()) + list(turn_left.getroot()) + list(turn_right.getroot()):
            if '}block' in child.tag:
                directions.append(child)
        return directions

    def __load_while_loops__(self):
        while_loops = []
        while_loops_tree = ET.parse("data_generation/Blocks_scenario/driving robot while loops.xml")
        for child in list(while_loops_tree.getroot()):
            if '}block' in child.tag:
                while_loops.append(child)
        return while_loops
    
    def __load_for_loops__(self):
        for_loops = []
        for_loops_tree = ET.parse("data_generation/Blocks_scenario/driving robot for loops.xml")
        for child in list(for_loops_tree.getroot()):
            if '}block' in child.tag:
                for_loops.append(child)
        return for_loops

    def __load_variable_increment__(self):
        variable_increment = []
        for child in list(ET.parse("data_generation/Blocks_scenario/driving robot variable increment.xml").getroot()):
            if '}block' in child.tag:
                variable_increment.append(child)
        return variable_increment

    #=========== ADD BLOCKS ===========#

    def __add_loop__(self, root, add_next):
        if random.randint(0,100) < 50:
            loop = self.__add_while_loop__(root, add_next)
        else:
            loop = self.__add_for_loop__(root, add_next)
        self.__add_dc_motors_in_loop__(loop)
        return loop

    def __add_while_loop__(self, root, add_next):
        if add_next:
            root = ET.SubElement(root, 'next')
        while_loop = copy.deepcopy(random.choice(self.while_loops))
        root.append(while_loop)
        return while_loop[2][0]

    def __add_for_loop__(self, root, add_next):
        if add_next:
            root = ET.SubElement(root, 'next')
        for_loop = copy.deepcopy(random.choice(self.for_loops))
        root.append(for_loop)
        if self.debug: print(for_loop.attrib.get("type"))
        return for_loop

    def __add_dc_motors_in_loop__(self, loop):          
        dc_motors = copy.deepcopy(random.choice(self.dc_motors))
        if loop.attrib.get("type") == 'controls_for':
            loop[4].append(dc_motors)
        else:
            temp = dc_motors
            while len(temp) == 3:
                if self.debug: print(dc_motors[2][0])
                temp = dc_motors[2][0]
            next_block = ET.SubElement(temp, 'next')
            next_block.append(copy.deepcopy(self.variable_increment[0]))
            loop[2].append(dc_motors)
            


def print_ET(tree):
    print("{} {}".format(tree.attrib.get('name'),tree.attrib.get('type')))
    for child in tree:
        print_ET(child)

print("\n\n")

def print_ast_tree(tree):
    print(tree)
    for child in tree.childNodes:
        print_ast_tree(child)

def generate_test_data():
    for i in range(1,11):
        generator = ScenarioDataGenerator(False)
        tree = generator.generate_code_test("data_generation/test_data/test_data_" + str(i))

        print_ET(tree)

        parser = BlocklyTreeParser()
        analyser = CodeTreeAnalyzer(None, parser)
        ast = analyser.convert_xml_trees_to_ast_trees([ET.tostring(tree)])

        print(ast[0])

        print("\n\n")

        igraphs = analyser.convert_ast_trees_to_igraph_ast_trees_keep_label(ast)
        igraph_obj = igraphs[0]

        layout = igraph_obj.layout("kk")
        igraph_obj.vs["label"] = igraph_obj.vs["name"]
        igraph.plot(igraph_obj, layout=layout, bbox=(1600,900), margin=40, vertex_label_dist=-3)

