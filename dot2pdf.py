import argparse, subprocess
import util_common, util_graph
import networkx as nx



if __name__ == '__main__':
    util_common.timer_start()

    parser = argparse.ArgumentParser(description='Convert a dot file(s) to a pdf.')
    parser.add_argument('--outfile', required=True, type=str, help='Output file.')
    parser.add_argument('--dotfile', required=True, type=str, nargs='+', help='Input dot file(s).')
    parser.add_argument('--layout', type=str, help='Individual graph layout command.', default='dot')
    args = parser.parse_args()

    if len(args.dotfile) == 1:
        data = subprocess.check_output([args.layout] + args.dotfile + ['-Tpdf'])
    else:
        data = subprocess.check_output([args.layout] + args.dotfile)
        data = subprocess.check_output(['gvpack', '-array_ci1', '-m100'], input=data)
        data = subprocess.check_output(['neato', '-n2', '-Tpdf'], input=data)

    with util_common.openz(args.outfile, 'wb') as f:
        f.write(data)
