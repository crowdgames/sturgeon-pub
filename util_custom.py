import argparse, pickle, os, json
import util_common, util_path, util_reach, util_solvers



WEIGHT_CUSTOM            = 100

CUST_TEXT_COUNT          = 'text-count'
CUST_TEXT_EXCLUDE        = 'text-exclude'
CUST_TEXT_MIN            = 'text-min'
CUST_TEXT_MAX            = 'text-max'

CUST_TEXT_LEVEL          = 'text-level'
CUST_TEXT_LEVEL_WEIGHTED = 'text-level-weighted'
CUST_TEXT_LEVEL_SUBST    = 'text-level-subst'
CUST_TEXT_LEVEL_RANGE    = 'text-level-range'

CUST_FLAT_PATH           = 'flat-path'
CUST_FLAT_ENDS           = 'flat-ends'
CUST_FLAT_FWD            = 'flat-fwd'
CUST_FLAT_MIN            = 'flat-min'

CUST_LAYERED_FWD         = 'layered-fwd'
CUST_LAYERED_MIN_EDGE    = 'layered-min-edge'
CUST_LAYERED_MIN_TILE    = 'layered-min-tile'

CUST_FWDBWD_NOSTUCK      = 'fwdbwd-nostuck'
CUST_FWDBWD_STUCK        = 'fwdbwd-stuck'
CUST_FWDBWD_REACH_OPEN   = 'fwdbwd-reach-open'
CUST_FWDBWD_REACH_SINK   = 'fwdbwd-reach-sink'
CUST_FWDBWD_COUNT_SINK   = 'fwdbwd-count-sink'
CUST_FWDBWD_COUNT_FWDBWD = 'fwdbwd-count-fwdbwd'

CUST_PATH_STATE          = 'path-state'

CUST_RESULT              = 'result'

CUST_LIST = [CUST_TEXT_COUNT, CUST_TEXT_EXCLUDE, CUST_TEXT_MIN, CUST_TEXT_MAX,
             CUST_TEXT_LEVEL, CUST_TEXT_LEVEL_WEIGHTED, CUST_TEXT_LEVEL_SUBST, CUST_TEXT_LEVEL_RANGE,
             CUST_FLAT_PATH, CUST_FLAT_ENDS, CUST_FLAT_FWD, CUST_FLAT_MIN,
             CUST_LAYERED_FWD, CUST_LAYERED_MIN_EDGE, CUST_LAYERED_MIN_TILE,
             CUST_FWDBWD_NOSTUCK, CUST_FWDBWD_STUCK, CUST_FWDBWD_REACH_OPEN, CUST_FWDBWD_REACH_SINK, CUST_FWDBWD_COUNT_SINK, CUST_FWDBWD_COUNT_FWDBWD,
             CUST_PATH_STATE,
             CUST_RESULT]



def str_to_weight(s):
    if s == 'hard':
        return None
    elif s == 'soft':
        return WEIGHT_CUSTOM
    else:
        util_common.check(False, 'weight')

def str_to_json(s):
    util_common.check(os.path.isfile(s), f'file not found: {s}')
    with open(s, 'rt') as f:
        return json.load(f)

def str_to_result(s):
    util_common.check(os.path.isfile(s), f'file not found: {s}')
    with util_common.openz(s, 'rb') as f:
        return pickle.load(f)

def str_to_path(s):
    ret = []
    for edge_str in s.split(','):
        edge = tuple([int(elem) for elem in edge_str.split()])
        util_common.check(len(edge) == 4, f'wrong edge length: {edge}')
        ret.append(edge)
    return ret

def arg_cvt(args, cvts):
    util_common.check(len(args) == len(cvts), 'argument length')

    return [cvt(arg) for arg, cvt in zip(args, cvts)]

def args_to_custom(cust, args):
    if cust == CUST_TEXT_COUNT:
        util_common.check(len(args) >= 5 + 3 and (len(args) - 3) % 5 == 0, 'argument length')
        regions = []
        while len(args) >= 5:
            rlo, clo, rhi, chi, out_texts = arg_cvt(args[:5], (int, int, int, int, str))
            regions.append((rlo, clo, rhi, chi, out_texts))
            args = args[5:]
        tlo, thi, weight = arg_cvt(args, (int, int, str_to_weight))
        return TextCountConstraint(regions, tlo, thi, weight)

    elif cust == CUST_TEXT_EXCLUDE:
        out_texts, weight = arg_cvt(args, (str, str_to_weight))
        return TextExcludeConstraint(out_texts, weight)

    elif cust == CUST_TEXT_MIN:
        rlo, clo, rhi, chi, out_texts, weight = arg_cvt(args, (int, int, int, int, str, str_to_weight))
        return TextMinimizeConstraint(rlo, clo, rhi, chi, out_texts, weight)

    elif cust == CUST_TEXT_MAX:
        rlo, clo, rhi, chi, out_texts, weight = arg_cvt(args, (int, int, int, int, str, str_to_weight))
        return TextMaximizeConstraint(rlo, clo, rhi, chi, out_texts, weight)


    elif cust == CUST_TEXT_LEVEL:
        out_text_level, weight = arg_cvt(args, (util_common.read_text_level, str_to_weight))
        return TextLevelConstraint(out_text_level, weight)

    elif cust == CUST_TEXT_LEVEL_WEIGHTED:
        out_text_level, weights = arg_cvt(args, (util_common.read_text_level, str_to_json))
        return TextLevelWeightedConstraint(out_text_level, weights)

    elif cust == CUST_TEXT_LEVEL_SUBST:
        out_text_level, weights = arg_cvt(args, (util_common.read_text_level, str_to_json))
        return TextLevelSubstConstraint(out_text_level, weights)

    elif cust == CUST_TEXT_LEVEL_RANGE:
        out_text_level, lo, hi, weight = arg_cvt(args, (util_common.read_text_level, int, int, str_to_weight))
        return TextLevelRangeConstraint(out_text_level, lo, hi, weight)


    elif cust == CUST_FLAT_PATH:
        path_points, weight = arg_cvt(args, (str_to_path, str_to_weight))
        return FlatPathConstraint(path_points, weight)

    elif cust == CUST_FLAT_ENDS:
        sr, sc, gr, gc, weight = arg_cvt(args, (int, int, int, int, str_to_weight))
        return FlatEndsConstraint(sr, sc, gr, gc, weight)

    elif cust == CUST_FLAT_FWD:
        direction, weight, = arg_cvt(args, (str, str_to_weight))
        return FlatFwdConstraint(direction, weight)

    elif cust == CUST_FLAT_MIN:
        weight, = arg_cvt(args, (str_to_weight,))
        return FlatMinConstraint(weight)


    elif cust == CUST_LAYERED_FWD:
        direction, weight, = arg_cvt(args, (str, str_to_weight))
        return LayeredFwdConstraint(direction, weight)

    elif cust == CUST_LAYERED_MIN_EDGE:
        weight, = arg_cvt(args, (str_to_weight,))
        return LayeredMinEdgeConstraint(weight)

    elif cust == CUST_LAYERED_MIN_TILE:
        weight, = arg_cvt(args, (str_to_weight,))
        return LayeredMinTileConstraint(weight)


    elif cust == CUST_FWDBWD_NOSTUCK:
        weight, = arg_cvt(args, (str_to_weight,))
        return FwdBwdNoStuckConstraint(weight)

    elif cust == CUST_FWDBWD_STUCK:
        sink_ok, weight = arg_cvt(args, (str, str_to_weight))
        return FwdBwdStuckConstraint(sink_ok, weight)

    elif cust == CUST_FWDBWD_REACH_OPEN:
        weight, = arg_cvt(args, (str_to_weight,))
        return FwdBwdReachOpenConstraint(weight)

    elif cust == CUST_FWDBWD_REACH_SINK:
        weight, = arg_cvt(args, (str_to_weight,))
        return FwdBwdReachSinkConstraint(weight)

    elif cust == CUST_FWDBWD_COUNT_SINK:
        if len(args) == 3:
            rlo, clo, rhi, chi = None, None, None, None
            snklo, snkhi, weight = arg_cvt(args, (int, int, str_to_weight))
        else:
            rlo, clo, rhi, chi, snklo, snkhi, weight = arg_cvt(args, (int, int, int, int, int, int, str_to_weight))

        return FwdBwdCountSinkConstraint(rlo, clo, rhi, chi, snklo, snkhi, weight)

    elif cust == CUST_FWDBWD_COUNT_FWDBWD:
        fwdlo, fwdhi, bwdlo, bwdhi, weight = arg_cvt(args, (int, int, int, int, str_to_weight))

        return FwdBwdCountFwdBwdConstraint(fwdlo, fwdhi, bwdlo, bwdhi, weight)


    elif cust == CUST_PATH_STATE:
        what, cost, reach_layers, unreach_layers, weight = arg_cvt(args, (str, str, int, int, str_to_weight))
        return PathStateConstraint(what, cost, reach_layers, unreach_layers, weight)


    elif cust == CUST_RESULT:
        result_info, which, rlo, clo, rhi, chi, roff, coff, weight = arg_cvt(args, (str_to_result, str, int, int, int, int, int, int, str_to_weight))
        return ResultConstraint(result_info, which, rlo, clo, rhi, chi, roff, coff, weight)


    else:
        util_common.check(False, 'cust')



