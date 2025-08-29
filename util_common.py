import atexit, base64, bz2, copy, gzip, io, json, os, pickle, pprint, subprocess, sys, time
import PIL.Image
import webcolors



META_STR         = 'META'

MGROUP_PATH            = 'path'
MGROUP_OFFPATH         = 'offpath'
MGROUP_REACHABLE       = 'reachable'
MGROUP_REACHABLE_BACK  = 'reachable-back'
MGROUP_REACHABLE_STUCK = 'reachable-stuck'
MGROUP_REACHABLE_SINK  = 'reachable-sink'

OPEN_TEXT        = '-'
OPEN_TEXT_ZELDA  = 'DLOMS-'
START_TEXT       = '{'
GOAL_TEXT        = '}'

DEFAULT_TEXT     = ','

VOID_TEXT        = ' '
VOID_TILE        = -1

INDEX_CHARS      = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'



class TileSetInfo:
    def __init__(self):
        self.tile_ids = None

        self.tile_to_text = None
        self.tile_to_image = None
        self.tile_image_size = None

class TileLevelInfo:
    def __init__(self):
        self.tiles = None
        self.tags = None
        self.games = None
        self.meta = None

class TileInfo:
    def __init__(self):
        self.tileset = None
        self.levels = None



class SchemeCountInfo:
    def __init__(self):
        self.divs_size = None

        self.divs_to_game_to_tag_to_tile_count = None

class SchemePatternInfo:
    def __init__(self):
        self.game_to_patterns = None

        self.dr_lo = None
        self.dr_hi = None
        self.dc_lo = None
        self.dc_hi = None
        self.stride_rows = None
        self.stride_cols = None

class SchemeInfo:
    def __init__(self):
        self.tileset = None

        self.game_to_tag_to_tiles = None

        self.count_info = None
        self.pattern_info = None

class ReachJunctionSetup:
    def __init__(self):
        self.text = None
        self.loc = None
        self.loc_params = None

class ReachConnectSetup:
    def __init__(self):
        self.src = None
        self.dst = None

        self.unreachable = None
        self.fwdbwd_layers = None

        self.sink_bottom = None
        self.sink_sides = None

        self.game_to_reach_move = None
        self.missing_aux_closed = None
        self.wrap_rows = None
        self.wrap_cols = None

        self.open_text = None

class ReachJunctionInfo:
    def __init__(self):
        self.text = None
        self.rcs = None
        self.game_to_junction_tile = None

class ReachMoveInfo:
    def __init__(self):
        self.move_template = None
        self.missing_aux_closed = None
        self.wrap_rows = None
        self.wrap_cols = None

class ReachConnectInfo:
    def __init__(self):
        self.src = None
        self.dst = None

        self.unreachable = None
        self.fwdbwd_layers = None

        self.sink_bottom = None
        self.sink_sides = None

        self.game_to_move_info = None

        self.game_to_open_tiles = None

class ResultReachInfo:
    def __init__(self):
        self.path_edges = None
        self.path_locations = None

        self.extra_meta = []

class PlaythroughStepInfo:
    def __init__(self):
        self.name = None
        self.changes = None
        self.text_level = None
        self.image_level = None
        self.term = None
        self.first_term = None

class ResultInfo:
    def __init__(self):
        self.tileset = None

        self.tile_level = None
        self.text_level = None
        self.image_level = None

        self.reach_info = None

        self.playthrough_info = None

        self.solver_id = None
        self.solver_objective = None

        self.extra_meta = []



class SectionTimer:
    def __init__(self):
        self._start_time = time.time()
        self._last_section = None
        self._last_time = None

    def print_done(self):
        if not mute_time():
            print('--TOTALTIME %.2f' % (time.time() - self._start_time))

    def print_section(self, section):
        curr_time = time.time()

        if self._last_section is not None:
            if mute_time():
                print('...%s done' % self._last_section, flush=True)
            else:
                last = '%.2f' % (curr_time - self._last_time)
                total = '%.2f' % (curr_time - self._start_time)
                print('...%s took %s, %s' % (self._last_section, last, total), flush=True)

        self._last_section = section
        self._last_time = curr_time

        if section is not None:
            print('starting %s...' % (section), flush=True)

_section_timer = None
def _timer_stop():
    global _section_timer
    _section_timer.print_section(None)
    _section_timer.print_done()
    _section_timer = None

def print_command():
    print('running ' + subprocess.list2cmdline(sys.argv))

def timer_start(print_cmd=True):
    global _section_timer
    _section_timer = SectionTimer()
    atexit.register(_timer_stop)
    if print_cmd:
        print_command()

