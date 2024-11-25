import argparse, itertools, json, pickle, random, sys, time
import util_common, util_graph
import networkx as nx



def gdesc2summary(grd):
    grs = util_graph.Graphs()
    grs.gtype = grd.gtype
    grs.colors = grd.colors
    grs.graphs = []
    result = grs

    for label in grd.node_labels:
        for central_subnode, subnodes, subedges in grd.node_label_subgraphs[label]:
            gid = len(grs.graphs)

            if util_graph.gtype_directed(grd.gtype):
                gr = nx.DiGraph()
            else:
                gr = nx.Graph()

            for subnode, label in subnodes.items():
                node = f'{gid}:{subnode}'
                gr.add_node(node)
                gr.nodes[node][util_graph.GATTR_LABEL] = label
                if subnode == central_subnode:
                    gr.nodes[node][util_graph.GATTR_CENTRAL] = True
                else:
                    gr.nodes[node][util_graph.GATTR_CENTRAL] = False

            for subedge, (label, delta, polar, cycle) in subedges.items():
                fra = f'{gid}:{subedge[0]}'
                til = f'{gid}:{subedge[1]}'
                gr.add_edge(fra, til)
                gr.edges[(fra, til)][util_graph.GATTR_LABEL] = label
                if delta is not None:
                    gr.edges[(fra, til)][util_graph.GATTR_DELTA] = delta
                if polar is not None:
                    gr.edges[(fra, til)][util_graph.GATTR_POLAR] = polar
                if cycle is not None:
                    gr.edges[(fra, til)][util_graph.GATTR_CYCLE] = cycle

            grs.graphs.append(gr)

    return grs



if __name__ == '__main__':
    util_common.timer_start()

    parser = argparse.ArgumentParser(description='Summarize graph description.')
    parser.add_argument('--outfile', type=str, help='Output file.')
    parser.add_argument('--gdescfile', required=True, type=str, help='Input graph description file.')
    args = parser.parse_args()

    with util_common.openz(args.gdescfile, 'rb') as f:
        grd = pickle.load(f)

    ogrs = gdesc2summary(grd)
    print(f'found {len(grd.node_labels)} node labels')
    print(f'found {len(grd.edge_labels_etc)} edge labels/etc')
    print(f'found {len(ogrs.graphs)} neighborhoods')

    if args.outfile is None:
        for gr in ogrs.graphs:
            ogr = util_graph.GraphDesc()
            ogr.gtype = ogrs.gtype
            ogr.colors = ogrs.colors
            ogr.graphs = [gr]
            print()
            util_graph.write_graph_gr(ogr, sys.stdout)

    else:
        util_graph.write_graph_to_file(ogrs, args.outfile)
