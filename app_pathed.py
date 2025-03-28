import argparse, hashlib, io, math, multiprocessing, os, pickle, random, sys, time
import scheme2output, util_common, util_custom, util_path, util_reach, util_solvers
import PIL.Image, PIL.ImageTk
import tkinter

WEIGHT_PATH    =  100
WEIGHT_PATTERN = None
WEIGHT_COUNTS  =    1

INSET          =   10
CELL_SIZE      =   25
FRAME          =    5

LEVEL_COUNT    =  128

REFRESH_MSEC   =   50
PATH_DELAY_SEC =    1.0

def tocvs(x):
    return (x * CELL_SIZE) + INSET

def fromcvs(x):
    return (x - INSET) / CELL_SIZE

def encode_result_info(result_info, want_image):
    if result_info is None:
        return None

    if not want_image:
        result_info.image_level = None
    elif result_info.image_level is not None:
        result_info.image_level = util_common.image_to_bytes(result_info.image_level.convert('RGB'))

    return result_info

def decode_result_info(result_info):
    if result_info is None:
        return None

    if result_info.image_level is not None:
        result_info.image_level = util_common.image_from_bytes(result_info.image_level)

    return result_info

class PathCanvas(tkinter.Canvas):
    def __init__(self, root, rows, cols, reach_move, reach_missing_aux_closed, reach_wrap_rows, reach_wrap_cols, schemefile, outfolder):
        super().__init__(root, width=cols*CELL_SIZE+2*INSET-FRAME, height=rows*CELL_SIZE+2*INSET-FRAME)

        self._rows = rows
        self._cols = cols

        self._seed_gen = 0
        self._seed_rand_path = 0
        self._reverse = False

        self._reach_move = reach_move
        self._reach_missing_aux_closed = reach_missing_aux_closed
        self._reach_wrap_rows = reach_wrap_rows
        self._reach_wrap_cols = reach_wrap_cols

        self._game_locations = { (rr, cc): util_common.DEFAULT_TEXT for rr in range(self._rows) for cc in range(self._cols) }
        self._game_to_move_info = { util_common.DEFAULT_TEXT: util_reach.get_move_info(self._reach_move, self._reach_missing_aux_closed, self._reach_wrap_rows, self._reach_wrap_cols) }

        self._schemefile = schemefile
        self._outfolder = outfolder

        self._path_nexts = None
        self._path_open = {}
        self._path_closed = {}

        self._working_draw = []
        self._gen_objective = None

        self._mouse = None
        self._draw_open_closed = False
        self._mouse_draw = []

        self._path_or_point = None
        self._gen_path = None
        self._path_draw = []

        self._grid_draw = []

        self._gen_image = None
        self._gen_text = None
        self._image_draw = []

        self._gen_proc = None
        self._gen_proc_wanted = None
        self._gen_proc_termed = False
        self._gen_proc_q = None

        self.bind_all("<BackSpace>", self.on_key_backspace) # delete from end
        self.bind_all("<KeyPress-=>", self.on_key_equal)    # delete from beginning
        self.bind_all("<KeyPress-c>", self.on_key_c)        # copy generated path
        self.bind_all("<KeyPress-x>", self.on_key_x)        # clear path
        self.bind_all("<KeyPress-p>", self.on_key_p)        # toggle add to beginning/end
        self.bind_all("<KeyPress-n>", self.on_key_n)        # next generated level
        self.bind_all("<KeyPress-b>", self.on_key_b)        # previous generated level
        self.bind_all("<KeyPress-o>", self.on_key_o)        # toggle show open/closed tiles
        self.bind_all("<KeyPress-r>", self.on_key_r)        # random path
        self.bind_all("<KeyPress-s>", self.on_key_s)        # shortest path between drawn beginning/end
        self.bind_all("<KeyPress-w>", self.on_key_w)        # shortest path between generated beginning/end in level
        self.bind("<Motion>", self.on_mouse_motion)
        self.bind("<Leave>", self.on_mouse_leave)
        self.bind("<ButtonPress-1>", self.on_mouse_button)
        self.after(REFRESH_MSEC, self.on_timer)

        self.pack()

        self.redraw_from_image()

    def restart_gen_proc(self, delay):
        if self._schemefile:
            self._gen_proc_wanted = time.time() + delay

    @staticmethod
    def gen_proc_body(q, rows, cols, seed, start_goal, path, reach_move, reach_wrap_rows, reach_wrap_cols, schemefile, want_image, outfile):
        util_common.timer_start(False)

        if outfile is not None:
            outfile_file = util_common.openz(outfile + '.log', 'wt')
            sys.stdout = outfile_file

        with util_common.openz(schemefile, 'rb') as f:
            scheme_info = pickle.load(f)

        tag_game_level = util_common.make_grid(rows, cols, util_common.DEFAULT_TEXT)
        solver = util_solvers.PySatSolverRC2()

        reach_start_setup = util_common.ReachJunctionSetup()
        reach_start_setup.text = util_common.START_TEXT
        reach_start_setup.loc = util_reach.RPLOC_ALL
        reach_start_setup.loc_params = []

        reach_goal_setup = util_common.ReachJunctionSetup()
        reach_goal_setup.text = util_common.GOAL_TEXT
        reach_goal_setup.loc = util_reach.RPLOC_ALL
        reach_goal_setup.loc_params = []

        reach_connect_setup = util_common.ReachConnectSetup()
        reach_connect_setup.src = util_common.START_TEXT
        reach_connect_setup.dst = util_common.GOAL_TEXT
        reach_connect_setup.unreachable = False
        reach_connect_setup.game_to_reach_move = { util_common.DEFAULT_TEXT: reach_move }
        reach_connect_setup.wrap_rows = reach_wrap_rows
        reach_connect_setup.wrap_cols = reach_wrap_cols
        reach_connect_setup.open_text = util_common.OPEN_TEXT

        custom_cnstrs = []
        if start_goal is not None:
            custom_cnstrs.append(util_custom.OutPathEndsConstraint(start_goal[0], start_goal[1], start_goal[2], start_goal[3], WEIGHT_PATH))
        if path is not None:
            custom_cnstrs.append(util_custom.OutPathConstraint(path, WEIGHT_PATH))

        if scheme_info.pattern_info is not None:
            pattern_weight = WEIGHT_PATTERN
        else:
            pattern_weight = 0

        if scheme_info.count_info is not None:
            count_weight = WEIGHT_COUNTS
            count_scale = scheme2output.COUNTS_SCALE_HALF
        else:
            count_weight = 0
            count_scale = None

        result_info = scheme2output.scheme2output(scheme_info, tag_game_level, tag_game_level, solver, seed, pattern_weight, count_weight, count_scale, [reach_start_setup, reach_goal_setup], [reach_connect_setup], None, custom_cnstrs, False)

        if outfile is not None and result_info is not None:
            print('saving to', outfile)
            util_common.save_result_info(result_info, outfile)

        encode_result_info(result_info, want_image)
        q.put(result_info)

        if result_info:
            util_common.exit_solution_found()
        else:
            util_common.exit_solution_not_found()

    def on_timer(self):
        if self._gen_proc is not None:
            if not self._gen_proc.is_alive():
                if self._gen_proc_termed:
                    print('proc termed')
                elif self._gen_proc.exitcode != 0:
                    print('proc error')
                else:
                    print('proc done')

                    result_info = self._gen_proc_q.get()
                    decode_result_info(result_info)

                    if result_info is not None:
                        if result_info.image_level is None:
                            self._gen_image = None
                        else:
                            self._gen_image = PIL.ImageTk.PhotoImage(result_info.image_level.resize((self._cols * CELL_SIZE, self._rows * CELL_SIZE), PIL.Image.Resampling.BILINEAR))
                        self._gen_text = result_info.text_level
                        self._gen_path = result_info.reach_info[0].path_edges
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

                if PathCanvas.is_edge_path(self._path_or_point):
                    print('starting proc')

                    if self._outfolder is None:
                        outfile = None
                    else:
                        outfile = os.path.join(self._outfolder, hashlib.md5(str(self._path_or_point).encode('utf-8')).hexdigest() + ('_%04d' % self._seed_gen))

                    self._gen_proc_q = multiprocessing.Queue()
                    self._gen_proc = multiprocessing.Process(target=PathCanvas.gen_proc_body, args=(self._gen_proc_q, self._rows, self._cols, self._seed_gen, None, self._path_or_point, self._reach_move, self._reach_wrap_rows, self._reach_wrap_cols, self._schemefile, True, outfile))
                    self._gen_proc.start()
                else:
                    print('empty path')
                    self._gen_image = None
                    self._gen_text = None
                    self._gen_path = None
                    self._gen_objective = None
                    self.redraw_from_image()

        self.redraw_from_working()
        self.after(REFRESH_MSEC, self.on_timer)

    def redraw_from_working(self):
        for draw in self._working_draw:
            self.delete(draw)
        self._working_draw = []

        if self._gen_path != self._path_or_point:
            self._working_draw.append(self.create_line(tocvs(0.65), tocvs(0.65), tocvs(1.35), tocvs(1.35), fill='purple', width=3))
            self._working_draw.append(self.create_line(tocvs(1.35), tocvs(0.65), tocvs(0.65), tocvs(1.35), fill='purple', width=3))

        if self._gen_proc is not None:
            self._working_draw.append(self.create_arc(tocvs(0.5), tocvs(0.5), tocvs(1.5), tocvs(1.5), outline='purple', width=3, style=tkinter.ARC, start=time.time() * 45.0, extent=300.0))

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

        self.redraw_from_mouse()

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
        else:
            self._image_draw.append(self.create_image(INSET, INSET, anchor=tkinter.NW, image=self._gen_image))

        self.redraw_from_grid()

    def recompute_nexts(self):
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
        self.redraw_from_path()

    def new_manual_path(self, delay_proc):
        self.recompute_nexts()
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

    def on_key_backspace(self, event):
        if PathCanvas.is_single_point_path(self._path_or_point):
            self._path_or_point = None
            self.new_manual_path(True)
        elif PathCanvas.is_edge_path(self._path_or_point):
            if len(self._path_or_point) == 1:
                self._path_or_point = tuple(self._path_or_point[0][0:2])
            else:
                self._path_or_point = self._path_or_point[:-1]
            self.new_manual_path(True)

    def on_key_equal(self, event):
        if PathCanvas.is_single_point_path(self._path_or_point):
            self._path_or_point = None
            self.new_manual_path(True)
        elif PathCanvas.is_edge_path(self._path_or_point):
            if len(self._path_or_point) == 1:
                self._path_or_point = tuple(self._path_or_point[0][2:4])
            else:
                self._path_or_point = self._path_or_point[1:]
            self.new_manual_path(True)

    def on_key_x(self, event):
        if self._schemefile:
            self._path_or_point = None
            self.new_manual_path(True)

    def on_key_p(self, event):
        self._reverse = not self._reverse
        self.recompute_nexts()

    def on_key_c(self, event):
        if self._schemefile:
            self._path_or_point = self._gen_path
            self.new_manual_path(True)

    def on_key_b(self, event):
        self._seed_gen = (self._seed_gen + LEVEL_COUNT - 1) % LEVEL_COUNT
        self.new_manual_path(False)

    def on_key_n(self, event):
        self._seed_gen = (self._seed_gen + 1) % LEVEL_COUNT
        self.new_manual_path(False)

    def on_key_o(self, event):
        self._draw_open_closed = not self._draw_open_closed
        self.redraw_from_path()

    def on_key_r(self, event):
        self._seed_rand_path += 1
        rng = random.Random(self._seed_rand_path)
        self._path_or_point, reachable = util_path.random_path_by_search(rng, self._rows, self._cols, self._game_to_move_info, self._game_locations)
        self.new_manual_path(False)

    def on_key_s(self, event):
        if PathCanvas.is_edge_path(self._path_or_point):
            begin = util_path.path_begin_point(self._path_or_point)
            end = util_path.path_end_point(self._path_or_point)
            self._path_or_point, reachable = util_path.shortest_path_between(begin, end, self._rows, self._cols, self._game_to_move_info, self._game_locations, None, None)
            self.new_manual_path(False)

    def on_key_w(self, event):
        if PathCanvas.is_edge_path(self._gen_path):
            begin = util_path.path_begin_point(self._gen_path)
            end = util_path.path_end_point(self._gen_path)
            open_locations, closed_locations = util_path.get_level_open_closed(self._gen_text, util_common.OPEN_TEXT, util_common.START_TEXT, util_common.GOAL_TEXT)
            self._path_or_point, reachable = util_path.shortest_path_between(begin, end, self._rows, self._cols, self._game_to_move_info, self._game_locations, open_locations, closed_locations)
            self.new_manual_path(False)

    def on_mouse_motion(self, event):
        mr, mc = math.floor(fromcvs(event.y)), math.floor(fromcvs(event.x))
        if 0 <= mr and mr < self._rows and 0 <= mc and mc < self._cols:
            self._mouse = (mr, mc)
        else:
            self._mouse = None
        self.redraw_from_mouse()

    def on_mouse_leave(self, event):
        self._mouse = None
        self.redraw_from_mouse()

    def on_mouse_button(self, event):
        if self._mouse is not None:
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



