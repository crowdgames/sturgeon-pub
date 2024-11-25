import argparse, json, math, io, os, pickle, sys, time
import util_common, util_explore, util_path
import numpy as np
import reportlab.lib.units
import reportlab.lib.utils
import reportlab.pdfgen.canvas
import squarify



CELL_SIZE_DEF   = 64

CELL_PAD        =  1
OUTLINE_WIDTH   =  1

LAYOUT_SQUARE         = 'square'
LAYOUT_TREE           = 'tree'
LAYOUT_TREE_ONE       = 'tree-one'
LAYOUT_TREE_SQRT      = 'tree-sqrt'
LAYOUT_TREE_LOG2PLUS1 = 'tree-log2plus1'
LAYOUT_LIST           = [LAYOUT_SQUARE, LAYOUT_TREE, LAYOUT_TREE_ONE, LAYOUT_TREE_SQRT, LAYOUT_TREE_LOG2PLUS1]

COLOR_BACK    = util_common.color_to_normal(util_explore.COLOR_BACK)
COLOR_CELL    = util_common.color_to_normal(util_explore.COLOR_CELL)
COLOR_TEXT    = util_common.color_to_normal(util_explore.COLOR_TEXT)
COLOR_OUTLINE = util_common.color_to_normal(util_explore.COLOR_OUTLINE)
ALPHA_OUTLINE = util_explore.ALPHA_OUTLINE / 255



