import argparse
import util_common



RMOVE_MAZE               = 'maze'
RMOVE_MAZE_BLINK         = 'maze-blink'
RMOVE_DRILLER            = 'driller'
RMOVE_TOMB               = 'tomb'
RMOVE_TOMB_FULL_50       = 'tomb-full-50'
RMOVE_CLIMB              = 'climb'
RMOVE_SUPERCAT           = 'supercat'
RMOVE_SUPERCAT_NEW       = 'supercat-new'
RMOVE_PLATFORM           = 'platform'
RMOVE_PLATFORM_HIGHJUMP  = 'platform-highjump'
RMOVE_PLATFORM_BLINK     = 'platform-blink'
RMOVE_LIST               = [RMOVE_MAZE, RMOVE_MAZE_BLINK, RMOVE_DRILLER, RMOVE_TOMB, RMOVE_TOMB_FULL_50, RMOVE_SUPERCAT, RMOVE_SUPERCAT_NEW, RMOVE_CLIMB, RMOVE_PLATFORM, RMOVE_PLATFORM_HIGHJUMP, RMOVE_PLATFORM_BLINK]

RSGLOC_ALL                = 'all'
RSGLOC_L_R                = 'l-r'
RSGLOC_B_T                = 'b-t'
RSGLOC_T_B                = 't-b'
RSGLOC_TL_BR              = 'tl-br'
RSGLOC_TR_BL              = 'tr-bl'
RSGLOC_BL_TR              = 'bl-tr'
RSGLOC_BR_TL              = 'br-tl'
RSGLOC_LIST = [RSGLOC_ALL, RSGLOC_L_R, RSGLOC_B_T, RSGLOC_T_B, RSGLOC_TL_BR, RSGLOC_TR_BL, RSGLOC_BL_TR, RSGLOC_BR_TL]

RPLOC_ALL                = 'all'
RPLOC_SET                = 'set'
RPLOC_L                  = 'l'
RPLOC_R                  = 'r'
RPLOC_B                  = 'b'
RPLOC_T                  = 't'
RPLOC_TL                 = 'tl'
RPLOC_TR                 = 'tr'
RPLOC_BL                 = 'bl'
RPLOC_BR                 = 'br'
RPLOC_DICT = {
    RPLOC_ALL: 0,
    RPLOC_SET: 2,
    RPLOC_L: 1,
    RPLOC_R: 1,
    RPLOC_B: 1,
    RPLOC_T: 1,
    RPLOC_TL: 1,
    RPLOC_TR: 1,
    RPLOC_BL: 1,
    RPLOC_BR: 1
}



def get_reach_junction_start_goal_setups(parser, name, args):
    reach_start_setup = util_common.ReachJunctionSetup()
    reach_goal_setup = util_common.ReachJunctionSetup()

    reach_start_setup.text = util_common.START_TEXT
    reach_goal_setup.text = util_common.GOAL_TEXT

    if args[0] not in RSGLOC_LIST:
        parser.error(name + '[0] must be in ' + ','.join(RSGLOC_LIST))

    if args[0] in [RSGLOC_ALL]:
        reach_start_setup.loc = args[0]
        reach_goal_setup.loc = args[0]
    else:
        reach_start_setup.loc, reach_goal_setup.loc = args[0].split('-')

    if len(args[1:]) != RPLOC_DICT[reach_start_setup.loc] or len(args[1:]) != RPLOC_DICT[reach_goal_setup.loc]:
        parser.error(name + '[1:] incorrect length')

    reach_start_setup.loc_params = []
    reach_goal_setup.loc_params = []
    for rg in args[1:]:
        if not rg.isnumeric():
            parser.error(name + '[1:] must all be integer')
        reach_start_setup.loc_params.append(int(rg))
        reach_goal_setup.loc_params.append(int(rg))

    return [reach_start_setup, reach_goal_setup]

def get_reach_junction_setup(parser, name, args):
    reach_junction_setup = util_common.ReachJunctionSetup()

    reach_junction_setup.text = args[0]

    if args[1] not in RPLOC_DICT:
        parser.error(name + '[1] must be in ' + ','.join(RPLOC_DICT.keys()))
    reach_junction_setup.loc = args[1]

    if len(args[2:]) != RPLOC_DICT[reach_junction_setup.loc]:
        parser.error(name + '[2:] incorrect length')

    reach_junction_setup.loc_params = []
    for rg in args[2:]:
        if not rg.isnumeric():
            parser.error(name + '[2:] must all be integer')
        reach_junction_setup.loc_params.append(int(rg))

    return reach_junction_setup

