import argparse, os, pickle, pprint, sys
import util_common



PATTERN_NEIGH_2        = [([(0, 0)], [( 0, 1)]),
                          ([(0, 0)], [( 1, 0)])]

PATTERN_NEIGH_L        = [([(0, 0)], [( 0, 1)]),
                          ([(0, 0)], [( 1, 1)]),
                          ([(0, 0)], [( 1, 0)])]

PATTERN_NEIGH_PLUS     = [([(0, 0)], [( 0,  1)]),
                          ([(0, 0)], [( 1,  0)]),
                          ([(0, 0)], [( 0, -1)]),
                          ([(0, 0)], [(-1,  0)])]

PATTERN_NEIGH_BLOCK2   = [([(0, 0), (0, 1), (1, 0), (1, 1)], [(2, 0), (2, 1)]),
                          ([(0, 0), (0, 1), (1, 0), (1, 1)], [(0, 2), (1, 2)]),
                          ([(0, 0), (0, 1), (1, 0), (1, 1)], [(1, 2), (2, 1), (2, 2)])]

PATTERN_NO_OUT_BLOCK_2  = [([(0, 0), (0, 1), (1, 0), (1, 1)], None)]

PATTERN_NO_OUT_BLOCK_3  = [([(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2), (2, 0), (2, 1), (2, 2)], None)]

PATTERN_BLOCKZ         = [([(0, 0)], [(0, 1), (1, 1)]),
                          ([(0, 0)], [(1, 0), (1, 1)])]

PATTERN_BLOCK2         = [([(0, 0)],
                           [(0, 1), (1, 1), (1, 0)])]

PATTERN_BLOCK2_INV     = [([(0, 0), (0, 1), (1, 0)],
                           [(1, 1)])]

PATTERN_BLOCK3         = [([(0, 0)],
                           [(0, 1), (0, 2), (1, 0), (1, 1), (1, 2), (2, 0), (2, 1), (2, 2)])]

PATTERN_RING           = [([(0, 0)],
                           [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)])]

PATTERN_DIAMOND        = [([(0, 0)],
                           [(-2, 0), (-1, -1), (-1, 0), (-1, 1), (0, -2), (0, -1), (0, 1), (0, 2), (1, -1), (1, 0), (1, 1), (2, 0)])]

PATTERN_DYN_NO_OUT_2GRAM_COLS = 'PATTERN_DYN_NO_OUT_2GRAM_COLS'
PATTERN_DYN_3GRAM_COLS        = 'PATTERN_DYN_3GRAM_COLS'
PATTERN_DYN_2GRAM_ROWS        = 'PATTERN_DYN_2GRAM_ROWS'
PATTERN_DYN_ZGRAM_COLS        = 'PATTERN_DYN_ZGRAM_COLS'
PATTERN_DYN_ROOMS             = 'PATTERN_DYN_ROOMS'

PATTERN_DICT = {
    'nbr-2'      : PATTERN_NEIGH_2,
    'nbr-l'      : PATTERN_NEIGH_L,
    'nbr-plus'   : PATTERN_NEIGH_PLUS,
    'nbr-block2' : PATTERN_NEIGH_BLOCK2,
    'noout-bl-2' : PATTERN_NO_OUT_BLOCK_2,
    'noout-bl-3' : PATTERN_NO_OUT_BLOCK_3, # was no-out3
    'blockz'     : PATTERN_BLOCKZ,
    'block2'     : PATTERN_BLOCK2,
    'block2-inv' : PATTERN_BLOCK2_INV,
    'block3'     : PATTERN_BLOCK3,
    'ring'       : PATTERN_RING,
    'diamond'    : PATTERN_DIAMOND,
    'noout-gc-2' : PATTERN_DYN_NO_OUT_2GRAM_COLS,
    '3gc'        : PATTERN_DYN_3GRAM_COLS,
    '2gr'        : PATTERN_DYN_2GRAM_ROWS,
    'zgc'        : PATTERN_DYN_ZGRAM_COLS,
    'rooms'      : PATTERN_DYN_ROOMS,
}



def inc(tile_dict, key, tile, amount):
    if key not in tile_dict:
        tile_dict[key] = {}
    if tile not in tile_dict[key]:
        tile_dict[key][tile] = 0
    tile_dict[key][tile] += amount