def possible_tiles_at_texts(rr, cc, texts, gen):
    tile_to_text = gen.get_scheme_info().tileset.tile_to_text
    possible_tiles = [tile for tile in gen.get_possible_tiles_at(rr, cc)
                      if ((tile == util_common.VOID_TILE and util_common.VOID_TEXT in texts) or
                          (tile != util_common.VOID_TILE and tile_to_text[tile] in texts))]
    return possible_tiles



class CustomConstraint:
    def __init__(self):
        pass

    def add(self, gen):
        pass



class TextCountConstraint(CustomConstraint):
    def __init__(self, regions, tlo, thi, weight):
        self._regions = regions
        self._tlo = tlo
        self._thi = thi
        self._weight = weight

    def add(self, gen):
        print('add custom text count constraint', self._weight)

        rcts = []
        for rlo, clo, rhi, chi, out_texts in self._regions:
            for rr in range(rlo, rhi):
                for cc in range(clo, chi):
                    possible_tiles = possible_tiles_at_texts(rr, cc, out_texts, gen)
                    rcts.append((rr, cc, possible_tiles))

        gen.add_constraint_tile_counts(rcts, self._tlo, self._thi, self._weight)

class TextExcludeConstraint(CustomConstraint):
    def __init__(self, out_texts, weight):
        self._out_texts = out_texts
        self._weight = weight

    def add(self, gen):
        print('add custom text exclude constraint', self._weight)

        rcts = []
        for rr in range(gen.get_rows()):
            for cc in range(gen.get_cols()):
                possible_tiles = possible_tiles_at_texts(rr, cc, self._out_texts, gen)
                rcts.append((rr, cc, possible_tiles))
        gen.add_constraint_tile_counts(rcts, 0, 0, self._weight)

class TextMinimizeConstraint(CustomConstraint):
    def __init__(self, rlo, clo, rhi, chi, out_texts, weight):
        self._rlo = rlo
        self._clo = clo
        self._rhi = rhi
        self._chi = chi
        self._out_texts = out_texts
        self._weight = weight

    def add(self, gen):
        print('add custom text minimize constraint', self._weight)

        for rr in range(self._rlo, self._rhi):
            for cc in range(self._clo, self._chi):
                possible_tiles = possible_tiles_at_texts(rr, cc, self._out_texts, gen)
                gen.add_constraint_tile_counts([(rr, cc, possible_tiles)], 0, 0, self._weight)

class TextMaximizeConstraint(CustomConstraint):
    def __init__(self, rlo, clo, rhi, chi, out_texts, weight):
        self._rlo = rlo
        self._clo = clo
        self._rhi = rhi
        self._chi = chi
        self._out_texts = out_texts
        self._weight = weight

    def add(self, gen):
        print('add custom text maximize constraint', self._weight)

        for rr in range(self._rlo, self._rhi):
            for cc in range(self._clo, self._chi):
                possible_tiles = possible_tiles_at_texts(rr, cc, self._out_texts, gen)
                gen.add_constraint_tile_counts([(rr, cc, possible_tiles)], 1, 1, self._weight)



class TextLevelConstraint(CustomConstraint):
    def __init__(self, out_text_level, weight):
        self._out_text_level = out_text_level
        self._weight = weight

    def add(self, gen):
        print('add custom text level constraint', self._weight)

        util_common.check(len(self._out_text_level) == gen.get_rows(), 'size')
        util_common.check(len(self._out_text_level[0]) == gen.get_cols(), 'size')

        for rr in range(gen.get_rows()):
            for cc in range(gen.get_cols()):
                out_text = self._out_text_level[rr][cc]
                if out_text != util_common.DEFAULT_TEXT:
                    possible_tiles = possible_tiles_at_texts(rr, cc, out_text, gen)
                    gen.add_constraint_tile_counts([(rr, cc, possible_tiles)], 1, 1, self._weight)

class TextLevelWeightedConstraint(CustomConstraint):
    def __init__(self, out_text_level, weights):
        self._out_text_level = out_text_level
        self._weights = weights

    def add(self, gen):
        print('add custom text level weighted constraint')

        util_common.check(len(self._out_text_level) == gen.get_rows(), 'size')
        util_common.check(len(self._out_text_level[0]) == gen.get_cols(), 'size')

        util_common.check(len(self._weights) == gen.get_rows(), 'weights size')
        util_common.check(len(self._weights[0]) == gen.get_cols(), 'weights size')

        for rr in range(gen.get_rows()):
            for cc in range(gen.get_cols()):
                out_text = self._out_text_level[rr][cc]
                weight = self._weights[rr][cc]
                if out_text != util_common.DEFAULT_TEXT:
                    possible_tiles = possible_tiles_at_texts(rr, cc, out_text, gen)
                    gen.add_constraint_tile_counts([(rr, cc, possible_tiles)], 1, 1, weight)

