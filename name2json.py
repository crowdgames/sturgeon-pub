import argparse, json
import util_common, util_mkiv, util_reach



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='.')
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument('--reach-move', type=str, help='Reachability move rules, from: ' + ','.join(util_reach.RMOVE_LIST) + '.')
    group.add_argument('--mkiv-example', type=str, choices=util_mkiv.EXAMPLES, help='MKIV example name, from: ' + ','.join(util_mkiv.EXAMPLES) + '.')
    parser.add_argument('--outfile', type=str, help='Output file.')
    args = parser.parse_args()

    out = None

    if args.reach_move is not None:
        move_template = util_reach.get_move_template(args.reach_move)

        out = []
        for dest, need_open_path, need_open_aux, need_closed_path, need_closed_aux in move_template:
            out.append({
                'dest': dest,
                'need_open_path': need_open_path,
                'need_open_aux': need_open_aux,
                'need_closed_path': need_closed_path,
                'need_closed_aux': need_closed_aux
            })

    elif args.mkiv_example is not None:
        mkiv_setup = util_mkiv.MKIVSetup()
        mkiv_setup.example = args.mkiv_example
        mkiv_setup.layers = 0

        mkiv_info = util_mkiv.get_example_info(mkiv_setup)

        out = {}
        out['directed'] = mkiv_info.directed

        rules = []
        for nodes, edges in mkiv_info.rep_rules:
            rule_nodes = []
            for static_node_label, dynamic_node_label0, dynamic_node_label1 in nodes:
                rule_nodes.append({'st':static_node_label, 'dy-lhs': dynamic_node_label0, 'dy-rhs': dynamic_node_label1})

            rule_edges = []
            for fra, til, static_edge_label, dynamic_edge_label0, dynamic_edge_label1 in edges:
                rule_edges.append({'src':fra, 'dst': til, 'st':static_edge_label, 'dy-lhs': dynamic_edge_label0, 'dy-rhs': dynamic_edge_label1})

            rules.append({
                'nodes': rule_nodes,
                'edges': rule_edges
            })
        out['rules'] = rules

    if args.outfile is None:
        json.dump(out, sys.stdout)
        sys.stdout.write('\n')
    else:
        with open(args.outfile, 'wt') as outfile:
            json.dump(out, outfile)
            outfile.write('\n')
