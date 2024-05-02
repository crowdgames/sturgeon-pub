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

def get_template_open_closed(move_template):
    template_open_closed = {}
    for dest, need_open_path, need_open_aux, need_closed_path, need_closed_aux in move_template:
        need_open_close = ([(0, 0)] + need_open_path + need_open_aux + [dest], need_closed_path + need_closed_aux, 1 + len(need_open_path) + len(need_closed_path))
        if dest not in template_open_closed:
            template_open_closed[dest] = []
        template_open_closed[dest].append(need_open_close)
    return template_open_closed

def get_path_open_closed(path, template_open_closed):
    path_open = {}
    path_closed = {}

    for (fr, fc, tr, tc) in edge_path_from_point_path(path):
        dr, dc = tr - fr, tc - fc
        open_sets, closed_sets = [], []

        for dopen, dclosed, dlen in template_open_closed[(dr, dc)]:
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
    are_open = {}
    are_closed = {}

    util_common.check(src_text not in open_text and dst_text not in open_text, 'src/dst in open_text')

    open_start_goal_text = open_text + src_text + dst_text

    for rr in range(len(text_level)):
        for cc in range(len(text_level[rr])):
            if text_level[rr][cc] in open_start_goal_text:
                are_open[(rr, cc)] = None
            else:
                are_closed[(rr, cc)] = None

    return are_open, are_closed

def get_nexts_from(pt, rows, cols, template_open_closed, are_open, are_closed, exclude):
    lr, lc = pt
    nexts = {}

    for dest, need_open_closed_len in template_open_closed.items():
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
                if (need_r, need_c) in are_closed:
                    need_missing = True
            for need_r, need_c in need_closed:
                need_r, need_c = lr + need_r, lc + need_c
                if need_r < 0 or rows <= need_r or need_c < 0 or cols <= need_c:
                    need_missing = True
                if (need_r, need_c) in are_open:
                    need_missing = True
            if need_missing:
                continue

            util_common.check((nr, nc) not in nexts, 'duplicate next')
            nexts[(nr, nc)] = path_len

    return nexts

def get_nexts_open_closed_from(path, reverse, rows, cols, template_open_closed):
    path_nexts = {}
    path_open, path_closed = get_path_open_closed(path, template_open_closed)

    if len(path) > 0:
        if not reverse:
            path_nexts = get_nexts_from(path[-1], rows, cols, template_open_closed, path_open, path_closed, path)
        else:
            path_nexts = {}
            for rr in range(rows):
                for cc in range(cols):
                    pt = (rr, cc)
                    if pt in path:
                        continue
                    if path[0] not in get_nexts_from(pt, rows, cols, template_open_closed, path_open, path_closed, path[1:]):
                        continue
                    path_nexts[pt] = None

    return path_nexts, path_open, path_closed

def path_between(rng, start, end, rows, cols, inset, template_open_closed, are_open_closed):
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

        if are_open_closed is not None:
            are_open, are_closed = are_open_closed
        else:
            are_open, are_closed = get_path_open_closed(path, template_open_closed)

        path_nexts = get_nexts_from(path[-1], rows, cols, template_open_closed, are_open, are_closed, path)

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

def path_between_dijkstra(start, end, rows, cols, template_open_closed, are_open, are_closed):
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

        path_nexts = get_nexts_from(path[-1], rows, cols, template_open_closed, are_open, are_closed, path)

        for n in path_nexts:
            new_cost = cost + path_nexts[n]
            if n not in best_cost or new_cost < best_cost[n]:
                heapq.heappush(q, (new_cost, path + (n,)))
                best_cost[n] = new_cost

    return found_path, dict.fromkeys(best_cost)

def shortest_path_between(start, end, rows, cols, template_open_closed, are_open, are_closed):
    return path_between(None, start, end, rows, cols, 0, template_open_closed, (are_open, are_closed))

def random_path_between(rng, start, end, rows, cols, inset, template_open_closed):
    return path_between(rng, start, end, rows, cols, inset, template_open_closed, None)

def random_path_by_search(rng, rows, cols, template_open_closed):
    pts = []
    for rr in range(RANDOM_PATH_INSET, rows - RANDOM_PATH_INSET):
        for cc in range(RANDOM_PATH_INSET, cols - RANDOM_PATH_INSET):
            pts.append((rr, cc))
    start, end = rng.sample(pts, 2)

    return random_path_between(rng, start, end, rows, cols, RANDOM_PATH_INSET, template_open_closed)
