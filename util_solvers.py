import json, multiprocessing, queue, random, re, sys
import util_common



SOLVER_JSON_WRITE         = 'json-write'
SOLVER_DIMACS_WRITE_CNF   = 'dimacs-write-cnf'
SOLVER_DIMACS_WRITE_WCNF  = 'dimacs-write-wcnf'
SOLVER_DIMACS_READ        = 'dimacs-read'
SOLVER_Z3_OPTIMIZE        = 'z3-opt'
SOLVER_Z3_SOLVE           = 'z3-slv'
SOLVER_CVC5               = 'cvc5'
SOLVER_SCIPY              = 'scipy'
SOLVER_CVXPY              = 'cvxpy'
SOLVER_CLINGO_FE          = 'clingo-fe'
SOLVER_CLINGO_BE          = 'clingo-be'
SOLVER_PYSAT_FM           = 'pysat-fm'
SOLVER_PYSAT_RC2          = 'pysat-rc2'
SOLVER_PYSAT_FM_BOOL      = 'pysat-fm-boolonly'
SOLVER_PYSAT_RC2_BOOL     = 'pysat-rc2-boolonly'
SOLVER_PYSAT_MC           = 'pysat-minicard'
SOLVER_PYSAT_GC41         = 'pysat-gluecard41'
SOLVER_LIST               = [SOLVER_JSON_WRITE, SOLVER_DIMACS_WRITE_CNF, SOLVER_DIMACS_WRITE_WCNF, SOLVER_DIMACS_READ, SOLVER_Z3_OPTIMIZE, SOLVER_Z3_SOLVE, SOLVER_CVC5, SOLVER_SCIPY, SOLVER_CVXPY, SOLVER_CLINGO_FE, SOLVER_CLINGO_BE, SOLVER_PYSAT_FM, SOLVER_PYSAT_RC2, SOLVER_PYSAT_FM_BOOL, SOLVER_PYSAT_RC2_BOOL, SOLVER_PYSAT_MC, SOLVER_PYSAT_GC41]
SOLVER_NOTEST_LIST        = [SOLVER_JSON_WRITE, SOLVER_DIMACS_WRITE_CNF, SOLVER_DIMACS_WRITE_WCNF, SOLVER_DIMACS_READ]



def try_import_z3():
    global z3
    try:
        import z3
        return True
    except ImportError:
        z3 = None
        del z3
        return False

def try_import_cvc5():
    global cvc5
    try:
        import cvc5.pythonic
        return True
    except ImportError:
        cvc5 = None
        del cvc5
        return False

def try_import_scipy():
    global numpy
    global scipy
    try:
        import numpy
        import scipy
        return True
    except ImportError:
        numpy = None
        del numpy
        scipy = None
        del scipy
        return False

def try_import_cvxpy():
    global numpy
    global cvxpy
    try:
        import numpy
        import cvxpy
        return True
    except ImportError:
        numpy = None
        del numpy
        cvxpy = None
        del cvxpy
        return False

def try_import_clingo():
    global clingo
    try:
        import clingo
        return True
    except ImportError:
        clingo = None
        del clingo
        return False

def try_import_pysat():
    global pysat
    try:
        import pysat.card
        import pysat.formula
        import pysat.examples.fm
        import pysat.examples.rc2
        import pysat.solvers
        return True
    except ImportError:
        pysat = None
        del pysat
        return False



def solver_id_to_solver(solver_id):
    if solver_id == SOLVER_JSON_WRITE:
        return WriteJsonSolver()
    elif solver_id == SOLVER_DIMACS_WRITE_CNF:
        return CnfWriteDimacsSolver()
    elif solver_id == SOLVER_DIMACS_WRITE_WCNF:
        return WcnfWriteDimacsSolver()
    elif solver_id == SOLVER_DIMACS_READ:
        return ReadDimacsSolver()
    elif solver_id == SOLVER_Z3_OPTIMIZE:
        return OptimizeZ3Solver()
    elif solver_id == SOLVER_Z3_SOLVE:
        return SolveZ3Solver()
    elif solver_id == SOLVER_CVC5:
        return CVC5Solver()
    elif solver_id == SOLVER_SCIPY:
        return SciPySolver()
    elif solver_id == SOLVER_CVXPY:
        return CvxPySolver()
    elif solver_id == SOLVER_CLINGO_FE:
        return FrontendClingoSolver()
    elif solver_id == SOLVER_CLINGO_BE:
        return BackendClingoSolver()
    elif solver_id == SOLVER_PYSAT_FM:
        return FMPySatSolver()
    elif solver_id == SOLVER_PYSAT_RC2:
        return RC2PySatSolver()
    elif solver_id == SOLVER_PYSAT_FM_BOOL:
        return BoolOnlyFMPySatSolver()
    elif solver_id == SOLVER_PYSAT_RC2_BOOL:
        return BoolOnlyRC2PySatSolver()
    elif solver_id == SOLVER_PYSAT_MC:
        return MiniCardPySatSolver()
    elif solver_id == SOLVER_PYSAT_GC41:
        return GlueCard41PySatSolver()
    else:
        util_common.check(False, 'solver ' + solver_id + ' unrecognized.')

def solver_takes_filename(solver):
    return isinstance(solver, _SolverFilename)



def get_one_set(solver, vv_map):
    set_val, found = None, False
    for val, vv in vv_map.items():
        if solver.get_var(vv):
            util_common.check(not found, 'multiple values')
            set_val, found = val, True
    util_common.check(found, 'no value')
    return set_val

def get_all_set(solver, vv_map):
    which_set = []
    for val, vv in vv_map.items():
        if solver.get_var(vv):
            which_set.append(val)
    return which_set

def are_all_set(solver, vvs):
    util_common.check(len(vvs) != 0, 'no vars to check')
    for vv in vvs:
        if not solver.get_var(vv):
            return False
    return True



class _Solver:
    def __init__(self, solver_id):
        self._solver_id = solver_id

    def get_id(self):
        return self._solver_id

    def make_var(self):
        util_common.check(False, 'unimplemented')

    def make_conj(self, vvs, settings):
        util_common.check(False, 'unimplemented')

    def cnstr_implies_disj(self, in_vv, in_vv_setting, out_vvs, out_vv_settings, weight):
        util_common.check(False, 'unimplemented')

    def cnstr_count(self, vvs, settings, lo, hi, weight):
        util_common.check(False, 'unimplemented')

    def solve(self):
        util_common.check(False, 'unimplemented')

    def get_var(self, vv):
        util_common.check(False, 'unimplemented')

    def get_objective(self):
        util_common.check(False, 'unimplemented')

    def get_solver_id_used(self):
        util_common.check(False, 'unimplemented')

    def supports_weights(self):
        return False

    def supports_xforms(self):
        return False



def _wrap_var(vv):
    return ('v', vv)

def _wrap_conj(vv):
    return ('c', vv)