class TextLevelSubstConstraint(CustomConstraint):
    def __init__(self, out_text_level, weights):
        self._out_text_level = out_text_level
        self._weights = weights

    def add(self, gen):
        print('add custom text level subst constraint')

        util_common.check(len(self._out_text_level) == gen.get_rows(), 'size')
        util_common.check(len(self._out_text_level[0]) == gen.get_cols(), 'size')

        tile_to_text = gen.get_scheme_info().tileset.tile_to_text

        for rr in range(gen.get_rows()):
            for cc in range(gen.get_cols()):
                out_text = self._out_text_level[rr][cc]
                if out_text != util_common.DEFAULT_TEXT:
                    possible_texts_to_tiles = {}
                    for ptile in gen.get_possible_tiles_at(rr, cc):
                        ptext = tile_to_text[ptile]
                        if ptext not in possible_texts_to_tiles:
                            possible_texts_to_tiles[ptext] = []
                        possible_texts_to_tiles[ptext].append(ptile)

                    if out_text not in self._weights:
                        gen.add_constraint_tile_counts([(rr, cc, possible_texts_to_tiles[out_text])], 1, 1, None)
                    else:
                        substs = self._weights[out_text]
                        for ptext, ptiles in possible_texts_to_tiles.items():
                            weight = substs[ptext] if ptext in substs else None
                            if weight == 0:
                                pass
                            elif weight is None:
                                gen.add_constraint_tile_counts([(rr, cc, ptiles)], 0, 0, None)
                            else:
                                other_tiles = []
                                for otext, otiles in possible_texts_to_tiles.items():
                                    if ptext != otext and otext in substs:
                                        other_tiles += otiles
                                gen.add_constraint_tile_counts([(rr, cc, other_tiles)], 1, 1, weight)

class TextLevelRangeConstraint(CustomConstraint):
    def __init__(self, out_text_level, lo, hi, weight):
        self._out_text_level = out_text_level
        self._lo = lo
        self._hi = hi
        self._weight = weight

    def add(self, gen):
        print('add custom text level range constraint', self._weight)

        util_common.check(len(self._out_text_level) == gen.get_rows(), 'size')
        util_common.check(len(self._out_text_level[0]) == gen.get_cols(), 'size')

        rcts = []
        for rr in range(gen.get_rows()):
            for cc in range(gen.get_cols()):
                out_text = self._out_text_level[rr][cc]
                if out_text != util_common.DEFAULT_TEXT:
                    possible_tiles = possible_tiles_at_texts(rr, cc, out_text, gen)
                    rcts.append((rr, cc, possible_tiles))

        gen.add_constraint_tile_counts(rcts, len(rcts) - self._hi, len(rcts) - self._lo, self._weight)



class FlatPathConstraint(CustomConstraint):
    def __init__(self, path, weight):
        self._path = path
        self._weight = weight

    def add(self, gen):
        print('add custom flat path constraint', self._weight)

        util_common.check(gen.get_num_reach_connect() > 0, 'no reach move')

        for connect_index in range(gen.get_num_reach_connect()):
            util_common.check(gen._reach_connect_entry[connect_index].method == util_common.REACH_METHOD_FLAT, 'method')

            if gen.is_unreachable(connect_index):
                continue

            path_cache = {}
            for edge in self._path:
                if len(edge) == 4:
                    fr, fc, tr, tc = edge
                    pwtr = tr
                    pwtc = tc
                elif len(edge) == 6:
                    fr, fc, tr, tc, pwtr, pwtc = edge
                else:
                    fr, fc, tr, tc, pwtr, pwtc = None, None, None, None, None, None
                    util_common.check(False, 'edge length')

                path_cache[(fr, fc, tr, tc, pwtr, pwtc)] = None

            reach_edges = gen.reachability_edges(connect_index)
            util_common.check(reach_edges is not None, 'reach_edges')

            for rr in range(gen.get_rows()):
                for cc in range(gen.get_cols()):
                    gen.add_constraint_start(rr, cc, (rr, cc) == tuple(self._path[0][0:2]), self._weight)
                    gen.add_constraint_goal(rr, cc, (rr, cc) == tuple(self._path[-1][2:4]), self._weight)

            for cfr, cfc, ctr, ctc, cpwtr, cpwtc in reach_edges:
                on_path = (cfr, cfc, ctr, ctc, cpwtr, cpwtc) in path_cache
                gen.add_constraint_reach_edge(connect_index, cfr, cfc, ctr, ctc, cpwtr, cpwtc, on_path, self._weight)
                if on_path:
                    del path_cache[(cfr, cfc, ctr, ctc, cpwtr, cpwtc)]

            util_common.check(len(path_cache) == 0, 'not all path edges used')

            gen.append_extra_meta([util_common.meta_path('custom-path', self._path)])

class FlatEndsConstraint(CustomConstraint):
    def __init__(self, sr, sc, gr, gc, weight):
        self._sr = sr
        self._sc = sc
        self._gr = gr
        self._gc = gc
        self._weight = weight

    def add(self, gen):
        print('add custom flat ends constraint', self._weight)

        for rr in range(gen.get_rows()):
            for cc in range(gen.get_cols()):
                gen.add_constraint_start(rr, cc, (rr, cc) == (self._sr, self._sc), self._weight)
                gen.add_constraint_goal(rr, cc, (rr, cc) == (self._gr, self._gc), self._weight)

        ends = [(self._sr, self._sc), (self._gr, self._gc)]
        gen.append_extra_meta([util_common.meta_tile('custom-path-ends', ends)])

class FlatFwdConstraint(CustomConstraint):
    def __init__(self, direction, weight):
        self._direction = direction
        self._weight = weight

    def add(self, gen):
        print('add custom flat forward constraint', self._weight)

        util_common.check(gen.get_num_reach_connect() > 0, 'no reach move')

        for connect_index in range(gen.get_num_reach_connect()):
            util_common.check(gen._reach_connect_entry[connect_index].method == util_common.REACH_METHOD_FLAT, 'method')

            if gen.is_unreachable(connect_index):
                continue

            reach_edges = gen.reachability_edges(connect_index)
            util_common.check(reach_edges is not None, 'reach_edges')

            for cfr, cfc, ctr, ctc, cpwtr, cpwtc in reach_edges:
                if self._direction == util_reach.RSGLOC_B_T:
                    exclude = (ctr >= cfr)
                elif self._direction == util_reach.RSGLOC_L_R:
                    exclude = (ctc <= cfc)
                else:
                    exclude = None
                    util_common.check(False, 'direction')

                if exclude:
                    gen.add_constraint_reach_edge(connect_index, cfr, cfc, ctr, ctc, cpwtr, cpwtc, False, self._weight)

class FlatMinConstraint(CustomConstraint):
    def __init__(self, weight):
        self._weight = weight

    def add(self, gen):
        print('add custom flat min constraint', self._weight)

        util_common.check(gen.get_num_reach_connect() > 0, 'no reach move')

        for connect_index in range(gen.get_num_reach_connect()):
            util_common.check(gen._reach_connect_entry[connect_index].method == util_common.REACH_METHOD_FLAT, 'method')

            if gen.is_unreachable(connect_index):
                continue

            vars_node = gen._reach_connect_entry[connect_index].vars_node

            for loc in vars_node:
                gen._solver.cnstr_count([vars_node[loc]], True, 0, 0, self._weight)



