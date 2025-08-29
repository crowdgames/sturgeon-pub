import argparse, os, pickle, pprint, sys
import util_common



def tilediff2scheme(tile_info, offset_row, context_delta, games):
    ti = tile_info

    si = util_common.SchemeInfo()

    si.tileset = ti.tileset

    si.game_to_tag_to_tiles = {}

    si.count_info = None

    si.pattern_info = util_common.SchemePatternInfo()

    si.pattern_info.game_to_patterns = {}

    si.pattern_info.stride_rows = 1
    si.pattern_info.stride_cols = 1
    si.pattern_info.dr_lo = 0
    si.pattern_info.dr_hi = 0
    si.pattern_info.dc_lo = 0
    si.pattern_info.dc_hi = 0

    tile_levels, tag_levels, game_levels = [], [], []
    for tli in ti.levels:
        tile_level = tli.tiles
        tag_level = tli.tags
        game_level = tli.games

        tile_levels.append(tile_level)
        tag_levels.append(tag_level)
        game_levels.append(game_level)

    def get_game(_level, _rows, _cols, _rr, _cc):
        return _level[max(0, min(_rr, _rows - 1))][max(0, min(_cc, _cols - 1))]

    def get_tile(_level, _rows, _cols, _rr, _cc):
        if _rr <= -1 or _rr >= _rows or _cc <= -1 or _cc >= cols:
            return util_common.VOID_TILE
        else:
            return _level[_rr][_cc]

    def update_dr_dc(_pattern_template):
        for _dr, _dc in _pattern_template:
            si.pattern_info.dr_lo = min(si.pattern_info.dr_lo, _dr)
            si.pattern_info.dr_hi = max(si.pattern_info.dr_hi, _dr)
            si.pattern_info.dc_lo = min(si.pattern_info.dc_lo, _dc)
            si.pattern_info.dc_hi = max(si.pattern_info.dc_hi, _dc)

    for tile_level, tag_level, game_level in zip(tile_levels, tag_levels, game_levels):
        rows = len(tile_level)
        cols = len(tile_level[0])

        util_common.print_tile_level(tile_level)
        print()

        for rr in range(rows):
            for cc in range(cols):
                tile = tile_level[rr][cc]
                tag = tag_level[rr][cc]
                game = game_level[rr][cc]

                if game not in games:
                    continue

                util_common.check(game != util_common.VOID_TEXT, 'void game')
                util_common.check((tile == util_common.VOID_TILE) == (tag == util_common.VOID_TEXT), 'void')
                if tile == util_common.VOID_TILE:
                    continue

                if game not in si.game_to_tag_to_tiles:
                    si.game_to_tag_to_tiles[game] = {}
                if tag not in si.game_to_tag_to_tiles[game]:
                    si.game_to_tag_to_tiles[game][tag] = {}
                si.game_to_tag_to_tiles[game][tag][tile] = None

                if game not in si.pattern_info.game_to_patterns:
                    si.pattern_info.game_to_patterns[game] = {}

        for row_delta in range(offset_row, rows, offset_row):
            row_range = list(range(row_delta, min(row_delta + offset_row, rows - offset_row)))
            col_range = list(range(-1, cols + 1))

            for rr in row_range:
                for cc in col_range:
                    game = get_game(game_level, rows, cols, rr, cc)

                    if game not in games:
                        continue

                    tile0 = get_tile(tile_level, rows, cols, rr, cc)

                    pattern_template_in = ((0, 0),)
                    pattern_in = (tile0,)

                    for pattern_group_out, group_offset_row in [('diff-next', offset_row), ('diff-prev', -offset_row)]:
                        tile1 = get_tile(tile_level, rows, cols, rr + group_offset_row, cc)

                        if tile0 == tile1:
                            pattern_template_out = ((group_offset_row, 0),)
                            pattern_out = (tile1,)

                        else:
                            delta_tiles = {}
                            for drr in row_range:
                                for dcc in col_range:
                                    dtile0 = get_tile(tile_level, rows, cols, drr, dcc)
                                    dtile1 = get_tile(tile_level, rows, cols, drr + group_offset_row, dcc)
                                    if dtile0 != dtile1:
                                        for crr, ccc in [(0, 0)] + context_delta:
                                            orr = drr + crr
                                            occ = dcc + ccc
                                            otile0 = get_tile(tile_level, rows, cols, orr, occ)
                                            otile1 = get_tile(tile_level, rows, cols, orr + group_offset_row, occ)
                                            if (orr, occ) != (rr, cc):
                                                delta_tiles[(orr - rr, occ - cc)] = otile0
                                            delta_tiles[(orr - rr + group_offset_row, occ - cc)] = otile1
                            pattern_template_out = tuple(delta_tiles.keys())
                            pattern_out = tuple(delta_tiles.values())

                        update_dr_dc(pattern_template_in)
                        update_dr_dc(pattern_template_out)

                        if pattern_template_in not in si.pattern_info.game_to_patterns[game]:
                            si.pattern_info.game_to_patterns[game][pattern_template_in] = {}

                        if pattern_in not in si.pattern_info.game_to_patterns[game][pattern_template_in]:
                            si.pattern_info.game_to_patterns[game][pattern_template_in][pattern_in] = {}

                        if pattern_group_out not in si.pattern_info.game_to_patterns[game][pattern_template_in][pattern_in]:
                            si.pattern_info.game_to_patterns[game][pattern_template_in][pattern_in][pattern_group_out] = {}

                        if pattern_template_out not in si.pattern_info.game_to_patterns[game][pattern_template_in][pattern_in][pattern_group_out]:
                            si.pattern_info.game_to_patterns[game][pattern_template_in][pattern_in][pattern_group_out][pattern_template_out] = {}

                        si.pattern_info.game_to_patterns[game][pattern_template_in][pattern_in][pattern_group_out][pattern_template_out][pattern_out] = None

    util_common.summarize_scheme_info(si, sys.stdout)

    return si



if __name__ == '__main__':
    util_common.timer_start()

    parser = argparse.ArgumentParser(description='Create scheme from tile info and (optionally) tag level.')
    parser.add_argument('--outfile', required=True, type=str, help='Output scheme file.')
    parser.add_argument('--tilefile', required=True, type=str, help='Input tile file.')
    parser.add_argument('--context', type=str, help='Context deltas to use for diffs.')
    parser.add_argument('--game', required=True, type=str, nargs='+', help='Game(s) to diff for.')
    parser.add_argument('--diff-offset-row', required=True, type=int)
    parser.add_argument('--quiet', action='store_true', help='Reduce output.')
    args = parser.parse_args()

    if args.quiet:
        sys.stdout = open(os.devnull, 'w')

    with util_common.openz(args.tilefile, 'rb') as f:
        tile_info = pickle.load(f)

    context = []
    if args.context is not None:
        for delta_str in args.context.split(','):
            delta = tuple([int(elem) for elem in delta_str.split()])
            util_common.check(len(delta) == 2, f'wrong delta length: {delta}')
            context.append(delta)

    scheme_info = tilediff2scheme(tile_info, args.diff_offset_row, context, args.game)
    with util_common.openz(args.outfile, 'wb') as f:
        pickle.dump(scheme_info, f)
