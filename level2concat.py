import argparse, json, os
import util_common, util_path, util_reach



def level2concat(text_levels, xform_rotate, xform_flip_rows, xform_flip_cols, term_inst, pad_between, pad_around, pad_end, game_init, game_intr, game_fini, game_pdng):
    concat_text = None
    concat_game = None
    rows, cols = None, None

    for ii in range(term_inst - 1):
        text_levels.append(text_levels[-1])

    use_games = False
    if (game_init is not None) or (game_intr is not None) or (game_fini is not None) or (game_pdng is not None):
        util_common.check(game_init is not None, 'game')
        util_common.check(game_intr is not None, 'game')
        util_common.check(game_fini is not None, 'game')
        util_common.check(game_pdng is not None, 'game')
        use_games = True

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
            concat_text = list(text_level)
            if use_games:
                concat_game = util_common.make_grid(rows, cols, game_init)
        else:
            util_common.check((rows, cols) == (curr_rows, curr_cols), 'level sizes do not match')
            if pad_between is not None:
                concat_text += util_common.make_grid(pad_between, cols, util_common.VOID_TEXT)
            concat_text += text_level
            if use_games:
                if pad_between is not None:
                    concat_game += util_common.make_grid(pad_between, cols, game_pdng)
                if ii + 1 < len(text_levels):
                    concat_game += util_common.make_grid(rows, cols, game_intr)
                else:
                    concat_game += util_common.make_grid(rows, cols, game_fini)

    if pad_end is not None:
        if pad_between is not None:
            concat_text += util_common.make_grid(pad_between, cols, util_common.VOID_TEXT)
        concat_text += util_common.make_grid(rows, cols, pad_end)
        if use_games:
            if pad_between is not None:
                concat_game += util_common.make_grid(pad_between, cols, game_pdng)
            concat_game += util_common.make_grid(rows, cols, game_fini)

    return concat_text, concat_game



if __name__ == '__main__':
    util_common.timer_start()

    parser = argparse.ArgumentParser(description='Concatenate multiple levels into a single level.')
    parser.add_argument('--outfile', required=True, type=str, help='File to write to.')
    parser.add_argument('--term-inst', type=int, default=1, help='Number of instances of last level to include.')
    parser.add_argument('--pad-between', type=int, help='Pad between individual levels.')
    parser.add_argument('--pad-around', type=str, nargs='+', help='Pad around individual levels.')
    parser.add_argument('--pad-end', type=str, help='Pad at end.')
    parser.add_argument('--game', type=str, nargs=4, help='Game to use for initial, interior, final levels, and pad between.')
    parser.add_argument('--xform-rotate', type=int, default=0, help='Times to rotate level.')
    parser.add_argument('--xform-flip-rows', action='store_true', help='Flip level rows.')
    parser.add_argument('--xform-flip-cols', action='store_true', help='Flip level cols.')
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
        game_init, game_intr, game_fini, game_pdng = args.game
    else:
        game_init, game_intr, game_fini, game_pdng = [None] * 4

    concat_text, concat_game = level2concat(text_levels, args.xform_rotate, args.xform_flip_rows, args.xform_flip_cols, args.term_inst, args.pad_between, args.pad_around, args.pad_end, game_init, game_intr, game_fini, game_pdng)

    with util_common.openz(args.outfile, 'wt') as f:
        util_common.print_text_level(concat_text, outstream=f)

    if concat_game is not None:
        gameoutfile = os.path.splitext(args.outfile)[0] + '.game'
        with util_common.openz(gameoutfile, 'wt') as f:
            util_common.print_text_level(concat_game, outstream=f)

    util_common.exit_solution_found()