class LayeredFwdConstraint(CustomConstraint):
    def __init__(self, direction, weight):
        self._direction = direction
        self._weight = weight

    def add(self, gen):
        print('add custom layered forward constraint', self._weight)

        util_common.check(gen.get_num_reach_connect() > 0, 'no reach move')

        for connect_index in range(gen.get_num_reach_connect()):
            util_common.check(gen._reach_connect_entry[connect_index].method == util_common.REACH_METHOD_LAYERED, 'method')
            util_common.check(not gen.is_unreachable(connect_index), 'unreachable')

            vars_layer_edge = gen._reach_connect_entry[connect_index].vars_layer_edge

            for layer in vars_layer_edge:
                for edge_key, edge_var in vars_layer_edge[layer].items():
                    fr, fc, tr, tc, pwtr, pwtc, need_open_path, need_open_aux, need_closed_path, need_closed_aux = edge_key

                    if self._direction == util_reach.RSGLOC_B_T:
                        exclude = (tr >= fr)
                    elif self._direction == util_reach.RSGLOC_L_R:
                        exclude = (tc <= fc)
                    else:
                        exclude = None
                        util_common.check(False, 'direction')

                    if exclude:
                        gen._solver.cnstr_count([edge_var], True, 0, 0, self._weight)

class LayeredMinEdgeConstraint(CustomConstraint):
    def __init__(self, weight):
        self._weight = weight

    def add(self, gen):
        print('add custom layered min edge constraint', self._weight)

        util_common.check(gen.get_num_reach_connect() > 0, 'no reach move')

        for connect_index in range(gen.get_num_reach_connect()):
            util_common.check(gen._reach_connect_entry[connect_index].method == util_common.REACH_METHOD_LAYERED, 'method')
            util_common.check(not gen.is_unreachable(connect_index), 'unreachable')

            vars_layer_edge = gen._reach_connect_entry[connect_index].vars_layer_edge

            for layer in vars_layer_edge:
                for edge_key, edge_var in vars_layer_edge[layer].items():
                    gen._solver.cnstr_count([edge_var], True, 0, 0, self._weight)

class LayeredMinTileConstraint(CustomConstraint):
    def __init__(self, weight):
        self._weight = weight

    def add(self, gen):
        print('add custom layered min tile constraint', self._weight)

        util_common.check(gen.get_num_reach_connect() > 0, 'no reach move')

        for connect_index in range(gen.get_num_reach_connect()):
            util_common.check(gen._reach_connect_entry[connect_index].method == util_common.REACH_METHOD_LAYERED, 'method')
            util_common.check(not gen.is_unreachable(connect_index), 'unreachable')

            vars_layer_edge = gen._reach_connect_entry[connect_index].vars_layer_edge

            tile_max = 0
            for layer in vars_layer_edge:
                for edge_key, edge_var in vars_layer_edge[layer].items():
                    fr, fc, tr, tc, pwtr, pwtc, need_open_path, need_open_aux, need_closed_path, need_closed_aux = edge_key
                    tile_len = util_path.edge_key_cost_tile(edge_key)
                    tile_max = max(tile_max, tile_len)

            for layer in vars_layer_edge:
                tile_len_vars = [gen._solver.make_var() for tt in range(tile_max)]
                for len_vv in tile_len_vars:
                    gen._solver.cnstr_count([len_vv], True, 0, 0, self._weight)

                for edge_key, edge_var in vars_layer_edge[layer].items():
                    fr, fc, tr, tc, pwtr, pwtc, need_open_path, need_open_aux, need_closed_path, need_closed_aux = edge_key
                    tile_len = util_path.edge_key_cost_tile(edge_key)
                    for tt, len_vv in enumerate(tile_len_vars):
                        if tt < tile_len:
                            gen._solver.cnstr_implies_disj(edge_var, True, [len_vv], True, None)



class FwdBwdNoStuckConstraint(CustomConstraint):
    def __init__(self, weight):
        self._weight = weight

    def add(self, gen):
        print('add custom fwdbwd nostuck constraint', self._weight)

        util_common.check(gen.get_num_reach_connect() > 0, 'no reach move')

        for connect_index in range(gen.get_num_reach_connect()):
            util_common.check(gen._reach_connect_entry[connect_index].method == util_common.REACH_METHOD_FWDBWD, 'method')

            fwd_reachable_vars = gen.reachability_fwdbwd_fwd_reachable(connect_index)
            bwd_reachable_vars = gen.reachability_fwdbwd_bwd_reachable(connect_index)
            sink_vars = gen.reachability_fwdbwd_sink(connect_index)

            # if reachable forward (and not sink) then reachable backward
            for rc in fwd_reachable_vars:
                fwd_reachable_and_not_sink = fwd_reachable_vars[rc] if sink_vars is None else gen._solver.make_conj([fwd_reachable_vars[rc], sink_vars[rc]], [True, False])
                gen._solver.cnstr_implies_disj(fwd_reachable_and_not_sink, True, [bwd_reachable_vars[rc]], True, self._weight)

class FwdBwdStuckConstraint(CustomConstraint):
    def __init__(self, sink_ok, weight):
        util_common.check(sink_ok in ['sink-ok', 'sink-no'], 'value must be sink-ok or sink-no')

        self._sink_ok = (sink_ok == 'sink-ok')
        self._weight = weight

    def add(self, gen):
        print('add custom fwdbwd stuck constraint', self._weight)

        util_common.check(gen.get_num_reach_connect() > 0, 'no reach move')

        for connect_index in range(gen.get_num_reach_connect()):
            util_common.check(gen._reach_connect_entry[connect_index].method == util_common.REACH_METHOD_FWDBWD, 'method')

            fwd_reachable_vars = gen.reachability_fwdbwd_fwd_reachable(connect_index)
            bwd_reachable_vars = gen.reachability_fwdbwd_bwd_reachable(connect_index)
            sink_vars = gen.reachability_fwdbwd_sink(connect_index)

            if not self._sink_ok:
                out_edges = {}
                edge_vars = gen.reachability_fwdbwd_edges(connect_index)
                for edge_key, edge_var in edge_vars.items():
                    fr, fc, tr, tc, pwtr, pwtc, need_open_path, need_open_aux, need_closed_path, need_closed_aux = edge_key
                    if (fr, fc) not in out_edges:
                        out_edges[(fr, fc)] = []
                    out_edges[(fr, fc)].append((tr, tc, edge_var))
            else:
                out_edges = None

            # at least one reachable forward (and not sink) location not reachable backward
            vars_stuck = []
            for rc in fwd_reachable_vars:
                if rc in bwd_reachable_vars:
                    fwd_reachable_and_not_sink = fwd_reachable_vars[rc] if sink_vars is None else gen._solver.make_conj([fwd_reachable_vars[rc], sink_vars[rc]], [True, False])
                    loc_stuck = gen._solver.make_conj([fwd_reachable_and_not_sink, bwd_reachable_vars[rc]], [True, False])
                    vars_stuck.append(loc_stuck)

                    if not self._sink_ok and sink_vars is not None and rc in out_edges:
                        for tr, tc, edge_var in out_edges[rc]:
                            sink_connect = gen._solver.make_conj([edge_var, sink_vars[(tr, tc)]], True)
                            gen._solver.cnstr_implies_disj(loc_stuck, True, [sink_connect], False, None)

            gen._solver.cnstr_count(vars_stuck, True, 1, len(vars_stuck), None)

class FwdBwdReachOpenConstraint(CustomConstraint):
    def __init__(self, weight):
        self._weight = weight

    def add(self, gen):
        print('add custom fwdbwd reach open constraint', self._weight)

        util_common.check(gen.get_num_reach_connect() > 0, 'no reach move')

        for connect_index in range(gen.get_num_reach_connect()):
            util_common.check(gen._reach_connect_entry[connect_index].method == util_common.REACH_METHOD_FWDBWD, 'method')

            open_vars = gen.reachability_open(connect_index)
            fwd_reachable_vars = gen.reachability_fwdbwd_fwd_reachable(connect_index)

            for rc, open_var in open_vars.items():
                gen._solver.cnstr_implies_disj(open_var, True, [fwd_reachable_vars[rc]], True, self._weight)

