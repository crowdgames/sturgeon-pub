import sys
import util
import networkx as nx



ATTR_LABEL     = 'label'
ATTR_POSITION  = 'pos'
ATTR_HIGHLIGHT = 'highlight'

GTYPE_UTREE    = 'utree'
GTYPE_DTREE    = 'dtree'
GTYPE_DAG      = 'dag'
GTYPE_UGRAPH   = 'ugraph'
GTYPE_LIST     = [GTYPE_UTREE, GTYPE_DTREE, GTYPE_DAG, GTYPE_UGRAPH]

LABEL_GRID_EAST  = 'e'
LABEL_GRID_SOUTH = 's'

DIR_FRA        = 'fra'
DIR_TIL        = 'til'



class Graphs:
    def __init__(self):
        self.gtype = None
        self.colors = {}
        self.graphs = []

class GraphDesc:
    def __init__(self):
        self.gtype = None
        self.colors = {}

        self.node_labels = {}
        self.edge_labels = {}

        self.node_label_count = {}
        self.node_label_neighbors = {}



def gtype_directed(gtype):
    if gtype in [GTYPE_DTREE, GTYPE_DAG]:
        return True
    elif gtype in [GTYPE_UTREE, GTYPE_UGRAPH]:
        return False
    else:
        util.check(False, 'Unknown gtype ' + str(gtype))

def gtype_tree(gtype):
    if gtype in [GTYPE_UTREE, GTYPE_DTREE]:
        return True
    elif gtype in [GTYPE_DAG, GTYPE_UGRAPH]:
        return False
    else:
        util.check(False, 'Unknown gtype ' + str(gtype))

def check_graph(gr, gtype):
    util.check(len(gr.nodes) > 0, 'no nodes')

    if gtype_directed(gtype):
        util.check(nx.is_weakly_connected(gr), 'not connected')
    else:
        util.check(nx.is_connected(gr), 'not connected')

    if gtype_tree(gtype):
        util.check(nx.is_tree(gr), 'not a tree')

    if gtype_directed(gtype):
        util.check(nx.is_directed_acyclic_graph(gr), 'not dag')

def nodes_and_labels(gr):
    return [(node, gr.nodes[node][ATTR_LABEL]) for node in gr.nodes]

def edges_and_labels(gr):
    return [(edge[0], edge[1], gr.edges[edge][ATTR_LABEL]) for edge in gr.edges]

def read_graphs(filenames):
    grs = Graphs()

    grs.gtype = None
    grs.colors = {}
    grs.graphs = []

    colors_warned = {}

    for filename in filenames:
        gr = None
        with open(filename, 'rt') as infile:
            for line in infile:
                if '#' in line:
                    line = line[:line.find('#')]

                line = line.strip()
                if len(line) == 0:
                    continue

                splt = line.split()
                if splt[0] == 't':
                    util.check(len(splt) == 2, 'splt len')
                    util.check(splt[1] in GTYPE_LIST, 'gtype')
                    if grs.gtype == None:
                        grs.gtype = splt[1]
                    else:
                        util.check(splt[1] == grs.gtype, 'gtype mismatch')

                    util.check(gr == None, 'mutliple t')
                    if gtype_directed(grs.gtype):
                        gr = nx.DiGraph()
                    else:
                        gr = nx.Graph()

                elif splt[0] == 'n':
                    util.check(len(splt) in [2, 3], 'splt len')
                    node = splt[1]
                    util.check(not gr.has_node(node), 'no duplicate nodes')
                    gr.add_node(node)
                    if len(splt) == 3:
                        gr.nodes[node][ATTR_LABEL] = splt[2]
                    else:
                        gr.nodes[node][ATTR_LABEL] = ''

                elif splt[0] == 'e':
                    util.check(len(splt) in [3, 4], 'splt len')
                    fra, til = splt[1], splt[2]
                    util.check(fra != til, 'no self edges')
                    util.check(not gr.has_edge(fra, til), 'no duplicate edges')
                    gr.add_edge(fra, til)
                    if len(splt) == 4:
                        gr.edges[(fra, til)][ATTR_LABEL] = splt[3]
                    else:
                        gr.edges[(fra, til)][ATTR_LABEL] = ''

                elif splt[0] == 'c':
                    util.check(len(splt) == 3, 'splt len')
                    label = splt[1]
                    color = splt[2]
                    if label not in grs.colors:
                        grs.colors[label] = color
                    elif grs.colors[label] != color and label not in colors_warned:
                        print('WARNING: multiple colors for same label', label)
                        colors_warned[label] = None

                elif splt[0] == 'p':
                    util.check(len(splt) == 4, 'splt len')
                    node = splt[1]
                    xx = int(splt[2])
                    yy = int(splt[3])
                    gr.nodes[node][ATTR_POSITION] = (xx, yy)

                elif splt[0] == 'h':
                    util.check(len(splt) == 2, 'splt len')
                    node = splt[1]
                    gr.nodes[node][ATTR_HIGHLIGHT] = True

                else:
                    util.check(False, 'line: ' + line)

        if gr != None:
            check_graph(gr, grs.gtype)

            grs.graphs.append(gr)

    util.check(len(grs.graphs) != 0, 'no graphs loaded')

    return grs