def get_reach_junction_info(reach_junction_setup, rows, cols, scheme_info):
    util_common.check(scheme_info.tileset.tile_to_text is not None, 'reachability only for (text) level generation')

    reach_junction_info = util_common.ReachJunctionInfo()

    reach_junction_info.text = reach_junction_setup.text
    reach_junction_info.rcs = []

    def r_all(_locs):
        for _rr in range(rows):
            for _cc in range(cols):
                _locs.append((_rr, _cc))

    def r_set(_locs, _lr, _lc):
        _locs.append((_lr, _lc))

    def r_left(_locs, _sz):
        for _rr in range(rows):
            for _cc in range(_sz):
                _locs.append((_rr, _cc))

    def r_right(_locs, _sz):
        for _rr in range(rows):
            for _cc in range(_sz):
                _locs.append((_rr, cols - 1 - _cc))

    def r_bottom(_locs, _sz):
        for _rr in range(_sz):
            for _cc in range(cols):
                _locs.append((rows - 1 - _rr, _cc))

    def r_top(_locs, _sz):
        for _rr in range(_sz):
            for _cc in range(cols):
                _locs.append((_rr, _cc))

    def r_topleft(_locs, _szr, _szc):
        for _rr in range(_szr):
            for _cc in range(_szc):
                _locs.append((_rr, _cc))

    def r_topright(_locs, _szr, _szc):
        for _rr in range(_szr):
            for _cc in range(_szc):
                _locs.append((_rr, cols - 1 - _cc))

    def r_botleft(_locs, _szr, _szc):
        for _rr in range(_szr):
            for _cc in range(_szc):
                _locs.append((rows - 1 - _rr, _cc))

    def r_botright(_locs, _szr, _szc):
        for _rr in range(_szr):
            for _cc in range(_szc):
                _locs.append((rows - 1 - _rr, cols - 1 - _cc))

    if reach_junction_setup.loc == RPLOC_ALL:
        r_all(reach_junction_info.rcs)
    elif reach_junction_setup.loc == RPLOC_SET:
        r_set(reach_junction_info.rcs, reach_junction_setup.loc_params[0], reach_junction_setup.loc_params[1], reach_junction_setup.loc_params[2], reach_junction_setup.loc_params[3])
    elif reach_junction_setup.loc == RPLOC_L:
        r_left(reach_junction_info.rcs, reach_junction_setup.loc_params[0])
    elif reach_junction_setup.loc == RPLOC_R:
        r_right(reach_junction_info.rcs, reach_junction_setup.loc_params[0])
    elif reach_junction_setup.loc == RPLOC_B:
        r_bottom(reach_junction_info.rcs, reach_junction_setup.loc_params[0])
    elif reach_junction_setup.loc == RPLOC_T:
        r_top(reach_junction_info.rcs, reach_junction_setup.loc_params[0])
    elif reach_junction_setup.loc == RPLOC_TL:
        r_topleft(reach_junction_info.rcs, reach_junction_setup.loc_params[0], reach_junction_setup.loc_params[0])
    elif reach_junction_setup.loc == RPLOC_TR:
        r_topright(reach_junction_info.rcs, reach_junction_setup.loc_params[0], reach_junction_setup.loc_params[0])
    elif reach_junction_setup.loc == RPLOC_BL:
        r_botleft(reach_junction_info.rcs, reach_junction_setup.loc_params[0], reach_junction_setup.loc_params[0])
    elif reach_junction_setup.loc == RPLOC_BR:
        r_botright(reach_junction_info.rcs, reach_junction_setup.loc_params[0], reach_junction_setup.loc_params[0])
    else:
        util_common.check(False, 'junction_loc ' + reach_junction_setup.loc)

    reach_junction_info.game_to_junction_tile = {}

    for game in scheme_info.game_to_tag_to_tiles:
        game_junction_tile = None

        for tag, tiles in scheme_info.game_to_tag_to_tiles[game].items():
            for tile in tiles:
                text = scheme_info.tileset.tile_to_text[tile]
                if text == reach_junction_setup.text:
                    util_common.check(game_junction_tile is None, 'multiple tiles with junction text ' + reach_junction_setup.text)
                    game_junction_tile = tile
        util_common.check(game_junction_tile is not None, 'no tiles with junction text ' + reach_junction_setup.text)

        reach_junction_info.game_to_junction_tile[game] = game_junction_tile

    return reach_junction_info