def explore2pdf(explorer_info, cell_size, layout, text_colors, use_text, use_image):
    width = CELL_PAD + explorer_info.cols * (CELL_PAD + cell_size)
    height = CELL_PAD + explorer_info.rows * (CELL_PAD + cell_size)

    all_bytes = np.unpackbits(explorer_info.level_data, axis=1)
    tind_bytes = np.split(all_bytes, [explorer_info.rows * explorer_info.cols * explorer_info.ntind, len(all_bytes[0])], axis=1)[0]
    tind_sum = np.sum(tind_bytes, axis=0)
    tind_count = tind_sum.reshape((explorer_info.rows, explorer_info.cols, explorer_info.ntind))

    if layout == LAYOUT_SQUARE:
        loc_fn = None
    elif layout == LAYOUT_TREE:
        loc_fn = lambda _c: _c
    elif layout == LAYOUT_TREE_ONE:
        loc_fn = lambda _c: 1
    elif layout == LAYOUT_TREE_SQRT:
        loc_fn = lambda _c: math.sqrt(_c)
    elif layout == LAYOUT_TREE_LOG2PLUS1:
        loc_fn = lambda _c: math.log(_c, 2) + 1
    else:
        util_common.check(False, 'unknown layout ' + layout)

    if use_text and use_image:
        util_common.check(False, 'cannot use both text and image')
    elif use_text:
        util_common.check(len(explorer_info.tind_to_text) > 0, 'explorer_info has no text')
        tind_to_data = list(explorer_info.tind_to_text.items())
    elif use_image:
        util_common.check(len(explorer_info.tind_to_image) > 0, 'explorer_info has no images')
        tind_to_data = list(explorer_info.tind_to_image.items())
    else:
        util_common.check(False, 'must use one of text or image')

    if explorer_info.void_tind is not None:
        tind_to_data.append((explorer_info.void_tind, None))

    unit = 0.1 * reportlab.lib.units.mm

    pdf_buffer = io.BytesIO()
    cvs = reportlab.pdfgen.canvas.Canvas(pdf_buffer, pagesize=(width * unit, height * unit))
    cvs.scale(unit, unit)
    cvs.setFont('Courier', 0.9 * cell_size)
    cvs.setFillColorRGB(*COLOR_BACK, 1.0)
    cvs.rect(0, 0, width, height, fill=1, stroke=0)

    void_poly = util_explore.get_void_poly(0.0, 0.0, cell_size, cell_size, False, False)
    void_path = cvs.beginPath()
    for ii, (xx, yy) in enumerate(void_poly):
        if ii == 0:
            void_path.moveTo(xx, yy)
        else:
            void_path.lineTo(xx, yy)

    tind_to_pdfimage = {}
    if use_image:
        for tind, image in tind_to_data:
            if image is not None:
                tind_to_pdfimage[tind] = reportlab.lib.utils.ImageReader(util_common.image_to_bytes_io(image))

    for rr in range(explorer_info.rows):
        for cc in range(explorer_info.cols):
            cx = CELL_PAD + cc * (CELL_PAD + cell_size)
            cy = height - cell_size - (CELL_PAD + rr * (CELL_PAD + cell_size))

            loc_tinds = []
            for tind, data in tind_to_data:
                count = tind_count[(rr, cc, tind)]
                if count > 0:
                    loc_tinds.append((count, tind, data))

            if layout == LAYOUT_SQUARE:
                def parts(_p, _n):
                    _off, _sz, _acc = [], [], 0
                    for _ii in range(_p - 1):
                        _off.append(_acc)
                        _sz.append(_n // _p)
                        _acc += _n // _p
                    _off.append(_acc)
                    _sz.append(_n - _acc)
                    return _off, _sz

                sqrt = math.ceil(math.sqrt(len(loc_tinds)))
                offs, szs = parts(sqrt, cell_size)
                rects = []
                for ind, (count, tind, data) in enumerate(loc_tinds):
                    xind = ind % sqrt
                    yind = ind // sqrt
                    ox = offs[xind]
                    oy = offs[yind]
                    szx = szs[xind]
                    szy = szs[yind]
                    rects.append((ox, oy, szx, szy))

            else:
                loc_tinds = list(reversed(sorted(loc_tinds)))
                loc_counts = [loc_fn(elem[0]) for elem in loc_tinds]
                sq_values = squarify.normalize_sizes(loc_counts, cell_size, cell_size)
                sq_rects = squarify.squarify(sq_values, 0, 0, cell_size, cell_size)
                rects = []
                for sq_rect in sq_rects:
                    rects.append((sq_rect['x'], sq_rect['y'], sq_rect['dx'], sq_rect['dy']))

            cvs.saveState()
            cvs.translate(cx, cy)
            cvs.setFillColorRGB(*COLOR_CELL, 1.0)
            cvs.rect(0, 0, cell_size, cell_size, fill=1, stroke=0)

            for (ox, oy, ow, oh), (count, tind, data) in zip(rects, loc_tinds):
                oy = cell_size - oy - oh

                cvs.saveState()
                cvs.translate(ox, oy)
                cvs.scale(ow / cell_size, oh / cell_size)

                if data is None:
                    fg_color, bg_color = util_explore.get_text_fg_bg_color_normal(None, {None:util_explore.COLOR_VOID})
                    cvs.setFillColorRGB(*bg_color, 1.0)
                    cvs.rect(0, 0, cell_size, cell_size, fill=1, stroke=0)
                    cvs.setFillColorRGB(*fg_color, 1.0)
                    cvs.drawPath(void_path, fill=1, stroke=0)
                elif use_text:
                    fg_color, bg_color = util_explore.get_text_fg_bg_color_normal(data, text_colors)
                    cvs.setFillColorRGB(*bg_color, 1.0)
                    cvs.rect(0, 0, cell_size, cell_size, fill=1, stroke=0)
                    cvs.setFillColorRGB(*fg_color, 1.0)
                    cvs.drawCentredString(0.5 * cell_size, 0.25 * cell_size, data)
                else:
                    cvs.drawImage(tind_to_pdfimage[tind], 0, 0, cell_size, cell_size)

                cvs.restoreState()

                if ow <= OUTLINE_WIDTH or oh <= OUTLINE_WIDTH:
                    cvs.setFillColorRGB(*COLOR_OUTLINE, ALPHA_OUTLINE)
                    cvs.rect(ox, oy, ow, oh, fill=1, stroke=0)
                else:
                    cvs.setLineWidth(OUTLINE_WIDTH)
                    cvs.setStrokeColorRGB(*COLOR_OUTLINE, ALPHA_OUTLINE)
                    cvs.rect(ox + OUTLINE_WIDTH / 2, oy + OUTLINE_WIDTH / 2, ow - OUTLINE_WIDTH, oh - OUTLINE_WIDTH, fill=0, stroke=1)

            cvs.restoreState()

    cvs.showPage()
    cvs.save()

    return pdf_buffer.getvalue()



if __name__ == '__main__':
    util_common.timer_start()

    parser = argparse.ArgumentParser(description='Make image from explore file.')

    parser.add_argument('--outfile', required=True, type=str, help='Output image file.')
    parser.add_argument('--explorefile', required=True, type=str, help='Explore file to run, or write to.')
    parser.add_argument('--cell-size', type=int, help='Size of cells.', default=CELL_SIZE_DEF)
    parser.add_argument('--layout', type=str, default=LAYOUT_TREE, help='Layout approach, from: ' + ','.join(LAYOUT_LIST) + '.')
    parser.add_argument('--cfgfile', type=str, help='Config file.')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--text', action='store_true', help='Use tile text.')
    group.add_argument('--image', action='store_true', help='Use tile image.')

    args = parser.parse_args()

    print('loading...')
    start_time = time.time()

    text_colors = None
    if args.cfgfile is not None:
        text_colors = util_common.load_color_cfg(args.cfgfile)

    with util_common.openz(args.explorefile, 'rb') as f:
        explore_info = pickle.load(f)

    msg = 'loaded %d levels' % len(explore_info.level_data)
    if not util_common.mute_time():
        msg += (' in %0.3f' % (time.time() - start_time))
    print(msg)

    pdf = explore2pdf(explore_info, args.cell_size, args.layout, text_colors, args.text, args.image)
    with util_common.openz(args.outfile, 'wb') as f:
        f.write(pdf)
