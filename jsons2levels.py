import argparse, json, os, sys
import util_common, util_explore



def jsons2levels(jsons, keys):
    levels = []
    
    for js in jsons:
        if keys is not None:
            for key in keys:
                js = js[key]

        if True:
            levels.append(js)
        else:
            level = None
            for layer, board in js.items():
                if level is None:
                    level = board
                else:
                    for rr in range(len(board)):
                        for cc in range(len(board[rr])):
                            level[rr][cc] += ',' + board[rr][cc]
            if level is not None:
                levels.append(level)
    
    return levels



if __name__ == '__main__':
    util_common.timer_start()

    parser = argparse.ArgumentParser(description='Convert levels to explore file.')
    parser.add_argument('--outfile', required=True, type=str, help='File prefix to write to.')
    parser.add_argument('--jsonsfile', required=True, type=str, help='Input jsons file.')
    parser.add_argument('--keys', type=str, nargs='+', help='Keys to find level in json.')

    args = parser.parse_args()

    jsons = []
    with open(args.jsonsfile, 'rt') as jf:
        for line in jf.readlines():
            jsons.append(json.loads(line))

    levels = jsons2levels(jsons, args.keys)
    for ii, level in enumerate(levels):
        with open(args.outfile + ('_%06d' % ii) + '.json', 'wt') as jf:
            json.dump(level, jf)