def _is_var(vv):
    return vv[0] == 'v'

def _is_conj(vv):
    return vv[0] == 'c'

def _unwrap_var(vv):
    util_common.check(type(vv) == tuple and len(vv) == 2 and vv[0] == 'v', 'unwrap')
    return vv[1]

def _unwrap_conj(vv):
    util_common.check(type(vv) == tuple and len(vv) == 2 and vv[0] == 'c', 'unwrap')
    return vv[1]

def _unwrap_any(vv):
    util_common.check(type(vv) == tuple and len(vv) == 2 and vv[0] in ['v', 'c'], 'unwrap')
    return vv[1]

def _unwrap_lit_lconj(vv, setting, negate_func):
    vv = _unwrap_any(vv)
    if not setting:
        vv = negate_func(vv)
    return vv

def _unwrap_lit_lconjs(vvs, settings, negate_func):
    if settings in [True, False]:
        settings = [settings for vv in vvs]
    else:
        util_common.check(len(vvs) == len(settings), 'different vvs and settings lengths')

    return [_unwrap_lit_lconj(vv, setting, negate_func) for vv, setting in zip(vvs, settings)]

def _is_xform_t(vv):
    return vv[0] in ['t2', 't3']

def _unwrap_xform_t(vv):
    util_common.check(type(vv) == tuple and vv[0] in ['t2', 't3'], 'unwrap')
    return vv[1:]

def _is_xform_x2(vv):
    return vv[0] in ['x2']

def _unwrap_xform_x2(vv):
    util_common.check(type(vv) == tuple and vv[0] in ['x2'], 'unwrap')
    return vv[1:]



class _SolverImpl(_Solver):
    def __init__(self, solver_id, supports_weights, supports_xforms):
        super().__init__(solver_id)

        self._supports_weights = supports_weights
        self._supports_xforms = supports_xforms

        self._result = None
        self._objective = None

    def make_var(self):
        return _wrap_var(self._IMPL_make_var())

    def make_conj(self, vvs, settings):
        util_common.check(len(vvs) > 0, 'empty conj')

        return _wrap_conj(self._IMPL_make_conj(_unwrap_lit_lconjs(vvs, settings, self._IMPL_negate_var_conj)))

    def cnstr_implies_disj(self, in_vv, in_vv_setting, out_vvs, out_vv_settings, weight):
        if not self._supports_weights:
            util_common.check(weight is None, 'solver does not support weights')
        else:
            util_common.check(weight is None or type(weight) == int, 'weights must be integers')

        return self._IMPL_cnstr_implies_disj(_unwrap_lit_lconj(in_vv, in_vv_setting, self._IMPL_negate_var_conj), _unwrap_lit_lconjs(out_vvs, out_vv_settings, self._IMPL_negate_var_conj_for_implies_out), weight)

    def cnstr_count(self, vvs, settings, lo, hi, weight):
        util_common.check(0 <= lo and lo <= hi and hi <= len(vvs), 'count')

        if not self._supports_weights:
            util_common.check(weight is None, 'solver does not support weights')
        else:
            util_common.check(weight is None or type(weight) == int, 'weights must be integers')

        return self._IMPL_cnstr_count(_unwrap_lit_lconjs(vvs, settings, self._IMPL_negate_var_conj), lo, hi, weight)

    def solve(self):
        return self._IMPL_solve()

    def get_var(self, vv):
        return self._IMPL_get_var(_unwrap_var(vv))

    def get_objective(self):
        return self._objective

    def get_solver_id_used(self):
        return self.get_id()

    def supports_weights(self):
        return self._supports_weights

    def supports_xforms(self):
        return self._supports_xforms

    def _IMPL_negate_var_conj_for_implies_out(self, ll):
        return self._IMPL_negate_var_conj(ll)

    def _IMPL_negate_var_conj(self, ll):
        util_common.check(False, 'unimplemented')

    def _IMPL_make_var(self):
        util_common.check(False, 'unimplemented')

    def _IMPL_make_conj(self, lls):
        util_common.check(False, 'unimplemented')

    def _IMPL_cnstr_implies_disj(self, ll_in, lls_out, weight):
        util_common.check(False, 'unimplemented')

    def _IMPL_cnstr_count(self, lls, lo, hi, weight):
        util_common.check(False, 'unimplemented')

    def _IMPL_solve(self):
        util_common.check(False, 'unimplemented')

    def _IMPL_get_var(self, vv):
        util_common.check(False, 'unimplemented')

class _SolverFilename:
    def __init__(self):
        self._filename = None

    def set_filename(self, filename):
        self._filename = filename

    def file_write(self, data):
        if self._filename is None:
            print(data)
        else:
            print('writing to', self._filename)
            with open(self._filename, 'wt') as f:
                f.write(data)

    def file_read(self):
        if self._filename is None:
            return sys.stdin.read()
        else:
            print('reading from', self._filename)
            with open(self._filename, 'rt') as f:
                return f.read()

