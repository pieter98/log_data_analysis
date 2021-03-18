import pymongo
import random
import xml.etree.ElementTree as ET
import xml
import copy
ET.register_namespace("","https://developers.google.com/blockly/xml")

class data_generator:

    def __init__(self, debug):
        if debug: print("initiating data generator:")
        self.debug = debug
        self.base_tree = self.load_base_tree()
        self.logic_compares = self.load_logic_compares()
        self.logic_operations = self.load_logic_operations()
        self.while_loops = self.load_while_loops()
        self.for_loops = self.load_for_loops()
        self.variables = self.load_variables()
        self.numeric_variables = self.load_numeric_variables()
        self.dwenguino_blocks = self.load_dwenguino_blocks()
        self.if_structures = self.load_if_structures()
    
    #=========== LOAD BLOCKS FROM XML FILES ===========#
    def load_base_tree(self):
        if self.debug: print("\tLoading base tree")
        base_tree = ET.parse("./data_generation/Blocks/base.xml")
        return base_tree
 
    def load_logic_compares(self):
        if self.debug: print("\tLoading logic compares")
        logic_compares = []
        logic_compares_tree = ET.parse("./data_generation/Blocks/logic compares.xml")
        for child in list(logic_compares_tree.getroot()):
            if '}block' in child.tag:
                logic_compares.append(child)
        return logic_compares

    def load_logic_operations(self):
        if self.debug: print("\tLoading logic operations")
        logic_operations = []
        logic_operations_tree = ET.parse("./data_generation/Blocks/logic operations.xml")
        for child in list(logic_operations_tree.getroot()):
            if '}block' in child.tag:
                logic_operations.append(child)
        return logic_operations
    
    def load_variables(self):
        if self.debug: print("\tLoading variables")
        variables = []
        variables_tree = ET.parse("./data_generation/Blocks/variables.xml")
        for child in list(variables_tree.getroot()):
            if '}block' in child.tag:
                variables.append(child)
        return variables

    def load_numeric_variables(self):
        if self.debug: print("\tLoading numeric variables")
        numeric_variables = []
        numeric_variables_tree = ET.parse("./data_generation/Blocks/numeric variables.xml")
        for child in list(numeric_variables_tree.getroot()):
            if '}block' in child.tag:
                numeric_variables.append(child)
        return numeric_variables

    def load_while_loops(self):
        if self.debug: print("\tLoading while loop structures")
        while_loops = []
        while_loops_tree = ET.parse("./data_generation/Blocks/while loops.xml")
        for child in list(while_loops_tree.getroot()):
            if '}block' in child.tag:
                while_loops.append(child)
        return while_loops

    def load_for_loops(self):
        if self.debug: print("\tLoading for loops")
        for_loops = []
        for_loops_tree = ET.parse("./data_generation/Blocks/for loops.xml")
        for child in list(for_loops_tree.getroot()):
            if '}block' in child.tag:
                for_loops.append(child)
        return for_loops

    def load_dwenguino_blocks(self):
        if self.debug: print("\tLoading dwenguino blocks")
        dwenguino_blocks = []
        dwenguino_blocks_tree = ET.parse("./data_generation/Blocks/dwenguino blocks updated.xml")
        for child in list(dwenguino_blocks_tree.getroot()):
            if '}block' in child.tag:
                dwenguino_blocks.append(child)
        return dwenguino_blocks

    def load_if_structures(self):
        if self.debug: print("\tLoading if structures")
        if_structures = []
        if_structures_tree = ET.parse("./data_generation/Blocks/if structures.xml")
        if_structures.append(list(if_structures_tree.getroot())[0])
        for i in range(1,len(list(if_structures_tree.getroot()))):
            if_structures.append(if_structures_tree.getroot()[i])
        return if_structures

    #=========== GENERATE CODE FUNCTIONS ===========#
    def generate_code(self, filename):
        new_tree = copy.deepcopy(self.base_tree)
        setup_loop = new_tree.getroot()[1]
        depth = 0
        # code generation for setup part of base structure      
        # self.add_blocks_including_loop_structures(depth, 30, setup_loop[0])
        # self.add_for_loop(depth, 30, setup_loop[0])

        # 80% chance to add blocks in the setup part
        if random.randint(0,100) < 80:
            self.add_blocks_no_loop_structures(depth, 10, setup_loop[0])
        
        # 80% chance to add blocks to the loop part, including loop structures
        if random.randint(0,100) < 80:
            self.add_blocks_including_loop_structures(depth, 10, setup_loop[1])

        if self.debug: print("start writing to file")
        with open(filename + '.xml', 'wb') as f:
            new_tree.write(f)
        if self.debug: print("done writing to file")

    def generate_code_test(self):
        new_tree = copy.deepcopy(self.base_tree)
        setup_loop = new_tree.getroot()[1]
        self.add_blocks(0, 10, setup_loop[0], False)
        self.add_blocks(0, 10, setup_loop[1], True)

        with open('generator-test.xml', 'wb') as f:
            new_tree.write(f)

    #=========== ADD BLOCKS FUNCTIONS ===========#

    def add_blocks(self, depth, max_count, elem, loops_included):
        # 50% chance of adding more blocks
        if random.randint(0,100) < 95:
            if loops_included:
                self.add_blocks_including_loop_structures(depth, max_count, elem)
            else:
                self.add_blocks_no_loop_structures(depth, max_count, elem)

    # add random blocks, no loop structures included
    def add_blocks_no_loop_structures(self, depth, max_count, elem):
        depth += 1
        if random.randint(0,100) < 95:
            temp = self.add_block(depth, elem)
        else:
            temp = self.add_if_structure(depth, max_count, elem)

        while(depth < max_count):
            if random.randint(0,100) < 80:
                if self.debug: print("adding another block")
                temp = self.add_block_after_block(depth, max_count, temp, False)
                depth += 1
                if self.debug: print(depth)
            else: break
    
    # add random blocks, includes loop structure options
    def add_blocks_including_loop_structures(self, depth, max_count, elem):
        if self.debug: print("adding block")
        depth += 1
        # 5% chance to add while loop and 5% chance to add for
        if depth < max_count:
            chance = random.randint(0,100)
            if chance < 5:
                temp = self.add_while_loop(depth, max_count, elem)
            elif chance >=5 and chance < 10:
                temp = self.add_for_loop(depth, max_count, elem)
            else:
                temp = self.add_block(depth, elem)
        
        # 80% chance to add more blocks
        while(depth < max_count):
            if random.randint(0,100) < 80:
                if self.debug: print("adding another block")
                temp = self.add_block_after_block(depth, max_count, temp)
                depth += 1
                if self.debug: print(depth)
            else: break
    
    #=========== HELPER FUNCTIONS ===========#

    # add simple if statement
    def add_if_structure(self, depth, max_count, elem, loops_included=False):
        depth += 1

        if_structure = copy.deepcopy(random.choice(self.if_structures))
        if depth < max_count:
            if len(if_structure) == 2:
                self.add_bool_structure(if_structure[0])
                self.add_blocks(depth, max_count, if_structure[1], loops_included)
            else: 
                for i in range(1, len(if_structure)):
                    if i is len(if_structure)-1:
                        self.add_blocks(depth, max_count, if_structure[i], loops_included)
                    elif i%2 == 1:
                        self.add_bool_structure(if_structure[i])
                    else:
                        self.add_blocks(depth, max_count, if_structure[i], loops_included)
        elem.append(if_structure)
        return if_structure

    # adds a for loop to the element
    def add_for_loop(self, depth, max_count, elem):
        depth += 1
        for_loop = copy.deepcopy(random.choice(self.for_loops))

        # 80% chance to add blocks to the for loop do statement
        if random.randint(0,100) < 80:
            if self.debug: print(for_loop[4].attrib.get("name"))
            self.add_blocks_including_loop_structures(depth, max_count, for_loop[4])
        elem.append(for_loop)
        return for_loop
    
    # adds a while loop to the element
    def add_while_loop(self, depth, max_count, elem):
        depth += 1
        while_loop = copy.deepcopy(random.choice(self.while_loops))

        # provide a boolean structure for the while loop
        boolean_root = while_loop[1]
        self.add_bool_structure(boolean_root)
        # 80% chance to add blocks to the while loop DO statement
        if random.randint(0,100) < 80:
            self.add_blocks_including_loop_structures(depth, max_count, while_loop[2])
        # add the while loop to the element
        elem.append(while_loop)
        if self.debug: print("done adding bool struct")
        return while_loop

    # creates a bool structure used for while loop
    def add_bool_structure(self, boolean_root):
        max_depth = 10
        depth_count = 0
        if random.randint(0,100) < 5:
            if self.debug: print("logic operation")
            self.add_logic_operation(boolean_root, max_depth, depth_count)
        else:
            if self.debug: print("logic compare")
            self.add_logic_compare(boolean_root)

    # adds a logic operation to a bool structure
    def add_logic_operation(self, boolean_root, max_depth, depth_count):
        depth_count += 1
        logic_operation = copy.deepcopy(random.choice(self.logic_operations))
        for i in range(1,3):
            if self.debug: print(logic_operation[i].attrib.get("name")) 
            #10% chance to get a logic operation, otherwise it's a logic compare
            if (random.randint(0,100) < 10) and (depth_count < max_depth):
                if self.debug: print(depth_count)                
                self.add_logic_operation(logic_operation[i], max_depth, depth_count)
            else:
                self.add_logic_compare(logic_operation[i])
        if self.debug: print("adding logic operation to boolean root")
        boolean_root.append(logic_operation)
    
    # adds a logic compare to a bool structure
    def add_logic_compare(self, boolean_root):
        logic_compare = copy.deepcopy(random.choice(self.logic_compares))
        #numerieke variabelen toevoegen
        logic_compare[1].append(copy.deepcopy(random.choice(self.numeric_variables)))
        logic_compare[2].append(copy.deepcopy(random.choice(self.numeric_variables)))
        boolean_root.append(logic_compare)

    # appends a block after another block
    def add_block(self, depth, elem):
        depth += 1
        elem.append(copy.deepcopy(random.choice(self.dwenguino_blocks)))
        elem = elem[0]
        return elem
    
    # appends a block after another block
    def add_block_after_block(self, depth, max_count, elem, loops_included=True):
        depth += 1
        child = ET.Element("next")
        elem.append(child)
        if loops_included:
            chance = random.randint(0,100)
            if chance < 5:
                self.add_while_loop(depth, max_count, child)
            elif chance >= 5 and chance < 10:
                self.add_for_loop(depth, max_count, child)
            elif chance >= 10 and chance < 15:
                self.add_if_structure(depth, max_count, child, loops_included)
            else:
                self.add_block(depth, child)
        else:
            if random.randint(0,100) < 95:
                self.add_block(depth, child)
            else:
                self.add_if_structure(depth, max_count, child)
        return child[0]

        

    

generator = data_generator(False)
for i in range(1,11):
    generator.generate_code("data_generation/test_data/test_data_" + str(i))
# generator.generate_code_test()