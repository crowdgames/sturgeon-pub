import itertools, os
import util_common

if __name__ == '__main__':
    os.environ['STG_MUTE_TIME'] = '1'
    os.environ['STG_MUTE_PORT'] = '1'

    print('xform_grid')
    grid = [[1,2,3], [4,5,6]]
    util_common.check(util_common.xform_grid_rotate_cw(grid) == [[4, 1], [5, 2], [6, 3]], 'xform_grid')
    util_common.check(util_common.xform_grid_flip_rows(grid) == [[4, 5, 6], [1, 2, 3]], 'xform_grid')
    util_common.check(util_common.xform_grid_flip_cols(grid) == [[3, 2, 1], [6, 5, 4]], 'xform_grid')
    util_common.check(util_common.xform_grid_pad_side(grid, -1, -2) == [[-1, 1, 2, 3, -2], [-1, 4, 5, 6, -2]], 'xform_grid')
    util_common.check(util_common.xform_grid_pad_around(grid, -1, -2, -3, -4, -5, -6, -7, -8) == [[-1, -2, -2, -2, -3], [-4, 1, 2, 3, -5], [-4, 4, 5, 6, -5], [-6, -7, -7, -7, -8]], 'xform_grid')
    util_common.check(util_common.xform_grid_subgrid(grid, 1, 1, 3, 3) == [[5, 6]], 'xform_grid')
    util_common.check(util_common.xform_grid_subgrid(grid, 0, 1, 3, 2) == [[2], [5]], 'xform_grid')
    util_common.check(util_common.xform_grid_subgrid(grid, 1, 1, 2, 2) == [[5]], 'xform_grid')

    print('corner_indices')
    for til in [5, 10, 15]:
        for depth in [2, 3, 5]:
            util_inds = util_common.corner_indices(til, depth)
            itertools_inds = [inds for inds in itertools.product(range(til), repeat=depth) if len(inds) == len(set(inds)) and list(inds) == sorted(inds)]
            util_common.check(util_inds == itertools_inds, 'corner_indices')