def timer_section(section):
    global _section_timer
    if _section_timer is None:
        print(section)
    else:
        _section_timer.print_section(section)



def mute_time():
    return os.environ.get('STG_MUTE_TIME')

def mute_port():
    return os.environ.get('STG_MUTE_PORT')

def write_time(ss):
    if not mute_time():
        sys.stdout.write(ss)
        sys.stdout.flush()

def write_portfolio(ss):
    if not mute_port():
        sys.stdout.write(ss)
        sys.stdout.flush()



def exit_solution_found():
    sys.stdout.write('--SOLVED\n')
    sys.stdout.flush()
    sys.exit(0)

def exit_solution_not_found():
    sys.stdout.write('--NOSOLUTION\n')
    sys.stdout.flush()
    sys.exit(-1)



def check(cond, msg):
    if not cond:
        raise RuntimeError(msg)

def strtobool(val):
    vallo = val.lower()
    if vallo in ['y', 'yes', 't', 'true', 'on', '1']:
        return True
    elif vallo in ['n', 'no', 'f', 'false', 'off', '0']:
        return False
    else:
        raise ValueError('invalid truth value \'' + str(val) + '\'')

def arg_list_to_dict(parser, name, arg_list, default_key, check_key, check_val):
    if arg_list is None:
        return None

    res = {}
    if len(arg_list) == 1 and '=' not in arg_list[0]:
        res[default_key] = check_val(arg_list[0])
    else:
        for kv in arg_list:
            if kv.count('=') != 1:
                parser.error(name + ' as dict must have exactly 1 =')
            key, val = kv.split('=')
            res[check_key(key)] = check_val(val)
    return res

def arg_list_to_dict_str_int(parser, name, arg_list):
    return arg_list_to_dict(parser, name, arg_list, None, str, int)

def arg_list_to_dict_text_options(parser, name, arg_list, val_options, allow_comma_prefix):
    def check_option(option):
        option_check = option.split(',')[0] if allow_comma_prefix else option
        if option_check not in val_options:
            parser.error(name + ' must be in ' + ','.join(val_options))
        return option

    return arg_list_to_dict(parser, name, arg_list, DEFAULT_TEXT, str, check_option)

def load_color_cfg(filename):
    color_cfg = {}

    with open(filename, 'rt') as f:
        cfg = json.load(f)

    if 'tile' in cfg:
        for text, colorname in cfg['tile'].items():
            try:
                color_cfg[text] = tuple(webcolors.name_to_rgb(colorname, 'css3'))
            except ValueError:
                pass

    return color_cfg

def color_to_normal(color):
    return (color[0] / 255, color[1] / 255, color[2] / 255)

def color_to_hex(color):
    return '#%02x%02x%02x' % (int(color[0]), int(color[1]), int(color[2]))

def check_tileset_match(ts0, ts1):
    check(ts0.tile_ids == ts1.tile_ids, 'tileset mismatch')
    check(ts0.tile_image_size == ts1.tile_image_size, 'tileset mismatch')

    if ts0.tile_to_text is not None or ts1.tile_to_text is not None:
        check(ts0.tile_to_text is not None and ts1.tile_to_text is not None, 'tileset mismatch')
        for tile in ts0.tile_ids:
            check(ts0.tile_to_text[tile] == ts1.tile_to_text[tile], 'tileset mismatch')
    else:
        check(ts0.tile_to_text is None and ts1.tile_to_text is None, 'tileset mismatch')

    if ts0.tile_to_image is not None or ts1.tile_to_image is not None:
        check(ts0.tile_to_image is not None and ts1.tile_to_image is not None, 'tileset mismatch')
        for tile in ts0.tile_ids:
            check(tuple(ts0.tile_to_image[tile].getdata()) == tuple(ts1.tile_to_image[tile].getdata()), 'tileset mismatch')
    else:
        check(ts0.tile_to_image is None and ts1.tile_to_image is None, 'tileset mismatch')

def make_grid(rows, cols, elem):
    out = []
    for rr in range(rows):
        out_row = []
        for cc in range(cols):
            out_row.append(copy.copy(elem))
        out.append(out_row)
    return out

def grid_size(grid):
    rows = len(grid)
    cols = None
    for row in grid:
        if cols is None:
            cols = len(row)
        else:
            check(len(row) == cols, 'grid not rectangular')
    return rows, cols

def xform_grid_rotate_cw(grid):
    return [list(elem) for elem in zip(*grid[::-1])]

def xform_grid_flip_rows(grid):
    return list(reversed(grid))

def xform_grid_flip_cols(grid):
    return [list(reversed(row)) for row in grid]