class PortfolioSolver(_Solver):
    RES_SOLN   = 'soln'
    RES_NOSOLN = 'nosoln'
    RES_ERROR  = 'error'

    def __init__(self, solver_ids, timeout):
        super().__init__('portfolio:' + ';'.join(solver_ids))

        self._solver_ids = solver_ids
        self._timeout = timeout

        self._solver_var_conjs = []
        self._solver_commands = []

        self._result = None
        self._objective = None

        self._solver_id_used = None

    def make_var(self):
        self._solver_var_conjs.append(_wrap_var(None))
        return len(self._solver_var_conjs) - 1

    def make_conj(self, vvs, settings):
        util_common.check(len(vvs) > 0, 'empty conj')

        self._solver_var_conjs.append(_wrap_conj((tuple(vvs), settings)))
        return len(self._solver_var_conjs) - 1

    def cnstr_implies_disj(self, in_vv, in_vv_setting, out_vvs, out_vv_settings, weight):
        util_common.check(weight is None or type(weight) == int, 'weights must be integers')

        self._solver_commands.append(('cnstr_implies_disj', (in_vv, in_vv_setting, out_vvs, out_vv_settings, weight)))

    def cnstr_count(self, vvs, settings, lo, hi, weight):
        util_common.check(0 <= lo and lo <= hi and hi <= len(vvs), 'count')
        util_common.check(weight is None or type(weight) == int, 'weights must be integers')

        self._solver_commands.append(('cnstr_count', (vvs, settings, lo, hi, weight)))

    def solve(self):
        q = multiprocessing.Queue()

        procs = [(multiprocessing.Process(target=PortfolioSolver.run_solver, args=(q, index, solver_id, self._solver_var_conjs, self._solver_commands))) for (index, solver_id) in enumerate(self._solver_ids)]
        for proc in procs:
            proc.start()

        result = None
        try:
            result = q.get(timeout=self._timeout)
        except queue.Empty:
            util_common.write_portfolio('portfolio timeout\n')

        for proc in procs:
            proc.kill()

        if result[0] == PortfolioSolver.RES_SOLN:
            index, self._result, self._objective = result[1]
            self._solver_id_used = self._solver_ids[index]
            util_common.write_portfolio('portfolio using %d %s\n' % (index, self._solver_id_used))
            return True
        elif result[0] == PortfolioSolver.RES_NOSOLN:
            return False
        elif result[0] == PortfolioSolver.RES_ERROR:
            err = result[1]
            raise err
        else:
            util.check(False, 'unexpected result')

    def get_var(self, vv):
        return self._result[vv]

    def get_objective(self):
        return self._objective

    def get_solver_id_used(self):
        return self._solver_id_used

    @staticmethod
    def run_solver(s_q, s_index, s_solver_id, s_solver_var_conjs, s_solver_commands):
        s_ret = (PortfolioSolver.RES_NOSOLN,)

        try:
            util_common.write_portfolio('portfolio starting %d %s\n' % (s_index, s_solver_id))

            s_solver = solver_id_to_solver(s_solver_id)

            s_var_conj_map = {}

            def translate_vars(_vvv):
                nonlocal s_var_conj_map
                if type(_vvv) in [list, tuple]:
                    return [s_var_conj_map[_vv] for _vv in _vvv]
                else:
                    return s_var_conj_map[_vvv]

            s_vars_inds = []
            s_conjs_inds = []

            for s_ind, s_var_conj in enumerate(s_solver_var_conjs):
                if _is_var(s_var_conj):
                    s_vars_inds.append(s_ind)
                elif _is_conj(s_var_conj):
                    s_conjs_inds.append(s_ind)
                else:
                    util_common.check(False, 'var_conj')

            random.Random(s_index).shuffle(s_vars_inds)

            for s_ind in s_vars_inds:
                util_common.check(_is_var(s_solver_var_conjs[s_ind]), 'var')
                s_var_conj_map[s_ind] = s_solver.make_var()

            for s_ind in s_conjs_inds:
                util_common.check(_is_conj(s_solver_var_conjs[s_ind]), 'conj')
                s_info = _unwrap_conj(s_solver_var_conjs[s_ind])
                s_var_conj_map[s_ind] = s_solver.make_conj(translate_vars(s_info[0]), s_info[1])

            for s_func_name, s_args in s_solver_commands:
                if s_func_name == 'cnstr_implies_disj':
                    s_solver.cnstr_implies_disj(translate_vars(s_args[0]), s_args[1], translate_vars(s_args[2]), s_args[3], s_args[4])
                elif s_func_name == 'cnstr_count':
                    s_solver.cnstr_count(translate_vars(s_args[0]), s_args[1], s_args[2], s_args[3], s_args[4])
                else:
                    util_common.check(False, 's_func_name')

            if s_solver.solve():
                s_vars_set = {}
                for s_ind, s_var_conj in enumerate(s_solver_var_conjs):
                    if _is_var(s_var_conj):
                        s_vars_set[s_ind] = s_solver.get_var(translate_vars(s_ind))

                s_ret = (PortfolioSolver.RES_SOLN, (s_index, s_vars_set, s_solver.get_objective()))

            util_common.write_portfolio('portfolio finishing %d %s\n' % (s_index, s_solver_id))

        except Exception as e:
            s_ret = (PortfolioSolver.RES_ERROR, e)

            util_common.write_portfolio('portfolio error %d %s %s\n' % (s_index, s_solver_id, e))

        s_q.put(s_ret)



class WriteJsonSolver(_SolverImpl, _SolverFilename):
    def __init__(self):
        _SolverImpl.__init__(self, SOLVER_JSON_WRITE, True, False)
        _SolverFilename.__init__(self)

        self._curr_id = 0

        self._output = {}
        self._output['var'] = []
        self._output['conj'] = []
        self._output['cnstr_implies_disj'] = []
        self._output['cnstr_count'] = []

    def _IMPL_negate_var_conj(self, ll):
        return '~' + ll

    def _IMPL_make_var(self):
        self._curr_id += 1
        ret = 'v%d' % self._curr_id
        self._output['var'].append({'id':ret})
        return ret

    def _IMPL_make_conj(self, lls):
        self._curr_id += 1
        ret = 'c%d' % self._curr_id
        self._output['conj'].append({'id':ret, 'of':lls})
        return ret

    def _IMPL_cnstr_implies_disj(self, in_ll, out_lls, weight):
        print_weight = weight if weight is not None else 0
        self._output['cnstr_implies_disj'].append({'if':in_ll, 'then':out_lls, 'weight':print_weight})

    def _IMPL_cnstr_count(self, lls, lo, hi, weight):
        print_weight = weight if weight is not None else 0
        self._output['cnstr_count'].append({'of':lls, 'min':lo, 'max':hi, 'weight':print_weight})

    def _IMPL_solve(self):
        self.file_write(json.dumps(self._output, indent=2) + '\n')
        return False



