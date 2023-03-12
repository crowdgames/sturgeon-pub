import atexit, os, pickle, shutil, subprocess, sys, time



META_STR        = 'META'
COMMENT_STR     = 'REM'
DRAW_STR        = 'DRAW'

OPEN_TEXT       = '-'
OPEN_TEXT_ZELDA = 'DLOMS-'
START_TEXT      = '{'
GOAL_TEXT       = '}'

DEFAULT_TEXT    = ','
PATH_TEXT       = '.'

VOID_TEXT       = ' '
VOID_TILE       = -1

SPECIAL_CHARS = [PATH_TEXT]
TILE_CHARS = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'



class TileInfo:
    def __init__(self):
        self.tile_ids = None

        self.tile_to_text = None
        self.tile_to_image = None
        self.tile_image_size = None

        self.tile_levels = None
        self.tag_levels = None
        self.game_levels = None



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
        self.tile_ids = None

        self.tile_to_text = None
        self.tile_to_image = None
        self.tile_image_size = None

        self.game_to_tag_to_tiles = None

        self.count_info = None
        self.pattern_info = None



class ReachabilitySetup:
    def __init__(self):
        self.game_to_move = None
        self.wrap_cols = None
        self.goal_loc = None
        self.goal_size = None
        self.open_text = None

class GameMoveInfo:
    def __init__(self):
        self.start_tile = None
        self.goal_tile = None
        self.open_tiles = None

        self.move_template = None
        self.wrap_cols = None

class ReachabilityInfo:
    def __init__(self):
        self.start_rcs = None
        self.goal_rcs = None

        self.game_to_move = None

class ResultReachInfo:
    def __init__(self):
        self.path_edges = None
        self.path_tiles = None
        self.offpath_edges = None

class ResultExecutionInfo:
    def __init__(self):
        self.levels = None
        self.names = None
        self.changes = None
        self.term = None
        self.first_term = None

class ResultInfo:
    def __init__(self):
        self.tile_level = None
        self.text_level = None
        self.image_level = None

        self.reach_info = None

        self.execution_info = None

        self.extra_text_lines = []



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

        if self._last_section != None:
            if mute_time():
                print('...%s done' % self._last_section, flush=True)
            else:
                last = '%.2f' % (curr_time - self._last_time)
                total = '%.2f' % (curr_time - self._start_time)
                print('...%s took %s, %s' % (self._last_section, last, total), flush=True)

        self._last_section = section
        self._last_time = curr_time

        if section != None:
            print('starting %s...' % (section), flush=True)

_section_timer = None
def _timer_stop():
    global _section_timer
    _section_timer.print_section(None)
    _section_timer.print_done()

def timer_start():
    global _section_timer
    _section_timer = SectionTimer()
    atexit.register(_timer_stop)
    print('running ' + subprocess.list2cmdline(sys.argv))

def timer_section(section):
    global _section_timer
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
    print('--SOLVED')
    sys.exit(0)

def exit_solution_not_found():
    print('--NOSOLUTION')
    sys.exit(-1)



def check(cond, msg):
    if not cond:
        raise RuntimeError(msg)

def arg_list_to_dict(parser, name, arg_list, check_option):
    if arg_list == None:
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

def make_grid(rows, cols, elem):
    out = []
    for rr in range(rows):
        out_row = []
        for cc in range(cols):
            out_row.append(elem)
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

def comment_line(comment):
    return META_STR + ' ' + COMMENT_STR + ' ' + comment + '\n'

def draw_path_line(style, points):
    return META_STR + ' ' + DRAW_STR + ' ' + 'PATH: ' + style + '; ' + ', '.join(['%d %d %d %d' % (ra, ca, rb, cd) for (ra, ca, rb, cd) in points]) + '\n'

def draw_line_line(style, points):
    return META_STR + ' ' + DRAW_STR + ' ' + 'LINE: ' + style + '; ' + ', '.join(['%d %d %d %d' % (ra, ca, rb, cd) for (ra, ca, rb, cd) in points]) + '\n'

def draw_tile_line(style, points):
    return META_STR + ' ' + DRAW_STR + ' ' + 'TILE: ' + style + '; ' + ', '.join(['%d %d' % (rr, cc) for (rr, cc) in points]) + '\n'

