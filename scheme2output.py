import argparse, pickle, random, sys, time
import generator, mkiii, reach, solvers, util



WEIGHT_PATTERNS       = 10000
WEIGHT_PREFERENCES    =   100
WEIGHT_COUNTS         =     1



COUNTS_SCALE_LO       = 0.5
COUNTS_SCALE_HI       = 1.5



class CustomConstraint:
    def __init__(self):
        pass

    def add(self, gen):
        pass

class OutResultConstraint(CustomConstraint):
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
        print('custom out result constraint')

        util.check(0 <= self._rlo, 'size')
        util.check(0 <= self._clo, 'size')
        util.check(self._rlo < self._rhi, 'size')
        util.check(self._clo < self._chi, 'size')
        util.check(self._rhi <= len(self._out_result.tile_level), 'size')
        util.check(self._chi <= len(self._out_result.tile_level[0]), 'size')

        util.check(0 <= self._roff, 'size')
        util.check(0 <= self._coff, 'size')
        util.check(self._rhi - self._rlo + self._roff <= gen.get_rows(), 'size')
        util.check(self._chi - self._clo + self._coff <= gen.get_cols(), 'size')

        # T: tiles
        # Po: path - on path
        # Pa: path - on and off path
        # Ro: reverse path - on path
        # Ra: reverse path - on and off path
        util.check(self._which in ['T', 'Po', 'Pa', 'Ro', 'Ra', 'TPo', 'TPa', 'TRo', 'TRa'], 'which')

        rinto = -self._rlo + self._roff
        cinto = -self._clo + self._coff

        gen.append_extra_text_lines([util.draw_rect_line('custom', [(self._rlo + rinto, self._clo + cinto, self._rhi + rinto, self._chi + cinto)])])

        if 'T' in self._which:
            for rr in range(self._rlo, self._rhi):
                for cc in range(self._clo, self._chi):
                    gen.add_constraint_tile_counts([(rr + rinto, cc + cinto)], [self._out_result.tile_level[rr][cc]], 1, 1, self._weight)

        if 'Po' in self._which or 'Pa' in self._which or 'Ro' in self._which or 'Ra' in self._which:
            util.check(self._out_result.reach_info != None, 'reach_info')

            path_all = ('Pa' in self._which) or ('Ra' in self._which)
            path_reverse = ('Ro' in self._which) or ('Ra' in self._which)

            path_edges = self._out_result.reach_info.path_edges
            if path_reverse:
                path_edges = reversed(path_edges)

            path_cache = {}
            path_start_found, path_start = False, self._out_result.reach_info.path_tiles[0]
            path_goal_found, path_goal = False, self._out_result.reach_info.path_tiles[-1]
            for (fr, fc, tr, pwtc) in path_edges:
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
                    cpwtc = pwtc + cinto
                    path_cache[(cfr, cfc, ctr, ctc, cpwtc)] = None
                elif fc < 0 or fc >= len(self._out_result.tile_level[0]):
                    # skip duplicate path edges coming in after a wrap
                    continue
                else:
                    break

                if not path_reverse and t_in and (tr, tc) == path_goal:
                    path_goal_found = True
                if path_reverse and f_in and (fr, fc) == path_start:
                    path_start_found = True

            reach_edges = gen.reachability_edges()
            util.check(reach_edges != None, 'reach_edges')

            for cfr, cfc, ctr, ctc, cpwtc in reach_edges:
                on_path = (cfr, cfc, ctr, ctc, cpwtc) in path_cache
                add_cnstr = on_path or path_all
                if add_cnstr:
                    gen.add_constraint_reach_edge(cfr, cfc, ctr, ctc, cpwtc, on_path, self._weight)

            for rr in range(self._rlo, self._rhi):
                for cc in range(self._clo, self._chi):
                    if path_start_found or path_all:
                        gen.add_constraint_start(rr + rinto, cc + cinto, (rr, cc) == path_start, self._weight)
                    if path_goal_found or path_all:
                        gen.add_constraint_goal(rr + rinto, cc + cinto, (rr, cc) == path_goal, self._weight)

