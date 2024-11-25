import argparse, math, pickle, pprint, random, sys, time
import util_common, util_solvers



class Generator:
    class ConnectItem:
        def __init__(self):
            self.connect_info = None
            self.vars_node = None
            self.vars_edge = None
            self.out_edges = None

    def __init__(self, solver, randomize, rows, cols, scheme_info, tag_level, game_level):
        super().__init__()

        self._solver = solver
        self._rng = random.Random(randomize) if randomize else None

        self._extra_meta = []

        self._rows = rows
        self._cols = cols

        self._scheme_info = scheme_info
        self._tag_level = tag_level
        self._game_level = game_level

        self._vars_rc_t = {}
        self._vars_pattern = {}

        self._var_void_true = self._solver.make_var()
        self._solver.cnstr_count([self._var_void_true], True, 1, 1, None)

        self._reach_junction_info = {}
        self._reach_connect_item = []

    def _tile_var(self, rr, cc, tile):
        if (rr, cc) in self._vars_rc_t:
            util_common.check(tile != util_common.VOID_TILE, 'void tile')
            return self._vars_rc_t[(rr, cc)][tile]
        else:
            util_common.check(tile == util_common.VOID_TILE, 'void tile')
            return self._var_void_true

    def _tile_has_var(self, rr, cc, tile):
        if (rr, cc) in self._vars_rc_t:
            return tile in self._vars_rc_t[(rr, cc)]
        else:
            return tile == util_common.VOID_TILE

    def _pattern_var(self, pattern):
        util_common.check(len(pattern) > 0, 'empty pattern')

        key = tuple(sorted(set(pattern)))

        if key not in self._vars_pattern:
            self._vars_pattern[key] = self._solver.make_conj([self._tile_var(pr, pc, ptile) for pr, pc, ptile in pattern], True)

        return self._vars_pattern[key]

    def get_num_reach_connect(self):
        return len(self._reach_connect_item)

    def is_unreachable(self, connect_index):
        return self._reach_connect_item[connect_index].connect_info.unreachable

    def get_rows(self):
        return self._rows

    def get_cols(self):
        return self._cols

    def get_scheme_info(self):
        return self._scheme_info

    def append_extra_meta(self, meta):
        self._extra_meta += meta

    def add_rules_tiles(self):
        print('add tile constraints')

        row_order = list(range(self._rows))
        col_order = list(range(self._cols))

        if self._rng:
            self._rng.shuffle(row_order)
            self._rng.shuffle(col_order)

        for rr in row_order:
            for cc in col_order:
                tag = self._tag_level[rr][cc]
                game = self._game_level[rr][cc]

                if tag == util_common.VOID_TEXT:
                    continue

                tiles = list(self._scheme_info.game_to_tag_to_tiles[game][tag].keys())
                util_common.check(util_common.VOID_TILE not in tiles, 'void tile')

                if self._rng:
                    self._rng.shuffle(tiles)

                self._vars_rc_t[(rr, cc)] = {}
                for tile in tiles:
                    self._vars_rc_t[(rr, cc)][tile] = self._solver.make_var()

                vvs = list(self._vars_rc_t[(rr, cc)].values())

                self._solver.cnstr_count(vvs, True, 1, 1, None)

    def add_rules_patterns(self, weight_patterns):
        print('add pattern constraints', weight_patterns)

        util_common.check(weight_patterns is None or weight_patterns > 0, 'weight')

        def add_tile_patterns(_pattern_in, _pattern_out_list):
            _pattern_in_var = self._pattern_var(_pattern_in)

            if len(_pattern_out_list) == 0:
                self._solver.cnstr_count([_pattern_in_var], True, 0, 0, weight_patterns)

            else:
                _pattern_out_vars = [self._pattern_var(_pattern_out) for _pattern_out in _pattern_out_list]
                self._solver.cnstr_implies_disj(_pattern_in_var, True, _pattern_out_vars, True, weight_patterns)

        def add_pattern_options(_patterns):
            _pattern_vars = [self._pattern_var(_pattern) for _pattern in _patterns]
            self._solver.cnstr_count(_pattern_vars, True, 1, len(_pattern_vars), weight_patterns)

        if self._scheme_info.pattern_info.stride_rows == 0:
            util_common.check(0 == self._scheme_info.pattern_info.dr_lo and self._rows == self._scheme_info.pattern_info.dr_hi + 1, 'rows do not stride and row count does not start at 0 or does not match')
        if self._scheme_info.pattern_info.stride_cols == 0:
            util_common.check(0 == self._scheme_info.pattern_info.dc_lo and self._cols == self._scheme_info.pattern_info.dc_hi + 1, 'cols do not stride and col count does not start at 0 or does not match')

        row_range = range(-self._scheme_info.pattern_info.dr_hi, self._rows - self._scheme_info.pattern_info.dr_lo, self._scheme_info.pattern_info.stride_rows) if self._scheme_info.pattern_info.stride_rows else [0]
        col_range = range(-self._scheme_info.pattern_info.dc_hi, self._cols - self._scheme_info.pattern_info.dc_lo, self._scheme_info.pattern_info.stride_cols) if self._scheme_info.pattern_info.stride_cols else [0]

        def pattern_inst(_pattern_template, _pattern):
            _inst = []
            for (_dr, _dc), _ptile in zip(_pattern_template, _pattern):
                _nr = rr + _dr
                _nc = cc + _dc

                _nbr_tag = util_common.VOID_TEXT if (_nr <= -1 or _nr >= self._rows or _nc <= -1 or _nc >= self._cols) else self._tag_level[_nr][_nc]

                if _nbr_tag == util_common.VOID_TEXT:
                    if _ptile != util_common.VOID_TILE:
                        return None
                else:
                    if _ptile not in self._vars_rc_t[(_nr, _nc)]:
                        return None

                _inst.append((_nr, _nc, _ptile))
            return tuple(_inst)

        for rr in row_range:
            for cc in col_range:
                game = self._game_level[max(0, min(self._rows - 1, rr))][max(0, min(self._cols - 1, cc))]

                game_patterns_info = self._scheme_info.pattern_info.game_to_patterns[game]

                if game_patterns_info is None:
                    continue

                for pattern_template_in in game_patterns_info:
                    all_pattern_in_inst = []

                    for pattern_in in game_patterns_info[pattern_template_in]:
                        pattern_inst_in = pattern_inst(pattern_template_in, pattern_in)
                        if pattern_inst_in is None:
                            continue

                        all_pattern_in_inst.append(pattern_inst_in)

                        for pattern_template_out in game_patterns_info[pattern_template_in][pattern_in]:
                            if pattern_template_out is None:
                                continue

                            pattern_list_out = []
                            for pattern_out in game_patterns_info[pattern_template_in][pattern_in][pattern_template_out]:
                                pattern_inst_out = pattern_inst(pattern_template_out, pattern_out)
                                if pattern_inst_out is not None:
                                    pattern_list_out.append(pattern_inst_out)

                            add_tile_patterns(pattern_inst_in, pattern_list_out)

                    util_common.check(len(all_pattern_in_inst) > 0, 'no inst in patterns')
                    add_pattern_options(all_pattern_in_inst)

    def add_rules_counts(self, use_out_text_groups, counts_scale_lo, counts_scale_hi, weight_counts):
        print('add count constraints', weight_counts)

        util_common.check(weight_counts is None or weight_counts > 0, 'weight')

        print('using output text groups' if use_out_text_groups else 'using single tile groups')

        def add_counts(_rr_lo, _rr_hi, _cc_lo, _cc_hi, _count_game_to_tag_to_tiles):
            for _game, _count_tag_to_tiles in _count_game_to_tag_to_tiles.items():
                for _tag in _count_tag_to_tiles:
                    _rcs = []
                    for _rr in range(_rr_lo, _rr_hi):
                        for _cc in range(_cc_lo, _cc_hi):
                            if self._game_level[_rr][_cc] == _game and self._tag_level[_rr][_cc] == _tag:
                                _rcs.append((_rr, _cc))

                    if len(_rcs) == 0:
                        continue

                    if use_out_text_groups:
                        util_common.check(self._scheme_info.tileset.tile_to_text is not None, 'tile groups out text')

                        _inv = {}
                        for _tile in _count_tag_to_tiles[_game][_tag]:
                            _out_text = self._scheme_info.tileset.tile_to_text[_tile]

                            # no counts on start/goal tiles
                            if _out_text == util_common.START_TEXT or _out_text == util_common.GOAL_TEXT:
                                continue

                            if _out_text not in _inv:
                                _inv[_out_text] = []
                            _inv[_out_text].append(_tile)

                        _tile_groups = [(_out_text, _tiles) for _out_text, _tiles in _inv.items()]
                    else:
                        _tile_groups = [(None, [_tile]) for _tile in _count_tag_to_tiles[_tag]]

                    if len(_tile_groups) <= 1:
                        continue

                    for _out_text, _tiles in _tile_groups:
                        _wt = 0.0
                        for _tile in _tiles:
                            _wt += _count_tag_to_tiles[_tag][_tile]

                        _lo = max(0,         math.floor(counts_scale_lo * len(_rcs) * _wt))
                        _hi = min(len(_rcs), math.ceil (counts_scale_hi * len(_rcs) * _wt))
                        self.add_constraint_tile_counts([(_rr, _cc, _tiles) for _rr, _cc in _rcs], _lo, _hi, weight_counts)

        for rr_divs in range(self._scheme_info.count_info.divs_size[0]):
            for cc_divs in range(self._scheme_info.count_info.divs_size[1]):
                rr_lo = self._rows * (rr_divs + 0) // self._scheme_info.count_info.divs_size[0]
                rr_hi = self._rows * (rr_divs + 1) // self._scheme_info.count_info.divs_size[0]
                cc_lo = self._cols * (cc_divs + 0) // self._scheme_info.count_info.divs_size[1]
                cc_hi = self._cols * (cc_divs + 1) // self._scheme_info.count_info.divs_size[1]

                add_counts(rr_lo, rr_hi, cc_lo, cc_hi, self._scheme_info.count_info.divs_to_game_to_tag_to_tile_count[(rr_divs, cc_divs)])

    def add_constraint_tile_counts(self, rcts, lo, hi, weight_counts):
        util_common.check(lo <= hi, 'counts')
        util_common.check(weight_counts is None or weight_counts > 0, 'weight')

        vvs = [self._tile_var(rr, cc, tile) for rr, cc, tiles in rcts for tile in tiles]

        self._solver.cnstr_count(vvs, True, lo, hi, weight_counts)

    def reachability_edges(self, connect_index):
        edges = {}
        for edge_key in self._reach_connect_item[connect_index].vars_edge:
            fr, fc, tr, tc, pwtr, pwtc, need_open_path, need_open_aux, need_closed_path, need_closed_aux = edge_key
            edges[(fr, fc, tr, tc, pwtr, pwtc)] = None

        return edges

    def add_constraint_reach_edge(self, connect_index, cfr, cfc, ctr, ctc, cpwtr, cpwtc, on_path, weight):
        edge_vars = []
        for edge_key in self._reach_connect_item[connect_index].out_edges[(cfr, cfc)]:
            fr, fc, tr, tc, pwtr, pwtc, need_open_path, need_open_aux, need_closed_path, need_closed_aux = edge_key
            if (cfr, cfc, ctr, ctc, cpwtr, cpwtc) == (fr, fc, tr, tc, pwtr, pwtc):
                edge_vars.append(self._reach_connect_item[connect_index].vars_edge[edge_key])

        edge_count = 1 if on_path else 0

        self._solver.cnstr_count(edge_vars, True, edge_count, edge_count, weight)

    def add_constraint_start(self, rr, cc, on_path, weight):
        game = self._game_level[rr][cc]
        start_tile = self._reach_junction_info[util_common.START_TEXT].game_to_junction_tile[game]
        vv = self._tile_var(rr, cc, start_tile)
        self._solver.cnstr_count([vv], on_path, 1, 1, weight)

    def add_constraint_goal(self, rr, cc, on_path, weight):
        game = self._game_level[rr][cc]
        goal_tile = self._reach_junction_info[util_common.GOAL_TEXT].game_to_junction_tile[game]
        vv = self._tile_var(rr, cc, goal_tile)
        self._solver.cnstr_count([vv], on_path, 1, 1, weight)

    def add_rules_reachability_junction(self, reach_junction_info):
        print('add reachability junction constraints')

        util_common.check(reach_junction_info is not None, 'must have reach_junction_info')
        util_common.check(reach_junction_info.text not in self._reach_junction_info, 'cannot add multiple reach_junction_info with same text')

        self._reach_junction_info[reach_junction_info.text] = reach_junction_info

        possible_vvs = []
        impossible_vvs = []
        for (rr, cc) in self._vars_rc_t:
            game = self._game_level[rr][cc]
            game_junction_tile = reach_junction_info.game_to_junction_tile[game]

            if self._tile_has_var(rr, cc, game_junction_tile):
                vv = self._tile_var(rr, cc, game_junction_tile)
                if (rr, cc) in reach_junction_info.rcs:
                    possible_vvs.append(vv)
                else:
                    impossible_vvs.append(vv)

        # exactly one junction in possible tiles
        if len(possible_vvs) > 0:
            self._solver.cnstr_count(possible_vvs, True, 1, 1, None)

        # no junction in impossible tiles
        if len(impossible_vvs) > 0:
            self._solver.cnstr_count(impossible_vvs, True, 0, 0, None)

    def add_rules_reachability_connect(self, reach_connect_info):
        print('add reachability connect constraints')

        util_common.check(reach_connect_info is not None, 'must have reach_connect_info')
        util_common.check(reach_connect_info.src in self._reach_junction_info, 'cannot add reach move without source junction')
        util_common.check(reach_connect_info.dst in self._reach_junction_info, 'cannot add reach move without destination junction')

        nodes = []
        in_edges = {}
        out_edges = {}

        reach_vars_node = {}
        reach_vars_edge = {}

        connect_item = Generator.ConnectItem()
        connect_item.connect_info = reach_connect_info
        connect_item.vars_node = reach_vars_node
        connect_item.vars_edge = reach_vars_edge
        connect_item.out_edges = out_edges
        self._reach_connect_item.append(connect_item)

        for rr, cc in self._vars_rc_t:
            util_common.check(not self._tile_has_var(rr, cc, util_common.VOID_TILE), 'void tile')

            node = (rr, cc)
            nodes.append(node)
            out_edges[node] = {}
            in_edges[node] = {}

            reach_vars_node[(rr, cc)] = self._solver.make_var()

        for rr, cc in nodes:
            game = self._game_level[rr][cc]
            move_info = reach_connect_info.game_to_move_info[game]

            edge_keys = util_common.get_edge_keys_from((rr, cc), self._rows, self._cols, move_info, nodes, {}, {}, {})

            for edge_key in edge_keys:
                fr, fc, tr, tc, pwtr, pwtc, need_open_path, need_open_aux, need_closed_path, need_closed_aux = edge_key
                util_common.check(fr == rr and fc == cc, 'edge')

                out_edges[(fr, fc)][edge_key] = None
                in_edges[(tr, tc)][edge_key] = None

                if edge_key not in reach_vars_edge:
                    reach_vars_edge[edge_key] = self._solver.make_var()

        open_vars = {}
        for rr, cc in nodes:
            game = self._game_level[rr][cc]
            src_tile = self._reach_junction_info[reach_connect_info.src].game_to_junction_tile[game]
            dst_tile = self._reach_junction_info[reach_connect_info.dst].game_to_junction_tile[game]
            move_info = reach_connect_info.game_to_move_info[game]
            open_tiles = reach_connect_info.game_to_open_tiles[game]

            # TODO: treat src and dst tiles separately from open tiles?
            all_open_tiles = open_tiles + [src_tile, dst_tile]

            if len(all_open_tiles) == 1:
                open_var = self._tile_var(rr, cc, all_open_tiles[0])
            else:
                open_var = self._solver.make_var()
                open_tile_vvs = [self._tile_var(rr, cc, all_open_tile) for all_open_tile in all_open_tiles]
                for open_tile_vv in open_tile_vvs:
                    self._solver.cnstr_implies_disj(open_tile_vv, True, [open_var], True, None)
                self._solver.cnstr_implies_disj(open_var, True, open_tile_vvs, True, None)
            open_vars[(rr, cc)] = open_var

        if reach_connect_info.unreachable:
            for rr, cc in nodes:
                game = self._game_level[rr][cc]
                src_tile = self._reach_junction_info[reach_connect_info.src].game_to_junction_tile[game]
                dst_tile = self._reach_junction_info[reach_connect_info.dst].game_to_junction_tile[game]
                move_info = reach_connect_info.game_to_move_info[game]

                reach_node_var = reach_vars_node[(rr, cc)]
                node_open_var = open_vars[(rr, cc)]

                # node reachable and outgoing edge means outgoing edge reachable
                for edge_key in out_edges[(rr, cc)]:
                    reach_out_edge_var = reach_vars_edge[edge_key]

                    fr, fc, tr, tc, pwtr, pwtc, need_open_path, need_open_aux, need_closed_path, need_closed_aux = edge_key
                    util_common.check((fr, fc) == (rr, cc), 'edge')

                    out_vvs = []
                    out_settings = []

                    out_vvs.append(reach_node_var)
                    out_settings.append(True)

                    for nor, noc in need_open_path + ((tr, tc),) + need_open_aux:
                        open_out_var = open_vars[(nor, noc)]
                        out_vvs.append(open_out_var)
                        out_settings.append(True)

                    for ncr, ncc in need_closed_path + need_closed_aux:
                        open_out_var = open_vars[(ncr, ncc)]
                        out_vvs.append(open_out_var)
                        out_settings.append(False)

                    out_conj = self._solver.make_conj(out_vvs, out_settings)
                    self._solver.cnstr_implies_disj(out_conj, True, [reach_out_edge_var], True, None)

                # any incoming edge reachable and open means node reachable
                for edge_key in in_edges[(rr, cc)]:
                    reach_in_edge_var = reach_vars_edge[edge_key]
                    in_conj = self._solver.make_conj([node_open_var, reach_in_edge_var], True)

                    self._solver.cnstr_implies_disj(in_conj, True, [reach_node_var], True, None) # reach_in_edge_var -> reach_node_var

                # not open means not reachable
                self._solver.cnstr_implies_disj(node_open_var, False, [reach_node_var], False, None) # !node_open_var -> !reach_node_var

                # src handling
                if self._tile_has_var(rr, cc, src_tile):
                    src_tile_var = self._tile_var(rr, cc, src_tile)

                    # src must be reachable
                    self._solver.cnstr_implies_disj(src_tile_var, True, [reach_node_var], True, None) # src_tile_var -> reach_node_var

                # dst handling
                if self._tile_has_var(rr, cc, dst_tile):
                    dst_tile_var = self._tile_var(rr, cc, dst_tile)

                    # dst must be unreachable
                    self._solver.cnstr_implies_disj(dst_tile_var, True, [reach_node_var], False, None) # dst_tile_var -> !reach_node_var

        else:
            for rr, cc in nodes:
                game = self._game_level[rr][cc]
                src_tile = self._reach_junction_info[reach_connect_info.src].game_to_junction_tile[game]
                dst_tile = self._reach_junction_info[reach_connect_info.dst].game_to_junction_tile[game]
                move_info = reach_connect_info.game_to_move_info[game]

                reach_node_var = reach_vars_node[(rr, cc)]

                out_vvs = []
                for edge_key in out_edges[(rr, cc)]:
                    reach_out_edge_var = reach_vars_edge[edge_key]
                    out_vvs.append(reach_out_edge_var)

                    fr, fc, tr, tc, pwtr, pwtc, need_open_path, need_open_aux, need_closed_path, need_closed_aux = edge_key
                    util_common.check((fr, fc) == (rr, cc), 'edge')

                    self._solver.cnstr_implies_disj(reach_node_var, False, [reach_out_edge_var], False, None) # !reach_node_var -> !reach_out_edge_var

                    for nor, noc in need_open_path + ((tr, tc),) + need_open_aux:
                        open_out_var = open_vars[(nor, noc)]
                        self._solver.cnstr_implies_disj(open_out_var, False, [reach_out_edge_var], False, None) # !open_out_var -> !reach_out_edge_var

                    for ncr, ncc in need_closed_path + need_closed_aux:
                        open_out_var = open_vars[(ncr, ncc)]
                        self._solver.cnstr_implies_disj(open_out_var, True, [reach_out_edge_var], False, None) # open_out_var -> !reach_out_edge_var

                in_vvs = []
                for edge_key in in_edges[(rr, cc)]:
                    reach_in_edge_var = reach_vars_edge[edge_key]
                    in_vvs.append(reach_in_edge_var)

                # at most 1 in edge
                if len(in_vvs) > 0:
                    self._solver.cnstr_count(in_vvs, True, 0, 1, None)

                # at most 1 out edge
                if len(out_vvs) > 0:
                    self._solver.cnstr_count(out_vvs, True, 0, 1, None)

                # src handling
                src_and_in_vvs = in_vvs

                if self._tile_has_var(rr, cc, src_tile):
                    src_tile_var = self._tile_var(rr, cc, src_tile)

                    # src must be reachable
                    self._solver.cnstr_implies_disj(src_tile_var, True, [reach_node_var], True, None) # src_tile_var -> reach_node_var

                    # src has no in edges
                    for in_vv in in_vvs:
                        self._solver.cnstr_implies_disj(src_tile_var, True, [in_vv], False, None) # ... src_tile_var -> A !in_edge

                    src_and_in_vvs = [src_tile_var] + src_and_in_vvs

                # unless it's the src, no in edges means not reachable
                conj_src_and_in_vvs = self._solver.make_conj(src_and_in_vvs, False)
                self._solver.cnstr_implies_disj(conj_src_and_in_vvs, True, [reach_node_var], False, None) # !src_tile_var & A !in_edge -> !reach_node_var

                # dst handling
                if self._tile_has_var(rr, cc, dst_tile):
                    dst_tile_var = self._tile_var(rr, cc, dst_tile)

                    # dst must be reachable
                    self._solver.cnstr_implies_disj(dst_tile_var, True, [reach_node_var], True, None) # dst_tile_var -> reach_node_var

                    # dst has no out edges
                    for out_vv in out_vvs:
                        self._solver.cnstr_implies_disj(dst_tile_var, True, [out_vv], False, None) # ... dst_tile_var -> A !in_edge

    def solve(self):
        if self._solver.solve():
            print('objective: %s' % str(self._solver.get_objective()))
            return True
        else:
            return False

    def get_result(self):
        res_info = util_common.ResultInfo()

        res_info.tileset = self._scheme_info.tileset

        res_info.solver_id = self._solver.get_solver_id_used()
        res_info.solver_objective = self._solver.get_objective()

        res_info.extra_meta += self._extra_meta

        res_info.reach_info = []
        for connect_index, connect_item in enumerate(self._reach_connect_item):
            if not connect_item.connect_info.unreachable:
                reach_info = util_common.ResultReachInfo()
                reach_info.path_edges, reach_info.path_tiles, path_edge_keys = self._get_reach_path(connect_index)
                reach_info.offpath_edges = self._get_reach_offpath_edges(connect_index, path_edge_keys)
                res_info.reach_info.append(reach_info)

        res_info.tile_level = util_common.make_grid(self._rows, self._cols, util_common.VOID_TILE)
        res_info.text_level = None
        res_info.image_level = None

        set_tiles = self._get_tiles_set()
        for rr in range(self._rows):
            for cc in range(self._cols):
                tag = self._tag_level[rr][cc]

                if (rr, cc) in set_tiles:
                    found_tile = set_tiles[(rr, cc)]
                else:
                    found_tile = util_common.VOID_TILE

                util_common.check((tag == util_common.VOID_TEXT) == (found_tile == util_common.VOID_TILE), 'void')

                res_info.tile_level[rr][cc] = found_tile

        if self._scheme_info.tileset.tile_to_text is not None:
            res_info.text_level = util_common.tile_level_to_text_level(res_info.tile_level, self._scheme_info.tileset)

        if self._scheme_info.tileset.tile_to_image is not None:
            res_info.image_level = util_common.tile_level_to_image_level(res_info.tile_level, self._scheme_info.tileset)

        return res_info

    def print_reach_internal(self):
        if len(self._reach_connect_item) == 0:
            print('no reach connect')
        else:
            for connect_index, connect_item in enumerate(self._reach_connect_item):
                src = connect_item.connect_info.src
                dst = connect_item.connect_info.dst
                unreachable = connect_item.connect_info.unreachable
                if unreachable:
                    path_tiles = None
                else:
                    _, path_tiles, _ = self._get_reach_path(connect_index)

                print(src, 'to', dst, 'unreachable' if unreachable else 'reachable')

                for rr in range(self._rows):
                    row = ''
                    for cc in range(self._cols):
                        if unreachable:
                            if self._solver.get_var(connect_item.vars_node[(rr, cc)]):
                                row = row + 'o'
                            else:
                                row = row + '.'
                        else:
                            if self._solver.get_var(connect_item.vars_node[(rr, cc)]):
                                if (rr, cc) in path_tiles:
                                    row = row + '*'
                                else:
                                    row = row + 'o'
                            else:
                                row = row + '.'
                    print(row)

    def _get_tiles_set(self):
        tiles = {}

        for rr, cc in self._vars_rc_t:
            tiles[(rr, cc)] = util_solvers.get_one_set(self._solver, self._vars_rc_t[(rr, cc)])

        return tiles

    def _get_reach_path(self, connect_index):
        reach_connect_info = self._reach_connect_item[connect_index].connect_info
        reach_vars_node = self._reach_connect_item[connect_index].vars_node
        reach_vars_edge = self._reach_connect_item[connect_index].vars_edge
        reach_out_edges = self._reach_connect_item[connect_index].out_edges

        node_path = []
        tile_path = []
        key_path = []

        src_rc, dst_rc = None, None
        for (rr, cc) in self._vars_rc_t:
            game = self._game_level[rr][cc]
            src_tile = self._reach_junction_info[reach_connect_info.src].game_to_junction_tile[game]
            dst_tile = self._reach_junction_info[reach_connect_info.dst].game_to_junction_tile[game]

            if src_tile in self._vars_rc_t[(rr, cc)] and self._solver.get_var(self._tile_var(rr, cc, src_tile)):
                src_rc = (rr, cc)
            if dst_tile in self._vars_rc_t[(rr, cc)] and self._solver.get_var(self._tile_var(rr, cc, dst_tile)):
                dst_rc = (rr, cc)

        util_common.check(src_rc is not None, 'no src')
        util_common.check(dst_rc is not None, 'no dst')

        tile_path.append(src_rc)

        current_node = src_rc

        while current_node:
            rr, cc = current_node

            current_reachable = self._solver.get_var(reach_vars_node[(rr, cc)])
            util_common.check(current_reachable, 'current node not reachable')

            next_node = None
            for edge_key in reach_out_edges[(rr, cc)]:
                fr, fc, tr, tc, pwtr, pwtc, need_open_path, need_open_aux, need_closed_path, need_closed_aux = edge_key
                util_common.check(fr == rr and fc == cc, 'edge')

                out_reachable = self._solver.get_var(reach_vars_edge[edge_key])
                if out_reachable:
                    util_common.check(next_node is None, 'multiple out edges')

                    for nr, nc in need_closed_path:
                        tile_path.append((nr, nc))
                    for nr, nc in need_open_path:
                        tile_path.append((nr, nc))
                    tile_path.append((tr, tc))

                    node_path.append(util_common.get_path_edge(fr, fc, tr, tc, pwtr, pwtc))

                    key_path.append(edge_key)

                    next_node = (tr, tc)

            util_common.check(next_node is not None or current_node == dst_rc, 'path does not end at dst')

            current_node = next_node

        for (ra, ca), (rb, cb) in zip(tile_path, tile_path[1:]):
            game = self._game_level[ra][ca]
            move_info = reach_connect_info.game_to_move_info[game]

            if move_info.wrap_rows:
                if ra > 1 + rb:
                    rb += self._rows
                if rb > 1 + ra:
                    ra += self._rows

            if move_info.wrap_cols:
                if ca > 1 + cb:
                    cb += self._cols
                if cb > 1 + ca:
                    ca += self._cols

            util_common.check(abs(ra - rb) + abs(ca - cb) == 1, 'path tiles')

        return node_path, tile_path, key_path

    def _get_reach_offpath_edges(self, connect_index, path_edge_keys):
        reach_vars_edge = self._reach_connect_item[connect_index].vars_edge

        edges = {}

        for edge_key in reach_vars_edge:
            edge_reachable = self._solver.get_var(reach_vars_edge[edge_key])
            if edge_reachable and edge_key not in path_edge_keys:
                fr, fc, tr, tc, pwtr, pwtc, need_open_path, need_open_aux, need_closed_path, need_closed_aux = edge_key
                if tr == pwtr and tc == pwtc:
                    edges[(fr, fc, tr, tc)] = None
                else:
                    edges[(fr, fc, tr, pwtc)] = None
                    edges[(fr + (tr - pwtr), fc + (tc - pwtc), tr, tc)] = None

        return list(edges.keys())
