from xml.etree import ElementTree as ET

from yaspin import yaspin
import random
import copy
ET.register_namespace("","https://developers.google.com/blockly/xml")

class XMLDecisionTreeGenerator:

    def __init__(self):
        print("creating decision tree generator")
        self.checkpoints = self.__parse_checkpoint_blocks__()
        self.base_tree = self.__load_base_tree__()
        self.solutions = self.__load_solutions__()
        self.solution_depths = self.__get_solution_depths__()

    def __parse_checkpoint_blocks__(self):
        checkpoints = []
        tree = ET.parse("./data_generation/checkpoint_blocks.xml")
        for child in list(tree.getroot()):
            if child.attrib.get("type"):
                checkpoints.append(child.attrib.get("type"))
        checkpoints.append("DO")
        for i in range(0,10):
            checkpoints.append("DO{}".format(i))
        checkpoints.append("ELSE")
        return checkpoints

    def __load_base_tree__(self):
        base_tree = ET.parse("./data_generation/zig_zag_robot/zig_zag_base.xml")
        return base_tree

    def __load_solutions__(self):
        solutions = []
        tree = ET.parse("./data_generation/zig_zag_robot/zig_zag_solutions_collection.xml")
        for child in list(tree.getroot()):
            solutions.append(child)
        return solutions

    def print_random_solution(self):
        new_tree = self.base_tree
        root = new_tree.getroot()
        # root.append(copy.deepcopy(random.choice(self.solutions)))
        root.append(self.solutions[0])
        with open('random_solution.xml', 'wb') as f:
            new_tree.write(f)

    def __get_solution_depths__(self):
        depths = []
        for i, solution in enumerate(self.solutions):
            depths.append(self.__get_solution_depth__(solution, 0))
        return depths

    def __get_solution_depth__(self, node, step_count):
        if "}block" in node.tag and node.attrib.get("type") in self.checkpoints:
            step_count += 1
        if "}statement" in node.tag and node.attrib.get("name") in self.checkpoints:
            step_count += 1

        for child in node:
                step_count = self.__get_solution_depth__(child, step_count)
        return step_count

    def generate_from_solution(self):
        index = random.randint(0,len(self.solutions)-1)
        solution = copy.deepcopy(self.solutions[index])
        steps = self.__traverse_solution__(solution, 0, None)
        label = "{}/{}".format(steps[1], self.solution_depths[index])
        

        new_tree = copy.deepcopy(self.base_tree)
        root = new_tree.getroot()
        root.append(solution)
        return ET.tostring(new_tree.getroot()), label

    def __traverse_solution__(self, node, step_count, parent):
        end = False
        checkpoint = False
        if "field" in node.tag and "VAR" in node.attrib.get("name"):
            node.attrib.pop("id")
        if "}block" in node.tag and node.attrib.get("type") in self.checkpoints:
            step_count += 1
            checkpoint = True
        if "}statement" in node.tag and node.attrib.get("name") in self.checkpoints:
            step_count += 1
            checkpoint = True
        
        if checkpoint:
            if random.randint(0,100) < 10:
                end = True

        for child in node:
            if not end:
                child, step_count, end = self.__traverse_solution__(child, step_count, node)
            else:
                node.remove(child)
        return node, step_count, end

    
    # def __traverse_solution_1__(self):
    #     solution = copy.deepcopy(self.solutions[1])
    #     steps = self.__inspect_children__(solution, 0, None)
    #     new_tree = copy.deepcopy(self.base_tree)
    #     root = new_tree.getroot()
    #     root.append(solution)
    #     with open('random_generation_2.xml', 'wb') as f:
    #         new_tree.write(f)
            

    # def __inspect_children__(self, node, step_count, parent):
    #     end = False
    #     checkpoint = False
    #     if "field" in node.tag and "VAR" in node.attrib.get("name"):
    #         node.attrib.pop("id")
    #     if "}block" in node.tag and node.attrib.get("type") in self.checkpoints:
    #         step_count += 1
    #         checkpoint = True
    #     if "}statement" in node.tag and node.attrib.get("name") in self.checkpoints:
    #         step_count += 1
    #         checkpoint = True
        
    #     if checkpoint:
    #         if random.randint(0,100) < 10:
    #             end = True

    #     for child in node:
    #         if not end:
    #             child, step_count, end = self.__inspect_children__(child, step_count, node)
    #         else:
    #             node.remove(child)
    #     return node, step_count, end



