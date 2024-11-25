import itertools, os, shutil
import util_common, util_graph, util_solvers
import networkx as nx



EX_VISIT_NODE          = 'visit-node'
EX_VISIT_EDGE          = 'visit-edge'
EX_COLOR               = 'color'
EX_PEBBLE              = 'pebble'
EX_LIGHTS              = 'lightsout'
EX_MAZE                = 'maze'
EX_SOKO                = 'soko'
EX_ADVENTURE_A         = 'adventure-a'
EX_ADVENTURE_B         = 'adventure-b'
EX_CODEMASTER_NOBRANCH = 'codemaster-nobranch'
EX_CODEMASTER_BRANCH   = 'codemaster-branch'

EXAMPLES = [EX_VISIT_NODE, EX_VISIT_EDGE, EX_COLOR, EX_PEBBLE, EX_LIGHTS, EX_MAZE, EX_SOKO, EX_ADVENTURE_A, EX_ADVENTURE_B, EX_CODEMASTER_NOBRANCH, EX_CODEMASTER_BRANCH]



class MKIVSetup:
    def __init__(self):
        self.example = None
        self.layers = None

class MKIVInfo:
    def __init__(self):
        self.rep_rules = None
        self.directed = None
        self.layers = None
        self.static_node_count = None
        self.dynamic_node_init_count = None
        self.dynamic_node_fini_count = None
        self.dynamic_edge_fini_count = None
        self.static_implies_dynamic_fini = None
        self.dynamic_implies_static_fini = None