def default_reach_connect(game_to_reach_move, wrap_rows, wrap_cols, open_text, unreachable):
    reach_connect_setup = util_common.ReachConnectSetup()

    reach_connect_setup.src = util_common.START_TEXT
    reach_connect_setup.dst = util_common.GOAL_TEXT

    reach_connect_setup.unreachable = unreachable
    reach_connect_setup.fwdbwd_layers = None

    reach_connect_setup.sink_bottom = False
    reach_connect_setup.sink_sides = False

    reach_connect_setup.game_to_reach_move = game_to_reach_move
    reach_connect_setup.missing_aux_closed = False
    reach_connect_setup.wrap_rows = wrap_rows
    reach_connect_setup.wrap_cols = wrap_cols

    reach_connect_setup.open_text = open_text

    return reach_connect_setup

def parse_reach_connect_subargs(name, subargs):
    reach_parser = argparse.ArgumentParser(prog=name+' sub-argument', description='Reach connect sub-argument parsing.')
    reach_parser.add_argument('--src', required=True, type=str, default=None, help='Source junction.')
    reach_parser.add_argument('--dst', required=True, type=str, default=None, help='Destination junction.')
    reach_parser.add_argument('--move', required=True, type=str, nargs='+', default=None, help='Use reachability move rules, from: ' + ','.join(RMOVE_LIST) + '.')
    reach_parser.add_argument('--missing-aux-closed', action='store_true', help='Treat missing locations as aux closed.')
    reach_parser.add_argument('--wrap-rows', action='store_true', help='Wrap rows in reachability.')
    reach_parser.add_argument('--wrap-cols', action='store_true', help='Wrap columns in reachability.')
    reach_parser.add_argument('--open', type=str, help='Use specified open tiles.')
    reach_parser.add_argument('--unreachable', action='store_true', help='Generate levels with unreachable goals.')
    reach_parser.add_argument('--fwdbwd-layers', type=int, help='Use forward/backward reachability, with given number of layers.')
    reach_parser.add_argument('--sink-bottom', action='store_true', help='Bottom side is sink.')
    reach_parser.add_argument('--sink-sides', action='store_true', help='All sides are sinks.')
    reach_args = reach_parser.parse_args(subargs)

    util_common.check(reach_args.fwdbwd_layers is None or reach_args.fwdbwd_layers >= 2, '--fwdbwd-layers must be >= 2')

    reach_connect_setup = util_common.ReachConnectSetup()

    reach_connect_setup.src = reach_args.src
    reach_connect_setup.dst = reach_args.dst

    reach_connect_setup.unreachable = reach_args.unreachable
    reach_connect_setup.fwdbwd_layers = reach_args.fwdbwd_layers

    reach_connect_setup.sink_bottom = reach_args.sink_bottom
    reach_connect_setup.sink_sides = reach_args.sink_sides

    reach_connect_setup.game_to_reach_move = util_common.arg_list_to_dict_options(reach_parser, name+' sub-argument --move', reach_args.move, RMOVE_LIST)
    reach_connect_setup.missing_aux_closed = reach_args.missing_aux_closed
    reach_connect_setup.wrap_rows = reach_args.wrap_rows
    reach_connect_setup.wrap_cols = reach_args.wrap_cols

    reach_connect_setup.open_text = reach_args.open if reach_args.open is not None else util_common.OPEN_TEXT

    return reach_connect_setup

