import itertools, os
import util_common, util_reach, util_path

if __name__ == '__main__':
    os.environ['STG_MUTE_TIME'] = '1'
    os.environ['STG_MUTE_PORT'] = '1'

    print('order_edge_path')
    test_order_edge_path = [
        ([(2, 3, 4, 5), (0, 1, 2, 3)],
         [(0, 1, 2, 3), (2, 3, 4, 5)]),
        ([(2, 3, 4, 5), (0, 1, 2, 3), (4, 5, 6, 7)],
         [(0, 1, 2, 3), (2, 3, 4, 5), (4, 5, 6, 7)]),
    ]
    for unordered, ordered in test_order_edge_path:
        util_common.check(util_path.order_edge_path(unordered) == ordered, str(unordered) + ' -> ' + str(ordered))

    print('path_begin_end_point')
    test_path_begin_end_point = [
        ([(1, 2, 3, 4)], (1, 2), (3, 4)),
        ([(1, 2, 3, 4), (3, 4, 5, 6)], (1, 2), (5, 6)),
    ]
    for path, begin_point, end_point in test_path_begin_end_point:
        util_common.check(util_path.path_begin_point(path) == begin_point, 'begin_point')
        util_common.check(util_path.path_end_point(path) == end_point, 'end_point')

    print('get_nexts_open_closed_from')
    rows, cols = 5, 5
    path = [(2, 2, 2, 3)]
    game_locations = { (rr, cc): util_common.DEFAULT_TEXT for rr in range(rows) for cc in range(cols) }
    game_to_move_info = { util_common.DEFAULT_TEXT: util_reach.get_move_info(util_reach.RMOVE_MAZE, False, False, False) }

    path_nexts, path_open, path_closed = util_path.get_nexts_open_closed_from(util_path.path_end_point(path), path, False, rows, cols, game_to_move_info, game_locations)
    util_common.check(list(sorted(path_nexts.items())) == [((1, 3), ((2, 3, 1, 3, 1, 3), 1)), ((2, 4), ((2, 3, 2, 4, 2, 4), 1)), ((3, 3), ((2, 3, 3, 3, 3, 3), 1))], 'path_nexts')
    util_common.check(list(sorted(path_open)) == [(2, 2), (2, 3)], 'path_open')
    util_common.check(list(sorted(path_closed)) == [], 'path_closed')

    path_nexts, path_open, path_closed = util_path.get_nexts_open_closed_from(util_path.path_begin_point(path), path, True, rows, cols, game_to_move_info, game_locations)
    util_common.check(list(sorted(path_nexts.items())) == [((1, 2), ((1, 2, 2, 2, 2, 2), 1)), ((2, 1), ((2, 1, 2, 2, 2, 2), 1)), ((3, 2), ((3, 2, 2, 2, 2, 2), 1))], 'path_nexts')
    util_common.check(list(sorted(path_open)) == [(2, 2), (2, 3)], 'path_open')
    util_common.check(list(sorted(path_closed)) == [], 'path_closed')