class _Z3Solver(_SolverImpl):
    Z3_OPTION_SOLVE       = 'solve'
    Z3_OPTION_OPTIMIZE    = 'optimize'

    def __init__(self, solver_id, solver_option):
        util_common.check(try_import_z3(), 'z3 not available')

        util_common.check(solver_option in [_Z3Solver.Z3_OPTION_OPTIMIZE, _Z3Solver.Z3_OPTION_SOLVE], 'invalid option for solver: ' + solver_option)

        self._option = solver_option

        if self._option == _Z3Solver.Z3_OPTION_OPTIMIZE:
            super().__init__(solver_id, True, True)
            self._s = z3.Optimize()
        else:
            super().__init__(solver_id, False, True)
            self._s = z3.Solver()

    def _help_add_cnstr_weight(self, cnstr, weight):
        if weight is None:
            self._s.add(cnstr)
        else:
            self._s.add_soft(cnstr, weight)

    def _IMPL_negate_var_conj(self, ll):
        return z3.Not(ll)

    def _IMPL_make_var(self):
        return z3.FreshBool()

    def _IMPL_make_conj(self, lls):
        if len(lls) == 1:
            return lls[0]
        else:
            return z3.And(*lls)

    def _IMPL_cnstr_implies_disj(self, in_ll, out_lls, weight):
        if self._option != _Z3Solver.Z3_OPTION_OPTIMIZE:
            util_common.check(weight is None, 'solver does not support weights')

        self._help_add_cnstr_weight(z3.Implies(in_ll, z3.Or(*out_lls)), weight)

    def _IMPL_cnstr_count(self, lls, lo, hi, weight):
        if self._option != _Z3Solver.Z3_OPTION_OPTIMIZE:
            util_common.check(weight is None, 'solver does not support weights')

        if len(lls) == 0:
            pass

        elif len(lls) == 1:
            if lo == 0 and hi == 1:
                pass
            elif lo == 0 and hi == 0:
                self._help_add_cnstr_weight(z3.Not(lls[0]), weight)
            elif lo == 1 and hi == 1:
                self._help_add_cnstr_weight(lls[0], weight)
            else:
                util_common.check(False, 'count vars')

        else:
            lls_count = [(vv, 1) for vv in lls]

            if lo == hi:
                self._help_add_cnstr_weight(z3.PbEq(lls_count, lo), weight)
            else:
                if lo == 0:
                    pass
                elif lo == 1:
                    self._help_add_cnstr_weight(z3.Or(lls), weight)
                else:
                    self._help_add_cnstr_weight(z3.PbGe(lls_count, lo), weight)

                if hi < len(lls):
                    self._help_add_cnstr_weight(z3.PbLe(lls_count, hi), weight)

    def _IMPL_solve(self):
        if self._option == _Z3Solver.Z3_OPTION_OPTIMIZE:
            def on_model(_m):
                util_common.write_time('.')

            self._s.set_on_model(on_model)

        chk = self._s.check()
        util_common.write_time('\n')
        util_common.write_time(str(chk) + '\n')

        if chk == z3.unsat:
            return False

        if chk == z3.unknown:
            util_common.write_time(str(self._s.reason_unknown()) + '\n')
            return False

        self._result = self._s.model()

        if self._option == _Z3Solver.Z3_OPTION_OPTIMIZE:
            objs = [self._s.model().evaluate(obj) for obj in self._s.objectives()]
        else:
            objs = []

        if len(objs) == 0:
            self._objective = 0
        else:
            util_common.check(len(objs) == 1, 'cost length')
            self._objective = objs[0].as_long()

        return True

    def _IMPL_get_var(self, vv):
        return bool(self._result[vv])

    def make_var_xform(self, dims):
        if dims == 2:
            return ('t2', z3.FreshReal(), z3.FreshReal())
        elif dims == 3:
            return ('t3', z3.FreshReal(), z3.FreshReal(), z3.FreshReal())
        elif dims == 'x2':
            return ('x2', z3.FreshReal(), z3.FreshReal(), z3.FreshReal(), z3.FreshReal(), z3.FreshReal(), z3.FreshReal())

    def get_var_pos_xform(self, vv):
        if _is_xform_t(vv):
            vv = _unwrap_xform_t(vv)
            return tuple([self._result[ee].numerator_as_long() / self._result[ee].denominator_as_long() for ee in vv])
        elif _is_xform_x2(vv):
            vv = _unwrap_xform_x2(vv)
            return tuple([self._result[vv[2]].numerator_as_long() / self._result[vv[2]].denominator_as_long(),
                          self._result[vv[5]].numerator_as_long() / self._result[vv[5]].denominator_as_long()])

    def _xform_type(self, xforms):
        xtypes = dict.fromkeys([vv[0] for vv in xforms])
        util_common.check(len(xtypes) == 1, 'xform types')
        xtype = next(iter(xtypes))
        util_common.check(xtype in ['t2', 't3', 'x2'], 'xform types')
        return xtype

    def _xform_xtype_t(self, xtype):
        return xtype in ['t2', 't3']

    def cnstr_ident_dist_xform(self, missing_conds, xforms, minlinfdist):
        def far(_p0, _p1):
            return z3.Or([z3.Or(_i0 - _i1 <= -minlinfdist, _i0 - _i1 >= minlinfdist) for _i0, _i1 in zip(_p0, _p1)])

        missing_conds = [_unwrap_var(vv) for vv in missing_conds]

        util_common.check(len(missing_conds) == len(xforms), 'lengths')

        if self._xform_xtype_t(self._xform_type(xforms)):
            xforms = [_unwrap_xform_t(vv) for vv in xforms]
            self._s.add(z3.Not(missing_conds[0]))
            self._s.add(z3.And([p0 == 0 for p0 in xforms[0]]))

            for ii in range(len(xforms)):
                for jj in range(ii + 1, len(xforms)):
                    self._s.add(z3.Implies(z3.And(z3.Not(missing_conds[ii]), z3.Not(missing_conds[jj])),
                                           far(xforms[ii], xforms[jj])))

        else:
            xforms = [_unwrap_xform_x2(vv) for vv in xforms]
            self._s.add(z3.Not(missing_conds[0]))
            self._s.add(z3.And(xforms[0][0] == 1, xforms[0][1] == 0, xforms[0][2] == 0,
                               xforms[0][3] == 0, xforms[0][4] == 1, xforms[0][5] == 0))

            for ii in range(len(xforms)):
                for jj in range(ii + 1, len(xforms)):
                    self._s.add(z3.Implies(z3.And(z3.Not(missing_conds[ii]), z3.Not(missing_conds[jj])),
                                           far([xforms[ii][2], xforms[ii][5]], [xforms[jj][2], xforms[jj][5]])))

    def cnstr_implies_xform(self, cond, xform0, xform1, dxform, primary):
        def close(_p0, _p1):
            return z3.And([z3.And(_i0 - _i1 >= -0.01, _i0 - _i1 <= 0.01) for _i0, _i1 in zip(_p0, _p1)])

        if self._xform_xtype_t(self._xform_type([xform0, xform1])):
            xform0 = _unwrap_xform_t(xform0)
            xform1 = _unwrap_xform_t(xform1)
            util_common.check(len(dxform) == len(xform0) == len(xform1), 'dims')
            if primary:
                xform_apply = z3.And([p1 == p0 + dd for dd, p0, p1 in zip(dxform, xform0, xform1)])
            else:
                xform_apply = close(xform1, [p0 + dd for dd, p0 in zip(dxform, xform0)])

        else:
            xform0 = _unwrap_xform_x2(xform0)
            xform1 = _unwrap_xform_x2(xform1)
            util_common.check(6 == len(dxform) == len(xform0) == len(xform1), 'dims')
            if primary:
                xform_apply = [xform1[0] == (xform0[0] * dxform[0] + xform0[1] * dxform[3]),
                               xform1[1] == (xform0[0] * dxform[1] + xform0[1] * dxform[4]),
                               xform1[2] == (xform0[0] * dxform[2] + xform0[1] * dxform[5] + xform0[2]),
                               xform1[3] == (xform0[3] * dxform[0] + xform0[4] * dxform[3]),
                               xform1[4] == (xform0[3] * dxform[1] + xform0[4] * dxform[4]),
                               xform1[5] == (xform0[3] * dxform[2] + xform0[4] * dxform[5] + xform0[5])]
            else:
                xform_apply = [close([xform1[2], xform1[5]],
                                     [xform0[0] * dxform[2] + xform0[1] * dxform[5] + xform0[2],
                                      xform0[3] * dxform[2] + xform0[4] * dxform[5] + xform0[5]])]

        cond = _unwrap_var(cond)
        self._s.add(z3.Implies(cond, z3.And(xform_apply)))

class OptimizeZ3Solver(_Z3Solver):
    def __init__(self):
        super().__init__(SOLVER_Z3_OPTIMIZE, _Z3Solver.Z3_OPTION_OPTIMIZE)

