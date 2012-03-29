from __future__ import unicode_literals
import codecs
import pygraphviz
import atexit

GRAPH_FILE = "graph.dot"
NODE_TYPES = {
        "add": ( 
                    ('a','b'), 
                    ('a+b')
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

for node, degree in graph.in_degree_iter(graph.nodes()):
    if degree == 0:
        ends.append(node)

outputs = filter(lambda x: x.attr['type']=='output', ends)
num_outputs = len(outputs)

if num_outputs > 1:
    exit("More than one output.")

if num_outputs == 0:
    exit("No output.")

output = outputs[0]
output.attr.update(color='red')
print output
