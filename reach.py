import util



RMOVE_MAZE               = 'maze'
RMOVE_TOMB               = 'tomb'
RMOVE_CLIMB              = 'climb'
RMOVE_SUPERCAT           = 'supercat'
RMOVE_SUPERCAT2          = 'supercat2'
RMOVE_PLATFORM           = 'platform'
RMOVE_LIST               = [RMOVE_MAZE, RMOVE_TOMB, RMOVE_SUPERCAT, RMOVE_SUPERCAT2, RMOVE_CLIMB, RMOVE_PLATFORM]

RGOAL_ALL                = 'all'
RGOAL_SET                = 'set'
RGOAL_L_R                = 'l-r'
RGOAL_B_T                = 'b-t'
RGOAL_T_B                = 't-b'
RGOAL_TL_BR              = 'tl-br'
RGOAL_TR_BL              = 'tr-bl'
RGOAL_BL_TR              = 'bl-tr'
RGOAL_BR_TL              = 'br-tl'
RGOAL_DICT = {
    RGOAL_ALL: 0,
    RGOAL_SET: 4,
    RGOAL_L_R: 1,
    RGOAL_B_T: 1,
    RGOAL_T_B: 1,
    RGOAL_TL_BR: 1,
    RGOAL_TR_BL: 1,
    RGOAL_BL_TR: 1,
    RGOAL_BR_TL: 1
}



def get_move_template(reach_move):
    move_template = []

    if reach_move == RMOVE_MAZE:
        move_template.append(((-1,  0), [], [], []))
        move_template.append((( 1,  0), [], [], []))
        move_template.append((( 0, -1), [], [], []))
        move_template.append((( 0,  1), [], [], []))

    elif reach_move == RMOVE_TOMB:
        for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            for ii in [1, 2, 4, 6, 10]:
                dest = (dr * ii, dc * ii)
                need_open_path = [(dr * jj, dc * jj) for jj in range(1, ii)]
                need_open_aux = []
                need_closed = [(dr * (ii + 1), dc * (ii + 1))]
                move_template.append((dest, need_open_path, need_open_aux, need_closed))

    elif reach_move in [RMOVE_CLIMB, RMOVE_SUPERCAT, RMOVE_SUPERCAT2]:
        # fall
        move_template.append(((1,  0), [], [], []))
        move_template.append(((1,  1), [(1, 0)], [], []))
        move_template.append(((1, -1), [(1, 0)], [], []))

        # walk
        move_template.append(((0,  1), [], [], [(1, 0)]))
        move_template.append(((0, -1), [], [], [(1, 0)]))

        # wall climb (only starting from ground, no continue onto ledge)
        for dc in [1, -1]:
            for ii in range(1, 8):
                dest = (-ii, 0)
                need_open_path = [(-jj, 0) for jj in range(1, ii)]
                need_open_aux = []
                need_closed = [(1, 0)] + [(-jj, dc) for jj in range(ii + 1)]
                move_template.append((dest, need_open_path, need_open_aux, need_closed))

        # wall jump (requires extra closed tiles to prevent continuing jump/fall in same direction, open to prevent jump from ground)
        jump_arc = [(0, 1), (-1,  1), (-1,  2), (-2,  2), (-2,  3), (-3,  3), (-3,  4)]
        for dc in [1, -1]:
            arc_start = 0 if reach_move == RMOVE_SUPERCAT else 1
            for ii in range(arc_start, len(jump_arc)):
                dest = (jump_arc[ii][0], dc * jump_arc[ii][1])
                need_open_path =  [(jr, dc * jc) for jr, jc in jump_arc[:ii]]
                need_open_aux = [(1, 0)]
                need_closed = [(-1, -dc), (0, -dc), (1, -dc)]
                move_template.append((dest, need_open_path, need_open_aux, need_closed))

        if reach_move in [RMOVE_SUPERCAT, RMOVE_SUPERCAT2]:
            # dash jump
            arc_start = 0 if reach_move == RMOVE_SUPERCAT else 1
            jump_arc = [(0, 1), (-1,  1), (-1,  2), (-2,  2), (-2,  3), (-2,  4), (-2,  5)]
            for dc in [1, -1]:
                for ii in range(arc_start, len(jump_arc)):
                    dest = (jump_arc[ii][0], dc * jump_arc[ii][1])
                    need_open_path = [(jr, dc * jc) for jr, jc in jump_arc[:ii]]
                    if reach_move == RMOVE_SUPERCAT:
                        need_open_aux = [(1, dc)]
                    elif reach_move == RMOVE_SUPERCAT2:
                        need_open_aux = [(1, dc), (-1, 0)]
                    else:
                        util.check(False, 'reach_move')
                    need_closed = [(1, 0)]
                    move_template.append((dest, need_open_path, need_open_aux, need_closed))

    elif reach_move == RMOVE_PLATFORM:
        # fall
        move_template.append(((1,  0), [], [], []))
        move_template.append(((1,  1), [(1, 0)], [], []))
        move_template.append(((1, -1), [(1, 0)], [], []))

        # walk
        move_template.append(((0,  1), [], [], [(1, 0)]))
        move_template.append(((0, -1), [], [], [(1, 0)]))

        # jump
        jump_arcs = [
            [(-1,  0), (-2,  0), (-3,  0), (-4,  0), (-4,  1)],
            [(-1,  0), (-2,  0), (-3,  0), (-4,  0), (-4, -1)],
            [(-1,  0), (-1,  1), (-2,  1), (-2,  2), (-3,  2), (-3,  3), (-4,  3), (-4,  4)],
            [(-1,  0), (-1, -1), (-2, -1), (-2, -2), (-3, -2), (-3, -3), (-4, -3), (-4, -4)],
        ]
        for jump_arc in jump_arcs:
            for ii in range(len(jump_arc)):
                dest = jump_arc[ii]
                need_open_path = [jrc for jrc in jump_arc[:ii]]
                need_open_aux = []
                need_closed = [(1, 0)]
                move_template.append((dest, need_open_path, need_open_aux, need_closed))
    else:
        util.check(False, 'reach_move ' + reach_move)

    move_template_uniq = []
    for arc in move_template:
        if arc not in move_template_uniq:
            move_template_uniq.append(arc)

    return move_template_uniq



