import sys
import util_common
import networkx as nx



GATTR_LABEL      = 'label'
GATTR_POSITION   = 'pos'
GATTR_CENTRAL    = 'central'
GATTR_DELTA      = 'delta'
GATTR_POLAR      = 'polar'
GATTR_CYCLE      = 'cycle'

CATTR_NONE       = '_'
CATTR_LABEL      = 'l'
CATTR_POSITION2  = '2'
CATTR_POSITION3  = '3'
CATTR_CENTRAL    = 'c'
CATTR_DELTA2     = '2'
CATTR_DELTA3     = '3'
CATTR_POLAR      = 'p'
CATTR_CYCLE      = 'y'

GTYPE_UTREE      = 'utree'
GTYPE_DTREE      = 'dtree'
GTYPE_DAG        = 'dag'
GTYPE_UGRAPH     = 'ugraph'
GTYPE_LIST       = [GTYPE_UTREE, GTYPE_DTREE, GTYPE_DAG, GTYPE_UGRAPH]

LABEL_GRID_EAST  = 'e'
LABEL_GRID_SOUTH = 's'

DIR_FRA          = 'fra'
DIR_TIL          = 'til'



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
        self.edge_labels_etc = {}

        self.node_label_count = {}
        self.node_label_subgraphs = {}



def gtype_directed(gtype):
    if gtype in [GTYPE_DTREE, GTYPE_DAG]:
        return True
    elif gtype in [GTYPE_UTREE, GTYPE_UGRAPH]:
        return False
    else:
        util_common.check(False, 'Unknown gtype ' + str(gtype))

def gtype_tree(gtype):
    if gtype in [GTYPE_UTREE, GTYPE_DTREE]:
        return True
    elif gtype in [GTYPE_DAG, GTYPE_UGRAPH]:
        return False
    else:
        util_common.check(False, 'Unknown gtype ' + str(gtype))

def check_graph(gr, gtype):
    util_common.check(len(gr.nodes) > 0, 'no nodes')

    if gtype_directed(gtype):
        util_common.check(nx.is_weakly_connected(gr), 'not connected')
    else:
        util_common.check(nx.is_connected(gr), 'not connected')

    if gtype_tree(gtype):
        util_common.check(nx.is_tree(gr), 'not a tree')

    if gtype_directed(gtype):
        util_common.check(nx.is_directed_acyclic_graph(gr), 'not dag')

def graph_node_cattrs(gr):
    node_cattrs = None

    for node in gr.nodes:
        this_node_cattrs = {}

        if gr.nodes[node][GATTR_LABEL] != '':
            this_node_cattrs[CATTR_LABEL] = None
        if GATTR_POSITION in gr.nodes[node]:
            if len(gr.nodes[node][GATTR_POSITION]) == 2:
                this_node_cattrs[CATTR_POSITION2] = None
            elif len(gr.nodes[node][GATTR_POSITION]) == 3:
                this_node_cattrs[CATTR_POSITION3] = None
        if GATTR_CENTRAL in gr.nodes[node]:
            this_node_cattrs[CATTR_CENTRAL] = None

        util_common.check(node_cattrs is None or node_cattrs == this_node_cattrs, 'node_cattrs mismatch')
        node_cattrs = this_node_cattrs

    return ''.join(node_cattrs.keys())

def graph_edge_cattrs(gr):
    edge_cattrs = None

    for edge in gr.edges:
        this_edge_cattrs = {}

        if gr.edges[edge][GATTR_LABEL] != '':
            this_edge_cattrs[CATTR_LABEL] = None
        if GATTR_DELTA in gr.edges[edge]:
            if len(gr.edges[edge][GATTR_DELTA]) == 2:
                this_edge_cattrs[CATTR_DELTA2] = None
            elif len(gr.edges[edge][GATTR_DELTA]) == 3:
                this_edge_cattrs[CATTR_DELTA3] = None
        if GATTR_POLAR in gr.edges[edge]:
            this_edge_cattrs[CATTR_POLAR] = None
        if GATTR_CYCLE in gr.edges[edge]:
            this_edge_cattrs[CATTR_CYCLE] = None

        util_common.check(edge_cattrs is None or edge_cattrs == this_edge_cattrs, 'edge_cattrs mismatch')
        edge_cattrs = this_edge_cattrs

    return ''.join(edge_cattrs.keys())