def get_move_template(reach_move):
    move_template = []

    if reach_move in [RMOVE_MAZE, RMOVE_MAZE_BLINK]:
        move_template.append(((-1,  0), [], [], [], []))
        move_template.append((( 1,  0), [], [], [], []))
        move_template.append((( 0, -1), [], [], [], []))
        move_template.append((( 0,  1), [], [], [], []))

        if reach_move == RMOVE_MAZE_BLINK:
            BLINK_WIDTH = 3
            brng1 = list(range(1, BLINK_WIDTH))
            brng2 = list(range(0, BLINK_WIDTH))
            move_template.append(((-BLINK_WIDTH,            0), [], [], [(-ii,   0) for ii in brng1], [(-ii,  -1) for ii in brng2] + [(-ii,   1) for ii in brng2]))
            move_template.append((( BLINK_WIDTH,            0), [], [], [( ii,   0) for ii in brng1], [( ii,  -1) for ii in brng2] + [( ii,   1) for ii in brng2]))
            move_template.append((( 0,           -BLINK_WIDTH), [], [], [( 0,  -ii) for ii in brng1], [( -1, -ii) for ii in brng2] + [(  1, -ii) for ii in brng2]))
            move_template.append((( 0,            BLINK_WIDTH), [], [], [( 0,   ii) for ii in brng1], [( -1,  ii) for ii in brng2] + [(  1,  ii) for ii in brng2]))

    elif reach_move in [RMOVE_DRILLER]:
        move_template.append((( 1,  0), [], [], [], []))
        move_template.append((( 0, -1), [], [], [], []))
        move_template.append((( 0,  1), [], [], [], []))

    elif reach_move in [RMOVE_TOMB, RMOVE_TOMB_FULL_50]:
        for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            if reach_move == RMOVE_TOMB:
                steps = [1, 2, 4, 6, 10]
            elif reach_move == RMOVE_TOMB_FULL_50:
                steps = list(range(1, 51))

            for ii in steps:
                dest = (dr * ii, dc * ii)
                need_open_path = [(dr * jj, dc * jj) for jj in range(1, ii)]
                need_open_aux = []
                need_closed_path = []
                need_closed_aux = [(dr * (ii + 1), dc * (ii + 1))]
                move_template.append((dest, need_open_path, need_open_aux, need_closed_path, need_closed_aux))

    elif reach_move in [RMOVE_CLIMB, RMOVE_SUPERCAT, RMOVE_SUPERCAT_NEW]:
        # fall
        move_template.append(((1,  0), [],       [], [], []))
        move_template.append(((1,  1), [(1, 0)], [], [], []))
        move_template.append(((1, -1), [(1, 0)], [], [], []))

        # walk
        move_template.append(((0,  1), [], [], [], [(1, 0)]))
        move_template.append(((0, -1), [], [], [], [(1, 0)]))

        # wall climb (only starting from ground, no continue onto ledge)
        for dc in [1, -1]:
            for ii in range(1, 8):
                dest = (-ii, 0)
                need_open_path = [(-jj, 0) for jj in range(1, ii)]
                need_open_aux = []
                need_closed_path = []
                need_closed_aux = [(1, 0)] + [(-jj, dc) for jj in range(ii + 1)]
                move_template.append((dest, need_open_path, need_open_aux, need_closed_path, need_closed_aux))

        # wall jump (requires extra closed tiles to prevent continuing jump/fall in same direction, open to prevent jump from ground)
        jump_arc = [(0, 1), (-1,  1), (-1,  2), (-2,  2), (-2,  3), (-3,  3), (-3,  4)]
        for dc in [1, -1]:
            arc_start = 0 if reach_move == RMOVE_SUPERCAT else 1
            for ii in range(arc_start, len(jump_arc)):
                dest = (jump_arc[ii][0], dc * jump_arc[ii][1])
                need_open_path =  [(jr, dc * jc) for jr, jc in jump_arc[:ii]]
                need_open_aux = [(1, 0)]
                need_closed_path = []
                need_closed_aux = [(-1, -dc), (0, -dc), (1, -dc)]
                move_template.append((dest, need_open_path, need_open_aux, need_closed_path, need_closed_aux))

        if reach_move in [RMOVE_SUPERCAT, RMOVE_SUPERCAT_NEW]:
            # dash jump
            arc_start = 0 if reach_move == RMOVE_SUPERCAT else 1
            jump_arc = [(0, 1), (-1,  1), (-1,  2), (-2,  2), (-2,  3), (-2,  4), (-2,  5)]
            for dc in [1, -1]:
                for ii in range(arc_start, len(jump_arc)):
                    dest = (jump_arc[ii][0], dc * jump_arc[ii][1])
                    need_open_path = [(jr, dc * jc) for jr, jc in jump_arc[:ii]]
                    if reach_move == RMOVE_SUPERCAT:
                        need_open_aux = [(1, dc)]
                    elif reach_move == RMOVE_SUPERCAT_NEW:
                        need_open_aux = [(1, dc), (-1, 0)]
                    else:
                        util_common.check(False, 'reach_move')
                    need_closed_path = []
                    need_closed_aux = [(1, 0)]
                    move_template.append((dest, need_open_path, need_open_aux, need_closed_path, need_closed_aux))

    elif reach_move in [RMOVE_PLATFORM, RMOVE_PLATFORM_HIGHJUMP, RMOVE_PLATFORM_BLINK]:
        # fall
        move_template.append(((1,  0), [],       [], [], []))
        move_template.append(((1,  1), [(1, 0)], [], [], []))
        move_template.append(((1, -1), [(1, 0)], [], [], []))

        # walk
        move_template.append(((0,  1), [], [], [], [(1, 0)]))
        move_template.append(((0, -1), [], [], [], [(1, 0)]))

        # jump
        jump_arcs = [
            [(-1,  0), (-2,  0), (-3,  0), (-4,  0), (-4,  1)],
            ##[(-1,  0), (-2,  0), (-3,  0), (-3,  1), (-4,  1), (-4,  2)],
            ##[(-1,  0), (-2,  0), (-2,  1), (-3,  1), (-3,  2), (-4,  2), (-4,  3)],
            [(-1,  0), (-1,  1), (-2,  1), (-2,  2), (-3,  2), (-3,  3), (-4,  3), (-4,  4)],
        ]
        for jump_arc in jump_arcs:
            for dc in [1, -1]:
                for ii in range(len(jump_arc)):
                    dest = (jump_arc[ii][0], dc * jump_arc[ii][1])
                    need_open_path = [(jrr, dc * jcc) for jrr, jcc in jump_arc[:ii]]
                    need_open_aux = []
                    need_closed_path = []
                    need_closed_aux = [(1, 0)]
                    move_template.append((dest, need_open_path, need_open_aux, need_closed_path, need_closed_aux))

        if reach_move == RMOVE_PLATFORM_HIGHJUMP:
            HIGHJUMP_HEIGHT = 8
            move_template.append(((-HIGHJUMP_HEIGHT,  0), [(-ii, 0) for ii in range(1, HIGHJUMP_HEIGHT)], [], [], [(1, 0)]))
        elif reach_move == RMOVE_PLATFORM_BLINK:
            BLINK_WIDTH = 3
            move_template.append(((0,  BLINK_WIDTH), [], [], [(0,  ii) for ii in range(1, BLINK_WIDTH)], [(1, 0)]))
            move_template.append(((0, -BLINK_WIDTH), [], [], [(0, -ii) for ii in range(1, BLINK_WIDTH)], [(1, 0)]))

    else:
        util_common.check(False, 'reach_move ' + reach_move)

    move_template_uniq = []
    for arc in move_template:
        if arc not in move_template_uniq:
            move_template_uniq.append(arc)

    return move_template_uniq

