import argparse, pickle, random, sys, time
import util_common, util_custom, util_generator, util_mkiii, util_reach, util_solvers



WEIGHT_PATTERNS       = 10000
WEIGHT_COUNTS         =     1



COUNTS_SCALE_DEFAULT  = (0.5, 1.5)



class scheme2output_Config:
    def __init__(self):
        self.scheme_info = None

        self.solver_ids = None
        self.solver_filename = None
        self.solver_timeout = None

        self.rows = None
        self.cols = None

        self.tag_level = None
        self.game_level = None

        self.patterns_weight = None
        self.patterns_single = None
        self.patterns_ignore_no_in = None

        self.counts_weight = None
        self.counts_scale = None

        self.reach_connect_setups = None
        self.reach_junction_setups = None
        self.reach_path_search = None
        self.reach_meta_internal = None
        self.reach_print_internal = None

        self.custom_constraints = None

        self.mkiii_setup = None

        self.randomize = None

        self.outfile = None
        self.out_compress = None
        self.out_level_none = None
        self.out_result_none = None
        self.out_tlvl_none = None

        self.quiet = None



def scheme2output(cfg):
    solver = util_solvers.make_solver(cfg.solver_ids, cfg.solver_filename, cfg.solver_timeout)

    print('using solver', solver.get_id())

    si = cfg.scheme_info

    for tag_row, game_row in zip(cfg.tag_level, cfg.game_level):
        util_common.check(len(tag_row) == len(game_row) == cfg.cols, 'row length mismatch')
        for tag, game in zip(tag_row, game_row):
            util_common.check(game != util_common.VOID_TEXT, 'void game')
            util_common.check(tag == util_common.VOID_TEXT or game in si.game_to_tag_to_tiles, 'unrecognized game ' + game)
            util_common.check(tag == util_common.VOID_TEXT or tag in si.game_to_tag_to_tiles[game], 'unrecognized tag ' + tag + ' for game ' + game)

    if cfg.mkiii_setup is not None:
        gen = util_mkiii.GeneratorMKIII(solver, cfg.randomize, cfg.rows, cfg.cols, si, cfg.tag_level, cfg.game_level)
    else:
        gen = util_generator.Generator(solver, cfg.randomize, cfg.rows, cfg.cols, si, cfg.tag_level, cfg.game_level)

    util_common.timer_section('add tile rules')
    gen.add_rules_tiles()

    if cfg.patterns_weight != 0:
        util_common.check(si.pattern_info is not None, 'pattern rules requested but not patterns')
        util_common.timer_section('add pattern rules')
        gen.add_rules_patterns(cfg.patterns_single, cfg.patterns_ignore_no_in, cfg.patterns_weight)
    elif si.pattern_info is not None:
        print('scheme has patterns but not using pattern rules')

    if cfg.counts_weight != 0:
        util_common.check(si.count_info is not None, 'count rules requested but not counts')
        util_common.timer_section('add count rules')
        gen.add_rules_counts(False, cfg.counts_scale, cfg.counts_weight) # TODO? (si.tile_to_text is not None)
    elif si.count_info is not None:
        print('scheme has counts but not using count rules')

    if cfg.reach_path_search:
        gen.use_reach_path_search()

    if cfg.reach_meta_internal:
        gen.use_reach_meta_internal()

    if cfg.reach_junction_setups is not None or cfg.reach_connect_setups is not None:
        util_common.timer_section('add reachability rules')

        if cfg.reach_junction_setups is not None:
            for reach_junction_setup in cfg.reach_junction_setups:
                gen.add_rules_reachability_junction(util_reach.get_reach_junction_info(reach_junction_setup, cfg.rows, cfg.cols, si))

        if cfg.reach_connect_setups is not None:
            for reach_connect_setup in cfg.reach_connect_setups:
                gen.add_rules_reachability_connect(util_reach.get_reach_connect_info(reach_connect_setup, cfg.rows, cfg.cols, si))

    if cfg.mkiii_setup is not None:
        util_common.timer_section('add mkiii rules')
        gen.add_rules_mkiii(util_mkiii.get_example_info(cfg.mkiii_setup))

    if cfg.custom_constraints and len(cfg.custom_constraints) > 0:
        util_common.timer_section('add custom')
        for custom_constraint in cfg.custom_constraints:
            custom_constraint.add(gen)

    util_common.timer_section('solve')

    result = None
    if gen.solve():
        util_common.timer_section('create output')
        result = gen.get_result()

        if cfg.reach_print_internal:
            gen.print_reach_internal()

    util_common.timer_section(None)

    return result



