import argparse, os, shutil, pickle, sys
import PIL.Image
import util



TILE_OUTPUT_FOLDER = 'tiles'



def input2tiles(text_levels, image_levels, tag_levels, games, tile_image_size, tile_output_folder):
    ti = util.TileInfo()

    ti.tile_ids = {}

    ti.tile_to_text = {} if text_levels else None
    ti.tile_to_image = {} if image_levels else None
    ti.tile_image_size = tile_image_size

    ti.tile_levels = []
    ti.tag_levels = []
    ti.game_levels = []



    if text_levels:
        level_count = len(text_levels)
    elif image_levels:
        level_count = len(image_levels)
    else:
        util.check(False, 'text and image both missing')

    if text_levels:
        util.check(len(text_levels) == level_count, 'need same number of levels')
    else:
        text_levels = [None] * level_count

    if image_levels:
        util.check(len(image_levels) == level_count, 'need same number of levels')
    else:
        image_levels = [None] * level_count

    if tag_levels:
        util.check(len(tag_levels) == level_count, 'need same number of levels')
    else:
        tag_levels = [None] * level_count

    if games:
        util.check(len(games) == level_count, 'need same number of levels')
    else:
        games = [None] * level_count



    tile_key_to_tile_id = {}

    for text_level, image_level, tag_level, game in zip(text_levels, image_levels, tag_levels, games):
        if text_level:
            text_sz = (len(text_level), len(text_level[0]))
        else:
            text_sz = None

        if image_level:
            image_sz = image_level.size
            util.check(image_sz[0] % tile_image_size == 0 and image_sz[1] % tile_image_size == 0, 'Image size not multiple of tile size')
            image_sz = (image_sz[1] // tile_image_size, image_sz[0] // tile_image_size)
        else:
            image_sz = None

        if text_sz and image_sz:
            util.check(text_sz == image_sz, 'text and image size mismatch')
            rows, cols = text_sz
        elif text_sz:
            rows, cols = text_sz
        elif image_sz:
            rows, cols = image_sz
        else:
            util.check(False, 'text and image both missing')

        tile_level = []
        for rr in range(rows):
            tile_level_row = []
            for cc in range(cols):
                tile_key = ()

                tile_text = None
                tile_text_is_void = None
                if text_level:
                    tile_text = text_level[rr][cc]
                    tile_key = tile_key + (tile_text,)
                    tile_text_is_void = (tile_text == util.VOID_TEXT)

                tile_image = None
                tile_image_is_void = None
                if image_level:
                    tile_image = image_level.crop((cc * tile_image_size, rr * tile_image_size, cc * tile_image_size + tile_image_size, rr * tile_image_size + tile_image_size))
                    tile_rgba_data = tile_image.convert('RGBA').getdata()
                    tile_key = tile_key + (tuple(tile_rgba_data),)
                    tile_image_is_void = (sum([ch for px in tile_rgba_data for ch in px]) == 0)

                if tile_text_is_void or tile_image_is_void:
                    util.check(tile_text_is_void in [True, None], 'void')
                    util.check(tile_image_is_void in [True, None], 'void')
                    tile_id = util.VOID_TILE

                else:
                    if tile_key not in tile_key_to_tile_id:
                        tile_id = len(ti.tile_ids)
                        ti.tile_ids[tile_id] = None

                        tile_key_to_tile_id[tile_key] = tile_id

                        if tile_text:
                            ti.tile_to_text[tile_id] = tile_text
                        if tile_image:
                            ti.tile_to_image[tile_id] = tile_image
                    else:
                        tile_id = tile_key_to_tile_id[tile_key]

                tile_level_row.append(tile_id)
            tile_level.append(tile_level_row)

        if tag_level == None:
            tag_level = util.make_grid(rows, cols, util.DEFAULT_TEXT)
            for rr in range(rows):
                for cc in range(cols):
                    if tile_level[rr][cc] == util.VOID_TILE:
                        tag_level[rr][cc] = util.VOID_TEXT
        else:
            util.check(len(tag_level) == rows, 'tile and tag level row count mismatch')
            for rr in range(rows):
                util.check(len(tag_level[rr]) == cols, 'row length mismatch')
                for cc in range(cols):
                    util.check((tile_level[rr][cc] == util.VOID_TILE) == (tag_level[rr][cc] == util.VOID_TEXT), 'void')

        if game == None:
            game_level = util.make_grid(rows, cols, util.DEFAULT_TEXT)
        else:
            util.check(type(game) == str and len(game) == 1, 'game')
            game_level = util.make_grid(rows, cols, game)

        util.print_tile_level(tile_level)
        print()
        util.print_text_level(tag_level)
        print()
        util.print_text_level(game_level)
        print()

        ti.tile_levels.append(tile_level)
        ti.tag_levels.append(tag_level)
        ti.game_levels.append(game_level)

    if image_level and tile_output_folder:
        print('saving image tiles')

        if os.path.exists(tile_output_folder):
            shutil.rmtree(tile_output_folder)
        os.makedirs(tile_output_folder)

        for tile, tile_image in ti.tile_to_image.items():
            tile_filename = '%s/tile%04d.png' % (tile_output_folder, tile)
            print(tile_filename)
            tile_image.save(tile_filename)
        print()

    print('Found %d tiles' % len(ti.tile_ids))

    return ti



if __name__ == '__main__':
    util.timer_start()

    parser = argparse.ArgumentParser(description='Generate tiles from level and/or image.')
    parser.add_argument('--outfile', required=True, type=str, help='Output tile file.')
    parser.add_argument('--textfile', type=str, nargs='+', help='Input text file(s).')
    parser.add_argument('--imagefile', type=str, nargs='+', help='Input image file(s).')
    parser.add_argument('--tagfile', type=str, nargs='+', help='Input tag level file(s).')
    parser.add_argument('--game', type=str, nargs='+', help='Input game(s).')
    parser.add_argument('--tilesize', type=int, help='Size of tiles in image.')
    parser.add_argument('--savetileimages', action='store_true', help='Save tile images.')
    args = parser.parse_args()

    if not args.textfile and not args.imagefile:
        parser.error('--textfile or --imagefile required')

    if args.imagefile and not args.tilesize:
        parser.error('--imagefile requires --tilesize')

    if args.textfile != None:
        text_levels = [util.read_text_level(textfile) for textfile in args.textfile]
    else:
        text_levels = None

    if args.imagefile != None:
        image_levels = [PIL.Image.open(imagefile) for imagefile in args.imagefile]
    else:
        image_levels = None

    if args.tagfile:
        tag_levels = [util.read_text_level(tagfile) for tagfile in args.tagfile]
    else:
        tag_levels = None

    tile_info = input2tiles(text_levels, image_levels, tag_levels, args.game, args.tilesize, TILE_OUTPUT_FOLDER if args.savetileimages else None)
    with open(args.outfile, 'wb') as f:
        pickle.dump(tile_info, f, pickle.HIGHEST_PROTOCOL)
