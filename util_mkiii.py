import util_common, util_generator



EX_MKJR_WALK      = 'mkjr-walk'
EX_MKJR_WALK_THRU = 'mkjr-walk-thru'
EX_MKJR_MAZE      = 'mkjr-maze'
EX_MKJR_MAZE_COIN = 'mkjr-maze-coin'
EX_SOKO           = 'soko'
EX_DOKU           = 'doku'
EX_LOCK           = 'lock'
EX_SLIDE          = 'slide'
EX_FILL           = 'fill'
EX_PLAT           = 'plat'
EX_VVV            = 'vvv'
EX_LINK           = 'link'
EX_MATCH          = 'match'

EXAMPLES = [EX_MKJR_WALK, EX_MKJR_WALK_THRU, EX_MKJR_MAZE, EX_MKJR_MAZE_COIN, EX_SOKO, EX_DOKU, EX_LOCK, EX_SLIDE, EX_FILL, EX_PLAT, EX_VVV, EX_LINK, EX_MATCH]



DIR_NORTH     = [(-1,  0)]
DIR_SOUTH     = [( 1,  0)]
DIR_EAST      = [( 0,  1)]
DIR_WEST      = [( 0, -1)]
DIR_EASTWEST  = [( 0,  1), ( 0, -1)]
DIR_SOUTHEAST = [( 1,  0), ( 0, 1)]
DIR_ALL       = [(1, 0), (-1, 0), (0, 1), (0, -1)]
DIR_NONE      = [(0, 0)]



RR_GRP_CHOICE = 'RULE_CHOICE'
RR_GRP_ALL    = 'RULE_ALL'

RR_ORD_ONE = 'ONE'
RR_ORD_SEQ = 'SEQ'
RR_ORD_PRI = 'PRI'



class MKIIISetup:
    def __init__(self):
        self.example = None
        self.layers = None

class MKIIIInfo:
    def __init__(self):
        self.states = None
        self.rep_rules = None
        self.rep_rule_names = None
        self.rep_rule_order = None
        self.use_term = None
        self.custom = None
        self.layers = None
        self.extra_meta = []

class CustomInfo:
    def __init__(self, solver, rng, vars_lrct, rows, cols, layers):
        self.solver = solver
        self.rng = rng
        self.vars_lrct = vars_lrct
        self.rows = rows
        self.cols = cols
        self.layers = layers



def init_range(ci, chars, lo, hi):
    vvs = []
    for rr in range(ci.rows):
        for cc in range(ci.cols):
            for char in chars:
                vvs.append(ci.vars_lrct[(0, rr, cc, char)])
    ci.solver.cnstr_count(vvs, True, lo, hi, None)

def init_exact(ci, chars, amt):
    init_range(ci, chars, amt, amt)

def init_points(ci, default, points):
    for rr in range(ci.rows):
        for cc in range(ci.cols):
            if (rr, cc) in points:
                st = points[(rr, cc)]
            else:
                st = default
            ci.solver.cnstr_count([ci.vars_lrct[(0, rr, cc, st)]], True, 1, 1, None)

def init_dist_atleast(ci, char1, char2, dst):
    for rr in range(ci.rows):
        for cc in range(ci.cols):
            for r2 in range(ci.rows):
                for c2 in range(ci.cols):
                    dstsq = (rr - r2) ** 2 + (cc - c2) ** 2
                    if dstsq < dst * dst:
                        ci.solver.cnstr_implies_disj(ci.vars_lrct[(0, rr, cc, char1)], True, [ci.vars_lrct[(0, r2, c2, char2)]], False, None)
                        ci.solver.cnstr_implies_disj(ci.vars_lrct[(0, rr, cc, char2)], True, [ci.vars_lrct[(0, r2, c2, char1)]], False, None)

def init_dist_impl_nearby(ci, char1, chars2, dst):
    for rr in range(ci.rows):
        for cc in range(ci.cols):
            vvs = []
            for r2 in range(ci.rows):
                for c2 in range(ci.cols):
                    dstsq = (rr - r2) ** 2 + (cc - c2) ** 2
                    if dstsq <= dst * dst + 0.001:
                        for char2 in chars2:
                            vvs.append(ci.vars_lrct[(0, r2, c2, char2)])
            ci.solver.cnstr_implies_disj(ci.vars_lrct[(0, rr, cc, char1)], True, vvs, True, None)

def full_range(ci, chars, lo, hi):
    vvs = []
    for ll in range(ci.layers):
        for rr in range(ci.rows):
            for cc in range(ci.cols):
                for char in chars:
                    vvs.append(ci.vars_lrct[(ll, rr, cc, char)])
    ci.solver.cnstr_count(vvs, True, lo, hi, None)

def full_exact(ci, chars, amt):
    full_range(ci, chars, amt, amt)

def full_norepeat(ci, char):
    vvs = []
    for ll in range(ci.layers - 1):
        for rr in range(ci.rows):
            for cc in range(ci.cols):
                for l2 in range(ll + 1, ci.layers):
                    ci.solver.cnstr_implies_disj(ci.vars_lrct[(ll, rr, cc, char)], True, [ci.vars_lrct[(l2, rr, cc, char)]], False, None)

def fini_range(ci, chars, lo, hi):
    vvs = []
    for rr in range(ci.rows):
        for cc in range(ci.cols):
            for char in chars:
                vvs.append(ci.vars_lrct[(ci.layers - 1, rr, cc, char)])
    ci.solver.cnstr_count(vvs, True, lo, hi, None)

def fini_exact(ci, chars, amt):
    fini_range(ci, chars, amt, amt)

def init_implies(ci, char1, r1, c1, chars2, r2, c2):
    v1 = ci.vars_lrct[(0, r1, c1, char1)]
    if r2 < 0 or r2 >= ci.rows or c2 < 0 or c2 >= ci.cols:
        pass
    else:
        vv2 = [ci.vars_lrct[(0, r2, c2, char2)] for char2 in chars2]
        ci.solver.cnstr_implies_disj(v1, True, vv2, True, None)

def fini_implies(ci, char1, r1, c1, chars2, r2, c2):
    v1 = ci.vars_lrct[(ci.layers - 1, r1, c1, char1)]
    if r2 < 0 or r2 >= ci.rows or c2 < 0 or c2 >= ci.cols:
        ci.solver.cnstr_count([v1], True, 0, 0, None)
    else:
        vv2 = [ci.vars_lrct[(ci.layers - 1, r2, c2, char2)] for char2 in chars2]
        ci.solver.cnstr_implies_disj(v1, True, vv2, True, None)



