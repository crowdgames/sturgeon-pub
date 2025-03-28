import argparse
import util_common, util_path, util_reach



REPATH_PATH_TILES = 'path-tiles'
REPATH_EDGES      = 'edges'
REPATH_LIST       = [REPATH_PATH_TILES, REPATH_EDGES]



def level2repath(text_level, game_level, reach_connect_setup, repath_type):
    src, dst = util_path.get_level_src_dst(text_level, reach_connect_setup.src, reach_connect_setup.dst)

    rows = len(text_level)
    cols = len(text_level[0])

    game_to_move_info = util_reach.get_game_to_move_info(reach_connect_setup)
    game_locations = { (rr, cc): game_level[rr][cc] for rr in range(rows) for cc in range(cols) }

    open_locations, closed_locations = util_path.get_level_open_closed(text_level, reach_connect_setup.open_text, reach_connect_setup.src, reach_connect_setup.dst)

    if repath_type == REPATH_PATH_TILES:
        path_fn = util_path.path_between_dijkstra
    elif repath_type == REPATH_EDGES:
        path_fn = util_path.shortest_path_between
    else:
        util_common.check(False, 'unrecognized repath type ' + str(repath_type))

    return path_fn(src, dst, rows, cols, game_to_move_info, game_locations, open_locations, closed_locations)



if __name__ == '__main__':
    util_common.timer_start()

    parser = argparse.ArgumentParser(description='Recalculate paths.')
    parser.add_argument('--outfile', required=True, type=str, help='File to write to.')
    parser.add_argument('--textfile', required=True, type=str, help='Input text file.')
    parser.add_argument('--gamefile', type=str, help='Input game file.')
    parser.add_argument('--reach-connect', type=str, action='append', default=None, help='Use reachability junction connect, as sub-arguments.')
    parser.add_argument('--print-level', action='store_true', help='Print repathed level.')
    parser.add_argument('--type', type=str, choices=REPATH_LIST, default=REPATH_PATH_TILES, help='Type of repath, from: ' + ','.join(REPATH_LIST) + '.')
    args = parser.parse_args()


    reach_connect_setups = []
    for reach_connect in args.reach_connect:
        reach_connect_setups.append(util_reach.parse_reach_connect_subargs('--reach-connect', reach_connect.split()))

    text_level, meta = util_common.read_text_level(args.textfile, True)

    rows = len(text_level)
    cols = len(text_level[0])

    if args.gamefile is not None:
        game_level = util_common.read_text_level(args.gamefile)
    else:
        game_level = util_common.make_grid(rows, cols, util_common.DEFAULT_TEXT)

    meta = util_common.remove_meta_geom_groups(meta, [util_common.MGROUP_PATH, util_common.MGROUP_OFFPATH, util_common.MGROUP_REACHABLE])

    for reach_connect_setup in reach_connect_setups:
        new_path, reachable_tiles = level2repath(text_level, game_level, reach_connect_setup, args.type)

        if not reach_connect_setup.unreachable and new_path is not None:
            meta.append(util_common.meta_path(util_common.MGROUP_PATH, new_path))
        elif reach_connect_setup.unreachable and new_path is None:
            meta.append(util_common.meta_tile(util_common.MGROUP_REACHABLE, list(reachable_tiles)))
        else:
            util_common.exit_solution_not_found()

    with util_common.openz(args.outfile, 'wt') as f:
        if args.print_level:
            util_common.print_text_level(text_level, meta=meta)
        util_common.print_text_level(text_level, meta=meta, outstream=f)
    util_common.exit_solution_found()
