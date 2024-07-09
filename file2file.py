import argparse, base64, json, io, pickle, sys, time
import util_common, util_explore
import numpy as np
import PIL.Image



def image2base64(image):
    bytes_io = io.BytesIO()
    util_common.fresh_image(image).save(bytes_io, 'png')
    bytes_io.flush()
    bytes_io.seek(0)
    return base64.b64encode(bytes_io.read()).decode('ascii')

def image2iid(image, iid_dict, image_list):
    if id(image) not in iid_dict:
        iid_dict[id(image)] = len(image_list)
        image_list.append(image2base64(image))
    return iid_dict[id(image)]

def dict2json(d, encode_val=None):
    if encode_val is None:
        encode_val = lambda x: x
    return [(key, encode_val(val)) for key, val in d.items()]

def tileset2json(ts, encode_image):
    ret = {}
    ret['tile_ids'] = list(ts.tile_ids.keys())
    ret['tile_to_text'] = dict2json(ts.tile_to_text) if ts.tile_to_text is not None else None
    ret['tile_to_image'] = dict2json(ts.tile_to_image, encode_image) if ts.tile_to_image is not None else None
    ret['tile_image_size'] = ts.tile_image_size
    return ret

def tileinfo2json(ti, encode_image):
    ret = {}
    ret['tileset'] = tileset2json(ti.tileset, encode_image)
    ret['levels'] = [{'tiles': tli.tiles, 'tags': tli.tags, 'games': tli.games, 'meta': tli.meta} for tli in ti.levels] if ti.levels is not None else None
    return ret

def exploreinfo2json(ex, encode_image):
    ret = {}
    ret['rows'] = ex.rows
    ret['cols'] = ex.cols
    ret['tileset'] = tileset2json(ex.tileset, encode_image)
    ret['ntind'] = ex.ntind
    ret['neind'] = ex.neind
    ret['npind'] = ex.npind
    ret['void_tind'] = ex.void_tind
    ret['tind_to_text'] = dict2json(ex.tind_to_text)
    ret['tind_to_image'] = dict2json(ex.tind_to_image, encode_image)
    ret['tinds_to_tiles'] = dict2json(ex.tinds_to_tiles)
    ret['eind_to_edge'] = dict2json(ex.eind_to_edge)
    ret['pind_to_prop'] = dict2json(ex.pind_to_prop)
    ret['level_data'] = [base64.b64encode(level_data.tobytes()).decode('ascii') for level_data in ex.level_data]
    return ret

def wrap2json(what, encode):
    iid_dict = {}
    image_list = []
    data = encode(what, lambda x: image2iid(x, iid_dict, image_list))
    ret = {}
    ret['image'] = image_list
    ret['data'] = data
    return ret

def base642image(st):
    return util_common.fresh_image(PIL.Image.open(io.BytesIO(base64.b64decode(st))))

def iid2image(iid, image_list):
    return image_list[iid]

def json2dict(j, decode_key=None, decode_val=None):
    if decode_key is None:
        decode_key = lambda x: x
    if decode_val is None:
        decode_val = lambda x: x
    return {decode_key(key): decode_val(val) for key, val in j}

def json2tileset(obj, decode_image):
    ts = util_common.TileSetInfo()
    ts.tile_ids = dict.fromkeys(obj['tile_ids'])
    ts.tile_to_text = json2dict(obj['tile_to_text']) if obj['tile_to_text'] is not None else None
    ts.tile_to_image = json2dict(obj['tile_to_image'], decode_val=decode_image) if obj['tile_to_image'] is not None else None
    ts.tile_image_size = obj['tile_image_size']
    return ts

def json2tileinfo(obj, decode_image):
    ti = util_common.TileInfo()
    ti.tileset = json2tileset(obj['tileset'], decode_image)
    if obj['levels'] is not None:
        ti.levels = []
        for jtli in obj['levels']:
            tli = util_common.TileLevelInfo()
            tli.tiles = jtli['tiles']
            tli.tags = jtli['tags']
            tli.games = jtli['games']
            tli.meta = [json.loads(json.dumps(entry)) for entry in jtli['meta']]
            ti.levels.append(tli)
    else:
        ti.levels = None
    return ti

