import argparse
import util_common, util_path, util_reach



def level2repath(text_level, game_level, reach_connect_setup):
    open_text = reach_connect_setup.open_text
    src_text = reach_connect_setup.src
    dst_text = reach_connect_setup.dst

    util_common.check(reach_connect_setup.wrap_cols == False, 'wrap_cols not supported')

    rows = len(text_level)
    cols = len(text_level[0])
    src, dst = util_path.get_level_src_dst(text_level, src_text, dst_text)
    open_locations, closed_locations = util_path.get_level_open_closed(text_level, open_text, src_text, dst_text)

    game_locations = { (rr, cc): game_level[rr][cc] for rr in range(rows) for cc in range(cols) }
    game_to_open_closed_template = {}
    for game, reach_move_name in reach_connect_setup.game_to_move.items():
        game_to_open_closed_template[game] = util_path.get_open_closed_template(util_reach.get_move_template(reach_move_name))

    return util_path.path_between_dijkstra(src, dst, rows, cols, game_to_open_closed_template, open_locations, closed_locations, game_locations)



if __name__ == '__main__':
    util_common.timer_start()

    parser = argparse.ArgumentParser(description='Recalculate paths.')
    parser.add_argument('--outfile', required=True, type=str, help='File to write to.')
    parser.add_argument('--textfile', required=True, type=str, help='Input text file.')
    parser.add_argument('--gamefile', type=str, help='Input game file.')
    parser.add_argument('--reach-connect', type=str, action='append', default=None, help='Use reachability junction connect, as sub-arguments.')
    parser.add_argument('--print-level', action='store_true', help='Print repathed level.')
    args = parser.parse_args()



    reach_connect_setups = []
    for reach_connect in args.reach_connect:
        reach_connect_setups.append(util_reach.parse_reach_subargs('--reach-connect', reach_connect.split()))

    text_level, meta = util_common.read_text_level(args.textfile, True)

    if args.gamefile is not None:
        game_level = util_common.read_text_level(args.gamefile)
    else:
        game_level = util_common.make_grid(len(text_level), len(text_level[0]), util_common.DEFAULT_TEXT)

    meta = util_common.remove_meta_geom_groups(meta, [util_common.MGROUP_PATH, util_common.MGROUP_OFFPATH, util_common.MGROUP_REACHABLE])

    for reach_connect_setup in reach_connect_setups:
        new_path, reachable_tiles = level2repath(text_level, game_level, reach_connect_setup)

        if not reach_connect_setup.unreachable and new_path is not None:
            meta.append(util_common.meta_path(util_common.MGROUP_PATH, util_path.edge_path_from_point_path(new_path)))
        elif reach_connect_setup.unreachable and new_path is None:
            meta.append(util_common.meta_tile(util_common.MGROUP_REACHABLE, list(reachable_tiles)))
        else:
            util_common.exit_solution_not_found()

    with util_common.openz(args.outfile, 'wt') as f:
        if args.print_level:
            util_common.print_text_level(text_level, meta=meta)
        util_common.print_text_level(text_level, meta=meta, outfile=f)
    util_common.exit_solution_found()