def scheme2output_argv2cfg(argv):
    parser = argparse.ArgumentParser(description='Create output from scheme.')

    parser.add_argument('--outfile', required=True, type=str, help='Output file (without extension, which will be added).')
    parser.add_argument('--schemefile', required=True, type=str, help='Input scheme file.')

    parser.add_argument('--tagfile', type=str, help='Input tag file.')
    parser.add_argument('--gamefile', type=str, help='Input game file.')
    parser.add_argument('--size', type=int, nargs=2, help='Level size (if no tag or game file provided.')

    parser.add_argument('--randomize', type=int, help='Randomize based on given number.')

    parser.add_argument('--solver', type=str, nargs='+', choices=util_solvers.SOLVER_LIST, default=[util_solvers.SOLVER_PYSAT_RC2], help='Solver name, from: ' + ','.join(util_solvers.SOLVER_LIST) + '.')
    parser.add_argument('--solver-file', type=str, help='Filename to use, for solvers that read/write files.')
    parser.add_argument('--solver-portfolio-timeout', type=int, help='Force use of portfolio with given timeout (even for single solver).')

    parser.add_argument('--pattern-single', action='store_true', help='Use single pattern rules.')
    parser.add_argument('--pattern-ignore-no-in', action='store_true', help='Ignore pattern template locations with no input pattern.')
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument('--pattern-hard', action='store_true', help='Use hard pattern rules.')
    group.add_argument('--pattern-soft', type=int, nargs='?', const=WEIGHT_PATTERNS, help='Use soft pattern rules, with weight if provided.')

    parser.add_argument('--pattern-range', type=int, nargs=6, help='Overwrite range placement values in pattern info.')

    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument('--count-hard', action='store_true', help='Use hard count rules.')
    group.add_argument('--count-soft', type=int, nargs='?', const=WEIGHT_COUNTS, help='Use soft count rules, with weight if provided.')

    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument('--count-scale', type=float, nargs=2, help='Use given count scaling.')
    group.add_argument('--count-zero', action='store_true', help='Use counts to prevent tiles from occuring in divisions where unseen.')
    group.add_argument('--count-zero-one', action='store_true', help='Use counts to prevent tiles from occuring in divisions where unseen, and occur in in divisions where seen.')

    parser.add_argument('--reach-junction', type=str, nargs='+', action='append', default=None, help='Use reachability junction, from: ' + ','.join(util_reach.RPLOC_DICT.keys()) + ', plus params.')
    parser.add_argument('--reach-connect', type=str, action='append', default=None, help='Use reachability junction connect, as sub-arguments.')

    parser.add_argument('--reach-start-goal', type=str, nargs='+', default=None, help='Use reachability start and goals, from: ' + ','.join(util_reach.RSGLOC_LIST) + ', plus params.')
    parser.add_argument('--reach-move', type=str, nargs='+', default=None, help='Use reachability move rules, from: ' + ','.join(util_reach.RMOVE_LIST) + '.')
    parser.add_argument('--reach-wrap-rows', action='store_true', help='Wrap rows in reachability.')
    parser.add_argument('--reach-wrap-cols', action='store_true', help='Wrap columns in reachability.')
    parser.add_argument('--reach-open-zelda', action='store_true', help='Use Zelda open tiles.')
    parser.add_argument('--reach-unreachable', action='store_true', help='Generate levels with unreachable goals.')

    parser.add_argument('--reach-path-search', action='store_true', help='Search to find path rather that using solution path (if present)')
    parser.add_argument('--reach-print-internal', action='store_true', help='Display some extra internal information about reachability.')
    parser.add_argument('--reach-meta-internal', action='store_true', help='Include some extra internal information about reachability in metadata.')

    parser.add_argument('--mkiii-example', type=str, choices=util_mkiii.EXAMPLES, help='MKIII example name, from: ' + ','.join(util_mkiii.EXAMPLES) + '.')
    parser.add_argument('--mkiii-layers', type=int, help='MKIII number of layers.')

    parser.add_argument('--custom', type=str, nargs='+', action='append', help='Constraints on output, from: ' + ','.join(util_custom.CUST_LIST) + ', plus options.')

    parser.add_argument('--out-compress', action='store_true', help='Compress output.')
    parser.add_argument('--out-level-none', action='store_true', help='Don\'t save text or image level file.')
    parser.add_argument('--out-result-none', action='store_true', help='Don\'t save result file.')
    parser.add_argument('--out-tlvl-none', action='store_true', help='Don\'t save tile level file.')

    parser.add_argument('--quiet', action='store_true', help='Reduce output.')

    args = parser.parse_args(argv)

    cfg = scheme2output_Config()

    cfg.solver_ids = args.solver
    cfg.solver_filename = args.solver_file
    cfg.solver_timeout = args.solver_portfolio_timeout

    with util_common.openz(args.schemefile, 'rb') as f:
        cfg.scheme_info = pickle.load(f)

    if args.size:
        if args.tagfile or args.gamefile:
            parser.error('cannot use --size with --tagfile or --gamefile')

        cfg.rows, cfg.cols = args.size

        cfg.tag_level = util_common.make_grid(cfg.rows, cfg.cols, util_common.DEFAULT_TEXT)
        cfg.game_level = util_common.make_grid(cfg.rows, cfg.cols, util_common.DEFAULT_TEXT)

    elif args.tagfile or args.gamefile:
        if args.size:
            parser.error('cannot use --size with --tagfile or --gamefile')

        if args.tagfile and args.gamefile:
            cfg.tag_level = util_common.read_text_level(args.tagfile)
            cfg.game_level = util_common.read_text_level(args.gamefile)
        elif args.tagfile:
            cfg.tag_level = util_common.read_text_level(args.tagfile)
            cfg.game_level = util_common.make_grid(len(cfg.tag_level), len(cfg.tag_level[0]), util_common.DEFAULT_TEXT)
        elif args.gamefile:
            cfg.game_level = util_common.read_text_level(args.gamefile)
            cfg.tag_level = util_common.make_grid(len(cfg.game_level), len(cfg.game_level[0]), util_common.DEFAULT_TEXT)

        cfg.rows, cfg.cols = util_common.grid_size(cfg.tag_level)

    else:
        parser.error('must use --size, --tagfile or --gamefile')



    if args.pattern_hard:
        cfg.patterns_weight = None
    elif args.pattern_soft is not None:
        cfg.patterns_weight = args.pattern_soft
    else:
        cfg.patterns_weight = 0

    cfg.patterns_single = args.pattern_single
    cfg.patterns_ignore_no_in = args.pattern_ignore_no_in

    if args.pattern_range is not None:
        pi = cfg.scheme_info.pattern_info
        pi.dr_lo, pi.dr_hi, pi.dc_lo, pi.dc_hi, pi.stride_rows, pi.stride_cols = args.pattern_range



    if args.count_hard:
        cfg.counts_weight = None
    elif args.count_soft is not None:
        cfg.counts_weight = args.count_soft
    else:
        cfg.counts_weight = 0

    cfg.counts_scale = None
    if cfg.counts_weight != 0:
        if args.count_scale is not None:
            cfg.counts_scale = args.count_scale
        elif args.count_zero:
            cfg.counts_scale = util_generator.COUNTS_ZERO
        elif args.count_zero_one:
            cfg.counts_scale = util_generator.COUNTS_ZERO_ONE
        else:
            cfg.counts_scale = COUNTS_SCALE_DEFAULT



    cfg.reach_junction_setups = []

    if args.reach_start_goal is not None:
        cfg.reach_junction_setups += util_reach.get_reach_junction_start_goal_setups(parser, '--reach-start-goal', args.reach_start_goal)

    if args.reach_junction is not None:
        for reach_junction in args.reach_junction:
            cfg.reach_junction_setups.append(util_reach.get_reach_junction_setup(parser, '--reach-junction', reach_junction))

    cfg.reach_junction_setups = cfg.reach_junction_setups if len(cfg.reach_junction_setups) > 0 else None



    cfg.reach_connect_setups = []

    if args.reach_move is not None:
        cfg.reach_connect_setups.append(util_reach.default_reach_connect(util_common.arg_list_to_dict_text_options(parser, '--reach-move', args.reach_move, util_reach.RMOVE_LIST, False), args.reach_wrap_rows, args.reach_wrap_cols, util_common.OPEN_TEXT_ZELDA if args.reach_open_zelda else util_common.OPEN_TEXT, args.reach_unreachable))

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
        if cfg.reach_junction_setups is None:
            parser.error('cannot specify --reach-connect without --reach-junction (or --reach-start-goal)')

        for reach_connect in args.reach_connect:
            cfg.reach_connect_setups.append(util_reach.parse_reach_connect_subargs('--reach-connect', reach_connect.split()))

    cfg.reach_connect_setups = cfg.reach_connect_setups if len(cfg.reach_connect_setups) > 0 else None



    cfg.reach_path_search = args.reach_path_search
    cfg.reach_print_internal = args.reach_print_internal
    cfg.reach_meta_internal = args.reach_meta_internal



    cfg.mkiii_setup = None

    if args.mkiii_example or args.mkiii_layers:
        if not args.mkiii_example or not args.mkiii_layers:
            parser.error('must use --mkiii-example and --mkiii-layers together')

        cfg.mkiii_setup = util_mkiii.MKIIISetup()
        cfg.mkiii_setup.example = args.mkiii_example
        cfg.mkiii_setup.layers = args.mkiii_layers



    cfg.custom_constraints = []

    if args.custom:
        for cust_args in args.custom:
            cfg.custom_constraints.append(util_custom.args_to_custom(cust_args[0], cust_args[1:]))



    cfg.randomize = args.randomize

    cfg.outfile = args.outfile
    cfg.out_compress = args.out_compress
    cfg.out_level_none = args.out_level_none
    cfg.out_result_none = args.out_result_none
    cfg.out_tlvl_none = args.out_tlvl_none

    cfg.quiet = args.quiet

    return cfg



def scheme2output_save_result(cfg, result_info):
    util_common.print_result_info(result_info, sys.stdout)
    util_common.save_result_info(result_info, cfg.outfile, cfg.out_compress, not cfg.out_level_none, not cfg.out_result_none, not cfg.out_tlvl_none)

    if cfg.mkiii_setup is not None:
        util_mkiii.print_result_info_mkiii(result_info, sys.stdout)
        util_mkiii.save_result_info_mkiii(result_info, cfg.outfile)



if __name__ == '__main__':
    util_common.timer_start()

    cfg = scheme2output_argv2cfg(sys.argv[1:])

    if cfg.quiet:
        sys.stdout = open(os.devnull, 'w')

    result_info = scheme2output(cfg)

    if result_info is not None:
        scheme2output_save_result(cfg, result_info)
        util_common.exit_solution_found()
    else:
        util_common.exit_solution_not_found()