def get_move_info(reach_move, missing_aux_closed, wrap_rows, wrap_cols):
    move_info = util_common.ReachMoveInfo()
    move_info.move_template = get_move_template(reach_move)
    move_info.missing_aux_closed = missing_aux_closed
    move_info.wrap_rows = wrap_rows
    move_info.wrap_cols = wrap_cols
    return move_info

def get_game_to_move_info(reach_connect_setup):
    game_to_move_info = {}
    for game, reach_move in reach_connect_setup.game_to_reach_move.items():
        game_to_move_info[game] = get_move_info(reach_move, reach_connect_setup.missing_aux_closed, reach_connect_setup.wrap_rows, reach_connect_setup.wrap_cols)
    return game_to_move_info

def get_reach_connect_info(reach_connect_setup, rows, cols, scheme_info):
    util_common.check(scheme_info.tileset.tile_to_text is not None, 'reachability only for (text) level generation')

    reach_connect_info = util_common.ReachConnectInfo()

    reach_connect_info.src = reach_connect_setup.src
    reach_connect_info.dst = reach_connect_setup.dst

    reach_connect_info.unreachable = reach_connect_setup.unreachable
    reach_connect_info.fwdbwd_layers = reach_connect_setup.fwdbwd_layers

    reach_connect_info.sink_bottom = reach_connect_setup.sink_bottom
    reach_connect_info.sink_sides = reach_connect_setup.sink_sides

    reach_connect_info.game_to_move_info = get_game_to_move_info(reach_connect_setup)

    reach_connect_info.game_to_open_tiles = {}

    for game in reach_connect_setup.game_to_reach_move:
        game_open_tiles = []

        for tag, tiles in scheme_info.game_to_tag_to_tiles[game].items():
            for tile in tiles:
                text = scheme_info.tileset.tile_to_text[tile]
                if text in reach_connect_setup.open_text:
                    game_open_tiles.append(tile)
        util_common.check(len(game_open_tiles) > 0, 'no tiles with open text')

        reach_connect_info.game_to_open_tiles[game] = game_open_tiles

    return reach_connect_info
