import math
import util_common



COLOR_BACK    = (128, 128, 128)
COLOR_CELL    = (204, 204, 204)
COLOR_TEXT    = (  0,   0,   0)
COLOR_VOID    = ( 96,  32,  32)

COLOR_OUTLINE = (  0,   0,   0)
ALPHA_OUTLINE = 64



class ExploreInfo:
    def __init__(self):
        self.rows = None
        self.cols = None

        self.tileset = None

        self.ntind = None
        self.neind = None
        self.npind = None

        self.void_tind = None

        self.tind_to_text = None
        self.tind_to_image = None
        self.tinds_to_tiles = None
        self.eind_to_edge = None
        self.pind_to_prop = None

        self.level_data = None



def get_text_fg_bg_color(text, text_colors):
    if text_colors is not None and text in text_colors:
        fg_color = tuple(text_colors[text])
    else:
        fg_color = (0, 0, 0)
    bg_color = tuple([int(val / 255 * 25 + 230) for val in fg_color])
    return fg_color, bg_color

def get_text_fg_bg_color_normal(text, text_colors):
    return [util_common.color_to_normal(color) for color in get_text_fg_bg_color(text, text_colors)]

def get_text_fg_bg_color_hex(text, text_colors):
    return [util_common.color_to_hex(color) for color in get_text_fg_bg_color(text, text_colors)]

def get_void_poly(xx, yy, ww, hh, flip, snap):
    if snap:
        fl = math.floor
        ce = math.ceil
    else:
        fl = lambda x:x
        ce = lambda x:x
    if flip:
        return [(fl(xx + 0.0 * ww), ce(yy + 1.0 * hh)),
                (ce(xx + 0.1 * ww), ce(yy + 1.0 * hh)),
                (ce(xx + 1.0 * ww), ce(yy + 0.1 * hh)),
                (ce(xx + 1.0 * ww), fl(yy + 0.0 * hh)),
                (fl(xx + 0.9 * ww), fl(yy + 0.0 * hh)),
                (fl(xx + 0.0 * ww), fl(yy + 0.9 * hh)),
                (fl(xx + 0.0 * ww), ce(yy + 1.0 * hh)),
                (fl(xx + 0.0 * ww), ce(yy + 1.0 * hh))]
    else:
        return [(fl(xx + 0.0 * ww), fl(yy + 0.0 * hh)),
                (ce(xx + 0.1 * ww), fl(yy + 0.0 * hh)),
                (ce(xx + 1.0 * ww), fl(yy + 0.9 * hh)),
                (ce(xx + 1.0 * ww), ce(yy + 1.0 * hh)),
                (fl(xx + 0.9 * ww), ce(yy + 1.0 * hh)),
                (fl(xx + 0.0 * ww), ce(yy + 0.1 * hh)),
                (fl(xx + 0.0 * ww), fl(yy + 0.0 * hh)),
                (fl(xx + 0.0 * ww), fl(yy + 0.0 * hh))]
