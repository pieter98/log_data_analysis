import copy
import random
from yaspin import yaspin
from xml.etree import ElementTree as ET
from treeparser import treeparser
from code_tree_analyzer import CodeTreeAnalyzer
ET.register_namespace("","https://developers.google.com/blockly/xml")

# SCENARIO DATA GENERATOR

class ScenarioDataGenerator:

    def __init__(self, debug):
        self.debug = debug
        
        with yaspin(color='blue', text='Loading blocks') as spinner:
            spinner.write("LOADING BLOCKS:")

            spinner.write("  > Loading base")
            self.base_tree = self.load_base_tree()

            spinner.write("  > Loading DC motors")
            self.dc_motors = self.load_dc_motors()

            spinner.write("  > Loading Directions")
            self.directions = self.load_directions()

            spinner.write("  > Loading While Loops")
            self.while_loops = self.load_while_loops()
            
            spinner.write("  > Loading For Loops")
            self.for_loops = self.load_for_loops()

            spinner.write(" > Loading variable increments")
            self.variable_increment = self.load_variable_increment()

            spinner.ok("✔")

    def generate_code_test(self):
        new_tree = copy.deepcopy(self.base_tree)
        setup_loop = new_tree.getroot()[1]
        root = self.add_loop(setup_loop[1],False)
        root = self.add_loop(root, True)
        root = self.add_loop(root, True)
        self.add_dc_motors_in_loop(root)
        with open('generator-test.xml', 'wb') as f:
            new_tree.write(f)

    #=========== LOAD BLOCKS FROM XML FILES ===========#
    def load_base_tree(self):
        base_tree = ET.parse("./data_generation/Blocks/base.xml")
        return base_tree

    def load_dc_motors(self):        
        dc_motors = []
        dc_motors_tree = ET.parse("data_generation/Blocks_scenario/driving robot dc motors.xml")
        for child in list(dc_motors_tree.getroot()):
            if '}block' in child.tag:
                dc_motors.append(child)
        return dc_motors
    
    def load_directions(self):
        directions = []
        drive_straight = ET.parse("data_generation/Blocks_scenario/driving robot drive straight.xml")
        turn_left = ET.parse("data_generation/Blocks_scenario/driving robot turn left.xml")
        turn_right = ET.parse("data_generation/Blocks_scenario/driving robot turn right.xml")
        for child in list(drive_straight.getroot()) + list(turn_left.getroot()) + list(turn_right.getroot()):
            if '}block' in child.tag:
                directions.append(child)
        return directions

    def load_while_loops(self):
        while_loops = []
        while_loops_tree = ET.parse("data_generation/Blocks_scenario/driving robot while loops.xml")
        for child in list(while_loops_tree.getroot()):
            if '}block' in child.tag:
                while_loops.append(child)
        return while_loops
    
    def load_for_loops(self):
        for_loops = []
        for_loops_tree = ET.parse("data_generation/Blocks_scenario/driving robot for loops.xml")
        for child in list(for_loops_tree.getroot()):
            if '}block' in child.tag:
                for_loops.append(child)
        return for_loops

    def load_variable_increment(self):
        variable_increment = []
        for child in list(ET.parse("data_generation/Blocks_scenario/driving robot variable increment.xml").getroot()):
            if '}block' in child.tag:
                variable_increment.append(child)
        return variable_increment

    #=========== ADD BLOCKS ===========#

    def add_loop(self, root, add_next):
        if random.randint(0,100) < 50:
            loop = self.add_while_loop(root, add_next)
        else:
            loop = self.add_for_loop(root, add_next)
        self.add_dc_motors_in_loop(loop)
        return loop

    def add_while_loop(self, root, add_next):
        if add_next:
            root = ET.SubElement(root, 'next')
        while_loop = copy.deepcopy(random.choice(self.while_loops))
        root.append(while_loop)
        return while_loop[2][0]

    def add_for_loop(self, root, add_next):
        if add_next:
            root = ET.SubElement(root, 'next')
        for_loop = copy.deepcopy(random.choice(self.for_loops))
        root.append(for_loop)
        if self.debug: print(for_loop.attrib.get("type"))
        return for_loop

    def add_dc_motors_in_loop(self, loop):          
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
            


generator = ScenarioDataGenerator(False)
generator.generate_code_test()

parser = treeparser()
analyser = CodeTreeAnalyzer(None, parser)