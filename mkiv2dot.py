import argparse, json, sys
import util_common, util_graph, util_mkiv
import networkx as nx



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='.')
    parser.add_argument('--mkiv-example', required=True, type=str, choices=util_mkiv.EXAMPLES, help='MKIV example name, from: ' + ','.join(util_mkiv.EXAMPLES) + '.')
    parser.add_argument('--select', type=int, nargs='+', help='Include selected rules by index, rather than including all.')
    parser.add_argument('--outfile', type=str, help='Output file.')
    args = parser.parse_args()

    mkiv_setup = util_mkiv.MKIVSetup()
    mkiv_setup.example = args.mkiv_example
    mkiv_setup.layers = 0

    mkiv_info = util_mkiv.get_example_info(mkiv_setup)

    grs = util_graph.Graphs()

    if mkiv_info.directed:
        grs.gtype = util_graph.GTYPE_DGRAPH
    else:
        grs.gtype = util_graph.GTYPE_UGRAPH

    def _wild(_s):
        return _s if _s is not None else '\u2610'

    for ii, (nodes, edges) in enumerate(mkiv_info.rep_rules):
        if args.select is not None and ii not in args.select:
            continue

        if mkiv_info.directed:
            gr = nx.DiGraph()
        else:
            gr = nx.Graph()

        for node, (static_node_label, dynamic_node_label0, dynamic_node_label1) in enumerate(nodes):
            gr.add_node(node)
            if dynamic_node_label0 == dynamic_node_label1:
                gr.nodes[node][util_graph.GATTR_LABEL] = _wild(static_node_label) + ':' + _wild(dynamic_node_label0)
            else:
                gr.nodes[node][util_graph.GATTR_LABEL] = _wild(static_node_label) + ':' + _wild(dynamic_node_label0) + '\u2192' + dynamic_node_label1

        for fra, til, static_edge_label, dynamic_edge_label0, dynamic_edge_label1 in edges:
            gr.add_edge(fra, til)
            if dynamic_edge_label0 == dynamic_edge_label1:
                gr.edges[(fra, til)][util_graph.GATTR_LABEL] = _wild(static_edge_label) + ':' + _wild(dynamic_edge_label0)
            else:
                gr.edges[(fra, til)][util_graph.GATTR_LABEL] = _wild(static_edge_label) + ':' + _wild(dynamic_edge_label0) + '\u2192' + dynamic_edge_label1

        grs.graphs.append(gr)

    write_fn = lambda _out: util_graph.write_graph_dot(grs, True, True, 1.0, _out)

    if args.outfile is None:
        write_fn(sys.stdout)
    else:
        with util_common.openz(args.outfile, 'wt') as outfile:
            write_fn(outfile)
