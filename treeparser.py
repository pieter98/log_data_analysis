import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element
import sys
#from graph_tool.all import *
from zss import simple_distance, Node
import json
#from tree_kernels import tree, tree_kernels




class BlocklyTreeParser:
    def __init__(self):
        self.treeRoot = None

    """
    Construct a syntax tree from a blockly xml file
    @param xmlString The xml string for a single blockly workspace
    @returns the root element of the syntax tree (always labeled "workspace")
    """
    def constructCodeTree(self, xmlString):
        root = ET.fromstring(xmlString)
        astRoot = MyTreeNode("workspace", None)
        for child in root:
            childType = child.get('type')
            if childType == 'setup_loop_structure' or \
               childType == 'procedures_defnoreturn' or \
               childType == 'setup_loop_structure_arduino' or \
               childType == 'procedures_defreturn':
                newNode = MyTreeNode(childType, astRoot)
                astTree = self.getSubTree(child, newNode)
                astRoot.addChild(astTree)
        #print(astRoot)
        return astRoot

    """
    Construct a code tree from code.org json ast file
    @param jsonString the json ast representation
    @returns thr root element of the syntax tree
    """
    def constructCodeTreeFromJson(self, jsonString):
        deserialized = json.load(jsonString)
        root_node = MyTreeNode(deserialized.get(type), None)
        return self.constructCodeTreeFromJsonRecursive(deserialized, None)

    def constructCodeTreeFromJsonRecursive(self, deserialized, parent):
        new_node = MyTreeNode(deserialized["type"], parent)
        if deserialized.get("children"):
            for child in deserialized.get("children"):
                childTree = self.constructCodeTreeFromJsonRecursive(child, new_node)
                if childTree != None:
                    new_node.addChild(childTree)
        return new_node


    """
    Recursively construct a Google Blockly xml tree for the given ast
    @param the current node of the ast
    @param the next element for the block that will be constructed
    @returns the Blockly xml subtree
    """
    def astToBlocklyXml(self, astRoot, parentNode=None):
        if astRoot.getLabel() == "program":
            node = Element('xml')
            node.attrib["xmlns"] = "http://www.w3.org/1999/xhtml"
            next = Element("next")
            block = Element('block')
            block.attrib["type"] = "program"
            if len(astRoot.childNodes) > 0:
                if astRoot.childNodes[0].getLabel() == "statementList":
                    self.astToBlocklyXml(astRoot.childNodes[0], next)
                else:
                    next.append(self.astToBlocklyXml(astRoot.childNodes[0]))
                block.append(next)
            node.append(block)
        elif astRoot.getLabel() == "statementList":
            if parentNode == None:
                parentNode = Element("statement")
            prevNode = None
            for child in reversed(astRoot.childNodes):
                newNode = self.astToBlocklyXml(child)
                if prevNode != None:
                    nextElement = Element("next")
                    nextElement.append(prevNode)
                    newNode.append(nextElement)
                prevNode = newNode
            if parentNode != None:
                parentNode.append(prevNode)
            return parentNode
        elif astRoot.getLabel() == "maze_forever":
            node = Element("block")
            node.attrib["type"] = "infinite_loop"
            node.append(self.astToBlocklyXml(astRoot.childNodes[0]))
        elif astRoot.getLabel() == "DO":
            node = Element("statement")
            node.attrib["name"] = "DO0"
            if astRoot.childNodes[0].getLabel() == "statementList":
                return self.astToBlocklyXml(astRoot.childNodes[0], node)
            node.append(self.astToBlocklyXml(astRoot.childNodes[0]))
        elif astRoot.getLabel() == "ELSE":
            node = Element("statement")
            node.attrib["name"] = "ELSE"
            if astRoot.childNodes[0].getLabel() == "statementList":
                return self.astToBlocklyXml(astRoot.childNodes[0], node)
            node.append(self.astToBlocklyXml(astRoot.childNodes[0]))
        elif astRoot.getLabel() == "maze_ifElse":
            node = Element("block")
            node.attrib["type"] = "controls_if"
            mutatorNode = Element("mutation")
            mutatorNode.attrib["else"] = "1"
            node.append(mutatorNode)
            for child in astRoot.childNodes:
                node.append(self.astToBlocklyXml(child))
        elif astRoot.getLabel() == "isPathLeft":
            node = Element("value")
            node.attrib["name"] = "IF0"
            terminalBlock = Element("block")
            terminalBlock.attrib["type"] = "left"
            node.append(terminalBlock)
        elif astRoot.getLabel() == "isPathRight":
            node = Element("value")
            node.attrib["name"] = "IF0"
            terminalBlock = Element("block")
            terminalBlock.attrib["type"] = "right"
            node.append(terminalBlock)
        elif astRoot.getLabel() == "isPathForward":
            node = Element("value")
            node.attrib["name"] = "IF0"
            terminalBlock = Element("block")
            terminalBlock.attrib["type"] = "forward"
            node.append(terminalBlock)
        elif astRoot.getLabel() ==  "maze_turn":
            for child in astRoot.childNodes:
                if child.getLabel() == "turnLeft":
                    node = Element("block")
                    node.attrib["type"] = "goLeft"
                elif child.getLabel() == "turnRight":
                    node = Element("block")
                    node.attrib["type"] = "goRight"
        elif astRoot.getLabel() == "maze_moveForward":
            node = Element("block")
            node.attrib["type"] = "goForward"
        return node

    """
    Recursively converts the xmlElement "element" to the treeNode "treeNode"
    @param element the element which has to be converted
    @param treeNode the treeNode which is tranformed to match "element"
    @returns the fully assembled treeNode
    """
    def getSubTree(self, element, treeNode):
        newNode = None
        for child in element:
            if child.tag == "{http://www.w3.org/1999/xhtml}statement":
                # Insert wrapper node for statement
                statementNode = MyTreeNode(child.get('name'), treeNode)
                statementContentBlock = child[0]
                newNode = MyTreeNode(statementContentBlock.get("type"), statementNode)
                newNodeWithChildren = self.getSubTree(statementContentBlock, newNode)
                statementNode.addChild(newNodeWithChildren)
                # Move the next nodes previously saved lower in the hierarchy after the currently inserted node
                for node in statementNode.nextNodes:
                    statementNode.childNodes.append(node)
                statementNode.nextNodes = []
                treeNode.addChild(statementNode)
            elif child.tag == "{http://www.w3.org/1999/xhtml}value":
                # Insert wrapper node for value
                valueNode = MyTreeNode(child.get('name'), treeNode)
                valueContentBlock = child[0]
                newNode = MyTreeNode(valueContentBlock.get("type"), valueNode)
                valueNode.addChild(self.getSubTree(valueContentBlock, newNode))
                treeNode.addChild(valueNode)
            elif child.tag == "{http://www.w3.org/1999/xhtml}field":
                fieldValue = child.text
                newNode = ValueTreeNode(child.get('name'), treeNode, fieldValue)
                treeNode.addChild(newNode)
            elif child.tag == "{http://www.w3.org/1999/xhtml}next":
                # print("next")
                nextBlock = child[0]
                newNode = MyTreeNode(nextBlock.get('type'), treeNode.getParent())
                treeNode.getParent().prependNextNode(self.getSubTree(nextBlock, newNode))
        return treeNode

    """
    Recusively translates the syntax graph to a graph for displaying with graph display
    @param node Node in source graph to translate
    @param graph display graph to add the nodes to
    @param parentVertex parent vertex of node
    @param vProp property map which saves the vertex label for each node in the display graph
    """
    def constructGraphForDisplay(self, node, graph, parentVertex, vProp):
        for child in node.childNodes:
            childVertex = graph.add_vertex()
            vProp[childVertex] = child.getLabel()
            edge = graph.add_edge(parentVertex, childVertex)
            self.constructGraphForDisplay(child, graph, childVertex, vProp)


    """
    Recusively translates the syntax tree to a tree to be used with kernel clustering
    @param currentRoot The root of the current subtree being translated.
    @returns The root of the translated tree
    """
    def constructTreeForKernelClustering(self, currentRoot):
        newRoot = tree.TreeNode(currentRoot.getLabel(), [])
        for child in currentRoot.childNodes:
            newRoot.appendChild(self.constructTreeForKernelClustering(child))
        return  newRoot

    """
    Returns the kernelTree for a given ast root element
    @param rootOfAst root node of the AST
    @returns The kernel tree
    """
    def getKernelTree(self, rootOfAst):
        return tree.Tree(self.constructTreeForKernelClustering(rootOfAst))

    """
    Draws the graph given a syntax tree (root) node
    """
    """def drawGraph(self, treeRootNode):
        # Create a graph for displaying with python_graph_tool.
        g = Graph()
        rootVertex = g.add_vertex()
        vProp = g.new_vertex_property("string")
        vProp[rootVertex] = treeRootNode.type
        self.constructGraphForDisplay(treeRootNode, g, rootVertex, vProp)
        graph_draw(g, vertex_text=vProp)"""

    """
    Constructs the zss tree of the specified tree
    @param treeNode the root node of the tree of which a zss tree has to be constructed
    """
    def constructZssTree(self, treeNode):
        newNode = Node(treeNode.getLabel())
        for childNode in treeNode.childNodes:
            newNode.addkid(self.constructZssTree(childNode))
        return newNode