def json2exploreinfo(obj, decode_image):
    ex = util_explore.ExploreInfo()
    ex.rows = obj['rows']
    ex.cols = obj['cols']
    ex.tileset = json2tileset(obj['tileset'], decode_image)
    ex.ntind = obj['ntind']
    ex.neind = obj['neind']
    ex.npind = obj['npind']
    ex.void_tind = obj['void_tind']
    ex.tind_to_text = json2dict(obj['tind_to_text'])
    ex.tind_to_image = json2dict(obj['tind_to_image'], decode_val=decode_image)
    ex.tinds_to_tiles = json2dict(obj['tinds_to_tiles'], decode_key=tuple, decode_val=tuple)
    ex.eind_to_edge = json2dict(obj['eind_to_edge'], decode_val=tuple)
    ex.pind_to_prop = json2dict(obj['pind_to_prop'])
    ex.level_data = np.array([np.frombuffer(base64.b64decode(level_data), dtype=np.uint8) for level_data in obj['level_data']])
    return ex

def json2wrap(obj, decode):
    image_list = [base642image(img) for img in obj['image']]
    return decode(obj['data'], lambda x: iid2image(x, image_list))

if __name__ == '__main__':
    util_common.timer_start()

    parser = argparse.ArgumentParser(description='Convert files to/from json.')
    parser.add_argument('--outfile', required=True, type=str, help='Output file.')
    parser.add_argument('--infile', required=True, type=str, help='Input file.')
    args = parser.parse_args()

    FTYPE_EXPLORE = 'explore'
    FTYPE_TILE    = 'tile'
    FTYPE_TILESET = 'tileset'

    ftypes = {}
    ftypes['.explore']  = FTYPE_EXPLORE
    ftypes['.jexplore'] = FTYPE_EXPLORE
    ftypes['.tile']     = FTYPE_TILE
    ftypes['.jtile']    = FTYPE_TILE
    ftypes['.tileset']  = FTYPE_TILESET
    ftypes['.jtileset'] = FTYPE_TILESET

    inwrapjson = {}
    inwrapjson['.jexplore'] = json2exploreinfo
    inwrapjson['.jtile']    = json2tileinfo
    inwrapjson['.jtileset'] = json2tileset

    outwrapjson = {}
    outwrapjson['.jexplore'] = exploreinfo2json
    outwrapjson['.jtile']    = tileinfo2json
    outwrapjson['.jtileset'] = tileset2json

    conversions = {}
    conversions[(FTYPE_TILE, FTYPE_TILESET)] = lambda _tile_info: _tile_info.tileset

    if args.infile == args.outfile:
        util_common.check(False, 'files are the same')

    inext, outext = None, None
    for ext in ftypes:
        if util_common.fileistype(args.infile, ext):
            inext = ext
        if util_common.fileistype(args.outfile, ext):
            outext = ext
    util_common.check(inext is not None and outext is not None, 'unrecognized extension')

    inftype = ftypes[inext]
    outftype = ftypes[outext]

    if inftype == outftype:
        convert = lambda _obj: _obj
    else:
        util_common.check((inftype, outftype) in conversions, 'unrecognized conversion')
        convert = conversions[(inftype, outftype)]

    if inext not in inwrapjson:
        with util_common.openz(args.infile, 'rb') as f:
            obj = pickle.load(f)
    else:
        with util_common.openz(args.infile, 'rt') as f:
            obj = json2wrap(json.load(f), inwrapjson[inext])

    obj = convert(obj)

    if outext not in outwrapjson:
        with util_common.openz(args.outfile, 'wb') as f:
            pickle.dump(obj, f)
    else:
        with util_common.openz(args.outfile, 'wt') as f:
            json.dump(wrap2json(obj, outwrapjson[outext]), f)
            f.write('\n')
