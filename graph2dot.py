import argparse, itertools, json, random, sys, time
import util_common, util_graph, util_mkiv
import networkx as nx



if __name__ == '__main__':
    util_common.timer_start()

    parser = argparse.ArgumentParser(description='Convert a graph file to a dot file.')
    parser.add_argument('--outfile', type=str, help='Output file.')
    parser.add_argument('--graphfile', required=True, nargs='+', type=str, help='Input graph file(s).')
    parser.add_argument('--grid', action='store_true', help='Layout as grid.')
    parser.add_argument('--no-dot-etc', action='store_true', help='Don\t append extra attributes to dot output.')
    parser.add_argument('--scale', type=float, help='Amount to scale node size.', default=1.0)
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument('--soko', action='store_true', help='Style as soko.')
    group.add_argument('--lightsout', action='store_true', help='Style as lightsout.')
    group.add_argument('--codemaster', action='store_true', help='Style as codemaster.')
    args = parser.parse_args()

    grs = util_graph.read_graphs(args.graphfile)

    if args.grid:
        util_graph.layout_grid(grs.graphs[0])

    if args.soko:
        write_fn = lambda _out: util_mkiv.write_graph_dot_soko(grs, _out)
    elif args.lightsout:
        write_fn = lambda _out: util_mkiv.write_graph_dot_lightsout(grs, _out)
    elif args.codemaster:
        write_fn = lambda _out: util_mkiv.write_graph_dot_codemaster(grs, _out)
    else:
        write_fn = lambda _out: util_graph.write_graph_dot(grs, args.no_dot_etc, False, args.scale, _out)

    if args.outfile is None:
        write_fn(sys.stdout)
    else:
        with util_common.openz(args.outfile, 'wt') as outfile:
            write_fn(outfile)
