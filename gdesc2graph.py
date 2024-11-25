import argparse, itertools, json, math, pickle, random, sys, time
import util_common, util_graph, util_mkiv, util_solvers
import networkx as nx



CONNECT_REACH  = 'reach'
CONNECT_LAYER  = 'layer'
CONNECT_LIST   = [CONNECT_REACH, CONNECT_LAYER]

EDGEOPT_TRI         = 'tri'
EDGEOPT_BAND        = 'band'
EDGEOPT_STRIPE      = 'stripe'
EDGEOPT_GRID        = 'grid'
EDGEOPT_RECT        = 'rect'
EDGEOPT_DBAND       = 'dband'
EDGEOPT_CODEMASTER  = 'codemaster'
EDGEOPT_LIST        = [EDGEOPT_TRI, EDGEOPT_BAND, EDGEOPT_STRIPE, EDGEOPT_GRID, EDGEOPT_RECT, EDGEOPT_DBAND, EDGEOPT_CODEMASTER]

def gdesc2graph(s, grd, min_size, max_size, edgeopt, edgeopt_params, label_min, label_max, label_count, forbid_cycle, require_cycle, connect, mkiv_setup, randomize):
    # set up solver vars
    util_common.timer_section('set up')

    if edgeopt in [EDGEOPT_GRID, EDGEOPT_RECT]:
        edge_labels = {}
        for label, delta, polar, cycle in grd.edge_labels_etc:
            edge_labels[label] = None

        if len(edge_labels) != 2:
            util_common.check(False, 'grid edge labels')

        if util_graph.LABEL_GRID_EAST in edge_labels and util_graph.LABEL_GRID_SOUTH in edge_labels:
            east_label = util_graph.LABEL_GRID_EAST
            south_label = util_graph.LABEL_GRID_SOUTH
        elif util_mkiv.make_label(util_graph.LABEL_GRID_EAST, '_') in edge_labels and util_mkiv.make_label(util_graph.LABEL_GRID_SOUTH, '_') in edge_labels:
            east_label = util_mkiv.make_label(util_graph.LABEL_GRID_EAST, '_')
            south_label = util_mkiv.make_label(util_graph.LABEL_GRID_SOUTH, '_')

    if label_min:
        for ll in label_min:
            util_common.check(ll == util_common.DEFAULT_TEXT or ll in grd.node_labels, 'no label_min')
    if label_max:
        for ll in label_max:
            util_common.check(ll == util_common.DEFAULT_TEXT or ll in grd.node_labels, 'no label_max')

    if util_graph.gtype_directed_cyclic(grd.gtype):
        if edgeopt == EDGEOPT_DBAND:
            util_common.check(len(edgeopt_params) == 1, 'edgeopt_params')
        elif edgeopt == EDGEOPT_CODEMASTER:
            util_common.check(len(edgeopt_params) == 2, 'edgeopt_params')
        else:
            util_common.check(False, 'edgeopt cannot be used with this graph type')
    else:
        if edgeopt == EDGEOPT_TRI:
            util_common.check(len(edgeopt_params) == 0, 'edgeopt_params')
        elif edgeopt == EDGEOPT_BAND:
            util_common.check(len(edgeopt_params) == 1, 'edgeopt_params')
        elif edgeopt == EDGEOPT_STRIPE:
            util_common.check(len(edgeopt_params) >= 1, 'edgeopt_params')
        elif edgeopt in [EDGEOPT_GRID, EDGEOPT_RECT]:
            util_common.check(len(edgeopt_params) == 1, 'edgeopt_params')
        else:
            util_common.check(False, 'edgeopt cannot be used with this graph type')

    use_edge_deltas = None
    use_edge_polars = None
    label0, delta0, polar0, cycle0 = next(iter(grd.edge_labels_etc))
    if delta0 is not None or polar0 is not None:
        if not util_graph.gtype_directed(grd.gtype):
            print('WARNING: graph is not directed but edges have deltas/polars, ignoring')
        else:
            for label, delta, polar, cycle in grd.edge_labels_etc:
                util_common.check((delta0 is None) == (delta is None), 'edge delta')
                util_common.check((polar0 is None) == (polar is None), 'edge polar')

            util_common.check(not ((delta0 is not None) and (polar0 is not None)), 'edge delta and polar')

            if delta0 is not None:
                use_edge_deltas = len(delta0)
                util_common.check(use_edge_deltas in [2, 3], 'edge delta dimensions')
                for label, delta, polar, cycle in grd.edge_labels_etc:
                    util_common.check(len(delta) == use_edge_deltas, 'edge delta')

            elif polar0 is not None:
                use_edge_polars = True

    if use_edge_deltas is not None or use_edge_polars is not None:
        util_common.check(use_edge_deltas is None or use_edge_polars is None, 'cannot have both edge deltas and polars')
        util_common.check(s.supports_xforms(), 'has edge deltas but solver does not support transformations')

    # node labels
    node_labels_plus_none = list(grd.node_labels) + [None]

    vars_nodes_by_label = {}
    for ll in node_labels_plus_none:
        vars_nodes_by_label[ll] = []

    node_id_order = list(range(max_size))
    if randomize is not None:
        rng = random.Random(randomize)
        rng.shuffle(node_id_order)

    vars_node_by_id = {}
    for ii in node_id_order:
        vars_node_by_id[ii] = {}
        for ll in node_labels_plus_none:
            vv = s.make_var()
            vars_nodes_by_label[ll].append(vv)
            vars_node_by_id[ii][ll] = vv
        s.cnstr_count(list(vars_node_by_id[ii].values()), True, 1, 1, None)

    MIN_LINF_DIST = 0.6

    if use_edge_deltas is not None or use_edge_polars is not None:
        vars_node_xform = {}
        vars_node_xform_list = []
        vars_node_missing_list = []

        node_id_order_zero_first = [0] + [node for node in node_id_order if node != 0]
        for ii in node_id_order_zero_first:
            vars_node_xform[ii] = s.make_var_xform(use_edge_deltas if use_edge_deltas else 'x2')
            vars_node_xform_list.append(vars_node_xform[ii])
            vars_node_missing_list.append(vars_node_by_id[ii][None])
        s.cnstr_ident_dist_xform(vars_node_missing_list, vars_node_xform_list, MIN_LINF_DIST)

    # edge labels
    def edge_with_label(_edges, _with_label):
        _ret = []
        for _label_etc in _edges:
            if _label_etc != None:
                _label, _delta, _polar, _cycle = _label_etc
                if _label == _with_label:
                    _ret.append(_edges[_label_etc])
        util_common.check(len(_ret) == 1, 'edge labels')
        return _ret[0]

    edge_labels_etc_plus_none = list(grd.edge_labels_etc) + [None]

    vars_edges_by_label_etc = {}
    for ll in edge_labels_etc_plus_none:
        vars_edges_by_label_etc[ll] = []

    PRINT_EDGES = False

    vars_edge_by_id_by_label_etc = {}
    for ii in node_id_order:
        if PRINT_EDGES:
            sys.stdout.write(f'{ii} ->')

        if edgeopt == EDGEOPT_TRI:
            jjs = range(ii + 1, max_size)
        elif edgeopt == EDGEOPT_BAND:
            band_size = edgeopt_params[0]
            jjs = range(ii + 1, min(ii + band_size + 1, max_size))
        elif edgeopt == EDGEOPT_STRIPE:
            jjs = [ii + stripe for stripe in edgeopt_params if ii + stripe < max_size]
        elif edgeopt in [EDGEOPT_GRID, EDGEOPT_RECT]:
            grid_stride = edgeopt_params[0]
            jjs = []
            if (ii + 1) < max_size and (ii + 1) % grid_stride != 0:
                jjs.append(ii + 1)
            if (ii + grid_stride) < max_size:
                jjs.append(ii + grid_stride)
        elif edgeopt == EDGEOPT_DBAND:
            band_size = edgeopt_params[0]
            jjs = list(range(ii + 1, min(ii + band_size + 1, max_size))) + list(range(ii - 1, max(ii - band_size - 1, -1), -1))
        elif edgeopt == EDGEOPT_CODEMASTER:
            map_count = edgeopt_params[0]
            scroll_count = edgeopt_params[1]
            util_common.check(1 + map_count + scroll_count == max_size, 'incorrect number of map and scroll nodes')
            jjs = util_mkiv.get_codemaster_edges(ii, map_count, scroll_count)
        else:
            util_common.check(False, 'edgeopt')

        for jj in jjs:
            util_common.check(0 <= jj and jj < max_size, 'out of bounds edge')

            if PRINT_EDGES:
                sys.stdout.write(f' {jj}')
                if type(jjs) == dict:
                    jj_str = ' '.join(jjs[jj])
                    sys.stdout.write(f'[{jj_str}]')

            ii_jj = (ii, jj)

            vars_edge_by_id_by_label_etc[ii_jj] = {}
            for label_etc in edge_labels_etc_plus_none:
                vv = s.make_var()
                vars_edge_by_id_by_label_etc[ii_jj][label_etc] = vv
                vars_edges_by_label_etc[label_etc].append(vv)
            s.cnstr_count(list(vars_edge_by_id_by_label_etc[ii_jj].values()), True, 1, 1, None)

            if type(jjs) == dict:
                allowed_labels = jjs[jj]
                for label_etc in vars_edge_by_id_by_label_etc[ii_jj]:
                    if label_etc is None:
                        continue
                    label, delta, polar, cycle = label_etc
                    if label not in allowed_labels:
                        s.cnstr_count([vars_edge_by_id_by_label_etc[ii_jj][label_etc]], True, 0, 0, None)

            if edgeopt in [EDGEOPT_GRID, EDGEOPT_RECT]:
                if jj == ii + 1:
                    edge = edge_with_label(vars_edge_by_id_by_label_etc[ii_jj], south_label)
                    s.cnstr_count([vars_edge_by_id_by_label_etc[ii_jj][None], edge], True, 1, 1, None)
                elif jj == ii + grid_stride:
                    edge = edge_with_label(vars_edge_by_id_by_label_etc[ii_jj], east_label)
                    s.cnstr_count([vars_edge_by_id_by_label_etc[ii_jj][None], edge], True, 1, 1, None)

        if PRINT_EDGES:
            sys.stdout.write('\n')
    if PRINT_EDGES:
        sys.exit(-1)

    # cycles
    if forbid_cycle or require_cycle:
        vars_edges_have_cycle = []
        for edge, label_etc_to_edge_var in vars_edge_by_id_by_label_etc.items():
            for label_etc, edge_var in label_etc_to_edge_var.items():
                if label_etc is None:
                    continue

                label, delta, polar, cycle = label_etc
                util_common.check(cycle is not None, 'cycle check but no cycle attr')
                if cycle != '_':
                    vars_edges_have_cycle.append(edge_var)
        util_common.check(len(vars_edges_have_cycle) > 0, 'cycle check but no cycle edges')
        if forbid_cycle:
            s.cnstr_count(vars_edges_have_cycle, True, 0, 0, None)
        if require_cycle:
            s.cnstr_count(vars_edges_have_cycle, True, 1, len(vars_edges_have_cycle), None)

    # edge deltas
    if use_edge_deltas is not None or use_edge_polars is not None:
        for (ii, jj), label_etc_to_edge_var in vars_edge_by_id_by_label_etc.items():
            node_vars_ii = vars_node_xform[ii]
            node_vars_jj = vars_node_xform[jj]

            for label_etc, edge_var in label_etc_to_edge_var.items():
                if label_etc is None:
                    continue

                label, delta, polar, cycle = label_etc
                if use_edge_deltas is not None:
                    util_common.check(delta is not None and len(delta) == use_edge_deltas, 'edge delta')
                    s.cnstr_implies_xform(edge_var, node_vars_ii, node_vars_jj, delta, True)
                elif use_edge_polars is not None:
                    util_common.check(polar is not None, 'edge polar')
                    delta_mag, delta_ang, delta_primary = polar
                    dxform_r = [math.cos(delta_ang), -math.sin(delta_ang), 0, math.sin(delta_ang), math.cos(delta_ang), 0]
                    dxform_t = [1, 0, delta_mag, 0, 1, 0]
                    dxform = [dxform_r[0] * dxform_t[0] + dxform_r[1] * dxform_t[3],
                              dxform_r[0] * dxform_t[1] + dxform_r[1] * dxform_t[4],
                              dxform_r[0] * dxform_t[2] + dxform_r[1] * dxform_t[5] + dxform_r[2],
                              dxform_r[3] * dxform_t[0] + dxform_r[4] * dxform_t[3],
                              dxform_r[3] * dxform_t[1] + dxform_r[4] * dxform_t[4],
                              dxform_r[3] * dxform_t[2] + dxform_r[4] * dxform_t[5] + dxform_r[5]]
                    s.cnstr_implies_xform(edge_var, node_vars_ii, node_vars_jj, dxform, delta_primary)

    # how many nodes can be missing
    s.cnstr_count(vars_nodes_by_label[None], True, 0, max_size - min_size, None)

    # connected
    if connect == CONNECT_REACH:
        vars_node_connect = []
        for ii in range(max_size):
            vars_node_connect.append(s.make_var())

        for ii in range(max_size):
            # all nodes must be either missing or connected
            # missing node not connected - covered by this
            s.cnstr_count([vars_node_by_id[ii][None], vars_node_connect[ii]], True, 1, 1, None)

        # other than first node, no incoming reachable means not reachable
        for jj in range(1, max_size):
            incoming = []
            for ii in range(jj):
                if (ii, jj) in vars_edge_by_id_by_label_etc:
                    incoming.append(s.make_conj([vars_node_connect[ii], vars_edge_by_id_by_label_etc[(ii, jj)][None]], [True, False]))
            s.cnstr_implies_disj(s.make_conj(incoming, False), True, [vars_node_connect[jj]], False, None)

    elif connect == CONNECT_LAYER:
        connect_layers = max_size // 2 + 1

        vars_node_connect = []
        for cc in range(connect_layers):
            layer = {}
            for ii in range(max_size):
                layer[ii] = s.make_var()
            vars_node_connect.append(layer)

        s.cnstr_count(list(vars_node_connect[0].values()), True, 1, 1, None)
        for cc in range(1, connect_layers):
            for ii in range(max_size):
                incoming = []
                for jj in range(max_size):
                    if ii == jj:
                        continue
                    ei, ej = min(ii, jj), max(ii, jj)
                    if (ei, ej) in vars_edge_by_id_by_label_etc:
                        incoming.append(s.make_conj([vars_node_connect[cc - 1][jj], vars_edge_by_id_by_label_etc[(ei, ej)][None]], [True, False]))
                s.cnstr_implies_disj(s.make_conj([vars_node_connect[cc - 1][ii]] + incoming, False), True, [vars_node_connect[cc][ii]], False, None)

        for ii in range(max_size):
            s.cnstr_count([vars_node_connect[connect_layers - 1][ii], vars_node_by_id[ii][None]], True, 1, 1, None)

    else:
        util_common.check(False, 'connect')

    # tree
    if util_graph.gtype_tree(grd.gtype):
        missing_edges = vars_edges_by_label_etc[None]
        missing_nodes = vars_nodes_by_label[None]
        s.cnstr_count(missing_edges + missing_nodes, [False] * len(missing_edges) + [True] * len(missing_nodes), max_size - 1, max_size - 1, None)

    # node label counts
    for ll in grd.node_labels:
        ll_min, ll_max = 0, max_size

        if label_min:
            if ll in label_min:
                ll_min = max(ll_min, label_min[ll])
            elif util_common.DEFAULT_TEXT in label_min:
                ll_min = max(ll_min, label_min[util_common.DEFAULT_TEXT])

        if label_max:
            if ll in label_max:
                ll_max = min(ll_max, label_max[ll])
            elif util_common.DEFAULT_TEXT in label_max:
                ll_max = min(ll_max, label_max[util_common.DEFAULT_TEXT])

        if label_count:
            ll_min = max(ll_min, int(min_size * 0.5 * grd.node_label_count[ll]))
            ll_max = min(ll_max, int(max_size * 1.5 * grd.node_label_count[ll]))

        if (ll_min, ll_max) != (0, max_size):
            s.cnstr_count(vars_nodes_by_label[ll], True, ll_min, ll_max, None)

    # add structure constraints
    if edgeopt in [EDGEOPT_GRID, EDGEOPT_RECT]:
        if edgeopt == EDGEOPT_RECT:
            # first column set
            for ii in range(grid_stride):
                s.cnstr_count([vars_node_by_id[ii][None]], False, 1, 1, None)

            # any in column set makes whole column set
            for ii in range(0, max_size, grid_stride):
                for jj in range(ii, min(ii + grid_stride, max_size)):
                    for kk in range(ii, min(ii + grid_stride, max_size)):
                        s.cnstr_implies_disj(vars_node_by_id[jj][None], False, [vars_node_by_id[kk][None]], False, None)

        # make squares
        grid_stride = edgeopt_params[0]
        for ii in node_id_order:
            # 0 a 1
            # b   c
            # 2 d 3
            ea = (ii, ii + grid_stride)
            eb = (ii, ii + 1)
            ec = (ii + grid_stride, ii + 1 + grid_stride)
            ed = (ii + 1, ii + 1 + grid_stride)

            if ea not in vars_edge_by_id_by_label_etc or eb not in vars_edge_by_id_by_label_etc or ec not in vars_edge_by_id_by_label_etc or ed not in vars_edge_by_id_by_label_etc:
                continue

            eav = edge_with_label(vars_edge_by_id_by_label_etc[ea], east_label)
            ebv = edge_with_label(vars_edge_by_id_by_label_etc[eb], south_label)
            ecv = edge_with_label(vars_edge_by_id_by_label_etc[ec], south_label)
            edv = edge_with_label(vars_edge_by_id_by_label_etc[ed], east_label)

            s.cnstr_implies_disj(s.make_conj([ebv, ecv, edv], [True, True, True]), True, [eav], True, None)
            s.cnstr_implies_disj(s.make_conj([eav, ecv, edv], [True, True, True]), True, [ebv], True, None)
            s.cnstr_implies_disj(s.make_conj([eav, ebv, edv], [True, True, True]), True, [ecv], True, None)
            s.cnstr_implies_disj(s.make_conj([eav, ebv, ecv], [True, True, True]), True, [edv], True, None)

    # add neighbor constraints
    util_common.timer_section('add neighbor constraints')

    for ii in node_id_order:
        nbr_edges = {}
        possible_nbr_nodes = {}
        for jj in node_id_order:
            if ii == jj:
                continue
            if (ii, jj) in vars_edge_by_id_by_label_etc:
                nbr_edges[(ii, jj)] = None
                possible_nbr_nodes[jj] = None
            if (jj, ii) in vars_edge_by_id_by_label_etc:
                nbr_edges[(jj, ii)] = None
                possible_nbr_nodes[jj] = None

        # missing node has no edges; using conj seems to work better than multiple individual implies
        s.cnstr_implies_disj(vars_node_by_id[ii][None], True, [s.make_conj([vars_edge_by_id_by_label_etc[edge][None] for edge in nbr_edges], [True] * len(nbr_edges))], True, None)

        # apply from description
        for label in grd.node_labels:
            patts = []
            for central_subnode, subnodes, subedges in grd.node_label_subgraphs[label]:
                node_inds_set = itertools.permutations(possible_nbr_nodes, len(subnodes) - 1)
                other_subnodes = [subnode for subnode in subnodes if subnode != central_subnode]
                util_common.check(len(other_subnodes) == len(subnodes) - 1, 'sizes')

                for node_inds in node_inds_set:
                    subnode_id_mapping = {}
                    subnode_id_mapping[central_subnode] = ii
                    for node_ind, subnode in zip(node_inds, other_subnodes):
                        subnode_id_mapping[subnode] = node_ind

                    any_missing_edges = False

                    node_labels = {}
                    for node, node_label in subnodes.items():
                        if node_label is not None:
                            node_labels[subnode_id_mapping[node]] = node_label

                    edge_labels = {}
                    for (fra, til), edge_label_etc in subedges.items():
                        fra = subnode_id_mapping[fra]
                        til = subnode_id_mapping[til]

                        if util_graph.gtype_directed(grd.gtype):
                            if util_graph.gtype_directed_cyclic(grd.gtype):
                                util_common.check(use_edge_deltas is None, 'directed cyclic edge delta')
                                util_common.check(use_edge_polars is None, 'directed cyclic edge polar')
                            else:
                                if fra >= til:
                                    any_missing_edges = True
                                    break
                            ei, ej = fra, til
                        else:
                            util_common.check(use_edge_deltas is None, 'undirected edge delta') # TODO edge flip vars ?
                            util_common.check(use_edge_polars is None, 'undirected edge polar')
                            ei, ej = min(fra, til), max(fra, til)

                        if (ei, ej) not in vars_edge_by_id_by_label_etc:
                            any_missing_edges = True
                            break

                        edge_labels[(ei, ej)] = edge_label_etc

                    if any_missing_edges:
                        continue

                    nodev = []
                    for node_ind, node_label in node_labels.items():
                        nodev.append(vars_node_by_id[node_ind][node_label])

                    edgev = []
                    for (ei, ej), edge_label_etc in edge_labels.items():
                        edgev.append(vars_edge_by_id_by_label_etc[(ei, ej)][edge_label_etc])
                    for ei, ej in nbr_edges:
                        if (ei, ej) not in edge_labels:
                            edgev.append(vars_edge_by_id_by_label_etc[(ei, ej)][None])

                    patts.append(s.make_conj(nodev + edgev, [True] * (len(nodev) + len(edgev))))

            if len(patts) == 0:
                s.cnstr_count([vars_node_by_id[ii][label]], True, 0, 0, None)
            else:
                s.cnstr_implies_disj(vars_node_by_id[ii][label], True, patts, True, None)

    if mkiv_setup is not None:
        util_common.timer_section('add mkiv')
        mkiv_info = util_mkiv.get_example_info(mkiv_setup)
        mkiv_tuple = util_mkiv.add_mkiv(mkiv_info, s, grd.gtype, list(grd.node_labels), vars_node_by_id, list(grd.edge_labels_etc), vars_edge_by_id_by_label_etc)

    util_common.timer_section('solve')

    result_info = None
    if s.solve():
        util_common.timer_section('create graph')

        if util_graph.gtype_directed(grd.gtype):
            gr = nx.DiGraph()
        else:
            gr = nx.Graph()

        for ii, vvs in vars_node_by_id.items():
            label = util_solvers.get_one_set(s, vvs)

            if label is not None:
                gr.add_node(ii)
                gr.nodes[ii][util_graph.GATTR_LABEL] = label
                if use_edge_deltas is not None or use_edge_polars is not None:
                    gr.nodes[ii][util_graph.GATTR_POSITION] = s.get_var_pos_xform(vars_node_xform[ii])

        for (ii, jj), vvs in vars_edge_by_id_by_label_etc.items():
            label_etc = util_solvers.get_one_set(s, vvs)

            if label_etc is not None:
                util_common.check(ii in gr.nodes and jj in gr.nodes, 'edge with missing node')

                label, delta, polar, cycle = label_etc
                gr.add_edge(ii, jj)
                gr.edges[(ii, jj)][util_graph.GATTR_LABEL] = label
                if delta is not None:
                    gr.edges[(ii, jj)][util_graph.GATTR_DELTA] = delta
                if polar is not None:
                    gr.edges[(ii, jj)][util_graph.GATTR_POLAR] = polar
                if cycle is not None:
                    gr.edges[(ii, jj)][util_graph.GATTR_CYCLE] = cycle

        util_graph.check_graph(gr, grd.gtype)

        if edgeopt in [EDGEOPT_GRID, EDGEOPT_RECT] and use_edge_deltas is None and use_edge_polars is None:
            util_graph.layout_grid(gr, east_label, south_label)

        if use_edge_deltas is not None or use_edge_polars is not None:
            for ii in node_id_order:
                if ii not in gr.nodes:
                    continue
                pos_ii = gr.nodes[ii][util_graph.GATTR_POSITION]
                for jj in node_id_order:
                    if ii == jj:
                        continue
                    if jj not in gr.nodes:
                        continue
                    pos_jj = gr.nodes[jj][util_graph.GATTR_POSITION]

                    util_common.check(len(pos_ii) == len(pos_jj), 'lengths')
                    util_common.check(max([abs(pi - pj) for pi, pj in zip(pos_ii, pos_jj)]) >= MIN_LINF_DIST, 'dist')

        result_info = util_graph.GraphResultInfo()

        result_info.graphs = util_graph.Graphs()
        result_info.graphs.gtype = grd.gtype
        result_info.graphs.colors = grd.colors
        result_info.graphs.graphs = [gr]

        if mkiv_setup is not None:
            util_mkiv.update_result(mkiv_tuple, result_info)

    util_common.timer_section(None)

    return result_info



