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



if __name__ == '__main__':
    util_common.timer_start()

    parser = argparse.ArgumentParser(description='Split concatenated level into multiple levels.')
    parser.add_argument('--outfile', required=True, type=str, help='File to write to.')
    parser.add_argument('--textfile', type=str, help='Input text file.')
    args = parser.parse_args()

    text_level_in = util_common.read_text_level(args.textfile, False)

    text_levels = concat2level(text_level_in)

    digits = int(math.log(len(text_levels), 10)) + 1
    for ii, text_level in enumerate(text_levels):
        outname = args.outfile + str(ii).zfill(digits) + '.lvl'
        with util_common.openz(outname, 'wt') as f:
            util_common.print_text_level(text_level, outstream=f)

    util_common.exit_solution_found()
