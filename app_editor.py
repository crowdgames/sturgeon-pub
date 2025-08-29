import argparse, hashlib, io, json, math, multiprocessing, os, pickle, queue, random, string, sys, time
import scheme2output, util_common, util_custom, util_path, util_reach, util_solvers
import PIL.Image, PIL.ImageTk
import tkinter

WEIGHT_APP     =  100

INSET          =   10
CELL_SIZE      =   25

LEVEL_COUNT    =  128

MAX_SIZE       =  800
REFRESH_MSEC   =   50
INIT_DELAY_SEC =    2.0
PATH_DELAY_SEC =    1.0

MODE_PATHED    = 'MODE_PATHED'
MODE_TEXTED    = 'MODE_TEXTED'
MODE_TEST      = 'MODE_TEST'
MODES = [MODE_PATHED, MODE_TEXTED, MODE_TEST]



def tocvs(x):
    return (x * CELL_SIZE) + INSET

def fromcvs(x):
    return (x - INSET) / CELL_SIZE

def encode_result_info(result_info):
    if result_info is not None:
        if result_info.image_level is not None:
            result_info.image_level = True

def decode_result_info(result_info):
    if result_info is not None:
        if result_info.image_level is not None:
            result_info.image_level = util_common.tile_level_to_image_level(result_info.tile_level, result_info.tileset)



