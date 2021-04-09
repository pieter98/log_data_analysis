from database_connection import DatabaseConnection
from igraph import *
import graphkernels.kernels as gk
import matplotlib.pyplot as plt
import seaborn as sns
from my_enums import WorkshopType

class CodeTreeAnalyzer:

    #1520340863837
    session1_epoch = [(1520290800000, 1520373600000), (1521414000000, 1521496800000), (1521500400000, 1521583200000), (1523829600000, 1523912400000), (1524434400000, 1524517200000)]
    session2_epoch = [(1520895600000, 1520978400000), (1521500400000, 1521583200000), (1522101600000, 1522184400000), (1523916000000, 1523998800000), (1524520800000, 1524603600000)]
    session_epochs = []

    def __init__(self, database_connection, treeparser):
        self.database_connection = database_connection
        self.treeparser = treeparser
        self.session_epochs.append(self.session1_epoch)
        self.session_epochs.append(self.session2_epoch)

    def get_all_xml_code_trees(self, workshop_type=WorkshopType.BOTH):
        code_trees = []
        timestamps = []
        session_ids = []
        labels = []
        code_trees_by_session = self.database_connection.get_code_trees_for(workshop_type=workshop_type)
        for session in code_trees_by_session:
            for tree in session["eventsForSession"]:
                code_trees.append(tree["data"])
                timestamps.append(tree["timestamp"])
                session_ids.append(session["_id"])
            for label in session["labelsForSession"]:
                labels.append(label)

        print("timestamps")
        print(timestamps)
        return (code_trees, timestamps, session_ids, labels)

    def get_xml_code_trees_for_session(self, session):
        code_trees = []
        timestamps = []
        session_ids = []
        for (startepoch, endepoch) in self.session_epochs[session]:
            code_trees_by_session = self.database_connection.get_code_trees_for(start_date=startepoch, end_date=endepoch)
            for session in code_trees_by_session:
                for tree in session["eventsForSession"]:
                    code_trees.append(tree["data"])
                    timestamps.append(tree["timestamp"])
                    session_ids.append(session["_id"])
        print("timestamps")
        print(timestamps)
        return (code_trees, timestamps, session_ids)

    def convert_xml_trees_to_ast_trees(self, xml_trees):
        ast_trees = []
        for index, xml_tree in enumerate(xml_trees):
            ast_trees.append(self.treeparser.constructCodeTree(xml_tree))
            if index % 1000 == 0:
                print("Number of trees converted:")
                print(index)
        #print(ast_trees)
        return ast_trees

    def convert_ast_trees_to_igraph_ast_trees(self, ast_trees):
        # fist count the number of unique labels:
        nr_unique_labels = self.count_unique_vertex_labels(ast_trees)
        igraph_ast_trees = []
        node_label_conversion_table = []    # This list maps the original node names to unique integers.
        for i, ast_tree in enumerate(ast_trees):
            index = -1
            graph = Graph()
            self.construct_igraph_subtree(ast_tree, index, -1, graph, node_label_conversion_table, nr_unique_labels)
            igraph_ast_trees.append(graph)
            if i % 1000 == 0:
                print("Number of trees converted to igraph:")
                print(i)
        '''for a in range(70000, 70020):
            g = igraph_ast_trees[a]
            layout = g.layout("kk")
            g.vs["label"] = g.vs["name"]
            plot(g, layout=layout)'''
        return igraph_ast_trees

    def convert_ast_trees_to_igraph_ast_trees_keep_label(self, ast_trees):
        # fist count the number of unique labels:
        nr_unique_labels = self.count_unique_vertex_labels(ast_trees)
        igraph_ast_trees = []
        node_label_conversion_table = []    # This list maps the original node names to unique integers.
        for i, ast_tree in enumerate(ast_trees):
            index = -1
            graph = Graph()
            self.construct_igraph_subtree_keep_label(ast_tree, index, -1, graph, node_label_conversion_table, nr_unique_labels)
            igraph_ast_trees.append(graph)
            if i % 1000 == 0:
                print("Number of trees converted to igraph:")
                print(i)
        '''for a in range(70000, 70020):
            g = igraph_ast_trees[a]
            layout = g.layout("kk")
            g.vs["label"] = g.vs["name"]
            plot(g, layout=layout)'''
        return igraph_ast_trees

    def convert_ast_trees_to_igraph_ast_trees_connected_siblings(self, ast_trees):
        # fist count the number of unique labels:
        nr_unique_labels = self.count_unique_vertex_labels(ast_trees)
        igraph_ast_trees = []
        node_label_conversion_table = []    # This list maps the original node names to unique integers.
        for i, ast_tree in enumerate(ast_trees):
            index = -1
            graph = Graph()
            self.construct_igraph_subtree_connected_siblings(ast_tree, index, -1, graph, node_label_conversion_table, nr_unique_labels)
            igraph_ast_trees.append(graph)
            if i % 1000 == 0:
                print("Number of trees converted to igraph:")
                print(i)
                #print(graph.vs["name"])
                #print(graph.es["label"])
                #summary(graph)
                #print(graph)
        return igraph_ast_trees

    def count_unique_vertex_labels(self, ast_trees):
        c_tab = []
        for ast_tree in ast_trees:
            self.map_vertex_names_to_ints(ast_tree, c_tab)
        return len(c_tab)


    def map_vertex_names_to_ints(self, vertex, conversion_table):
        if vertex.type not in conversion_table:
            conversion_table.append(vertex.type)
        for i, child in enumerate(vertex.childNodes):
            self.map_vertex_names_to_ints(child, conversion_table)
        return


    def construct_igraph_subtree(self, vertex, index, parent_index, graph, node_label_conversion_table, nr_unique_labels):
        # Map the vertex name to an integer, if it does not exist yet -> add it
        if vertex.type not in node_label_conversion_table:
            node_label_conversion_table.append(vertex.type)
        new_label = node_label_conversion_table.index(vertex.type)

        graph.add_vertex(name=new_label)
        index += 1
        if (parent_index != -1):
            edge_label = graph.vs[parent_index]["name"]*nr_unique_labels + graph.vs[index]["name"]
            graph.add_edge(index, parent_index, label=edge_label)
        parent_index = index
        for i, child in enumerate(vertex.childNodes):
            index = self.construct_igraph_subtree(child, index, parent_index, graph, node_label_conversion_table, nr_unique_labels)
        return index

    def construct_igraph_subtree_keep_label(self, vertex, index, parent_index, graph, node_label_conversion_table, nr_unique_labels, parent=None):
        # Map the vertex name to an integer, if it does not exist yet -> add it
        if vertex.type not in node_label_conversion_table:
            node_label_conversion_table.append(vertex.type)
        new_label = vertex.type

        graph.add_vertex(name=new_label)
        index += 1
        if (parent_index != -1):
            # edge_label = graph.vs[parent_index]["name"]*nr_unique_labels + graph.vs[index]["name"]
            # edge_label = "{} - {}".format(parent.type, vertex.type)
            graph.add_edge(index, parent_index)
        parent_index = index
        for i, child in enumerate(vertex.childNodes):
            index = self.construct_igraph_subtree_keep_label(child, index, parent_index, graph, node_label_conversion_table, nr_unique_labels, vertex)
        return index

    def construct_igraph_subtree_connected_siblings(self, vertex, index, parent_index, graph, node_label_conversion_table, nr_unique_labels):
        # Map the vertex name to an integer, if it does not exist yet -> add it
        if vertex.type not in node_label_conversion_table:
            node_label_conversion_table.append(vertex.type)
        new_label = node_label_conversion_table.index(vertex.type)

        graph.add_vertex(name=new_label)
        index += 1
        if (parent_index != -1):
            edge_label = graph.vs[parent_index]["name"] * nr_unique_labels + graph.vs[index]["name"]
            graph.add_edge(index, parent_index, label=edge_label)
        parent_index = index
        child_indeses = []
        for i, child in enumerate(vertex.childNodes):
            index = self.construct_igraph_subtree_connected_siblings(child, index, parent_index, graph, node_label_conversion_table, nr_unique_labels)
            child_indeses.append(index)

        for i in range(len(child_indeses) - 1):
            edge_label = graph.vs[child_indeses[i]]["name"] * nr_unique_labels + graph.vs[child_indeses[i + 1]]["name"]
            graph.add_edge(child_indeses[i], child_indeses[i + 1], label=edge_label)

        return index


    def calculate_WL_subtree_kernel(self, igraph_list):
        K_wl = gk.CalculateWLKernel(igraph_list, par=50)
        print(K_wl.shape)
        print(K_wl)
        plt.imshow(K_wl, cmap='gist_ncar', interpolation='none')
        plt.show()
        return K_wl

    def calculate_kernel_matrices(self, igraph_list):
        kernel_matrices = []
        kernel_matrices.append(gk.CalculateEdgeHistKernel(igraph_list))
        kernel_matrices.append(gk.CalculateVertexHistKernel(igraph_list))
        kernel_matrices.append(gk.CalculateVertexVertexEdgeHistKernel(igraph_list))
        kernel_matrices.append(gk.CalculateVertexVertexEdgeHistKernel(igraph_list))
        kernel_matrices.append(gk.CalculateVertexHistGaussKernel(igraph_list))
        kernel_matrices.append(gk.CalculateEdgeHistGaussKernel(igraph_list))
        kernel_matrices.append(gk.CalculateVertexEdgeHistGaussKernel(igraph_list))
        #kernel_matrices.append(gk.CalculateGeometricRandomWalkKernel(igraph_list))
        #kernel_matrices.append(gk.CalculateExponentialRandomWalkKernel(igraph_list))
        #kernel_matrices.append(gk.CalculateKStepRandomWalkKernel(igraph_list))
        #kernel_matrices.append(gk.CalculateShortestPathKernel(igraph_list))
        kernel_matrices.append(gk.CalculateWLKernel(igraph_list))
        #kernel_matrices.append(gk.CalculateGraphletKernel(igraph_list))
        #kernel_matrices.append(gk.CalculateConnectedGraphletKernel(igraph_list))
        return kernel_matrices

    def get_kernel_function_list(self):
        kernels = []
        kernels.append(gk.CalculateEdgeHistKernel)
        kernels.append(gk.CalculateVertexHistKernel)
        kernels.append(gk.CalculateVertexVertexEdgeHistKernel)
        kernels.append(gk.CalculateVertexVertexEdgeHistKernel)
        kernels.append(gk.CalculateVertexHistGaussKernel)
        kernels.append(gk.CalculateEdgeHistGaussKernel)
        kernels.append(gk.CalculateVertexEdgeHistGaussKernel)
        # kernel_matrices.append(gk.CalculateGeometricRandomWalkKernel(igraph_list))
        # kernel_matrices.append(gk.CalculateExponentialRandomWalkKernel(igraph_list))
        # kernel_matrices.append(gk.CalculateKStepRandomWalkKernel(igraph_list))
        # kernel_matrices.append(gk.CalculateShortestPathKernel(igraph_list))
        kernels.append(gk.CalculateWLKernel)
        kernels.append(gk.CalculateGraphletKernel)
        kernels.append(gk.CalculateConnectedGraphletKernel)
        return kernels