def write_graph(grs, out):
    util.check(len(grs.graphs) == 1, 'can only write single graph')
    gr = grs.graphs[0]

    out.write(f't {grs.gtype}\n')
    for label, color in grs.colors.items():
        out.write(f'c {label} {color}\n')
    for node, label in nodes_and_labels(gr):
        if label == '':
            out.write(f'n {node}\n')
        else:
            out.write(f'n {node} {label}\n')
    for fra, til, label in edges_and_labels(gr):
        if label == '':
            out.write(f'e {fra} {til}\n')
        else:
            out.write(f'e {fra} {til} {label}\n')
    for node in gr.nodes:
        if ATTR_POSITION in gr.nodes[node]:
            xx, yy = gr.nodes[node][ATTR_POSITION]
            out.write(f'p {node} {xx} {yy}\n')
    for node in gr.nodes:
        if ATTR_HIGHLIGHT in gr.nodes[node]:
            out.write(f'h {node}\n')

def write_graph_dot(grs, out):
    if gtype_directed(grs.gtype):
        dtype = 'digraph'
        dedge = '->'
    else:
        dtype = 'graph'
        dedge = '--'

    out.write(f'{dtype} G {{\n')
    out.write(f'  node [shape="circle" fontsize="24" width="0.5" height="0.5" fixedsize="true"]\n')
    out.write(f'  edge [fontsize="20"]\n')
    for gg, gr in enumerate(grs.graphs):
        if len(grs.graphs) > 1:
            nodeprefix = f'{gg}-'
        else:
            nodeprefix = ''

        for node, label in nodes_and_labels(gr):
            attrs = ''
            if label == '':
                attrs += f'label=""'
            else:
                attrs += f'label="{label}"'

            if len(label) > 1:
                fontsize = max(6, 24 - 2.5 * (len(label) - 1))
                attrs += f' fontsize="{fontsize}"'

            if label in grs.colors:
                attrs += f' style="filled" fillcolor="#{grs.colors[label]}"'
            else:
                attrs += f' style="filled" fillcolor="#eeeeee"'

            if ATTR_POSITION in gr.nodes[node]:
                xx, yy = gr.nodes[node][ATTR_POSITION]
                attrs += f' pos="{xx},{yy}!"'

            if ATTR_HIGHLIGHT in gr.nodes[node]:
                attrs += f' shape="doublecircle"'

            out.write(f'  "{nodeprefix}{node}" [{attrs}]\n')
        for fra, til, label in edges_and_labels(gr):
            attrs = ''
            if label == '':
                attrs += f'label=""'
            else:
                attrs += f'label="{label}"'

            if len(label) > 1:
                fontsize = max(6, 24 - 2.5 * (len(label) - 1))
                attrs += f' fontsize="{fontsize}"'

            out.write(f'  "{nodeprefix}{fra}" {dedge} "{nodeprefix}{til}" [{attrs}]\n')
    out.write('}\n')

def write_graph_to_file(grs, filename):
    if filename == None:
        write_graph(grs, sys.stdout)
    else:
        with open(filename, 'wt') as outfile:
            if filename.endswith('.dot'):
                write_graph_dot(grs, outfile)
            else:
                write_graph(grs, outfile)

def layout_grid(gr):
    roots = [nn for nn, dd in gr.in_degree() if dd == 0]
    util.check(len(roots) == 1, 'grid does not have 1 root')
    root = roots[0]

    used_pos = {}

    queue = [root]
    gr.nodes[root][ATTR_POSITION] = (0, 0)
    used_pos[(0, 0)] = root

    while len(queue) != 0:
        node = queue[0]
        queue = queue[1:]
        out_edges = gr.out_edges(node)

        pos = gr.nodes[node][ATTR_POSITION]

        for out_edge in out_edges:
            out_node = out_edge[1]
            if gr.edges[out_edge][ATTR_LABEL] == LABEL_GRID_EAST:
                out_pos = (pos[0] + 1, pos[1])
            elif gr.edges[out_edge][ATTR_LABEL] == LABEL_GRID_SOUTH:
                out_pos = (pos[0], pos[1] - 1)
            else:
                util.check(False, 'grid edge label')

            if ATTR_POSITION in gr.nodes[out_node]:
                util.check(gr.nodes[out_node][ATTR_POSITION] == out_pos, 'different positions found')

            else:
                util.check(out_pos not in used_pos, 'duplicate pos')
                gr.nodes[out_node][ATTR_POSITION] = out_pos
                used_pos[out_pos] = out_node

                queue.append(out_node)
