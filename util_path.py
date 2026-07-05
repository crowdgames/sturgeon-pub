import heapq
import util_common

RANDOM_PATH_INSET = 1

UNWRAP_NONE = 0
UNWRAP_PRE  = 1
UNWRAP_POST = 2

def order_edge_path(edge_path_unordered):
    src_to_dst = {}
    dsts = {}
    for a, b, c, d in edge_path_unordered:
        src_to_dst[(a, b)] = (c, d)
        dsts[(c, d)] = None

    src = None
    for a, b, c, d in edge_path_unordered:
        if (a, b) not in dsts:
            util_common.check(src is None, 'multiple starts in path')
            src = (a, b)
    util_common.check(src is not None, 'no starts in path')

    edge_path = []
    while src in src_to_dst:
        dst = src_to_dst[src]
        edge_path.append((src[0], src[1], dst[0], dst[1]))
        util_common.check(len(edge_path) <= len(edge_path_unordered), 'path lengths')
        src = dst
    util_common.check(len(edge_path) == len(edge_path_unordered), 'path lengths')

    return edge_path

def unwrap_edge_path(path):
    path_unwrapped = []
    path_orig_from = []
    path_was_unwrapped = []
    for edge in path:
        if len(edge) == 4:
            fr, fc, tr, tc = edge
            path_unwrapped.append(edge)
            path_orig_from.append((fr, fc))
            path_was_unwrapped.append(UNWRAP_NONE)
        elif len(edge) == 6:
            fr, fc, tr, tc, pwtr, pwtc = edge
            path_unwrapped.append((fr, fc, pwtr, pwtc))
            path_orig_from.append((fr, fc))
            path_was_unwrapped.append(UNWRAP_PRE)
            path_unwrapped.append((tr - (pwtr - fr), tc - (pwtc - fc), tr, tc))
            path_orig_from.append((fr, fc))
            path_was_unwrapped.append(UNWRAP_POST)
        else:
            util_common.check(False, 'path edge wrong length')
    return path_unwrapped, path_orig_from, path_was_unwrapped

def merge_unwrapped_edge_paths(edge_paths):
    edges = {}
    for edge_path in edge_paths:
        path_unwrapped, _, _ = unwrap_edge_path(edge_path)
        for edge in path_unwrapped:
            edges[edge] = None
    return list(edges.keys())

def path_begin_point(path):
    return path[0][0:2]

def path_end_point(path):
    return path[-1][2:4]

def edge_path_from_lines(prefix, lines):
    for line in lines:
        if line.startswith(prefix):
            edge_path = []
            edges_str = line[len(prefix):]
            for edge in edges_str.split(','):
                edge = tuple([int(el) for el in edge.strip().split()])
                util_common.check(len(edge) == 4, 'edge length')
                edge_path.append(edge)
            return edge_path
    return None

def get_move_info_delta_moves(move_info, dr, dc):
    ret = []

    for move in move_info.move_template:
        dest_delta, need_open_path_delta, need_open_aux_delta, need_closed_path_delta, need_closed_aux_delta = move

        if (dr, dc) == dest_delta:
            ret.append(move)

    return ret

def get_path_open_closed(path, game_to_move_info, game_locations):
    path_open = {}
    path_closed = {}

    path_unwrapped, path_orig_from, path_was_unwrapped = unwrap_edge_path(path)
    for (fr, fc, tr, tc), (ofr, ofc) in zip(path_unwrapped, path_orig_from):
        move_info = game_to_move_info[game_locations[(ofr, ofc)]]

        dr, dc = tr - fr, tc - fc
        open_sets, closed_sets = [], []

        for move in get_move_info_delta_moves(move_info, dr, dc):
            dest_delta, need_open_path_delta, need_open_aux_delta, need_closed_path_delta, need_closed_aux_delta = move

            open_set, closed_set = set(), set()
            for (rr, cc) in [(0, 0)] + need_open_path_delta + need_open_aux_delta + [dest_delta]:
                open_set.add((fr + rr, fc + cc))
            open_sets.append(open_set)
            for (rr, cc) in need_closed_path_delta + need_closed_aux_delta:
                closed_set.add((fr + rr, fc + cc))
            closed_sets.append(closed_set)

        if len(open_sets) > 0:
            for open_pt in sorted(set.intersection(*open_sets)):
                path_open[open_pt] = None
        if len(closed_sets) > 0:
            for closed_pt in sorted(set.intersection(*closed_sets)):
                path_closed[closed_pt] = None

    return path_open, path_closed