if __name__ == '__main__':
    util_common.timer_start()

    parser = argparse.ArgumentParser(description='Generate graphs based on example graph.')

    parser.add_argument('--solver', type=str, nargs='+', choices=util_solvers.SOLVER_LIST, default=[util_solvers.SOLVER_PYSAT_RC2], help='Solver name, from: ' + ','.join(util_solvers.SOLVER_LIST) + '.')
    parser.add_argument('--outfile', required=True, type=str, help='Output file.')
    parser.add_argument('--gdescfile', required=True, type=str, help='Input graph description file.')

    parser.add_argument('--minsize', required=True, type=int, help='Minimum size.')
    parser.add_argument('--maxsize', required=True, type=int, help='Maximum size.')

    parser.add_argument('--label-min', type=str, nargs='+', default=None, help='Minimum number of each label to generate.')
    parser.add_argument('--label-max', type=str, nargs='+', default=None, help='Maximum number of each label to generate.')
    parser.add_argument('--label-count', action='store_true', help='Generate using label counts from example.')

    parser.add_argument('--cycle-no', action='store_true', help='Forbid cycle.')
    parser.add_argument('--cycle-yes', action='store_true', help='Require cycle.')

    parser.add_argument('--mkiv-example', type=str, choices=util_mkiv.EXAMPLES, help='MKIV example name, from: ' + ','.join(util_mkiv.EXAMPLES) + '.')
    parser.add_argument('--mkiv-layers', type=int, help='MKIV number of layers.')

    parser.add_argument('--edgeopt', type=str, nargs='+', default=[EDGEOPT_TRI], help='Edge options, from: ' + ','.join(EDGEOPT_LIST) + '.')
    parser.add_argument('--connect', type=str, choices=CONNECT_LIST, default=CONNECT_REACH, help='Connect approach name, from: ' + ','.join(CONNECT_LIST) + '.')
    parser.add_argument('--randomize', type=int, help='Randomize based on given number.')

    parser.add_argument('--out-dot-none', action='store_true', help='Don\'t save dot file.')

    args = parser.parse_args()

    if len(args.solver) == 1:
        solver = util_solvers.solver_id_to_solver(args.solver[0])
    else:
        solver = util_solvers.PortfolioSolver(args.solver, None)

    if args.edgeopt is not None:
        edgeopt = args.edgeopt[0]
        edgeopt_params = tuple([int(ee) for ee in args.edgeopt[1:]])
        util_common.check(edgeopt in EDGEOPT_LIST, '--edgeopt must be in ' + ','.join(EDGEOPT_LIST))



    label_min = util_common.arg_list_to_dict_int(parser, '--label-min', args.label_min)
    label_max = util_common.arg_list_to_dict_int(parser, '--label-max', args.label_max)



    mkiv_setup = None

    if args.mkiv_example or args.mkiv_layers:
        if not args.mkiv_example or not args.mkiv_layers:
            parser.error('must use --mkiv-example and --mkiv-layers together')

        mkiv_setup = util_mkiv.MKIVSetup()
        mkiv_setup.example = args.mkiv_example
        mkiv_setup.layers = args.mkiv_layers



    with util_common.openz(args.gdescfile, 'rb') as f:
        grd = pickle.load(f)

    result_info = gdesc2graph(solver, grd, args.minsize, args.maxsize, edgeopt, edgeopt_params, label_min, label_max, args.label_count, args.cycle_no, args.cycle_yes, args.connect, mkiv_setup, args.randomize)

    if result_info is not None:
        util_graph.write_graph_gr(result_info.graphs, sys.stdout)
        util_graph.save_graph_result_info(result_info, args.out_dot_none, args.outfile)

        if mkiv_setup is not None:
            util_mkiv.save_graph_result_info_mkiv(result_info, args.out_dot_none, args.outfile)

        util_common.exit_solution_found()

    else:
        util_common.exit_solution_not_found()
