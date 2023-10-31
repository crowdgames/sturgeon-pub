import argparse, itertools, json, math, pickle, random, sys, time
import util_common, util_graph
import networkx as nx


NRAD_EDGE = 'edge'
NRAD_NODE = 'node'
NRAD_SUB1 = 'sub1'
NRAD_LIST = [NRAD_EDGE, NRAD_NODE, NRAD_SUB1]

def check_node_positions(gr):
    any_node_missing_position = False
    for node in gr.nodes:
        if util_graph.GATTR_POSITION not in gr.nodes[node]:
            any_node_missing_position = True
    util_common.check(not any_node_missing_position, 'node positions')

def rotate_node_positions(gr):
    ret = gr.copy()
    for node in ret.nodes:
        pos = ret.nodes[node][util_graph.GATTR_POSITION]
        ret.nodes[node][util_graph.GATTR_POSITION] = (pos[1], -pos[0])
    return ret

def edge_deltas_from_node_positions(gr):
    for fra, til in gr.edges:
        fra_pos = gr.nodes[fra][util_graph.GATTR_POSITION]
        til_pos = gr.nodes[til][util_graph.GATTR_POSITION]
        delta = tuple([(tt - ff) for ff, tt in zip(fra_pos, til_pos)])
        gr.edges[(fra, til)][util_graph.GATTR_DELTA] = delta

def edge_polars_from_node_positions(gr):
    root = util_graph.get_root_node(gr)

    rdx = 0.0
    rdy = 0.0
    rnum = 0
    fra_pos = gr.nodes[root][util_graph.GATTR_POSITION]
    for til in gr.neighbors(root):
        til_pos = gr.nodes[til][util_graph.GATTR_POSITION]

        dx = til_pos[0] - fra_pos[0]
        dy = til_pos[1] - fra_pos[1]
        mag = math.sqrt(dx ** 2 + dy ** 2)
        util_common.check(mag > 0.01, 'mag')
        rdx += dx / mag
        rdy += dy / mag
        rnum += 1

    rdx /= rnum
    rdy /= rnum
    rmag = math.sqrt(rdx ** 2 + rdy ** 2)
    util_common.check(rmag > 0.01, 'mag')
    rdx /= rmag
    rdy /= rmag

    incoming_vectors = {}
    incoming_vectors[root] = rdx, rdy, 1.0

    primary = {}
    for node in gr.nodes:
        if node == root:
            continue

        primary[node] = sorted(list(gr.predecessors(node)))[0]

        fra_pos = gr.nodes[primary[node]][util_graph.GATTR_POSITION]
        til_pos = gr.nodes[node][util_graph.GATTR_POSITION]

        dx = til_pos[0] - fra_pos[0]
        dy = til_pos[1] - fra_pos[1]
        delta_mag = math.sqrt(dx ** 2 + dy ** 2)

        incoming_vectors[node] = dx, dy, delta_mag

    queue = [root]
    while len(queue) > 0:
        fra = queue[0]
        del queue[0]

        idx, idy, imag = incoming_vectors[fra]

        fra_pos = gr.nodes[fra][util_graph.GATTR_POSITION]

        for til in gr.neighbors(fra):
            til_pos = gr.nodes[til][util_graph.GATTR_POSITION]

            dx = til_pos[0] - fra_pos[0]
            dy = til_pos[1] - fra_pos[1]
            delta_mag = math.sqrt(dx ** 2 + dy ** 2)
            delta_ang = math.copysign(math.acos(max(-1.0, min(1.0, (dx * idx + dy * idy) / (delta_mag * imag)))), dy * idx - dx * idy)
            delta_mag = round(delta_mag, 3)
            delta_ang = round(delta_ang, 3)

            gr.edges[(fra, til)][util_graph.GATTR_POLAR] = (delta_mag, delta_ang, fra == primary[til])

            queue.append(til)

def subgraph_from_nodes(gr, subnodes):
    subgraph = gr.__class__()

    for node, attr in gr.nodes.items():
        if node in subnodes:
            subgraph.add_node(node, **attr)

    for (fra, til), attr in gr.edges.items():
        if fra in subnodes and til in subnodes:
            subgraph.add_edge(fra, til, **attr)

    return subgraph