class MyTreeNode:
    def __init__(self, type, parent):
        self.type = type
        self.parent = parent
        self.childNodes = []
        self.nextNodes = []
        self.parent

    def __float__(self):
        return 0.0


    def addChild(self, childNode):
        self.childNodes.append(childNode)

    def getChildWithType(self, type):
        for child in self.childNodes:
            if child.type == type:
                return child

    def prependNextNode(self, childNode):
        self.nextNodes.insert(0, childNode)

    def setType(self, type):
        self.type = type

    def getParent(self):
        return self.parent

    def __str__(self):
        returnString = self.type
        for child in self.childNodes:
            returnString = returnString + " " + str(child)
        return returnString

    def constructGraph(self, graph):
        return None

    def getLabel(self):
        return self.type

    def getDistance(self, node):
        return 1 if self.getLabel() == node.getLabel() else 0

    @staticmethod
    def get_children(node):
        return node.childNodes

    @staticmethod
    def get_label(node):
        return node.getLabel()

    """ @brief Used by the zss algorithm to compare (sub)trees
        This method returns the distance between two node labels, it will be crucial to choose the right value for
        this distance to get a valid comparison between code statements. For example, the distance between for and while
        should be less than the distance between for and if
        @param nodeALabel The label of the first node
        @param nodeBLabel The label of the second node
    """
    @staticmethod
    def get_pairwise_node_distance(nodeALabel, nodeBLabel):
        return 0 if nodeALabel == nodeBLabel else 1

    def getSubtreeLabelSet(self):
        labelset = set()
        labelset.add(self.getLabel())
        for child in self.childNodes:
            for label in child.getSubtreeLabelSet():
                labelset.add(label)
        return labelset

    def getLabelCount(self, label):
        childrenLabelCount = 0
        for child in self.childNodes:
            childrenLabelCount += child.getLabelCount(label)
        if self.getLabel() == label:
            return 1 + childrenLabelCount
        else:
            return childrenLabelCount



class ValueTreeNode(MyTreeNode):
    def __init__(self, type, parent, value):
        MyTreeNode.__init__(self, type, parent)
        self.value = value

    def getValue(self):
        return self.value

    def getLabel(self):
        return self.value


"""if __name__ == "__main__":
    parser = BlocklyTreeParser()
    f = open(sys.argv[1], 'r')
    xmlString = f.read()
    parser.constructCodeTree(xmlString)"""