class SolveZ3Solver(_Z3Solver):
    def __init__(self):
        super().__init__(SOLVER_Z3_SOLVE, _Z3Solver.Z3_OPTION_SOLVE)




class CVC5Solver(_SolverImpl):
    def __init__(self):
        util_common.check(try_import_cvc5(), 'cvc5 not available')

        super().__init__(SOLVER_CVC5, False, False)

        self._s = cvc5.pythonic.SimpleSolver()

    def _IMPL_negate_var_conj(self, ll):
        return cvc5.pythonic.Not(ll)

    def _IMPL_make_var(self):
        return cvc5.pythonic.FreshBool()

    def _IMPL_make_conj(self, lls):
        if len(lls) == 1:
            return lls[0]
        else:
            return cvc5.pythonic.And(*lls)

    def _IMPL_cnstr_implies_disj(self, in_ll, out_lls, weight):
        util_common.check(weight is None, 'solver does not support weights')

        if len(out_lls) == 0:
            self._s.add(cvc5.pythonic.Implies(in_ll, False))
        elif len(out_lls) == 1:
            self._s.add(cvc5.pythonic.Implies(in_ll, out_lls[0]))
        else:
            self._s.add(cvc5.pythonic.Implies(in_ll, cvc5.pythonic.Or(*out_lls)))

    def _IMPL_cnstr_count(self, lls, lo, hi, weight):
        util_common.check(weight is None, 'solver does not support weights')

        if len(lls) == 0:
            pass

        elif len(lls) == 1:
            if lo == 0 and hi == 1:
                pass
            elif lo == 0 and hi == 0:
                self._s.add(cvc5.pythonic.Not(lls[0]))
            elif lo == 1 and hi == 1:
                self._s.add(lls[0])
            else:
                util_common.check(False, 'count vars')

        else:
            lls_if = sum([cvc5.pythonic.If(ll, 1, 0) for ll in lls])

            if lo == hi:
                self._s.add(lls_if == lo)
            else:
                if lo == 0:
                    pass
                elif lo == 1:
                    self._s.add(cvc5.pythonic.Or(lls))
                else:
                    self._s.add(lls_if >= lo)

                if hi < len(lls):
                    self._s.add(lls_if <= hi)

    def _IMPL_solve(self):
        chk = self._s.check()
        util_common.write_time('\n')
        util_common.write_time(str(chk) + '\n')

        if chk == cvc5.pythonic.unsat:
            return False

        if chk == cvc5.pythonic.unknown:
            util_common.write_time(str(self._s.reason_unknown()) + '\n')
            return False

        self._result = self._s.model()
        self._objective = 0

        return True

    def _IMPL_get_var(self, vv):
        return bool(self._result[vv])



class _MilpSolver(_SolverImpl):
    def __init__(self, solver_id):
        super().__init__(solver_id, True, False)

        self._curr_id = 0
        self._weights = []
        self._constraints = []

    def _help_new_var(self):
        self._curr_id += 1
        return self._curr_id

    def _IMPL_negate_var_conj(self, ll):
        return -ll

    def _IMPL_make_var(self):
        return self._help_new_var()

    def _IMPL_make_conj(self, lls):
        if len(lls) == 1:
            return lls[0]
        else:
            vv = self._help_new_var()
            n = len(lls)

            coefs, inds, lo, hi = [], [], None, 0
            coefs.append(n)
            inds.append(abs(vv) - 1)
            for ll in lls:
                inds.append(abs(ll) - 1)
                if ll > 0:
                    coefs.append(-1)
                elif ll < 0:
                    coefs.append(1)
                    hi += 1
                else:
                    util_common.check(False, 'no id 0')
            self._constraints.append((coefs, inds, lo, hi))

            coefs, inds, lo, hi = [], [], None, n - 1
            coefs.append(-n)
            inds.append(abs(vv) - 1)
            for ll in lls:
                inds.append(abs(ll) - 1)
                if ll > 0:
                    coefs.append(1)
                elif ll < 0:
                    coefs.append(-1)
                    hi -= 1
                else:
                    util_common.check(False, 'no id 0')
            self._constraints.append((coefs, inds, lo, hi))

            return vv

    def _IMPL_cnstr_implies_disj(self, in_ll, out_lls, weight):
        coefs, inds, lo, hi = [], [], None, 0

        inds.append(abs(in_ll) - 1)
        if in_ll > 0:
            coefs.append(1)
        elif in_ll < 0:
            coefs.append(-1)
            hi -= 1
        else:
            util_common.check(False, 'no id 0')

        for ll in out_lls:
            inds.append(abs(ll) - 1)
            if ll > 0:
                coefs.append(-1)
            elif ll < 0:
                coefs.append(1)
                hi += 1
            else:
                util_common.check(False, 'no id 0')

        if weight is not None:
            weight_var = self._help_new_var()
            self._weights.append((weight, abs(weight_var) - 1))
            inds.append(abs(weight_var) - 1)
            coefs.append(-1)

        self._constraints.append((coefs, inds, lo, hi))

    def _IMPL_cnstr_count(self, lls, lo, hi, weight):
        if len(lls) > 0:
            coefs, inds, lo, hi = [], [], lo, hi
            for ll in lls:
                inds.append(abs(ll) - 1)
                if ll > 0:
                    coefs.append(1)
                elif ll < 0:
                    coefs.append(-1)
                    lo -= 1
                    hi -= 1
                else:
                    util_common.check(False, 'no id 0')

            if weight is not None:
                weight_var1 = self._help_new_var()
                self._weights.append((weight, abs(weight_var1) - 1))
                weight_var2 = self._help_new_var()
                self._weights.append((weight, abs(weight_var2) - 1))

                self._constraints.append((coefs + [ len(lls)], inds + [abs(weight_var1) - 1], lo, None))
                self._constraints.append((coefs + [-len(lls)], inds + [abs(weight_var2) - 1], None, hi))
            else:
                self._constraints.append((coefs, inds, lo, hi))

    def _IMPL_solve(self):
        soln = self._do_solve()

        if soln is None:
            return False

        self._result, self._objective = soln

        return True

    def _IMPL_get_var(self, vv):
        return self._result[vv - 1] > 0

