import argparse, pickle, random, sys, time
import util_common, util_custom, util_generator, util_mkiii, util_reach, util_solvers



WEIGHT_PATTERNS       = 10000
WEIGHT_COUNTS         =     1



COUNTS_SCALE_HALF     = (0.5, 1.5)
COUNTS_SCALE_ZERO     = (0.0, 1e10)



def scheme2output(scheme_info, tag_level, game_level, solver, randomize, weight_patterns, weight_counts, counts_scale, reach_junction_setups, reach_connect_setups, mkiii_setup, custom_constraints, print_reach_internal):
    si = scheme_info

    rows = len(tag_level)
    cols = len(tag_level[0])

    for tag_row, game_row in zip(tag_level, game_level):
        util_common.check(len(tag_row) == len(game_row) == cols, 'row length mismatch')
        for tag, game in zip(tag_row, game_row):
            util_common.check(game != util_common.VOID_TEXT, 'void game')
            util_common.check(game in si.game_to_tag_to_tiles, 'unrecognized game ' + game)
            util_common.check(tag == util_common.VOID_TEXT or tag in si.game_to_tag_to_tiles[game], 'unrecognized tag ' + tag + ' for game ' + game)

    print('using solver', solver.get_id())

    if mkiii_setup is not None:
        gen = util_mkiii.GeneratorMKIII(solver, randomize, rows, cols, si, tag_level, game_level)
    else:
        gen = util_generator.Generator(solver, randomize, rows, cols, si, tag_level, game_level)

    util_common.timer_section('add tile rules')
    gen.add_rules_tiles()

    if weight_patterns != 0:
        util_common.check(si.pattern_info is not None, 'pattern rules requested but not patterns')
        util_common.timer_section('add pattern rules')
        gen.add_rules_patterns(weight_patterns)
    elif si.pattern_info is not None:
        print('scheme has patterns but not using pattern rules')

    if weight_counts != 0:
        util_common.check(si.count_info is not None, 'count rules requested but not counts')
        util_common.timer_section('add count rules')
        lo, hi = counts_scale
        gen.add_rules_counts(False, lo, hi, weight_counts) # TODO? (si.tile_to_text is not None)
    elif si.count_info is not None:
        print('scheme has counts but not using count rules')

    if reach_junction_setups is not None or reach_connect_setups is not None:
        util_common.timer_section('add reachability rules')

        if reach_junction_setups is not None:
            for reach_junction_setup in reach_junction_setups:
                gen.add_rules_reachability_junction(util_reach.get_reach_junction_info(reach_junction_setup, rows, cols, si))

        if reach_connect_setups is not None:
            for reach_connect_setup in reach_connect_setups:
                gen.add_rules_reachability_connect(util_reach.get_reach_connect_info(reach_connect_setup, rows, cols, si))

    if mkiii_setup is not None:
        util_common.timer_section('add mkiii rules')
        gen.add_rules_mkiii(util_mkiii.get_example_info(mkiii_setup))

    if custom_constraints and len(custom_constraints) > 0:
        util_common.timer_section('add custom')
        for custom_constraint in custom_constraints:
            custom_constraint.add(gen)

    util_common.timer_section('solve')

    result = None
    if gen.solve():
        util_common.timer_section('create output')
        result = gen.get_result()
        util_common.print_result_info(result)

        if print_reach_internal:
            gen.print_reach_internal()

    util_common.timer_section(None)

    return result



