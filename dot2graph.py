import argparse, itertools, json, random, sys, time
import gutil, util
import networkx as nx

MULTILABEL = ';'



if __name__ == '__main__':
    util.timer_start()

    parser = argparse.ArgumentParser(description='Convert a dot file to a graph file.')
    parser.add_argument('--outfile', type=str, help='Output file.')
    parser.add_argument('--dotfile', required=True, type=str, help='Input dot file.')
    parser.add_argument('--root', type=str, help='Root node label; produces dag, otherwise produces ugraph.')
    args = parser.parse_args()

    dot = nx.DiGraph(nx.nx_pydot.read_dot(args.dotfile))

    for node in dot.nodes:
        dot.nodes[node][gutil.ATTR_LABEL] = dot.nodes[node][gutil.ATTR_LABEL].strip('"')
    for edge in dot.edges:
        dot.edges[edge][gutil.ATTR_LABEL] = dot.edges[edge][gutil.ATTR_LABEL].strip('"')

    grs = gutil.Graphs()
    grs.colors = {}

    if args.root:
        grs.gtype = gutil.GTYPE_DAG
        root_node = None
        for node in dot.nodes:
            if dot.nodes[node][gutil.ATTR_LABEL] == args.root:
                util.check(root_node == None, 'multiple root nodes')
                root_node = node
        util.check(root_node != None, 'no root node')

        gr = nx.bfs_tree(dot, root_node)

        for edge in dot.edges:
            if not nx.has_path(gr, edge[1], edge[0]):
                gr.add_edge(edge[0], edge[1])
    else:
        grs.gtype = gutil.GTYPE_UGRAPH

        gr = dot.to_undirected()

    def orderlabels(lbls):
        lbls = lbls.split(',')
        lbls = [lbl.strip() for lbl in lbls]
        lbls = [lbl for lbl in lbls if lbl != '']
        lbls = sorted(lbls)
        lbls = MULTILABEL.join(lbls)
        return lbls

    gr_orig = dot

    for node in gr.nodes:
        gr.nodes[node][gutil.ATTR_LABEL] = orderlabels(gr_orig.nodes[node][gutil.ATTR_LABEL])

    for ea, eb in gr.edges:
        lbla = gr_orig.edges[(ea, eb)][gutil.ATTR_LABEL] if (ea, eb) in gr_orig.edges else ''
        lblb = gr_orig.edges[(eb, ea)][gutil.ATTR_LABEL] if (eb, ea) in gr_orig.edges else ''

        if lbla == lblb or lblb == '':
            lbl = lbla
        elif lbla == '':
            lbl = lblb
        else:
            lbl = lbla + MULTILABEL + lblb
        gr.edges[(ea, eb)][gutil.ATTR_LABEL] = orderlabels(lbl)

    grs.graphs = [gr]

    gutil.write_graph_to_file(grs, args.outfile)