class SciPySolver(_MilpSolver):
    def __init__(self):
        util_common.check(try_import_scipy(), 'scipy not available')

        super().__init__(SOLVER_SCIPY)

    def _do_solve(self):
        c = numpy.zeros(self._curr_id)
        for coef, ind in self._weights:
            c[ind] += coef

        A = numpy.zeros((len(self._constraints), self._curr_id))
        b_l = numpy.zeros(len(self._constraints))
        b_u = numpy.zeros(len(self._constraints))
        for ii, (coefs, inds, lo, hi) in enumerate(self._constraints):
            for coef, ind in zip(coefs, inds):
                A[ii][ind] += coef
            if lo is None:
                b_l[ii] = -numpy.inf
            else:
                b_l[ii] = lo
            if hi is None:
                b_u[ii] = numpy.inf
            else:
                b_u[ii] = hi
        constraints = scipy.optimize.LinearConstraint(A, b_l, b_u)

        integrality = numpy.ones(self._curr_id, dtype=numpy.uint8)
        bounds = scipy.optimize.Bounds(numpy.zeros(self._curr_id), numpy.ones(self._curr_id))

        res = scipy.optimize.milp(c=c, constraints=constraints, integrality=integrality, bounds=bounds)

        if res.status != 0:
            return None

        util_common.check(int(res.fun) == res.fun, 'non-integer objective')

        return (res.x > 0.5), int(res.fun)

class CvxPySolver(_MilpSolver):
    def __init__(self):
        util_common.check(try_import_cvxpy(), 'cvxpy not available')

        super().__init__(SOLVER_CVXPY)

    def _do_solve(self):
        x = cvxpy.Variable(self._curr_id, integer=True)

        c = numpy.zeros(self._curr_id)
        for coef, ind in self._weights:
            c[ind] += coef

        objective = cvxpy.Minimize(c @ x)

        constraints = [0 <= x, x <= 1]
        for coefs, inds, lo, hi in self._constraints:
            expr = 0
            for coef, ind in zip(coefs, inds):
                expr += coef * x[ind]

            if lo == hi:
                util_common.check(lo is not None, 'both bounds None')
                constraints.append(expr == lo)
            else:
                if lo is not None:
                    constraints.append(expr >= lo)
                if hi is not None:
                    constraints.append(expr <= hi)

        prob = cvxpy.Problem(objective, constraints)

        res = prob.solve()

        if prob.status != 'optimal':
            return None

        util_common.check(int(prob.value) == prob.value, 'non-integer objective')

        return (x.value > 0.5), int(prob.value)



class FrontendClingoSolver(_SolverImpl):
    def __init__(self):
        util_common.check(try_import_clingo(), 'clingo not available')

        super().__init__(SOLVER_CLINGO_FE, True, False)

        self._ctl_init()

        self._curr_id = 0
        self._soft_var_weights = {}

    def _ctl_init(self):
        ctl_args = ['--rand-freq=0.2', '--seed=0']
        self._ctl = clingo.Control(ctl_args)

    def _ctl_add_rule(self, rule):
        self._ctl.add('base', [], rule)

    def _ctl_ground(self):
        self._ctl.ground([('base', [])])

    def _ctl_solve(self, on_model):
        self._ctl.solve(on_model=on_model)

    def _help_new_soft_var(self, weight):
        weight_func = 'soft%d' % weight

        if weight in self._soft_var_weights:
            util_common.check(self._soft_var_weights[weight] == weight_func, 'weight and weight_func mismatch')
        else:
            self._soft_var_weights[weight] = weight_func

        self._curr_id += 1
        soft_var = '%s(%d)' % (weight_func, self._curr_id)
        self._ctl_add_rule('0 { %s } 1.' % soft_var)

        return soft_var

    def _help_new_var(self):
        self._curr_id += 1
        new_var = 'var(%d)' % self._curr_id
        self._ctl_add_rule('0 { %s } 1.' % new_var)

        return new_var

    def _IMPL_negate_var_conj(self, ll):
        return 'not %s' % ll

    def _IMPL_make_var(self):
        return self._help_new_var()

    def _IMPL_make_conj(self, lls):
        if len(lls) == 1:
            return lls[0]
        else:
            conj_var = self._help_new_var()
            for ll in lls:
                self._ctl_add_rule('%s :- %s.' % (ll, conj_var))
            self._ctl_add_rule('%s :- %s.' % (conj_var, ','.join(lls)))
            return conj_var

    def _IMPL_cnstr_implies_disj(self, in_ll, out_lls, weight):
        soft_var = []
        if weight is not None:
            soft_var = [self._help_new_soft_var(weight)]

        self._ctl_add_rule('%s :- %s.' % (';'.join(out_lls + soft_var), in_ll))

    def _IMPL_cnstr_count(self, lls, lo, hi, weight):
        soft_var_body = None
        def get_soft_var_body():
            nonlocal soft_var_body
            if soft_var_body is None:
                if weight is None:
                    soft_var_body = ''
                else:
                    soft_var_body = ' :- not %s' % self._help_new_soft_var(weight)
            return soft_var_body

        if len(lls) == 0:
            pass

        elif len(lls) == 1:
            if lo == 0 and hi == 1:
                pass
            elif lo == 0 and hi == 0:
                self._ctl_add_rule('not %s%s.' % (lls[0], get_soft_var_body()))
            elif lo == 1 and hi == 1:
                self._ctl_add_rule('%s%s.' % (lls[0], get_soft_var_body()))
            else:
                util_common.check(False, 'count vars')

        else:
            lo_str = ''
            if lo > 0:
                lo_str = str(lo) + ' '

            hi_str = ''
            if hi < len(lls):
                hi_str = ' ' + str(hi)

            if lo_str != '' or hi_str != '':
                lls = [str(ii) + ':' + ll for ii, ll in enumerate(lls)]
                self._ctl_add_rule('%s#count{ %s }%s%s.' % (lo_str, ';'.join(lls), hi_str, get_soft_var_body()))

    def _IMPL_solve(self):
        def on_model(_m):
            util_common.write_time('.')

            if len(_m.cost) == 0:
                self._objective = 0
            else:
                util_common.check(len(_m.cost) == 1, 'cost length')
                self._objective = _m.cost[0]

            self._result = {}
            for symbol in _m.symbols(atoms=True):
                self._result[str(symbol)] = None

        for weight, weight_func in self._soft_var_weights.items():
            self._ctl_add_rule('#minimize{ %d, ID : %s(ID) }.' % (weight, weight_func))

        self._ctl_ground()
        self._ctl_solve(on_model)
        util_common.write_time('\n')

        return self._result is not None

    def _IMPL_get_var(self, vv):
        return vv in self._result