def get_level_src_dst(text_level, src_text, dst_text):
    src_loc, dst_loc = None, None

    for rr in range(len(text_level)):
        for cc in range(len(text_level[rr])):
            if text_level[rr][cc] == src_text:
                util_common.check(src_loc is None, 'multiple src in level')
                src_loc = (rr, cc)
            elif text_level[rr][cc] == dst_text:
                util_common.check(dst_loc is None, 'multiple dst in level')
                dst_loc = (rr, cc)

    util_common.check(src_loc is not None, 'no src in level')
    util_common.check(dst_loc is not None, 'no dst in level')

    return src_loc, dst_loc

def get_level_open_closed(text_level, open_text, src_text, dst_text):
    open_locations = {}
    closed_locations = {}

    util_common.check(src_text not in open_text and dst_text not in open_text, 'src/dst in open_text')

    open_start_goal_text = open_text + src_text + dst_text

    for rr in range(len(text_level)):
        for cc in range(len(text_level[rr])):
            if text_level[rr][cc] in open_start_goal_text:
                open_locations[(rr, cc)] = None
            else:
                closed_locations[(rr, cc)] = None

    return open_locations, closed_locations

def edge_key_cost_tile(edge_key):
    fr, fc, tr, tc, pwtr, pwtc, need_open_path, need_open_aux, need_closed_path, need_closed_aux = edge_key
    return 1 + len(need_open_path) + len(need_closed_path)

def get_nexts_from(pt, rows, cols, game_to_move_info, game_locations, open_locations, closed_locations, exclude):
    nexts = {}

    move_info = game_to_move_info[game_locations[pt]]

    rr, cc = pt

    edge_keys = util_common.get_edge_keys_from(pt, rows, cols, move_info, game_locations, open_locations, closed_locations, exclude)

    for edge_key in edge_keys:
        fr, fc, tr, tc, pwtr, pwtc, need_open_path, need_open_aux, need_closed_path, need_closed_aux = edge_key
        util_common.check(fr == rr and fc == cc, 'edge')
        util_common.check((tr, tc) not in nexts, 'duplicate next')

        nexts[(tr, tc)] = ((fr, fc, tr, tc, pwtr, pwtc), (edge_key_cost_tile(edge_key), ((tr, tc),) + need_open_path + need_closed_path))

    return nexts

def get_nexts_open_closed_from(pt, path, reverse, rows, cols, game_to_move_info, game_locations):
    path_nexts = {}
    path_open, path_closed = get_path_open_closed(path, game_to_move_info, game_locations)

    path_unwrapped, path_orig_from, path_was_unwrapped = unwrap_edge_path(path)

    exclude = {}
    for (fr, fc, tr, tc) in path_unwrapped:
        exclude[(fr, fc)] = None
        exclude[(tr, tc)] = None

    if not reverse:
        path_nexts = get_nexts_from(pt, rows, cols, game_to_move_info, game_locations, path_open, path_closed, exclude)
    else:
        if pt in exclude:
            del exclude[pt]

        path_nexts = {}
        for rr in range(rows):
            for cc in range(cols):
                frompt = (rr, cc)
                if frompt in path_closed:
                    continue
                if frompt in exclude:
                    continue
                nexts = get_nexts_from(frompt, rows, cols, game_to_move_info, game_locations, path_open, path_closed, exclude)
                if pt not in nexts:
                    continue
                path_nexts[frompt] = nexts[pt]

    return path_nexts, path_open, path_closed

COST_EDGE = 'edge'
COST_TILE = 'tile'
COST_LIST = [COST_EDGE, COST_TILE]