def nodes_and_label_pos_central(gr):
    return [(node,
             gr.nodes[node][GATTR_LABEL],
             gr.nodes[node][GATTR_POSITION] if GATTR_POSITION in gr.nodes[node] else None,
             gr.nodes[node][GATTR_CENTRAL] if GATTR_CENTRAL in gr.nodes[node] else None)
            for node in gr.nodes]

def edges_and_label_delta_polar_cycle(gr):
    return [(edge[0], edge[1],
             gr.edges[edge][GATTR_LABEL],
             gr.edges[edge][GATTR_DELTA] if GATTR_DELTA in gr.edges[edge] else None,
             gr.edges[edge][GATTR_POLAR] if GATTR_POLAR in gr.edges[edge] else None,
             gr.edges[edge][GATTR_CYCLE] if GATTR_CYCLE in gr.edges[edge] else None)
            for edge in gr.edges]

def read_graphs(filenames):
    grs = Graphs()

    grs.gtype = None
    grs.colors = {}
    grs.graphs = []

    colors_warned = {}

    node_cattrs = None
    edge_cattrs = None

    for filename in filenames:
        gr = None
        with util_common.openz(filename, 'rt') as infile:
            for line in infile:
                if '#' in line:
                    line = line[:line.find('#')]

                line = line.strip()
                if len(line) == 0:
                    continue

                splt = line.split()
                key = splt[0]
                splt = splt[1:]

                if key == 't':
                    util_common.check(len(splt) == 3, 'splt len')
                    util_common.check(splt[0] in GTYPE_LIST, 'gtype')
                    if grs.gtype is None:
                        grs.gtype = splt[0]
                    else:
                        util_common.check(grs.gtype == splt[0], 'gtype mismatch')

                    t_node_cattrs = splt[1] if splt[1] != CATTR_NONE else ''
                    if node_cattrs is None:
                        node_cattrs = t_node_cattrs
                    else:
                        util_common.check(node_cattrs == t_node_cattrs, 'node mismatch')

                    t_edge_cattrs = splt[2] if splt[2] != CATTR_NONE else ''
                    if edge_cattrs is None:
                        edge_cattrs = t_edge_cattrs
                    else:
                        util_common.check(edge_cattrs == t_edge_cattrs, 'node mismatch')

                    util_common.check(gr is None, 'mutliple t')
                    if gtype_directed(grs.gtype):
                        gr = nx.DiGraph()
                    else:
                        gr = nx.Graph()

                elif key == 'n':
                    util_common.check(len(splt) >= 1, 'splt len')
                    node = splt[0]
                    splt = splt[1:]
                    util_common.check(not gr.has_node(node), f'no duplicate nodes {filename} {node}')
                    gr.add_node(node)
                    gr.nodes[node][GATTR_LABEL] = ''
                    for cattr in node_cattrs:
                        if cattr == CATTR_LABEL:
                            util_common.check(len(splt) >= 1, 'splt len')
                            gr.nodes[node][GATTR_LABEL] = splt[0]
                            splt = splt[1:]
                        elif cattr == CATTR_POSITION2:
                            util_common.check(len(splt) >= 2, 'splt len')
                            pos = (float(splt[0]), float(splt[1]))
                            gr.nodes[node][GATTR_POSITION] = pos
                            splt = splt[2:]
                        elif cattr == CATTR_POSITION3:
                            util_common.check(len(splt) >= 3, 'splt len')
                            pos = (float(splt[0]), float(splt[1]), float(splt[2]))
                            gr.nodes[node][GATTR_POSITION] = pos
                            splt = splt[3:]
                        elif cattr == CATTR_CENTRAL:
                            util_common.check(len(splt) >= 1, 'splt len')
                            gr.nodes[node][GATTR_CENTRAL] = (splt[0] == 'T')
                            splt = splt[1:]
                        else:
                            util_common.check(False, 'unrecognized')
                    util_common.check(len(splt) == 0, 'unused')

                elif key == 'e':
                    util_common.check(len(splt) >= 2, 'splt len')
                    fra, til = splt[0], splt[1]
                    splt = splt[2:]
                    util_common.check(fra != til, 'no self edges')
                    util_common.check(not gr.has_edge(fra, til), f'no duplicate edges {filename} {fra} {til}')
                    if not gtype_directed(grs.gtype):
                        util_common.check(not gr.has_edge(til, fra), f'no duplicate undirected edges {filename} {fra} {til}')
                    gr.add_edge(fra, til)
                    gr.edges[(fra, til)][GATTR_LABEL] = ''
                    for cattr in edge_cattrs:
                        if cattr == CATTR_LABEL:
                            util_common.check(len(splt) >= 1, 'splt len')
                            gr.edges[(fra, til)][GATTR_LABEL] = splt[0]
                            splt = splt[1:]
                        elif cattr == CATTR_DELTA2:
                            util_common.check(len(splt) >= 2, 'splt len')
                            gr.edges[(fra, til)][GATTR_DELTA] = (float(splt[0]), float(splt[1]))
                            splt = splt[2:]
                        elif cattr == CATTR_DELTA3:
                            util_common.check(len(splt) >= 3, 'splt len')
                            gr.edges[(fra, til)][GATTR_DELTA] = (float(splt[0]), float(splt[1]), float(splt[2]))
                            splt = splt[3:]
                        elif cattr == CATTR_POLAR:
                            util_common.check(len(splt) >= 3, 'splt len')
                            gr.edges[(fra, til)][GATTR_POLAR] = (float(splt[0]), float(splt[1]), splt[2] == 'T')
                            splt = splt[3:]
                        elif cattr == CATTR_CYCLE:
                            util_common.check(len(splt) >= 1, 'splt len')
                            gr.edges[(fra, til)][GATTR_CYCLE] = splt[0]
                            splt = splt[1:]
                        else:
                            util_common.check(False, 'unrecognized')
                    util_common.check(len(splt) == 0, 'unused')

                elif key == 'c':
                    util_common.check(len(splt) == 2, 'splt len')
                    label = splt[0]
                    color = splt[1]
                    if label not in grs.colors:
                        grs.colors[label] = color
                    elif grs.colors[label] != color and label not in colors_warned:
                        print('WARNING: multiple colors for same label', label)
                        colors_warned[label] = None

                else:
                    util_common.check(False, 'line: ' + line)

        if gr is not None:
            check_graph(gr, grs.gtype)

            grs.graphs.append(gr)

    util_common.check(len(grs.graphs) != 0, 'no graphs loaded')

    return grs