class BackendClingoSolver(_SolverImpl):
    def __init__(self):
        util_common.check(try_import_clingo(), 'clingo not available')

        super().__init__(SOLVER_CLINGO_BE, True, False)

        ctl_args = ['--rand-freq=0.2', '--seed=0']
        self._ctl = clingo.Control(ctl_args)

        self._all_atoms = []

    def _help_new_var(self, be):
        ret = be.add_atom()
        self._all_atoms.append(ret)
        be.add_rule([ret], choice=True)
        return ret

    def _IMPL_negate_var_conj_for_implies_out(self, ll):
        # TODO: is there a better way to get negative literals in the head of a rule?
        with self._ctl.backend() as be:
            opp_ll = self._help_new_var(be)
            # one is true, one is false
            be.add_rule([], [ll, opp_ll])
            be.add_rule([], [-ll, -opp_ll])
            return opp_ll

    def _IMPL_negate_var_conj(self, ll):
        return -ll

    def _IMPL_make_var(self):
        with self._ctl.backend() as be:
            return self._help_new_var(be)

    def _IMPL_make_conj(self, lls):
        if len(lls) == 1:
            return lls[0]
        else:
            with self._ctl.backend() as be:
                conj_var = self._help_new_var(be)
                for ll in lls:
                    be.add_rule([], [-ll, conj_var])
                be.add_rule([conj_var], lls)
                return conj_var

    def _IMPL_cnstr_implies_disj(self, in_ll, out_lls, weight):
        with self._ctl.backend() as be:
            soft_var = []
            if weight is not None:
                soft_var = [self._help_new_var(be)]

            be.add_rule(out_lls + soft_var, [in_ll])

            if len(soft_var) != 0:
                util_common.check(len(soft_var) == 1, 'soft var')
                be.add_minimize(1, [(soft_var[0], weight)])

    def _IMPL_cnstr_count(self, lls, lo, hi, weight):
        with self._ctl.backend() as be:
            soft_var = None
            def get_soft_var():
                nonlocal soft_var
                if soft_var is None:
                    if weight is None:
                        soft_var = []
                    else:
                        soft_var = [self._help_new_var(be)]
                        be.add_minimize(1, [(soft_var[0], weight)])
                return soft_var

            if len(lls) == 0:
                pass

            elif len(lls) == 1:
                if lo == 0 and hi == 1:
                    pass
                elif lo == 0 and hi == 0:
                    be.add_rule(get_soft_var(), [lls[0]])
                elif lo == 1 and hi == 1:
                    be.add_rule(get_soft_var(), [-lls[0]])
                else:
                    util_common.check(False, 'count vars')

            else:
                if lo == 0:
                    pass
                elif lo == 1:
                    be.add_rule(get_soft_var(), [-ll for ll in lls])
                else:
                    be.add_weight_rule(get_soft_var(), len(lls) + 1 - lo, [(-ll, 1) for ll in lls])

                if hi < len(lls):
                    be.add_weight_rule(get_soft_var(), hi + 1, [(ll, 1) for ll in lls])

    def _IMPL_solve(self):
        def on_model(_m):
            util_common.write_time('.')

            if len(_m.cost) == 0:
                self._objective = 0
            else:
                util_common.check(len(_m.cost) == 1, 'cost length')
                self._objective = _m.cost[0]

            self._result = {}
            for atom in self._all_atoms:
                if _m.is_true(atom):
                    self._result[atom] = None

        self._ctl.solve(on_model=on_model)
        util_common.write_time('\n')

        return self._result is not None

    def _IMPL_get_var(self, vv):
        return vv in self._result



class _GenericSatSolver(_SolverImpl):
    def __init__(self, solver_id, supports_weights):
        super().__init__(solver_id, supports_weights, False)

        self._curr_id = 0

    def _next_var(self):
        self._curr_id += 1
        return self._curr_id

    def _IMPL_negate_var_conj(self, ll):
        return -ll

    def _IMPL_make_var(self):
        return self._next_var()

    def _IMPL_make_conj(self, lls):
        if len(lls) == 1:
            return lls[0]
        else:
            conj_var = self._next_var()
            for ll in lls:
                self._IMPL_SAT_add_clause([-conj_var, ll], None) # ... conj_var -> A ll
            self._IMPL_SAT_add_clause([-ll for ll in lls] + [conj_var], None) # A lls -> conj_var
            return conj_var

    def _IMPL_cnstr_implies_disj(self, in_ll, out_lls, weight):
        if not self.supports_weights():
            util_common.check(weight is None, 'solver does not support weights')

        self._IMPL_SAT_add_clause([-in_ll] + out_lls, weight)

    def _IMPL_cnstr_count(self, lls, lo, hi, weight):
        if not self.supports_weights():
            util_common.check(weight is None, 'solver does not support weights')

        if len(lls) == 0:
            pass

        elif len(lls) == 1:
            if lo == 0 and hi == 1:
                pass
            elif lo == 0 and hi == 0:
                self._IMPL_SAT_add_clause([-lls[0]], weight)
            elif lo == 1 and hi == 1:
                self._IMPL_SAT_add_clause([lls[0]], weight)
            else:
                util_common.check(False, 'count vars')

        else:
            if lo == 0:
                pass
            elif lo == 1:
                self._IMPL_SAT_add_clause(lls, weight)
            else:
                self._IMPL_SAT_add_atmost([-ll for ll in lls], len(lls) - lo, weight)

            if hi < len(lls):
                self._IMPL_SAT_add_atmost(lls, hi, weight)

    def _IMPL_solve(self):
        result = self._IMPL_SAT_solve()
        if result is None:
            return False
        else:
            self._result, self._objective = result
            return True

    def _IMPL_get_var(self, vv):
        return self._result[vv - 1] > 0

    def _IMPL_SAT_add_clause(self, lls, weight):
        util_common.check(False, '_IMPL_SAT_add_clause unimplemented')

    def _IMPL_SAT_add_atmost(self, lls, atmost, weight):
        util_common.check(False, '_IMPL_SAT_add_atmost unimplemented')

    def _IMPL_SAT_solve(self):
        util_common.check(False, '_IMPL_SAT_solve unimplemented')

class _UnweightedPySatSatSolver(_GenericSatSolver):
    def __init__(self, solver_id, pysat_name):
        util_common.check(try_import_pysat(), 'pysat not available')

        super().__init__(solver_id, False)

        self._s = pysat.solvers.Solver(name=pysat_name)

    def _IMPL_SAT_add_clause(self, lls, weight):
        util_common.check(weight is None, 'solver does not support weights')
        self._s.add_clause(lls)

    def _IMPL_SAT_add_atmost(self, lls, atmost, weight):
        util_common.check(weight is None, 'solver does not support weights')
        self._s.add_atmost(lls, atmost)

    def _IMPL_SAT_solve(self):
        if not self._s.solve():
            return None

        result = self._s.get_model()

        for ii, vv in enumerate(result):
            util_common.check(abs(vv) - 1 == ii, 'result index')

        return result, 0

class MiniCardPySatSolver(_UnweightedPySatSatSolver):
    def __init__(self):
        util_common.check(try_import_pysat(), 'pysat not available')

        super().__init__(SOLVER_PYSAT_MC, 'minicard')

class GlueCard41PySatSolver(_UnweightedPySatSatSolver):
    def __init__(self):
        util_common.check(try_import_pysat(), 'pysat not available')

        super().__init__(SOLVER_PYSAT_GC41, 'gluecard41')

