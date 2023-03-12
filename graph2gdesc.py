import argparse, itertools, json, pickle, random, sys, time
import gutil, util
import networkx as nx



def graph_nbrs(gr, gtype, node):
    nbrs = []
    for fra, til, label in gutil.edges_and_labels(gr):
        nbr, dir_tag = None, None

        if gutil.gtype_directed(gtype):
            if fra == node:
                nbr, dir_tag = til, gutil.DIR_TIL
            elif til == node:
                nbr, dir_tag = fra, gutil.DIR_FRA
        else:
            if fra == node:
                nbr = til
            elif til == node:
                nbr = fra

        if nbr:
            nbrs.append((nbr, label, dir_tag))

    return nbrs

def graph2gdesc(grs, edgesonly):
    util.timer_section('extract')

    grd = gutil.GraphDesc()

    grd.gtype = grs.gtype
    grd.colors = grs.colors

    grd.node_labels = {}
    grd.edge_labels = {}

    total_nodes = 0

    for gr in grs.graphs:
        total_nodes += len(gr.nodes)

        for node, label in gutil.nodes_and_labels(gr):
            if label not in grd.node_labels:
                grd.node_labels[label] = None
                grd.node_label_count[label] = 0
                grd.node_label_neighbors[label] = []

        for fra, til, label in gutil.edges_and_labels(gr):
            if label not in grd.edge_labels:
                grd.edge_labels[label] = None

        for node, label in gutil.nodes_and_labels(gr):
            grd.node_label_count[label] += 1

            nbr_labels = []

            nbrs = graph_nbrs(gr, grd.gtype, node)
            for nbr_node, nbr_edge_label, nbr_edge_dir in nbrs:
                if edgesonly:
                    nbr_node_label = None
                else:
                    nbr_node_label = gr.nodes[nbr_node][gutil.ATTR_LABEL]
                nbr_labels.append((nbr_node_label, nbr_edge_label, nbr_edge_dir))

            nbr_labels = tuple(sorted(nbr_labels))

            if nbr_labels not in grd.node_label_neighbors[label]:
                grd.node_label_neighbors[label].append(nbr_labels)

    for label in grd.node_labels:
        grd.node_label_count[label] = grd.node_label_count[label] / total_nodes
        grd.node_label_neighbors[label] = sorted(grd.node_label_neighbors[label])

    return grd



if __name__ == '__main__':
    util.timer_start()

    parser = argparse.ArgumentParser(description='Extract description from example graph.')
    parser.add_argument('--outfile', required=True, type=str, help='Output file.')
    parser.add_argument('--graphfile', required=True, nargs='+', type=str, help='Input graph file(s).')
    parser.add_argument('--edgesonly', action='store_true', help='Make description from only edges.')
    args = parser.parse_args()

    grs = gutil.read_graphs(args.graphfile)

    grd = graph2gdesc(grs, args.edgesonly)
    with open(args.outfile, 'wb') as f:
        pickle.dump(grd, f, pickle.HIGHEST_PROTOCOL)
