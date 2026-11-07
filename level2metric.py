import argparse, json, sys
import util_common, util_custom, util_path



def level2metric(metric, text_level, meta_level, open_text, src_text, dst_text):
    open_locations, closed_locations = util_path.get_level_open_closed(text_level, open_text, src_text, dst_text)

    edge_tile_paths = []
    for md in meta_level:
        if md['type'] == 'path-enum-edge-tile':
            edge_tile_paths.append(md['data'])

    def for_each_path(_path_func):
        _values = []
        for _edge_tile_path in edge_tile_paths:
            _values.append(_path_func(_edge_tile_path))
        return _values

    def count_edge_values(_func):
        return for_each_path(lambda _edge_tile_path: sum([_func(_edge) for _edge, _tiles in _edge_tile_path if len(_edge) > 0]))

    def count_tile_values(_func):
        return for_each_path(lambda _edge_tile_path: sum([_func(_tiles) for _edge, _tiles in _edge_tile_path]))

    def high_water_values(_func):
        def _helper(_edge_tile_path):
            _curr, _high = 0, 0
            for _edge, _tiles in _edge_tile_path:
                _curr = _func(_edge, _tiles, _curr)
                _high = max(_high, _curr)
            return _high
        return for_each_path(_helper)

    def fraction_values(_func):
        def _helper(_edge_tile_path):
            _numer, _denom = 0, 0
            for _edge, _tiles in _edge_tile_path:
                _numer, _denom = _func(_edge, _tiles, _numer, _denom)
            return _numer / _denom
        return for_each_path(_helper)

    if metric == util_custom.PATH_COUNT_EDGE:
        return count_edge_values(lambda _edge: True)
    elif metric == util_custom.PATH_COUNT_EDGE_UP:
        return count_edge_values(lambda _edge: util_path.edge_is_up_by(_edge, 1))
    elif metric == util_custom.PATH_COUNT_EDGE_DOWN:
        return count_edge_values(lambda _edge: util_path.edge_is_down_by(_edge, 1))
    elif metric == util_custom.PATH_COUNT_EDGE_LEFT:
        return count_edge_values(lambda _edge: util_path.edge_is_left_by(_edge, 1))
    elif metric == util_custom.PATH_COUNT_EDGE_RIGHT:
        return count_edge_values(lambda _edge: util_path.edge_is_right_by(_edge, 1))
    elif metric == util_custom.PATH_COUNT_EDGE_JUMP:
        return count_edge_values(lambda _edge: util_path.edge_is_jump(_edge, closed_locations))
    elif metric == util_custom.PATH_COUNT_EDGE_ONGROUND:
        return count_edge_values(lambda _edge: util_path.edge_is_onground(_edge, closed_locations))
    elif metric == util_custom.PATH_COUNT_TILE:
        return count_tile_values(lambda _tiles: len(_tiles))
    elif metric == util_custom.PATH_AIRTIME_JUMP:
        def func(_edge, _tiles, _curr):
            if len(_edge) == 0:
                return _curr
            elif util_path.edge_is_jump(_edge, closed_locations):
                return len(_tiles)
            elif _curr > 0 and not util_path.edge_is_onground(_edge, closed_locations):
                return _curr + len(_tiles)
            else:
                return 0
        return high_water_values(func)
    elif metric == util_custom.PATH_JUMP_ENTROPY:
        def func(_edge, _tiles, _numer, _denom):
            if len(_edge) > 0:
                if util_path.edge_is_jump(_edge, closed_locations):
                    _numer += 1
                    _denom += 1
                _denom += abs(util_path.edge_delta_cols(_edge))
            return _numer, _denom
        return fraction_values(func)
    elif metric == util_custom.PATH_AVERAGE_ROW:
        def func(_edge, _tiles, _numer, _denom):
            return _numer + sum([_rr for _rr, _cc in _tiles]), _denom + len(_tiles)
        return fraction_values(func)
    elif metric == util_custom.PATH_SPEED:
        def func(_edge, _tiles, _numer, _denom):
            return _numer + (util_path.edge_delta_cols(_edge) if len(_edge) > 0 else 0), _denom + len(_tiles)
        return fraction_values(func)
    elif metric == util_custom.PATH_ONGROUNDRATIO:
        def func(_edge, _tiles, _numer, _denom):
            return _numer + (util_path.edge_is_onground(_edge, closed_locations) if len(_edge) > 0 else 0), _denom + len(_tiles)
        return fraction_values(func)

    else:
        util_common.check(False, metric)



if __name__ == '__main__':
    util_common.timer_start()

    parser = argparse.ArgumentParser(description='Calculate metric for level.')
    parser.add_argument('--outfile', type=str, help='Output file.')
    parser.add_argument('--textfile', required=True, type=str, help='Input text file.')
    parser.add_argument('--metric', required=True, type=str, help='Metric to calculate.')
    parser.add_argument('--open', required=True, type=str, help='Open tile text.')
    parser.add_argument('--src', required=True, type=str, help='Src tile text.')
    parser.add_argument('--dst', required=True, type=str, help='Dst tile text.')
    args = parser.parse_args()


    text_level, meta_level = util_common.read_text_level(args.textfile, True)

    metric = level2metric(args.metric, text_level, meta_level, args.open, args.src, args.dst)

    if args.outfile is None:
        json.dump(metric, sys.stdout)
        sys.stdout.write('\n')
    else:
        with open(args.outfile, 'wt') as outfile:
            json.dump(metric, outfile)
            outfile.write('\n')

    util_common.exit_solution_found()