def get_reach_info(rows, cols, reach_setup, scheme_info):
    util.check(scheme_info.tileset.tile_to_text is not None, 'reachability only for (text) level generation')

    reach_info = util.ReachabilityInfo()



    reach_info.start_rcs = []
    reach_info.goal_rcs = []

    def r_all(_st, _gl):
        for _rr in range(rows):
            for _cc in range(cols):
                _st.append((_rr, _cc))
                _gl.append((_rr, _cc))

    def r_set(_sr, _sc, _gr, _gc, _st, _gl):
        _st.append((_sr, _sc))
        _gl.append((_gr, _gc))

    def r_left_to_right(_sz, _st, _gl):
        for _rr in range(rows):
            for _cc in range(_sz):
                _st.append((_rr, _cc))
                _gl.append((_rr, cols - 1 - _cc))

    def r_bottom_to_top(_sz, _st, _gl):
        for _rr in range(_sz):
            for _cc in range(cols):
                _st.append((rows - 1 - _rr, _cc))
                _gl.append((_rr, _cc))

    def r_top_to_bottom(_sz, _st, _gl):
        for _rr in range(_sz):
            for _cc in range(cols):
                _st.append((_rr, _cc))
                _gl.append((rows - 1 - _rr, _cc))

    def r_topleft_to_botright(_szr, _szc, _st, _gl):
        for _rr in range(_szr):
            for _cc in range(_szc):
                _st.append((_rr, _cc))
                _gl.append((rows - 1 - _rr, cols - 1 - _cc))

    def r_topright_to_botleft(_szr, _szc, _st, _gl):
        for _rr in range(_szr):
            for _cc in range(_szc):
                _st.append((_rr, cols - 1 - _cc))
                _gl.append((rows - 1 - _rr, _cc))

    def r_botleft_to_topright(_szr, _szc, _st, _gl):
        for _rr in range(_szr):
            for _cc in range(_szc):
                _st.append((rows - 1 - _rr, _cc))
                _gl.append((_rr, cols - 1 - _cc))

    def r_botright_to_topleft(_szr, _szc, _st, _gl):
        for _rr in range(_szr):
            for _cc in range(_szc):
                _st.append((rows - 1 - _rr, cols - 1 - _cc))
                _gl.append((_rr, _cc))

    if reach_setup.goal_loc == RGOAL_ALL:
        r_all(reach_info.start_rcs, reach_info.goal_rcs)
    elif reach_setup.goal_loc == RGOAL_SET:
        r_set(reach_setup.goal_params[0], reach_setup.goal_params[1], reach_setup.goal_params[2], reach_setup.goal_params[3], reach_info.start_rcs, reach_info.goal_rcs)
    elif reach_setup.goal_loc == RGOAL_L_R:
        r_left_to_right(reach_setup.goal_params[0], reach_info.start_rcs, reach_info.goal_rcs)
    elif reach_setup.goal_loc == RGOAL_B_T:
        r_bottom_to_top(reach_setup.goal_params[0], reach_info.start_rcs, reach_info.goal_rcs)
    elif reach_setup.goal_loc == RGOAL_T_B:
        r_top_to_bottom(reach_setup.goal_params[0], reach_info.start_rcs, reach_info.goal_rcs)
    elif reach_setup.goal_loc == RGOAL_TL_BR:
        r_topleft_to_botright(reach_setup.goal_params[0], reach_setup.goal_params[0], reach_info.start_rcs, reach_info.goal_rcs)
    elif reach_setup.goal_loc == RGOAL_TR_BL:
        r_topright_to_botleft(reach_setup.goal_params[0], reach_setup.goal_params[0], reach_info.start_rcs, reach_info.goal_rcs)
    elif reach_setup.goal_loc == RGOAL_BL_TR:
        r_botleft_to_topright(reach_setup.goal_params[0], reach_setup.goal_params[0], reach_info.start_rcs, reach_info.goal_rcs)
    elif reach_setup.goal_loc == RGOAL_BR_TL:
        r_botright_to_topleft(reach_setup.goal_params[0], reach_setup.goal_params[0], reach_info.start_rcs, reach_info.goal_rcs)
    else:
        util.check(False, 'reach_goal_loc ' + reach_setup.goal_loc)



    reach_info.game_to_move = {}

    for game, reach_move in reach_setup.game_to_move.items():
        game_move = util.GameMoveInfo()
        reach_info.game_to_move[game] = game_move

        game_move.start_tile, game_move.goal_tile, game_move.open_tiles = None, None, []
        for tag, tiles in scheme_info.game_to_tag_to_tiles[game].items():
            for tile in tiles:
                text = scheme_info.tileset.tile_to_text[tile]
                if text == util.START_TEXT:
                    util.check(game_move.start_tile is None, 'multiple tiles with start text')
                    game_move.start_tile = tile
                if text == util.GOAL_TEXT:
                    util.check(game_move.goal_tile is None, 'multiple tiles with goal text')
                    game_move.goal_tile = tile
                if text in reach_setup.open_text:
                    game_move.open_tiles.append(tile)
        util.check(game_move.start_tile is not None, 'no tiles with start text')
        util.check(game_move.goal_tile is not None, 'no tiles with goal text')
        util.check(len(game_move.open_tiles) > 0, 'no tiles with open text')

        game_move.wrap_cols = reach_setup.wrap_cols
        game_move.move_template = get_move_template(reach_move)

    return reach_info