def pathed(rows, cols, reach_move, reach_missing_aux_closed, reach_wrap_rows, reach_wrap_cols, schemefile, outfolder):
    root = tkinter.Tk()
    root.title('pathed')

    PathCanvas(root, rows, cols, reach_move, reach_missing_aux_closed, reach_wrap_rows, reach_wrap_cols, schemefile, outfolder)

    root.mainloop()



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Path editor.')

    parser.add_argument('--size', required=True, type=int, nargs=2, help='Level size.')
    parser.add_argument('--reach-move', required=True, type=str, help='Use reachability move rules, from: ' + ','.join(util_reach.RMOVE_LIST) + '.')
    parser.add_argument('--reach-missing-aux-closed', action='store_true', help='Treat missing locations as aux closed.')
    parser.add_argument('--reach-wrap-rows', action='store_true', help='Wrap rows in reachability.')
    parser.add_argument('--reach-wrap-cols', action='store_true', help='Wrap columns in reachability.')
    parser.add_argument('--schemefile', type=str, help='Input scheme file.')
    parser.add_argument('--outfolder', type=str, help='Output folder.')

    args = parser.parse_args()

    pathed(args.size[0], args.size[1], args.reach_move, args.reach_missing_aux_closed, args.reach_wrap_rows, args.reach_wrap_cols, args.schemefile, args.outfolder)