class OutPathShortConstraint(CustomConstraint):
    def __init__(self, direction, most, weight):
        self._direction = direction
        self._most = most
        self._weight = weight

    def add(self, gen):
        print('custom out path short constraint')

        if self._direction == reach.RGOAL_L_R:
            for cc in range(gen.get_cols()):
                vvs = []
                for rr in range(gen.get_rows()):
                    vvs.append(gen._reach_vars_node[(rr, cc)])
                gen._solver.cnstr_count(vvs, True, 0, self._most, self._weight)

        elif self._direction == reach.RGOAL_B_T:
            for rr in range(gen.get_rows()):
                vvs = []
                for cc in range(gen.get_cols()):
                    vvs.append(gen._reach_vars_node[(rr, cc)])
                gen._solver.cnstr_count(vvs, True, 0, self._most, self._weight)

        else:
            util.check(False, 'direction')

class OutTextLevelConstraint(CustomConstraint):
    def __init__(self, out_text_level, weight):
        self._out_text_level = out_text_level
        self._weight = weight

    def add(self, gen):
        print('custom out text level constraint')

        util.check(len(self._out_text_level) == gen.get_rows(), 'size')
        util.check(len(self._out_text_level[0]) == gen.get_cols(), 'size')

        for rr in range(gen.get_rows()):
            for cc in range(gen.get_cols()):
                out_text = self._out_text_level[rr][cc]
                if out_text != util.DEFAULT_TEXT:
                    possible_tiles = [tile for tile, text in gen.get_scheme_info().tile_to_text.items() if text == out_text]
                    gen.add_constraint_tile_counts([(rr, cc)], possible_tiles, 1, 1, self._weight)

class OutTextLevelDiffCellConstraint(CustomConstraint):
    def __init__(self, out_text_level, density, offset, weight):
        self._out_text_level = out_text_level
        self._density = density
        self._offset = offset
        self._weight = weight

    def add(self, gen):
        print('custom out text level diff cell constraint')

        util.check(len(self._out_text_level) == gen.get_rows(), 'size')
        util.check(len(self._out_text_level[0]) == gen.get_cols(), 'size')

        for rr in range(gen.get_rows()):
            for cc in range(gen.get_cols()):
                if (self._offset + cc + gen.get_cols() * rr) % self._density != 0:
                    print('-', end='')
                    continue
                else:
                    print('+', end='')

                out_text = self._out_text_level[rr][cc]
                if out_text != util.DEFAULT_TEXT:
                    diff_tiles = [tile for tile, text in gen.get_scheme_info().tile_to_text.items() if text != out_text]
                    gen.add_constraint_tile_counts([(rr, cc)], diff_tiles, 1, 1, self._weight)
            print()

