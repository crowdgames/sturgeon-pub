import argparse, itertools, json, random, sys, time
import gutil, util
import networkx as nx



if __name__ == '__main__':
    util.timer_start()

    parser = argparse.ArgumentParser(description='Convert a dot file to a graph file.')
    parser.add_argument('--outfile', type=str, help='Output file.')
    parser.add_argument('--graphfile', required=True, nargs='+', type=str, help='Input graph file(s).')
    parser.add_argument('--grid', action='store_true', help='Layout as grid.')
    args = parser.parse_args()

    grs = gutil.read_graphs(args.graphfile)

    if args.grid:
        gutil.layout_grid(grs.graphs[0])

    if args.outfile == None:
        gutil.write_graph_dot(grs, sys.stdout)
    else:
        with open(args.outfile, 'wt') as outfile:
            gutil.write_graph_dot(grs, outfile)