def local_subgraph(gr, node, nrad):
    util_common.check(nrad in NRAD_LIST, 'nrad')

    subnodes = [node] + list(sorted(nx.all_neighbors(gr, node)))
    subgraph = subgraph_from_nodes(gr, subnodes)

    if nrad in [NRAD_EDGE, NRAD_NODE]:
        to_remove = []
        for fra, til in subgraph.edges:
            if fra != node and til != node:
                to_remove.append((fra, til))
        subgraph.remove_edges_from(to_remove)

    if nrad in [NRAD_EDGE]:
        for snode in subgraph.nodes:
            subgraph.nodes[snode][util_graph.GATTR_LABEL] = None

    for snode in subgraph.nodes:
        subgraph.nodes[snode][util_graph.GATTR_CENTRAL] = (snode == node)

    return subgraph

def graph_desc(gr, node):
    new_ids = {}
    new_ids[node] = 0

    for snode in gr.nodes:
        if snode not in new_ids:
            new_ids[snode] = len(new_ids)

    nodes = {}
    for snode in gr.nodes:
        nodes[new_ids[snode]] = gr.nodes[snode][util_graph.GATTR_LABEL]

    edges = {}
    for fra, til in gr.edges:
        attrs = gr.edges[(fra, til)]
        edges[(new_ids[fra], new_ids[til])] = (attrs[util_graph.GATTR_LABEL],
                                               attrs[util_graph.GATTR_DELTA] if util_graph.GATTR_DELTA in attrs else None,
                                               attrs[util_graph.GATTR_POLAR] if util_graph.GATTR_POLAR in attrs else None,
                                               attrs[util_graph.GATTR_CYCLE] if util_graph.GATTR_CYCLE in attrs else None)

    return (new_ids[node], nodes, edges)

