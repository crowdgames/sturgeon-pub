import argparse, json, pickle, sys, time
import util_common, util_explore
import numpy as np


def explore2summary(ex, summarize_levels, summarize_edges):
    level_length = ex.rows * ex.cols * ex.ntind + ex.neind + ex.npind

    print('levels:', ex.level_data.shape[0])
    print('level length:', level_length)
    print('level length (packed):', ex.level_data.shape[1])
    print('size:', ex.rows, 'rows,', ex.cols, 'cols')
    print('tile indices / bits:', ex.ntind, '/', ex.rows * ex.cols * ex.ntind)
    print('edge indices:', ex.neind)
    print('property indices:', ex.npind)

    image_ids = {}
    for tind, image in ex.tind_to_image.items():
        image_id = id(image)
        if image_id not in image_ids:
            image_ids[image_id] = util_common.index_to_char(len(image_ids))

    print('index text:  ', ''.join([(ex.tind_to_text[tind] if tind in ex.tind_to_text else ' ') for tind in range(ex.ntind)]))
    print('index image: ', ''.join([(image_ids[id(ex.tind_to_image[tind])] if tind in ex.tind_to_image else ' ')  for tind in range(ex.ntind)]))

    tile_to_tinds = {}
    for tinds, tile in ex.tinds_to_tile.items():
        tile_to_tinds[tile] = tinds

    tiles_strings = []
    for tile in ex.tileset.tile_ids:
        tile_string = str(tile) + ':'
        for tind in tile_to_tinds[tile]:
            if tind in ex.tind_to_text:
                tile_string = tile_string + ex.tind_to_text[tind]
            if tind in ex.tind_to_image:
                tile_string = tile_string + image_ids[id(ex.tind_to_image[tind])]
        tiles_strings.append(tile_string)

    print('tiles:', ' '.join(tiles_strings))

    print('void tile:', 'yes' if ex.void_tind is not None else 'no')

    print('properties:', '; '.join(ex.pind_to_prop.values()))

    if summarize_edges:
        print('edges:')
        for eind in range(ex.neind):
            print(ex.eind_to_edge[eind])

    if summarize_levels:
        print('levels:')
        print(''.join(((['T'] + ['t'] * (ex.ntind - 1)) * (ex.rows * ex.cols)) + ['e'] * ex.neind  + ['p'] * ex.npind))
        levels_unpacked = np.unpackbits(ex.level_data, count=level_length, axis=1)
        for level in levels_unpacked:
            print(''.join([str(vv) for vv in level]))

if __name__ == '__main__':
    util_common.timer_start()

    parser = argparse.ArgumentParser(description='Summarize explore file.')
    parser.add_argument('--explorefile', required=True, type=str, help='Input explore file.')
    parser.add_argument('--levels', action='store_true', help='Include levels in summary.')
    parser.add_argument('--edges', action='store_true', help='Include edges in summary.')
    args = parser.parse_args()

    with util_common.openz(args.explorefile, 'rb') as f:
        ex = pickle.load(f)

    explore2summary(ex, args.levels, args.edges)
