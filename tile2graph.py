import argparse, os, shutil, pickle, sys
import util_common, util_graph
import networkx as nx



def tiles2graph(tile_info, text_labels, no_edge_labels):
    util_common.check(len(tile_info.levels) == 1, 'only handles one tile level')

    if text_labels:
        util_common.check(tile_info.tileset.tile_to_text, 'no text')

    tile_level = tile_info.levels[0].tiles

    rows = len(tile_level)
    cols = len(tile_level[0])

    def nodeid(_rr, _cc):
        return f'{_rr}-{_cc}'

    gr = nx.DiGraph()
    for rr in range(rows):
        for cc in range(cols):
            if text_labels:
                node_label = tile_info.tileset.tile_to_text[tile_level[rr][cc]]
            else:
                node_label = tile_level[rr][cc]

            gr.add_node(nodeid(rr, cc))
            gr.nodes[nodeid(rr, cc)][util_graph.GATTR_LABEL] = node_label
            gr.nodes[nodeid(rr, cc)][util_graph.GATTR_POSITION] = (cc, rows - rr - 1)

    for rr in range(rows):
        for cc in range(cols):
            if rr + 1 < rows:
                gr.add_edge(nodeid(rr, cc), nodeid(rr + 1, cc))
                gr.edges[(nodeid(rr, cc), nodeid(rr + 1, cc))][util_graph.GATTR_LABEL] = '' if no_edge_labels else util_graph.LABEL_GRID_SOUTH

            if cc + 1 < cols:
                gr.add_edge(nodeid(rr, cc), nodeid(rr, cc + 1))
                gr.edges[(nodeid(rr, cc), nodeid(rr, cc + 1))][util_graph.GATTR_LABEL] = '' if no_edge_labels else util_graph.LABEL_GRID_EAST

    gtype = util_graph.GTYPE_DAG

    util_graph.check_graph(gr, gtype)

    grs = util_graph.Graphs()
    grs.gtype = gtype
    grs.colors = {}
    grs.graphs = [gr]

    return grs



if __name__ == '__main__':
    util_common.timer_start()

    parser = argparse.ArgumentParser(description='Generate tiles from level and/or image.')
    parser.add_argument('--outfile', required=True, type=str, help='Output tile file.')
    parser.add_argument('--tilefile', required=True, type=str, help='Input tile file.')
    parser.add_argument('--text-labels', action='store_true', help='Use tile text for labels.')
    parser.add_argument('--no-edge-labels', action='store_true', help='Don\'t output edge labels.')
    args = parser.parse_args()

    with util_common.openz(args.tilefile, 'rb') as f:
        tile_info = pickle.load(f)

    ogrs = tiles2graph(tile_info, args.text_labels, args.no_edge_labels)
    util_graph.write_graph_to_file(ogrs, args.outfile)
