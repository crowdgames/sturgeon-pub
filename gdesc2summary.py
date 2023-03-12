import argparse, itertools, json, pickle, random, sys, time
import gutil, util
import networkx as nx



def gdesc2summary(grd):
    grs = gutil.Graphs()
    grs.gtype = grd.gtype
    grs.colors = grd.colors
    grs.graphs = []
    result = grs

    for label in grd.node_labels:
        for nbrs in grd.node_label_neighbors[label]:
            gid = len(grs.graphs)

            if gutil.gtype_directed(grd.gtype):
                gr = nx.DiGraph()
            else:
                gr = nx.Graph()

            central_node = f'{gid}:*'

            gr.add_node(central_node)
            gr.nodes[central_node][gutil.ATTR_LABEL] = label
            gr.nodes[central_node][gutil.ATTR_HIGHLIGHT] = True

            for ni, (nbr_node_label, nbr_edge_label, nbr_edge_dir) in enumerate(nbrs):
                nbr_node = f'{gid}:{ni}'

                if nbr_edge_dir == gutil.DIR_TIL or nbr_edge_dir == None:
                    edge = (central_node, nbr_node)
                elif nbr_edge_dir == gutil.DIR_FRA:
                    edge = (nbr_node, central_node)
                else:
                    util.check(False, 'nbr_edge_dir')

                gr.add_node(nbr_node)
                gr.nodes[nbr_node][gutil.ATTR_LABEL] = nbr_node_label

                gr.add_edge(edge[0], edge[1])
                gr.edges[edge][gutil.ATTR_LABEL] = nbr_edge_label

            grs.graphs.append(gr)

    return grs



if __name__ == '__main__':
    util.timer_start()

    parser = argparse.ArgumentParser(description='Summarize graph description.')
    parser.add_argument('--outfile', type=str, help='Output file.')
    parser.add_argument('--gdescfile', required=True, type=str, help='Input graph description file.')
    args = parser.parse_args()

    with open(args.gdescfile, 'rb') as f:
        grd = pickle.load(f)

    ogrs = gdesc2summary(grd)
    print(f'found {len(grd.node_labels)} node labels')
    print(f'found {len(grd.edge_labels)} edge labels')
    print(f'found {len(ogrs.graphs)} neighborhoods')

    if args.outfile == None:
        for gr in ogrs.graphs:
            ogr = gutil.GraphDesc()
            ogr.gtype = ogrs.gtype
            ogr.colors = ogrs.colors
            ogr.graphs = [gr]
            print()
            gutil.write_graph(ogr, sys.stdout)

    else:
        gutil.write_graph_to_file(ogrs, args.outfile)