class FwdBwdReachSinkConstraint(CustomConstraint):
    def __init__(self, weight):
        self._weight = weight

    def add(self, gen):
        print('add custom fwdbwd reach sink constraint', self._weight)

        util_common.check(gen.get_num_reach_connect() > 0, 'no reach move')

        for connect_index in range(gen.get_num_reach_connect()):
            sink_vars = gen.reachability_fwdbwd_sink(connect_index)
            fwd_reachable_vars = gen.reachability_fwdbwd_fwd_reachable(connect_index)

            util_common.check(sink_vars is not None, 'sinks requested but no sink vars')

            for rc, sink_var in sink_vars.items():
                gen._solver.cnstr_implies_disj(sink_var, True, [fwd_reachable_vars[rc]], True, self._weight)

class FwdBwdCountSinkConstraint(CustomConstraint):
    def __init__(self, rlo, clo, rhi, chi, snklo, snkhi, weight):
        self._rlo = rlo
        self._clo = clo
        self._rhi = rhi
        self._chi = chi
        self._snklo = snklo
        self._snkhi = snkhi
        self._weight = weight

    def add(self, gen):
        print('add custom fwdbwd count sink constraint', self._weight)

        util_common.check(gen.get_num_reach_connect() > 0, 'no reach move')

        rlo = 0 if self._rlo is None else self._rlo
        clo = 0 if self._clo is None else self._clo
        rhi = gen.get_rows() if self._rhi is None else self._rhi
        chi = gen.get_cols() if self._chi is None else self._chi

        for connect_index in range(gen.get_num_reach_connect()):
            util_common.check(gen._reach_connect_entry[connect_index].method == util_common.REACH_METHOD_FWDBWD, 'method')

            sink_vars = gen.reachability_fwdbwd_sink(connect_index)

            if sink_vars is None:
                util_common.check(self._snklo == 0, 'sinks requested but no sink vars')
            else:
                use_sink_vars = []
                for rc, sink_var in sink_vars.items():
                    rr, cc = rc
                    if rlo <= rr and rr < rhi and clo <= cc and cc < chi:
                        use_sink_vars.append(sink_var)

                gen._solver.cnstr_count(use_sink_vars, True, self._snklo, self._snkhi, self._weight)

class FwdBwdCountFwdBwdConstraint(CustomConstraint):
    def __init__(self, fwdlo, fwdhi, bwdlo, bwdhi, weight):
        self._fwdlo = fwdlo
        self._fwdhi = fwdhi
        self._bwdlo = bwdlo
        self._bwdhi = bwdhi
        self._weight = weight

    def add(self, gen):
        print('add custom fwdbwd count fwdbwd constraint', self._weight)

        util_common.check(gen.get_num_reach_connect() > 0, 'no reach move')

        for connect_index in range(gen.get_num_reach_connect()):
            util_common.check(gen._reach_connect_entry[connect_index].method == util_common.REACH_METHOD_FWDBWD, 'method')

            fwd_reachable_vars = gen.reachability_fwdbwd_fwd_reachable(connect_index)
            bwd_reachable_vars = gen.reachability_fwdbwd_bwd_reachable(connect_index)

            gen._solver.cnstr_count(list(fwd_reachable_vars.values()), True, self._fwdlo, self._fwdhi, self._weight)
            gen._solver.cnstr_count(list(bwd_reachable_vars.values()), True, self._bwdlo, self._bwdhi, self._weight)



PATH_ANY                   = 'any'

PATH_COUNT_EDGE            = 'count-edge'
PATH_COUNT_EDGE_UP         = 'count-edge-up'
PATH_COUNT_EDGE_DOWN       = 'count-edge-down'
PATH_COUNT_EDGE_LEFT       = 'count-edge-left'
PATH_COUNT_EDGE_RIGHT      = 'count-edge-right'
PATH_COUNT_EDGE_JUMP       = 'count-edge-jump'
PATH_COUNT_EDGE_ONGROUND   = 'count-edge-onground'
PATH_COUNT_TILE            = 'count-tile'

PATH_AIRTIME_JUMP          = 'airtime-jump'

PATH_JUMP_ENTROPY          = 'jumpentropy'
PATH_SPEED                 = 'speed'
PATH_ONGROUNDRATIO         = 'ongroundratio'
PATH_AVERAGE_ROW           = 'average-row'

