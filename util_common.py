import atexit, bz2, copy, gzip, json, os, pickle, shutil, subprocess, sys, time
import PIL.Image



META_STR         = 'META'

MGROUP_PATH      = 'path'
MGROUP_OFFPATH   = 'offpath'
MGROUP_REACHABLE = 'reachable'

OPEN_TEXT        = '-'
OPEN_TEXT_ZELDA  = 'DLOMS-'
START_TEXT       = '{'
GOAL_TEXT        = '}'

DEFAULT_TEXT     = ','
PATH_TEXT        = 'p'

VOID_TEXT        = ' '
VOID_TILE        = -1

SPECIAL_CHARS    = [PATH_TEXT]
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

        self.stride_rows = None
        self.stride_cols = None
        self.dr_lo = None
        self.dr_hi = None
        self.dc_lo = None
        self.dc_hi = None

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
        self.game_to_move = None
        self.open_text = None
        self.wrap_cols = None
        self.unreachable = None

class ReachJunctionInfo:
    def __init__(self):
        self.text = None
        self.rcs = None
        self.game_to_junction_tile = None

class GameMoveInfo:
    def __init__(self):
        self.move_template = None
        self.open_tiles = None
        self.wrap_cols = None

class ReachConnectInfo:
    def __init__(self):
        self.src = None
        self.dst = None
        self.game_to_move = None
        self.unreachable = None

class ResultReachInfo:
    def __init__(self):
        self.path_edges = None
        self.path_tiles = None
        self.offpath_edges = None

class ExecutionStepInfo:
    def __init__(self):
        self.name = None
        self.changes = None
        self.text_level = None
        self.image_level = None
        self.term = None
        self.first_term = None

class ResultInfo:
    def __init__(self):
        self.tile_level = None
        self.text_level = None
        self.image_level = None

        self.reach_info = None

        self.execution_info = None

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

def timer_start(print_cmdline=True):
    global _section_timer
    _section_timer = SectionTimer()
    atexit.register(_timer_stop)
    if print_cmdline:
        print('running ' + subprocess.list2cmdline(sys.argv))

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

def arg_list_to_dict(parser, name, arg_list, check_option):
    if arg_list is None:
        return None

    res = {}
    if len(arg_list) == 1 and '=' not in arg_list[0]:
        res[DEFAULT_TEXT] = check_option(arg_list[0])
    else:
        for kv in arg_list:
            if kv.count('=') != 1:
                parser.error(name + ' as dict must have exactly 1 =')
            key, val = kv.split('=')
            res[key] = check_option(val)
    return res

def arg_list_to_dict_int(parser, name, arg_list):
    return arg_list_to_dict(parser, name, arg_list, int)

def arg_list_to_dict_options(parser, name, arg_list, val_options):
    def check_option(option):
        if option not in val_options:
            parser.error(name + ' must be in ' + ','.join(val_options))
        return option

    return arg_list_to_dict(parser, name, arg_list, check_option)

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

def rotate_grid_cw(grid):
    return [list(elem) for elem in zip(*grid[::-1])]

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
        meta.append(meta_path(MGROUP_PATH, reach_info.path_edges))
        meta.append(meta_tile(MGROUP_PATH, reach_info.path_tiles))
        meta.append(meta_line(MGROUP_OFFPATH, reach_info.offpath_edges))

    if result_info.extra_meta is not None:
        meta += result_info.extra_meta

    return meta

def print_result_info(result_info, replace_path_tiles):
    print('tile level')
    print_tile_level(result_info.tile_level)

    if result_info.text_level is not None:
        print('text level')
        print_result_text_level(result_info, replace_path_tiles)

    if result_info.execution_info is not None:
        print('execution')
        for step_info in result_info.execution_info:
            if step_info.first_term:
                print('>>> TERM <<<')
                print()
            if step_info.name:
                print('>>> ' + step_info.name)
            print_text_level(step_info.text_level)
            print()

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
                print_result_text_level(result_info, False, outfile=f)

        if result_info.image_level is not None:
            image_name = prefix + '.png'
            print('writing image level to', image_name)

            result_info.image_level.save(image_name)

        if result_info.execution_info is not None:
            exec_folder = prefix + '_exec'
            print('writing execution levels to', exec_folder)
            if os.path.exists(exec_folder):
                shutil.rmtree(exec_folder)
            os.makedirs(exec_folder)

            for ii, step_info in enumerate(result_info.execution_info):
                descr = ['term' if step_info.term else 'step']
                if step_info.name:
                    descr.append(step_info.name)

                step_prefix = exec_folder + ('/%02d_' % ii) + '_'.join(descr) + '_exec'

                meta = result_info.extra_meta
                if len(step_info.changes) != 0:
                    meta.append(meta_rect('change', step_info.changes))
                meta.append(meta_custom({'type': 'mkiii', 'desc': descr}))

                step_text_name = step_prefix + '.lvl'
                with openz(step_text_name, 'wt') as f:
                    print_text_level(step_info.text_level, meta=meta, outfile=f)

                if step_info.image_level is not None:
                    step_image_name = step_prefix + '.png'
                    step_info.image_level.save(step_image_name)

    if save_tlvl:
        json_name = prefix + '.tlvl'
        if compress:
            json_name += '.gz'
        print('writing json to', json_name)

        with openz(json_name, 'wt') as f:
            print_tile_level_json(result_info.tile_level, meta=get_meta_from_result(result_info), outfile=f)

def index_to_char(idx):
    if idx < len(INDEX_CHARS):
        return INDEX_CHARS[idx]
    else:
        return '?'

def print_tile_level(tile_level, outfile=None):
    if outfile is None:
        outfile = sys.stdout

    for row in tile_level:
        for tile in row:
            if tile == VOID_TILE:
                display_tile = VOID_TEXT
            else:
                display_tile = index_to_char(tile)
            outfile.write(display_tile)
        outfile.write('\n')

def print_tile_level_json(tile_level, meta=None, outfile=None):
    if outfile is None:
        outfile = sys.stdout

    json_data = {}
    json_data['tile_level'] = tile_level
    if meta != None:
        json_data['meta'] = meta

    json.dump(json_data, outfile)
    outfile.write('\n')

def print_result_text_level(result_info, replace_path_tiles, outfile=None):
    if outfile is None:
        outfile = sys.stdout

    meta = get_meta_from_result(result_info)

    if replace_path_tiles and result_info.reach_info is not None:
        path_tiles = result_info.reach_info.path_tiles
    else:
        path_tiles = None

    print_text_level(result_info.text_level, meta=meta, replace_path_tiles=path_tiles, outfile=outfile)

def print_text_level(text_level, meta=None, replace_path_tiles=None, outfile=None):
    if outfile is None:
        outfile = sys.stdout

    for rr, row in enumerate(text_level):
        for cc, tile in enumerate(row):
            if replace_path_tiles is not None and (rr, cc) in replace_path_tiles:
                outfile.write(PATH_TEXT)
            else:
                outfile.write(tile)
        outfile.write('\n')

    if meta is not None:
        for md in meta:
            outfile.write(META_STR + ' ' + json.dumps(md) + '\n')

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
                for special_char in SPECIAL_CHARS:
                    check(special_char not in line, 'special char ' + special_char + ' in level.')

                lvl.append([c for c in line])

        if include_meta:
            return lvl, meta
        else:
            return lvl