def normalize(tile_dict):
    for key in tile_dict:
        total = 0
        for tile in tile_dict[key]:
            total += tile_dict[key][tile]
        if total != 0:
            for tile in tile_dict[key]:
                tile_dict[key][tile] = tile_dict[key][tile] / total

def tiles2scheme(tile_info, divs_size, game_to_patterns_delta, level_rotate):
    ti = tile_info
    si = util_common.SchemeInfo()

    si.tileset = ti.tileset

    si.game_to_tag_to_tiles = {}

    if divs_size is None:
        si.count_info = None
    else:
        si.count_info = util_common.SchemeCountInfo()

        si.count_info.divs_size = divs_size
        si.count_info.divs_to_game_to_tag_to_tile_count = {}
        for rr_divs in range(si.count_info.divs_size[0]):
            for cc_divs in range(si.count_info.divs_size[1]):
                si.count_info.divs_to_game_to_tag_to_tile_count[(rr_divs, cc_divs)] = {}

    if game_to_patterns_delta is None:
        si.pattern_info = None
    else:
        si.pattern_info = util_common.SchemePatternInfo()

        si.pattern_info.game_to_patterns = {}

        si.pattern_info.stride_rows = 1
        si.pattern_info.stride_cols = 1
        si.pattern_info.dr_lo = 0
        si.pattern_info.dr_hi = 0
        si.pattern_info.dc_lo = 0
        si.pattern_info.dc_hi = 0

        for game, patterns_delta in game_to_patterns_delta.items():
            if patterns_delta == PATTERN_DYN_NO_OUT_2GRAM_COLS:
                util_common.check(len(game_to_patterns_delta) == 1, 'multiple games stride')

                gram_rows = [len(tli.tiles) for tli in ti.levels]
                util_common.check(len(set(gram_rows)) == 1, 'all levels must be same height')
                gram_rows = gram_rows[0]

                si.pattern_info.stride_rows = 0
                patterns_delta = [([(rr, cc) for rr in range(gram_rows) for cc in range(2)], None)]
                game_to_patterns_delta[game] = patterns_delta
            elif patterns_delta == PATTERN_DYN_3GRAM_COLS:
                util_common.check(len(game_to_patterns_delta) == 1, 'multiple games stride')

                gram_rows = [len(tli.tiles) for tli in ti.levels]
                util_common.check(len(set(gram_rows)) == 1, 'all levels must be same height')
                gram_rows = gram_rows[0]

                si.pattern_info.stride_rows = 0
                patterns_delta = [([(rr, cc) for rr in range(gram_rows) for cc in range(2)],
                                   [(rr, 2) for rr in range(gram_rows)])]
                game_to_patterns_delta[game] = patterns_delta
            elif patterns_delta == PATTERN_DYN_2GRAM_ROWS:
                util_common.check(len(game_to_patterns_delta) == 1, 'multiple games stride')

                gram_cols = [len(tli.tiles[0]) for tli in ti.levels]
                util_common.check(len(set(gram_cols)) == 1, 'all levels must be same width')
                gram_cols = gram_cols[0]

                si.pattern_info.stride_cols = 0
                patterns_delta = [([(rr, cc) for rr in [0] for cc in range(gram_cols)],
                                   [(1, cc) for cc in range(gram_cols)])]
                game_to_patterns_delta[game] = patterns_delta
            elif patterns_delta == PATTERN_DYN_ZGRAM_COLS:
                util_common.check(len(game_to_patterns_delta) == 1, 'multiple games stride')

                si.pattern_info.stride_rows = 11
                patterns_delta = [([(rr, 0) for rr in range(11)],
                                   [(rr, 1) for rr in range(11)]),
                                  ([(10, 0)],
                                   [(11, 0)])]
                game_to_patterns_delta[game] = patterns_delta
            elif patterns_delta == PATTERN_DYN_ROOMS:
                util_common.check(len(game_to_patterns_delta) == 1, 'multiple games stride')

                si.pattern_info.stride_rows = 11
                si.pattern_info.stride_cols = 3
                patterns_delta = [
                    ([(rr, cc) for rr in range(11) for cc in range(3)],
                     None),
                    ([(rr, 2) for rr in range(11)],
                     [(rr, 3) for rr in range(11)]),
                    ([(10, cc) for cc in range(3)],
                     [(11, cc) for cc in range(3)])
                ]
                game_to_patterns_delta[game] = patterns_delta

        for game, patterns_delta in game_to_patterns_delta.items():
            si.pattern_info.game_to_patterns[game] = {}

            for pattern_template_in, pattern_template_out in patterns_delta:
                for dr, dc in pattern_template_in + (pattern_template_out if pattern_template_out else []):
                    si.pattern_info.dr_lo = min(si.pattern_info.dr_lo, dr)
                    si.pattern_info.dr_hi = max(si.pattern_info.dr_hi, dr)
                    si.pattern_info.dc_lo = min(si.pattern_info.dc_lo, dc)
                    si.pattern_info.dc_hi = max(si.pattern_info.dc_hi, dc)

    tile_levels, tag_levels, game_levels = [], [], []
    for tli in ti.levels:
        tile_level = tli.tiles
        tag_level = tli.tags
        game_level = tli.games

        tile_levels.append(tile_level)
        tag_levels.append(tag_level)
        game_levels.append(game_level)

        if level_rotate:
            for ii in range(3):
                tile_level = util_common.rotate_grid_cw(tile_level)
                tag_level = util_common.rotate_grid_cw(tag_level)
                game_level = util_common.rotate_grid_cw(game_level)

                tile_levels.append(tile_level)
                tag_levels.append(tag_level)
                game_levels.append(game_level)

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

                util_common.check(game != util_common.VOID_TEXT, 'void game')
                util_common.check((tile == util_common.VOID_TILE) == (tag == util_common.VOID_TEXT), 'void')
                if tile == util_common.VOID_TILE:
                    continue

                if game not in si.game_to_tag_to_tiles:
                    si.game_to_tag_to_tiles[game] = {}
                if tag not in si.game_to_tag_to_tiles[game]:
                    si.game_to_tag_to_tiles[game][tag] = {}
                si.game_to_tag_to_tiles[game][tag][tile] = None

        if si.count_info is not None:
            util_common.check(si.count_info.divs_size[0] <= rows and si.count_info.divs_size[1] <= cols, 'level to small for divs')

            for rr_divs in range(si.count_info.divs_size[0]):
                for cc_divs in range(si.count_info.divs_size[1]):
                    rr_lo = rows * (rr_divs + 0) // si.count_info.divs_size[0]
                    rr_hi = rows * (rr_divs + 1) // si.count_info.divs_size[0]
                    cc_lo = cols * (cc_divs + 0) // si.count_info.divs_size[1]
                    cc_hi = cols * (cc_divs + 1) // si.count_info.divs_size[1]

                    for game, tag_to_tiles in si.game_to_tag_to_tiles.items():
                        if game not in si.count_info.divs_to_game_to_tag_to_tile_count[(rr_divs, cc_divs)]:
                            si.count_info.divs_to_game_to_tag_to_tile_count[(rr_divs, cc_divs)][game] = {}

                            for tag, tiles in tag_to_tiles.items():
                                for tile in tiles:
                                    inc(si.count_info.divs_to_game_to_tag_to_tile_count[(rr_divs, cc_divs)][game], tag, tile, 0)

                    for rr in range(rr_lo, rr_hi):
                        for cc in range(cc_lo, cc_hi):
                            tile = tile_level[rr][cc]
                            tag = tag_level[rr][cc]
                            game = game_level[rr][cc]

                            util_common.check(game != util_common.VOID_TEXT, 'void game')
                            util_common.check((tile == util_common.VOID_TILE) == (tag == util_common.VOID_TEXT), 'void')
                            if tile == util_common.VOID_TILE:
                                continue

                            inc(si.count_info.divs_to_game_to_tag_to_tile_count[(rr_divs, cc_divs)][game], tag, tile, 1)

                    for game, tag_to_tiles in si.game_to_tag_to_tiles.items():
                        for tag, tiles in tag_to_tiles.items():
                            for tile in tiles:
                                inc(si.count_info.divs_to_game_to_tag_to_tile_count[(rr_divs, cc_divs)][game], tag, tile, 0)

        if si.pattern_info is not None:
            row_range = range(-si.pattern_info.dr_hi, rows - si.pattern_info.dr_lo, si.pattern_info.stride_rows) if si.pattern_info.stride_rows else [0]
            col_range = range(-si.pattern_info.dc_hi, cols - si.pattern_info.dc_lo, si.pattern_info.stride_cols) if si.pattern_info.stride_cols else [0]

            for rr in row_range:
                for cc in col_range:
                    game = game_level[max(0, min(rows - 1, rr))][max(0, min(cols - 1, cc))]

                    if game not in game_to_patterns_delta:
                        continue

                    def get_pattern(_template):
                        _pattern = []
                        for _dr, _dc in _template:
                            _nr = rr + _dr
                            _nc = cc + _dc

                            if _nr <= -1 or _nr >= rows or _nc <= -1 or _nc >= cols:
                                _nbr_tile = util_common.VOID_TILE
                            else:
                                _nbr_tile = tile_level[_nr][_nc]

                            _pattern.append(_nbr_tile)
                        return tuple(_pattern)

                    for pattern_template_in, pattern_template_out in game_to_patterns_delta[game]:
                        pattern_template_in = tuple(pattern_template_in)
                        pattern_in = get_pattern(pattern_template_in)
                        pattern_template_out = tuple(pattern_template_out) if pattern_template_out else None
                        pattern_out = get_pattern(pattern_template_out) if pattern_template_out else None

                        if pattern_template_in not in si.pattern_info.game_to_patterns[game]:
                            si.pattern_info.game_to_patterns[game][pattern_template_in] = {}

                        if pattern_in not in si.pattern_info.game_to_patterns[game][pattern_template_in]:
                            si.pattern_info.game_to_patterns[game][pattern_template_in][pattern_in] = {}

                        if pattern_template_out not in si.pattern_info.game_to_patterns[game][pattern_template_in][pattern_in]:
                            si.pattern_info.game_to_patterns[game][pattern_template_in][pattern_in][pattern_template_out] = {}

                        si.pattern_info.game_to_patterns[game][pattern_template_in][pattern_in][pattern_template_out][pattern_out] = None



    if si.count_info is not None:
        for grc in si.count_info.divs_to_game_to_tag_to_tile_count:
            for game in si.count_info.divs_to_game_to_tag_to_tile_count[grc]:
                normalize(si.count_info.divs_to_game_to_tag_to_tile_count[grc][game])

    printer = pprint.PrettyPrinter(width=200)
    printer.pprint(si.game_to_tag_to_tiles)

    print()
    if si.count_info is not None:
        print('Counts:')
        printer.pprint(si.count_info.divs_to_game_to_tag_to_tile_count)
    else:
        print('No counts.')

    print()
    if si.pattern_info is not None:
        print('Patterns:')
        print(si.pattern_info.dr_lo, si.pattern_info.dr_hi, si.pattern_info.dc_lo, si.pattern_info.dc_hi, si.pattern_info.stride_rows, si.pattern_info.stride_cols)
        printer.pprint(si.pattern_info.game_to_patterns)
    else:
        print('No patterns.')

    return si



