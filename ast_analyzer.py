import pymongo
import igraph
from ast_node_encoding_upgrade import train, load_vectors
from data_generation.scenario_data_generator import ScenarioDataGenerator
from data_generation.xml_decision_tree_generator import XMLDecisionTreeGenerator
from treeparser import BlocklyTreeParser
from code_tree_analyzer import CodeTreeAnalyzer
from yaspin import yaspin

class AstAnalyzer:

    def __init__(self, database_connection, experimentId):
        self.experimentId = experimentId
        self.db_connection = database_connection

    def analyze(self, args):

        if 'generate_simple_data' in args:
            self.__generate_simple_data__(1000)

        if 'parse_simple_data' in args:
            xml_trees = self.db_connection.get_generated_simple_data_xml_blocks()
            print(xml_trees[0])
            
            parser = BlocklyTreeParser()
            analyzer = CodeTreeAnalyzer(None, parser)

            ast_trees = analyzer.convert_xml_trees_to_ast_trees(xml_trees)
            print(ast_trees[0])

            igraph_trees = analyzer.convert_ast_trees_to_igraph_ast_trees_keep_label(ast_trees)
            print(igraph_trees[0])
            print("\n")
            
            # igraph_obj = igraph_trees[0]

            # layout = igraph_obj.layout("kk")
            # igraph_obj.vs["label"] = igraph_obj.vs["name"]
            # igraph.plot(igraph_obj, layout=layout, bbox=(1600,900), margin=40, vertex_label_dist=-3)


            print(self.__get_unique_nodes_from_igraph_trees__(igraph_trees))

            self.__parse_data_from_ast_trees__(ast_trees)
            
        if 'generate_zig_zag_data' in args:
            self.__generate_zig_zag_data__(3000)
        
        if 'parse_zig_zag_data' in args:
            xml_trees = self.db_connection.get_generated_zig_zag_scenario_xml_blocks()
            print(xml_trees[0])
            
            parser = BlocklyTreeParser()
            analyzer = CodeTreeAnalyzer(None, parser)

            ast_trees = analyzer.convert_xml_trees_to_ast_trees(xml_trees)
            print(ast_trees[0])

            igraph_trees = analyzer.convert_ast_trees_to_igraph_ast_trees_keep_label(ast_trees)
            print(igraph_trees[0])
            print("\n")
            
            # igraph_obj = igraph_trees[0]

            # layout = igraph_obj.layout("kk")
            # igraph_obj.vs["label"] = igraph_obj.vs["name"]
            # igraph.plot(igraph_obj, layout=layout, bbox=(1600,900), margin=40, vertex_label_dist=-3)


            print(self.__get_unique_nodes_from_igraph_trees__(igraph_trees))

            self.__parse_data_from_ast_trees__(ast_trees)

        if 'train_network' in args:
            train.train()

        if 'load_vectors' in args:
            load_vectors.load_vectors()


    def __generate_simple_data__(self, amount):
        print("Generate data:\n")
        mydb = self.db_connection.get_generated_simple_data_DB()
        mycol = mydb["xml_data"]
        mycol.drop()

        generator = ScenarioDataGenerator(False)
        with yaspin(color='blue', text='Generated 0 xml trees') as spinner:
            for i in range (1, amount+1):
                mycol.insert_one({"xml_blocks":generator.generate_code()})
                spinner.text = "Generated {} xml trees".format(i)
            spinner.ok("✔")
    
    def __generate_zig_zag_data__(self, amount):
        print("Generate Zig Zag Scenario data\n")
        mydb = self.db_connection.get_generated_zig_zag_scenario_DB()
        mycol = mydb["xml_data"]
        mycol.drop()

        generator = XMLDecisionTreeGenerator()
        with yaspin(color='blue', text='Generated 0 xml trees') as spinner:
            for i in range(1, amount+1):
                xml_blocks, label = generator.generate_from_solution()
                mycol.insert_one({"xml_blocks":xml_blocks, "label":label})
                spinner.text = "Generated {} xml trees".format(i)
            spinner.ok("✔")
    
    def __get_unique_nodes_from_igraph_trees__(self, igraph_trees):
        unique_nodes = []
        for igraph in igraph_trees:
            for vertex in igraph.vs:
                if not vertex["name"] in unique_nodes:
                    unique_nodes.append(vertex["name"])
        with open('ast_node_encoding_upgrade/nodes.txt', 'w') as filehandle:
            for node in unique_nodes:
                filehandle.write("{}\n".format(node))
        return unique_nodes
            
    def __parse_data_from_ast_trees__(self, ast_trees):
        mydb = self.db_connection.get_generated_simple_data_DB()
        mycol = mydb["dataset"]
        mycol.drop()
        dataset = []
        for ast_tree in ast_trees:
            dataset = self.__parse_data_from_node__(ast_tree, dataset)

        mycol.insert_many(dataset)
        return dataset
    
    def __parse_data_from_node__(self, node, dataset):
        data = {}
        data["node"] = node.type
        children = []
        for child in node.childNodes:
            children.append(child.type)
            dataset = self.__parse_data_from_node__(child, dataset)
        data["children"] = children
        if node.parent:
            data["parent"] = node.parent.type
        else:
            data["parent"] = node.parent
        dataset.append(data)
        return dataset
        