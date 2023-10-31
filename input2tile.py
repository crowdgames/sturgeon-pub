import argparse, json, os, shutil, pickle, sys
import util_common
import PIL.Image



TILE_OUTPUT_FOLDER = 'tiles'



def get_tile_key(tile_text, tile_image):
    tile_key = ()
    if tile_text is not None:
        tile_key = tile_key + (tile_text,)
    if tile_image is not None:
        tile_key = tile_key + (tuple(tile_image.getdata()),)
    return tile_key



def input2tiles(base_tile_info, text_levels, image_levels, tag_levels, games, paths, tile_image_size, no_levels, text_key_only, tile_output_folder):
    tile_key_to_tile_id = {}

    if base_tile_info is not None:
        ts = base_tile_info.tileset

        for tile in ts.tile_ids:
            tile_text = ts.tile_to_text[tile] if ts.tile_to_text is not None else None
            tile_image = ts.tile_to_image[tile] if ts.tile_to_image is not None else None
            tile_key = get_tile_key(tile_text, tile_image if not text_key_only else None)
            util_common.check(tile_key not in tile_key_to_tile_id, 'duplicate tile key in base tile info')
            tile_key_to_tile_id[tile_key] = tile
    else:
        ts = util_common.TileSetInfo()

        ts.tile_ids = {}

        ts.tile_to_text = {} if text_levels else None
        ts.tile_to_image = {} if image_levels else None
        ts.tile_image_size = tile_image_size

    ti = util_common.TileInfo()
    ti.tileset = ts
    if no_levels:
        ti.levels = None
    else:
        ti.levels = []



    if text_levels is not None:
        level_count = len(text_levels)
    elif image_levels is not None:
        level_count = len(image_levels)
    else:
        util_common.check(False, 'text and image both missing')

    if text_levels is not None:
        util_common.check(len(text_levels) == level_count, 'need same number of levels')
    else:
        text_levels = [None] * level_count

    if image_levels is not None:
        util_common.check(len(image_levels) == level_count, 'need same number of levels')
    else:
        image_levels = [None] * level_count

    if tag_levels is not None:
        util_common.check(len(tag_levels) == level_count, 'need same number of levels')
    else:
        tag_levels = [None] * level_count

    if games is not None:
        util_common.check(len(games) == level_count, 'need same number of levels')
    else:
        games = [None] * level_count

    if paths is not None:
        util_common.check(len(paths) == level_count, 'need same number of levels')
    else:
        paths = [None] * level_count



    for ii, (text_level_meta, image_level, tag_level, game, path) in enumerate(zip(text_levels, image_levels, tag_levels, games, paths)):
        if text_level_meta is not None:
            text_level, text_meta = text_level_meta
            text_sz = (len(text_level), len(text_level[0]))
        else:
            text_level, text_meta = None, None
            text_sz = None

        if image_level is not None:
            image_sz = image_level.size

            if ts.tile_image_size is None:
                util_common.check(text_sz is not None, 'need text level to determine tile image size')
                tile_size_x = image_sz[0] / text_sz[1]
                tile_size_y = image_sz[1] / text_sz[0]
                util_common.check(tile_size_y == tile_size_x and tile_size_y == int(tile_size_y) and tile_size_x == int(tile_size_x), 'can\'t determine tile image size')
                ts.tile_image_size = int(tile_size_x)
                print('Tile size set to', ts.tile_image_size)

            util_common.check(image_sz[0] % ts.tile_image_size == 0 and image_sz[1] % ts.tile_image_size == 0, 'Image size not multiple of tile size')
            image_sz = (image_sz[1] // ts.tile_image_size, image_sz[0] // ts.tile_image_size)
        else:
            image_sz = None

        if text_sz and image_sz:
            util_common.check(text_sz == image_sz, 'text and image size mismatch')
            rows, cols = text_sz
        elif text_sz:
            rows, cols = text_sz
        elif image_sz:
            rows, cols = image_sz
        else:
            util_common.check(False, 'text and image both missing')

        tile_level = []
        for rr in range(rows):
            tile_level_row = []
            for cc in range(cols):
                tile_text = None
                tile_text_is_void = None
                if text_level is not None:
                    tile_text = text_level[rr][cc]
                    tile_text_is_void = (tile_text == util_common.VOID_TEXT)

                tile_image = None
                tile_image_is_void = None
                if image_level is not None:
                    tile_image = util_common.fresh_image(image_level.crop((cc * ts.tile_image_size, rr * ts.tile_image_size, cc * ts.tile_image_size + ts.tile_image_size, rr * ts.tile_image_size + ts.tile_image_size)).convert('RGBA'))
                    tile_image_is_void = (sum([ch for px in tile_image.getdata() for ch in px]) == 0)

                if tile_text_is_void or tile_image_is_void:
                    util_common.check(tile_text_is_void in [True, None], 'void')
                    util_common.check(tile_image_is_void in [True, None], 'void')
                    tile_id = util_common.VOID_TILE

                else:
                    tile_key = get_tile_key(tile_text, tile_image if not text_key_only else None)
                    if tile_key not in tile_key_to_tile_id:
                        if base_tile_info is not None:
                            util_common.check(False, 'tile missing in base tile info')

                        tile_id = len(ts.tile_ids)
                        ts.tile_ids[tile_id] = None

                        tile_key_to_tile_id[tile_key] = tile_id

                        if tile_text:
                            ts.tile_to_text[tile_id] = tile_text
                        if tile_image:
                            ts.tile_to_image[tile_id] = tile_image
                    else:
                        tile_id = tile_key_to_tile_id[tile_key]

                tile_level_row.append(tile_id)
            tile_level.append(tile_level_row)

        if tag_level is None:
            tag_level = util_common.make_grid(rows, cols, util_common.DEFAULT_TEXT)
            for rr in range(rows):
                for cc in range(cols):
                    if tile_level[rr][cc] == util_common.VOID_TILE:
                        tag_level[rr][cc] = util_common.VOID_TEXT
        else:
            util_common.check(len(tag_level) == rows, 'tile and tag level row count mismatch')
            for rr in range(rows):
                util_common.check(len(tag_level[rr]) == cols, 'row length mismatch')
                for cc in range(cols):
                    util_common.check((tile_level[rr][cc] == util_common.VOID_TILE) == (tag_level[rr][cc] == util_common.VOID_TEXT), 'void')

        if game is None:
            game_level = util_common.make_grid(rows, cols, util_common.DEFAULT_TEXT)
        else:
            util_common.check(type(game) == str and len(game) == 1, 'game')
            game_level = util_common.make_grid(rows, cols, game)

        if path is not None:
            if text_meta is None:
                text_meta = []
            text_meta.insert(0, util_common.meta_path(path))

        util_common.print_tile_level(tile_level)
        print()
        util_common.print_text_level(tag_level)
        print()
        util_common.print_text_level(game_level)
        print()

        if not no_levels:
            tli = util_common.TileLevelInfo()
            tli.tiles = tile_level
            tli.tags = tag_level
            tli.games = game_level
            tli.meta = text_meta
            ti.levels.append(tli)

    if image_level and tile_output_folder:
        print('saving image tiles')

        if os.path.exists(tile_output_folder):
            shutil_common.rmtree(tile_output_folder)
        os.makedirs(tile_output_folder)

        for tile, tile_image in ts.tile_to_image.items():
            tile_filename = '%s/tile%04d.png' % (tile_output_folder, tile)
            print(tile_filename)
            tile_image.save(tile_filename)
        print()

    print('Found %d tiles' % len(ts.tile_ids))

    return ti



if __name__ == '__main__':
    util_common.timer_start()

    parser = argparse.ArgumentParser(description='Generate tiles from level and/or image.')
    parser.add_argument('--outfile', required=True, type=str, help='Output tile file.')
    parser.add_argument('--basefile', type=str, help='Input base files containing all tiles.')
    parser.add_argument('--textfile', type=str, nargs='+', help='Input text file(s).')
    parser.add_argument('--imagefile', type=str, nargs='+', help='Input image file(s).')
    parser.add_argument('--tagfile', type=str, nargs='+', help='Input tag level file(s).')
    parser.add_argument('--game', type=str, nargs='+', help='Input game(s).')
    parser.add_argument('--pathfile', type=str, nargs='+', help='Input path file(s).')
    parser.add_argument('--tilesize', type=int, help='Size of tiles in image.')
    parser.add_argument('--savetileimages', action='store_true', help='Save tile images.')
    parser.add_argument('--text-key-only', action='store_true', help='Only use text when keying tiles.')
    parser.add_argument('--no-levels', action='store_true', help='Don\'t store levels with tiles.')
    parser.add_argument('--quiet', action='store_true', help='Reduce output.')
    args = parser.parse_args()

    if args.quiet:
        sys.stdout = open(os.devnull, 'w')

    if not args.textfile and not args.imagefile:
        parser.error('--textfile or --imagefile required')

    if args.imagefile and not (args.textfile or args.tilesize):
        parser.error('--imagefile requires --textfile or --tilesize')

    if args.basefile is not None:
        with util_common.openz(args.basefile, 'rb') as f:
            base_tile_info = pickle.load(f)
    else:
        base_tile_info = None

    if args.textfile is not None:
        text_levels = [util_common.read_text_level(textfile, True) for textfile in args.textfile]
    else:
        text_levels = None

    if args.imagefile is not None:
        def open_and_load_image(fn):
            with util_common.openz(fn, 'rb') as f:
                img = PIL.Image.open(f)
                img.load()
                return img
        image_levels = [open_and_load_image(imagefile) for imagefile in args.imagefile]
    else:
        image_levels = None

    if args.tagfile is not None:
        tag_levels = [util_common.read_text_level(tagfile) for tagfile in args.tagfile]
    else:
        tag_levels = None

    if args.pathfile is not None:
        def open_and_load_path(fn):
            with util_common.openz(fn, 'rt') as f:
                return [tuple(edge) for edge in json.load(f)]
        paths = [open_and_load_path(pathfile) for pathfile in args.pathfile]
    else:
        paths = None

    tile_info = input2tiles(base_tile_info, text_levels, image_levels, tag_levels, args.game, paths, args.tilesize,
                            args.no_levels, args.text_key_only, TILE_OUTPUT_FOLDER if args.savetileimages else None)
    with util_common.openz(args.outfile, 'wb') as f:
        pickle.dump(tile_info, f)