class _CardEncodingPySatSolver(_GenericSatSolver):
    def __init__(self, solver_id, supports_weights, formula):
        util_common.check(try_import_pysat(), 'pysat not available')

        super().__init__(solver_id, supports_weights)

        self._formula = formula

        self._pysat_encoding = pysat.card.EncType.kmtotalizer

    def _IMPL_cnstr_count(self, lls, lo, hi, weight):
        if len(lls) <= 1:
            _GenericSatSolver._IMPL_cnstr_count(self, lls, lo, hi, weight)

        else:
            label_var_cls = []

            if lo == 0:
                pass
            elif lo == 1:
                self._IMPL_SAT_add_clause(lls, weight)
            else:
                if weight is not None and len(label_var_cls) == 0:
                    label_var_cls = [self._next_var()]

                cnf = pysat.card.CardEnc.atleast(lits=lls, bound=lo, top_id=self._curr_id, encoding=self._pysat_encoding)
                util_common.check(len(cnf.atmosts) == 0, 'atmosts in card encoding')
                for cls in cnf.clauses:
                    self._IMPL_SAT_add_clause(cls + label_var_cls, None)
                    self._curr_id = max(self._curr_id, max([abs(cll) for cll in cls]))

            if hi < len(lls):
                if weight is not None and len(label_var_cls) == 0:
                    label_var_cls = [self._next_var()]

                cnf = pysat.card.CardEnc.atmost(lits=lls, bound=hi, top_id=self._curr_id, encoding=self._pysat_encoding)
                util_common.check(len(cnf.atmosts) == 0, 'atmosts in card encoding')
                for cls in cnf.clauses:
                    self._IMPL_SAT_add_clause(cls + label_var_cls, None)
                    self._curr_id = max(self._curr_id, max([abs(cll) for cll in cls]))

            for label_var in label_var_cls:
                self._IMPL_SAT_add_clause([-label_var], weight)

    def _IMPL_SAT_add_clause(self, lls, weight):
        extra_args = {}
        if weight is not None:
            extra_args['weight'] = weight
        self._formula.append(lls, **extra_args)

class CnfWriteDimacsSolver(_CardEncodingPySatSolver, _SolverFilename):
    def __init__(self):
        util_common.check(try_import_pysat(), 'pysat not available')

        _CardEncodingPySatSolver.__init__(self, SOLVER_DIMACS_WRITE_CNF, False, pysat.formula.CNF())
        _SolverFilename.__init__(self)

    def _IMPL_SAT_solve(self):
        self.file_write(self._formula.to_dimacs())
        return None

class WcnfWriteDimacsSolver(_CardEncodingPySatSolver, _SolverFilename):
    def __init__(self):
        util_common.check(try_import_pysat(), 'pysat not available')

        _CardEncodingPySatSolver.__init__(self, SOLVER_DIMACS_WRITE_CNF, True, pysat.formula.WCNF())
        _SolverFilename.__init__(self)

    def _IMPL_SAT_solve(self):
        self.file_write(self._formula.to_dimacs())
        return None

class ReadDimacsSolver(_CardEncodingPySatSolver, _SolverFilename):
    def __init__(self):
        util_common.check(try_import_pysat(), 'pysat not available')

        _CardEncodingPySatSolver.__init__(self, SOLVER_DIMACS_WRITE_CNF, True, pysat.formula.WCNF())
        _SolverFilename.__init__(self)

    def _IMPL_SAT_solve(self):
        data = self.file_read()

        v_find_re = re.compile(r'-?\d+')
        v_re = re.compile(r'^v((?:\s+-?\d+)+)\s*$')

        v_match = None
        for line in data.split('\n'):
            if (m := v_re.match(line)) is not None:
                v_match = m

        if v_match is None:
            return None

        result = []
        v_nums = re.findall(v_find_re, v_match.group(1))
        for ii, v_num in enumerate(v_nums):
            v_num_int = int(v_num)
            if v_num_int == 0:
                util_common.check(ii + 1 == len(v_nums), '0 before end')
                break
            util_common.check(ii + 1 == abs(v_num_int), 'variables out of order')
            result.append(v_num_int)

        def _satisfies(_cls, _vvs):
            for _cc in _cls:
                if (_cc > 0) == (_vvs[abs(_cc) - 1] > 0):
                    return True
            return False

        for cls in self._formula.hard:
            if not _satisfies(cls, result):
                return None

        objective = 0
        for cls, wt in zip(self._formula.soft, self._formula.wght):
            if not _satisfies(cls, result):
                objective += wt

        return result, objective

class _OptionsPySatSolver(_CardEncodingPySatSolver):
    def __init__(self, solver_id, formula):
        super().__init__(solver_id, True, formula)

        self._solve_options = {}

class _BoolOnlyPySatSolver(_OptionsPySatSolver):
    def __init__(self, solver_id):
        util_common.check(try_import_pysat(), 'pysat not available')

        super().__init__(solver_id, pysat.formula.WCNF())

class _FullPySatSolver(_OptionsPySatSolver):
    def __init__(self, solver_id):
        util_common.check(try_import_pysat(), 'pysat not available')

        super().__init__(solver_id, pysat.formula.WCNFPlus())

        self._solve_options['solver'] = 'minicard'

    def _IMPL_cnstr_count(self, lls, lo, hi, weight):
        if weight is None: # PySat currently only supports hard cardinality constraints
            return _GenericSatSolver._IMPL_cnstr_count(self, lls, lo, hi, weight)
        else: # fall back to encoding
            return _CardEncodingPySatSolver._IMPL_cnstr_count(self, lls, lo, hi, weight)

    def _IMPL_SAT_add_atmost(self, lls, atmost, weight):
        util_common.check(weight is None, 'solver does not support weighted atmost')
        self._formula.append([lls, atmost], is_atmost=True, weight=weight)

class _PySatFMSolveFunc:
    def _IMPL_SAT_solve(self):
        fm = pysat.examples.fm.FM(self._formula, **self._solve_options)
        if fm.compute():
            return fm.model, fm.cost

        return None

class FMPySatSolver(_PySatFMSolveFunc, _FullPySatSolver):
    def __init__(self):
        _FullPySatSolver.__init__(self, SOLVER_PYSAT_FM)

class BoolOnlyFMPySatSolver(_PySatFMSolveFunc, _BoolOnlyPySatSolver):
    def __init__(self):
        _BoolOnlyPySatSolver.__init__(self, SOLVER_PYSAT_FM_BOOL)

class _PySatRC2SolveFunc:
    def _IMPL_SAT_solve(self):
        with pysat.examples.rc2.RC2(self._formula, **self._solve_options) as rc2:
            for m in rc2.enumerate():
                return list(m), rc2.cost

        return None

class RC2PySatSolver(_PySatRC2SolveFunc, _FullPySatSolver):
    def __init__(self):
        _FullPySatSolver.__init__(self, SOLVER_PYSAT_RC2)

class BoolOnlyRC2PySatSolver(_PySatRC2SolveFunc, _BoolOnlyPySatSolver):
    def __init__(self):
        _BoolOnlyPySatSolver.__init__(self, SOLVER_PYSAT_RC2_BOOL)