if __name__ == '__main__':
    util_common.timer_start()

    parser = argparse.ArgumentParser(description='Create scheme from tile info and (optionally) tag level.')
    parser.add_argument('--outfile', required=True, type=str, help='Output scheme file.')
    parser.add_argument('--tilefile', required=True, type=str, help='Input tile file.')
    parser.add_argument('--count-divs', type=int, nargs=2, help='Count divisions.')
    parser.add_argument('--pattern', type=str, nargs='+', help='Pattern template, from: ' + ','.join(PATTERN_DICT.keys()) + '.')
    parser.add_argument('--level-rotate', action='store_true', help='Rotate levels to create more patterns.')
    parser.add_argument('--quiet', action='store_true', help='Reduce output.')
    args = parser.parse_args()

    if args.quiet:
        sys.stdout = open(os.devnull, 'w')

    with util_common.openz(args.tilefile, 'rb') as f:
        tile_info = pickle.load(f)

    if args.pattern is not None:
        game_to_patterns_name = util_common.arg_list_to_dict_options(parser, '--pattern', args.pattern, PATTERN_DICT.keys())
        game_to_patterns_delta = {}
        for game, patterns_name in game_to_patterns_name.items():
            game_to_patterns_delta[game] = PATTERN_DICT[patterns_name]
    else:
        game_to_patterns_delta = None

    scheme_info = tiles2scheme(tile_info, args.count_divs, game_to_patterns_delta, args.level_rotate)
    with util_common.openz(args.outfile, 'wb') as f:
        pickle.dump(scheme_info, f)
