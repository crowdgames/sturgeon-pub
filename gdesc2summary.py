import argparse, itertools, json, pickle, random, sys, time
import util, util_graph
import networkx as nx



def gdesc2summary(grd):
    grs = util_graph.Graphs()
    grs.gtype = grd.gtype
    grs.colors = grd.colors
    grs.graphs = []
    result = grs

    for label in grd.node_labels:
        for nbrs in grd.node_label_neighbors[label]:
            gid = len(grs.graphs)

            if util_graph.gtype_directed(grd.gtype):
                gr = nx.DiGraph()
            else:
                gr = nx.Graph()

            central_node = f'{gid}:*'

            gr.add_node(central_node)
            gr.nodes[central_node][util_graph.ATTR_LABEL] = label
            gr.nodes[central_node][util_graph.ATTR_HIGHLIGHT] = True

            for ni, (nbr_node_label, nbr_edge_label, nbr_edge_dir) in enumerate(nbrs):
                nbr_node = f'{gid}:{ni}'

                if nbr_edge_dir == util_graph.DIR_TIL or nbr_edge_dir is None:
                    edge = (central_node, nbr_node)
                elif nbr_edge_dir == util_graph.DIR_FRA:
                    edge = (nbr_node, central_node)
                else:
                    util.check(False, 'nbr_edge_dir')

                gr.add_node(nbr_node)
                gr.nodes[nbr_node][util_graph.ATTR_LABEL] = nbr_node_label

                gr.add_edge(edge[0], edge[1])
                gr.edges[edge][util_graph.ATTR_LABEL] = nbr_edge_label

            grs.graphs.append(gr)

    return grs



if __name__ == '__main__':
    util.timer_start()

    parser = argparse.ArgumentParser(description='Summarize graph description.')
    parser.add_argument('--outfile', type=str, help='Output file.')
    parser.add_argument('--gdescfile', required=True, type=str, help='Input graph description file.')
    args = parser.parse_args()

    with util.openz(args.gdescfile, 'rb') as f:
        grd = pickle.load(f)

    ogrs = gdesc2summary(grd)
    print(f'found {len(grd.node_labels)} node labels')
    print(f'found {len(grd.edge_labels)} edge labels')
    print(f'found {len(ogrs.graphs)} neighborhoods')

    if args.outfile is None:
        for gr in ogrs.graphs:
            ogr = util_graph.GraphDesc()
            ogr.gtype = ogrs.gtype
            ogr.colors = ogrs.colors
            ogr.graphs = [gr]
            print()
            util_graph.write_graph(ogr, sys.stdout)

    else:
        util_graph.write_graph_to_file(ogrs, args.outfile)
