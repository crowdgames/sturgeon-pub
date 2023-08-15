import argparse, math, pickle, pprint, random, sys, time
import solvers, util



class Generator:
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

        self._reach_info = None
        self._reach_vars_node = {}
        self._reach_vars_edge = {}
        self._reach_out_edges = None

    def _tile_var(self, rr, cc, tile):
        if (rr, cc) in self._vars_rc_t:
            util.check(tile != util.VOID_TILE, 'void tile')
            return self._vars_rc_t[(rr, cc)][tile]
        else:
            util.check(tile == util.VOID_TILE, 'void tile')
            return self._var_void_true

    def _tile_has_var(self, rr, cc, tile):
        if (rr, cc) in self._vars_rc_t:
            return tile in self._vars_rc_t[(rr, cc)]
        else:
            return tile == util.VOID_TILE

    def _pattern_var(self, pattern):
        util.check(len(pattern) > 0, 'empty pattern')

        key = tuple(sorted(set(pattern)))

        if key not in self._vars_pattern:
            self._vars_pattern[key] = self._solver.make_conj([self._tile_var(pr, pc, ptile) for pr, pc, ptile in pattern], True)

        return self._vars_pattern[key]

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

                if tag == util.VOID_TEXT:
                    continue

                tiles = list(self._scheme_info.game_to_tag_to_tiles[game][tag].keys())
                util.check(util.VOID_TILE not in tiles, 'void tile')

                if self._rng:
                    self._rng.shuffle(tiles)

                self._vars_rc_t[(rr, cc)] = {}
                for tile in tiles:
                    self._vars_rc_t[(rr, cc)][tile] = self._solver.make_var()

                vvs = list(self._vars_rc_t[(rr, cc)].values())

                self._solver.cnstr_count(vvs, True, 1, 1, None)

    def add_rules_patterns(self, weight_patterns):
        print('add pattern constraints', weight_patterns)

        util.check(weight_patterns is None or weight_patterns > 0, 'weight')

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
            util.check(0 == self._scheme_info.pattern_info.dr_lo and self._rows == self._scheme_info.pattern_info.dr_hi + 1, 'rows do not stride and row count does not start at 0 or does not match')
        if self._scheme_info.pattern_info.stride_cols == 0:
            util.check(0 == self._scheme_info.pattern_info.dc_lo and self._cols == self._scheme_info.pattern_info.dc_hi + 1, 'cols do not stride and col count does not start at 0 or does not match')

        row_range = range(-self._scheme_info.pattern_info.dr_hi, self._rows - self._scheme_info.pattern_info.dr_lo, self._scheme_info.pattern_info.stride_rows) if self._scheme_info.pattern_info.stride_rows else [0]
        col_range = range(-self._scheme_info.pattern_info.dc_hi, self._cols - self._scheme_info.pattern_info.dc_lo, self._scheme_info.pattern_info.stride_cols) if self._scheme_info.pattern_info.stride_cols else [0]

        def pattern_inst(_pattern_template, _pattern):
            _inst = []
            for (_dr, _dc), _ptile in zip(_pattern_template, _pattern):
                _nr = rr + _dr
                _nc = cc + _dc

                _nbr_tag = util.VOID_TEXT if (_nr <= -1 or _nr >= self._rows or _nc <= -1 or _nc >= self._cols) else self._tag_level[_nr][_nc]

                if _nbr_tag == util.VOID_TEXT:
                    if _ptile != util.VOID_TILE:
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

                    util.check(len(all_pattern_in_inst) > 0, 'no inst in patterns')
                    add_pattern_options(all_pattern_in_inst)

    def add_rules_counts(self, use_out_text_groups, counts_scale_lo, counts_scale_hi, weight_counts):
        print('add count constraints', weight_counts)

        util.check(weight_counts is None or weight_counts > 0, 'weight')

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
                        util.check(self._scheme_info.tileset.tile_to_text is not None, 'tile groups out text')

                        _inv = {}
                        for _tile in _count_tag_to_tiles[_game][_tag]:
                            _out_text = self._scheme_info.tileset.tile_to_text[_tile]

                            # no counts on start/goal tiles
                            if _out_text == util.START_TEXT or _out_text == util.GOAL_TEXT:
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
                        self.add_constraint_tile_counts(_rcs, _tiles, _lo, _hi, weight_counts)

        for rr_divs in range(self._scheme_info.count_info.divs_size[0]):
            for cc_divs in range(self._scheme_info.count_info.divs_size[1]):
                rr_lo = self._rows * (rr_divs + 0) // self._scheme_info.count_info.divs_size[0]
                rr_hi = self._rows * (rr_divs + 1) // self._scheme_info.count_info.divs_size[0]
                cc_lo = self._cols * (cc_divs + 0) // self._scheme_info.count_info.divs_size[1]
                cc_hi = self._cols * (cc_divs + 1) // self._scheme_info.count_info.divs_size[1]

                add_counts(rr_lo, rr_hi, cc_lo, cc_hi, self._scheme_info.count_info.divs_to_game_to_tag_to_tile_count[(rr_divs, cc_divs)])

    def add_constraint_tile_counts(self, rcs, tiles, lo, hi, weight_counts):
        util.check(lo <= hi, 'counts')
        util.check(weight_counts is None or weight_counts > 0, 'weight')

        vvs = [self._tile_var(rr, cc, tile) for rr, cc in rcs for tile in tiles]

        self._solver.cnstr_count(vvs, True, lo, hi, weight_counts)

    def reachability_edges(self):
        if self._reach_info is None:
            return None

        edges = {}
        for edge_key in self._reach_vars_edge:
            fr, fc, tr, tc, pwtc, need_open_path, need_open_aux, need_closed = edge_key
            edges[(fr, fc, tr, tc, pwtc)] = None

        return edges

    def add_constraint_reach_edge(self, cfr, cfc, ctr, ctc, cpwtc, on_path, weight):
        edge_vars = []
        for edge_key in self._reach_out_edges[(cfr, cfc)]:
            fr, fc, tr, tc, pwtc, need_open_path, need_open_aux, need_closed = edge_key
            if (cfr, cfc, ctr, ctc, cpwtc) == (fr, fc, tr, tc, pwtc):
                edge_vars.append(self._reach_vars_edge[edge_key])

        edge_count = 1 if on_path else 0

        self._solver.cnstr_count(edge_vars, True, edge_count, edge_count, weight)

    def add_constraint_start(self, rr, cc, on_path, weight):
        game = self._game_level[rr][cc]
        move_info = self._reach_info.game_to_move[game]
        vv = self._tile_var(rr, cc, move_info.start_tile)
        self._solver.cnstr_count([vv], on_path, 1, 1, weight)

    def add_constraint_goal(self, rr, cc, on_path, weight):
        game = self._game_level[rr][cc]
        move_info = self._reach_info.game_to_move[game]
        vv = self._tile_var(rr, cc, move_info.goal_tile)
        self._solver.cnstr_count([vv], on_path, 1, 1, weight)

    def add_rules_reachability(self, reach_info):
        print('add reachability constraints')

        self._reach_info = reach_info

        nodes = []
        in_edges = {}
        out_edges = {}

        possible_start_vvs, possible_goal_vvs = [], []
        impossible_start_vvs, impossible_goal_vvs = [], []
        for (rr, cc) in self._vars_rc_t:
            game = self._game_level[rr][cc]
            move_info = reach_info.game_to_move[game]

            if self._tile_has_var(rr, cc, move_info.start_tile):
                vv = self._tile_var(rr, cc, move_info.start_tile)
                if (rr, cc) in reach_info.start_rcs:
                    possible_start_vvs.append(vv)
                else:
                    impossible_start_vvs.append(vv)
            if self._tile_has_var(rr, cc, move_info.goal_tile):
                vv = self._tile_var(rr, cc, move_info.goal_tile)
                if (rr, cc) in reach_info.goal_rcs:
                    possible_goal_vvs.append(vv)
                else:
                    impossible_goal_vvs.append(vv)

        # exactly one start in possible tiles
        self._solver.cnstr_count(possible_start_vvs, True, 1, 1, None)

        # no start in impossible tiles
        self._solver.cnstr_count(impossible_start_vvs, True, 0, 0, None)

        # exactly one goal in possible tiles
        self._solver.cnstr_count(possible_goal_vvs, True, 1, 1, None)

        # no goal in impossible tiles
        self._solver.cnstr_count(impossible_goal_vvs, True, 0, 0, None)

        for rr, cc in self._vars_rc_t:
            util.check(not self._tile_has_var(rr, cc, util.VOID_TILE), 'void tile')

            node = (rr, cc)
            nodes.append(node)
            out_edges[node] = {}
            in_edges[node] = {}

            self._reach_vars_node[(rr, cc)] = self._solver.make_var()

        for rr, cc in nodes:
            game = self._game_level[rr][cc]
            move_info = reach_info.game_to_move[game]

            for dest_delta, need_open_path_delta, need_open_aux_delta, need_closed_delta in move_info.move_template:
                def inst_deltas(_deltas):
                    _inst = ()
                    for _dr, _dc in _deltas:
                        _nr = rr + _dr
                        _nc = cc + _dc
                        if move_info.wrap_cols: _nc = _nc % self._cols
                        if (_nr, _nc) not in nodes:
                            return None
                        _inst = _inst + ((_nr, _nc),)
                    return _inst

                need_open_path = inst_deltas(need_open_path_delta + [dest_delta])
                if need_open_path is None:
                    continue

                need_open_aux = inst_deltas(need_open_aux_delta)
                if need_open_aux is None:
                    continue

                need_closed = inst_deltas(need_closed_delta)
                if need_closed is None:
                    continue

                tr = rr + dest_delta[0]
                tc = cc + dest_delta[1]

                pwtc = tc
                if move_info.wrap_cols: tc = tc % self._cols

                edge_key = (rr, cc, tr, tc, pwtc, need_open_path, need_open_aux, need_closed)

                out_edges[(rr, cc)][edge_key] = None
                in_edges[(tr, tc)][edge_key] = None

                if edge_key not in self._reach_vars_edge:
                    self._reach_vars_edge[edge_key] = self._solver.make_var()

        open_vars = {}
        for rr, cc in nodes:
            game = self._game_level[rr][cc]
            move_info = reach_info.game_to_move[game]

            # TODO: treat start and goal tiles separately from open tiles?
            all_open_tiles = move_info.open_tiles + [move_info.start_tile, move_info.goal_tile]

            if len(all_open_tiles) == 1:
                open_var = self._tile_var(rr, cc, all_open_tiles[0])
            else:
                open_var = self._solver.make_var()
                open_tile_vvs = [self._tile_var(rr, cc, all_open_tile) for all_open_tile in all_open_tiles]
                for open_tile_vv in open_tile_vvs:
                    self._solver.cnstr_implies_disj(open_tile_vv, True, [open_var], True, None)
                self._solver.cnstr_implies_disj(open_var, True, open_tile_vvs, True, None)
            open_vars[(rr, cc)] = open_var

        for rr, cc in nodes:
            game = self._game_level[rr][cc]
            move_info = reach_info.game_to_move[game]

            reach_node_var = self._reach_vars_node[(rr, cc)]

            out_vvs = []
            for edge_key in out_edges[(rr, cc)]:
                reach_out_edge_var = self._reach_vars_edge[edge_key]
                out_vvs.append(reach_out_edge_var)

                fr, fc, tr, tc, pwtc, need_open_path, need_open_aux, need_closed = edge_key
                util.check((fr, fc) == (rr, cc), 'edge')

                self._solver.cnstr_implies_disj(reach_node_var, False, [reach_out_edge_var], False, None) # !reach_node_var -> !reach_out_edge_var

                for nor, noc in need_open_path + need_open_aux:
                    open_out_var = open_vars[(nor, noc)]
                    self._solver.cnstr_implies_disj(open_out_var, False, [reach_out_edge_var], False, None) # !open_out_var -> !reach_out_edge_var

                for ncr, ncc in need_closed:
                    open_out_var = open_vars[(ncr, ncc)]
                    self._solver.cnstr_implies_disj(open_out_var, True, [reach_out_edge_var], False, None) # open_out_var -> !reach_out_edge_var

            in_vvs = []
            for edge_key in in_edges[(rr, cc)]:
                reach_in_edge_var = self._reach_vars_edge[edge_key]
                in_vvs.append(reach_in_edge_var)

            # at most 1 in edge
            if len(in_vvs) > 0:
                self._solver.cnstr_count(in_vvs, True, 0, 1, None)

            # at most 1 out edge
            if len(out_vvs) > 0:
                self._solver.cnstr_count(out_vvs, True, 0, 1, None)

            # start handling
            start_and_in_vvs = in_vvs

            if self._tile_has_var(rr, cc, move_info.start_tile):
                start_tile_var = self._tile_var(rr, cc, move_info.start_tile)

                # start must be reachable
                self._solver.cnstr_implies_disj(start_tile_var, True, [reach_node_var], True, None) # start_tile_var -> reach_node_var

                # start has no in edges
                for in_vv in in_vvs:
                    self._solver.cnstr_implies_disj(start_tile_var, True, [in_vv], False, None) # ... start_tile_var -> A !in_edge

                start_and_in_vvs = [start_tile_var] + start_and_in_vvs

            # unless it's the start, no in edges means not reachable
            conj_start_and_in_vvs = self._solver.make_conj(start_and_in_vvs, False)
            self._solver.cnstr_implies_disj(conj_start_and_in_vvs, True, [reach_node_var], False, None) # !start_tile_var & A !in_edge -> !reach_node_var

            # goal handling
            if self._tile_has_var(rr, cc, move_info.goal_tile):
                goal_tile_var = self._tile_var(rr, cc, move_info.goal_tile)

                # goal must be reachable
                self._solver.cnstr_implies_disj(goal_tile_var, True, [reach_node_var], True, None) # goal_tile_var -> reach_node_var

                # goal has no out edges
                for out_vv in out_vvs:
                    self._solver.cnstr_implies_disj(goal_tile_var, True, [out_vv], False, None) # ... goal_tile_var -> A !in_edge

        self._reach_out_edges = out_edges

    def solve(self):
        if self._solver.solve():
            print('objective: %s' % str(self._solver.get_objective()))
            return True
        else:
            return False

    def get_result(self):
        res_info = util.ResultInfo()

        res_info.objective = self._solver.get_objective()

        res_info.extra_meta += self._extra_meta

        res_info.reach_info = None
        if self._reach_info:
            res_info.reach_info = util.ResultReachInfo()
            res_info.reach_info.path_edges, res_info.reach_info.path_tiles, path_edge_keys = self._get_reach_path()
            res_info.reach_info.offpath_edges = self._get_reach_offpath_edges(path_edge_keys)

        res_info.tile_level = util.make_grid(self._rows, self._cols, util.VOID_TILE)
        res_info.text_level = None
        res_info.image_level = None

        set_tiles = self._get_tiles_set()
        for rr in range(self._rows):
            for cc in range(self._cols):
                tag = self._tag_level[rr][cc]

                if (rr, cc) in set_tiles:
                    found_tile = set_tiles[(rr, cc)]
                else:
                    found_tile = util.VOID_TILE

                util.check((tag == util.VOID_TEXT) == (found_tile == util.VOID_TILE), 'void')

                res_info.tile_level[rr][cc] = found_tile

        if self._scheme_info.tileset.tile_to_text is not None:
            res_info.text_level = util.tile_level_to_text_level(res_info.tile_level, self._scheme_info.tileset)

        if self._scheme_info.tileset.tile_to_image is not None:
            res_info.image_level = util.tile_level_to_image_level(res_info.tile_level, self._scheme_info.tileset)

        return res_info

    def _get_tiles_set(self):
        tiles = {}

        for rr, cc in self._vars_rc_t:
            found_tile = None
            for tile in self._vars_rc_t[(rr, cc)]:
                if self._solver.get_var(self._vars_rc_t[(rr, cc)][tile]):
                    util.check(found_tile is None, 'multiple tiles selected.')
                    found_tile = tile
            util.check(found_tile is not None, 'no tile selected.')
            tiles[(rr, cc)] = found_tile

        return tiles

    def _get_reach_path(self):
        if not self._reach_info:
            return None

        node_path = []
        tile_path = []
        key_path = []

        start_rc, goal_rc = None, None
        for (rr, cc) in self._vars_rc_t:
            game = self._game_level[rr][cc]
            move_info = self._reach_info.game_to_move[game]

            if move_info.start_tile in self._vars_rc_t[(rr, cc)] and self._solver.get_var(self._tile_var(rr, cc, move_info.start_tile)):
                start_rc = (rr, cc)
            if move_info.goal_tile in self._vars_rc_t[(rr, cc)] and self._solver.get_var(self._tile_var(rr, cc, move_info.goal_tile)):
                goal_rc = (rr, cc)

        util.check(start_rc is not None, 'no start')
        util.check(goal_rc is not None, 'no goal')

        tile_path.append(start_rc)

        current_node = start_rc

        while current_node:
            rr, cc = current_node

            current_reachable = self._solver.get_var(self._reach_vars_node[(rr, cc)])
            util.check(current_reachable, 'current node not reachable')

            next_node = None
            for edge_key in self._reach_out_edges[(rr, cc)]:
                fr, fc, tr, tc, pwtc, need_open_path, need_open_aux, need_closed = edge_key
                util.check(fr == rr and fc == cc, 'edge')

                out_reachable = self._solver.get_var(self._reach_vars_edge[edge_key])
                if out_reachable:
                    util.check(next_node is None, 'multiple out edges')
                    util.check(need_open_path[-1] == (tr, tc), 'path does not end at node')

                    for nr, nc in need_open_path:
                        tile_path.append((nr, nc))

                    if tc == pwtc:
                        node_path.append((fr, fc, tr, tc))
                    else:
                        node_path.append((fr, fc, tr, pwtc))
                        node_path.append((fr, fc + (tc - pwtc), tr, tc))

                    key_path.append(edge_key)

                    next_node = (tr, tc)

            util.check(next_node is not None or current_node == goal_rc, 'path does not end at goal')

            current_node = next_node

        for (ra, ca), (rb, cb) in zip(tile_path, tile_path[1:]):
            game = self._game_level[ra][ca]
            move_info = self._reach_info.game_to_move[game]

            if not move_info.wrap_cols:
                util.check(abs(ra - rb) + abs(ca - cb) == 1, 'path tiles')
            else:
                if ca > 1 + cb:
                    cb += self._cols
                if cb > 1 + ca:
                    ca += self._cols
                util.check(abs(ra - rb) + abs(ca - cb) == 1, 'path tiles')

        return node_path, tile_path, key_path

    def _get_reach_offpath_edges(self, path_edge_keys):
        if not self._reach_info:
            return None

        edges = {}

        for edge_key in self._reach_vars_edge:
            edge_reachable = self._solver.get_var(self._reach_vars_edge[edge_key])
            if edge_reachable and edge_key not in path_edge_keys:
                fr, fc, tr, tc, pwtc, need_open_path, need_open_aux, need_closed = edge_key
                if tc == pwtc:
                    edges[(fr, fc, tr, tc)] = None
                else:
                    edges[(fr, fc, tr, pwtc)] = None
                    edges[(fr, fc + (tc - pwtc), tr, tc)] = None

        return list(edges.keys())
