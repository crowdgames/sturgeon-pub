import argparse, os, shutil
import util_common, util_path, util_reach



def level2repath(text_level, game_level, reach_connect_setup, repath_cost, enum):
    src, dst = util_path.get_level_src_dst(text_level, reach_connect_setup.src, reach_connect_setup.dst)

    rows = len(text_level)
    cols = len(text_level[0])

    game_to_move_info = util_reach.get_game_to_move_info(reach_connect_setup)
    game_locations = { (rr, cc): game_level[rr][cc] for rr in range(rows) for cc in range(cols) }

    open_locations, closed_locations = util_path.get_level_open_closed(text_level, reach_connect_setup.open_text, reach_connect_setup.src, reach_connect_setup.dst)

    return util_path.path_between(src, dst, rows, cols, game_to_move_info, game_locations, open_locations, closed_locations, repath_cost, None, 0, enum)



if __name__ == '__main__':
    util_common.timer_start()

    parser = argparse.ArgumentParser(description='Recalculate paths.')
    parser.add_argument('--outfile', required=True, type=str, help='File to write to.')
    parser.add_argument('--textfile', required=True, type=str, help='Input text file.')
    parser.add_argument('--gamefile', type=str, help='Input game file.')
    parser.add_argument('--reach-connect', required=True, type=str, action='append', default=None, help='Use reachability junction connect, as sub-arguments.')
    parser.add_argument('--cost', required=True, type=str, choices=util_path.COST_LIST, help='Type of repath, from: ' + ','.join(util_path.COST_LIST) + '.')
    parser.add_argument('--print-level', action='store_true', help='Print repathed level.')
    parser.add_argument('--copy-image', action='store_true', help='Copy level image if present.')
    parser.add_argument('--enum', action='store_true', help='Enumerate multiple paths.')
    parser.add_argument('--ignore-none', action='store_true', help='Ignore levels with no path.')
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
        new_paths, reachable_tiles = level2repath(text_level, game_level, reach_connect_setup, args.cost, args.enum)

        if not reach_connect_setup.unreachable and new_paths is not None:
            if not args.enum:
                new_paths = [new_paths]

            all_path_edges = []
            all_path_tiles = []
            for new_path_edges, new_path_tiles in new_paths:
                all_path_edges.append(new_path_edges)
                all_path_tiles.append(new_path_tiles)
                meta.append(util_common.meta_path(util_common.MGROUP_PATH, new_path_edges))
                meta.append(util_common.meta_tile(util_common.MGROUP_PATH, new_path_tiles))
                if args.enum:
                    meta.append({ 'type': 'path-enum-edge-tile',
                                  'data': list(zip([[]] + new_path_edges, new_path_tiles)) })

            if args.enum:
                meta.append(util_common.meta_line('path-enum-line', util_path.merge_unwrapped_edge_paths(all_path_edges)))
                meta.append(util_common.meta_tile('path-enum-tile', util_path.merge_tile_paths(all_path_tiles)))
                meta.append(util_common.meta_line('path-enum-border', util_path.merge_tile_paths_border(all_path_tiles)))

        elif reach_connect_setup.unreachable and new_paths is None:
            meta.append(util_common.meta_tile(util_common.MGROUP_REACHABLE, list(reachable_tiles)))

        elif not args.ignore_none:
            util_common.exit_solution_not_found()

    with util_common.openz(args.outfile, 'wt') as f:
        if args.print_level:
            util_common.print_text_level(text_level, meta=meta)
        util_common.print_text_level(text_level, meta=meta, outstream=f)

    if args.copy_image:
        image_name_in = os.path.splitext(args.textfile)[0] + '.png'
        image_name_out = os.path.splitext(args.outfile)[0] + '.png'
        if os.path.exists(image_name_in):
            shutil.copyfile(image_name_in, image_name_out)

    util_common.exit_solution_found()