def get_example_info(mkiii_setup):
    ei = MKIIIInfo()

    ei.layers = mkiii_setup.layers

    if mkiii_setup.example == EX_MKJR_WALK:
        ei.states = 'X-*'
        ei.rep_rules = [(RR_GRP_CHOICE, [(DIR_ALL, '*XX', '--*')])]
        ei.rep_rule_order = RR_ORD_ONE
        ei.use_term = False

        def _custom(ci):
            init_points(ci, 'X', {(1, 1): '*'})
        ei.custom = _custom

    elif mkiii_setup.example == EX_MKJR_WALK_THRU:
        ei.states = 'X-*$oO'
        ei.rep_rules = [(RR_GRP_CHOICE, [(DIR_ALL, '*XX', '--*'), (DIR_ALL, '*X$', '--*'), (DIR_ALL, '*Xo', '--O')])]
        ei.rep_rule_order = RR_ORD_ONE
        ei.use_term = True

        def _custom(ci):
            # start in top-left
            init_points(ci, 'X', {(1, 1): '*', (1, ci.cols - 2): '$', (ci.rows - 2, 1): '$', (ci.rows - 2, ci.cols - 2): 'o'})

            # through collectibles to exit
            fini_exact(ci, '$', 0)
            fini_exact(ci, 'o', 0)

        ei.custom = _custom

    elif mkiii_setup.example == EX_MKJR_MAZE:
        ei.states = 'X-~'
        ei.rep_rules = [(RR_GRP_CHOICE, [(DIR_ALL, '-XX', '-~-')])]
        ei.rep_rule_order = RR_ORD_ONE
        ei.use_term = False

        def _custom(ci):
            # start in middle
            init_points(ci, 'X', {(ci.rows // 2, ci.cols // 2): '-'})
        ei.custom = _custom

    elif mkiii_setup.example == EX_MKJR_MAZE_COIN:
        ei.states = 'X-~$@o'
        ei.rep_rules = [(RR_GRP_CHOICE, [(DIR_ALL, '-XX', '-~-'), (DIR_ALL, '-XX', '-$-'), (DIR_ALL, '-XX', '-@-'), (DIR_ALL, '-XX', '-o-')])]
        ei.rep_rule_order = RR_ORD_ONE
        ei.use_term = False

        def _custom(ci):
            # start in middle
            init_points(ci, 'X', {(ci.rows // 2, ci.cols // 2): '-'})

            # placements
            fini_range(ci, '$', 3, 5)
            fini_exact(ci, '@', 1)
            fini_exact(ci, 'o', 1)
        ei.custom = _custom

    elif mkiii_setup.example == EX_SOKO:
        ei.states = 'X-@#oO'
        ei.rep_rules = [(RR_GRP_CHOICE, [(DIR_ALL, '@-', '-@'), (DIR_ALL, '@#-', '-@#'), (DIR_ALL, '@#o', '-@O')])]
        ei.rep_rule_order = RR_ORD_ONE
        ei.use_term = True

        def _custom(ci):
            # start
            init_exact(ci, '@', 1)
            init_exact(ci, '#', 2)
            init_exact(ci, 'o', 2)

            # border
            for rr in range(ci.rows):
                ci.solver.cnstr_count([ci.vars_lrct[(0, rr, 0, 'X')]], True, 1, 1, None)
                ci.solver.cnstr_count([ci.vars_lrct[(0, rr, ci.cols - 1, 'X')]], True, 1, 1, None)
            for cc in range(ci.cols):
                ci.solver.cnstr_count([ci.vars_lrct[(0, 0, cc, 'X')]], True, 1, 1, None)
                ci.solver.cnstr_count([ci.vars_lrct[(0, ci.rows - 1, cc, 'X')]], True, 1, 1, None)

            # distances
            init_dist_atleast(ci, '#', 'o', 2)

            # clear around boxes
            for rr in range(ci.rows):
                for cc in range(ci.cols):
                    for r2 in range(1, ci.rows - 1):
                        if rr == r2:
                            continue
                        ci.solver.cnstr_implies_disj(ci.vars_lrct[(0, rr, cc, '#')], True, [ci.vars_lrct[(0, r2, cc, 'o')]], False, None)
                    for c2 in range(1, ci.cols - 1):
                        if cc == c2:
                            continue
                        ci.solver.cnstr_implies_disj(ci.vars_lrct[(0, rr, cc, '#')], True, [ci.vars_lrct[(0, rr, c2, 'o')]], False, None)

            # all boxes cleared at end
            fini_exact(ci, '#', 0)
        ei.custom = _custom

    elif mkiii_setup.example == EX_DOKU:
        ei.states = '-123456789'
        ei.rep_rules = [(RR_GRP_CHOICE, [(DIR_NONE, '-', '1'), (DIR_NONE, '-', '2'), (DIR_NONE, '-', '3'),
                                         (DIR_NONE, '-', '4'), (DIR_NONE, '-', '5'), (DIR_NONE, '-', '6'),
                                         (DIR_NONE, '-', '7'), (DIR_NONE, '-', '8'), (DIR_NONE, '-', '9')])]
        ei.rep_rule_order = RR_ORD_ONE
        ei.use_term = False

        ei.extra_meta.append(util_common.meta_rect('level', [(0, 0, 3, 3), (0, 3, 3, 6), (0, 6, 3, 9), (3, 0, 6, 3), (3, 3, 6, 6), (3, 6, 6, 9), (6, 0, 9, 3), (6, 3, 9, 6), (6, 6, 9, 9)]))

        def _custom(ci):
            # check size
            util_common.check(ci.rows == 9, 'doku size')
            util_common.check(ci.cols == 9, 'doku size')

            # start
            init_range(ci, '-', ci.layers - 1, ci.layers - 1)

            # symmetric
            for rr in range(ci.rows):
                for cc in range(ci.cols):
                    ci.solver.cnstr_implies_disj(ci.vars_lrct[(0, rr, cc, '-')], True, [ci.vars_lrct[(0, ci.rows - 1 - rr, ci.cols - 1 - cc, '-')]], True, None)

            # extra layer vars
            vars_layer_cant = {}
            for ll in range(ci.layers - 1):
                vars_layer_cant[ll] = {}
                for ss in '123456789':
                    for rr in range(ci.rows):
                        for cc in range(ci.cols):
                            vars_layer_cant[ll][(rr, cc, ss)] = ci.solver.make_var()
                for ss in '123456789':
                    for rr in range(ci.rows):
                        for cc in range(ci.cols):
                            cant_vvs = []
                            for r2 in range(ci.rows):
                                if rr != r2:
                                    cant_vvs.append(ci.vars_lrct[(ll, r2, cc, ss)])
                            for c2 in range(ci.cols):
                                if cc != c2:
                                    cant_vvs.append(ci.vars_lrct[(ll, rr, c2, ss)])
                            ci.solver.cnstr_implies_disj(vars_layer_cant[ll][(rr, cc, ss)], True, cant_vvs, True, None)

            vars_layer_must = {}
            for ll in range(ci.layers - 1):
                vars_layer_must[ll] = {}
                for ss in '123456789':
                    for rr in range(ci.rows):
                        for cc in range(ci.cols):
                            box_cant = []
                            for br in range(3):
                                for bc in range(3):
                                    r2 = (rr // 3) * 3 + br
                                    c2 = (cc // 3) * 3 + bc
                                    if (rr, cc) != (r2, c2):
                                        box_cant.append(vars_layer_cant[ll][(r2, c2, ss)])
                            box_cant_conj = ci.solver.make_conj(box_cant, True)
                            vars_layer_must[ll][(rr, cc, ss)] = box_cant_conj

            for ll in range(ci.layers - 1):
                for ss in '123456789':
                    for rr in range(ci.rows):
                        for cc in range(ci.cols):
                            changes = ci.solver.make_conj([ci.vars_lrct[(ll, rr, cc, '-')], ci.vars_lrct[(ll + 1, rr, cc, ss)]], True)
                            ci.solver.cnstr_implies_disj(changes, True, [vars_layer_must[ll][(rr, cc, ss)]], True, None)

            # partially filled then filled at end
            for ll in range(ci.layers):
                lo = 1 if ll + 1 == ci.layers else 0
                for ss in '123456789':
                    for rr in range(ci.rows):
                        vars_rc = []
                        for cc in range(ci.cols):
                            vars_rc.append(ci.vars_lrct[(ll, rr, cc, ss)])
                        ci.solver.cnstr_count(vars_rc, True, lo, 1, None)

                    for cc in range(ci.cols):
                        vars_rc = []
                        for rr in range(ci.rows):
                            vars_rc.append(ci.vars_lrct[(ll, rr, cc, ss)])
                        ci.solver.cnstr_count(vars_rc, True, lo, 1, None)

                    for br in range(ci.rows // 3):
                        for bc in range(ci.cols // 3):
                            vars_rc = []
                            for ir in range(3):
                                for ic in range(3):
                                    vars_rc.append(ci.vars_lrct[(ll, br * 3 + ir, bc * 3 + ic, ss)])
                            ci.solver.cnstr_count(vars_rc, True, lo, 1, None)

        ei.custom = _custom

    elif mkiii_setup.example == EX_LOCK:
        rep_rules_player = (RR_GRP_CHOICE, [(DIR_ALL, '@-', '-@'), (DIR_ALL, '&-', '-&'), (DIR_ALL, '@%', '-&'), (DIR_ALL, '&:', '@-'), (DIR_ALL, '@~', '~@'), (DIR_ALL, '@o', '~O')])
        rep_rules_enemy = (RR_GRP_ALL, [(DIR_ALL, '+--@', '-+-@'), (DIR_ALL, '+-@', '-+@'), (DIR_ALL, '+@', '-+'),
                                         (DIR_ALL, '+--&', '-+-&'), (DIR_ALL, '+-&', '-+&'), (DIR_ALL, '+&', '-+')])
        ei.states = 'X-~@%:&oO+'
        ei.rep_rules = [rep_rules_player, rep_rules_enemy]
        ei.rep_rule_names = ['player', 'enemy']
        ei.rep_rule_order = RR_ORD_SEQ
        ei.use_term = True

        def _custom(ci):
            # one start/goal
            init_exact(ci, '@', 1)
            init_exact(ci, 'o', 1)

            # key/door/enemy
            init_exact(ci, '%', 1)
            init_exact(ci, ':', 1)
            init_exact(ci, '+', 2)

            # setup
            init_range(ci, 'X', 0, ci.rows * ci.cols // 2)
            init_dist_impl_nearby(ci, '+', '%:@', 2)
            for rr in range(ci.rows):
                for cc in range(ci.cols):
                    ci.solver.cnstr_implies_disj(ci.vars_lrct[(0, rr, cc, '+')], True, [ci.vars_lrct[(ci.layers - 1, rr, cc, '+')]], False, None)

            # goal reached at end
            fini_exact(ci, 'o', 0)
        ei.custom = _custom

    elif mkiii_setup.example == EX_SLIDE:
        ei.states = 'X-@^v><oOabc()[]'
        ei.rep_rules = [
            (RR_GRP_CHOICE, [
                (DIR_NONE, '@', '@'),
                (DIR_NORTH, '@-', '-^'), (DIR_SOUTH, '@-', '-v'), (DIR_EAST, '@-', '->'), (DIR_WEST, '@-', '-<'),
                (DIR_NORTH, '@o', '-O'), (DIR_SOUTH, '@o', '-O'), (DIR_EAST, '@o', '-O'), (DIR_WEST, '@o', '-O'),
                (DIR_NORTH, '^o', '-O'), (DIR_SOUTH, 'vo', '-O'), (DIR_EAST, '>o', '-O'), (DIR_WEST, '<o', '-O'),
                (DIR_NORTH, '^a', '-a'), (DIR_SOUTH, 'va', '-a'), (DIR_EAST, '>a', '-a'), (DIR_WEST, '<a', '-a'),
                (DIR_NORTH, '^b', '-b'), (DIR_SOUTH, 'vb', '-b'), (DIR_EAST, '>b', '-b'), (DIR_WEST, '<b', '-b'),
                (DIR_NORTH, '^c', '-c'), (DIR_SOUTH, 'vc', '-c'), (DIR_EAST, '>c', '-c'), (DIR_WEST, '<c', '-c'),
                (DIR_NORTH, '^-', '-^'), (DIR_SOUTH, 'v-', '-v'), (DIR_EAST, '>-', '->'), (DIR_WEST, '<-', '-<'),
                (DIR_NORTH, '^X', '@X'), (DIR_SOUTH, 'vX', '@X'), (DIR_EAST, '>X', '@X'), (DIR_WEST, '<X', '@X')]),
             (RR_GRP_ALL, [(DIR_NONE, 'a', 'b'), (DIR_NONE, 'b', 'c'), (DIR_NONE, 'c', 'a'), # only one turret so no rules on those collisions; turret/goal?
                            (DIR_NORTH, 'a-', 'b('), (DIR_SOUTH, 'a-', 'b)'), (DIR_EAST, 'a-', 'b]'), (DIR_WEST, 'a-', 'b['),
                            (DIR_NORTH, 'a@', 'b('), (DIR_SOUTH, 'a@', 'b)'), (DIR_EAST, 'a@', 'b]'), (DIR_WEST, 'a@', 'b['),
                            (DIR_NORTH, 'a^', 'b('), (DIR_SOUTH, 'a^', 'b)'), (DIR_EAST, 'a^', 'b]'), (DIR_WEST, 'a^', 'b['),
                            (DIR_NORTH, 'av', 'b('), (DIR_SOUTH, 'av', 'b)'), (DIR_EAST, 'av', 'b]'), (DIR_WEST, 'av', 'b['),
                            (DIR_NORTH, 'a>', 'b('), (DIR_SOUTH, 'a>', 'b)'), (DIR_EAST, 'a>', 'b]'), (DIR_WEST, 'a>', 'b['),
                            (DIR_NORTH, 'a<', 'b('), (DIR_SOUTH, 'a<', 'b)'), (DIR_EAST, 'a<', 'b]'), (DIR_WEST, 'a<', 'b['),
                            (DIR_NORTH, '(-', '-('), (DIR_SOUTH, ')-', '-)'), (DIR_EAST, ']-', '-]'), (DIR_WEST, '[-', '-['),
                            (DIR_NORTH, '(@', '-('), (DIR_SOUTH, ')@', '-)'), (DIR_EAST, ']@', '-]'), (DIR_WEST, '[@', '-['),
                            (DIR_NORTH, '(^', '-('), (DIR_SOUTH, ')^', '-)'), (DIR_EAST, ']^', '-]'), (DIR_WEST, '[^', '-['),
                            (DIR_NORTH, '(v', '-('), (DIR_SOUTH, ')v', '-)'), (DIR_EAST, ']v', '-]'), (DIR_WEST, '[v', '-['),
                            (DIR_NORTH, '(>', '-('), (DIR_SOUTH, ')>', '-)'), (DIR_EAST, ']>', '-]'), (DIR_WEST, '[>', '-['),
                            (DIR_NORTH, '(<', '-('), (DIR_SOUTH, ')<', '-)'), (DIR_EAST, ']<', '-]'), (DIR_WEST, '[<', '-['),
                            (DIR_NORTH, '(X', '-X'), (DIR_SOUTH, ')X', '-X'), (DIR_EAST, ']X', '-X'), (DIR_WEST, '[X', '-X')])]
        ei.rep_rule_names = ['player', 'enemy']
        ei.rep_rule_order = RR_ORD_SEQ
        ei.use_term = True

        def _custom(ci):
            # start/goal/turret
            init_exact(ci, '@', 1)
            init_exact(ci, 'a', 1)
            init_exact(ci, 'o', 1)

            # start and goal in opposite corners
            CSIZE = 3
            start_vvs_rem = []
            start_vvs_00 = []
            start_vvs_01 = []
            start_vvs_10 = []
            start_vvs_11 = []
            goal_vvs_rem = []
            goal_vvs_00 = []
            goal_vvs_01 = []
            goal_vvs_10 = []
            goal_vvs_11 = []
            for rr in range(CSIZE):
                for cc in range(CSIZE):
                    start_vvs_rem.append(ci.vars_lrct[(0, rr, cc, '@')])
                    goal_vvs_rem.append(ci.vars_lrct[(0, rr, cc, 'o')])
            for rr in range(CSIZE):
                for cc in range(CSIZE):
                    start_vvs_00.append(ci.vars_lrct[(0, rr, cc, '@')])
                    goal_vvs_00.append(ci.vars_lrct[(0, rr, cc, 'o')])
            for rr in range(CSIZE):
                for cc in range(ci.cols - CSIZE, ci.cols):
                    start_vvs_01.append(ci.vars_lrct[(0, rr, cc, '@')])
                    goal_vvs_01.append(ci.vars_lrct[(0, rr, cc, 'o')])
            for rr in range(ci.rows - CSIZE, ci.rows):
                for cc in range(CSIZE):
                    start_vvs_10.append(ci.vars_lrct[(0, rr, cc, '@')])
                    goal_vvs_10.append(ci.vars_lrct[(0, rr, cc, 'o')])
            for rr in range(ci.rows - CSIZE, ci.rows):
                for cc in range(ci.cols - CSIZE, ci.cols):
                    start_vvs_11.append(ci.vars_lrct[(0, rr, cc, '@')])
                    goal_vvs_11.append(ci.vars_lrct[(0, rr, cc, 'o')])
            start_vvs_rem = sorted(list(set(start_vvs_rem) - set(start_vvs_00) - set(start_vvs_01) - set(start_vvs_10) - set(start_vvs_11)))
            ci.solver.cnstr_count(start_vvs_00 + start_vvs_01 + start_vvs_10 + start_vvs_11, True, 1, 1, None)
            ci.solver.cnstr_count(start_vvs_rem, True, 0, 0, None)
            goal_vvs_rem = sorted(list(set(goal_vvs_rem) - set(goal_vvs_00) - set(goal_vvs_01) - set(goal_vvs_10) - set(goal_vvs_11)))
            ci.solver.cnstr_count(goal_vvs_00 + goal_vvs_01 + goal_vvs_10 + goal_vvs_11, True, 1, 1, None)
            ci.solver.cnstr_count(goal_vvs_rem, True, 0, 0, None)

            for start_vv in start_vvs_00:
                ci.solver.cnstr_implies_disj(start_vv, True, goal_vvs_00, False, None)
                ci.solver.cnstr_implies_disj(start_vv, True, goal_vvs_01, False, None)
                ci.solver.cnstr_implies_disj(start_vv, True, goal_vvs_10, False, None)
                ci.solver.cnstr_implies_disj(start_vv, True, goal_vvs_11, True, None)
            for start_vv in start_vvs_01:
                ci.solver.cnstr_implies_disj(start_vv, True, goal_vvs_00, False, None)
                ci.solver.cnstr_implies_disj(start_vv, True, goal_vvs_01, False, None)
                ci.solver.cnstr_implies_disj(start_vv, True, goal_vvs_10, True, None)
                ci.solver.cnstr_implies_disj(start_vv, True, goal_vvs_11, False, None)
            for start_vv in start_vvs_10:
                ci.solver.cnstr_implies_disj(start_vv, True, goal_vvs_00, False, None)
                ci.solver.cnstr_implies_disj(start_vv, True, goal_vvs_01, True, None)
                ci.solver.cnstr_implies_disj(start_vv, True, goal_vvs_10, False, None)
                ci.solver.cnstr_implies_disj(start_vv, True, goal_vvs_11, False, None)
            for start_vv in start_vvs_11:
                ci.solver.cnstr_implies_disj(start_vv, True, goal_vvs_00, True, None)
                ci.solver.cnstr_implies_disj(start_vv, True, goal_vvs_01, False, None)
                ci.solver.cnstr_implies_disj(start_vv, True, goal_vvs_10, False, None)
                ci.solver.cnstr_implies_disj(start_vv, True, goal_vvs_11, False, None)

            for goal_vv in goal_vvs_00:
                ci.solver.cnstr_implies_disj(goal_vv, True, start_vvs_00, False, None)
                ci.solver.cnstr_implies_disj(goal_vv, True, start_vvs_01, False, None)
                ci.solver.cnstr_implies_disj(goal_vv, True, start_vvs_10, False, None)
                ci.solver.cnstr_implies_disj(goal_vv, True, start_vvs_11, True, None)
            for goal_vv in goal_vvs_01:
                ci.solver.cnstr_implies_disj(goal_vv, True, start_vvs_00, False, None)
                ci.solver.cnstr_implies_disj(goal_vv, True, start_vvs_01, False, None)
                ci.solver.cnstr_implies_disj(goal_vv, True, start_vvs_10, True, None)
                ci.solver.cnstr_implies_disj(goal_vv, True, start_vvs_11, False, None)
            for goal_vv in goal_vvs_10:
                ci.solver.cnstr_implies_disj(goal_vv, True, start_vvs_00, False, None)
                ci.solver.cnstr_implies_disj(goal_vv, True, start_vvs_01, True, None)
                ci.solver.cnstr_implies_disj(goal_vv, True, start_vvs_10, False, None)
                ci.solver.cnstr_implies_disj(goal_vv, True, start_vvs_11, False, None)
            for goal_vv in goal_vvs_11:
                ci.solver.cnstr_implies_disj(goal_vv, True, start_vvs_00, True, None)
                ci.solver.cnstr_implies_disj(goal_vv, True, start_vvs_01, False, None)
                ci.solver.cnstr_implies_disj(goal_vv, True, start_vvs_10, False, None)
                ci.solver.cnstr_implies_disj(goal_vv, True, start_vvs_11, False, None)

            # turret in middle
            turret_rows = range(ci.rows // 3, 2 * ci.rows // 3)
            turret_cols = range(ci.cols // 3, 2 * ci.cols // 3)
            vvs = []
            for rr in turret_rows:
                for cc in turret_cols:
                    vvs.append(ci.vars_lrct[(0, rr, cc, 'a')])
            ci.solver.cnstr_count(vvs, True, 1, 1, None)

            # clear around turrets
            for rr in range(ci.rows):
                for cc in range(ci.cols):
                    for r2 in range(1, ci.rows - 1):
                        if rr == r2:
                            continue
                        ci.solver.cnstr_implies_disj(ci.vars_lrct[(0, rr, cc, 'a')], True, [ci.vars_lrct[(0, r2, cc, '-')]], True, None)
                    for c2 in range(1, ci.cols - 1):
                        if cc == c2:
                            continue
                        ci.solver.cnstr_implies_disj(ci.vars_lrct[(0, rr, cc, 'a')], True, [ci.vars_lrct[(0, rr, c2, '-')]], True, None)

            # bump along side walls
            vvs = []
            for rr in turret_rows:
                vvs.append(ci.vars_lrct[(0, rr, 1, 'X')])
            ci.solver.cnstr_count(vvs, True, 1, 1, None)
            vvs = []
            for rr in turret_rows:
                vvs.append(ci.vars_lrct[(0, rr, ci.cols - 2, 'X')])
            ci.solver.cnstr_count(vvs, True, 1, 1, None)
            vvs = []
            for cc in turret_cols:
                vvs.append(ci.vars_lrct[(0, 1, cc, 'X')])
            ci.solver.cnstr_count(vvs, True, 1, 1, None)
            vvs = []
            for cc in turret_cols:
                vvs.append(ci.vars_lrct[(0, ci.rows - 2, cc, 'X')])
            ci.solver.cnstr_count(vvs, True, 1, 1, None)

            # goal reached at end
            fini_exact(ci, 'o', 0)
        ei.custom = _custom

    elif mkiii_setup.example == EX_FILL:
        ei.states = 'X-~@^v><'
        ei.rep_rules = [
            (RR_GRP_CHOICE, [
                (DIR_NORTH, '@-', '~^'), (DIR_SOUTH, '@-', '~v'), (DIR_EAST, '@-', '~>'), (DIR_WEST, '@-', '~<'),
                (DIR_NORTH, '@~', '~^'), (DIR_SOUTH, '@~', '~v'), (DIR_EAST, '@~', '~>'), (DIR_WEST, '@~', '~<'),
                (DIR_NORTH, '^-', '~^'), (DIR_SOUTH, 'v-', '~v'), (DIR_EAST, '>-', '~>'), (DIR_WEST, '<-', '~<'),
                (DIR_NORTH, '^~', '~^'), (DIR_SOUTH, 'v~', '~v'), (DIR_EAST, '>~', '~>'), (DIR_WEST, '<~', '~<'),
                (DIR_NORTH, '^X', '@X'), (DIR_SOUTH, 'vX', '@X'), (DIR_EAST, '>X', '@X'), (DIR_WEST, '<X', '@X')])]
        ei.rep_rule_order = RR_ORD_ONE
        ei.use_term = True

        def _custom(ci):
            # start
            init_exact(ci, '@', 1)
            init_range(ci, '-', (ci.rows - 2) * (ci.cols - 2) // 3, ci.rows * ci.cols)
            init_range(ci, '~', 0, 0)

            # border
            for rr in range(ci.rows):
                ci.solver.cnstr_count([ci.vars_lrct[(0, rr, 0, 'X')]], True, 1, 1, None)
                ci.solver.cnstr_count([ci.vars_lrct[(0, rr, ci.cols - 1, 'X')]], True, 1, 1, None)
            for cc in range(ci.cols):
                ci.solver.cnstr_count([ci.vars_lrct[(0, 0, cc, 'X')]], True, 1, 1, None)
                ci.solver.cnstr_count([ci.vars_lrct[(0, ci.rows - 1, cc, 'X')]], True, 1, 1, None)

            # filled
            fini_exact(ci, '-', 0)
            fini_exact(ci, '@', 1)
        ei.custom = _custom

    elif mkiii_setup.example == EX_PLAT:
        ei.states = 'X-@12oO+?'
        ei.rep_rules = [(RR_GRP_CHOICE,
                         [(DIR_EASTWEST, '@-', '-@'), (DIR_NONE, '@', '@'), (DIR_EASTWEST, '@o', '-O'), (DIR_NORTH, 'X@', 'X2'),
                          (DIR_EASTWEST, '1-', '-1'), (DIR_NONE, '1', '1'),
                          (DIR_EASTWEST, '2-', '-2'), (DIR_NONE, '2', '2')]),
                        (RR_GRP_ALL,
                         [(DIR_WEST, '+-', '-+'), (DIR_WEST, '+@', '-+'), (DIR_WEST, '+2', '-+'), (DIR_WEST, '+1', '-+')]),
                        (RR_GRP_ALL, # TODO: what about enemy above player? '-@+'
                         [(DIR_NORTH, '-+', '+-'), (DIR_NORTH, '@+', '+-'),
                          (DIR_NORTH, 'X@', 'X@'), (DIR_NORTH, '+@', '@-'), (DIR_NORTH, '-@', '@-'),
                          (DIR_NORTH, '2-', '-1'), (DIR_NORTH, '2X', '@X'), (DIR_NORTH, '2?', '@X'),
                          (DIR_NORTH, '1-', '-@'), (DIR_NORTH, '1X', '@X'), (DIR_NORTH, '1?', '@X')])]
        ei.rep_rule_names = ['player', 'enemy', 'physics']
        ei.rep_rule_order = RR_ORD_SEQ
        ei.use_term = True

        def _custom(ci):
            # start/goal placement
            ci.solver.cnstr_count([ci.vars_lrct[(0, ci.rows - 2, 0, '@')]], True, 1, 1, None)
            ci.solver.cnstr_count([ci.vars_lrct[(0, ci.rows - 2, ci.cols - 1, 'o')]], True, 1, 1, None)

            # one start/goal
            init_exact(ci, '@', 1)
            init_exact(ci, 'o', 1)
            init_exact(ci, '?', 1)
            init_exact(ci, '+', 2)

            # goal reached at end
            fini_exact(ci, 'o', 0)
            fini_exact(ci, '?', 0)
            fini_exact(ci, '+', 0)
        ei.custom = _custom

    elif mkiii_setup.example == EX_VVV:
        ei.states = 'X-^v+()oO'
        ei.rep_rules = [(RR_GRP_CHOICE,
                         [(DIR_SOUTH, 'vX', '^X'), (DIR_NONE, 'v', 'v'), (DIR_EASTWEST, 'v-', '-v'), (DIR_EASTWEST, 'vo', '-O'),
                          (DIR_NORTH, '^X', 'vX'), (DIR_NONE, '^', '^'), (DIR_EASTWEST, '^-', '-^'), (DIR_EASTWEST, '^o', '-O')]),
                        (RR_GRP_ALL,
                         [(DIR_EAST, ')-', '-)'), (DIR_EAST, ')X', '(X'), (DIR_EAST, ')v', '-)'), (DIR_EAST, ')^', '-)'),
                          (DIR_WEST, '(-', '-('), (DIR_WEST, '(X', ')X'), (DIR_WEST, '(v', '-('), (DIR_WEST, '(^', '-('),
                          (DIR_EAST, ')(', '()')]),
                        (RR_GRP_ALL,
                         [(DIR_SOUTH, 'v-', '-v'), (DIR_SOUTH, 'vo', '-O'), (DIR_SOUTH, 'v(', '-('), (DIR_SOUTH, 'v)', '-)'), (DIR_SOUTH, 'v+', '-+'),
                          (DIR_NORTH, '^-', '-^'), (DIR_NORTH, '^o', '-O'), (DIR_NORTH, '^)', '-)'), (DIR_NORTH, '^)', '-)'), (DIR_NORTH, '^+', '-+')])]

        ei.rep_rule_names = ['player', 'enemy', 'physics']
        ei.rep_rule_order = RR_ORD_SEQ
        ei.use_term = True

        def _custom(ci):
            # start/goal placement
            ci.solver.cnstr_count([ci.vars_lrct[(0, ci.rows - 2, 1, 'v')]], True, 1, 1, None)
            ci.solver.cnstr_count([ci.vars_lrct[(0, ci.rows - 2, ci.cols - 2, 'o')]], True, 1, 1, None)

            # one start/goal
            init_exact(ci, 'v', 1)
            init_exact(ci, 'o', 1)

            # turrets / solid
            init_exact(ci, '()', 2)
            init_range(ci, '+', 4, ci.cols)

            # goal reached at end
            fini_exact(ci, 'o', 0)
        ei.custom = _custom

    elif mkiii_setup.example == EX_LINK:
        ei.states = '─│┐┘└┌X'
        ei.rep_rules = [(RR_GRP_CHOICE, [(DIR_NONE, '─', '│'), (DIR_NONE, '│', '─'), (DIR_NONE, '┐', '┘'), (DIR_NONE, '┘', '└'), (DIR_NONE, '└', '┌'), (DIR_NONE, '┌', '┐')])]
        ei.rep_rule_order = RR_ORD_ONE
        ei.use_term = True

        def _custom(ci):
            init_range(ci, '─', 1, 10)
            init_range(ci, '│', 1, 10)
            init_range(ci, 'X', max(1, ci.rows * ci.rows // 10), ci.rows * ci.rows // 2)

            # disconnected at start
            rows_order = list(range(ci.rows))
            cols_order = list(range(ci.cols))
            if ci.rng:
                ci.rng.shuffle(rows_order)
                ci.rng.shuffle(cols_order)

            ind = 0
            for rr in rows_order:
                for cc in cols_order:
                    ind += 1
                    if ind % 4 == 0:
                        ci.solver.cnstr_count([ci.vars_lrct[(0, rr, cc, ss)] for ss in '─│┐┘└┌'], True, 1, 1, None)
                        init_implies(ci, '─', rr, cc, '┐┘│X', rr, cc - 1)
                        init_implies(ci, '─', rr, cc, '└┌│X', rr, cc + 1)
                        init_implies(ci, '│', rr, cc, '┘└─X', rr - 1, cc)
                        init_implies(ci, '│', rr, cc, '┌┐─X', rr + 1, cc)
                        init_implies(ci, '┐', rr, cc, '┐┘│X', rr, cc - 1)
                        init_implies(ci, '┐', rr, cc, '┌┐─X', rr + 1, cc)
                        init_implies(ci, '┘', rr, cc, '┐┘│X', rr, cc - 1)
                        init_implies(ci, '┘', rr, cc, '┘└─X', rr - 1, cc)
                        init_implies(ci, '└', rr, cc, '└┌│X', rr, cc + 1)
                        init_implies(ci, '└', rr, cc, '┘└─X', rr - 1, cc)
                        init_implies(ci, '┌', rr, cc, '└┌│X', rr, cc + 1)
                        init_implies(ci, '┌', rr, cc, '┌┐─X', rr + 1, cc)

            # connected at end
            for rr in range(ci.rows):
                for cc in range(ci.cols):
                    fini_implies(ci, '─', rr, cc, '└┌─', rr, cc - 1)
                    fini_implies(ci, '─', rr, cc, '┐┘─', rr, cc + 1)
                    fini_implies(ci, '│', rr, cc, '┘└│', rr + 1, cc)
                    fini_implies(ci, '│', rr, cc, '┌┐│', rr - 1, cc)
                    fini_implies(ci, '┐', rr, cc, '└┌─', rr, cc - 1)
                    fini_implies(ci, '┐', rr, cc, '┘└│', rr + 1, cc)
                    fini_implies(ci, '┘', rr, cc, '└┌─', rr, cc - 1)
                    fini_implies(ci, '┘', rr, cc, '┌┐│', rr - 1, cc)
                    fini_implies(ci, '└', rr, cc, '┐┘─', rr, cc + 1)
                    fini_implies(ci, '└', rr, cc, '┌┐│', rr - 1, cc)
                    fini_implies(ci, '┌', rr, cc, '┐┘─', rr, cc + 1)
                    fini_implies(ci, '┌', rr, cc, '┘└│', rr + 1, cc)

            # no simple loops at end
            for rr in range(ci.rows - 1):
                for cc in range(ci.cols - 1):
                    patt = ci.solver.make_conj([ci.vars_lrct[(ci.layers - 1, rr, cc, '┌')], ci.vars_lrct[(ci.layers - 1, rr, cc + 1, '┐')], ci.vars_lrct[(ci.layers - 1, rr + 1, cc, '└')], ci.vars_lrct[(ci.layers - 1, rr + 1, cc + 1, '┘')]], True)
                    ci.solver.cnstr_count([patt], True, 0, 0, None)

        ei.custom = _custom

    elif mkiii_setup.example == EX_MATCH:
        ei.states = 'X-789'
        rep_rules_fall  = (RR_GRP_ALL, [(DIR_SOUTH, '7-', '-7'), (DIR_SOUTH, '8-', '-8'), (DIR_SOUTH, '9-', '-9')])
        rep_rules_match = (RR_GRP_ALL, [(DIR_SOUTHEAST, '777', '---'), (DIR_SOUTHEAST, '888', '---'), (DIR_SOUTHEAST, '999', '---')])
        rep_rules_swap  = (RR_GRP_CHOICE, [(DIR_ALL, '78', '87'), (DIR_ALL, '89', '98'), (DIR_ALL, '97', '79'), (DIR_EASTWEST, '7-', '-7'), (DIR_EASTWEST, '8-', '-8'), (DIR_EASTWEST, '9-', '-9')])
        ei.rep_rules = [rep_rules_fall, rep_rules_match, rep_rules_swap]
        ei.rep_rule_names = ['fall', 'match', 'swap']
        ei.rep_rule_order = RR_ORD_PRI
        ei.use_term = True

        def _custom(ci):
            # no block above blanks
            for rr in range(1, ci.rows):
                for cc in range(ci.cols):
                    ci.solver.cnstr_implies_disj(ci.vars_lrct[(0, rr, cc, '-')], True, [ci.vars_lrct[(0, rr - 1, cc, '-')]], True, None)

            # only a few blank at top
            init_range(ci, '-', ci.cols + 1, ci.cols * 3)

            # only a few blocks
            init_range(ci, 'X', 0, ci.rows * ci.cols // 5)

            # a few of each block
            init_range(ci, '7', 3, ci.rows * ci.cols)
            init_range(ci, '8', 3, ci.rows * ci.cols)
            init_range(ci, '9', 3, ci.rows * ci.cols)

            # no 3 in a row
            for ss in '789':
                for rr in range(1, ci.rows - 1):
                    for cc in range(ci.cols):
                        ci.solver.cnstr_implies_disj(ci.vars_lrct[(0, rr, cc, ss)], True, [ci.vars_lrct[(0, rr - 1, cc, ss)], ci.vars_lrct[(0, rr + 1, cc, ss)]], False, None)
                for rr in range(ci.rows):
                    for cc in range(1, ci.cols - 1):
                        ci.solver.cnstr_implies_disj(ci.vars_lrct[(0, rr, cc, ss)], True, [ci.vars_lrct[(0, rr, cc - 1, ss)], ci.vars_lrct[(0, rr, cc + 1, ss)]], False, None)

            # all cleared at end
            fini_range(ci, '7', 0, 0)
            fini_range(ci, '8', 0, 0)
            fini_range(ci, '9', 0, 0)

        ei.custom = _custom

    else:
        util_common.check(False, 'mkiii_setup example' + mkiii_setup.example)

    return ei



class GeneratorMKIII(util_generator.Generator):
    def __init__(self, solver, randomize, rows, cols, scheme_info, tag_level, game_level):
        super().__init__(solver, randomize, rows, cols, scheme_info, tag_level, game_level)

        self._states = None
        self._layers = None
        self._group_names = None

        self._vars_lrct = None
        self._vars_patt = None
        self._vars_term = None
        self._vars_pri = None

        self._var_state_false = None

        self._change_vars_rcs = None

        self._text_to_tile = None

    def add_rules_mkiii(self, mkiii_info):
        print('add mkiii constraints')

        self._states = mkiii_info.states
        self._layers = mkiii_info.layers
        self._group_names = list(mkiii_info.rep_rule_names) if mkiii_info.rep_rule_names else None

        self.append_extra_meta(mkiii_info.extra_meta)

        self._vars_lrct = {}
        self._vars_patt = {}
        self._vars_term = None
        self._vars_pri = None

        self._var_state_false = self._solver.make_var()
        self._solver.cnstr_count([self._var_state_false], True, 0, 0, None)

        self._change_vars_rcs = [[]]

        self._text_to_tile = {}
        for tile, text in self._scheme_info.tileset.tile_to_text.items():
            util_common.check(text not in self._text_to_tile, 'cannot have duplicate tile text ' + text + ' for mkiii')
            util_common.check(text in self._states, 'text ' + text + ' not in states')
            self._text_to_tile[text] = tile

        layers_order = list(range(self._layers))
        rows_order = list(range(self._rows))
        cols_order = list(range(self._cols))
        states_order = list(self._states)

        if self._rng:
            self._rng.shuffle(layers_order)
            self._rng.shuffle(rows_order)
            self._rng.shuffle(cols_order)
            self._rng.shuffle(states_order)

        # terminal variables
        if mkiii_info.use_term:
            self._vars_term = []
            self._vars_term.append(None)
            for ll in range(self._layers - 1):
                self._vars_term.append(self._solver.make_var())

        # state variables
        for ll in layers_order:
            for rr in rows_order:
                for cc in cols_order:
                    for ss in states_order:
                        if ll == 0:
                            if ss in self._text_to_tile:
                                self._vars_lrct[(0, rr, cc, ss)] = self._vars_rc_t[(rr, cc)][self._text_to_tile[ss]]
                            else:
                                self._vars_lrct[(0, rr, cc, ss)] = self._var_state_false
                        else:
                            self._vars_lrct[(ll, rr, cc, ss)] = self._solver.make_var()

        # one state true (first layer already handled)
        for ll in range(1, self._layers):
            for rr in range(self._rows):
                for cc in range(self._cols):
                    vvs = []
                    for ss in self._states:
                        vvs.append(self._vars_lrct[(ll, rr, cc, ss)])

                    self._solver.cnstr_count(vvs, True, 1, 1, None)

        # make_conj duplicate helper
        conjs = {}
        def _make_conj(_vvs):
            nonlocal conjs

            _key = tuple(sorted([str(_vv) for _vv in _vvs]))

            if _key not in conjs:
                conjs[_key] = self._solver.make_conj(_vvs, True)
            return conjs[_key]

        if mkiii_info.rep_rule_order in [RR_ORD_ONE, RR_ORD_SEQ]:
            self._vars_pri = None
        elif mkiii_info.rep_rule_order == RR_ORD_PRI:
            self._vars_pri = []
        else:
            util_common.check(False, 'rep_rule_order')

        if mkiii_info.rep_rule_order == RR_ORD_ONE:
            util_common.check(len(mkiii_info.rep_rules) == 1, 'rep_rule_order')
        elif mkiii_info.rep_rule_order in [RR_ORD_SEQ, RR_ORD_PRI]:
            util_common.check(len(mkiii_info.rep_rules) > 1, 'rep_rule_order')
        else:
            util_common.check(False, 'rep_rule_order')

        for ll in range(self._layers - 1):
            # keep track of change vars
            layer_change_vars_rcs = []

            # terminal stays set
            if self._vars_term is not None:
                if ll > 0:
                    self._solver.cnstr_implies_disj(self._vars_term[ll], True, [self._vars_term[ll + 1]], True, None)

            # keep track of possible changes at this layer
            all_changes_rc = {}
            for rr in range(self._rows):
                for cc in range(self._cols):
                    all_changes_rc[(rr, cc)] = []

            # set up priority vars
            if self._vars_pri is not None:
                inds_pri = []

            # set up rep rules
            for rep_rules_index in range(len(mkiii_info.rep_rules)):
                if self._vars_pri is not None:
                    ind_pri = self._solver.make_var()
                    prev_inds_pri = list(inds_pri)
                    inds_pri.append(ind_pri)
                else:
                    if rep_rules_index != (ll % len(mkiii_info.rep_rules)):
                        continue

                rep_rules_type, rep_rules = mkiii_info.rep_rules[rep_rules_index]

                # keep track of possible changes at this index
                ind_changes = []
                ind_changes_vin = []

                # connections between layers
                for rr in range(self._rows):
                    for cc in range(self._cols):
                        for rule_info in rep_rules:
                            rule_dirs, rule_in, rule_out = rule_info
                            util_common.check(len(rule_in) == len(rule_out), 'rule in and out different lengths')

                            for dr, dc in rule_dirs:
                                util_common.check(abs(dr) + abs(dc) <= 1, 'dr and/or dc out of range')
                                if dr == dc == 0:
                                    util_common.check(len(rule_in) == len(rule_out) == 1, 'rule has length but no direction')

                                if rr + dr * len(rule_in) >= -1 and rr + dr * len(rule_in) <= self._rows and cc + dc * len(rule_in) >= -1 and cc + dc * len(rule_in) <= self._cols:
                                    vin = []
                                    vou = []
                                    vrs = []
                                    vcs = []
                                    for ii in range(len(rule_in)):
                                        vin.append(self._vars_lrct[(ll + 0, rr + dr * ii, cc + dc * ii, rule_in[ii])])
                                        vou.append(self._vars_lrct[(ll + 1, rr + dr * ii, cc + dc * ii, rule_out[ii])])
                                        vrs.append(rr + dr * ii)
                                        vcs.append(cc + dc * ii)

                                    change = _make_conj(vin + vou)
                                    change_vin = _make_conj(vin)
                                    layer_change_vars_rcs.append((vin + vou, (min(vrs), min(vcs), max(vrs) + 1, max(vcs) + 1)))

                                    ind_changes.append(change)
                                    ind_changes_vin.append(change_vin)

                                    for ii in range(len(rule_in)):
                                        all_changes_rc[(rr + dr * ii, cc + dc * ii)].append(change)

                if self._vars_pri is not None:
                    # pri equals any change
                    for change in ind_changes:
                        self._solver.cnstr_implies_disj(change, True, [ind_pri], True, None)
                    self._solver.cnstr_implies_disj(ind_pri, True, ind_changes, True, None)

                if rep_rules_type == RR_GRP_CHOICE:
                    # exactly one change or terminal or prev pri changed
                    changes_or_term_or_prev_pri = ind_changes
                    if self._vars_term is not None:
                        changes_or_term_or_prev_pri.append(self._vars_term[ll + 1])
                    if self._vars_pri is not None:
                        changes_or_term_or_prev_pri = changes_or_term_or_prev_pri + prev_inds_pri
                    self._solver.cnstr_count(changes_or_term_or_prev_pri, True, 1, 1, None)

                elif rep_rules_type == RR_GRP_ALL:
                    # everything that can change does, unless terminal or prev_pri
                    for ind_change, ind_change_vin in zip(ind_changes, ind_changes_vin):
                        change_or_term_or_prev_pri = [ind_change]
                        if self._vars_term is not None:
                            change_or_term_or_prev_pri.append(self._vars_term[ll + 1])
                        if self._vars_pri is not None:
                            change_or_term_or_prev_pri = change_or_term_or_prev_pri + prev_inds_pri
                        self._solver.cnstr_implies_disj(ind_change_vin, True, change_or_term_or_prev_pri, True, None)
                        self._solver.cnstr_count(change_or_term_or_prev_pri, True, 0, 1, None)

                else:
                    util_common.check(False, 'rep_rules_type')

            self._change_vars_rcs.append(layer_change_vars_rcs)

            if self._vars_pri is not None:
                self._vars_pri.append(inds_pri)

                # exactly one priority changes, or term
                inds_pri_or_term = list(inds_pri)
                if self._vars_term is not None:
                    inds_pri_or_term.append(self._vars_term[ll + 1])
                self._solver.cnstr_count(inds_pri_or_term, True, 1, 1, None)

            # everything is either the same or part of a change
            for rr in range(self._rows):
                for cc in range(self._cols):
                    for ss in self._states:
                        vv0 = self._vars_lrct[(ll + 0, rr, cc, ss)]
                        vv1 = self._vars_lrct[(ll + 1, rr, cc, ss)]
                        self._solver.cnstr_implies_disj(vv0, True, [vv1] + all_changes_rc[(rr, cc)], True, None)
                        # TODO needed?
                        self._solver.cnstr_implies_disj(vv0, False, [vv1] + all_changes_rc[(rr, cc)], [False] + [True] * len(all_changes_rc[(rr, cc)]), None)

        if mkiii_info.custom:
            mkiii_info.custom(CustomInfo(self._solver, self._rng, self._vars_lrct, self._rows, self._cols, self._layers))

    def get_result(self):
        result_info = super().get_result()
        result_info.execution_info = self._get_execution()
        return result_info

    def _get_execution(self):
        steps = []

        for ll in range(self._layers):
            step_info = util_common.ExecutionStepInfo()
            steps.append(step_info)

            if not self._group_names:
                step_info.name = None
            elif ll == 0:
                step_info.name = 'initial'
            else:
                if self._vars_pri is not None: # RR_ORD_PRI
                    inds_pri = self._vars_pri[(ll - 1)]
                    util_common.check(len(inds_pri) == len(self._group_names), 'pri and name length mismatch')
                    pri_name = None
                    for vv, name in zip(inds_pri, self._group_names):
                        if self._solver.get_var(vv):
                            util_common.check(pri_name is None, 'multiple pri set')
                            pri_name = name
                    if pri_name is None:
                        pri_name = 'none'
                    step_info.name = pri_name
                else: # RR_ORD_SEQ, RR_ORD_ONE
                    step_info.name = self._group_names[(ll - 1) % len(self._group_names)]

            changes = []
            for cvvs, crcs in self._change_vars_rcs[ll]:
                changed = True
                for vv in cvvs:
                    if not self._solver.get_var(vv):
                        changed = False
                if changed:
                    changes.append(crcs)
            step_info.changes = changes

            text_level = []
            for rr in range(self._rows):
                level_row = []
                for cc in range(self._cols):
                    use_ss = None
                    for ss in self._states:
                        vv = self._vars_lrct[(ll, rr, cc, ss)]
                        if self._solver.get_var(vv):
                            util_common.check(use_ss is None, 'multiple states set')
                            use_ss = ss
                    util_common.check(use_ss is not None, 'no state set')
                    level_row.append(use_ss)
                text_level.append(level_row)
            step_info.text_level = text_level

            if self._scheme_info.tileset.tile_to_image is None:
                step_info.image_level = None
            else:
                tile_level = []
                for rr in range(self._rows):
                    level_row = []
                    for cc in range(self._cols):
                        text = text_level[rr][cc]
                        level_row.append(self._text_to_tile[text] if text in self._text_to_tile else util_common.VOID_TILE)
                    tile_level.append(level_row)
                step_info.image_level = util_common.tile_level_to_image_level(tile_level, self._scheme_info.tileset)

            if self._vars_term is None or ll == 0:
                step_info.term = None
                step_info.first_term = None

            else:
                prev_term = False if ll == 1 else self._solver.get_var(self._vars_term[ll - 1])
                curr_term = self._solver.get_var(self._vars_term[ll])

                if prev_term:
                    util_common.check(curr_term, 'term unset')

                step_info.term = curr_term

                if curr_term and not prev_term:
                    step_info.first_term = True
                else:
                    step_info.first_term = False

        return steps
