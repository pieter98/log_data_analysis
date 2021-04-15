NODE_LIST = []

with open('ast_node_encoding_upgrade/nodes.txt','r') as filehandle:
    for line in filehandle:
        currentPlace = line[:-1]
        NODE_LIST.append(currentPlace)

NODE_MAP = {x: i for (i, x) in enumerate(NODE_LIST)}
