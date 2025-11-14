import itertools, os, shutil, sys
import util_common, util_graph, util_solvers
import networkx as nx



EX_DORMANS               = 'dormans'
EX_DORMANS_RUN           = 'dormans-run'
EX_DORMANS_SLOT_RUN      = 'dormans-slot-run'
EX_DORMANS_MINI_RUN      = 'dormans-mini-run'
EX_GEN_DAG               = 'gen-dag'
EX_GEN_RUN_DAG           = 'gen-run-dag'
EX_GEN_DAG_CHAIN         = 'gen-dag-chain'
EX_GEN_DAG_MULTI         = 'gen-dag-multi'
EX_GEN_DAG_FORCE         = 'gen-dag-force'
EX_GEN_DAG_INTER_HINT    = 'gen-dag-inter-hint'
EX_GEN_DAG_INTER_NOHINT  = 'gen-dag-inter-nohint'

EX_VISIT_NODE            = 'visit-node'
EX_VISIT_EDGE            = 'visit-edge'
EX_COLOR                 = 'color'
EX_PEBBLE                = 'pebble'
EX_GEN_PEBBLE            = 'gen-pebble'
EX_LIGHTS                = 'lightsout'
EX_MAZE                  = 'maze'
EX_SOKO                  = 'soko'
EX_ADVENTURE_A           = 'adventure-a'
EX_ADVENTURE_B           = 'adventure-b'
EX_CODEMASTER_NOBRANCH   = 'codemaster-nobranch'
EX_CODEMASTER_BRANCH     = 'codemaster-branch'

EXAMPLES = [
    EX_DORMANS, EX_DORMANS_RUN, EX_DORMANS_SLOT_RUN, EX_DORMANS_MINI_RUN,
    EX_GEN_DAG, EX_GEN_RUN_DAG, EX_GEN_DAG_CHAIN, EX_GEN_DAG_MULTI, EX_GEN_DAG_FORCE, EX_GEN_DAG_INTER_HINT, EX_GEN_DAG_INTER_NOHINT,
    EX_VISIT_NODE, EX_VISIT_EDGE,
    EX_COLOR, EX_PEBBLE, EX_GEN_PEBBLE, EX_LIGHTS, EX_MAZE, EX_SOKO, EX_ADVENTURE_A, EX_ADVENTURE_B, EX_CODEMASTER_NOBRANCH, EX_CODEMASTER_BRANCH
]



LABEL_GEN_STATIC    = util_graph.LABEL_GEN_STATIC
LABEL_GEN_DYN_START = util_graph.LABEL_GEN_DYN_START
LABEL_GEN_DYN_NIL   = util_graph.LABEL_GEN_DYN_NIL

LABEL_GEN_START     = LABEL_GEN_STATIC + ':' + LABEL_GEN_DYN_START
LABEL_GEN_NIL       = LABEL_GEN_STATIC + ':' + LABEL_GEN_DYN_NIL

LABEL_RULE_NOT      = util_graph.LABEL_RULE_NOT



RULE_LAYER          = '__LAYER'
RULE_CHAIN          = '__CHAIN'



class MKIVSetup:
    def __init__(self):
        self.example = None
        self.layers = None

class MKIVInfo:
    def __init__(self):
        self.rep_rules = None

        self.layers = None

        self.layer_hint_labels_node = None
        self.id_hint_labels_node = None

        self.directed = None

        self.multi_allow = None
        self.multi_layer_allow_none = None
        self.multi_layer_force_any = None

        self.static_label_all = None

        self.static_node_count = None
        self.dynamic_node_init_count = None
        self.dynamic_node_step_count = None
        self.dynamic_node_fini_count = None
        self.dynamic_edge_fini_count = None

        self.static_implies_dynamic_fini = None
        self.dynamic_implies_static_fini = None