def draw_rect_line(style, points):
    return META_STR + ' ' + DRAW_STR + ' ' + 'RECT: ' + style + '; ' + ', '.join(['%d %d %d %d' % (ra, ca, rb, cd) for (ra, ca, rb, cd) in points]) + '\n'

def print_result_info(result_info, replace_path_tiles):
    print('tile level')
    print_tile_level(result_info.tile_level)

    if result_info.text_level != None:
        print('text level')
        print_result_text_level(result_info, replace_path_tiles)

    if result_info.execution_info != None:
        print('execution')
        for level, name, first_term in zip(result_info.execution_info.levels, result_info.execution_info.names, result_info.execution_info.first_term):
            if first_term:
                print('>>> TERM <<<')
                print()
            if name:
                print('>>> ' + name)
            print_text_level(level)
            print()

def save_result_info(result_info, prefix):
    result_name = prefix + '.result'
    print('writing result to', result_name)

    with open(result_name, 'wb') as f:
        pickle.dump(result_info, f, pickle.HIGHEST_PROTOCOL)

    if result_info.text_level != None:
        text_name = prefix + '.lvl'
        print('writing text level to', text_name)

        with open(text_name, 'wt') as f:
            print_result_text_level(result_info, False, outfile=f)
            for extra_text_line in result_info.extra_text_lines:
                f.write(extra_text_line)

    if result_info.image_level != None:
        image_name = prefix + '.png'
        print('writing image level to', image_name)

        result_info.image_level.save(image_name)

    if result_info.execution_info != None:
        exec_folder = prefix + '_exec'
        print('writing execution levels to', exec_folder)
        if os.path.exists(exec_folder):
            shutil.rmtree(exec_folder)
        os.makedirs(exec_folder)

        for ii, (level, name, changes, term) in enumerate(zip(result_info.execution_info.levels, result_info.execution_info.names, result_info.execution_info.changes, result_info.execution_info.term)):
            descr = ['term' if term else 'step']
            if name:
                descr.append(name)

            step_name = exec_folder + ('/%02d_' % ii) + '_'.join(descr) + '_exec.lvl'

            with open(step_name, 'wt') as f:
                print_text_level(level, outfile=f)
                if len(result_info.extra_text_lines) != 0:
                    f.write('\n'.join(result_info.extra_text_lines) + '\n')
                if len(changes) != 0:
                    f.write(draw_rect_line('change', changes))
                f.write(comment_line(' MKIII ' + (' '.join(descr))))

def print_tile_level(tile_level, outfile=sys.stdout):
    for row in tile_level:
        for tile in row:
            if tile == VOID_TILE:
                display_tile = VOID_TEXT
            elif tile < len(TILE_CHARS):
                display_tile = TILE_CHARS[tile]
            else:
                display_tile = '?'
            outfile.write(display_tile)
        outfile.write('\n')

def print_result_text_level(result_info, replace_path_tiles, outfile=sys.stdout):
    if result_info.reach_info:
        print_text_level(result_info.text_level, meta_path_edges=result_info.reach_info.path_edges, meta_path_tiles=result_info.reach_info.path_tiles, meta_offpath_edges=result_info.reach_info.offpath_edges, replace_path_tiles=replace_path_tiles, outfile=outfile)
    else:
        print_text_level(result_info.text_level, replace_path_tiles=replace_path_tiles, outfile=outfile)

def print_text_level(text_level, meta_path_edges=None, meta_path_tiles=None, meta_offpath_edges=None, replace_path_tiles=False, outfile=sys.stdout):
    for rr, row in enumerate(text_level):
        for cc, tile in enumerate(row):
            if replace_path_tiles and (rr, cc) in meta_path_tiles:
                outfile.write(PATH_TEXT)
            else:
                outfile.write(tile)
        outfile.write('\n')

    if meta_path_edges != None:
        outfile.write(draw_path_line('path', meta_path_edges))

    if meta_path_tiles != None:
        outfile.write(draw_tile_line('path', meta_path_tiles))

    if meta_offpath_edges != None:
        outfile.write(draw_line_line('offpath', meta_offpath_edges))

def read_text_level(infilename):
    with open(infilename, 'rt') as infile:
        lvl = []
        for line in infile.readlines():
            if line.startswith(META_STR):
                continue

            line = line.rstrip('\n')

            for special_char in SPECIAL_CHARS:
                check(special_char not in line, 'special char ' + special_char + ' in level.')

            lvl.append([c for c in line])
        return lvl
