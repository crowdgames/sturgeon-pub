import heapq
import util_common

RANDOM_PATH_INSET = 1

def point_path_from_json(point_path_json):
    return [tuple(pt) for pt in point_path_json]

def edge_path_from_json(edge_path_json):
    return [tuple(pt) for pt in edge_path_json]

def point_path_from_edge_path(edge_path):
    point_path = []
    if len(edge_path) > 0:
        (fr, fc, tr, tc) = edge_path[0]
        point_path.append((fr, fc))
    for (fr, fc, tr, tc) in edge_path:
        util_common.check((fr, fc) == point_path[-1], 'edge path')
        point_path.append((tr, tc))
    return point_path

def edge_path_from_point_path(point_path):
    return [(a, b, c, d) for (a, b), (c, d) in zip(point_path, point_path[1:])]

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

def get_open_closed_template(move_template):
    open_closed_template = {}
    for dest, need_open_path, need_open_aux, need_closed_path, need_closed_aux in move_template:
        need_open_close = ([(0, 0)] + need_open_path + need_open_aux + [dest], need_closed_path + need_closed_aux, 1 + len(need_open_path) + len(need_closed_path))
        if dest not in open_closed_template:
            open_closed_template[dest] = []
        open_closed_template[dest].append(need_open_close)
    return open_closed_template

def get_path_open_closed(path, game_to_open_closed_template, game_locations):
    path_open = {}
    path_closed = {}

    for (fr, fc, tr, tc) in edge_path_from_point_path(path):
        open_closed_template = game_to_open_closed_template[game_locations[(fr, fc)]]

        dr, dc = tr - fr, tc - fc
        open_sets, closed_sets = [], []

        for dopen, dclosed, dlen in open_closed_template[(dr, dc)]:
            open_set, closed_set = set(), set()
            for (rr, cc) in dopen:
                open_set.add((fr + rr, fc + cc))
            open_sets.append(open_set)
            for (rr, cc) in dclosed:
                closed_set.add((fr + rr, fc + cc))
            closed_sets.append(closed_set)

        for open_pt in sorted(set.intersection(*open_sets)):
            path_open[open_pt] = None
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

def get_nexts_from(pt, rows, cols, game_to_open_closed_template, open_locations, closed_locations, game_locations, exclude):
    lr, lc = pt
    nexts = {}

    open_closed_template = game_to_open_closed_template[game_locations[pt]]

    for dest, need_open_closed_len in open_closed_template.items():
        nr, nc = lr + dest[0], lc + dest[1]
        if nr < 0 or rows <= nr or nc < 0 or cols <= nc:
            continue
        if (nr, nc) in exclude:
            continue

        for need_open, need_closed, path_len in need_open_closed_len:
            need_missing = False
            for need_r, need_c in need_open:
                need_r, need_c = lr + need_r, lc + need_c
                if need_r < 0 or rows <= need_r or need_c < 0 or cols <= need_c:
                    need_missing = True
                if (need_r, need_c) in closed_locations:
                    need_missing = True
            for need_r, need_c in need_closed:
                need_r, need_c = lr + need_r, lc + need_c
                if need_r < 0 or rows <= need_r or need_c < 0 or cols <= need_c:
                    need_missing = True
                if (need_r, need_c) in open_locations:
                    need_missing = True
            if need_missing:
                continue

            util_common.check((nr, nc) not in nexts, 'duplicate next')
            nexts[(nr, nc)] = path_len

    return nexts

def get_nexts_open_closed_from(path, reverse, rows, cols, game_to_open_closed_template, game_locations):
    path_nexts = {}
    path_open, path_closed = get_path_open_closed(path, game_to_open_closed_template, game_locations)

    if len(path) > 0:
        if not reverse:
            path_nexts = get_nexts_from(path[-1], rows, cols, game_to_open_closed_template, path_open, path_closed, game_locations, path)
        else:
            path_nexts = {}
            for rr in range(rows):
                for cc in range(cols):
                    pt = (rr, cc)
                    if pt in path:
                        continue
                    if path[0] not in get_nexts_from(pt, rows, cols, game_to_open_closed_template, path_open, path_closed, game_locations, path[1:]):
                        continue
                    path_nexts[pt] = None

    return path_nexts, path_open, path_closed

def path_between(rng, start, end, rows, cols, inset, game_to_open_closed_template, open_locations, closed_locations, game_locations):
    recompute_open_closed_locations = False
    if open_locations is None or closed_locations is None:
        util_common.check(open_locations is None and closed_locations is None, 'open_locations and closed_locations must be set together')
        recompute_open_closed_locations = True
        
    q = []
    seen = {}

    q.append([start])
    seen[start] = None

    found_path = None
    while len(q) > 0:
        path = q.pop()

        if path[-1] == end:
            found_path = path
            break

        if recompute_open_closed_locations:
            open_locations, closed_locations = get_path_open_closed(path, game_to_open_closed_template, game_locations)

        path_nexts = get_nexts_from(path[-1], rows, cols, game_to_open_closed_template, open_locations, closed_locations, game_locations, path)

        for n in path_nexts:
            if n[0] < inset or n[0] >= rows - inset:
                continue
            if n[1] < inset or n[1] >= cols - inset:
                continue

            if n not in seen:
                q.insert(0, path + [n])
                seen[n] = None

        if rng is not None:
            rng.shuffle(q)

    return found_path

def path_between_dijkstra(start, end, rows, cols, game_to_open_closed_template, open_locations, closed_locations, game_locations):
    q = []
    best_cost = {}

    heapq.heappush(q, (0, (start,)))
    best_cost[start] = 0.0

    found_path = None
    while len(q) > 0:
        cost, path = heapq.heappop(q)

        if path[-1] == end:
            found_path = path
            break

        path_nexts = get_nexts_from(path[-1], rows, cols, game_to_open_closed_template, open_locations, closed_locations, game_locations, path)

        for n in path_nexts:
            new_cost = cost + path_nexts[n]
            if n not in best_cost or new_cost < best_cost[n]:
                heapq.heappush(q, (new_cost, path + (n,)))
                best_cost[n] = new_cost

    return found_path, dict.fromkeys(best_cost)

def shortest_path_between(start, end, rows, cols, game_to_open_closed_template, open_locations, closed_locations, game_locations):
    return path_between(None, start, end, rows, cols, 0, game_to_open_closed_template, open_locations, closed_locations, game_locations)

def random_path_between(rng, start, end, rows, cols, inset, game_to_open_closed_template, game_locations):
    return path_between(rng, start, end, rows, cols, inset, game_to_open_closed_template, None, None, game_locations)

def random_path_by_search(rng, rows, cols, game_to_open_closed_template, game_locations):
    pts = []
    for rr in range(RANDOM_PATH_INSET, rows - RANDOM_PATH_INSET):
        for cc in range(RANDOM_PATH_INSET, cols - RANDOM_PATH_INSET):
            pts.append((rr, cc))
    start, end = rng.sample(pts, 2)

    return random_path_between(rng, start, end, rows, cols, RANDOM_PATH_INSET, game_to_open_closed_template, game_locations)