def write_graph(grs, out):
    util_common.check(len(grs.graphs) == 1, 'can only write single graph')
    gr = grs.graphs[0]

    node_cattrs = graph_node_cattrs(gr)
    edge_cattrs = graph_edge_cattrs(gr)

    write_node_cattrs = CATTR_NONE if node_cattrs == '' else node_cattrs
    write_edge_cattrs = CATTR_NONE if edge_cattrs == '' else edge_cattrs

    out.write(f't {grs.gtype} {write_node_cattrs} {write_edge_cattrs}\n')
    for label, color in grs.colors.items():
        out.write(f'c {label} {color}\n')
    for node in gr.nodes:
        line = f'n {node}'
        cattrs = gr.nodes[node]
        for cattr in node_cattrs:
            if cattr == CATTR_LABEL:
                line += f' {cattrs[GATTR_LABEL]}'
            elif cattr == CATTR_POSITION2:
                line += f' {cattrs[GATTR_POSITION][0]} {cattrs[GATTR_POSITION][1]}'
            elif cattr == CATTR_POSITION3:
                line += f' {cattrs[GATTR_POSITION][0]} {cattrs[GATTR_POSITION][1]} {cattrs[GATTR_POSITION][2]}'
            elif cattr == CATTR_CENTRAL:
                line += f' {"T" if cattrs[GATTR_CENTRAL] else "F"}'
        out.write(f'{line}\n')
    for fra, til in gr.edges:
        line = f'e {fra} {til}'
        cattrs = gr.edges[(fra, til)]
        for cattr in edge_cattrs:
            if cattr == CATTR_LABEL:
                line += f' {cattrs[GATTR_LABEL]}'
            elif cattr == CATTR_DELTA2:
                line += f' {cattrs[GATTR_DELTA][0]} {cattrs[GATTR_DELTA][1]}'
            elif cattr == CATTR_DELTA3:
                line += f' {cattrs[GATTR_DELTA][0]} {cattrs[GATTR_DELTA][1]} {cattrs[GATTR_DELTA][2]}'
            elif cattr == CATTR_POLAR:
                line += f' {cattrs[GATTR_POLAR][0]} {cattrs[GATTR_POLAR][1]} {"T" if cattrs[GATTR_POLAR][2] else "F"}'
            elif cattr == CATTR_CYCLE:
                line += f' {cattrs[GATTR_CYCLE]}'
        out.write(f'{line}\n')

