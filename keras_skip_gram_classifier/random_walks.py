import sys, os
from stellargraph.data import BiasedRandomWalk
from stellargraph import StellarGraph
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import matplotlib.pyplot as plt

import igraph
import networkx
from constants import *
from tqdm import tqdm

# conn = DatabaseConnection()

# xml_trees = conn.get_generated_zig_zag_scenario_xml_blocks()
# print(xml_trees[0])
            
# parser = BlocklyTreeParser()
# analyzer = CodeTreeAnalyzer(None, parser)

# ast_trees = analyzer.convert_xml_trees_to_ast_trees(xml_trees)
# print(ast_trees[0])

# igraph_trees = analyzer.convert_ast_trees_to_igraph_ast_trees_keep_label(ast_trees)
# graph = igraph_trees[200]
# print("\n")

def get_walks_from_igraphs(igraphs):
    walks = []
    for graph in tqdm(igraphs, desc="RANDOM WALKS"):
        A = graph.get_edgelist()
        G = networkx.Graph(A)
        stellar_graph = StellarGraph.from_networkx(G)
        rw = BiasedRandomWalk(stellar_graph)
        walks_num = rw.run(
            nodes=list(stellar_graph.nodes()),
            length=WALK_LENGTH,
            n=AMOUNT_PER_NODE,
            p=P_VALUE,
            q=Q_VALUE         
        )
        for walk_num in walks_num:
            walks.append([graph.vs[num]["name"] for num in walk_num])
    
    return walks
