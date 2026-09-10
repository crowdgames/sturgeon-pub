import argparse, json, os
import util_common, util_path, util_reach



def level2concat(text_levels, xform_rotate, xform_flip_rows, xform_flip_cols, term_inst, across_cols, pad_rows, pad_cols, pad_around, game_lvl, game_pad):
    concat_text = []
    concat_game = None
    rows, cols = None, None

    pad_rows = 0 if pad_rows is None else pad_rows
    pad_cols = 0 if pad_cols is None else pad_cols

    for ii in range(term_inst - 1):
        text_levels.append(text_levels[-1])

    if game_lvl is not None or game_pad is not None:
        util_common.check(game_lvl is not None, 'game')
        util_common.check(game_pad is not None, 'game')
        concat_game = []

    def game_ind(_ii, _jj):
        if _jj == 0:
            if _ii == 0:
                return 0
            elif _ii + 1 < len(text_levels):
                return 3
            else:
                return 6
        elif _jj + 1 < across_cols:
            if _ii == 0:
                return 1
            elif _ii + 1 < len(text_levels):
                return 4
            else:
                return 7
        else:
            if _ii == 0:
                return 2
            elif _ii + 1 < len(text_levels):
                return 5
            else:
                return 8

    for ii, text_level in enumerate(text_levels):
        if pad_around is not None:
            if len(pad_around) in [1, 8]:
                if len(pad_around) == 1:
                    pad_around = pad_around * 8
                text_level = util_common.xform_grid_pad_around(text_level, *pad_around)
            elif len(pad_around) == 2:
                text_level = util_common.xform_grid_pad_side(text_level, *pad_around)
            else:
                util_common.check(False, 'unrecognized pad')

        for xx in range(xform_rotate):
            text_level = util_common.xform_grid_rotate_cw(text_level)
        if xform_flip_rows:
            text_level = util_common.xform_grid_flip_rows(text_level)
        if xform_flip_cols:
            text_level = util_common.xform_grid_flip_cols(text_level)

        curr_rows = len(text_level)
        curr_cols = len(text_level[0])

        if ii == 0:
            rows, cols = curr_rows, curr_cols
        else:
            util_common.check((rows, cols) == (curr_rows, curr_cols), 'level sizes do not match')
            concat_text += util_common.make_grid(pad_rows, len(concat_text[-1]), util_common.VOID_TEXT)
            if concat_game is not None:
                concat_game += util_common.make_grid(pad_rows, len(concat_game[-1]), game_pad)

        curr_concat_text = list(text_level)
        for jj in range(across_cols - 1):
            curr_concat_text = util_common.grid_cat_col(curr_concat_text, util_common.make_grid(rows, pad_cols, util_common.VOID_TEXT))
            curr_concat_text = util_common.grid_cat_col(curr_concat_text, list(text_level))
        concat_text += curr_concat_text

        if concat_game is not None:
            curr_concat_game = util_common.make_grid(rows, cols, game_lvl[game_ind(ii, 0)])
            for jj in range(across_cols - 1):
                curr_concat_game = util_common.grid_cat_col(curr_concat_game, util_common.make_grid(rows, pad_cols, game_pad))
                curr_concat_game = util_common.grid_cat_col(curr_concat_game, util_common.make_grid(rows, cols, game_lvl[game_ind(ii, jj + 1)]))
            concat_game += curr_concat_game

    return concat_text, concat_game



if __name__ == '__main__':
    util_common.timer_start()

    parser = argparse.ArgumentParser(description='Concatenate multiple levels into a single level.')
    parser.add_argument('--outfile', required=True, type=str, help='File to write to.')
    parser.add_argument('--term-inst', type=int, default=1, help='Number of instances of last level to include.')
    parser.add_argument('--pad-around', type=str, nargs='+', help='Pad border around individual levels.')
    parser.add_argument('--pad-rows', type=int, help='Pad rows between individual levels.')
    parser.add_argument('--pad-cols', type=int, help='Pad cols between individual levels.')
    parser.add_argument('--game', type=str, nargs='+', help='Game to use for initial, interior, final levels, and pad between.')
    parser.add_argument('--xform-rotate', type=int, default=0, help='Times to rotate level.')
    parser.add_argument('--xform-flip-rows', action='store_true', help='Flip level rows.')
    parser.add_argument('--xform-flip-cols', action='store_true', help='Flip level cols.')
    parser.add_argument('--across-cols', type=int, default=1, help='Spread slices across columns axis.')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--size', type=int, nargs=2, help='Level size (if no tag or game file provided.')
    group.add_argument('--textfile', type=str, nargs='+', help='Input text file.')
    group.add_argument('--jsonfile', type=str, help='Input json file.')
    args = parser.parse_args()

    if args.size is not None:
        rows, cols = args.size
        text_levels = [util_common.make_grid(rows, cols, util_common.DEFAULT_TEXT)]
    elif args.textfile is not None:
        text_levels = [util_common.read_text_level(textfile, False) for textfile in args.textfile]
    elif args.jsonfile is not None:
        with open(args.jsonfile, 'rt') as f:
            text_levels = json.load(f)

    if args.game is not None:
        if len(args.game) == 4:
            game_init, game_intr, game_fini, game_pad = args.game
            game_lvl = [game_init, game_init, game_init, game_intr, game_intr, game_intr, game_fini, game_fini, game_fini]
        elif len(args.game) == 10:
            game_lvl = args.game[:9]
            game_pad = args.game[9]
        else:
            util_common.check(False, '--game must be length 4 or 10')
    else:
        game_lvl = None
        game_pad = None

    concat_text, concat_game = level2concat(text_levels, args.xform_rotate, args.xform_flip_rows, args.xform_flip_cols, args.term_inst, args.across_cols, args.pad_rows, args.pad_cols, args.pad_around, game_lvl, game_pad)

    with util_common.openz(args.outfile, 'wt') as f:
        util_common.print_text_level(concat_text, outstream=f)

    if concat_game is not None:
        gameoutfile = os.path.splitext(args.outfile)[0] + '.game'
        with util_common.openz(gameoutfile, 'wt') as f:
            util_common.print_text_level(concat_game, outstream=f)

    util_common.exit_solution_found()