def xform_grid_pad_side(grid, ll, rr):
    new_grid = []
    for row in grid:
        new_grid.append([ll] + row + [rr])
    return new_grid

def xform_grid_pad_around(grid, tl, tt, tr, ll, rr, bl, bb, br):
    cols = len(grid[0])
    new_grid = []
    new_grid.append([tl] + ([tt] * cols) + [tr])
    for row in grid:
        new_grid.append([ll] + row + [rr])
    new_grid.append([bl] + ([bb] * cols) + [br])
    return new_grid

def corner_indices(til, depth):
    def corner_indices_helper(_fra, _til, _depth, _sofar, _track):
        if _depth == 0:
            _track.append(_sofar)
        else:
            for _ind in range(_fra, _til):
                corner_indices_helper(_ind + 1, _til, _depth - 1, _sofar + (_ind,), _track)
    ret = []
    corner_indices_helper(0, til, depth, (), ret)
    return ret

def fileistype(fn, ext):
    return fn.endswith(ext) or fn.endswith(ext + '.gz') or fn.endswith(ext + '.bz2')

def fresh_image(image):
    image_data = PIL.Image.new(image.mode, image.size)
    image_data.putdata(image.getdata())
    return image_data

def image_to_bytes_io(image):
    bytes_io = io.BytesIO()
    fresh_image(image).save(bytes_io, 'png')
    bytes_io.flush()
    bytes_io.seek(0)
    return bytes_io

def image_to_bytes(image):
    return image_to_bytes_io(image).read()

def image_to_b64ascii(image):
    return base64.b64encode(image_to_bytes(image)).decode('ascii')

def image_from_bytes(fr):
    return fresh_image(PIL.Image.open(io.BytesIO(fr)))

def image_from_b64ascii(fr):
    return image_from_bytes(base64.b64decode(fr))

def trim_void_tile_level(tile_level):
    rows, cols = len(tile_level), len(tile_level[0])

    rr_lo, rr_hi = rows, 0
    for rr in range(rows):
        any_nonvoid = False
        for cc in range(cols):
            if tile_level[rr][cc] != VOID_TILE:
                any_nonvoid = True
                break
        if any_nonvoid:
            rr_lo = min(rr_lo, rr)
            rr_hi = max(rr_hi, rr + 1)

    cc_lo, cc_hi = cols, 0
    for cc in range(cols):
        any_nonvoid = False
        for rr in range(rows):
            if tile_level[rr][cc] != VOID_TILE:
                any_nonvoid = True
                break
        if any_nonvoid:
            cc_lo = min(cc_lo, cc)
            cc_hi = max(cc_hi, cc + 1)

    ret = []
    for rr in range(rr_lo, rr_hi):
        row = []
        for cc in range(cc_lo, cc_hi):
            row.append(tile_level[rr][cc])
        ret.append(row)
    print(rr_lo, rr_hi, cc_lo, cc_hi)
    print(ret)
    return ret

def tile_level_to_text_level(tile_level, tileset):
    rows, cols = len(tile_level), len(tile_level[0])

    text_level = make_grid(rows, cols, VOID_TEXT)
    for rr in range(rows):
        for cc in range(cols):
            if tile_level[rr][cc] != VOID_TILE:
                text_level[rr][cc] = tileset.tile_to_text[tile_level[rr][cc]]
    return text_level

def tile_level_to_image_level(tile_level, tileset):
    rows, cols = len(tile_level), len(tile_level[0])

    image_level = PIL.Image.new('RGBA', (cols * tileset.tile_image_size, rows * tileset.tile_image_size), (0, 0, 0, 0))
    for rr in range(rows):
        for cc in range(cols):
            if tile_level[rr][cc] != VOID_TILE:
                image_level.paste(tileset.tile_to_image[tile_level[rr][cc]], (cc * tileset.tile_image_size, rr * tileset.tile_image_size))
    return image_level

def get_meta_path(meta):
    if meta is not None:
        for md in meta:
            if md['type'] == 'geom' and md['shape'] == 'path' and md['group'] == MGROUP_PATH:
                return [tuple(elem) for elem in md['data']]
    return None

def get_meta_properties(meta):
    if meta is not None:
        ret = None
        for md in meta:
            if md['type'] == 'property':
                if ret is None:
                    ret = []
                ret += md['value']
        return ret
    return None

def meta_check_json(obj):
    check(type(obj) == dict, 'json')
    check('type' in obj, 'json')
    check(type(obj['type']) == str, 'json')
    for key, value in obj.items():
        check(type(key) == str, 'json')
        check(type(value) in [str, int, float, list], 'json')
        if type(value) == list:
            for elem in value:
                check(type(elem) in [str, int, float, list], 'json')
                if type(elem) == list:
                    for elem2 in elem:
                        check(type(elem2) in [str, int, float], 'json')
    return obj

