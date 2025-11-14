import argparse, json, sys
import util_common, util_graph, util_mkiv
import networkx as nx



if __name__ == '__main__':
    util_common.timer_start()

    parser = argparse.ArgumentParser(description='.')
    parser.add_argument('--outfile', type=str, help='Output file.')
    parser.add_argument('--mkiv-example', required=True, type=str, choices=util_mkiv.EXAMPLES, help='MKIV example name, from: ' + ','.join(util_mkiv.EXAMPLES) + '.')
    parser.add_argument('--select', type=int, nargs='+', help='Include selected rules by index, rather than including all.')
    parser.add_argument('--central-color', action='store_true', help='Use central attribute colors.')
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

    def _rule_label_helper(_s):
        return _s if _s is not None else util_graph.LABEL_RULE_WILD

    def _rule_label(_sta, _dyn0, _dyn1):
        _label = util_mkiv.make_label(_rule_label_helper(_sta), _rule_label_helper(_dyn0))
        if _dyn0 != _dyn1:
            _label += util_graph.LABEL_RULE_ARROW + _rule_label_helper(_dyn1)
        return _label

    def _edge_hint_label_helper(_h):
        if _h is None:
            return ''
        elif _h <= 0:
            return '@' + str(-_h)
        else:
            return '+' + str(_h)

    def _edge_hint_label(_lo, _hi):
        if _lo is None and _hi is None:
            return ''
        elif _lo == _hi:
            return '<BR/><I>' + _edge_hint_label_helper(_lo) + '</I>'
        else:
            return '<BR/><I>' + _edge_hint_label_helper(_lo) + '\u2026' + _edge_hint_label_helper(_hi) + '</I>'

    def _layer_hint_label_helper(_h):
        if _h is None:
            return ''
        else:
            return str(_h)

    def _layer_hint_label(_lo, _hi):
        if _lo is None and _hi is None:
            return ''
        elif _lo == _hi:
            return '<I>' + _layer_hint_label_helper(_lo) + '</I>'
        else:
            return '<I>' + _layer_hint_label_helper(_lo) + '\u2026' + _layer_hint_label_helper(_hi) + '</I>'

    for rule_index, (layer_hint_lo, layer_hint_hi, chain, nodes, edges) in enumerate(mkiv_info.rep_rules):
        if args.select is not None and rule_index not in args.select:
            continue

        if mkiv_info.directed:
            gr = nx.DiGraph()
        else:
            gr = nx.Graph()

        rule_label = _layer_hint_label(layer_hint_lo, layer_hint_hi)
        if rule_label != '':
            rule_label += '<BR/>'
        rule_label += '<B>' + 'Rule ' + str(rule_index) + '</B>'
        gr.graph[util_graph.GATTR_LABEL] = rule_label

        for node, (static_node_label, dynamic_node_label0, dynamic_node_label1) in enumerate(nodes):
            gr.add_node(node)
            gr.nodes[node][util_graph.GATTR_LABEL] = _rule_label(static_node_label, dynamic_node_label0, dynamic_node_label1)
            if args.central_color:
                if dynamic_node_label0 is not None or dynamic_node_label1 is not None:
                    gr.nodes[node][util_graph.GATTR_CENTRAL] = rule_index

        for fra, til, ind_hint_lo, ind_hint_hi, static_edge_label, dynamic_edge_label0, dynamic_edge_label1 in edges:
            gr.add_edge(fra, til)
            label = _rule_label(static_edge_label, dynamic_edge_label0, dynamic_edge_label1)
            label += _edge_hint_label(ind_hint_lo, ind_hint_hi)
            gr.edges[(fra, til)][util_graph.GATTR_LABEL] = label
            if args.central_color:
                if dynamic_edge_label0 is not None or dynamic_edge_label1 is not None:
                    gr.edges[(fra, til)][util_graph.GATTR_CENTRAL] = rule_index

        grs.graphs = [gr]

        write_fn = lambda _out: util_graph.write_graph_dot(grs, True, True, args.central_color, 1.0, _out)

        if args.outfile is None:
            write_fn(sys.stdout)
        else:
            with util_common.openz(args.outfile + ('_%04d.dot' % rule_index), 'wt') as outfile:
                write_fn(outfile)
