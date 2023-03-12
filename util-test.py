import itertools, os
import util

if __name__ == '__main__':
    os.environ['STG_MUTE_TIME'] = '1'
    os.environ['STG_MUTE_PORT'] = '1'

    print('corner_indices')
    for til in [5, 10, 15]:
        for depth in [2, 3, 5]:
            util_inds = util.corner_indices(til, depth)
            itertools_inds = [inds for inds in itertools.product(range(til), repeat=depth) if len(inds) == len(set(inds)) and list(inds) == sorted(inds)]
            util.check(util_inds == itertools_inds, 'corner_indices')