class OutTextLevelDiffCountConstraint(CustomConstraint):
    def __init__(self, out_text_level, diff_pct, weight):
        self._out_text_level = out_text_level
        self._diff_pct = diff_pct
        self._weight = weight

    def add(self, gen):
        print('custom out text level diff count constraint')

        util.check(len(self._out_text_level) == gen.get_rows(), 'size')
        util.check(len(self._out_text_level[0]) == gen.get_cols(), 'size')

        all_diff_vars = []
        for rr in range(gen.get_rows()):
            for cc in range(gen.get_cols()):
                out_text = self._out_text_level[rr][cc]
                if out_text != util.DEFAULT_TEXT:
                    diff_tiles = [tile for tile, text in gen.get_scheme_info().tile_to_text.items() if text != out_text]
                    for tile in diff_tiles:
                        all_diff_vars.append(gen._tile_var(rr, cc, tile))

        tile_diff_count = max(1, min(len(all_diff_vars), int(gen.get_rows() * gen.get_cols() * self._diff_pct // 100)))
        gen._solver.cnstr_count(all_diff_vars, True, tile_diff_count, len(all_diff_vars), self._weight)

class OutTextCountConstraint(CustomConstraint):
    def __init__(self, rlo, clo, rhi, chi, tlo, thi, out_texts, weight):
        self._rlo = rlo
        self._clo = clo
        self._rhi = rhi
        self._chi = chi
        self._tlo = tlo
        self._thi = thi
        self._out_texts = out_texts
        self._weight = weight

    def add(self, gen):
        print('custom out text count constraint')

        possible_tiles = [tile for tile, text in gen.get_scheme_info().tile_to_text.items() if text in self._out_texts]

        rcs = []
        for rr in range(self._rlo, self._rhi):
            for cc in range(self._clo, self._chi):
                rcs.append((rr, cc))
        gen.add_constraint_tile_counts(rcs, possible_tiles, self._tlo, self._thi, self._weight)

class OutTileCountConstraint(CustomConstraint):
    def __init__(self, rlo, clo, rhi, chi, tlo, thi, out_tile, weight):
        self._rlo = rlo
        self._clo = clo
        self._rhi = rhi
        self._chi = chi
        self._tlo = tlo
        self._thi = thi
        self._out_tile = out_tile
        self._weight = weight

    def add(self, gen):
        print('custom out tile count constraint')

        possible_tiles = [self._out_tile]

        rcs = []
        for rr in range(self._rlo, self._rhi):
            for cc in range(self._clo, self._chi):
                rcs.append((rr, cc))
        gen.add_constraint_tile_counts(rcs, possible_tiles, self._tlo, self._thi, self._weight)

class OutTextMaximizeConstraint(CustomConstraint):
    def __init__(self, rlo, clo, rhi, chi, out_texts, weight):
        self._rlo = rlo
        self._clo = clo
        self._rhi = rhi
        self._chi = chi
        self._out_texts = out_texts
        self._weight = weight

    def add(self, gen):
        print('custom out text maximize constraint')

        possible_tiles = [tile for tile, text in gen.get_scheme_info().tile_to_text.items() if text in self._out_texts]

        for rr in range(self._rlo, self._rhi):
            for cc in range(self._clo, self._chi):
                gen.add_constraint_tile_counts([(rr, cc)], possible_tiles, 1, 1, self._weight)



def scheme2output(scheme_info, tag_level, game_level, solver, randomize, soft_patterns, no_patterns, zero_counts, no_counts, reach_setup, mkiii_setup, custom_constraints, show_path_tiles):
    si = scheme_info

    rows = len(tag_level)
    cols = len(tag_level[0])

    for tag_row, game_row in zip(tag_level, game_level):
        util.check(len(tag_row) == len(game_row) == cols, 'row length mismatch')
        for tag, game in zip(tag_row, game_row):
            util.check(game != util.VOID_TEXT, 'void game')
            util.check(game in si.game_to_tag_to_tiles, 'unrecognized game ' + game)
            util.check(tag == util.VOID_TEXT or tag in si.game_to_tag_to_tiles[game], 'unrecognized tag ' + tag + ' for game ' + game)

    weight_counts = WEIGHT_COUNTS
    weight_patterns = WEIGHT_PATTERNS if soft_patterns else None

    print('using solver', solver.get_id())

    if mkiii_setup != None:
        gen = mkiii.GeneratorMKIII(solver, randomize, rows, cols, si, tag_level, game_level)
    else:
        gen = generator.Generator(solver, randomize, rows, cols, si, tag_level, game_level)

    util.timer_section('add tile rules')
    gen.add_rules_tiles()

    if si.pattern_info != None and not no_patterns:
        util.timer_section('add pattern rules')
        gen.add_rules_patterns(weight_patterns)

    if si.count_info != None and not no_counts:
        util.timer_section('add count rules')
        if zero_counts:
            lo, hi = 0, rows * cols
        else:
            lo, hi = COUNTS_SCALE_LO, COUNTS_SCALE_HI
        gen.add_rules_counts(False, lo, hi, weight_counts) # TODO? (si.tile_to_text != None)

    if reach_setup != None:
        util.timer_section('add reachability rules')
        gen.add_rules_reachability(reach.get_reach_info(rows, cols, reach_setup, si))

    if mkiii_setup != None:
        util.timer_section('add mkiii rules')
        gen.add_rules_mkiii(mkiii.get_example_info(mkiii_setup))

    if custom_constraints and len(custom_constraints) > 0:
        util.timer_section('add custom')
        for custom_constraint in custom_constraints:
            custom_constraint.add(gen)

    util.timer_section('solve')

    result = None
    if gen.solve():
        util.timer_section('create output')
        result = gen.get_result()
        util.print_result_info(result, False)

    util.timer_section(None)

    return result



if __name__ == '__main__':
    util.timer_start()

    parser = argparse.ArgumentParser(description='Create output from scheme.')

    parser.add_argument('--outfile', required=True, type=str, help='Output file (without extension, which will be added).')
    parser.add_argument('--schemefile', required=True, type=str, help='Input scheme file.')

    parser.add_argument('--tagfile', type=str, help='Input tag file.')
    parser.add_argument('--gamefile', type=str, help='Input game file.')
    parser.add_argument('--size', type=int, nargs=2, help='Level size (if no tag or game file provided.')

    parser.add_argument('--randomize', type=int, help='Randomize based on given number.')
    parser.add_argument('--show-path-tiles', action='store_true', help='Show path in tiles.')

    parser.add_argument('--solver', type=str, nargs='+', choices=solvers.SOLVER_LIST, default=[solvers.SOLVER_PYSAT_RC2], help='Solver name, from: ' + ','.join(solvers.SOLVER_LIST) + '.')
    parser.add_argument('--solver-portfolio-timeout', type=int, help='Force use of portfolio with given timeout (even for single solver).')

    parser.add_argument('--soft-patterns', action='store_true', help='Make patterns soft constraints.')
    parser.add_argument('--no-patterns', action='store_true', help='Don\'t use pattern rules, even if present.')
    parser.add_argument('--zero-counts', action='store_true', help='Only use counts to prevent tiles not occuring in region.')
    parser.add_argument('--no-counts', action='store_true', help='Don\'t use tile count rules, even if present.')

    parser.add_argument('--reach-move', type=str, nargs='+', default=None, help='Use reachability move rules, from: ' + ','.join(reach.RMOVE_LIST) + '.')
    parser.add_argument('--reach-wrap-cols', action='store_true', help='Wrap columns in reachability.')
    parser.add_argument('--reach-goal', type=str, nargs=2, default=None, help='Use reachability goals, from: ' + ','.join(reach.RGOAL_LIST) + ', plus size.')
    parser.add_argument('--reach-open-zelda', action='store_true', help='Use Zelda open tiles.')

    parser.add_argument('--mkiii-example', type=str, choices=mkiii.EXAMPLES, help='MKIII example name, from: ' + ','.join(mkiii.EXAMPLES) + '.')
    parser.add_argument('--mkiii-layers', type=int, help='MKIII number of layers.')

    parser.add_argument('--out-result', type=str, nargs=9, action='append', help='Constraints on output based on previous result.')
    parser.add_argument('--out-path-short', type=str, nargs=3, action='append', help='Constraints to shorten path.')
    parser.add_argument('--out-text-level', type=str, nargs=2, action='append', help='Constraints on output text level.')
    parser.add_argument('--out-text-level-diff-cell', type=str, nargs=4, action='append', help='Constraints on output text level.')
    parser.add_argument('--out-text-level-diff-count', type=str, nargs=3, action='append', help='Constraints on output text level.')
    parser.add_argument('--out-text-count', type=str, nargs=8, action='append', help='Constraints on output text count.')
    parser.add_argument('--out-tile-count', type=str, nargs=8, action='append', help='Constraints on output tile count.')
    parser.add_argument('--out-text-max', type=str, nargs=6, action='append', help='Constraints to maximize text output.')

    args = parser.parse_args()



    if len(args.solver) == 1 and not args.solver_portfolio_timeout:
        solver = solvers.solver_id_to_solver(args.solver[0])
    else:
        solver = solvers.PortfolioSolver(args.solver, args.solver_portfolio_timeout)

    with open(args.schemefile, 'rb') as f:
        scheme_info = pickle.load(f)

    if args.size:
        if args.tagfile or args.gamefile:
            parser.error('cannot use --size with --tagfile or --gamefile')

        tag_level = util.make_grid(args.size[0], args.size[1], util.DEFAULT_TEXT)
        game_level = util.make_grid(args.size[0], args.size[1], util.DEFAULT_TEXT)

    elif args.tagfile or args.gamefile:
        if args.size:
            parser.error('cannot use --size with --tagfile or --gamefile')

        if args.tagfile and args.gamefile:
            tag_level = util.read_text_level(args.tagfile)
            game_level = util.read_text_level(args.gamefile)
        elif args.tagfile:
            tag_level = util.read_text_level(args.tagfile)
            game_level = util.make_grid(len(tag_level), len(tag_level[0]), util.DEFAULT_TEXT)
        elif args.gamefile:
            game_level = util.read_text_level(args.gamefile)
            tag_level = util.make_grid(len(game_level), len(game_level[0]), util.DEFAULT_TEXT)

    else:
        parser.error('must use --size, --tagfile or --gamefile')



    reach_setup = None

    if args.reach_move or args.reach_goal:
        if not args.reach_move or not args.reach_goal:
            parser.error('must use --reach-move and --reach-goal together')

        reach_setup = util.ReachabilitySetup()
        reach_setup.wrap_cols = False
        reach_setup.open_text = util.OPEN_TEXT

        reach_setup.game_to_move = util.arg_list_to_dict_options(parser, '--reach-move', args.reach_move, reach.RMOVE_LIST)

        if args.reach_goal[0] not in reach.RGOAL_LIST:
            parser.error('--reach-goal[0] must be in ' + ','.join(reach.RGOAL_LIST))
        reach_setup.goal_loc = args.reach_goal[0]

        if not args.reach_goal[1].isnumeric():
            parser.error('--reach-goal[1] must be integer')
        reach_setup.goal_size = int(args.reach_goal[1])

    if args.reach_open_zelda:
        if not reach_setup:
            parser.error('cannot specify --reach-open-zelda without other reach args')
        reach_setup.open_text = util.OPEN_TEXT_ZELDA

    if args.reach_wrap_cols:
        if not reach_setup:
            parser.error('cannot specify --reach-wrap-cols without other reach args')
        reach_setup.wrap_cols = True



    mkiii_setup = None

    if args.mkiii_example or args.mkiii_layers:
        if not args.mkiii_example or not args.mkiii_layers:
            parser.error('must use --mkiii-example and --mkiii-layers together')

        mkiii_setup = mkiii.MKIIISetup()
        mkiii_setup.example = args.mkiii_example
        mkiii_setup.layers = args.mkiii_layers



    custom_constraints = []

    def str_to_weight(s):
        if s == 'hard':
            return None
        elif s == 'soft':
            return WEIGHT_PREFERENCES
        else:
            util.check(False, 'weight')

    if args.out_result:
        for out_result_file, which, rlo, clo, rhi, chi, roff, coff, weight_str in args.out_result:
            with open(out_result_file, 'rb') as f:
                out_result_info = pickle.load(f)
            roff, coff, rlo, clo, rhi, chi = [int(e) for e in (roff, coff, rlo, clo, rhi, chi)]

            custom_constraints.append(OutResultConstraint(out_result_info, which, rlo, clo, rhi, chi, roff, coff, str_to_weight(weight_str)))

    if args.out_path_short:
        for direction, most, weight_str in args.out_path_short:
            most = int(most)
            custom_constraints.append(OutPathShortConstraint(direction, most, str_to_weight(weight_str)))

    if args.out_text_level:
        for out_text_level_file, weight_str in args.out_text_level:
            out_text_level = util.read_text_level(out_text_level_file)

            custom_constraints.append(OutTextLevelConstraint(out_text_level, str_to_weight(weight_str)))

    if args.out_text_level_diff_cell:
        for out_text_level_file, density_str, offset_str, weight_str in args.out_text_level_diff_cell:
            out_text_level = util.read_text_level(out_text_level_file)

            custom_constraints.append(OutTextLevelDiffCellConstraint(out_text_level, int(density_str), int(offset_str), str_to_weight(weight_str)))

    if args.out_text_level_diff_count:
        for out_text_level_file, diff_pct_str, weight_str in args.out_text_level_diff_count:
            out_text_level = util.read_text_level(out_text_level_file)

            custom_constraints.append(OutTextLevelDiffCountConstraint(out_text_level, int(diff_pct_str), str_to_weight(weight_str)))

    if args.out_text_count:
        for rlo, clo, rhi, chi, tlo, thi, out_texts, weight_str in args.out_text_count:
            rlo, clo, rhi, chi, tlo, thi = [int(e) for e in (rlo, clo, rhi, chi, tlo, thi)]

            custom_constraints.append(OutTextCountConstraint(rlo, clo, rhi, chi, tlo, thi, out_texts, str_to_weight(weight_str)))

    if args.out_tile_count:
        for rlo, clo, rhi, chi, tlo, thi, out_tile, weight_str in args.out_tile_count:
            rlo, clo, rhi, chi, tlo, thi, out_tile = [int(e) for e in (rlo, clo, rhi, chi, tlo, thi, out_tile)]

            custom_constraints.append(OutTileCountConstraint(rlo, clo, rhi, chi, tlo, thi, out_tile, str_to_weight(weight_str)))

    if args.out_text_max:
        for rlo, clo, rhi, chi, out_texts, weight_str in args.out_text_max:
            rlo, clo, rhi, chi = [int(e) for e in (rlo, clo, rhi, chi)]

            custom_constraints.append(OutTextMaximizeConstraint(rlo, clo, rhi, chi, out_texts, str_to_weight(weight_str)))



    result_info = scheme2output(scheme_info, tag_level, game_level, solver, args.randomize, args.soft_patterns, args.no_patterns, args.zero_counts, args.no_counts, reach_setup, mkiii_setup, custom_constraints, args.show_path_tiles)
    if result_info:
        util.save_result_info(result_info, args.outfile)
        util.exit_solution_found()
    else:
        util.exit_solution_not_found()