def write_graph_dot(grs, no_etc, out):
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

        for node, label, pos, central in nodes_and_label_pos_central(gr):
            attrs = ''

            if label is None:
                attrs += f'label=""'
                attrs += f'style="invis"'

            else:
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

            if pos is not None:
                pos_str = ','.join([str(ee) for ee in pos])
                attrs += f' pos="{pos_str}!"'

            if central is not None:
                if central:
                    attrs += f' shape="doublecircle"'

            out.write(f'  "{nodeprefix}{node}" [{attrs}]\n')

        for fra, til, label, delta, polar, cycle in edges_and_label_delta_polar_cycle(gr):
            attrs = ''
            dot_label = ''

            if label != '':
                fontsize = max(6, 24 - 2.5 * (len(label) - 1))
                dot_label += f'<FONT POINT-SIZE="{fontsize}">{label}</FONT>'

            if not no_etc:
                if delta is not None:
                    delta_str = ','.join([str(ee) for ee in delta])
                    attrs += f' delta="{delta_str}"'
                    dot_label += f'<BR/><FONT POINT-SIZE="10">delta:{delta_str}</FONT>'

                if polar is not None:
                    polar_str = f'{polar[0]},{polar[1]},{"T" if polar[2] else "F"}'
                    attrs += f' polar="{polar_str}"'
                    dot_label += f'<BR/><FONT POINT-SIZE="10">polar:{polar_str}</FONT>'

                if cycle is not None:
                    cycle_str = f'{cycle}'
                    attrs += f' cycle="{cycle_str}"'
                    dot_label += f'<BR/><FONT POINT-SIZE="10">cycle:{cycle_str}</FONT>'

            attrs += f'label=<{dot_label}>'

            out.write(f'  "{nodeprefix}{fra}" {dedge} "{nodeprefix}{til}" [{attrs}]\n')
    out.write('}\n')

def write_graph_to_file(grs, filename):
    if filename is None:
        write_graph(grs, sys.stdout)
    else:
        with util_common.openz(filename, 'wt') as outfile:
            if util_common.fileistype(filename, '.dot'):
                write_graph_dot(grs, False, outfile)
            else:
                write_graph(grs, outfile)

def get_root_node(gr):
    util_common.check(gr.is_directed(), 'graph not directed')
    roots = [nn for nn, dd in gr.in_degree() if dd == 0]
    util_common.check(len(roots) == 1, 'graph does not have 1 root')
    return roots[0]

def layout_grid(gr):
    root = get_root_node(gr)

    used_pos = {}

    queue = [root]
    gr.nodes[root][GATTR_POSITION] = (0, 0)
    used_pos[(0, 0)] = root

    while len(queue) != 0:
        node = queue[0]
        queue = queue[1:]
        out_edges = gr.out_edges(node)

        pos = gr.nodes[node][GATTR_POSITION]

        for out_edge in out_edges:
            out_node = out_edge[1]
            if gr.edges[out_edge][GATTR_LABEL] == LABEL_GRID_EAST:
                out_pos = (pos[0] + 1, pos[1])
            elif gr.edges[out_edge][GATTR_LABEL] == LABEL_GRID_SOUTH:
                out_pos = (pos[0], pos[1] - 1)
            else:
                util_common.check(False, 'grid edge label')

            if GATTR_POSITION in gr.nodes[out_node]:
                util_common.check(gr.nodes[out_node][GATTR_POSITION] == out_pos, 'different positions found')

            else:
                util_common.check(out_pos not in used_pos, 'duplicate pos')
                gr.nodes[out_node][GATTR_POSITION] = out_pos
                used_pos[out_pos] = out_node

                queue.append(out_node)