def meta_path(group, data):
    return meta_check_json({ 'type': 'geom', 'shape': 'path', 'group': group, 'data': [list(elem) for elem in data] })

def meta_line(group, data):
    return meta_check_json({ 'type': 'geom', 'shape': 'line', 'group': group, 'data': [list(elem) for elem in data] })

def meta_tile(group, data):
    return meta_check_json({ 'type': 'geom', 'shape': 'tile', 'group': group, 'data': [list(elem) for elem in data] })

def meta_rect(group, data):
    return meta_check_json({ 'type': 'geom', 'shape': 'rect', 'group': group, 'data': [list(elem) for elem in data] })

def meta_properties(data):
    return meta_check_json({ 'type': 'property', 'value': data })

def meta_custom(data):
    return meta_check_json(data)

def remove_meta_geom_groups(meta, groups):
    if meta is None:
        return None

    ret = []
    for md in meta:
        if md['type'] == 'geom' and md['group'] in groups:
            continue
        ret.append(md)
    return ret

def openz(filename, mode):
    if filename.endswith('.gz'):
        return gzip.open(filename, mode)
    elif filename.endswith('.bz2'):
        return bz2.open(filename, mode)
    else:
        return open(filename, mode)

def get_meta_from_result(result_info):
    meta = []

    meta.append(meta_custom({ 'type': 'solver', 'id': result_info.solver_id, 'objective': result_info.solver_objective }))

    for reach_info in result_info.reach_info:
        if reach_info.path_edges is not None:
            meta.append(meta_path(MGROUP_PATH, reach_info.path_edges))
        if reach_info.path_locations is not None:
            meta.append(meta_tile(MGROUP_PATH, reach_info.path_locations))
        meta += reach_info.extra_meta

    meta += result_info.extra_meta

    return meta

def summarize_scheme_info(scheme_info, outstream):
    printer = pprint.PrettyPrinter(width=200, stream=outstream)
    printer.pprint(scheme_info.game_to_tag_to_tiles)

    outstream.write('\n')
    if scheme_info.count_info is not None:
        outstream.write('Counts:\n')
        printer.pprint(scheme_info.count_info.divs_to_game_to_tag_to_tile_count)
    else:
        outstream.write('No counts.\n')

    outstream.write('\n')
    if scheme_info.pattern_info is not None:
        outstream.write('Patterns:\n')
        outstream.write(f'{scheme_info.pattern_info.dr_lo} {scheme_info.pattern_info.dr_hi} {scheme_info.pattern_info.dc_lo} {scheme_info.pattern_info.dc_hi} {scheme_info.pattern_info.stride_rows} {scheme_info.pattern_info.stride_cols}\n')
        printer.pprint(scheme_info.pattern_info.game_to_patterns)
    else:
        outstream.write('No patterns.\n')

def print_result_info(result_info, outstream):
    outstream.write('tile level\n')
    print_tile_level(result_info.tile_level, outstream)

    if result_info.text_level is not None:
        outstream.write('text level\n')
        print_result_text_level(result_info)

def save_result_info(result_info, prefix, compress=False, save_level=True, save_result=True, save_tlvl=True):
    if save_result:
        result_name = prefix + '.result'
        if compress:
            result_name += '.gz'
        print('writing result to', result_name)

        with openz(result_name, 'wb') as f:
            pickle.dump(result_info, f)

    if save_level:
        if result_info.text_level is not None:
            text_name = prefix + '.lvl'
            print('writing text level to', text_name)

            with openz(text_name, 'wt') as f:
                print_result_text_level(result_info, outstream=f)

        if result_info.image_level is not None:
            image_name = prefix + '.png'
            print('writing image level to', image_name)

            result_info.image_level.save(image_name)

    if save_tlvl:
        json_name = prefix + '.tlvl'
        if compress:
            json_name += '.gz'
        print('writing json to', json_name)

        with openz(json_name, 'wt') as f:
            print_tile_level_json(result_info.tile_level, meta=get_meta_from_result(result_info), outstream=f)

def index_to_char(idx):
    if idx < len(INDEX_CHARS):
        return INDEX_CHARS[idx]
    else:
        return '?'

def print_tile_level(tile_level, outstream=None):
    if outstream is None:
        outstream = sys.stdout

    for row in tile_level:
        for tile in row:
            if tile == VOID_TILE:
                display_tile = VOID_TEXT
            else:
                display_tile = index_to_char(tile)
            outstream.write(display_tile)
        outstream.write('\n')