class PathStateConstraint(CustomConstraint):
    def __init__(self, what, cost, reach_layers, unreach_layers, weight):
        self._what = what
        self._cost = cost
        self._reach_layers = reach_layers
        self._unreach_layers = unreach_layers
        self._weight = weight

    def add(self, gen):
        print('add custom path state constraint', self._what, self._cost, self._reach_layers, self._unreach_layers, self._weight)

        reach_layers = self._reach_layers
        unreach_layers = self._unreach_layers

        util_common.check(reach_layers >= 0 and unreach_layers >= 0 and (reach_layers > 0 or unreach_layers > 0), 'layers')

        what_splt = self._what.split(',')
        what_type = what_splt[0]
        what_args = what_splt[1:]

        def edge_key_to_edge(_edge_key):
            _fr, _fc, _tr, _tc, _pwtr, _pwtc, _need_open_path, _need_open_aux, _need_closed_path, _need_closed_aux = _edge_key
            return (_fr, _fc, _tr, _tc, _pwtr, _pwtc)

        def edge_key_to_need_closed_aux(_edge_key):
            _fr, _fc, _tr, _tc, _pwtr, _pwtc, _need_open_path, _need_open_aux, _need_closed_path, _need_closed_aux = _edge_key
            return _need_closed_aux

        def edge_is_jump(_edge_key):
            return util_path.edge_is_jump(edge_key_to_edge(_edge_key), edge_key_to_need_closed_aux(_edge_key))

        def edge_is_onground(_edge_key):
            return util_path.edge_is_onground(edge_key_to_edge(_edge_key), edge_key_to_need_closed_aux(_edge_key))

        def edge_accum_rows(_edge_key, _include_from):
            _fr, _fc, _tr, _tc, _pwtr, _pwtc, _need_open_path, _need_open_aux, _need_closed_path, _need_closed_aux = _edge_key
            _tiles = _need_open_path + _need_closed_path + ((_pwtr, _pwtc),)
            if _include_from:
                _tiles += ((_fr, _fc),)
            return sum([_rr for _rr, _cc in _tiles])

        if what_type in [PATH_ANY]:
            util_common.check(len(what_args) == 0, 'what_args')

            state_start = None

            def state_reachable_func(_state):
                return True

            state_unreachable_func = None

            def state_next_func(_state, _edge_key):
                return None

        elif what_type in [PATH_COUNT_EDGE, PATH_COUNT_EDGE_UP, PATH_COUNT_EDGE_DOWN, PATH_COUNT_EDGE_LEFT, PATH_COUNT_EDGE_RIGHT, PATH_COUNT_EDGE_JUMP, PATH_COUNT_EDGE_ONGROUND, PATH_COUNT_TILE]:
            count_lo, count_hi = arg_cvt(what_args[:2], (int, int))
            what_args = what_args[2:]

            if what_type == PATH_COUNT_TILE: # adjust for not counting starting tile
                count_lo -= 1
                count_hi -= 1

            state_start = 0

            def state_reachable_func(_state):
                return count_lo <= _state and _state <= count_hi

            def state_unreachable_func(_state):
                return _state < count_lo

            if what_type == PATH_COUNT_EDGE:
                util_common.check(len(what_args) == 0, 'what_args')
                count_func = lambda _edge_key: 1
            elif what_type == PATH_COUNT_EDGE_UP:
                by, = (1,) if len(what_args) == 0 else arg_cvt(what_args, (int,))
                count_func = lambda _edge_key: util_path.edge_is_up_by(edge_key_to_edge(_edge_key), by)
            elif what_type == PATH_COUNT_EDGE_DOWN:
                by, = (1,) if len(what_args) == 0 else arg_cvt(what_args, (int,))
                count_func = lambda _edge_key: util_path.edge_is_down_by(edge_key_to_edge(_edge_key), by)
            elif what_type == PATH_COUNT_EDGE_LEFT:
                by, = (1,) if len(what_args) == 0 else arg_cvt(what_args, (int,))
                count_func = lambda _edge_key: util_path.edge_is_left_by(edge_key_to_edge(_edge_key), by)
            elif what_type == PATH_COUNT_EDGE_RIGHT:
                by, = (1,) if len(what_args) == 0 else arg_cvt(what_args, (int,))
                count_func = lambda _edge_key: util_path.edge_is_right_by(edge_key_to_edge(_edge_key), by)
            elif what_type == PATH_COUNT_EDGE_JUMP:
                util_common.check(len(what_args) == 0, 'what_args')
                count_func = edge_is_jump
            elif what_type == PATH_COUNT_EDGE_ONGROUND:
                util_common.check(len(what_args) == 0, 'what_args')
                count_func = edge_is_onground
            elif what_type == PATH_COUNT_TILE:
                util_common.check(len(what_args) == 0, 'what_args')
                count_func = util_path.edge_key_cost_tile
            else:
                count_func = None
                util_common.check(False, 'count_func')

            def state_next_func(_state, _edge_key):
                return min(count_hi + 1, _state + count_func(_edge_key))

        elif what_type == PATH_AIRTIME_JUMP:
            count_lo, count_hi = arg_cvt(what_args, (int, int))

            state_start = (0, 0)

            def state_reachable_func(_state):
                _curr, _high = _state
                return count_lo <= _high and _high <= count_hi

            state_unreachable_func = None

            def state_next_func(_state, _edge_key):
                _curr, _high = _state
                if edge_is_jump(_edge_key): # start with a jump
                    _curr = min(count_hi + 1, util_path.edge_key_cost_tile(_edge_key))
                elif _curr > 0 and not edge_is_onground(_edge_key): # continuing a jump
                    _curr = min(count_hi + 1, _curr + util_path.edge_key_cost_tile(_edge_key))
                else:
                    _curr = 0
                _high = max(_curr, _high)
                return (_curr, _high)

        elif what_type in [PATH_JUMP_ENTROPY, PATH_SPEED, PATH_ONGROUNDRATIO, PATH_AVERAGE_ROW]:
            if len(what_args) == 3:
                target_lo, target_hi, target_bound_lo = arg_cvt(what_args, (float, float, float))
                target_bound_hi = target_bound_lo
            elif len(what_args) == 4:
                target_lo, target_hi, target_bound_lo, target_bound_hi = arg_cvt(what_args, (float, float, float, float))
            else:
                target_lo, target_hi, target_bound_lo, target_bound_hi = None, None, None, None
                util_common.check(False, 'what_args')

            state_start = (0, 0)

            def state_reachable_func(_state):
                if _state is None:
                    return False

                _numer, _denom = _state

                if _denom <= 0:
                    return False

                _val = _numer / _denom
                return target_lo <= _val and _val <= target_hi

            state_unreachable_func = None

            def state_next_func(_state, _edge_key):
                if _state is None:
                    return None

                _numer, _denom = _state

                if what_type == PATH_JUMP_ENTROPY:
                    if edge_is_jump(_edge_key):
                        _numer += 1
                        _denom += 1
                    _denom += abs(util_path.edge_delta_cols(edge_key_to_edge(_edge_key)))

                elif what_type in [PATH_SPEED, PATH_ONGROUNDRATIO, PATH_AVERAGE_ROW]:
                    include_from = (_denom == 0)

                    if what_type == PATH_SPEED:
                        _numer += util_path.edge_delta_cols(edge_key_to_edge(_edge_key))
                    elif what_type == PATH_ONGROUNDRATIO:
                        _numer += edge_is_onground(_edge_key)
                    elif what_type == PATH_AVERAGE_ROW:
                        _numer += edge_accum_rows(_edge_key, include_from)
                    else:
                        util_common.check(False, 'what_type')

                    _denom += util_path.edge_key_cost_tile(_edge_key)
                    if include_from:
                        _denom += 1

                util_common.check(_denom >= 0, 'denom')

                if _denom == 0:
                    return None

                if _denom >= reach_layers + 1:
                    return None

                _val = _numer / _denom
                _bound_lo = target_bound_lo if target_bound_lo >= 0.0 else -target_bound_lo / _denom
                _bound_hi = target_bound_hi if target_bound_hi >= 0.0 else -target_bound_hi / _denom
                if _val < target_lo - _bound_lo or target_hi + _bound_hi < _val:
                    return None

                return (_numer, _denom)

        else:
            state_start = None
            state_reachable_func = None
            state_unreachable_func = None
            state_next_func = None
            util_common.check(False, 'what')

        if self._cost in util_path.COST_EDGE:
            def reach_edge_cost(_edge_key):
                return 1
        elif self._cost == util_path.COST_TILE:
            def reach_edge_cost(_edge_key):
                return util_path.edge_key_cost_tile(_edge_key)
        else:
            reach_edge_cost = None
            util_common.check(False, 'cost')

        start_key = (state_start, 0)

        var_false = gen._solver.make_var()
        gen._solver.cnstr_count([var_false], True, 0, 0, None)

        util_common.check(gen.get_num_reach_connect() > 0, 'no reach move')

        for connect_index in range(gen.get_num_reach_connect()):
            util_common.check(gen._reach_connect_entry[connect_index].method == util_common.REACH_METHOD_NULL, 'method')

            if gen.is_unreachable(connect_index):
                continue

            reach_connect_info = gen._reach_connect_entry[connect_index].connect_info
            open_vars = gen._reach_connect_entry[connect_index].vars_open
            rgraph = gen._reach_connect_entry[connect_index].rgraph


            reach_vars_edge = gen._make_edge_vars(rgraph)

            for edge_key, edge_var in reach_vars_edge.items():
                fr, fc, tr, tc, pwtr, pwtc, need_open_path, need_open_aux, need_closed_path, need_closed_aux = edge_key

                edge_needed_vars = []
                edge_needed_settings = []

                for nor, noc in ((fr, fc),) + need_open_path + ((tr, tc),) + need_open_aux:
                    open_out_var = open_vars[(nor, noc)]
                    edge_needed_vars.append(open_out_var)
                    edge_needed_settings.append(True)

                for ncr, ncc in need_closed_path + need_closed_aux:
                    open_out_var = open_vars[(ncr, ncc)]
                    edge_needed_vars.append(open_out_var)
                    edge_needed_settings.append(False)

                conj_needed = gen._solver.make_conj(edge_needed_vars, edge_needed_settings)
                gen._solver.cnstr_implies_disj(conj_needed, True, [edge_var], True, None)
                gen._solver.cnstr_implies_disj(conj_needed, False, [edge_var], False, None)


            def find_layer_var_for(_vars_sl_node, _state, _layer, _rr, _cc):
                while _layer >= 0:
                    _key = (_state, _layer, _rr, _cc)
                    if _key in _vars_sl_node:
                        return _vars_sl_node[_key], _layer
                    _layer = _layer - 1
                return var_false, None

            src_tile_vars = {}
            dst_tile_vars = {}
            for rr, cc in rgraph.nodes:
                game = gen._game_level[rr][cc]
                src_tile = gen._reach_junction_info[reach_connect_info.src].game_to_junction_tile[game]
                dst_tile = gen._reach_junction_info[reach_connect_info.dst].game_to_junction_tile[game]

                src_tile_vars[(rr, cc)] = gen._tile_var(rr, cc, src_tile) if gen._tile_has_var(rr, cc, src_tile) else None
                dst_tile_vars[(rr, cc)] = gen._tile_var(rr, cc, dst_tile) if gen._tile_has_var(rr, cc, dst_tile) else None

            def setup_reach_problem(_edge_cost, _layers):
                _state_possible = {}

                _state_layer_possible = { start_key: None }
                _state_layer_queue = [start_key]

                while len(_state_layer_queue) > 0:
                    (_state, _layer), _state_layer_queue = _state_layer_queue[0], _state_layer_queue[1:]

                    _state_possible[_state] = None

                    for _edge_key in rgraph.edges:
                        _layer_dst = _layer + _edge_cost(_edge_key)
                        if _layer_dst >= _layers:
                            continue
                        _state_dst = state_next_func(_state, _edge_key)

                        _possible_key = (_state_dst, _layer_dst)
                        if _possible_key not in _state_layer_possible:
                            _state_layer_possible[_possible_key] = None
                            _state_layer_queue.append(_possible_key)

                _state_edges_incoming = {}

                for _state, _layer in _state_layer_possible.keys():
                    for _edge_key in rgraph.edges:
                        _fr, _fc, _tr, _tc, _pwtr, _pwtc, _need_open_path, _need_open_aux, _need_closed_path, _need_closed_aux = _edge_key

                        _layer_dst = _layer + _edge_cost(_edge_key)
                        if _layer_dst >= _layers:
                            continue
                        _state_dst = state_next_func(_state, _edge_key)

                        _incoming_key = (_state_dst, _layer_dst, _fr, _fc, _tr, _tc)
                        if _incoming_key not in _state_edges_incoming:
                            _state_edges_incoming[_incoming_key] = []
                        _state_edges_incoming[_incoming_key].append((_state, _layer))

                _vars_sl_node = {}

                for _rr, _cc in rgraph.nodes:
                    for _state, _layer in _state_layer_possible.keys():
                        _vars_sl_node[(_state, _layer, _rr, _cc)] = gen._solver.make_var()


                for _rr, _cc in rgraph.nodes:
                    src_tile_var = src_tile_vars[(_rr, _cc)]

                    for _state, _layer in _state_layer_possible.keys():
                        _node_var = _vars_sl_node[(_state, _layer, _rr, _cc)]

                        if _layer == 0:
                            # src is reachable in initial state/layer, others are not
                            util_common.check(_state == state_start, 'state_start')
                            if src_tile_var is not None:
                                gen._solver.cnstr_implies_disj(src_tile_var, True, [_node_var], True, None)
                                gen._solver.cnstr_implies_disj(src_tile_var, False, [_node_var], False, None)
                            else:
                                gen._solver.cnstr_count([_node_var], False, 1, 1, None)

                        else:
                            # in other layers, previously reachable or any incoming reachable edge means reachable, otherwise, not
                            _prev_node_var, _prev_node_var_layer = find_layer_var_for(_vars_sl_node, _state, _layer - 1, _rr, _cc)

                            _in_vvs = []
                            for _edge_key in rgraph.in_edges[(_rr, _cc)]:
                                _fr, _fc, _tr, _tc, _pwtr, _pwtc, _need_open_path, _need_open_aux, _need_closed_path, _need_closed_aux = _edge_key
                                _key = (_state, _layer, _fr, _fc, _tr, _tc)
                                if _key not in _state_edges_incoming:
                                    continue
                                _in_node_vars = [_vars_sl_node[(_in_state, _in_layer, _fr, _fc)] for _in_state, _in_layer in _state_edges_incoming[_key]]
                                _in_node_var, _ = util_solvers.make_disj_cache(gen._solver, {}, _in_node_vars, True)
                                _in_edge_var = reach_vars_edge[_edge_key]
                                _in_var = gen._solver.make_conj([_in_node_var, _in_edge_var], True) # TODO?: prevent moving out of dst?
                                _in_vvs.append(_in_var)

                            _conj_not_prev_or_in = gen._solver.make_conj([_prev_node_var] + _in_vvs, False)
                            gen._solver.cnstr_implies_disj(_conj_not_prev_or_in, True, [_node_var], False, None)
                            gen._solver.cnstr_implies_disj(_conj_not_prev_or_in, False, [_node_var], True, None)

                return _state_possible, _state_layer_possible, _state_edges_incoming, _vars_sl_node


            if reach_layers != 0:
                util_common.check(state_reachable_func is not None, 'reach_layers')
                pr_state_possible, pr_state_layer_possible, pr_state_edges_incoming, pr_node_vars = setup_reach_problem(reach_edge_cost, reach_layers)

                state_reachable = {}
                state_blocked = {}

                for state in pr_state_possible:
                    if state_reachable_func(state):
                        util_common.check(state not in state_blocked, 'state')
                        state_reachable[state] = None
                    else:
                        util_common.check(state not in state_reachable, 'state')
                        state_blocked[state] = None

                util_common.check(len(state_reachable) > 0, 'no reachable states')

                var_disj_reachable = {}
                var_disj_blocked = {}

                for rr, cc in rgraph.nodes:
                    for layer in range(reach_layers):
                        vars_reachable = []
                        vars_blocked = []
                        for state in pr_state_possible:
                            state_var, state_var_layer = find_layer_var_for(pr_node_vars, state, layer, rr, cc)
                            if state_var_layer is not None:
                                if state in state_reachable:
                                    vars_reachable.append(state_var)
                                if state in state_blocked:
                                    vars_blocked.append(state_var)
                        var_disj_reachable[(layer, rr, cc)], _ = util_solvers.make_disj_cache(gen._solver, {}, vars_reachable, True) if len(vars_reachable) > 0 else (var_false, False)
                        var_disj_blocked[(layer, rr, cc)], _ = util_solvers.make_disj_cache(gen._solver, {}, vars_blocked, True) if len(vars_blocked) > 0 else (var_false, False)

                for rr, cc in rgraph.nodes:
                    dst_tile_var = dst_tile_vars[(rr, cc)]

                    if dst_tile_var is not None:
                        state_dst_reachable_any_vars = []

                        for state, layer in pr_state_layer_possible.keys():
                            if state in state_reachable:
                                node_var = pr_node_vars[(state, layer, rr, cc)]
                                any_reach_prev = var_disj_reachable[(layer - 1, rr, cc)] if layer > 0 else var_false
                                to_block_curr = var_disj_blocked[(layer, rr, cc)]

                                # in state where dst must be reachable in some layer
                                state_dst_reachable_any_vars.append(node_var)

                                # in state where dst must not be reachable in same layers as blocked states, unless it was previously reachable
                                gen._solver.cnstr_implies_disj(gen._solver.make_conj([dst_tile_var, node_var, any_reach_prev], [True, True, False]), True, [to_block_curr], False, None)

                        gen._solver.cnstr_implies_disj(dst_tile_var, True, state_dst_reachable_any_vars, True, None)


            if unreach_layers != 0:
                util_common.check(state_unreachable_func is not None, 'unreach_layers')
                pr_state_possible, pr_state_layer_possible, pr_state_edges_incoming, pr_node_vars = setup_reach_problem(lambda _edge_key: 1, unreach_layers)

                state_unreachable = {}

                for state in pr_state_possible:
                    if state_unreachable_func(state):
                        state_unreachable[state] = None

                util_common.check(len(state_unreachable) > 0, 'no unreachable states')

                for rr, cc in rgraph.nodes:
                    dst_tile_var = dst_tile_vars[(rr, cc)]

                    for state in pr_state_possible:
                        final_node_var1, final_node_var1_layer = find_layer_var_for(pr_node_vars, state, unreach_layers - 1, rr, cc)
                        final_node_var2, final_node_var2_layer = find_layer_var_for(pr_node_vars, state, unreach_layers - 2, rr, cc)

                        # saturation check
                        gen._solver.cnstr_implies_disj(final_node_var1, True, [final_node_var2], True, None)
                        gen._solver.cnstr_implies_disj(final_node_var1, False, [final_node_var2], False, None)

                        # unreachable at dst
                        if dst_tile_var is not None:
                            if state in state_unreachable:
                                gen._solver.cnstr_implies_disj(dst_tile_var, True, [final_node_var1], False, None)