def get_example_info(mkiv_setup):
    ei = MKIVInfo()

    ei.layers = mkiv_setup.layers

    ei.directed = False

    ei.static_node_count = {}
    ei.dynamic_node_init_count = {}
    ei.dynamic_node_fini_count = {}
    ei.dynamic_edge_fini_count = {}
    ei.static_implies_dynamic_fini = {}
    ei.dynamic_implies_static_fini = {}


    def _organize_rep_rules(_rep_rules):
        _ret = []

        for _nodes0, _edges0, _nodes1, _edges1 in _rep_rules:
            _nodes, _edges = [], []

            util_common.check(len(_nodes0) == len(_nodes1), 'length mismatch')
            for (_static_node_label, _dynamic_node_label0), _dynamic_node_label1 in zip(_nodes0, _nodes1):
                _nodes.append((_static_node_label, _dynamic_node_label0, _dynamic_node_label1))

            util_common.check(len(_edges0) == len(_edges1), 'length mismatch')
            for (_fra, _til, _static_edge_label, _dynamic_edge_label0), _dynamic_edge_label1 in zip(_edges0, _edges1):
                _edges.append((_fra, _til, _static_edge_label, _dynamic_edge_label0, _dynamic_edge_label1))

            _ret.append((_nodes, _edges))

        return _ret


    if mkiv_setup.example == EX_VISIT_NODE:
        ei.directed = True

        ei.rep_rules = []
        ei.rep_rules.append(([('S', 'P'), ('_', '_')], [(0, 1, None, '_')],
                             [      '_',        'P' ], [             '_']))
        ei.rep_rules.append(([('_', 'P'), ('_', '_')], [(0, 1, None, '_')],
                             [      '*',        'P' ], [             '_']))
        ei.rep_rules.append(([('_', 'P'), ('S', '_')], [(0, 1, None, '_')],
                             [      '*',        'P' ], [             '_']))

        ei.static_node_count = {'S':1}
        ei.dynamic_node_init_count = {'P':1}
        ei.dynamic_node_fini_count = {'_':0}
        ei.static_implies_dynamic_fini = [('S', 'P')]

    elif mkiv_setup.example == EX_VISIT_EDGE:
        ei.directed = True

        ei.rep_rules = []
        ei.rep_rules.append(([(None, 'P'), (None, '_')], [(0, 1, None, '_')],
                             [       '_',         'P' ], [             '*']))

        ei.static_node_count = {'S':1}
        ei.dynamic_node_init_count = {'P':1}
        ei.dynamic_edge_fini_count = {'_':0}
        ei.static_implies_dynamic_fini = [('S', 'P')]

    elif mkiv_setup.example == EX_COLOR:
        ei.directed = True

        ei.rep_rules = []

        ei.rep_rules.append(([('_', 'PR'), ('_', '_')], [(0, 1, 'R', '_')],
                             [      '*',         'PG'], [            '*']))
        ei.rep_rules.append(([('_', 'PG'), ('_', '_')], [(0, 1, 'G', '_')],
                             [      '*',         'PB'], [            '*']))
        ei.rep_rules.append(([('_', 'PB'), ('_', '_')], [(0, 1, 'B', '_')],
                             [      '*',         'PR'], [            '*']))

        ei.rep_rules.append(([('_', 'PR'), ('E', '_')], [(0, 1, 'R', '_')],
                             [      '*',         'PE'], [            '*']))
        ei.rep_rules.append(([('_', 'PG'), ('E', '_')], [(0, 1, 'G', '_')],
                             [      '*',         'PE'], [            '*']))
        ei.rep_rules.append(([('_', 'PB'), ('E', '_')], [(0, 1, 'B', '_')],
                             [      '*',         'PE'], [            '*']))

        ei.static_node_count = {'E':1}
        ei.dynamic_node_init_count = {'PR':1}
        ei.dynamic_node_fini_count = {'_':0}

        ei.static_implies_dynamic_fini = [('E', 'PE')]

    elif mkiv_setup.example == EX_PEBBLE:
        ei.directed = True

        ei.rep_rules = []
        for src in range(7):
            for dst in range(7):
                if src >= 2:
                    ei.rep_rules.append(([('_', str(src)),    ('_', str(dst))],    [(0, 1, '_', '_')],
                                         [      str(src - 2),       str(dst + 1)], [            '_']))

        ei.dynamic_node_init_count = {'0':lambda nvars: nvars // 2}
        ei.dynamic_node_fini_count = {'0':0}

    elif mkiv_setup.example == EX_LIGHTS:
        ei.directed = False

        ei.rep_rules = []

        xx = None

        for src_on in [True, False]:
            aS, bS = ('*', '_') if src_on else ('_', '*')

            for num_on in range(3):
                a1, b1 = ('*', '_') if num_on > 0 else ('_', '*')
                a2, b2 = ('*', '_') if num_on > 1 else ('_', '*')
                ei.rep_rules.append(([('2', aS), (xx, a1), (xx, a2)], [(0, 1, xx, '_'), (0, 2, xx, '_')],
                                     [      bS,       b1,       b2],  [           '_' ,            '_']))

            for num_on in range(4):
                a1, b1 = ('*', '_') if num_on > 0 else ('_', '*')
                a2, b2 = ('*', '_') if num_on > 1 else ('_', '*')
                a3, b3 = ('*', '_') if num_on > 2 else ('_', '*')
                ei.rep_rules.append(([('3', aS), (xx, a1), (xx, a2), (xx, a3)], [(0, 1, xx, '_'), (0, 2, xx, '_'), (0, 3, xx, '_')],
                                     [      bS,       b1,       b2,       b3],  [           '_' ,            '_' ,            '_']))

            for num_on in range(5):
                a1, b1 = ('*', '_') if num_on > 0 else ('_', '*')
                a2, b2 = ('*', '_') if num_on > 1 else ('_', '*')
                a3, b3 = ('*', '_') if num_on > 2 else ('_', '*')
                a4, b4 = ('*', '_') if num_on > 3 else ('_', '*')
                ei.rep_rules.append(([('4', aS), (xx, a1), (xx, a2), (xx, a3), (xx, a4)], [(0, 1, xx, '_'), (0, 2, xx, '_'), (0, 3, xx, '_'), (0, 4, xx, '_')],
                                     [      bS,       b1,       b2,       b3,       b4],  [           '_' ,            '_' ,            '_' ,            '_']))

        ei.dynamic_node_init_count = {'*':1}
        ei.dynamic_node_fini_count = {'*':0}

    elif mkiv_setup.example == EX_MAZE:
        ei.directed = False

        ei.rep_rules = []
        ei.rep_rules.append(([(None, 'P'), (None, '_')], [(0, 1, '_', '_')],
                             [       '_',         'P' ], [            '_']))

        ei.static_node_count = {'E':1}
        ei.dynamic_node_init_count = {'P':1}
        ei.static_implies_dynamic_fini = [('E', 'P')]

    elif mkiv_setup.example == EX_SOKO:
        ei.directed = True

        ei.rep_rules = []
        for lbl in ['e', 's']:
            ei.rep_rules.append(([(None, 'P'), (None, '_')],              [(0, 1, lbl, '_')],
                                 [       '_',         'P' ],              [            '_']))
            ei.rep_rules.append(([(None, 'P'), (None, 'C'), (None, '_')], [(0, 1, lbl, '_'), (1, 2, lbl, '_')],
                                 [       '_',         'P',         'C' ], [            '_',              '_']))
            ei.rep_rules.append(([(None, 'P'), (None, 'C'), (None, 'o')], [(0, 1, lbl, '_'), (1, 2, lbl, '_')],
                                 [       '_',         'P',         'O' ], [            '_',              '_']))
            ei.rep_rules.append(([(None, '_'), (None, 'P')],              [(0, 1, lbl, '_')],
                                 [       'P',         '_' ],              [            '_']))
            ei.rep_rules.append(([(None, '_'), (None, 'C'), (None, 'P')], [(0, 1, lbl, '_'), (1, 2, lbl, '_')],
                                 [       'C',         'P',         '_' ], [            '_',              '_']))
            ei.rep_rules.append(([(None, 'o'), (None, 'C'), (None, 'P')], [(0, 1, lbl, '_'), (1, 2, lbl, '_')],
                                 [       'O',         'P',         '_' ], [            '_',              '_']))

        ei.dynamic_node_init_count = {'P':1, 'C':2, 'o':2}
        ei.dynamic_node_fini_count = {'o':0}

    elif mkiv_setup.example in [EX_ADVENTURE_A, EX_ADVENTURE_B]:
        ei.directed = False

        if mkiv_setup.example == EX_ADVENTURE_A:
            all_keys = ['a']
            all_pows = ['u']
        else:
            all_keys = ['a', 'b']
            all_pows = ['u']

        def _powerset(_ll):
            return itertools.chain.from_iterable(itertools.combinations(_ll, _rr) for _rr in range(len(_ll) + 1))

        def _pstring(_ps):
            nonlocal all_keys, all_pows

            _ret = 'P'
            for _prop in all_keys + all_pows:
                if _prop in _ps:
                    _ret += _prop
                else:
                    _ret += '.'
            return _ret

        ei.rep_rules = []
        for keys in _powerset(all_keys):
            for pows in _powerset(all_pows):
                pla = _pstring(keys + pows)

                for lock in ['_'] + all_keys:
                    for boss in ['_'] + all_pows:
                        if (lock == '_' or lock in keys) and (boss == '_' or boss in pows):
                            lock = lock.upper()
                            boss = boss.upper()

                            ei.rep_rules.append(([(None, pla), ('_', boss)], [(0, 1, lock, '_')],
                                                 [       '_',        pla  ], [             '_']))
                            for pick in all_keys + all_pows:
                                if pick not in keys + pows: # with only one of each pickup, don't need to pick up a second time
                                    plp = _pstring(keys + pows + (pick,))
                                    ei.rep_rules.append(([(None, pla), ('_', pick)], [(0, 1, lock, '_')],
                                                         [       '_',        plp  ], [             '_']))

        for pick in all_keys + all_pows:
            ei.dynamic_node_init_count[pick] = 1
        for boss in all_pows:
            ei.dynamic_node_init_count[boss.upper()] = 1
            ei.dynamic_node_fini_count[boss.upper()] = 0
        ei.dynamic_node_init_count[_pstring([])] = 1

    elif mkiv_setup.example in [EX_CODEMASTER_NOBRANCH, EX_CODEMASTER_BRANCH]:
        ei.directed = True

        MAX_CRYSTAL_PLAYER = 2

        ei.rep_rules = []
        for mclr1 in ['R', 'G', 'B', 'RG', 'RB', 'GB']:
            for sclr1 in 'RGB':
                if sclr1 not in mclr1:
                    continue
                mclr = 'm' + mclr1
                sclr = 's' + sclr1
                for pcrystal in range(MAX_CRYSTAL_PLAYER + 1):
                    mplyr = 'mP' + str(pcrystal)
                    s2TF = 'sT' if pcrystal == 2 else 'sF'

                    # move along scroll next onto empty
                    ei.rep_rules.append(([(None, mplyr), (None, '_'),  (None, 'sP'), (sclr, '_')], [(0, 1, mclr, '_'), (2, 3, 'sN', None)],
                                         [       '_',           mplyr,         '_',         'sP'], [             '_',               '_']))
                    ei.rep_rules.append(([(None, mplyr), (None, '_'),  ('s2', 'sP'), (sclr, '_')], [(0, 1, mclr, '_'), (2, 3, s2TF, None)],
                                         [       '_',           mplyr,         '_',         'sP'], [             '_',               '_']))

                    # TODO: check moving along true/false edge onto color

                    if pcrystal + 1 <= MAX_CRYSTAL_PLAYER:
                        mplyrc = 'mP' + str(pcrystal + 1)
                        # move along scroll next and collect
                        ei.rep_rules.append(([(None, mplyr), (None, 'mC'),  (None, 'sP'), (sclr, '_')], [(0, 1, mclr, '_'), (2, 3, 'sN', None)],
                                             [       '_',           mplyrc,        '_',          'sP'], [             '_',               '_']))
                        ei.rep_rules.append(([(None, mplyr), (None, 'mC'),  ('s2', 'sP'), (sclr, '_')], [(0, 1, mclr, '_'), (2, 3, s2TF, None)],
                                             [       '_',           mplyrc,        '_',          'sP'], [             '_',               '_']))

        for pcrystal in range(MAX_CRYSTAL_PLAYER + 1):
            mplyr = 'mP' + str(pcrystal)

            # move into exit along next
            ei.rep_rules.append(([('mE', mplyr), (None, 'sP'), ('sE', '_')], [(1, 2, 'sN', None)],
                                 [       mplyr,         '_',          'sP'], [             '_']))
            # move into exit along true/false
            s2TF = 'sT' if pcrystal == 2 else 'sF'
            ei.rep_rules.append(([('mE', mplyr), ('s2', 'sP'), ('sE', '_')], [(1, 2, s2TF, None)],
                                 [       mplyr,         '_',          'sP'], [             '_']))

        # move onto branch along next
        ei.rep_rules.append(([(None, 'sP'), ('s2', '_')], [(0, 1, 'sN', None)],
                             [       '_',          'sP'], [             '_']))

        # one root and exit on each
        ei.static_node_count = {'r':1, 'mE':1, 'sE':1}
        # one player on each
        ei.dynamic_node_init_count = {'mP0':1, 'sP':1}
        # visit all scroll edges
        ei.dynamic_edge_fini_count = {'*':0}

        # scroll size and variety
        ei.static_node_count[('sR', 'sG')] = (1, None)
        ei.static_node_count[('sG', 'sB')] = (1, None)
        ei.static_node_count[('sB', 'sR')] = (1, None)
        ei.static_node_count[('sR', 'sG', 'sB', 's2')] = (4, None)

        if mkiv_setup.example in [EX_CODEMASTER_NOBRANCH]:
            ei.dynamic_node_init_count['mC'] = 0 # no crystals
            ei.static_node_count['s2'] = 0 # no branches
        if mkiv_setup.example in [EX_CODEMASTER_BRANCH]:
            ei.dynamic_node_init_count['mC'] = 2 # two crystals
            ei.static_node_count['s2'] = 1 # one branch

        # both end at goal
        ei.dynamic_implies_static_fini = [('mP' + str(pcrystal), 'mE') for pcrystal in range(MAX_CRYSTAL_PLAYER + 1)] + [('sP', 'sE')]

    else:
        util_common.check(False, 'mkiv_setup example ' + mkiv_setup.example)

    ei.rep_rules = _organize_rep_rules(ei.rep_rules)

    return ei


def get_codemaster_edges(fra, map_count, scroll_count):
    if fra == 0: # root
        return {1:['map:_'], 1 + map_count:['scroll:_']}
    elif fra <= map_count: # map
        BAND = 4
        tils = {}
        for til in range(fra - BAND, fra + BAND + 1):
            if til != fra and til > 0 and til < 1 + map_count:
                tils[til] = ['mR:_', 'mG:_', 'mB:_', 'mRG:_', 'mRB:_', 'mGB:_']
        return tils
    else: # scroll
        tils = {}
        if fra == 1 + map_count: # start
            tils[fra + 1] = ['sN:_', 'sN:*']
        elif fra == map_count + scroll_count: # exit
            pass
        else:
            tils[fra + 1] = ['sN:_', 'sN:*', 'sT:_', 'sT:*', 'sF:_', 'sF:*']
            for til in [fra - 2, fra - 3, fra - 4]:
                if til != fra and til > 1 + map_count and til < 1 + map_count + scroll_count:
                    tils[til] = ['sT:_', 'sT:*', 'sF:_', 'sF:*']
        return tils

def write_graph_dot_lightsout(grs, out):
    util_common.check(len(grs.graphs) == 1, 'can only write single graph')
    gr = grs.graphs[0]

    gr = gr.copy()

    for node in gr.nodes:
        node_on = gr.nodes[node][util_graph.GATTR_LABEL].endswith('*')
        gr.nodes[node][util_graph.GATTR_LABEL] = ' ' if node_on else ''

    for edge in gr.edges:
        gr.edges[edge][util_graph.GATTR_LABEL] = ''

    grs_out = util_graph.Graphs()
    grs_out.gtype = grs.gtype
    grs_out.colors = {' ':'00FF00', '':'006600'}
    grs_out.graphs = [gr]

    util_graph.write_graph_dot(grs_out, True, False, 1.0, out)

def write_graph_dot_soko(grs, out):
    util_common.check(len(grs.graphs) == 1, 'can only write single graph')
    gr = grs.graphs[0]

    gr = gr.copy()

    for node in gr.nodes:
        static_label, dynamic_label = get_static_dynamic_label(gr.nodes[node][util_graph.GATTR_LABEL])
        gr.nodes[node][util_graph.GATTR_LABEL] = dynamic_label

    for edge in gr.edges:
        gr.edges[edge][util_graph.GATTR_LABEL] = ''

    grs_out = util_graph.Graphs()
    grs_out.gtype = grs.gtype
    grs_out.colors = {'X':'AAAAAA', 'P':'AAAAFF', 'C':'FFFFAA', 'o':'AAFFFF', 'O':'AAFFAA'}
    grs_out.graphs = [gr]

    util_graph.write_graph_dot(grs_out, True, False, 1.0, out)

def write_graph_dot_codemaster(grs, out):
    util_common.check(len(grs.graphs) == 1, 'can only write single graph')
    gr = grs.graphs[0]

    size = 0.5

    fontsize = 16
    fontsize_per = 2.0
    fontsize_min = 5

    out.write(f'digraph G {{\n')
    out.write(f'  graph [fontname="Courier New" margin="0"]\n')
    out.write(f'  node [fontname="Courier New" fontsize="{fontsize}" shape="circle" width="{size}" height="{size}" fixedsize="true" style="filled" color="none"]\n')
    out.write(f'  edge [fontname="Courier New" fontsize="{fontsize}"]\n')

    for node, label, central, pos in util_graph.nodes_and_label_central_pos(gr):
        static_label, dynamic_label = get_static_dynamic_label(label)

        attrs = ''
        if static_label in ['r']:
            attrs += f' label=""'
            attrs += f' style="invis"'
            attrs += f' width="0.0" height="0.0"'
            attrs += f' ordering="out"'
            attrs += f' rank="min"'
            out.write(f'  {{rank="source" "{node}"}}\n')
        elif static_label in ['mO', 'mE']:
            display_label = ''

            if static_label == 'mE':
                display_label += 'ex'

            if dynamic_label.startswith('mP'):
                if display_label != '':
                    display_label += ' '
                display_label += dynamic_label[1:]

            if dynamic_label == 'mC':
                if display_label != '':
                    display_label += ' '
                display_label += 'C'

            attrs += f' label="{display_label}"'

            if len(display_label) > 1:
                fontsize_disp = max(fontsize_min, fontsize - fontsize_per * (len(display_label) - 1))
                attrs += f' fontsize="{fontsize_disp}"'

            if central:
                attrs += f' penwidth="4"'
                attrs += f' color="#000000"'

            if static_label == 'mE':
                attrs += f' fillcolor="#ffffaa"'
            else:
                attrs += f' fillcolor="#aaaaaa"'

            attrs += f' width="0.5" height="0.5"'
        elif static_label in ['sP', 'sR', 'sG', 'sB', 's2', 'sE']:
            display_label = ''

            if static_label == 'sE':
                display_label += 'ex'
            elif static_label == 's2':
                display_label += '2?'

            if static_label == 's2':
                attrs += f' shape="hexagon"'
                attrs += f' width="0.6" height="0.5"'
            else:
                attrs += f' shape="square"'

            if dynamic_label == 'sP':
                if display_label != '':
                    display_label += ' '
                display_label += 'P'

            attrs += f' label="{display_label}"'

            if len(display_label) > 1:
                fontsize_disp = max(fontsize_min, fontsize - fontsize_per * (len(display_label) - 1))
                attrs += f' fontsize="{fontsize_disp}"'

            if central:
                attrs += f' penwidth="4"'
                attrs += f' color="#000000"'

            if static_label == 'sR':
                attrs += f' fillcolor="#ffaaaa"'
            elif static_label == 'sG':
                attrs += f' fillcolor="#aaffaa"'
            elif static_label == 'sB':
                attrs += f' fillcolor="#aaaaff"'
            elif static_label == 's2':
                attrs += f' fillcolor="#aaffff"'
            elif static_label == 'sE':
                attrs += f' fillcolor="#ffffaa"'
            else:
                attrs += f' fillcolor="#aaaaaa"'

        else:
            util_common.check(False, 'node label: ' + label)

        out.write(f'  "{node}" [{attrs.strip()}]\n')

    root_map_edges = {}
    root_scroll_edges = {}
    map_edges = {}
    scroll_edges = {}

    for fra, til, label, central, delta, polar, cycle in util_graph.edges_and_label_central_delta_polar_cycle(gr):
        if label in ['map:_']:
            root_map_edges[(fra, til)] = None
        elif label in ['map:_', 'scroll:_']:
            root_scroll_edges[(fra, til)] = None
        elif label in ['sN:_', 'sN:*']:
            scroll_edges[(fra, til)] = (None, central)
        elif label in ['sT:_', 'sT:*']:
            scroll_edges[(fra, til)] = (True, central)
        elif label in ['sF:_', 'sF:*']:
            scroll_edges[(fra, til)] = (False, central)
        elif label in ['mR:_', 'mG:_', 'mB:_', 'mRG:_', 'mRB:_', 'mGB:_']:
            colors = None
            if label == 'mR:_':
                colors = 'R'
            elif label == 'mG:_':
                colors = 'G'
            elif label == 'mB:_':
                colors = 'B'
            elif label == 'mRG:_':
                colors = 'RG'
            elif label == 'mRB:_':
                colors = 'RB'
            elif label == 'mGB:_':
                colors = 'GB'
            for color in colors:
                if (til, fra, color) in map_edges:
                    map_edges[(til, fra, color)] = (True, central or map_edges[(til, fra, color)][1])
                else:
                    map_edges[(fra, til, color)] = (False, central)

        else:
            util_common.check(False, 'edge label: ' + label)

    for fra, til in list(root_map_edges.keys()) + list(root_scroll_edges.keys()):
        attrs = ''
        attrs += f' label=""'
        attrs += f' style="invis"'
        out.write(f'  "{fra}" -> "{til}" [{attrs.strip()}]\n')

    for (fra, til, color), (both, central) in map_edges.items():
        attrs = ''
        if central:
            attrs += f' penwidth="8"'
        else:
            attrs += f' penwidth="5"'
        if color == 'R':
            attrs += (f' color="#aa0000"' if central else f' color="#ffaaaa"')
        elif color == 'G':
            attrs += (f' color="#00aa00"' if central else f' color="#aaffaa"')
        elif color == 'B':
            attrs += (f' color="#0000aa"' if central else f' color="#aaaaff"')
        if both:
            attrs += f' arrowhead="none"'
        out.write(f'  "{fra}" -> "{til}" [{attrs.strip()}]\n')

    for (fra, til), (what, central) in scroll_edges.items():
        attrs = ''
        if central:
            attrs += f' penwidth="5"'
        else:
            attrs += f' penwidth="2"'
        attrs += (f' color="#000000"' if central else f' color="#aaaaaa"')
        if what is None:
            attrs += f' label=""'
        elif what is True:
            attrs += f' label="\u2713"'
        elif what is False:
            attrs += f' label="\u00D7"'
            attrs += f' fontsize="30"'
        out.write(f'  "{fra}" -> "{til}" [{attrs.strip()}]\n')

    out.write('}\n')



def make_label(static_label, dynamic_label):
    util_common.check(static_label != '', 'invalid mkiv static label: ' + static_label)
    util_common.check(dynamic_label != '', 'invalid mkiv dynamic label: ' + dynamic_label)

    return static_label + ':' + dynamic_label

def get_static_dynamic_label(label):
    parts = label.split(':')
    util_common.check(len(parts) == 2, 'invalid mkiv label: ' + label)

    static_label, dynamic_label = parts
    util_common.check(static_label != '', 'invalid mkiv label: ' + label)
    util_common.check(dynamic_label != '', 'invalid mkiv label: ' + label)

    return static_label, dynamic_label



def add_mkiv(mkiv_info, s, gtype, node_labels, vars_node_by_id, edge_labels_etc, vars_edge_by_id_by_label_etc):
    # determine static and dynamic labels from graph description
    def find_static_dynamic_labels(_label, _static_labels, _dynamic_labels):
        _static_label, _dynamic_label = get_static_dynamic_label(_label)

        if _static_label not in _static_labels:
            _static_labels[_static_label] = {}
        _static_labels[_static_label][_label] = None

        if _dynamic_label not in _dynamic_labels:
            _dynamic_labels[_dynamic_label] = {}
        _dynamic_labels[_dynamic_label][_label] = None

    static_node_labels = {}
    dynamic_node_labels = {}
    for node_label in node_labels:
        find_static_dynamic_labels(node_label, static_node_labels, dynamic_node_labels)

    static_edge_labels = {}
    dynamic_edge_labels = {}
    for edge_label, delta, polar, cycle in edge_labels_etc:
        find_static_dynamic_labels(edge_label, static_edge_labels, dynamic_edge_labels)

    # determine static and dynamic labels from rules
    def update_static_dynamic_labels(_static_label, _dynamic_label0, _dynamic_label1, _static_labels, _dynamic_labels):
        if _static_label not in _static_labels:
            if _static_label is not None:
                _static_labels[_static_label] = None
        if _dynamic_label0 not in _dynamic_labels:
            if _dynamic_label0 is not None:
                _dynamic_labels[_dynamic_label0] = None
        if _dynamic_label1 not in _dynamic_labels:
            util_common.check(_dynamic_label1 is not None, 'label')
            _dynamic_labels[_dynamic_label1] = None

    for nodes, edges in mkiv_info.rep_rules:
        for static_node_label, dynamic_node_label0, dynamic_node_label1 in nodes:
            update_static_dynamic_labels(static_node_label, dynamic_node_label0, dynamic_node_label1, static_node_labels, dynamic_node_labels)

        for fra, til, static_edge_label, dynamic_edge_label0, dynamic_edge_label1 in edges:
            update_static_dynamic_labels(static_edge_label, dynamic_edge_label0, dynamic_edge_label1, static_edge_labels, dynamic_edge_labels)

    static_node_labels[None] = [None]
    dynamic_node_labels[None] = [None]
    static_edge_labels[None] = [None]
    dynamic_edge_labels[None] = [None]



    # make_conj duplicate helper
    conjs = {}
    def _check_duple_conj(_vvs):
        nonlocal s, conjs

        util_common.check(len(_vvs) > 0, 'empty conj')

        _key = tuple(sorted([str(_vv) for _vv in _vvs]))

        if _key not in conjs:
            if len(_vvs) == 1:
                conjs[_key] = _vvs[0]
            else:
                conjs[_key] = s.make_conj(_vvs, True)
            return conjs[_key]
        else:
            return None

    # disj duplicate helper
    disjs = {}
    def _make_disj(_vvs):
        nonlocal s, disjs

        util_common.check(len(_vvs) > 0, 'empty disj')

        _key = tuple(sorted([str(_vv) for _vv in _vvs]))

        if _key not in disjs:
            if len(_vvs) == 1:
                disjs[_key] = _vvs[0]
            else:
                _disj = s.make_var()
                for _vv in _vvs:
                    s.cnstr_implies_disj(_vv, True, [_disj], True, None)
                s.cnstr_implies_disj(_disj, True, _vvs, True, None)
                disjs[_key] = _disj

        return disjs[_key]

    # always false
    var_false = s.make_var()
    s.cnstr_count([var_false], True, 0, 0, None)

    def _edge(_label):
        if _label is None:
            return None
        else:
            return (_label, None, None, None)

    def _find_edge_vars(_vv_map, _labels):
        _ret = {}
        for _check_label in _labels:
            for _label_etc, _vv in _vv_map.items():
                if _label_etc is None:
                    if _check_label == None:
                        _ret[_vv] = None
                else:
                    _label, _delta, _polar, _cycle = _label_etc
                    if _check_label == _label:
                        _ret[_vv] = None
        util_common.check(len(_ret) != 0, 'no vars')
        return list(_ret.keys())

    # static node variables
    vars_node_static_by_id = {}

    for node in vars_node_by_id:
        vars_node_static_by_id[node] = {}
        for static_node_label, labels in static_node_labels.items():
            if labels is not None:
                vars_node_static_by_id[node][static_node_label] = _make_disj([vars_node_by_id[node][label] for label in labels])
            else:
                vars_node_static_by_id[node][static_node_label] = var_false

    # static edge variables
    vars_edge_static_by_id = {}

    for edge in vars_edge_by_id_by_label_etc:
        vars_edge_static_by_id[edge] = {}
        for static_edge_label, labels in static_edge_labels.items():
            if labels is not None:
                vars_edge_static_by_id[edge][static_edge_label] = _make_disj(_find_edge_vars(vars_edge_by_id_by_label_etc[edge], labels))
            else:
                vars_edge_static_by_id[edge][static_edge_label] = var_false

    # dynamic node variables
    vars_node_dynamic_by_layer_by_id = {}

    for layer in range(mkiv_info.layers):
        vars_node_dynamic_by_layer_by_id[layer] = {}

        for node in vars_node_by_id:
            vars_node_dynamic_by_layer_by_id[layer][node] = {}

            if layer == 0:
                for dynamic_node_label, labels in dynamic_node_labels.items():
                    if labels is not None:
                        vars_node_dynamic_by_layer_by_id[layer][node][dynamic_node_label] = _make_disj([vars_node_by_id[node][label] for label in labels])
                    else:
                        vars_node_dynamic_by_layer_by_id[layer][node][dynamic_node_label] = var_false
            else:
                for dynamic_node_label in dynamic_node_labels:
                    vv = s.make_var()
                    vars_node_dynamic_by_layer_by_id[layer][node][dynamic_node_label] = vv
                s.cnstr_count(list(vars_node_dynamic_by_layer_by_id[layer][node].values()), True, 1, 1, None)

    # dynamic edge variables
    vars_edge_dynamic_by_layer_by_id = {}

    for layer in range(mkiv_info.layers):
        vars_edge_dynamic_by_layer_by_id[layer] = {}

        for edge in vars_edge_by_id_by_label_etc:
            vars_edge_dynamic_by_layer_by_id[layer][edge] = {}

            if layer == 0:
                for dynamic_edge_label, labels in dynamic_edge_labels.items():
                    if labels is not None:
                        vars_edge_dynamic_by_layer_by_id[layer][edge][dynamic_edge_label] = _make_disj(_find_edge_vars(vars_edge_by_id_by_label_etc[edge], labels))
                    else:
                        vars_edge_dynamic_by_layer_by_id[layer][edge][dynamic_edge_label] = var_false
            else:
                for dynamic_edge_label in dynamic_edge_labels:
                    vv = s.make_var()
                    vars_edge_dynamic_by_layer_by_id[layer][edge][dynamic_edge_label] = vv
                s.cnstr_count(list(vars_edge_dynamic_by_layer_by_id[layer][edge].values()), True, 1, 1, None)

    # terminal variables
    vars_term = []
    vars_term.append(None)
    for layer in range(mkiv_info.layers - 1):
        vars_term.append(s.make_var())

    # for checking what changed
    changes_by_layer = {}

    for layer in range(mkiv_info.layers - 1):
        # terminal stays set
        if layer > 0:
            s.cnstr_implies_disj(vars_term[layer], True, [vars_term[layer + 1]], True, None)

        # keep track of change vars
        layer_changes = []

        # keep track of possible changes at this layer
        layer_changes_by_node = {}
        for node in vars_node_by_id:
            layer_changes_by_node[node] = []

        layer_changes_by_edge = {}
        for edge in vars_edge_by_id_by_label_etc:
            layer_changes_by_edge[edge] = []

        changes_by_layer[layer] = []

        # connect layers
        seen_changes = {}
        for nodes, edges in mkiv_info.rep_rules:
            for node_indices in itertools.permutations(vars_node_by_id, len(nodes)):
                change_edges, ved_st, ved_in, ved_ou  = [], [], [], []
                for fra, til, static_edge_label, dynamic_edge_label0, dynamic_edge_label1 in edges:
                    if util_graph.gtype_directed(gtype) and mkiv_info.directed:
                        fra_ind = node_indices[fra]
                        til_ind = node_indices[til]
                    else:
                        fra_ind = min(node_indices[fra], node_indices[til])
                        til_ind = max(node_indices[fra], node_indices[til])
                    if (fra_ind, til_ind) in vars_edge_by_id_by_label_etc:
                        change_edges.append((fra_ind, til_ind))
                        if static_edge_label is not None:
                            ved_st.append(vars_edge_static_by_id[(fra_ind, til_ind)][static_edge_label])
                        if dynamic_edge_label0 is not None:
                            ved_in.append(vars_edge_dynamic_by_layer_by_id[layer+0][(fra_ind, til_ind)][dynamic_edge_label0])
                        util_common.check(dynamic_edge_label1 is not None, 'label')
                        ved_ou.append(vars_edge_dynamic_by_layer_by_id[layer+1][(fra_ind, til_ind)][dynamic_edge_label1])
                if len(edges) != len(change_edges):
                    continue

                change_nodes, vnd_st, vnd_in, vnd_ou = [], [], [], []
                for node_ind, (static_node_label, dynamic_node_label0, dynamic_node_label1) in zip(node_indices, nodes):
                    change_nodes.append(node_ind)
                    if static_node_label is not None:
                        vnd_st.append(vars_node_static_by_id[node_ind][static_node_label])
                    if dynamic_node_label0 is not None:
                        vnd_in.append(vars_node_dynamic_by_layer_by_id[layer+0][node_ind][dynamic_node_label0])
                    util_common.check(dynamic_node_label1 is not None, 'label')
                    vnd_ou.append(vars_node_dynamic_by_layer_by_id[layer+1][node_ind][dynamic_node_label1])

                change_vars = ved_st + ved_in + ved_ou + vnd_st + vnd_in + vnd_ou
                change = _check_duple_conj(change_vars)

                if change is None:
                    continue

                changes_by_layer[layer].append((change_vars, change_nodes, change_edges))
                layer_changes.append(change)
                for node_ind in change_nodes:
                    layer_changes_by_node[node_ind].append(change)
                for edge_ind in change_edges:
                    layer_changes_by_edge[edge_ind].append(change)

        # exactly one change or terminal
        changes_or_term = layer_changes + [vars_term[layer + 1]]
        s.cnstr_count(changes_or_term, True, 1, 1, None)

        # everything is either the same or part of a change
        for node in vars_node_by_id:
            for dynamic_node_label in dynamic_node_labels:
                vv0 = vars_node_dynamic_by_layer_by_id[layer + 0][node][dynamic_node_label]
                vv1 = vars_node_dynamic_by_layer_by_id[layer + 1][node][dynamic_node_label]
                s.cnstr_implies_disj(vv0, True, [vv1] + layer_changes_by_node[node], True, None)
                #s.cnstr_implies_disj(vv0, False, [vv1] + layer_changes_by_node[node], [False] + [True] * len(layer_changes_by_node[node]), None)

        for edge in vars_edge_by_id_by_label_etc:
            for dynamic_edge_label in dynamic_edge_labels:
                vv0 = vars_edge_dynamic_by_layer_by_id[layer + 0][edge][dynamic_edge_label]
                vv1 = vars_edge_dynamic_by_layer_by_id[layer + 1][edge][dynamic_edge_label]
                s.cnstr_implies_disj(vv0, True, [vv1] + layer_changes_by_edge[edge], True, None)
                #s.cnstr_implies_disj(vv0, False, [vv1] + layer_changes_by_edge[edge], [False] + [True] * len(layer_changes_by_edge[edge]), None)



    # count constraints
    def _add_count_cnstr(_ids, _vv_map, _labels, _count):
        if type(_labels) == tuple:
            _vvs = [_vv_map[_id][_label] for _id in _ids for _label in _labels]
        else:
            _vvs = [_vv_map[_id][_labels] for _id in _ids]
        _count = _count(len(_vvs)) if callable(_count) else _count
        _lo, _hi = _count if type(_count) == tuple else (_count, _count)
        _hi = len(_vvs) if _hi is None else _hi
        s.cnstr_count(_vvs, True, _lo, _hi, None)

    for static_labels, count in mkiv_info.static_node_count.items():
        _add_count_cnstr(vars_node_by_id.keys(), vars_node_static_by_id, static_labels, count)

    for dynamic_labels, count in mkiv_info.dynamic_node_init_count.items():
        _add_count_cnstr(vars_node_by_id.keys(), vars_node_dynamic_by_layer_by_id[0], dynamic_labels, count)

    for dynamic_labels, count in mkiv_info.dynamic_node_fini_count.items():
        _add_count_cnstr(vars_node_by_id.keys(), vars_node_dynamic_by_layer_by_id[mkiv_info.layers - 1], dynamic_labels, count)

    for dynamic_labels, count in mkiv_info.dynamic_edge_fini_count.items():
        _add_count_cnstr(vars_edge_by_id_by_label_etc.keys(), vars_edge_dynamic_by_layer_by_id[mkiv_info.layers - 1], dynamic_labels, count)

    # implies constraints
    for static_label, dynamic_label in mkiv_info.static_implies_dynamic_fini:
        for node in vars_node_by_id:
            static_var = vars_node_static_by_id[node][static_label]
            dynamic_var = vars_node_dynamic_by_layer_by_id[mkiv_info.layers - 1][node][dynamic_label]
            s.cnstr_implies_disj(static_var, True, [dynamic_var], True, None)

    for dynamic_label, static_label in mkiv_info.dynamic_implies_static_fini:
        for node in vars_node_by_id:
            dynamic_var = vars_node_dynamic_by_layer_by_id[mkiv_info.layers - 1][node][dynamic_label]
            static_var = vars_node_static_by_id[node][static_label]
            s.cnstr_implies_disj(dynamic_var, True, [static_var], True, None)

    layers = mkiv_info.layers
    return s, layers, vars_term, vars_node_static_by_id, vars_node_dynamic_by_layer_by_id, vars_edge_static_by_id, vars_edge_dynamic_by_layer_by_id, changes_by_layer



def update_result(mkiv_tuple, result_info):
    s, layers, vars_term, vars_node_static_by_id, vars_node_dynamic_by_layer_by_id, vars_edge_static_by_id, vars_edge_dynamic_by_layer_by_id, changes_by_layer = mkiv_tuple

    util_common.check(len(result_info.graphs.graphs) == 1, 'only one graph expected')
    util_common.check(result_info.playthrough_info is None, 'playthrough already set')

    relabel_first = False

    result_info.playthrough_info = []

    first_graph = result_info.graphs.graphs[0]

    static_node_labels = {}
    for node, vvs in vars_node_static_by_id.items():
        static_node_labels[node] = util_solvers.get_one_set(s, vvs)

    static_edge_labels = {}
    for edge, vvs in vars_edge_static_by_id.items():
        static_edge_labels[edge] = util_solvers.get_one_set(s, vvs)

    prev_dynamic_node_labels = {}
    prev_dynamic_edge_labels = {}
    prev_term = False
    for layer in range(layers):
        is_term = vars_term[layer] is not None and s.get_var(vars_term[layer])
        util_common.check(not prev_term or is_term, 'term unset')

        mapping = {node:str(layer) + '__' + str(node) for node in vars_node_static_by_id}
        for edge in vars_edge_static_by_id:
            mapping[edge] = mapping[edge[0]], mapping[edge[1]]

        layer_graph = nx.relabel_nodes(first_graph, mapping)
        nx.set_node_attributes(layer_graph, None, util_graph.GATTR_LABEL)
        nx.set_node_attributes(layer_graph, False, util_graph.GATTR_CENTRAL)
        nx.set_edge_attributes(layer_graph, None, util_graph.GATTR_LABEL)
        nx.set_edge_attributes(layer_graph, False, util_graph.GATTR_CENTRAL)

        step = util_graph.GraphPlaythroughStepInfo()
        step.term = is_term
        step.first_term = is_term and not prev_term
        step.graphs = util_graph.Graphs()
        step.graphs.gtype = result_info.graphs.gtype
        step.graphs.colors = result_info.graphs.colors
        step.graphs.graphs = [layer_graph]

        result_info.playthrough_info.append(step)

        for node, vvs in vars_node_dynamic_by_layer_by_id[layer].items():
            static_node_label = static_node_labels[node]
            dynamic_node_label = util_solvers.get_one_set(s, vvs)

            if dynamic_node_label != None:
                util_common.check(node in first_graph.nodes, 'node appeared')

                if is_term:
                    if node in prev_dynamic_node_labels:
                        util_common.check(dynamic_node_label == prev_dynamic_node_labels[node], 'label changed after terminal')
                    if not prev_term and is_term and relabel_first:
                        first_graph.nodes[node][util_graph.GATTR_LABEL] += '|'
                elif relabel_first:
                    first_graph.nodes[node][util_graph.GATTR_LABEL] += '\\n' if layer == 0 else ';'
                    first_graph.nodes[node][util_graph.GATTR_LABEL] += dynamic_node_label

                layer_graph.nodes[mapping[node]][util_graph.GATTR_LABEL] = make_label(static_node_label, dynamic_node_label)

            else:
                util_common.check(node not in first_graph.nodes, 'node disappeared')

            prev_dynamic_node_labels[node] = dynamic_node_label

        for edge, vvs in vars_edge_dynamic_by_layer_by_id[layer].items():
            static_edge_label = static_edge_labels[edge]
            dynamic_edge_label = util_solvers.get_one_set(s, vvs)

            if dynamic_edge_label != None:
                util_common.check(edge in first_graph.edges, 'edge appeared')

                if is_term:
                    if edge in prev_dynamic_edge_labels:
                        util_common.check(dynamic_edge_label == prev_dynamic_edge_labels[edge], 'label changed after terminal')
                    if not prev_term and is_term and relabel_first:
                        first_graph.edges[edge][util_graph.GATTR_LABEL] += '|'
                elif relabel_first:
                    first_graph.edges[edge][util_graph.GATTR_LABEL] += '\\n' if layer == 0 else ';'
                    first_graph.edges[edge][util_graph.GATTR_LABEL] += dynamic_edge_label

                layer_graph.edges[mapping[edge]][util_graph.GATTR_LABEL] = make_label(static_edge_label, dynamic_edge_label)

            else:
                util_common.check(edge not in first_graph.edges, 'edge disappeared')

            prev_dynamic_edge_labels[edge] = dynamic_edge_label

        if layer != 0:
            for change_vars, change_nodes, change_edges in changes_by_layer[layer - 1]:
                if util_solvers.are_all_set(s, change_vars):
                    for node in change_nodes:
                        layer_graph.nodes[mapping[node]][util_graph.GATTR_CENTRAL] = True
                    for fra, til in change_edges:
                        layer_graph.edges[(mapping[fra], mapping[til])][util_graph.GATTR_CENTRAL] = True

        prev_term = is_term



def save_graph_result_info_mkiv(result_info, no_dot, prefix):
    util_common.check(result_info.playthrough_info is not None, 'playthrough not set')

    play_folder = prefix + '_play'
    print('writing playthrough levels to', play_folder)
    if os.path.exists(play_folder):
        shutil.rmtree(play_folder)
    os.makedirs(play_folder)

    for ii, step_info in enumerate(result_info.playthrough_info):
        descr = ['term' if step_info.term else 'step']

        step_prefix = play_folder + ('/%02d_' % ii) + '_'.join(descr) + '_play'

        util_graph.save_graph_gr_dot(step_info.graphs, no_dot, step_prefix)