def print_tile_level_json(tile_level, meta=None, outstream=None):
    if outstream is None:
        outstream = sys.stdout

    json_data = {}
    json_data['tile_level'] = tile_level
    if meta != None:
        json_data['meta'] = meta

    json.dump(json_data, outstream)
    outstream.write('\n')

def print_result_text_level(result_info, outstream=None):
    if outstream is None:
        outstream = sys.stdout

    meta = get_meta_from_result(result_info)

    print_text_level(result_info.text_level, meta=meta, outstream=outstream)

def print_text_level(text_level, meta=None, outstream=None):
    if outstream is None:
        outstream = sys.stdout

    for row in text_level:
        for tile in row:
            outstream.write(tile)
        outstream.write('\n')

    if meta is not None:
        for md in meta:
            outstream.write(META_STR + ' ' + json.dumps(md) + '\n')

def process_old_meta(line):
    TAG = 'META DRAW'
    if line.startswith(TAG):
        res = {}
        res['type'] = 'geom'

        line = line[len(TAG):].strip()

        splt = line.split(':')
        check(len(splt) == 2, 'split')
        res['shape'] = splt[0].strip().lower()
        line = splt[1].strip()

        splt = line.split(';')
        if len(splt) == 1:
            points_str = splt[0].strip()
        elif len(splt) == 2:
            res['group'] = splt[0].strip()
            points_str = splt[1].strip()
        else:
            check(False, 'split')

        def _number(_s):
            _ret = float(_s)
            if _ret == int(_ret):
                return int(_ret)
            else:
                return _ret

        res['data'] = [tuple([_number(el) for el in pt.strip().split()]) for pt in points_str.split(',')]
        return res

    TAG = 'META REM'
    if line.startswith(TAG):
        return {'type': 'comment', 'value': line[len(TAG):].strip()}

    return None

def read_text_level(infilename, include_meta=False):
    with openz(infilename, 'rt') as infile:
        lvl = []
        meta = []

        for line in infile.readlines():
            line = line.rstrip('\n')

            old_meta = process_old_meta(line)
            if old_meta is not None:
                meta.append(old_meta)
            elif line.startswith(META_STR):
                if include_meta:
                    meta.append(json.loads(line[len(META_STR):]))
            else:
                lvl.append([c for c in line])

        if include_meta:
            return lvl, meta
        else:
            return lvl



def get_path_edge(fr, fc, tr, tc, pwtr, pwtc):
    if (tr, tc) == (pwtr, pwtc):
        return (fr, fc, tr, tc)
    else:
        return (fr, fc, tr, tc, pwtr, pwtc)

def get_edge_keys_from(pt, rows, cols, move_info, all_locations, open_locations, closed_locations, exclude):
    rr, cc = pt
    edge_keys = []

    all_locations = set(all_locations)
    open_locations = set(open_locations)
    closed_locations = set(closed_locations)
    exclude = set(exclude)

    for move in move_info.move_template:
        dest_delta, need_open_path_delta, need_open_aux_delta, need_closed_path_delta, need_closed_aux_delta = move

        def inst_deltas(_deltas, _exclude_these, _ignore_missing):
            _inst = ()
            for _dr, _dc in _deltas:
                _nr = rr + _dr
                _nc = cc + _dc
                if move_info.wrap_rows: _nr = _nr % rows
                if move_info.wrap_cols: _nc = _nc % cols
                if (_nr, _nc) in _exclude_these:
                    return None
                if (_nr, _nc) not in all_locations:
                    if _ignore_missing:
                        continue
                    else:
                        return None
                _inst = _inst + ((_nr, _nc),)
            return _inst

        need_open_path = inst_deltas(need_open_path_delta, closed_locations, False)
        if need_open_path is None:
            continue

        need_open_aux = inst_deltas(need_open_aux_delta, closed_locations, False)
        if need_open_aux is None:
            continue

        need_closed_path = inst_deltas(need_closed_path_delta, open_locations, False)
        if need_closed_path is None:
            continue

        need_closed_aux = inst_deltas(need_closed_aux_delta, open_locations, move_info.missing_aux_closed)
        if need_closed_aux is None:
            continue

        dest = inst_deltas([dest_delta], set.union(closed_locations, exclude), False)
        if dest is None:
            continue

        tr, tc = dest[0]

        pwtr = rr + dest_delta[0]
        pwtc = cc + dest_delta[1]

        edge_key = (rr, cc, tr, tc, pwtr, pwtc, need_open_path, need_open_aux, need_closed_path, need_closed_aux)
        edge_keys.append(edge_key)

    return edge_keys
