import argparse
import util_common, util_path, util_reach



def level2repath(text_level, open_text, src_text, dst_text, reach_move_name):
    rows = len(text_level)
    cols = len(text_level[0])
    src, dst = util_path.get_level_src_dst(text_level, src_text, dst_text)
    are_open, are_closed = util_path.get_level_open_closed(text_level, open_text, src_text, dst_text)
    template_open_closed = util_path.get_template_open_closed(util_reach.get_move_template(reach_move_name))

    return util_path.path_between_dijkstra(src, dst, rows, cols, template_open_closed, are_open, are_closed)



if __name__ == '__main__':
    util_common.timer_start()

    parser = argparse.ArgumentParser(description='Recalculate paths.')
    parser.add_argument('--outfile', required=True, type=str, help='File to write to.')
    parser.add_argument('--textfile', required=True, type=str, help='Input text file.')
    parser.add_argument('--reach-move', required=True, type=str, nargs='+', help='Use reachability move rules, from: ' + ','.join(util_reach.RMOVE_LIST) + '.')
    parser.add_argument('--src', type=str, nargs='+', default=[util_common.START_TEXT], help='Source junction(s)')
    parser.add_argument('--dst', type=str, nargs='+', default=[util_common.GOAL_TEXT], help='Destination junction(s)')
    parser.add_argument('--path', type=util_common.strtobool, nargs='+', default=[True], help='Check that there should not be a path or not a path.')
    args = parser.parse_args()

    util_common.check(len(args.src) == len(args.dst), '--src and --dst must be same length')

    reach_move = args.reach_move
    if len(reach_move) == 1 and len(args.src) > 1:
        reach_move = len(args.src) * reach_move
    util_common.check(len(args.src) == len(reach_move), '--src and --reach-move must be same length')

    path = args.path
    if len(path) == 1 and len(args.src) > 1:
        path = len(args.src) * path
    util_common.check(len(args.src) == len(path), '--src and --path must be same length')


    text_level, meta = util_common.read_text_level(args.textfile, True)

    meta = util_common.remove_meta_geom_groups(meta, [util_common.MGROUP_PATH, util_common.MGROUP_OFFPATH, util_common.MGROUP_REACHABLE])

    for src, dst, mv, pt in zip(args.src, args.dst, reach_move, path):
        new_path, reachable_tiles = level2repath(text_level, util_common.OPEN_TEXT, src, dst, mv)
        if pt and new_path is not None:
            meta.append(util_common.meta_path(util_common.MGROUP_PATH, util_path.edge_path_from_point_path(new_path)))
        elif not pt and new_path is None:
            meta.append(util_common.meta_tile(util_common.MGROUP_REACHABLE, list(reachable_tiles)))
        else:
            util_common.exit_solution_not_found()


    with util_common.openz(args.outfile, 'wt') as f:
        util_common.print_text_level(text_level, meta=meta, outfile=f)
    util_common.exit_solution_found()
