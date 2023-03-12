import argparse, os, shutil, pickle, sys
import util, gutil
import networkx as nx



def tiles2graph(tile_info, text_labels):
    util.check(len(tile_info.tile_levels) == 1, 'only handles one tile level')

    if text_labels:
        util.check(tile_info.tile_to_text, 'no text')

    tile_level = tile_info.tile_levels[0]

    rows = len(tile_level)
    cols = len(tile_level[0])

    def nodeid(_rr, _cc):
        return f'{_rr}-{_cc}'

    gr = nx.DiGraph()
    for rr in range(rows):
        for cc in range(cols):
            if text_labels:
                node_label = tile_info.tile_to_text[tile_level[rr][cc]]
            else:
                node_label = tile_level[rr][cc]

            gr.add_node(nodeid(rr, cc))
            gr.nodes[nodeid(rr, cc)][gutil.ATTR_LABEL] = node_label

    for rr in range(rows):
        for cc in range(cols):
            if rr + 1 < rows:
                gr.add_edge(nodeid(rr, cc), nodeid(rr + 1, cc))
                gr.edges[(nodeid(rr, cc), nodeid(rr + 1, cc))][gutil.ATTR_LABEL] = gutil.LABEL_GRID_SOUTH
            if cc + 1 < cols:
                gr.add_edge(nodeid(rr, cc), nodeid(rr, cc + 1))
                gr.edges[(nodeid(rr, cc), nodeid(rr, cc + 1))][gutil.ATTR_LABEL] = gutil.LABEL_GRID_EAST

    gtype = gutil.GTYPE_DAG

    gutil.check_graph(gr, gtype)

    grs = gutil.Graphs()
    grs.gtype = gtype
    grs.colors = {}
    grs.graphs = [gr]

    return grs



if __name__ == '__main__':
    util.timer_start()

    parser = argparse.ArgumentParser(description='Generate tiles from level and/or image.')
    parser.add_argument('--outfile', required=True, type=str, help='Output tile file.')
    parser.add_argument('--tilefile', required=True, type=str, help='Input tile file.')
    parser.add_argument('--text-labels', action='store_true', help='Use tile text for labels.')
    args = parser.parse_args()

    with open(args.tilefile, 'rb') as f:
        tile_info = pickle.load(f)

    ogrs = tiles2graph(tile_info, args.text_labels)
    gutil.write_graph_to_file(ogrs, args.outfile)
