import itertools, os
import util_common, util_path

if __name__ == '__main__':
    os.environ['STG_MUTE_TIME'] = '1'
    os.environ['STG_MUTE_PORT'] = '1'

    test_order_edge_path = [
        ([(2, 3, 4, 5), (0, 1, 2, 3)],
         [(0, 1, 2, 3), (2, 3, 4, 5)]),
        ([(2, 3, 4, 5), (0, 1, 2, 3), (4, 5, 6, 7)],
         [(0, 1, 2, 3), (2, 3, 4, 5), (4, 5, 6, 7)]),
        ]

    print('order_edge_path')
    for unordered, ordered in test_order_edge_path:
        util_common.check(util_path.order_edge_path(unordered) == ordered, str(unordered) + ' -> ' + str(ordered))