def graph2gdesc(grs, nrad, cycle_label, edge_deltas, edge_polars, rotate):
    util_common.timer_section('extract')

    util_common.check(not edge_deltas or not edge_polars, 'cannot use both edge deltas and polars')
    util_common.check(not rotate or edge_deltas, 'can only use rotate with edge deltas')

    grd = util_graph.GraphDesc()

    grd.gtype = grs.gtype
    grd.colors = grs.colors

    grd.node_labels = {}
    grd.edge_labels_etc = {}

    total_nodes = 0
    distinct_node_label_subgraphs = {}

    if edge_deltas or edge_polars or rotate:
        for gr in grs.graphs:
            check_node_positions(gr)

        if edge_deltas:
            edge_deltas_from_node_positions(gr)

        if edge_polars:
            edge_polars_from_node_positions(gr)

    nm = nx.algorithms.isomorphism.categorical_node_match([util_graph.GATTR_LABEL, util_graph.GATTR_CENTRAL], [None, None])
    em = nx.algorithms.isomorphism.categorical_edge_match([util_graph.GATTR_LABEL, util_graph.GATTR_DELTA, util_graph.GATTR_POLAR, util_graph.GATTR_CYCLE], [None, None, None, None])

    if cycle_label:
        cycles = []
        for gr in grs.graphs:
            ugr = gr.to_undirected(as_view=True)

            cycle_bases = tuple(sorted([tuple(sorted(cycle_basis)) for cycle_basis in nx.cycle_basis(ugr)]))

            for cycle_basis in cycle_bases:
                cycle_subgraph = subgraph_from_nodes(gr, cycle_basis)
                clen = len(cycle_subgraph)

                ci_mapping = None
                for eci, (existing_subgraph, existing_eis) in enumerate(cycles):
                    matcher = nx.algorithms.isomorphism.DiGraphMatcher(cycle_subgraph, existing_subgraph, node_match=nm, edge_match=em)
                    found_mappings = list(matcher.subgraph_isomorphisms_iter())
                    util_common.check(len(found_mappings) <= 1, 'multiple mappings found')
                    if len(found_mappings) != 0:
                        ci_mapping = eci, found_mappings[0]
                        break

                if ci_mapping is None:
                    ci_mapping = len(cycles), {node:node for node in cycle_basis}
                    cycles.append((cycle_subgraph, {edge:ei for ei, edge in enumerate(cycle_subgraph.edges)}))

                ci, mapping = ci_mapping

                existing_subgraph, existing_eis = cycles[ci]
                for edge in cycle_subgraph.edges:
                    ei = existing_eis[(mapping[edge[0]], mapping[edge[1]])]
                    if util_graph.GATTR_CYCLE not in gr.edges[edge]:
                        gr.edges[edge][util_graph.GATTR_CYCLE] = ''
                    else:
                        gr.edges[edge][util_graph.GATTR_CYCLE] += ';'
                    gr.edges[edge][util_graph.GATTR_CYCLE] += f'{ci}-{ei}'

            for edge in gr.edges:
                if util_graph.GATTR_CYCLE not in gr.edges[edge]:
                    gr.edges[edge][util_graph.GATTR_CYCLE] = '_'

        print(f'found {len(cycles)} distinct cycle')

    if rotate:
        all_graphs = []
        for gr in grs.graphs:
            all_graphs.append(gr)

            for rt in range(3):
                gr = rotate_node_positions(gr)
                all_graphs.append(gr)

    else:
        all_graphs = grs.graphs

    for gr in all_graphs:
        total_nodes += len(gr.nodes)

        for node, label, pos, central in util_graph.nodes_and_label_pos_central(gr):
            if label not in grd.node_labels:
                grd.node_labels[label] = None
                grd.node_label_count[label] = 0
                distinct_node_label_subgraphs[label] = []

        for fra, til, label, delta, polar, cycle in util_graph.edges_and_label_delta_polar_cycle(gr):
            if (label, delta, polar, cycle) not in grd.edge_labels_etc:
                grd.edge_labels_etc[(label, delta, polar, cycle)] = None

        for node, label, pos, central in util_graph.nodes_and_label_pos_central(gr):
            grd.node_label_count[label] += 1

            sub = local_subgraph(gr, node, nrad)

            is_distinct = True
            for other_sub, other_node in distinct_node_label_subgraphs[label]:
                if nx.is_isomorphic(sub, other_sub, nm, em):
                    is_distinct = False
                    break

            if is_distinct:
                distinct_node_label_subgraphs[label].append((sub, node))

    for label in grd.node_labels:
        grd.node_label_count[label] = grd.node_label_count[label] / total_nodes
        grd.node_label_subgraphs[label] = [graph_desc(sub, node) for sub, node in distinct_node_label_subgraphs[label]]

    return grd



if __name__ == '__main__':
    util_common.timer_start()

    parser = argparse.ArgumentParser(description='Extract description from example graph.')
    parser.add_argument('--outfile', required=True, type=str, help='Output file.')
    parser.add_argument('--graphfile', required=True, nargs='+', type=str, help='Input graph file(s).')
    parser.add_argument('--nrad', type=str, default=NRAD_NODE, help='Neighbor radius options, from: ' + ','.join(NRAD_LIST) + '.')
    parser.add_argument('--cycle-label', action='store_true', help='Add extra labels to cycle edges.')
    edge_group = parser.add_mutually_exclusive_group(required=False)
    edge_group.add_argument('--edge-delta', action='store_true', help='Compute edge deltas from node positions.')
    edge_group.add_argument('--edge-delta-rotate', action='store_true', help='Compute edge deltas from node positions, and rotate graphs.')
    edge_group.add_argument('--edge-polar', action='store_true', help='Compute edge polars from node positions.')
    args = parser.parse_args()

    grs = util_graph.read_graphs(args.graphfile)

    grd = graph2gdesc(grs, args.nrad, args.cycle_label, args.edge_delta or args.edge_delta_rotate, args.edge_polar, args.edge_delta_rotate)
    with util_common.openz(args.outfile, 'wb') as f:
        pickle.dump(grd, f)