class PathCanvas(tkinter.Canvas):
    def __init__(self, parent, cfg, mode, out_no_hash, app_state, app_weight):
        super().__init__(parent)

        util_common.check(cfg.scheme_info.tileset.tile_to_text is not None, 'no text in tileset')

        self._cfg = cfg

        self._rows = cfg.rows
        self._cols = cfg.cols

        self._out_no_hash = out_no_hash
        self._app_weight = app_weight

        self._seed_gen = 0
        self._seed_rand_path = 0
        self._reverse = False

        self._game_locations = { (rr, cc): cfg.game_level[rr][cc] for rr in range(self._rows) for cc in range(self._cols) }

        if cfg.reach_connect_setups is not None:
            util_common.check(len(cfg.reach_connect_setups) == 1, 'need at most one reach connect setup')
            self._game_to_move_info = util_reach.get_reach_connect_info(cfg.reach_connect_setups[0], cfg.rows, cfg.cols, cfg.scheme_info).game_to_move_info
        else:
            self._game_to_move_info = None

        self._path_nexts = None
        self._path_open = {}
        self._path_closed = {}

        self._working_draw = []
        self._gen_objective = None

        self._mouse = None
        self._mouse_text_copy = None
        self._draw_open_closed = False
        self._mouse_draw = []

        self._path_or_point = None if (app_state is None or 'path' not in app_state) else [tuple(pt) for pt in app_state['path']]
        self._gen_path = None
        self._path_draw = []

        self._text_level = None if (app_state is None or 'text' not in app_state) else app_state['text']
        self._text_level_draw = []

        self._grid_draw = []

        self._gen_image = None
        self._gen_text = None
        self._image_draw = []

        self._gen_result = None

        self._gen_proc = None
        self._gen_proc_wanted = None
        self._gen_proc_termed = False
        self._gen_proc_q = None

        self.bind_all('<Escape>', self.on_evt_all_tog_mode)
        self.bind_all('<Return>', self.on_evt_all_export)      # export
        self.bind_all('<Right>',  self.on_evt_all_next_level)  # next generated level
        self.bind_all('<Left>',   self.on_evt_all_prev_level)  # previous generated level
        self.bind('<Motion>',          self.on_mouse_motion)
        self.bind('<Leave>',           self.on_mouse_leave)
        self.bind('<ButtonPress-1>',   self.on_mouse_down)
        self.bind('<ButtonRelease-1>', self.on_mouse_up)
        self.after(REFRESH_MSEC, self.on_timer)

        self._mode = mode if mode in MODES else MODES[0]
        self._bindings = []
        self.set_mode(mode)

        self._scrollregion = None

        self.recompute_nexts()
        self.recompute_texts()
        self.redraw_from_image()
        self.restart_gen_proc(INIT_DELAY_SEC)

    def set_mode(self, mode):
        def unbind_keys():
            for key, callback_id in self._bindings:
                self.unbind_all(key)
            self._bindings = []

        def bind_key(key, callback):
            self._bindings.append((key, self.bind_all(key, callback)))

        self._mouse_text_copy = None

        if mode == MODE_PATHED:
            print('mode: pathed')
            self.winfo_toplevel().title('pathed')
            self._mode = mode
            unbind_keys()
            bind_key('<BackSpace>',       self.on_evt_path_del_end)         # delete from end
            bind_key('<KeyPress-=>',      self.on_evt_path_del_begin)       # delete from beginning
            bind_key('<KeyPress-c>',      self.on_evt_path_copy)            # copy generated path
            bind_key('<Shift-BackSpace>', self.on_evt_path_clear)           # clear path
            bind_key('<KeyPress-p>',      self.on_evt_path_tog_begend)      # toggle add to beginning/end
            bind_key('<KeyPress-o>',      self.on_evt_path_tog_opcl)        # toggle show open/closed tiles
            bind_key('<KeyPress-r>',      self.on_evt_path_random)          # random path
            bind_key('<KeyPress-s>',      self.on_evt_path_shortest_drawn)  # shortest path between drawn beginning/end
            bind_key('<KeyPress-w>',      self.on_evt_path_shortest_gen)    # shortest path between generated beginning/end in level

        elif mode == MODE_TEXTED:
            print('mode: texted')
            self.winfo_toplevel().title('texted')
            self._mode = mode
            unbind_keys()
            bind_key('<KeyPress>',        self.on_evt_text_change)         # change text
            bind_key('<Up>',              self.on_evt_text_copy)           # copy text
            bind_key('<BackSpace>',       self.on_evt_text_del)            # delete text
            bind_key('<Down>',            self.on_evt_text_del_same_after) # delete text
            bind_key('<Shift-BackSpace>', self.on_evt_text_clear)          # clear text

        elif mode == MODE_TEST:
            print('mode: test')
            self.winfo_toplevel().title('test')
            self._mode = mode
            unbind_keys()

    def get_gen_text_level(self):
        return self._gen_text

    def create_text_level_if_needed(self):
        if self._text_level is None:
            self._text_level = util_common.make_grid(self._cfg.rows, self._cfg.cols, util_common.DEFAULT_TEXT)

    def clear_text_level_if_needed(self):
        if self._text_level is not None:
            all_default = True
            for row in self._text_level:
                for text in row:
                    if text != util_common.DEFAULT_TEXT:
                        all_default = False
                        break
            if all_default:
                self._text_level = None

    def restart_gen_proc(self, delay):
        self._gen_proc_wanted = time.time() + delay

    def is_gen_proc_running(self):
        return self._gen_proc is not None

    @staticmethod
    def gen_proc_body(q, cfg, seed_gen, weight_app, path, text_level):
        util_common.timer_start(False)

        if cfg.randomize is None:
            cfg.randomize = 0
        cfg.randomize += seed_gen

        if cfg.custom_constraints is None:
            cfg.custom_constraints = []
        if PathCanvas.is_edge_path(path):
            cfg.custom_constraints.append(util_custom.OutPathConstraint(path, weight_app))
        if text_level is not None:
            cfg.custom_constraints.append(util_custom.OutTextLevelConstraint(text_level, weight_app))

        result_info = scheme2output.scheme2output(cfg)

        if result_info is not None:
            if PathCanvas.is_edge_path(path):
                data = list(path)
                result_info.extra_meta.append(util_common.meta_path('app-path', data))

            if text_level is not None:
                data = []
                for rr in range(len(text_level)):
                    for cc in range(len(text_level[rr])):
                        if text_level[rr][cc] != util_common.DEFAULT_TEXT:
                            data.append((rr, cc))
                result_info.extra_meta.append(util_common.meta_tile('app-text', data))

        encode_result_info(result_info)
        q.put(result_info)

        if result_info is not None:
            util_common.exit_solution_found()
        else:
            util_common.exit_solution_not_found()

    def on_timer(self):
        if self._gen_proc is not None:
            if not self._gen_proc.is_alive():
                if self._gen_proc_termed:
                    print('proc termed')
                elif self._gen_proc.exitcode != 0:
                    try:
                        result_info = self._gen_proc_q.get_nowait()
                        util_common.check(result_info is None, 'result error')
                        print('proc no solution')
                        self._gen_result = None
                        self._gen_image = None
                        self._gen_text = None
                        self._gen_path = None
                        self._gen_objective = None
                        self.redraw_from_image()
                    except queue.Empty:
                        print('proc error')
                else:
                    print('proc solution')

                    result_info = self._gen_proc_q.get()
                    util_common.check(result_info is not None, 'result error')
                    decode_result_info(result_info)

                    self._gen_result = result_info
                    self._gen_image = PIL.ImageTk.PhotoImage(result_info.image_level.resize((self._cols * CELL_SIZE, self._rows * CELL_SIZE), PIL.Image.Resampling.BILINEAR)) if result_info.image_level is not None else None
                    self._gen_text = result_info.text_level
                    self._gen_path = result_info.reach_info[0].path_edges if result_info.reach_info else None
                    self._gen_objective = result_info.solver_objective

                    self.redraw_from_image()
                self._gen_proc = None

        if self._gen_proc_wanted is not None:
            if self._gen_proc is not None:
                if self._gen_proc.is_alive():
                    print('terminating proc')
                    self._gen_proc_termed = True
                    self._gen_proc.terminate()

            elif time.time() >= self._gen_proc_wanted:
                self._gen_proc_wanted = None
                self._gen_proc_termed = False

                print('starting proc')

                self._gen_proc_q = multiprocessing.Manager().Queue()
                self._gen_proc = multiprocessing.Process(target=PathCanvas.gen_proc_body, args=(self._gen_proc_q, self._cfg, self._seed_gen, self._app_weight, self._path_or_point, self._text_level))
                self._gen_proc.start()

        self.redraw_from_working()
        self.after(REFRESH_MSEC, self.on_timer)

    def set_scroll_region(self, scw, sch):
        self._scrollregion = (scw, sch)
        self.config(scrollregion=(0, 0, scw, sch))

    def set_scroll_x(self, *args):
        self.xview(*args)
        self.redraw_from_working()

    def set_scroll_y(self, *args):
        self.yview(*args)
        self.redraw_from_working()

    def redraw_from_working(self):
        for draw in self._working_draw:
            self.delete(draw)
        self._working_draw = []

        if self._scrollregion is not None:
            xoff = self.xview()[0] * self._scrollregion[0]
            yoff = self.yview()[0] * self._scrollregion[1]
        else:
            xoff, yoff = 0, 0

        if self._gen_objective is not None and self._gen_objective > 0:
            self._working_draw.append(self.create_line(xoff + tocvs(0.65), yoff + tocvs(0.65), xoff + tocvs(1.35), yoff + tocvs(1.35), fill='dark orange', width=3))
            self._working_draw.append(self.create_line(xoff + tocvs(1.35), yoff + tocvs(0.65), xoff + tocvs(0.65), yoff + tocvs(1.35), fill='dark orange', width=3))

        if self._gen_proc is not None:
            self._working_draw.append(self.create_arc(xoff + tocvs(0.5), yoff + tocvs(0.5), xoff + tocvs(1.5), yoff + tocvs(1.5), outline='dark orange', width=3, style=tkinter.ARC, start=time.time() * 45.0, extent=300.0))

    def redraw_from_mouse(self):
        for draw in self._mouse_draw:
            self.delete(draw)
        self._mouse_draw = []

        if self._mouse is not None:
            mr, mc = self._mouse

            if self._path_nexts is None or self._mouse in self._path_nexts:
                self._mouse_draw.append(self.create_rectangle(tocvs(mc), tocvs(mr), tocvs(mc + 1), tocvs(mr + 1), outline='green', width=3))
            else:
                self._mouse_draw.append(self.create_rectangle(tocvs(mc), tocvs(mr), tocvs(mc + 1), tocvs(mr + 1), outline='gray', width=3))

        self.redraw_from_working()

    def redraw_from_text_level(self):
        for draw in self._text_level_draw:
            self.delete(draw)
        self._text_level_draw = []

        if self._text_level is not None:
            for rr in range(self._rows):
                for cc in range(self._cols):
                    text = self._text_level[rr][cc]
                    if text != util_common.DEFAULT_TEXT:
                        self._text_level_draw.append(self.create_rectangle(tocvs(cc), tocvs(rr), tocvs(cc + 0.5), tocvs(rr + 0.5), fill='pink', outline='purple'))
                        self._text_level_draw.append(self.create_text(tocvs(cc + 0.25), tocvs(rr + 0.25), text=text, fill='purple', font=('Courier', CELL_SIZE // 2), anchor=tkinter.CENTER))

        self.redraw_from_mouse()

    def _do_draw_path(self, path, larger, color, dash):
        if larger:
            outline_color = color
            width = 3
        else:
            outline_color = ''
            width = 2

        if PathCanvas.is_edge_path(path):
            path_unwrapped, path_orig_from, path_was_unwrapped = util_path.unwrap_edge_path(path)

            draw_lines = []
            prev_pt = None
            for (pr0, pc0, pr1, pc1) in path_unwrapped:
                if prev_pt != (pr0, pc0):
                    if prev_pt is not None:
                        draw_lines[-1].append(tocvs(prev_pt[1] + 0.5))
                        draw_lines[-1].append(tocvs(prev_pt[0] + 0.5))
                    draw_lines.append([])
                    draw_lines[-1].append(tocvs(pc0 + 0.5))
                    draw_lines[-1].append(tocvs(pr0 + 0.5))
                draw_lines[-1].append(tocvs(pc1 + 0.5))
                draw_lines[-1].append(tocvs(pr1 + 0.5))
                prev_pt = (pr1, pc1)
            for draw_line in draw_lines:
                self._path_draw.append(self.create_line(*draw_line, fill=color, width=width, dash=dash))

            for (pr0, pc0, pr1, pc1), was_unwrapped in zip(path_unwrapped, path_was_unwrapped):
                if was_unwrapped == util_path.UNWRAP_PRE:
                    continue
                pr0 += 0.5
                pc0 += 0.5
                pr1 += 0.5
                pc1 += 0.5
                dr = pr1 - pr0
                dc = pc1 - pc0
                ll = (dr ** 2 + dc ** 2) ** 0.5
                dr /= ll
                dc /= ll
                SCL = 0.3
                OFF = 0.075
                tra = pr1 - OFF * dr
                tca = pc1 - OFF * dc
                trb = (pr1 - dr * SCL - 0.5 * dc * SCL) - OFF * dr
                tcb = (pc1 - dc * SCL + 0.5 * dr * SCL) - OFF * dc
                trc = (pr1 - dr * SCL + 0.5 * dc * SCL) - OFF * dr
                tcc = (pc1 - dc * SCL - 0.5 * dr * SCL) - OFF * dc
                self._path_draw.append(self.create_polygon([tocvs(tca), tocvs(tra), tocvs(tcb), tocvs(trb), tocvs(tcc), tocvs(trc)], fill=color, outline=outline_color, width=width))

        draw_ends = []
        if PathCanvas.is_single_point_path(path):
            draw_ends.append(path)
        elif PathCanvas.is_edge_path(path):
            draw_ends.append(util_path.path_begin_point(path))
            draw_ends.append(util_path.path_end_point(path))
        for pr, pc in draw_ends:
            sz = 0.15
            self._path_draw.append(self.create_oval(tocvs(pc + (0.5 - sz)), tocvs(pr + (0.5 - sz)), tocvs(pc + (0.5 + sz)), tocvs(pr + (0.5 + sz)), fill=color, outline=outline_color, width=width))

    def redraw_from_path(self):
        for draw in self._path_draw:
            self.delete(draw)
        self._path_draw = []

        if self._draw_open_closed:
            for nr, nc in self._path_open:
                self._path_draw.append(self.create_oval(tocvs(nc + 0.25), tocvs(nr + 0.25), tocvs(nc + 0.75), tocvs(nr + 0.75), outline='blue', width=2))
            for nr, nc in self._path_closed:
                self._path_draw.append(self.create_rectangle(tocvs(nc + 0.25), tocvs(nr + 0.25), tocvs(nc + 0.75), tocvs(nr + 0.75), outline='blue', width=2))

        self._do_draw_path(self._gen_path, True, 'red', None)
        self._do_draw_path(self._path_or_point, False, 'pink', (3, 3))

        if self._path_nexts is not None:
            for nr, nc in self._path_nexts:
                self._path_draw.append(self.create_rectangle(tocvs(nc), tocvs(nr), tocvs(nc + 1), tocvs(nr + 1), outline='black', width=3))

        self.redraw_from_text_level()

    def redraw_from_grid(self):
        for draw in self._grid_draw:
            self.delete(draw)
        self._grid_draw = []

        for rr in range(self._rows + 1):
            self._grid_draw.append(self.create_line(tocvs(0), tocvs(rr), tocvs(self._cols), tocvs(rr), fill='gray'))
        for cc in range(self._cols + 1):
            self._grid_draw.append(self.create_line(tocvs(cc), tocvs(0), tocvs(cc), tocvs(self._rows), fill='gray'))

        self.redraw_from_path()

    def redraw_from_image(self):
        for draw in self._image_draw:
            self.delete(draw)
        self._image_draw = []

        if self._gen_image is None:
            self._image_draw.append(self.create_rectangle(tocvs(0), tocvs(0), tocvs(self._cols), tocvs(self._rows), outline=None, fill='white'))
            for rr in range(self._rows):
                for cc in range(self._cols):
                    tag = self._cfg.tag_level[rr][cc]
                    if tag == util_common.VOID_TEXT:
                        self._image_draw.append(self.create_rectangle(tocvs(cc), tocvs(rr), tocvs(cc + 1), tocvs(rr + 1), outline=None, fill='black'))
        else:
            self._image_draw.append(self.create_rectangle(tocvs(0), tocvs(0), tocvs(self._cols), tocvs(self._rows), outline=None, fill='black'))
            self._image_draw.append(self.create_image(INSET, INSET, anchor=tkinter.NW, image=self._gen_image))

        self.redraw_from_grid()

    def recompute_nexts(self):
        if self._game_to_move_info is None:
            return

        if self._path_or_point is None:
            self._path_nexts = None
            self._path_open = {}
            self._path_closed = {}
        else:
            if PathCanvas.is_single_point_path(self._path_or_point):
                pt = self._path_or_point
                path = []
            else:
                if self._reverse:
                    pt = util_path.path_begin_point(self._path_or_point)
                else:
                    pt = util_path.path_end_point(self._path_or_point)
                path = self._path_or_point

            self._path_nexts, self._path_open, self._path_closed = util_path.get_nexts_open_closed_from(pt, path, self._reverse, self._rows, self._cols, self._game_to_move_info, self._game_locations)

    def new_manual_path(self, delay_proc):
        self.recompute_nexts()
        self.redraw_from_path()
        self.restart_gen_proc(PATH_DELAY_SEC if delay_proc else 0.0)

    def recompute_texts(self):
        self.clear_text_level_if_needed()

    def new_manual_text_level(self, delay_proc):
        self.recompute_texts()
        if self._text_level == None:
            print('text cleared')
        else:
            util_common.print_text_level(self._text_level)
        self.redraw_from_text_level()
        self.restart_gen_proc(PATH_DELAY_SEC if delay_proc else 0.0)

    @staticmethod
    def is_empty_path(path):
        return path is None

    @staticmethod
    def is_single_point_path(path):
        return type(path) == tuple

    @staticmethod
    def is_edge_path(path):
        return type(path) == list

    def on_evt_all_tog_mode(self, event):
        if self._mode == MODE_PATHED:
            self.set_mode(MODE_TEXTED)
        else:
            self.set_mode(MODE_PATHED)

    def on_evt_all_export(self, event):
        if self.is_gen_proc_running():
            print('cannot export while proc running')
            return

        if self._gen_result is not None:
            app_state = {}
            if self._path_or_point is not None:
                app_state['path'] = self._path_or_point
            if self._text_level is not None:
                app_state['text'] = self._text_level

            outfile_base = cfg.outfile
            if not self._out_no_hash:
                outfile_base += '_' + hashlib.md5(json.dumps(app_state).encode('utf-8')).hexdigest()

            cfg_outfile = cfg.outfile
            cfg.outfile = outfile_base + ('_%04d' % self._seed_gen)
            scheme2output.scheme2output_save_result(cfg, self._gen_result)
            print('saved to', cfg.outfile)
            cfg.outfile = cfg_outfile

            print('writing app state to ' + outfile_base + '.state')
            with open(outfile_base + '.state', 'wt') as outfile:
                json.dump(app_state, outfile)
                outfile.write('\n')

    def on_evt_all_next_level(self, event):
        self._seed_gen = (self._seed_gen + 1) % LEVEL_COUNT
        self.new_manual_path(False)

    def on_evt_all_prev_level(self, event):
        self._seed_gen = (self._seed_gen + LEVEL_COUNT - 1) % LEVEL_COUNT
        self.new_manual_path(False)

    def on_evt_text_change(self, event):
        if self._mouse is None:
            return
        row, col = self._mouse

        if len(event.char) != 1 or event.char not in string.ascii_letters + string.digits + string.punctuation:
            return

        text = event.char
        tag = self._cfg.tag_level[row][col]
        game = self._cfg.game_level[row][col]

        if game not in self._cfg.scheme_info.game_to_tag_to_tiles:
            print('unrecognized game')
            return
        if tag not in self._cfg.scheme_info.game_to_tag_to_tiles[game]:
            print('unrecognized tag')
            return
        if text not in [self._cfg.scheme_info.tileset.tile_to_text[tile] for tile in self._cfg.scheme_info.game_to_tag_to_tiles[game][tag]]:
            print('unrecognized text')
            return

        self.create_text_level_if_needed()

        self._text_level[row][col] = text

        self.new_manual_text_level(True)

    def on_evt_text_copy(self, event):
        if self._mouse is None:
            return
        row, col = self._mouse

        if self._gen_text is None:
            return

        mr, mc = self._mouse
        copy_text = self._gen_text[mr][mc]

        if copy_text in [util_common.DEFAULT_TEXT, util_common.VOID_TEXT]:
            return

        self.create_text_level_if_needed()

        for rr in range(self._rows):
            for cc in range(self._cols):
                if self._gen_text[rr][cc] == copy_text and self._text_level[rr][cc] == util_common.DEFAULT_TEXT:
                    self._text_level[rr][cc] = copy_text

        self.new_manual_text_level(False)

    def on_evt_text_del(self, event):
        if self._mouse is None:
            return
        row, col = self._mouse

        if self._text_level is None:
            return

        if self._text_level[row][col] == util_common.DEFAULT_TEXT:
            return

        self._text_level[row][col] = util_common.DEFAULT_TEXT

        self.new_manual_text_level(True)

    def on_evt_text_del_same_after(self, event):
        if self._mouse is None:
            return
        row, col = self._mouse

        if self._text_level is None:
            return

        del_text = self._text_level[row][col]
        if del_text == util_common.DEFAULT_TEXT:
            return

        for rr in range(row, self._rows):
            for cc in range(self._cols):
                if self._text_level[rr][cc] == del_text:
                    self._text_level[rr][cc] = util_common.DEFAULT_TEXT

        self.new_manual_text_level(True)

    def on_evt_text_clear(self, event):
        if self._text_level is None:
            return

        self._text_level = None

        self.new_manual_text_level(True)

    def on_evt_path_del_end(self, event):
        if self._game_to_move_info is None:
            return

        if PathCanvas.is_single_point_path(self._path_or_point):
            self._path_or_point = None
            self.new_manual_path(True)
        elif PathCanvas.is_edge_path(self._path_or_point):
            if len(self._path_or_point) == 1:
                self._path_or_point = util_path.path_begin_point(self._path_or_point)
            else:
                self._path_or_point = self._path_or_point[:-1]
            self.new_manual_path(True)

    def on_evt_path_del_begin(self, event):
        if self._game_to_move_info is None:
            return

        if PathCanvas.is_single_point_path(self._path_or_point):
            self._path_or_point = None
            self.new_manual_path(True)
        elif PathCanvas.is_edge_path(self._path_or_point):
            if len(self._path_or_point) == 1:
                self._path_or_point = util_path.path_end_point(self._path_or_point)
            else:
                self._path_or_point = self._path_or_point[1:]
            self.new_manual_path(True)

    def on_evt_path_clear(self, event):
        if self._game_to_move_info is None:
            return

        self._path_or_point = None
        self.new_manual_path(True)

    def on_evt_path_tog_begend(self, event):
        if self._game_to_move_info is None:
            return

        self._reverse = not self._reverse
        self.recompute_nexts()
        self.redraw_from_path()

    def on_evt_path_copy(self, event):
        if self._game_to_move_info is None:
            return

        self._path_or_point = self._gen_path
        self.new_manual_path(True)

    def on_evt_path_tog_opcl(self, event):
        if self._game_to_move_info is None:
            return

        self._draw_open_closed = not self._draw_open_closed
        self.redraw_from_path()

    def on_evt_path_random(self, event):
        if self._game_to_move_info is None:
            return

        self._seed_rand_path += 1
        rng = random.Random(self._seed_rand_path)
        self._path_or_point, reachable = util_path.random_path_by_search(rng, self._rows, self._cols, self._game_to_move_info, self._game_locations)
        self.new_manual_path(False)

    def on_evt_path_shortest_drawn(self, event):
        if self._game_to_move_info is None:
            return

        if PathCanvas.is_edge_path(self._path_or_point):
            begin = util_path.path_begin_point(self._path_or_point)
            end = util_path.path_end_point(self._path_or_point)
            self._path_or_point, reachable = util_path.shortest_path_between(begin, end, self._rows, self._cols, self._game_to_move_info, self._game_locations, None, None)
            self.new_manual_path(False)

    def on_evt_path_shortest_gen(self, event):
        if self._game_to_move_info is None:
            return

        if PathCanvas.is_edge_path(self._gen_path):
            begin = util_path.path_begin_point(self._gen_path)
            end = util_path.path_end_point(self._gen_path)
            open_locations, closed_locations = util_path.get_level_open_closed(self._gen_text, util_common.OPEN_TEXT, util_common.START_TEXT, util_common.GOAL_TEXT)
            self._path_or_point, reachable = util_path.shortest_path_between(begin, end, self._rows, self._cols, self._game_to_move_info, self._game_locations, open_locations, closed_locations)
            self.new_manual_path(False)

    def on_mouse_motion(self, event):
        mouse_prev = self._mouse

        mr, mc = math.floor(fromcvs(self.canvasy(event.y))), math.floor(fromcvs(self.canvasx(event.x)))
        if 0 <= mr and mr < self._rows and 0 <= mc and mc < self._cols:
            self._mouse = (mr, mc)
        else:
            self._mouse = None

        if self._mouse != mouse_prev:
            if self._mouse is not None and self._mouse_text_copy is not None:
                self._text_level[mr][mc] = self._mouse_text_copy
                self.redraw_from_text_level()
            else:
                self.redraw_from_mouse()

    def on_mouse_leave(self, event):
        self._mouse = None
        self.redraw_from_mouse()

    def on_mouse_down(self, event):
        if self._mouse is None:
            return

        if self._mode == MODE_PATHED:
            if self._game_to_move_info is None:
                return

            if self._path_nexts is None or self._mouse in self._path_nexts:
                pt = self._mouse
                if PathCanvas.is_empty_path(self._path_or_point):
                    self._path_or_point = pt
                else:
                    if self._reverse:
                        if PathCanvas.is_single_point_path(self._path_or_point):
                            pt_begin = self._path_or_point
                            self._path_or_point = []
                        else:
                            pt_begin = util_path.path_begin_point(self._path_or_point)
                        self._path_or_point.insert(0, self._path_nexts[self._mouse][0])
                    else:
                        if PathCanvas.is_single_point_path(self._path_or_point):
                            pt_end = self._path_or_point
                            self._path_or_point = []
                        else:
                            pt_end = util_path.path_end_point(self._path_or_point)
                        self._path_or_point.append(self._path_nexts[self._mouse][0])
                self.new_manual_path(True)

        elif self._mode == MODE_TEXTED:
            if self._text_level is not None:
                mr, mc = self._mouse
                self._mouse_text_copy = self._text_level[mr][mc]

    def on_mouse_up(self, event):
        if self._mode == MODE_TEXTED:
            self._mouse_text_copy = None
            self.new_manual_text_level(True)



def app_editor(cfg, mode, out_no_hash, app_state, app_weight):
    if mode is None:
        if cfg.reach_connect_setups is None:
            mode = MODE_TEXTED
        else:
            mode = MODE_PATHED

    canvas_width  = cfg.cols * CELL_SIZE + 2 * INSET
    canvas_height = cfg.rows * CELL_SIZE + 2 * INSET

    width = min(canvas_width, MAX_SIZE)
    height = min(canvas_height, MAX_SIZE)

    root = tkinter.Tk()

    frame = tkinter.Frame(root, width=width, height=width)
    frame.pack(expand=True, fill=tkinter.BOTH)

    canvas = PathCanvas(frame, cfg, mode, out_no_hash, app_state, app_weight)
    scroll = False

    if width < canvas_width:
        hbar = tkinter.Scrollbar(frame, orient=tkinter.HORIZONTAL)
        hbar.pack(side=tkinter.BOTTOM, fill=tkinter.X)
        hbar.config(command=canvas.set_scroll_x)
        canvas.config(xscrollcommand=hbar.set)
        scroll = True

    if height < canvas_height:
        vbar = tkinter.Scrollbar(frame, orient=tkinter.VERTICAL)
        vbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        vbar.config(command=canvas.set_scroll_y)
        canvas.config(yscrollcommand=vbar.set)
        scroll = True

    if scroll:
        canvas.set_scroll_region(canvas_width, canvas_height)

    canvas.config(width=width, height=height)
    canvas.pack(side=tkinter.LEFT, expand=True, fill=tkinter.BOTH)
    canvas.xview_moveto(0.0)
    canvas.yview_moveto(0.0)

    if mode == MODE_TEST:
        canvas.on_evt_path_random(None)
        canvas.restart_gen_proc(-1.0)
        canvas.on_timer()
        while canvas.is_gen_proc_running():
            time.sleep(REFRESH_MSEC / 1000)
            canvas.on_timer()
        canvas.on_evt_all_export(None)
        util_common.print_text_level(canvas.get_gen_text_level())
    else:
        root.mainloop()



if __name__ == '__main__':
    util_common.print_command()

    mode = None
    app_state = None
    app_weight = WEIGHT_APP

    argv = sys.argv[1:]

    if '--app' in argv:
        app_ind = argv.index('--app')
        app_argv = argv[app_ind + 1:]
        del argv[app_ind:]

        parser = argparse.ArgumentParser(description='App-specific arguments.')
        group = parser.add_mutually_exclusive_group()
        group.add_argument('--pathed', action='store_true', help='Set mode.')
        group.add_argument('--texted', action='store_true', help='Set mode.')
        group.add_argument('--test', action='store_true', help='Set mode.')
        parser.add_argument('--out-no-hash', action='store_true', help='Do not append state has to outfile name.')
        parser.add_argument('--statefile', type=str, help='Input state file.')
        parser.add_argument('--app-hard', action='store_true', help='Use hard app constraints.')
        args = parser.parse_args(app_argv)

        if args.pathed:
            mode = MODE_PATHED
        elif args.texted:
            mode = MODE_TEXTED
        elif args.test:
            mode = MODE_TEST

        if args.statefile is not None:
            with open(args.statefile, 'rt') as f:
                app_state = json.load(f)

        if args.app_hard:
            app_weight = None

    cfg = scheme2output.scheme2output_argv2cfg(argv)

    app_editor(cfg, mode, args.out_no_hash, app_state, app_weight)