class ResultConstraint(CustomConstraint):
    def __init__(self, out_result, which, rlo, clo, rhi, chi, roff, coff, weight):
        self._out_result = out_result
        self._which = which
        self._rlo = rlo
        self._clo = clo
        self._rhi = rhi
        self._chi = chi
        self._roff = roff
        self._coff = coff
        self._weight = weight

    def add(self, gen):
        print('add custom result constraint', self._weight)

        util_common.check(gen.get_num_reach_connect() == 1, 'only supports one reach move')

        connect_index = 0

        util_common.check(not gen.is_unreachable(connect_index), 'reach move is unreachable')

        util_common.check(0 <= self._rlo, 'size')
        util_common.check(0 <= self._clo, 'size')
        util_common.check(self._rlo < self._rhi, 'size')
        util_common.check(self._clo < self._chi, 'size')
        util_common.check(self._rhi <= len(self._out_result.tile_level), 'size')
        util_common.check(self._chi <= len(self._out_result.tile_level[0]), 'size')

        util_common.check(0 <= self._roff, 'size')
        util_common.check(0 <= self._coff, 'size')
        util_common.check(self._rhi - self._rlo + self._roff <= gen.get_rows(), 'size')
        util_common.check(self._chi - self._clo + self._coff <= gen.get_cols(), 'size')

        # T: tiles
        # Po: path - on path
        # Pa: path - on and off path
        # Ro: reverse path - on path
        # Ra: reverse path - on and off path
        util_common.check(self._which in ['T', 'Po', 'Pa', 'Ro', 'Ra', 'TPo', 'TPa', 'TRo', 'TRa'], 'which')

        rinto = -self._rlo + self._roff
        cinto = -self._clo + self._coff

        gen.append_extra_meta([util_common.meta_rect('custom', [(self._rlo + rinto, self._clo + cinto, self._rhi + rinto, self._chi + cinto)])])

        if 'T' in self._which:
            for rr in range(self._rlo, self._rhi):
                for cc in range(self._clo, self._chi):
                    gen.add_constraint_tile_counts([(rr + rinto, cc + cinto, [self._out_result.tile_level[rr][cc]])], 1, 1, self._weight)

        if 'Po' in self._which or 'Pa' in self._which or 'Ro' in self._which or 'Ra' in self._which:
            util_common.check(self._out_result.reach_info is not None, 'reach_info')
            util_common.check(len(self._out_result.reach_info) == 1, 'reach_info')

            path_all = ('Pa' in self._which) or ('Ra' in self._which)
            path_reverse = ('Ro' in self._which) or ('Ra' in self._which)

            path_edges = self._out_result.reach_info[connect_index].path_edges
            if path_reverse:
                path_edges = reversed(path_edges)

            path_cache = {}
            path_start_found, path_start = False, self._out_result.reach_info[connect_index].path_locations[0]
            path_goal_found, path_goal = False, self._out_result.reach_info[connect_index].path_locations[-1]
            for (fr, fc, pwtr, pwtc) in path_edges:
                tr = pwtr % len(self._out_result.tile_level)
                tc = pwtc % len(self._out_result.tile_level[0])

                f_in = self._rlo <= fr and fr < self._rhi and self._clo <= fc and fc < self._chi
                t_in = self._rlo <= tr and tr < self._rhi and self._clo <= tc and tc < self._chi

                if path_reverse and t_in and (tr, tc) == path_goal:
                    path_goal_found = True
                if not path_reverse and f_in and (fr, fc) == path_start:
                    path_start_found = True

                if f_in and t_in:
                    cfr = fr + rinto
                    cfc = fc + cinto
                    ctr = tr + rinto
                    ctc = tc + cinto
                    cpwtr = pwtr + rinto
                    cpwtc = pwtc + cinto
                    path_cache[(cfr, cfc, ctr, ctc, cpwtr, cpwtc)] = None
                elif fr < 0 or fr >= len(self._out_result.tile_level):
                    # skip duplicate path edges coming in after a wrap
                    continue
                elif fc < 0 or fc >= len(self._out_result.tile_level[0]):
                    # skip duplicate path edges coming in after a wrap
                    continue
                else:
                    break

                if not path_reverse and t_in and (tr, tc) == path_goal:
                    path_goal_found = True
                if path_reverse and f_in and (fr, fc) == path_start:
                    path_start_found = True

            reach_edges = gen.reachability_edges(connect_index)
            util_common.check(reach_edges is not None, 'reach_edges')

            for cfr, cfc, ctr, ctc, cpwtr, cpwtc in reach_edges:
                on_path = (cfr, cfc, ctr, ctc, cpwtr, cpwtc) in path_cache
                add_cnstr = on_path or path_all
                if add_cnstr:
                    gen.add_constraint_reach_edge(connect_index, cfr, cfc, ctr, ctc, cpwtr, cpwtc, on_path, self._weight)

            for rr in range(self._rlo, self._rhi):
                for cc in range(self._clo, self._chi):
                    if path_start_found or path_all:
                        gen.add_constraint_start(rr + rinto, cc + cinto, (rr, cc) == path_start, self._weight)
                    if path_goal_found or path_all:
                        gen.add_constraint_goal(rr + rinto, cc + cinto, (rr, cc) == path_goal, self._weight)