def path_between(start, end, rows, cols, game_to_move_info, game_locations, open_locations, closed_locations, cost_type, rng, inset, enum):
    util_common.check(cost_type in COST_LIST, 'cost_type')

    recompute_open_closed_locations = False
    if open_locations is None or closed_locations is None:
        util_common.check(open_locations is None and closed_locations is None, 'open_locations and closed_locations must be set together')
        recompute_open_closed_locations = True

    if not recompute_open_closed_locations:
        for location in game_locations:
            util_common.check(location in open_locations or location in closed_locations, 'location not open or closed')

    q = []
    best_cost = {}

    if cost_type == COST_TILE:
        heapq.heappush(q, (0, [], [start]))
    else:
        q.append(([], [start]))
    best_cost[start] = 0

    found_paths, found_paths_cost = None, None
    while len(q) > 0:
        if cost_type == COST_TILE:
            cost, path_edges, path_tiles = heapq.heappop(q)
            util_common.check(len(path_tiles) - 1 == cost, 'cost')
        else:
            path_edges, path_tiles = q.pop()
            cost = len(path_edges)

        if len(path_edges) == 0:
            path_end = start
        else:
            path_end = path_edges[-1][2:4]

        if found_paths_cost is not None and cost > found_paths_cost:
            continue

        if path_end == end:
            if not enum:
                found_paths = (path_edges, path_tiles)
                found_paths_cost = cost
                break
            else:
                if found_paths is None:
                    found_paths = [(path_edges, path_tiles)]
                    found_paths_cost = cost
                else:
                    util_common.check(cost >= found_paths_cost, 'found_paths_cost')
                    if cost > found_paths_cost:
                        break
                    else:
                        found_paths.append((path_edges, path_tiles))

        if recompute_open_closed_locations:
            open_locations, closed_locations = get_path_open_closed(path_edges, game_to_move_info, game_locations)

        path_unwrapped, _, _ = unwrap_edge_path(path_edges)
        exclude = {}
        for (fr, fc, tr, tc) in path_unwrapped:
            exclude[(fr, fc)] = None
            exclude[(tr, tc)] = None
        path_nexts = get_nexts_from(path_end, rows, cols, game_to_move_info, game_locations, open_locations, closed_locations, exclude)

        for n in path_nexts:
            if n[0] < inset or n[0] >= rows - inset:
                continue
            if n[1] < inset or n[1] >= cols - inset:
                continue

            (fr, fc, tr, tc, pwtr, pwtc), (tile_cost, need_path) = path_nexts[n]
            if cost_type == COST_TILE:
                new_cost = cost + tile_cost
            else:
                new_cost = cost + 1

            if n in best_cost:
                if not enum:
                    if cost_type == COST_TILE:
                        if new_cost >= best_cost[n]:
                            continue
                    else:
                        continue
                else:
                    if (new_cost > best_cost[n] or (found_paths_cost is not None and cost > found_paths_cost)):
                        continue

            best_cost[n] = new_cost
            next_path_edges = path_edges + [util_common.get_path_edge(fr, fc, tr, tc, pwtr, pwtc)]
            next_path_tiles = path_tiles + list(need_path)
            if cost_type == COST_TILE:
                heapq.heappush(q, (new_cost, next_path_edges, next_path_tiles))
            else:
                q.insert(0, (next_path_edges, next_path_tiles))

        if rng is not None:
            rng.shuffle(q)

    if found_paths is None:
        return None, dict.fromkeys(best_cost)
    else:
        return found_paths, None

def shortest_path_between(start, end, rows, cols, game_to_move_info, game_locations, open_locations, closed_locations):
    path, reachable = path_between(start, end, rows, cols, game_to_move_info, game_locations, open_locations, closed_locations, COST_EDGE, None, 0, False)
    return None if path is None else path[0]

def random_path(rows, cols, game_to_move_info, game_locations, rng):
    pts = []
    for rr in range(RANDOM_PATH_INSET, rows - RANDOM_PATH_INSET):
        for cc in range(RANDOM_PATH_INSET, cols - RANDOM_PATH_INSET):
            pts.append((rr, cc))
    start, end = rng.sample(pts, 2)

    path, reachable = path_between(start, end, rows, cols, game_to_move_info, game_locations, None, None, COST_EDGE, rng, RANDOM_PATH_INSET, False)
    return None if path is None else path[0]
