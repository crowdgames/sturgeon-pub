import argparse, itertools, json, random, sys, time
import util, util_graph
import networkx as nx



if __name__ == '__main__':
    util.timer_start()

    parser = argparse.ArgumentParser(description='Convert a dot file to a graph file.')
    parser.add_argument('--outfile', type=str, help='Output file.')
    parser.add_argument('--graphfile', required=True, nargs='+', type=str, help='Input graph file(s).')
    parser.add_argument('--grid', action='store_true', help='Layout as grid.')
    args = parser.parse_args()

    grs = util_graph.read_graphs(args.graphfile)

    if args.grid:
        util_graph.layout_grid(grs.graphs[0])

    if args.outfile is None:
        util_graph.write_graph_dot(grs, sys.stdout)
    else:
        with util.openz(args.outfile, 'wt') as outfile:
            util_graph.write_graph_dot(grs, outfile)
