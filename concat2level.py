import argparse, json, math, os
import util_common, util_path, util_reach



def concat2level(text_level):
    ret_levels = []

    curr_level = []
    for row in text_level:
        if row.count(util_common.VOID_TEXT) == len(row):
            if len(curr_level) > 0:
                ret_levels.append(curr_level)
                curr_level = []
        else:
            curr_level.append(row)

    if len(curr_level) > 0:
        ret_levels.append(curr_level)
        curr_level = []

    return ret_levels

def slice_cols(text_levels, pad_r=1, pad_c=1):
    if not text_levels:
        return []

    processed_levels = []
    pad_c_arr = [util_common.VOID_TEXT] * pad_c

    for level in text_levels:
        new_level = []
        for row in level:
            new_row = []
            for i, char in enumerate(row):
                new_row.append(char)
                if i < len(row) - 1:
                    new_row.extend(pad_c_arr)
            new_level.append(new_row)
        processed_levels.append(new_level)

    # stack vertically
    max_width = 0
    for level in processed_levels:
        for row in level:
            if len(row) > max_width:
                max_width = len(row)

    final_sliced_level = []
    padding_row = [util_common.VOID_TEXT] * max_width
    for i, level in enumerate(processed_levels):
        for row in level:
            padded_row = row + [util_common.VOID_TEXT] * (max_width - len(row))
            final_sliced_level.append(padded_row)

        if i < len(processed_levels) - 1 and pad_r > 0:
            for _ in range(pad_r):
                final_sliced_level.append(padding_row)

    return final_sliced_level

def unslice_cols(sliced_level, pad_c=1):
    levels_to_unslice = concat2level(sliced_level)

    unsliced_levels = []

    for level in levels_to_unslice:
        new_level = []
        for row in level:
            # taking one character, skipping 'pad_c' characters
            new_row = row[::(1 + pad_c)]
            new_level.append(new_row)
        unsliced_levels.append(new_level)

    return unsliced_levels

def slice_rows(text_levels, pad_r=1, pad_c=1):
    pad_c_arr = [util_common.VOID_TEXT] * pad_c

    sliced_level = []
    for idx, lvl in enumerate(text_levels):
        row = []
        for r in range(len(lvl)):
            row.extend(lvl[r])
            if r < len(lvl) - 1:
                row.extend(pad_c_arr)
        sliced_level.append(row)

        if idx < len(text_levels) - 1 and pad_c > 0:
            sliced_level.extend([[util_common.VOID_TEXT] * len(sliced_level[0])] * pad_r)

    return sliced_level

def unslice_rows(sliced_level, pad_r=1):
    unsliced_lvl = []

    for idb, block in enumerate(sliced_level):
        newblock = []
        for line in block:
            newline = []
            for c in line:
                if(c == ' '):
                    if newline:
                        newblock.extend([newline])
                        newline=[]
                else:
                    newline.append(c)
            if newline:
                newblock.extend([newline])

            unsliced_lvl.extend(newblock)

            if(idb < len(sliced_level)-1):
                unsliced_lvl.extend([[util_common.VOID_TEXT] * len(newblock[0])] * pad_r)

    return unsliced_lvl


if __name__ == '__main__':
    util_common.timer_start()

    parser = argparse.ArgumentParser(description='Split concatenated level into multiple levels.')
    parser.add_argument('--outfile', required=True, type=str, help='File to write to.')
    parser.add_argument('--textfile', type=str, help='Input text file.')
    parser.add_argument('--slice-rows', action='store_true', help='Slice level across rows (side by side).')
    parser.add_argument('--unslice-rows', action='store_true', help='Unslice level across rows (original spacetime format).')
    parser.add_argument('--slice-cols', action='store_true', help='Slice level across cols (side by side).')
    parser.add_argument('--unslice-cols', action='store_true', help='Unslice level across cols (original spacetime format).')
    parser.add_argument('--pad-rows', type=int, default=1, help='Horizontal padding between levels.')
    parser.add_argument('--pad-cols', type=int, default=1, help='Vertical padding between rows.')

    args = parser.parse_args()

    text_level_in = util_common.read_text_level(args.textfile, False)

    text_levels = concat2level(text_level_in)

    if args.slice_rows:
        sliced_r = slice_rows(text_levels, args.pad_rows, args.pad_cols)
        with util_common.openz(args.outfile, 'wt') as f:
            util_common.print_text_level(sliced_r, outstream=f)
    elif args.unslice_rows:
        unsliced_r = unslice_rows(text_levels, args.pad_rows)
        with util_common.openz(args.outfile, 'wt') as f:
            util_common.print_text_level(unsliced_r, outstream=f)
    elif args.slice_cols:
        sliced_c = slice_cols(text_levels, args.pad_rows, args.pad_cols)
        with util_common.openz(args.outfile, 'wt') as f:
            util_common.print_text_level(sliced_c, outstream=f)
    elif args.unslice_cols:
        unsliced_c = unslice_cols(text_levels, args.pad_rows)
        with util_common.openz(args.outfile, 'wt') as f:
            util_common.print_text_level(unsliced_c, outstream=f)
    else:
        digits = int(math.log(len(text_levels), 10)) + 1
        for ii, text_level in enumerate(text_levels):
            outname = args.outfile + str(ii).zfill(digits) + '.lvl'
            with util_common.openz(outname, 'wt') as f:
                util_common.print_text_level(text_level, outstream=f)

    util_common.exit_solution_found()