def get_example_info(mkiv_setup):
    ei = MKIVInfo()

    ei.rep_rules = []

    ei.layers = mkiv_setup.layers

    ei.layer_hint_labels_node = None
    ei.id_hint_labels_node = None

    ei.directed = False

    ei.multi_allow = False
    ei.multi_layer_allow_none = {}
    ei.multi_layer_force_any = {}

    ei.static_label_all = None

    ei.static_node_count = {}
    ei.dynamic_node_init_count = {}
    ei.dynamic_node_step_count = {}
    ei.dynamic_node_fini_count = {}
    ei.dynamic_edge_fini_count = {}

    ei.static_implies_dynamic_fini = {}
    ei.dynamic_implies_static_fini = {}

    def _organize_rep_rules(_rep_rules, _static_label_all):
        _rules = []

        _layer_hint_lo, _layer_hint_hi = None, None
        _chain = None

        for _rule in _rep_rules:
            if _rule[0] == RULE_LAYER:
                _layer_hint_lo = _rule[1]
                _layer_hint_hi = _rule[2]
                util_common.check(_layer_hint_lo is None or _layer_hint_lo >= 0, 'layer')
                util_common.check(_layer_hint_hi is None or _layer_hint_hi >= 1, 'layer')
                util_common.check(_layer_hint_lo is None or _layer_hint_hi is None or _layer_hint_lo < _layer_hint_hi, 'layer')

            elif _rule[0] == RULE_CHAIN:
                _chain = _rule[1]

            else:
                _nodes0, _edges0, _nodes1, _edges1 = _rule
                _nodes, _edges = [], []

                util_common.check(len(_nodes0) == len(_nodes1), 'length mismatch')
                for _node_label0, _dynamic_node_label1 in zip(_nodes0, _nodes1):
                    if _static_label_all is None:
                        _static_node_label, _dynamic_node_label0 = _node_label0
                    else:
                        _static_node_label = _static_label_all
                        _dynamic_node_label0 = _node_label0
                    _nodes.append((_static_node_label, _dynamic_node_label0, _dynamic_node_label1))

                util_common.check(len(_edges0) == len(_edges1), 'length mismatch')
                for edge_fra_til_label0, _dynamic_edge_label1 in zip(_edges0, _edges1):
                    if _static_label_all is None:
                        _fra, _til, _static_edge_label, _dynamic_edge_label0 = edge_fra_til_label0
                        _ind_hint_lo, _ind_hint_hi = None, None
                    else:
                        _static_edge_label = _static_label_all
                        if len(edge_fra_til_label0) == 3:
                            _fra, _til, _dynamic_edge_label0 = edge_fra_til_label0
                            _ind_hint_lo, _ind_hint_hi = None, None
                        else:
                            _fra, _til, _ind_hint_lo, _ind_hint_hi, _dynamic_edge_label0 = edge_fra_til_label0
                    _edges.append((_fra, _til, _ind_hint_lo, _ind_hint_hi, _static_edge_label, _dynamic_edge_label0, _dynamic_edge_label1))

                _rules.append((_layer_hint_lo, _layer_hint_hi, _chain, _nodes, _edges))
                _chain = None

        return _rules

    def _check_rep_rules_subiso(_directed, _rep_rules):
        _nm = nx.algorithms.isomorphism.categorical_node_match([util_graph.GATTR_LABEL], [None])
        _em = nx.algorithms.isomorphism.categorical_edge_match([util_graph.GATTR_LABEL], [None])

        if _directed:
            _class_graph = nx.DiGraph
            _class_match = nx.algorithms.isomorphism.DiGraphMatcher
        else:
            _class_graph = nx.Graph
            _class_match = nx.algorithms.isomorphism.GraphMatcher

        _graphs = []
        for _layer_hint_lo, _layer_hint_hi, _chain, _nodes, _edges in _rep_rules:
            _gr = _class_graph()
            for _node, (_static_node_label, _dynamic_node_label0, _dynamic_node_label1) in enumerate(_nodes):
                _gr.add_node(_node)
                _gr.nodes[_node][util_graph.GATTR_LABEL] = (_static_node_label, _dynamic_node_label0, _dynamic_node_label1)
            for _fra, _til, _ind_hint_lo, _ind_hint_hi, _static_edge_label, _dynamic_edge_label0, _dynamic_edge_label1 in _edges:
                _gr.add_edge(_fra, _til)
                _gr.edges[(_fra, _til)][util_graph.GATTR_LABEL] = (_static_edge_label, _dynamic_edge_label0, _dynamic_edge_label1)
            _graphs.append(_gr)

        for _ii, _gr_main in enumerate(_graphs):
            for _jj, _gr_sub in enumerate(_graphs):
                if _ii == _jj:
                    continue
                _matcher = _class_match(_gr_main, _gr_sub, node_match=_nm, edge_match=_em)
                if _matcher.subgraph_is_isomorphic():
                    _gtype = util_graph.GTYPE_DGRAPH if _directed else util_graph.GTYPE_UGRAPH
                    util_graph.write_graph_gr_single(_gr_main, _gtype, sys.stdout)
                    util_graph.write_graph_gr_single(_gr_sub, _gtype, sys.stdout)
                    util_common.check(False, 'rep rule subgraph isomorphism')



    STR = LABEL_GEN_DYN_START
    NIL = LABEL_GEN_DYN_NIL



    if mkiv_setup.example in [EX_DORMANS, EX_DORMANS_RUN, EX_DORMANS_SLOT_RUN, EX_DORMANS_MINI_RUN]:
        ei.directed = True
        ei.multi_allow = True

        ei.static_label_all = LABEL_GEN_STATIC

        use_mini = mkiv_setup.example in [EX_DORMANS_MINI_RUN]
        use_slot = mkiv_setup.example in [EX_DORMANS_SLOT_RUN]

        TBL = 'bl'
        TBM = 'bm'
        TIB = 'ib'
        TN_ = 'n'
        TT_ = 't'
        TTS = 'ts'

        TK_ = 'k'
        TKF = 'kf'
        TKM = 'km'
        TL_ = 'l'
        TLF = 'lf'
        TLM = 'lm'

        TIQ = 'iq'
        TTI = 'ti'

        TE_ = 'e'
        TG_ = 'g'

        NC_ = 'C'
        NCF = 'CF'
        NCL = 'CL'
        NCP = 'CP'
        NF_ = 'F'
        NG_ = 'G'
        NH_ = 'H'

        NXX = 'XX'

        NSL = 'SL'

        if use_mini:
            NODES_TERM_GENERIC = [TN_]
            NODES_TERM = NODES_TERM_GENERIC + [TK_, TL_] + [TE_, TG_]
            NODES_NONTERM = [NC_, NSL]
        else:
            NODES_TERM_GENERIC = [TBL, TBM, TIB, TN_, TT_, TTS]
            NODES_TERM = NODES_TERM_GENERIC + [TK_, TKF, TL_, TLF, TLM] + [TIQ, TTI] + [TE_, TG_] + ([TKM] if not use_slot else [])
            NODES_NONTERM = [NC_, NCF, NCL, NCP, NF_, NG_, NH_] + [NXX]

        if use_slot:
            SN_ = NSL
            SK_ = NSL
            SKM = NSL
            SKF = NSL
            SIQ = NSL

            RESOLVE_SLOTS = [TN_, TK_, TKF, TIQ]
            NODES_NONTERM.append(NSL)

        else:
            SN_ = TN_
            SK_ = TK_
            SKM = TKM
            SKF = TKF
            SIQ = TIQ

        ED1 = '-'
        ED2 = '='

        if mkiv_setup.example in [EX_DORMANS]:
            layer_gen_max = None

            ei.dynamic_node_fini_count[STR] = 0
            for label in NODES_NONTERM:
                ei.dynamic_node_fini_count[label] = 0

        else:
            if use_mini:
                layer_gen_max = 3
            else:
                layer_gen_max = 7

            ei.dynamic_node_step_count[(STR, layer_gen_max)] = 0
            for label in NODES_NONTERM:
                ei.dynamic_node_step_count[(label, layer_gen_max)] = 0

            for layer in range(layer_gen_max + 1):
                ei.multi_layer_allow_none[layer] = None

        if use_mini:
            ei.rep_rules.append((RULE_LAYER, 0, 1))

            ei.rep_rules.append(([STR, NIL, NIL, NIL, NIL, NIL],
                                 [(0, 1, 1, 1, NIL), (1, 2, 4, 6, NIL), (2, 3,  1,  1, NIL), (3, 4, 4, 6, NIL), (4, 5, 1, 1, NIL)],
                                 [TE_, NC_, TL_, NC_, TL_, TG_],
                                 [ED1, ED1, ED2, ED1, ED2]))

            ei.rep_rules.append((RULE_LAYER, 1, layer_gen_max))

            ei.rep_rules.append(([NC_, NIL, TL_], [(0, 2, 4, 6, ED1), (0, 1, 2, 4, NIL), (1, 2, 2, 4, NIL)],
                                 [NSL, NSL, TL_], [             NIL,               ED2,               ED2 ]))
            ei.rep_rules.append(([NC_, NIL, NIL, NIL, TL_],
                                 [(0, 4, 4, 6, ED1),
                                  (0, 1, 1, 4, NIL), (1, 4, 1, 4, NIL), (0, 2, 1, 4, NIL), (2, 4, 1, 4, NIL), (0, 3, 1, 4, NIL), (3, 4, 1, 4, NIL)],
                                 [NSL, NSL, NSL, NSL, TL_],
                                 [NIL, ED1, ED1, ED1, ED1, ED1, ED2]))

            ei.rep_rules.append(([NSL], [],
                                 [TK_], []))
            ei.rep_rules.append(([NSL], [],
                                 [TN_], []))

        else:
            # from https://dl.acm.org/doi/10.1145/1814256.1814257

            # start rule
            ei.rep_rules.append((RULE_LAYER, 0, 1))

            ei.rep_rules.append(([STR, NIL, NIL, NIL, NIL, NIL, NIL, NIL],
                                 [(0, 1, 1, 1, NIL), (1, 2, 14, 14, NIL), (2, 3,  1,  1, NIL), (3, 4, 1, 1, NIL),
                                  (4, 5, 1, 1, NIL), (5, 6,  1,  1, NIL), (6, 7, 21, 21, NIL)],
                                 [TE_, NC_, NG_, TBM, SIQ, TTI, NCF, TG_],
                                 [ED1, ED1, ED2, ED2, ED2, ED2, ED1]))

            # create final chain
            ei.rep_rules.append((RULE_LAYER, 1, 2))

            ei.rep_rules.append(([NCF, NIL, NIL, NIL, NIL, NIL, NIL, NIL, TG_],
                                 [(0, 8, 21, 21, ED1),
                                  (0, 1, 15, 15, NIL), (0, 2, 17, 17, NIL), (0, 3, 14, 14, NIL),
                                  (2, 4, 1, 5, NIL), (2, 5, 1, 5, NIL),
                                  (3, 6, 1, 5, NIL),
                                  (4, 6, 1, 5, NIL),
                                  (6, 7, 1, 1, NIL),
                                  (7, 8, 1, 1, NIL)],
                                 [NC_, NH_, TT_, NG_, SKF, NH_, TLF, TBL, TG_],
                                 [NIL,
                                  ED1, ED1, ED1,
                                  ED2, ED1,
                                  ED2,
                                  ED1,
                                  ED2,
                                  ED2]))

            # remaining gen rules
            ei.rep_rules.append((RULE_LAYER, 2, layer_gen_max))

            # create linear chain
            ei.rep_rules.append(([NC_, NIL, NG_], [(0, 2, 14, 14, ED1), (0, 1, 6, 8, NIL), (1, 2, 6, 8, NIL)],
                                 [NCL, NCL, NCL], [               NIL,               ED2,               ED2]))
            ei.rep_rules.append(([NC_, NIL, NIL, NG_], [(0, 3, 14, 14, ED1), (0, 1, 3, 5, NIL), (1, 2, 3, 5, NIL), (2, 3, 3, 5, NIL)],
                                 [NCL, NCL, NCL, NCL], [               NIL,               ED2,               ED2,               ED2]))
            ei.rep_rules.append(([NC_, NIL, NIL, NIL, NG_],
                                 [(0, 4, 14, 14, ED1), (0, 1, 2, 4, NIL), (1, 2, 2, 4, NIL), (2, 3, 2, 4, NIL), (3, 4, 2, 4, NIL)],
                                 [NCL, NCL, NCL, NCL, NCL],
                                 [NIL, ED2, ED2, ED2, ED2]))

            ei.rep_rules.append(([NCL], [],
                                 [NXX], []))
            ei.rep_rules.append(([NXX], [], # remove subgraph isomorphism
                                 [TT_], []))
            ei.rep_rules.append(([NCL, NIL, NIL], [(0, 1, 1, 2, NIL), (1, 2, 1, 2, NIL)],
                                 [TT_, TT_, TIB], [             ED2,               ED2]))
            ei.rep_rules.append(([NCL], [],
                                 [TTS], []))
            ei.rep_rules.append(([NCL, NCL], [(0, 1, 2, 6, ED2)],
                                 [SK_, TL_], [             ED2]))
            ei.rep_rules.append(([NCL, NIL, NCL], [(0, 2, 2, 6, ED2), (0, 1, 1, 2, NIL), (1, 2, 1, 2, NIL)],
                                 [SK_, TL_, NCL], [             NIL,               ED2,               ED2]))

            # create parallel chain
            ei.rep_rules.append(([NC_, NG_], [(0, 1, 14, 14, ED1)],
                                 [NCP, NG_], [               ED1]))
            ei.rep_rules.append(([NCP, NIL, NIL, NIL, NG_],
                                 [(0, 4, 14, 14, ED1),
                                  (0, 1, 5, 9, NIL), (1, 4, 5, 9, NIL), (0, 2, 5, 9, NIL), (2, 4, 5, 9, NIL), (0, 3, 5, 9, NIL), (3, 4, 5, 9, NIL)],
                                 [NF_, SKM, SKM, SKM, TLM],
                                 [NIL, ED1, ED1, ED1, ED1, ED1, ED1 if not use_slot else ED2]))
            ei.rep_rules.append(([NF_, NIL, NIL, NIL, SKM], [(0, 3, 5, 9, ED1), (0, 1, 1, 2, NIL), (1, 2, 1, 2, NIL), (2, 4, 4, 7, NIL), (2, 3, 1, 2, NIL)],
                                 [NF_, SK_, TL_, NH_, SKM], [             NIL,               ED1,               ED1,               ED2,               ED2]))

            if not use_slot:
                ei.rep_rules.append(([NF_, NIL, SKM], [(0, 2, 5, 9, ED1), (0, 1, 1, 2, NIL), (1, 2, 1, 2, NIL)],
                                     [NF_, TT_, SKM], [             NIL,               ED1,               ED2]))
                ei.rep_rules.append(([NF_, NIL, SKM], [(0, 2, 5, 9, ED1), (0, 1, 1, 2, NIL), (1, 2, 1, 2, NIL)],
                                     [NF_, TTS, SKM], [             NIL,               ED1,               ED2]))
            ei.rep_rules.append(([NF_, NIL, SK_], [(0, 2, 5, 9, ED1), (0, 1, 1, 2, NIL), (1, 2, 1, 2, NIL)],
                                 [NF_, TT_, SK_], [             NIL,               ED1,               ED2]))
            ei.rep_rules.append(([NF_, NIL, SK_], [(0, 2, 5, 9, ED1), (0, 1, 1, 2, NIL), (1, 2, 1, 2, NIL)],
                                 [NF_, TTS, SK_], [             NIL,               ED1,               ED2]))
            ei.rep_rules.append(([NF_, NIL, NIL], [(0, 1, 1, 5, NIL), (0, 2, 1, 5, NIL)],
                                 [SN_, NH_, NH_], [             ED1,               ED1]))

            # resolve hooks
            ei.rep_rules.append(([NH_], [],
                                 [SN_], []))
            ei.rep_rules.append(([NH_, NIL], [(0, 1, 1, 2, NIL)],
                                 [TT_, TIB], [             ED2]))
            ei.rep_rules.append(([NH_, NIL], [(0, 1, 1, 2, NIL)],
                                 [TTS, TIB], [             ED2]))

            if use_slot:
                # resolve slots
                for slt in RESOLVE_SLOTS:
                    ei.rep_rules.append(([NSL], [],
                                         [slt], []))

        if mkiv_setup.example in [EX_DORMANS_RUN, EX_DORMANS_SLOT_RUN, EX_DORMANS_MINI_RUN]:
            EKR = -0
            EKF = -1
            EIQ = -2
            INV_MAX = 2

            EDI = 'i'
            EDO = '.'
            EDX = 'x'

            if not use_mini:
                KEY_SLOTS = ['_', '1', '2', '3', '4']
            else:
                KEY_SLOTS = ['_', '1', '2']
            ITEM_SLOTS = ['_', 'X']

            NODES_RUN_MOVE = []
            NODES_RUN_MOVE.append('_')
            NODES_RUN_MOVE.append('@')

            NODES_RUN_INV = []
            for sl in KEY_SLOTS:
                NODES_RUN_INV.append('k:' + sl)
            if not use_mini:
                for sl in ITEM_SLOTS:
                    NODES_RUN_INV.append('kf:' + sl)
                for sl in ITEM_SLOTS:
                    NODES_RUN_INV.append('iq:' + sl)

            # mark edges parallel to double edges
            ei.rep_rules.append((RULE_LAYER, layer_gen_max, layer_gen_max + 1))
            ei.multi_layer_allow_none[layer_gen_max] = None
            ei.multi_layer_force_any[layer_gen_max] = None

            ei.rep_rules.append(([None, None, None], [(0, 2, 1, 20, ED1), (1, 2, 1, 20, ED2)],
                                 [None, None, None], [              EDX,                ED2]))

            # mark other edges
            ei.rep_rules.append((RULE_LAYER, layer_gen_max + 1, layer_gen_max + 2))
            ei.multi_layer_allow_none[layer_gen_max + 1] = None
            ei.multi_layer_force_any[layer_gen_max + 1] = None

            ei.rep_rules.append(([None, None], [(0, 1, 1, 20, ED1)],
                                 [None, None], [              EDO]))
            ei.rep_rules.append(([None, None], [(0, 1, 1, 20, ED2)],
                                 [None, None], [              EDO]))

            # enter dungeon
            if not use_mini:
                ei.rep_rules.append((RULE_LAYER, layer_gen_max + 2, layer_gen_max + 3))
                ei.rep_rules.append(([NIL,   NIL,    NIL,    TE_], [(0, 3, EKR, None, NIL), (1, 3, EKF, None, NIL), (2, 3, EIQ, None, NIL)],
                                     ['k:_', 'kf:_', 'iq:_', '@'], [                  EDI,                    EDI,                    EDI]))
            else:
                ei.rep_rules.append((RULE_LAYER, layer_gen_max + 2, layer_gen_max + 3))
                ei.rep_rules.append(([NIL,   TE_], [(0, 1, EKR, None, NIL)],
                                     ['k:_', '@'], [                  EDI ]))

            # remaining run rules
            ei.rep_rules.append((RULE_LAYER, layer_gen_max + 3, None))

            NODES_RUN_GENERIC = ['_'] + NODES_TERM_GENERIC

            # move onto standard nodes
            for nd0 in NODES_RUN_GENERIC:
                ei.rep_rules.append((['@', nd0], [(0, 1, 1, 20, EDO)],
                                     ['_', '@'], [              EDO]))

            # move onto goal
            ei.rep_rules.append((['@', TG_], [(0, 1, 1, 20, EDO)],
                                 ['_', '@'], [              EDO]))

            # move back onto blank
            ei.rep_rules.append((['_', '@'], [(0, 1, 1, 20, EDO)],
                                 ['@', '_'], [              EDO]))

            # key/item pickup
            for ini in range(len(KEY_SLOTS) - 1):
                in0 = 'k:' + KEY_SLOTS[ini]
                in1 = 'k:' + KEY_SLOTS[ini + 1]
                ei.rep_rules.append(([in0, '@', TK_], [(0, 1, EKR, None, NIL), (1, 2, 1, 20, EDO)],
                                     [in1, '_', '@'], [                  NIL,                EDO]))
                if not use_mini and not use_slot:
                    ei.rep_rules.append(([in0, '@', TKM], [(0, 1, EKR, None, NIL), (1, 2, 1, 20, EDO)],
                                         [in1, '_', '@'], [                  NIL,                EDO]))

            if not use_mini:
                for ini in range(len(ITEM_SLOTS) - 1):
                    in0 = 'kf:' + ITEM_SLOTS[ini]
                    in1 = 'kf:' + ITEM_SLOTS[ini + 1]
                    ei.rep_rules.append(([in0, '@', TKF], [(0, 1, EKF, None, NIL), (1, 2, 1, 20, EDO)],
                                         [in1, '_', '@'], [                  NIL,                EDO]))

                for ini in range(len(ITEM_SLOTS) - 1):
                    in0 = 'iq:' + ITEM_SLOTS[ini]
                    in1 = 'iq:' + ITEM_SLOTS[ini + 1]
                    ei.rep_rules.append(([in0, '@', TIQ], [(0, 1, EIQ, None, NIL), (1, 2, 1, 20, EDO)],
                                         [in1, '_', '@'], [                  NIL,                EDO]))

            # key/item use
            for ini in range(1, len(KEY_SLOTS)):
                in0 = 'k:' + KEY_SLOTS[ini]
                in1 = 'k:' + KEY_SLOTS[ini - 1]
                ei.rep_rules.append(([in0, '@', TL_], [(0, 1, EKR, None, NIL), (1, 2, 1, 20, EDO)],
                                     [in1, '_', '@'], [                  NIL,                EDO]))

            if not use_mini:
                for ini in range(3, len(KEY_SLOTS)):
                    in0 = 'k:' + KEY_SLOTS[ini]
                    in1 = 'k:' + KEY_SLOTS[ini - 3]
                    ei.rep_rules.append(([in0, '@', TLM], [(0, 1, EKR, None, NIL), (1, 2, 1, 20, EDO)],
                                         [in1, '_', '@'], [                  NIL,                EDO]))

                for ini in range(1, len(ITEM_SLOTS)):
                    in0 = 'kf:' + ITEM_SLOTS[ini]
                    in1 = 'kf:' + ITEM_SLOTS[ini - 1]
                    ei.rep_rules.append(([in0, '@', TLF], [(0, 1, EKF, None, NIL), (1, 2, 1, 20, EDO)],
                                         [in1, '_', '@'], [                  NIL,                EDO]))

                for ini in range(1, len(ITEM_SLOTS)):
                    in0 = 'iq:' + ITEM_SLOTS[ini]
                    in1 = 'iq:' + ITEM_SLOTS[ini] # keep item
                    ei.rep_rules.append(([in0, '@', TTI], [(0, 1, EIQ, None, NIL), (1, 2, 1, 20, EDO)],
                                         [in1, '_', '@'], [                  NIL,                EDO]))

            # setup node labels
            ei.layer_hint_labels_node = {}
            ei.layer_hint_labels_node[STR] = (0, 1)
            for label in NODES_NONTERM:
                ei.layer_hint_labels_node[label] = (0, layer_gen_max)

            ei.id_hint_labels_node = {}
            for label in NODES_RUN_INV:
                ei.id_hint_labels_node[label] = (0, INV_MAX)
            for label in NODES_RUN_MOVE + NODES_TERM + NODES_NONTERM + [STR]:
                ei.id_hint_labels_node[label] = (INV_MAX + 1, None)

            # setup run counts
            ei.dynamic_node_fini_count[TG_] = 0

    elif mkiv_setup.example == EX_GEN_DAG:
        ei.directed = True

        ei.static_label_all = LABEL_GEN_STATIC

        ei.rep_rules.append(([STR, NIL], [(0, 1, NIL)],
                             ['_', '_'], [       '_' ]))
        ei.rep_rules.append((['_', '_', NIL], [(0, 1, '_'), (0, 2, NIL), (2, 1, NIL)],
                             ['_', '_', '_'], [       NIL,         '_',         '_' ]))
        ei.rep_rules.append((['_', '_', NIL, NIL], [(0, 1, '_'), (1, 3, NIL), (0, 2, NIL), (2, 3, NIL)],
                             ['_', '_', '_', '_'], [       '_',         '_',         '_',         '_' ]))
        ei.dynamic_node_fini_count = {'_':lambda nvars: nvars}

    elif mkiv_setup.example == EX_GEN_RUN_DAG:
        ei.directed = True

        ei.static_label_all = LABEL_GEN_STATIC

        switch_layer = 4

        ei.rep_rules.append((RULE_LAYER, 0, 1))
        ei.rep_rules.append(([STR, NIL], [(0, 1, NIL)],
                             ['P', '*'], [       '_' ]))

        ei.rep_rules.append((RULE_LAYER, 1, switch_layer))
        for src in ['P', '*', '_']:
            for dst in ['*', '_']:
                ei.rep_rules.append(([src, dst, NIL], [(0, 1, '_'), (0, 2, NIL), (2, 1, NIL)],
                                     [src, dst, '*'], [       NIL,         '_',         '_' ]))
                ei.rep_rules.append(([src, dst, NIL, NIL], [(0, 1, '_'), (1, 3, NIL), (0, 2, NIL), (2, 3, NIL)],
                                     [src, '*', '_', dst], [       '_',         '_',         '_',         '_' ]))

        ei.rep_rules.append((RULE_LAYER, switch_layer, None))
        ei.rep_rules.append((['P', '_'], [(0, 1, '_')],
                             ['=', 'P'], [       '_' ]))
        ei.rep_rules.append((['P', '*'], [(0, 1, '_')],
                             ['=', 'P'], [       '_' ]))

        ei.layer_hint_labels_node = {}
        ei.layer_hint_labels_node[STR] = (0, 1)
        ei.layer_hint_labels_node['='] = (switch_layer, None)

        ei.dynamic_node_fini_count = {('_', '='):lambda nvars: (nvars // 2 - 1, None), '*':0}

    elif mkiv_setup.example == EX_GEN_DAG_CHAIN:
        ei.directed = True

        ei.static_label_all = LABEL_GEN_STATIC

        ei.rep_rules.append(([STR, NIL], [(0, 1, NIL)],
                             ['A', 'X'], [       '_' ]))
        ei.rep_rules.append((RULE_CHAIN, 1))
        ei.rep_rules.append((['X', NIL], [(0, 1, NIL)],
                             ['B', 'X'], [       '_' ]))
        ei.rep_rules.append((RULE_CHAIN, 1))
        ei.rep_rules.append((['X', NIL], [(0, 1, NIL)],
                             ['C', 'X'], [       '_' ]))
        ei.rep_rules.append((RULE_CHAIN, 1))
        ei.rep_rules.append((['X', NIL], [(0, 1, NIL)],
                             ['D', 'X'], [       '_' ]))
        ei.rep_rules.append((RULE_CHAIN, 1))
        ei.rep_rules.append((['X'], [],
                             ['E'], []))

        ei.dynamic_node_fini_count[STR] = 0
        ei.dynamic_node_fini_count['X'] = 0

    elif mkiv_setup.example == EX_GEN_DAG_MULTI:
        ei.directed = True
        ei.multi_allow = True

        ei.static_label_all = LABEL_GEN_STATIC

        ei.rep_rules.append(([STR,  NIL,  NIL,  NIL],  [(0, 1, NIL), (1, 2, NIL), (2, 3, NIL)],
                             ['X1', 'X2', 'X3', 'X4'], [       '_',         '_',         '_' ]))
        ei.rep_rules.append((RULE_CHAIN, 1))
        ei.rep_rules.append(([NIL, 'X1'], [(0, 1, NIL)],
                             ['A', 'B'], [       '_' ]))
        ei.rep_rules.append((RULE_CHAIN, 2))
        ei.rep_rules.append((['X2'], [],
                             ['C'],  []))
        ei.rep_rules.append((RULE_CHAIN, 3))
        ei.rep_rules.append((['X3'], [],
                             ['D'],  []))
        ei.rep_rules.append((RULE_CHAIN, 4))
        ei.rep_rules.append((['X4', NIL], [(0, 1, NIL)],
                             ['E',  'F'], [       '_' ]))

        ei.dynamic_node_fini_count[STR] = 0
        ei.dynamic_node_fini_count['X1'] = 0
        ei.dynamic_node_fini_count['X2'] = 0
        ei.dynamic_node_fini_count['X3'] = 0
        ei.dynamic_node_fini_count['X4'] = 0

    elif mkiv_setup.example == EX_GEN_DAG_FORCE:
        ei.directed = True
        ei.multi_allow = True

        ei.static_label_all = LABEL_GEN_STATIC

        ei.rep_rules.append((RULE_LAYER, 0, 1))
        ei.rep_rules.append(([NIL, STR], [(0, 1, NIL)],
                             ['X', 'Y'], [       '-' ]))
        ei.multi_layer_force_any[0] = None

        ei.rep_rules.append((RULE_LAYER, 1, 2))
        ei.rep_rules.append((['X', 'Y'], [(0, 1, '-')],
                             ['X', 'Y'], [       '=' ]))

        ei.rep_rules.append((RULE_LAYER, 2, None))
        ei.rep_rules.append(([None, None, None], [(0, 2, '='), (1, 2, '-')],
                             [None, None, None], [       '.',         'x' ]))
        ei.multi_layer_force_any[2] = None

        ei.dynamic_node_fini_count['X'] = lambda nvars: nvars - 1

    elif mkiv_setup.example in [EX_GEN_DAG_INTER_HINT, EX_GEN_DAG_INTER_NOHINT]:
        ei.directed = True
        ei.multi_allow = True

        ei.static_label_all = LABEL_GEN_STATIC

        if mkiv_setup.example == EX_GEN_DAG_INTER_HINT:
            ei.rep_rules.append(([STR,  NIL ],
                                 [(0, 1, 7, 9, NIL)],
                                 ['X1', 'X2'],
                                 ['_']))
            ei.rep_rules.append((['X1', NIL, NIL, NIL, NIL, NIL, NIL, 'X2'],
                                 [(0, 7, 7, 9, '_'),
                                  (0, 1, 1, 3, NIL), (1, 2, 1, 3, NIL), (2, 3, 1, 3, NIL), (3, 7, 1, 3, NIL),
                                  (0, 4, 1, 3, NIL), (4, 5, 1, 3, NIL), (5, 6, 1, 3, NIL), (6, 7, 1, 3, NIL)],
                                 ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'],
                                 [NIL, '_', '_', '_', '_', '_', '_', '_', '_']))
        else:
            ei.rep_rules.append(([STR,  NIL ],
                                 [(0, 1, NIL)],
                                 ['X1', 'X2'],
                                 ['_']))
            ei.rep_rules.append((['X1', NIL, NIL, NIL, NIL, NIL, NIL, 'X2'],
                                 [(0, 7, '_'),
                                  (0, 1, NIL), (1, 2, NIL), (2, 3, NIL), (3, 7, NIL),
                                  (0, 4, NIL), (4, 5, NIL), (5, 6, NIL), (6, 7, NIL)],
                                 ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'],
                                 [NIL, '_', '_', '_', '_', '_', '_', '_', '_']))

        ei.dynamic_node_fini_count[STR] = 0
        ei.dynamic_node_fini_count['X1'] = 0
        ei.dynamic_node_fini_count['X2'] = 0

    elif mkiv_setup.example == EX_VISIT_NODE:
        ei.directed = True

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

        ei.rep_rules.append(([(None, 'P'), (None, '_')], [(0, 1, None, '_')],
                             [       '_',         'P' ], [             '*']))

        ei.static_node_count = {'S':1}
        ei.dynamic_node_init_count = {'P':1}
        ei.dynamic_edge_fini_count = {'_':0}
        ei.static_implies_dynamic_fini = [('S', 'P')]

    elif mkiv_setup.example == EX_COLOR:
        ei.directed = True

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

        MAX_PEBBLE = 6

        def _pstr(_num):
            return str(_num)

        ei.rep_rules = []
        for src in range(MAX_PEBBLE + 1):
            for dst in range(MAX_PEBBLE):
                if src >= 2:
                    ei.rep_rules.append(([('_', _pstr(src)),    ('_', _pstr(dst))],    [(0, 1, '_', '_')],
                                         [      _pstr(src - 2),       _pstr(dst + 1)], [            '_']))

        ei.dynamic_node_init_count[_pstr(0)] = lambda nvars: nvars // 2
        ei.dynamic_node_fini_count[_pstr(0)] = 0

    elif mkiv_setup.example == EX_GEN_PEBBLE:
        ei.directed = False
        ei.multi_allow = True

        ei.static_label_all = LABEL_GEN_STATIC

        GEN_LAYERS = 5
        MAX_PEBBLE = 6

        def _pstr(_num):
            return str(_num)

        ei.rep_rules.append((RULE_LAYER, 0, GEN_LAYERS))
        ei.rep_rules.append(([STR, NIL], [(0, 1, NIL)],
                             ['X', 'X'], [       '_' ]))
        ei.rep_rules.append((['X', NIL, 'X'], [(0, 2, '_'), (0, 1, NIL), (1, 2, NIL)],
                             ['X', 'X', 'X'], [       NIL,         '_',         '_' ]))
        ei.rep_rules.append((['X', NIL, 'X'], [(0, 2, '_'), (0, 1, NIL), (1, 2, NIL)],
                             ['X', 'X', 'X'], [       '_',         '_',         '_' ]))
        ei.rep_rules.append((['X', NIL, 'X'], [(0, 2, '_'), (0, 1, NIL), (1, 2, NIL)],
                             ['Z', 'Z', 'Z'], [       '_',         '_',         '_' ]))

        ei.rep_rules.append((RULE_LAYER, GEN_LAYERS, GEN_LAYERS + 1))
        ei.rep_rules.append((['Z'],      [],
                             [_pstr(0)], []))
        for num in range(MAX_PEBBLE + 1):
            ei.rep_rules.append((['X'],        [],
                                 [_pstr(num)], []))

        ei.rep_rules.append((RULE_LAYER, GEN_LAYERS + 1, None))

        for src in range(MAX_PEBBLE + 1):
            for dst in range(MAX_PEBBLE):
                if src >= 2:
                    ei.rep_rules.append(([_pstr(src),     _pstr(dst)],     [(0, 1, '_')],
                                         [_pstr(src - 2), _pstr(dst + 1)], [       '_' ]))

        ei.dynamic_node_step_count[(('X', 'Z'), GEN_LAYERS)]     = lambda nvars: nvars // 2
        ei.dynamic_node_step_count[(('X', 'Z'), GEN_LAYERS + 1)] = 0
        ei.dynamic_node_fini_count[_pstr(0)] = 0

    elif mkiv_setup.example == EX_LIGHTS:
        ei.directed = False

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

        ei.rep_rules.append(([(None, 'P'), (None, '_')], [(0, 1, '_', '_')],
                             [       '_',         'P' ], [            '_']))

        ei.static_node_count = {'E':1}
        ei.dynamic_node_init_count = {'P':1}
        ei.static_implies_dynamic_fini = [('E', 'P')]

    elif mkiv_setup.example == EX_SOKO:
        ei.directed = True

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

        def _append_uniq(_rep_rules, _rule):
            if _rule not in _rep_rules:
                _rep_rules.append(_rule)

        for keys in _powerset(all_keys):
            for pows in _powerset(all_pows):
                pla = _pstring(keys + pows)

                for lock in ['_'] + all_keys:
                    for boss in ['_'] + all_pows:
                        if (lock == '_' or lock in keys) and (boss == '_' or boss in pows):
                            lock = lock.upper()
                            boss = boss.upper()

                            _append_uniq(ei.rep_rules, ([(None, pla), ('_', boss)], [(0, 1, lock, '_')],
                                                        [       '_',        pla  ], [             '_']))
                            for pick in all_keys + all_pows:
                                if pick not in keys + pows: # with only one of each pickup, don't need to pick up a second time
                                    plp = _pstring(keys + pows + (pick,))
                                    _append_uniq(ei.rep_rules, ([(None, pla), ('_', pick)], [(0, 1, lock, '_')],
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

    ei.rep_rules = _organize_rep_rules(ei.rep_rules, ei.static_label_all)
    _check_rep_rules_subiso(ei.directed, ei.rep_rules)

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

def write_graph_dot_lightsout(grs, outstream):
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

    util_graph.write_graph_dot(grs_out, True, False, False, 1.0, outstream)

def write_graph_dot_soko(grs, outstream):
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

    util_graph.write_graph_dot(grs_out, True, False, False, 1.0, outstream)

def write_graph_dot_codemaster(grs, outstream):
    util_common.check(len(grs.graphs) == 1, 'can only write single graph')
    gr = grs.graphs[0]

    size = 0.5

    fontsize = 16
    fontsize_per = 2.0
    fontsize_min = 5

    outstream.write(f'digraph G {{\n')
    outstream.write(f'  graph [fontname="Courier New" margin="0"]\n')
    outstream.write(f'  node [fontname="Courier New" fontsize="{fontsize}" shape="circle" width="{size}" height="{size}" fixedsize="true" style="filled" color="none"]\n')
    outstream.write(f'  edge [fontname="Courier New" fontsize="{fontsize}"]\n')

    for node, label, central, pos in util_graph.nodes_and_label_central_pos(gr):
        static_label, dynamic_label = get_static_dynamic_label(label)

        attrs = ''
        if static_label in ['r']:
            attrs += f' label=""'
            attrs += f' style="invis"'
            attrs += f' width="0.0" height="0.0"'
            attrs += f' ordering="out"'
            attrs += f' rank="min"'
            outstream.write(f'  {{rank="source" "{node}"}}\n')
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

            if util_graph.is_central(central):
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

            if util_graph.is_central(central):
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

        outstream.write(f'  "{node}" [{attrs.strip()}]\n')

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
            scroll_edges[(fra, til)] = (None, util_graph.is_central(central))
        elif label in ['sT:_', 'sT:*']:
            scroll_edges[(fra, til)] = (True, util_graph.is_central(central))
        elif label in ['sF:_', 'sF:*']:
            scroll_edges[(fra, til)] = (False, util_graph.is_central(central))
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
                    map_edges[(til, fra, color)] = (True, util_graph.is_central(central) or map_edges[(til, fra, color)][1])
                else:
                    map_edges[(fra, til, color)] = (False, util_graph.is_central(central))

        else:
            util_common.check(False, 'edge label: ' + label)

    for fra, til in list(root_map_edges.keys()) + list(root_scroll_edges.keys()):
        attrs = ''
        attrs += f' label=""'
        attrs += f' style="invis"'
        outstream.write(f'  "{fra}" -> "{til}" [{attrs.strip()}]\n')

    for (fra, til, color), (both, highlight) in map_edges.items():
        attrs = ''
        if highlight:
            attrs += f' penwidth="8"'
        else:
            attrs += f' penwidth="5"'
        if color == 'R':
            attrs += (f' color="#aa0000"' if highlight else f' color="#ffaaaa"')
        elif color == 'G':
            attrs += (f' color="#00aa00"' if highlight else f' color="#aaffaa"')
        elif color == 'B':
            attrs += (f' color="#0000aa"' if highlight else f' color="#aaaaff"')
        if both:
            attrs += f' arrowhead="none"'
        outstream.write(f'  "{fra}" -> "{til}" [{attrs.strip()}]\n')

    for (fra, til), (what, highlight) in scroll_edges.items():
        attrs = ''
        if highlight:
            attrs += f' penwidth="5"'
        else:
            attrs += f' penwidth="2"'
        attrs += (f' color="#000000"' if highlight else f' color="#aaaaaa"')
        if what is None:
            attrs += f' label=""'
        elif what is True:
            attrs += f' label="\u2713"'
        elif what is False:
            attrs += f' label="\u00D7"'
            attrs += f' fontsize="30"'
        outstream.write(f'  "{fra}" -> "{til}" [{attrs.strip()}]\n')

    outstream.write('}\n')



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



def add_mkiv(mkiv_info, s, gtype, mkiv_start_nil, mkiv_rule_index_count, mkiv_label_count_layer, mkiv_match_graph_layer, node_labels, vars_node_by_id, edge_labels_etc, vars_edge_by_id_by_label_etc):
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
            if _dynamic_label1 is not None:
                _dynamic_labels[_dynamic_label1] = None

    for layer_hint_lo, layer_hint_hi, chain, nodes, edges in mkiv_info.rep_rules:
        for static_node_label, dynamic_node_label0, dynamic_node_label1 in nodes:
            update_static_dynamic_labels(static_node_label, dynamic_node_label0, dynamic_node_label1, static_node_labels, dynamic_node_labels)

        for fra, til, ind_hint_lo, ind_hint_hi, static_edge_label, dynamic_edge_label0, dynamic_edge_label1 in edges:
            update_static_dynamic_labels(static_edge_label, dynamic_edge_label0, dynamic_edge_label1, static_edge_labels, dynamic_edge_labels)

    if not mkiv_start_nil:
        static_node_labels[None] = [None]
        dynamic_node_labels[None] = [None]
        static_edge_labels[None] = [None]
        dynamic_edge_labels[None] = [None]



    # conj and disj caches
    def _make_conj_check_dupl(_vvs_and_settings, _cache):
        nonlocal s
        _vvs, _settings = zip(*_vvs_and_settings)
        conj, dupl = util_solvers.make_conj_cache(s, _cache, _vvs, _settings)
        if dupl:
            return None
        else:
            return conj

    conj_cache = {}
    def _make_conj(_vvs_and_settings):
        nonlocal s, conj_cache
        _vvs, _settings = zip(*_vvs_and_settings)
        conj, dupl = util_solvers.make_conj_cache(s, conj_cache, _vvs, _settings)
        return conj

    disj_cache = {}
    def _make_disj(_vvs_and_settings):
        nonlocal s, disj_cache
        _vvs, _settings = zip(*_vvs_and_settings)
        disj, dupl = util_solvers.make_disj_cache(s, disj_cache, _vvs, _settings)
        return disj



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
        return [(_vv, True) for _vv in _ret.keys()]

    # static node variables
    vars_node_static_by_id = {}

    for node in vars_node_by_id:
        vars_node_static_by_id[node] = {}
        for static_node_label, labels in static_node_labels.items():
            if labels is not None:
                vars_node_static_by_id[node][static_node_label] = _make_disj([(vars_node_by_id[node][label], True) for label in labels])
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
                        vars_node_dynamic_by_layer_by_id[layer][node][dynamic_node_label] = _make_disj([(vars_node_by_id[node][label], True) for label in labels])
                    else:
                        vars_node_dynamic_by_layer_by_id[layer][node][dynamic_node_label] = var_false
            else:
                for dynamic_node_label in dynamic_node_labels:
                    if mkiv_info.layer_hint_labels_node is not None and dynamic_node_label in mkiv_info.layer_hint_labels_node:
                        layer_hint_lo, layer_hint_hi = mkiv_info.layer_hint_labels_node[dynamic_node_label]
                        if layer_hint_lo is not None and layer < layer_hint_lo:
                            continue
                        if layer_hint_hi is not None and layer > layer_hint_hi:
                            continue

                    if mkiv_info.id_hint_labels_node is not None and dynamic_node_label in mkiv_info.id_hint_labels_node:
                        id_hint_lo, id_hint_hi = mkiv_info.id_hint_labels_node[dynamic_node_label]
                        if id_hint_lo is not None and node < id_hint_lo:
                            continue
                        if id_hint_hi is not None and node > id_hint_hi:
                            continue

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
    changes_by_layer = []

    for layer in range(mkiv_info.layers - 1):
        # terminal stays set
        if layer > 0:
            s.cnstr_implies_disj(vars_term[layer], True, [vars_term[layer + 1]], True, None)

        # keep track of change vars
        layer_changes = {}

        # keep track of possible changes at this layer
        layer_changes_by_node = {}
        for node in vars_node_by_id:
            layer_changes_by_node[node] = []

        layer_changes_by_edge = {}
        for edge in vars_edge_by_id_by_label_etc:
            layer_changes_by_edge[edge] = []

        changes_by_layer.append({})

        def _node_perm_helper(_node_ids, _num, _directed, _edges, _edges_possible, _curr_perm):
            _perm_ok_so_far = True
            _edge_perm = []
            for _fra, _til, _ind_hint_lo, _ind_hint_hi in _edges:
                if _fra < len(_curr_perm) and _til < len(_curr_perm):
                    if _directed:
                        _fra_ind = _curr_perm[_fra]
                        _til_ind = _curr_perm[_til]
                    else:
                        _fra_ind = min(_curr_perm[_fra], _curr_perm[_til])
                        _til_ind = max(_curr_perm[_fra], _curr_perm[_til])
                    if _ind_hint_lo is not None:
                        if (_ind_hint_lo > 0) and (_til_ind - _fra_ind < _ind_hint_lo):
                            _perm_ok_so_far = False
                            break
                        if (_ind_hint_lo <= 0) and (_fra_ind != -_ind_hint_lo):
                            _perm_ok_so_far = False
                            break
                    if _ind_hint_hi is not None:
                        if (_ind_hint_hi > 0) and (_til_ind - _fra_ind > _ind_hint_hi):
                            _perm_ok_so_far = False
                            break
                        if (_ind_hint_hi <= 0) and (_til_ind != -_ind_hint_hi):
                            _perm_ok_so_far = False
                            break
                    if (_fra_ind, _til_ind) not in _edges_possible:
                        _perm_ok_so_far = False
                        break
                    _edge_perm.append((_fra_ind, _til_ind))

            if _perm_ok_so_far:
                if _num == 0:
                    util_common.check(len(_edges) == len(_edge_perm), 'edge list length')
                    yield (_curr_perm, _edge_perm)
                else:
                    for _node_id in _node_ids:
                        if _node_id not in _curr_perm:
                            yield from _node_perm_helper(_node_ids, _num - 1, _directed, _edges, _edges_possible, _curr_perm + (_node_id,))

        def _node_perm(_node_ids, _num, _directed, _edges, _edges_possible):
            yield from _node_perm_helper(_node_ids, _num, _directed, _edges, _edges_possible, ())

        def _label_and_setting(_label):
            if _label.startswith(LABEL_RULE_NOT):
                return (_label[len(LABEL_RULE_NOT):], False)
            else:
                return (_label, True)

        use_directed = util_graph.gtype_directed(gtype) and mkiv_info.directed

        # connect layers
        for rule_index, (layer_hint_lo, layer_hint_hi, chain, nodes, edges) in enumerate(mkiv_info.rep_rules):
            changes_by_layer[layer][rule_index] = []

            # skip if needs to chain from previous
            if chain is not None and layer == 0:
                continue

            # layer hints
            if layer_hint_lo is not None and layer < layer_hint_lo:
                continue
            if layer_hint_hi is not None and layer + 1 > layer_hint_hi:
                continue

            edges_fra_til = [(fra, til, ind_hint_lo, ind_hint_hi) for fra, til, ind_hint_lo, ind_hint_hi, static_edge_label, dynamic_edge_label0, dynamic_edge_label1 in edges]
            for node_indices, edge_indices in _node_perm(vars_node_by_id, len(nodes), use_directed, edges_fra_til, vars_edge_by_id_by_label_etc):
                if mkiv_info.id_hint_labels_node is not None:
                    change_ok = True
                    for node_ind, (static_node_label, dynamic_node_label0, dynamic_node_label1) in zip(node_indices, nodes):
                        if not change_ok:
                            break
                        for dynamic_node_label in [dynamic_node_label0, dynamic_node_label1]:
                            if not change_ok:
                                break
                            if dynamic_node_label in mkiv_info.id_hint_labels_node:
                                id_hint_lo, id_hint_hi = mkiv_info.id_hint_labels_node[dynamic_node_label]
                                if id_hint_lo is not None and node_ind < id_hint_lo:
                                    change_ok = False
                                if id_hint_hi is not None and node_ind > id_hint_hi:
                                    change_ok = False
                    if not change_ok:
                        continue

                change_edges, ved_st, ved_in, ved_ou  = [], [], [], []
                util_common.check(len(edge_indices) == len(edges), 'edge perm')
                for (fra_ind, til_ind), (fra, til, ind_hint_lo, ind_hint_hi, static_edge_label, dynamic_edge_label0, dynamic_edge_label1) in zip(edge_indices, edges):
                    if static_edge_label is not None:
                        ved_st.append((vars_edge_static_by_id[(fra_ind, til_ind)][static_edge_label], True))
                    if dynamic_edge_label0 is not None:
                        dynamic_edge_label0, setting = _label_and_setting(dynamic_edge_label0)
                        ved_in.append((vars_edge_dynamic_by_layer_by_id[layer+0][(fra_ind, til_ind)][dynamic_edge_label0], setting))
                    if dynamic_edge_label1 is not None:
                        ved_ou.append((vars_edge_dynamic_by_layer_by_id[layer+1][(fra_ind, til_ind)][dynamic_edge_label1], True))
                        change_edges.append((fra_ind, til_ind))
                    else:
                        util_common.check(static_edge_label in [None, LABEL_GEN_STATIC], 'label')
                        util_common.check(dynamic_edge_label0 is None, 'label')

                change_nodes, vnd_st, vnd_in, vnd_ou = [], [], [], []
                util_common.check(len(node_indices) == len(nodes), 'node perm')
                for node_ind, (static_node_label, dynamic_node_label0, dynamic_node_label1) in zip(node_indices, nodes):
                    if static_node_label is not None:
                        vnd_st.append((vars_node_static_by_id[node_ind][static_node_label], True))
                    if dynamic_node_label0 is not None:
                        dynamic_node_label0, setting = _label_and_setting(dynamic_node_label0)
                        vnd_in.append((vars_node_dynamic_by_layer_by_id[layer+0][node_ind][dynamic_node_label0], True))
                    if dynamic_node_label1 is not None:
                        vnd_ou.append((vars_node_dynamic_by_layer_by_id[layer+1][node_ind][dynamic_node_label1], True))
                        change_nodes.append(node_ind)
                    else:
                        util_common.check(static_node_label in [None, LABEL_GEN_STATIC], 'label')
                        util_common.check(dynamic_node_label0 is None, 'label')

                change_vars = ved_st + ved_in + ved_ou + vnd_st + vnd_in + vnd_ou
                change = _make_conj_check_dupl(change_vars, layer_changes)

                if change == None: # prevent the same change from being counted as more than one change
                    continue

                if layer in mkiv_info.multi_layer_force_any:
                    change_lhs = _make_conj(ved_st + ved_in + vnd_st + vnd_in)
                    s.cnstr_implies_disj(change_lhs, True, [change], True, None)

                changes_by_layer[layer][rule_index].append((change, change_vars, change_nodes, change_edges))
                for node_ind in change_nodes:
                    layer_changes_by_node[node_ind].append(change)
                for edge_ind in change_edges:
                    layer_changes_by_edge[edge_ind].append(change)

            # chain from previous
            if chain is not None:
                these_changes = [change for change, change_vars, change_nodes, change_edges in changes_by_layer[layer][rule_index]]
                chain_changes = [change for change, change_vars, change_nodes, change_edges in changes_by_layer[layer - 1][rule_index - chain]]
                for chain_change in chain_changes:
                    s.cnstr_implies_disj(chain_change, True, these_changes, True, None)
                for these_change in these_changes:
                    s.cnstr_implies_disj(these_change, True, chain_changes, True, None)

        if mkiv_info.multi_allow:
            if layer not in mkiv_info.multi_layer_allow_none:
                # at least one change or terminal
                changes_or_term = list(layer_changes.values()) + [vars_term[layer + 1]]
                s.cnstr_count(changes_or_term, True, 1, len(changes_or_term), None)

            if layer not in mkiv_info.multi_layer_force_any:
                # each node part of at most one change
                for node, changes in layer_changes_by_node.items():
                    if len(changes) > 0:
                        s.cnstr_count(changes, True, 0, 1, None)

                # each edge part of at most one change
                for edge, changes in layer_changes_by_edge.items():
                    if len(changes) > 0:
                        s.cnstr_count(changes, True, 0, 1, None)

            else:
                s.cnstr_count([vars_term[layer + 1]], True, 0, 0, None)

            # no changes during terminal, no terminal during change
            for change in layer_changes.values():
                s.cnstr_implies_disj(vars_term[layer + 1], True, [change], False, None)
                s.cnstr_implies_disj(change, True, [vars_term[layer + 1]], False, None)

        else:
            # exactly one change or terminal
            changes_or_term = list(layer_changes.values()) + [vars_term[layer + 1]]
            s.cnstr_count(changes_or_term, True, 1, 1, None)

        # everything is either the same or part of a change
        for node in vars_node_by_id:
            for dynamic_node_label in dynamic_node_labels:
                vv0 = vars_node_dynamic_by_layer_by_id[layer + 0][node].get(dynamic_node_label)
                vv1 = vars_node_dynamic_by_layer_by_id[layer + 1][node].get(dynamic_node_label)
                if vv0 is not None and vv1 is not None:
                    s.cnstr_implies_disj(vv0, True, [vv1] + layer_changes_by_node[node], True, None)
                    #s.cnstr_implies_disj(vv0, False, [vv1] + layer_changes_by_node[node], [False] + [True] * len(layer_changes_by_node[node]), None)
                elif vv0 is not None:
                    s.cnstr_count([vv0], True, 0, 0, None)
                elif vv1 is not None:
                    s.cnstr_count([vv1], True, 0, 0, None)

        for edge in vars_edge_by_id_by_label_etc:
            for dynamic_edge_label in dynamic_edge_labels:
                vv0 = vars_edge_dynamic_by_layer_by_id[layer + 0][edge].get(dynamic_edge_label)
                vv1 = vars_edge_dynamic_by_layer_by_id[layer + 1][edge].get(dynamic_edge_label)
                if vv0 is not None and vv1 is not None:
                    s.cnstr_implies_disj(vv0, True, [vv1] + layer_changes_by_edge[edge], True, None)
                    #s.cnstr_implies_disj(vv0, False, [vv1] + layer_changes_by_edge[edge], [False] + [True] * len(layer_changes_by_edge[edge]), None)
                elif vv0 is not None:
                    s.cnstr_count([vv0], True, 0, 0, None)
                elif vv1 is not None:
                    s.cnstr_count([vv1], True, 0, 0, None)

    # rule index variables
    if mkiv_rule_index_count is not None:
        vars_rule_index = {}
        for rule_index in range(len(mkiv_info.rep_rules)):
            vars_rule_index[rule_index] = []

        for layer in range(mkiv_info.layers - 1):
            for rule_index in range(len(mkiv_info.rep_rules)):
                for change, change_vars, change_nodes, change_edges in changes_by_layer[layer][rule_index]:
                    vars_rule_index[rule_index].append(change)

        for rule_index, rule_count in mkiv_rule_index_count.items():
            util_common.check(rule_count <= len(vars_rule_index[rule_index]), 'not enough rule counts')
            s.cnstr_count(vars_rule_index[rule_index], True, rule_count, rule_count, None)

    # count constraints
    def _to_tuple(_labels):
        if type(_labels) == tuple:
            return _labels
        else:
            return (_labels,)

    def _add_count_cnstr_var(_vvs, _count):
        _count = _count(len(_vvs)) if callable(_count) else _count
        _lo, _hi = _count if type(_count) == tuple else (_count, _count)
        _hi = len(_vvs) if _hi is None else _hi
        s.cnstr_count(_vvs, True, _lo, _hi, None)

    def _add_count_cnstr_map(_vv_map, _layers, _ids, _labels, _count):
        _vvs = []

        if _layers is None:
            _vv_map = {None: _vv_map}

        for _layer in _to_tuple(_layers):
            for _id in _ids:
                for _label in _to_tuple(_labels):
                    if _label in _vv_map[_layer][_id]:
                        _vvs.append(_vv_map[_layer][_id][_label])

        _add_count_cnstr_var(_vvs, _count)

    for static_labels, count in mkiv_info.static_node_count.items():
        _add_count_cnstr_map(vars_node_static_by_id, None, vars_node_by_id.keys(), static_labels, count)

    for dynamic_labels, count in mkiv_info.dynamic_node_init_count.items():
        _add_count_cnstr_map(vars_node_dynamic_by_layer_by_id, 0, vars_node_by_id.keys(), dynamic_labels, count)

    for (dynamic_labels, count_layers), count in mkiv_info.dynamic_node_step_count.items():
        _add_count_cnstr_map(vars_node_dynamic_by_layer_by_id, count_layers, vars_node_by_id.keys(), dynamic_labels, count)

    for dynamic_labels, count in mkiv_info.dynamic_node_fini_count.items():
        _add_count_cnstr_map(vars_node_dynamic_by_layer_by_id, mkiv_info.layers - 1, vars_node_by_id.keys(), dynamic_labels, count)

    for dynamic_labels, count in mkiv_info.dynamic_edge_fini_count.items():
        _add_count_cnstr_map(vars_edge_dynamic_by_layer_by_id, mkiv_info.layers - 1, vars_edge_by_id_by_label_etc.keys(), dynamic_labels, count)

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

    # more count constraints
    if mkiv_label_count_layer is not None:
        label_count, label_layer = mkiv_label_count_layer
        use_layer = label_layer if label_layer is not None else mkiv_info.layers - 1

        for label, count in label_count.items():
            vvs = [vars_node_dynamic_by_layer_by_id[use_layer][node][label] for node in vars_node_by_id if label in vars_node_dynamic_by_layer_by_id[use_layer][node]]
            s.cnstr_count(vvs, True, count, count, None)

    # match contraints
    match_layer = None
    match_nodes = {}
    match_edges = {}
    if mkiv_match_graph_layer is not None:
        match_graph, match_layer = mkiv_match_graph_layer
        gr = match_graph.graphs[0]
        use_layer = match_layer if match_layer is not None else mkiv_info.layers - 1

        for node in gr.nodes:
            if util_graph.is_central(gr.nodes[node][util_graph.GATTR_CENTRAL]):
                node_key = int(node)
                dynamic_label = gr.nodes[node][util_graph.GATTR_LABEL]
                s.cnstr_count([vars_node_dynamic_by_layer_by_id[use_layer][node_key][dynamic_label]], True, 1, 1, None)
                match_nodes[node_key] = None

        for edge in gr.edges:
            if util_graph.is_central(gr.edges[edge][util_graph.GATTR_CENTRAL]):
                edge_key = (int(edge[0]), int(edge[1]))
                dynamic_label = gr.edges[edge][util_graph.GATTR_LABEL]
                s.cnstr_count([vars_edge_dynamic_by_layer_by_id[use_layer][edge_key][dynamic_label]], True, 1, 1, None)
                match_edges[edge_key] = None

    layers = mkiv_info.layers
    multi_allow = mkiv_info.multi_allow
    static_label_all = mkiv_info.static_label_all

    return s, layers, multi_allow, static_label_all, vars_term, vars_node_static_by_id, vars_node_dynamic_by_layer_by_id, vars_edge_static_by_id, vars_edge_dynamic_by_layer_by_id, changes_by_layer, match_layer, match_nodes, match_edges



def update_result(mkiv_tuple, result_info):
    s, layers, multi_allow, static_label_all, vars_term, vars_node_static_by_id, vars_node_dynamic_by_layer_by_id, vars_edge_static_by_id, vars_edge_dynamic_by_layer_by_id, changes_by_layer, match_layer, match_nodes, match_edges = mkiv_tuple

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
    prev_term = None

    for layer in range(layers):
        step = util_graph.GraphPlaythroughStepInfo()
        result_info.playthrough_info.append(step)

        is_term = vars_term[layer] is not None and s.get_var(vars_term[layer])
        next_term = layer + 1 == layers or (vars_term[layer + 1] is not None and s.get_var(vars_term[layer + 1]))
        util_common.check(not prev_term or is_term, 'term unset')

        mapping = {node:str(layer) + '__' + str(node) for node in vars_node_static_by_id}
        for edge in vars_edge_static_by_id:
            mapping[edge] = mapping[edge[0]], mapping[edge[1]]

        layer_graph = nx.relabel_nodes(first_graph, mapping)
        nx.set_node_attributes(layer_graph, None, util_graph.GATTR_LABEL)
        nx.set_node_attributes(layer_graph, False, util_graph.GATTR_CENTRAL)
        nx.set_edge_attributes(layer_graph, None, util_graph.GATTR_LABEL)
        nx.set_edge_attributes(layer_graph, False, util_graph.GATTR_CENTRAL)

        step.term = is_term
        step.first_term = is_term and not prev_term

        step.graphs = util_graph.Graphs()
        step.graphs.gtype = result_info.graphs.gtype
        step.graphs.colors = result_info.graphs.colors
        step.graphs.graphs = [layer_graph]

        change_index = 1

        for node, vvs in vars_node_dynamic_by_layer_by_id[layer].items():
            static_node_label = static_node_labels[node]
            dynamic_node_label = util_solvers.get_one_set(s, vvs)

            if dynamic_node_label != None:
                util_common.check(node in first_graph.nodes, 'node appeared')

                dynamic_node_label_disp = dynamic_node_label
                if node in match_nodes:
                    if match_layer is None and next_term:
                        dynamic_node_label_disp = '[' + dynamic_node_label + ']'
                    elif match_layer == layer:
                        dynamic_node_label_disp = '(' + dynamic_node_label + ')'

                if is_term:
                    if node in prev_dynamic_node_labels:
                        util_common.check(dynamic_node_label == prev_dynamic_node_labels[node], 'label changed after terminal')
                    if not prev_term and relabel_first:
                        first_graph.nodes[node][util_graph.GATTR_LABEL] += '|'
                elif relabel_first:
                    first_graph.nodes[node][util_graph.GATTR_LABEL] += '\\n' if layer == 0 else ';'
                    first_graph.nodes[node][util_graph.GATTR_LABEL] += dynamic_node_label_disp

                if static_label_all is not None:
                    util_common.check(static_node_label == static_label_all, 'static_label_all')
                    node_label = dynamic_node_label_disp
                else:
                    node_label = make_label(static_node_label, dynamic_node_label_disp)
                layer_graph.nodes[mapping[node]][util_graph.GATTR_LABEL] = node_label

            else:
                util_common.check(node not in first_graph.nodes, 'node disappeared')

            prev_dynamic_node_labels[node] = dynamic_node_label

        for edge, vvs in vars_edge_dynamic_by_layer_by_id[layer].items():
            static_edge_label = static_edge_labels[edge]
            dynamic_edge_label = util_solvers.get_one_set(s, vvs)

            if dynamic_edge_label != None:
                util_common.check(edge in first_graph.edges, 'edge appeared')

                dynamic_edge_label_disp = dynamic_edge_label
                if edge in match_edges:
                    if match_layer is None and next_term:
                        dynamic_edge_label_disp = '[' + dynamic_edge_label + ']'
                    elif match_layer == layer:
                        dynamic_edge_label_disp = '(' + dynamic_edge_label + ')'

                if is_term:
                    if edge in prev_dynamic_edge_labels:
                        util_common.check(dynamic_edge_label == prev_dynamic_edge_labels[edge], 'label changed after terminal')
                    if not prev_term and relabel_first:
                        first_graph.edges[edge][util_graph.GATTR_LABEL] += '|'
                elif relabel_first:
                    first_graph.edges[edge][util_graph.GATTR_LABEL] += '\\n' if layer == 0 else ';'
                    first_graph.edges[edge][util_graph.GATTR_LABEL] += dynamic_edge_label_disp

                if static_label_all is not None:
                    util_common.check(static_edge_label == static_label_all, 'static_label_all')
                    edge_label = dynamic_edge_label_disp
                else:
                    edge_label = make_label(static_edge_label, dynamic_edge_label_disp)
                layer_graph.edges[mapping[edge]][util_graph.GATTR_LABEL] = edge_label

            else:
                util_common.check(edge not in first_graph.edges, 'edge disappeared')

            prev_dynamic_edge_labels[edge] = dynamic_edge_label

        if layer != 0:
            for rule_index in changes_by_layer[layer - 1]:
                for change, change_vars, change_nodes, change_edges in changes_by_layer[layer - 1][rule_index]:
                    if util_solvers.are_all_set_to(s, change_vars):
                        for node in change_nodes:
                            layer_graph.nodes[mapping[node]][util_graph.GATTR_CENTRAL] = rule_index
                        for fra, til in change_edges:
                            layer_graph.edges[(mapping[fra], mapping[til])][util_graph.GATTR_CENTRAL] = rule_index

        for fra, til in list(layer_graph.edges):
            if layer_graph.edges[(fra, til)][util_graph.GATTR_LABEL] in [LABEL_GEN_NIL, LABEL_GEN_DYN_NIL]:
                layer_graph.remove_edge(fra, til)
            else:
                util_common.check(layer_graph.nodes[fra][util_graph.GATTR_LABEL] not in [LABEL_GEN_NIL, LABEL_GEN_DYN_NIL], 'edge has nil node')
                util_common.check(layer_graph.nodes[til][util_graph.GATTR_LABEL] not in [LABEL_GEN_NIL, LABEL_GEN_DYN_NIL], 'edge has nil node')

        for node in list(layer_graph.nodes):
            if layer_graph.nodes[node][util_graph.GATTR_LABEL] in [LABEL_GEN_NIL, LABEL_GEN_DYN_NIL]:
                layer_graph.remove_node(node)

        prev_term = is_term



def save_graph_result_info_mkiv(result_info, prefix, no_dot):
    util_common.check(result_info.playthrough_info is not None, 'playthrough not set')

    play_folder = prefix + '_play'
    print('writing playthrough levels to', play_folder)
    if os.path.exists(play_folder):
        shutil.rmtree(play_folder)
    os.makedirs(play_folder)

    for ii, step_info in enumerate(result_info.playthrough_info):
        descr = 'term' if step_info.term else 'step'

        step_prefix = play_folder + ('/%02d_' % ii) + descr + '_step'

        util_graph.save_graph_gr_dot(step_info.graphs, step_prefix, no_dot)

def print_graph_result_info_mkiv(result_info, outstream):
    util_common.check(result_info.playthrough_info is not None, 'playthrough not set')

    outstream.write('playthrough\n')
    outstream.write('\n')
    for step_info in result_info.playthrough_info:
        if step_info.first_term:
            outstream.write('>>> TERM <<<\n')
            outstream.write('\n')
        util_graph.write_graph_gr(step_info.graphs, outstream)
        outstream.write('\n')
