from __future__ import unicode_literals
import codecs
import pygraphviz
import atexit
import warnings
import logging

logging.basicConfig()
logger = logging.getLogger("graphgen")

GRAPH_FILE = "graph.dot"
NODE_TYPES = {
        "add": ( 
                    ('a','b'), 
                    ('a+b',)
               ),
        "output": (
                ('diffuse', 'alpha', 'clip'),
                ()
            )
}

graph = pygraphviz.AGraph(GRAPH_FILE).copy()


def save_graph_file():
    graph.draw(path='out.png', format='png', prog='dot')
    print "Graph saved in out.png"

atexit.register(save_graph_file)

ends = []

for node, degree in graph.out_degree_iter(graph.nodes()):
    if degree == 0:
        ends.append(node)

outputs = filter(lambda x: x.attr['kind']=='output', ends)
num_outputs = len(outputs)

if num_outputs > 1:
    exit("More than one output.")

if num_outputs == 0:
    exit("No output.")

output = outputs[0]

def color_preds(node, color):
    for pred in graph.predecessors_iter(node):
        color_subbranch(pred, color)
        color_preds(pred, color)

def color_subbranch(node, color):
    color_node(node, color)
    for edge in graph.in_edges_iter([node]):
        edge.attr.update(color=color, fontcolor=color)

def color_node(node, color):
    node.attr.update(color=color, fontcolor=color)

def color_node_bg(node, color):
    node.attr.update(style="filled", fillcolor=color, bgcolor=color)

if len(ends) != 1:
    # color orphaned branches

    for end in ends:
        if end is output:
            continue
        color_subbranch(end, 'red')
        color_preds(end, 'red')

    logger.warn("There is/are %d orphaned branch(es). They have been colored red." % (len(ends)-1))

for node in graph.iternodes():
    if 'kind' not in node.attr or node.attr['kind'] not in NODE_TYPES:
        logger.warn("Encountered a node with an unknown type. Gave it a purple background.")
        color_node_bg(node, 'purple')
    else:
        input_kinds = NODE_TYPES[node.attr['kind']][0]
        output_kinds = NODE_TYPES[node.attr['kind']][1]

        input_string = ""
        output_string = ""

        if len(input_kinds) != 0:
            input_string = " { " + " | ".join([("<"+x+"> "+x) for x in input_kinds]) + " } | "
        if len(output_kinds) != 0:
            output_string = " | { " + " | ".join([("<"+x+"> "+x) for x in output_kinds]) + " }"

        node.attr.update(label = ("{" + input_string + " {" + node.attr.get('kind', '<unknown kind>') + "\\n('" + node.name + "')} "+output_string+"}"))