if __name__ == '__main__':
    util_common.timer_start()

    parser = argparse.ArgumentParser(description='Create output from scheme.')

    parser.add_argument('--outfile', required=True, type=str, help='Output file (without extension, which will be added).')
    parser.add_argument('--schemefile', required=True, type=str, help='Input scheme file.')

    parser.add_argument('--tagfile', type=str, help='Input tag file.')
    parser.add_argument('--gamefile', type=str, help='Input game file.')
    parser.add_argument('--size', type=int, nargs=2, help='Level size (if no tag or game file provided.')

    parser.add_argument('--randomize', type=int, help='Randomize based on given number.')
    parser.add_argument('--print-reach-internal', action='store_true', help='Display some extra internal information about reachability.')

    parser.add_argument('--solver', type=str, nargs='+', choices=util_solvers.SOLVER_LIST, default=[util_solvers.SOLVER_PYSAT_RC2], help='Solver name, from: ' + ','.join(util_solvers.SOLVER_LIST) + '.')
    parser.add_argument('--solver-file', type=str, help='Filename to use, for solvers that read/write files.')
    parser.add_argument('--solver-portfolio-timeout', type=int, help='Force use of portfolio with given timeout (even for single solver).')

    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument('--pattern-hard', action='store_true', help='Use hard pattern rules.')
    group.add_argument('--pattern-soft', type=int, nargs='?', const=WEIGHT_PATTERNS, help='Use soft pattern rules, with weight if provided.')

    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument('--count-hard', action='store_true', help='Use hard count rules.')
    group.add_argument('--count-soft', type=int, nargs='?', const=WEIGHT_COUNTS, help='Use soft count rules, with weight if provided.')

    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument('--count-scale', type=float, nargs=2, help='Use given count scaling.')
    group.add_argument('--count-scale-zero', action='store_true', help='Only use counts to prevent tiles not occuring in region.')

    parser.add_argument('--reach-junction', type=str, nargs='+', action='append', default=None, help='Use reachability junction, from: ' + ','.join(util_reach.RPLOC_DICT.keys()) + ', plus params.')
    parser.add_argument('--reach-connect', type=str, action='append', default=None, help='Use reachability junction connect, as sub-arguments.')

    parser.add_argument('--reach-start-goal', type=str, nargs='+', default=None, help='Use reachability start and goals, from: ' + ','.join(util_reach.RSGLOC_LIST) + ', plus params.')
    parser.add_argument('--reach-move', type=str, nargs='+', default=None, help='Use reachability move rules, from: ' + ','.join(util_reach.RMOVE_LIST) + '.')
    parser.add_argument('--reach-wrap-rows', action='store_true', help='Wrap rows in reachability.')
    parser.add_argument('--reach-wrap-cols', action='store_true', help='Wrap columns in reachability.')
    parser.add_argument('--reach-open-zelda', action='store_true', help='Use Zelda open tiles.')
    parser.add_argument('--reach-unreachable', action='store_true', help='Generate levels with unreachable goals.')

    parser.add_argument('--mkiii-example', type=str, choices=util_mkiii.EXAMPLES, help='MKIII example name, from: ' + ','.join(util_mkiii.EXAMPLES) + '.')
    parser.add_argument('--mkiii-layers', type=int, help='MKIII number of layers.')

    parser.add_argument('--custom', type=str, nargs='+', action='append', help='Constraints on output, from: ' + ','.join(util_custom.CUST_LIST) + ', plus options.')

    parser.add_argument('--out-compress', action='store_true', help='Compress output.')
    parser.add_argument('--out-level-none', action='store_true', help='Don\'t save text or image level file.')
    parser.add_argument('--out-result-none', action='store_true', help='Don\'t save result file.')
    parser.add_argument('--out-tlvl-none', action='store_true', help='Don\'t save tile level file.')

    parser.add_argument('--quiet', action='store_true', help='Reduce output.')

    args = parser.parse_args()

    if args.quiet:
        sys.stdout = open(os.devnull, 'w')

    if len(args.solver) == 1 and not args.solver_portfolio_timeout:
        solver = util_solvers.solver_id_to_solver(args.solver[0])
    else:
        solver = util_solvers.PortfolioSolver(args.solver, args.solver_portfolio_timeout)

    if args.solver_file:
        util_common.check(util_solvers.solver_takes_filename(solver), 'solver cannot use filename')
        solver.set_filename(args.solver_file)

    with util_common.openz(args.schemefile, 'rb') as f:
        scheme_info = pickle.load(f)

    if args.size:
        if args.tagfile or args.gamefile:
            parser.error('cannot use --size with --tagfile or --gamefile')

        tag_level = util_common.make_grid(args.size[0], args.size[1], util_common.DEFAULT_TEXT)
        game_level = util_common.make_grid(args.size[0], args.size[1], util_common.DEFAULT_TEXT)

    elif args.tagfile or args.gamefile:
        if args.size:
            parser.error('cannot use --size with --tagfile or --gamefile')

        if args.tagfile and args.gamefile:
            tag_level = util_common.read_text_level(args.tagfile)
            game_level = util_common.read_text_level(args.gamefile)
        elif args.tagfile:
            tag_level = util_common.read_text_level(args.tagfile)
            game_level = util_common.make_grid(len(tag_level), len(tag_level[0]), util_common.DEFAULT_TEXT)
        elif args.gamefile:
            game_level = util_common.read_text_level(args.gamefile)
            tag_level = util_common.make_grid(len(game_level), len(game_level[0]), util_common.DEFAULT_TEXT)

    else:
        parser.error('must use --size, --tagfile or --gamefile')



    reach_junction_setups = None

    if args.reach_start_goal is not None:
        reach_junction_setups = util_reach.get_reach_start_goal_setups(parser, '--reach-start-goal', args.reach_start_goal)

    if args.reach_junction is not None:
        if reach_junction_setups is None:
            reach_junction_setups = []
        for reach_junction in args.reach_junction:
            reach_junction_setups.append(util_reach.get_reach_junction_setup(parser, '--reach-junction', reach_junction))



    reach_connect_setups = None

    if args.reach_move is not None:
        if reach_junction_setups is None:
            parser.error('cannot specify --reach-move without --reach-junction (or --reach-start-goal)')

        reach_connect_setup = util_common.ReachConnectSetup()
        reach_connect_setup.src = util_common.START_TEXT
        reach_connect_setup.dst = util_common.GOAL_TEXT
        reach_connect_setup.unreachable = args.reach_unreachable
        reach_connect_setup.game_to_reach_move = util_common.arg_list_to_dict_options(parser, '--reach-move', args.reach_move, util_reach.RMOVE_LIST)
        reach_connect_setup.wrap_rows = args.reach_wrap_rows
        reach_connect_setup.wrap_cols = args.reach_wrap_cols
        reach_connect_setup.open_text = util_common.OPEN_TEXT_ZELDA if args.reach_open_zelda else util_common.OPEN_TEXT

        if reach_connect_setups is None:
            reach_connect_setups = []
        reach_connect_setups.append(reach_connect_setup)
    else:
        if args.reach_open_zelda:
            parser.error('cannot specify --reach-open-zelda without --reach-move')
        if args.reach_wrap_rows:
            parser.error('cannot specify --reach-wrap-rows without --reach-move')
        if args.reach_wrap_cols:
            parser.error('cannot specify --reach-wrap-cols without --reach-move')
        if args.reach_unreachable:
            parser.error('cannot specify --reach-unreachable without --reach-move')

    if args.reach_connect is not None:
        if reach_junction_setups is None:
            parser.error('cannot specify --reach-connect without --reach-junction (or --reach-start-goal)')

        for reach_connect in args.reach_connect:
            if reach_connect_setups is None:
                reach_connect_setups = []
            reach_connect_setups.append(util_reach.parse_reach_subargs('--reach-connect', reach_connect.split()))



    mkiii_setup = None

    if args.mkiii_example or args.mkiii_layers:
        if not args.mkiii_example or not args.mkiii_layers:
            parser.error('must use --mkiii-example and --mkiii-layers together')

        mkiii_setup = util_mkiii.MKIIISetup()
        mkiii_setup.example = args.mkiii_example
        mkiii_setup.layers = args.mkiii_layers



    custom_constraints = []

    if args.custom:
        for cust_args in args.custom:
            custom_constraints.append(util_custom.args_to_custom(cust_args[0], cust_args[1:]))



    if args.pattern_hard:
        weight_patterns = None
    elif args.pattern_soft is not None:
        weight_patterns = args.pattern_soft
    else:
        weight_patterns = 0

    if args.count_hard:
        weight_counts = None
    elif args.count_soft is not None:
        weight_counts = args.count_soft
    else:
        weight_counts = 0

    if args.count_scale_zero:
        counts_scale = COUNTS_SCALE_ZERO
    elif args.count_scale:
        counts_scale = args.count_scale
    else:
        counts_scale = COUNTS_SCALE_HALF

    result_info = scheme2output(scheme_info, tag_level, game_level, solver, args.randomize, weight_patterns, weight_counts, counts_scale, reach_junction_setups, reach_connect_setups, mkiii_setup, custom_constraints, args.print_reach_internal)
    if result_info:
        util_common.save_result_info(result_info, args.outfile, args.out_compress, not args.out_level_none, not args.out_result_none, not args.out_tlvl_none)
        util_common.exit_solution_found()
    else:
        util_common.exit_solution_not_found()
