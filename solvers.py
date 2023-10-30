import json, multiprocessing, queue, random, sys
import util

try:
    available_z3 = False
    import z3
    available_z3 = True
except ImportError:
    pass

try:
    available_cvc5 = False
    import cvc5.pythonic
    available_cvc5 = True
except ImportError:
    pass

try:
    available_clingo = False
    import clingo
    available_clingo = True
except ImportError:
    pass

try:
    available_pysat = False
    import pysat.card
    import pysat.formula
    import pysat.examples.fm
    import pysat.examples.rc2
    import pysat.solvers
    available_pysat = True
except ImportError:
    pass



SOLVER_PRINT          = 'print'
SOLVER_Z3_OPTIMIZE    = 'z3-opt'
SOLVER_Z3_SOLVE       = 'z3-slv'
SOLVER_CVC5           = 'cvc5'
SOLVER_CLINGO_FE      = 'clingo-fe'
SOLVER_CLINGO_BE      = 'clingo-be'
SOLVER_PYSAT_FM       = 'pysat-fm'
SOLVER_PYSAT_RC2      = 'pysat-rc2'
SOLVER_PYSAT_FM_BOOL  = 'pysat-fm-boolonly'
SOLVER_PYSAT_RC2_BOOL = 'pysat-rc2-boolonly'
SOLVER_PYSAT_MC       = 'pysat-minicard'
SOLVER_LIST           = [SOLVER_PRINT, SOLVER_Z3_OPTIMIZE, SOLVER_Z3_SOLVE, SOLVER_CVC5, SOLVER_CLINGO_FE, SOLVER_CLINGO_BE, SOLVER_PYSAT_FM, SOLVER_PYSAT_RC2, SOLVER_PYSAT_FM_BOOL, SOLVER_PYSAT_RC2_BOOL, SOLVER_PYSAT_MC]
SOLVER_NOTEST_LIST    = [SOLVER_PRINT]

Z3_OPTION_SOLVE       = 'solve'
Z3_OPTION_OPTIMIZE    = 'optimize'

PYSAT_OPTION_CARD     = 'card'
PYSAT_OPTION_BOOLONLY = 'boolonly'
PYSAT_ENCODING        = pysat.card.EncType.kmtotalizer



def solver_id_to_solver(solver_id):
    if solver_id == SOLVER_PRINT:
        return PrintSolver()
    elif solver_id == SOLVER_Z3_OPTIMIZE:
        return Z3SolverOptimize()
    elif solver_id == SOLVER_Z3_SOLVE:
        return Z3SolverSolve()
    elif solver_id == SOLVER_CVC5:
        return CVC5Solver()
    elif solver_id == SOLVER_CLINGO_FE:
        return ClingoFrontendSolver()
    elif solver_id == SOLVER_CLINGO_BE:
        return ClingoBackendSolver()
    elif solver_id == SOLVER_PYSAT_FM:
        return PySatSolverFM()
    elif solver_id == SOLVER_PYSAT_RC2:
        return PySatSolverRC2()
    elif solver_id == SOLVER_PYSAT_FM_BOOL:
        return PySatSolverFMBoolOnly()
    elif solver_id == SOLVER_PYSAT_RC2_BOOL:
        return PySatSolverRC2BoolOnly()
    elif solver_id == SOLVER_PYSAT_MC:
        return PySatSolverMiniCard()
    else:
        util.check(False, 'solver ' + solver_id + ' unrecognized.')



class Solver:
    def __init__(self, solver_id):
        self._solver_id = solver_id

    def get_id(self):
        return self._solver_id

    def make_var(self):
        util.check(False, 'unimplemented')

    def make_conj(self, vvs, settings):
        util.check(False, 'unimplemented')

    def cnstr_implies_disj(self, in_vv, in_vv_setting, out_vvs, out_vv_settings, weight):
        util.check(False, 'unimplemented')

    def cnstr_count(self, vvs, settings, lo, hi, weight):
        util.check(False, 'unimplemented')

    def solve(self):
        util.check(False, 'unimplemented')

    def get_var(self, vv):
        util.check(False, 'unimplemented')

    def get_objective(self):
        util.check(False, 'unimplemented')

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
    util.check(type(vv) == tuple and len(vv) == 2 and vv[0] == 'v', 'unwrap')
    return vv[1]

def _unwrap_conj(vv):
    util.check(type(vv) == tuple and len(vv) == 2 and vv[0] == 'c', 'unwrap')
    return vv[1]

def _unwrap_any(vv):
    util.check(type(vv) == tuple and len(vv) == 2 and vv[0] in ['v', 'c'], 'unwrap')
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
        util.check(len(vvs) == len(settings), 'different vvs and settings lengths')

    return [_unwrap_lit_lconj(vv, setting, negate_func) for vv, setting in zip(vvs, settings)]

def _is_xform_t(vv):
    return vv[0] in ['t2', 't3']

def _unwrap_xform_t(vv):
    util.check(type(vv) == tuple and vv[0] in ['t2', 't3'], 'unwrap')
    return vv[1:]

def _is_xform_x2(vv):
    return vv[0] in ['x2']

def _unwrap_xform_x2(vv):
    util.check(type(vv) == tuple and vv[0] in ['x2'], 'unwrap')
    return vv[1:]



class SolverImpl(Solver):
    def __init__(self, solver_id, supports_weights, supports_xforms):
        super().__init__(solver_id)

        self._supports_weights = supports_weights
        self._supports_xforms = supports_xforms

        self._result = None
        self._objective = None

    def make_var(self):
        return _wrap_var(self._IMPL_make_var())

    def make_conj(self, vvs, settings):
        util.check(len(vvs) > 0, 'empty conj')

        return _wrap_conj(self._IMPL_make_conj(_unwrap_lit_lconjs(vvs, settings, self._IMPL_negate_var_conj)))

    def cnstr_implies_disj(self, in_vv, in_vv_setting, out_vvs, out_vv_settings, weight):
        if not self._supports_weights:
            util.check(weight is None, 'solver does not support weights')

        return self._IMPL_cnstr_implies_disj(_unwrap_lit_lconj(in_vv, in_vv_setting, self._IMPL_negate_var_conj), _unwrap_lit_lconjs(out_vvs, out_vv_settings, self._IMPL_negate_var_conj_for_implies_out), weight)

    def cnstr_count(self, vvs, settings, lo, hi, weight):
        util.check(0 <= lo and lo <= hi and hi <= len(vvs), 'count')

        if not self._supports_weights:
            util.check(weight is None, 'solver does not support weights')

        return self._IMPL_cnstr_count(_unwrap_lit_lconjs(vvs, settings, self._IMPL_negate_var_conj), lo, hi, weight)

    def solve(self):
        return self._IMPL_solve()

    def get_var(self, vv):
        return self._IMPL_get_var(_unwrap_var(vv))

    def get_objective(self):
        return self._objective

    def supports_weights(self):
        return self._supports_weights

    def supports_xforms(self):
        return self._supports_xforms

    def _IMPL_negate_var_conj_for_implies_out(self, ll):
        return self._IMPL_negate_var_conj(ll)

    def _IMPL_negate_var_conj(self, ll):
        util.check(False, 'unimplemented')

    def _IMPL_make_var(self):
        util.check(False, 'unimplemented')

    def _IMPL_make_conj(self, lls):
        util.check(False, 'unimplemented')

    def _IMPL_cnstr_implies_disj(self, ll_in, lls_out, weight):
        util.check(False, 'unimplemented')

    def _IMPL_cnstr_count(self, lls, lo, hi, weight):
        util.check(False, 'unimplemented')

    def _IMPL_solve(self):
        util.check(False, 'unimplemented')

    def _IMPL_get_var(self, vv):
        util.check(False, 'unimplemented')



class PortfolioSolver(Solver):
    def __init__(self, solver_ids, timeout):
        super().__init__('portfolio:' + ';'.join(solver_ids))

        self._solver_ids = solver_ids
        self._timeout = timeout

        self._solver_var_conjs = []
        self._solver_commands = []

        self._result = None
        self._objective = None

    def make_var(self):
        self._solver_var_conjs.append(_wrap_var(None))
        return len(self._solver_var_conjs) - 1

    def make_conj(self, vvs, settings):
        util.check(len(vvs) > 0, 'empty conj')

        self._solver_var_conjs.append(_wrap_conj((tuple(vvs), settings)))
        return len(self._solver_var_conjs) - 1

    def cnstr_implies_disj(self, in_vv, in_vv_setting, out_vvs, out_vv_settings, weight):
        self._solver_commands.append(('cnstr_implies_disj', (in_vv, in_vv_setting, out_vvs, out_vv_settings, weight)))

    def cnstr_count(self, vvs, settings, lo, hi, weight):
        util.check(0 <= lo and lo <= hi and hi <= len(vvs), 'count')

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
            util.write_portfolio('portfolio timeout\n')

        for proc in procs:
            proc.kill()

        if result is None:
            return False
        else:
            index, self._result, self._objective = result
            util.write_portfolio('portfolio using %d %s\n' % (index, self._solver_ids[index]))
            return True

    def get_var(self, vv):
        return self._result[vv]

    def get_objective(self):
        return self._objective

    @staticmethod
    def run_solver(s_q, s_index, s_solver_id, s_solver_var_conjs, s_solver_commands):
        s_ret = None

        try:
            util.write_portfolio('portfolio starting %d %s\n' % (s_index, s_solver_id))

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
                    util.check(False, 'var_conj')

            random.Random(s_index).shuffle(s_vars_inds)

            for s_ind in s_vars_inds:
                util.check(_is_var(s_solver_var_conjs[s_ind]), 'var')
                s_var_conj_map[s_ind] = s_solver.make_var()

            for s_ind in s_conjs_inds:
                util.check(_is_conj(s_solver_var_conjs[s_ind]), 'conj')
                s_info = _unwrap_conj(s_solver_var_conjs[s_ind])
                s_var_conj_map[s_ind] = s_solver.make_conj(translate_vars(s_info[0]), s_info[1])

            for s_func_name, s_args in s_solver_commands:
                if s_func_name == 'cnstr_implies_disj':
                    s_solver.cnstr_implies_disj(translate_vars(s_args[0]), s_args[1], translate_vars(s_args[2]), s_args[3], s_args[4])
                elif s_func_name == 'cnstr_count':
                    s_solver.cnstr_count(translate_vars(s_args[0]), s_args[1], s_args[2], s_args[3], s_args[4])
                else:
                    util.check(False, 's_func_name')

            if s_solver.solve():
                s_vars_set = {}
                for s_ind, s_var_conj in enumerate(s_solver_var_conjs):
                    if _is_var(s_var_conj):
                        s_vars_set[s_ind] = s_solver.get_var(translate_vars(s_ind))

                s_ret = (s_index, s_vars_set, s_solver.get_objective())

            util.write_portfolio('portfolio finishing %d %s\n' % (s_index, s_solver_id))

        except Exception as e:
            util.write_portfolio('portfolio error %d %s %s\n' % (s_index, s_solver_id, e))

        s_q.put(s_ret)



class PrintSolver(SolverImpl):
    def __init__(self):
        super().__init__(SOLVER_PRINT, True, False)

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
        print(json.dumps(self._output, indent=2))
        return False



class _Z3Solver(SolverImpl):
    def __init__(self, solver_id, solver_option):
        util.check(available_z3, 'z3 not available')

        util.check(solver_option in [Z3_OPTION_OPTIMIZE, Z3_OPTION_SOLVE], 'invalid option for solver: ' + solver_option)

        self._option = solver_option

        if self._option == Z3_OPTION_OPTIMIZE:
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
        if self._option != Z3_OPTION_OPTIMIZE:
            util.check(weight is None, 'solver does not support weights')

        self._help_add_cnstr_weight(z3.Implies(in_ll, z3.Or(*out_lls)), weight)

    def _IMPL_cnstr_count(self, lls, lo, hi, weight):
        if self._option != Z3_OPTION_OPTIMIZE:
            util.check(weight is None, 'solver does not support weights')

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
                util.check(False, 'count vars')

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
        if self._option == Z3_OPTION_OPTIMIZE:
            def on_model(_m):
                util.write_time('.')

            self._s.set_on_model(on_model)

        chk = self._s.check()
        util.write_time('\n')
        util.write_time(str(chk) + '\n')

        if chk == z3.unsat:
            return False

        if chk == z3.unknown:
            util.write_time(str(self._s.reason_unknown()) + '\n')
            return False

        self._result = self._s.model()

        if self._option == Z3_OPTION_OPTIMIZE:
            objs = [self._s.model().evaluate(obj) for obj in self._s.objectives()]
        else:
            objs = []

        if len(objs) == 0:
            self._objective = 0
        else:
            util.check(len(objs) == 1, 'cost length')
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
        util.check(len(xtypes) == 1, 'xform types')
        xtype = next(iter(xtypes))
        util.check(xtype in ['t2', 't3', 'x2'], 'xform types')
        return xtype

    def _xform_xtype_t(self, xtype):
        return xtype in ['t2', 't3']

    def cnstr_ident_dist_xform(self, missing_conds, xforms, minlinfdist):
        def far(_p0, _p1):
            return z3.Or([z3.Or(_i0 - _i1 <= -minlinfdist, _i0 - _i1 >= minlinfdist) for _i0, _i1 in zip(_p0, _p1)])

        missing_conds = [_unwrap_var(vv) for vv in missing_conds]

        util.check(len(missing_conds) == len(xforms), 'lengths')

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
            util.check(len(dxform) == len(xform0) == len(xform1), 'dims')
            if primary:
                xform_apply = z3.And([p1 == p0 + dd for dd, p0, p1 in zip(dxform, xform0, xform1)])
            else:
                xform_apply = close(xform1, [p0 + dd for dd, p0 in zip(dxform, xform0)])

        else:
            xform0 = _unwrap_xform_x2(xform0)
            xform1 = _unwrap_xform_x2(xform1)
            util.check(6 == len(dxform) == len(xform0) == len(xform1), 'dims')
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

class Z3SolverOptimize(_Z3Solver):
    def __init__(self):
        super().__init__(SOLVER_Z3_OPTIMIZE, Z3_OPTION_OPTIMIZE)

class Z3SolverSolve(_Z3Solver):
    def __init__(self):
        super().__init__(SOLVER_Z3_SOLVE, Z3_OPTION_SOLVE)




class CVC5Solver(SolverImpl):
    def __init__(self):
        util.check(available_cvc5, 'cvc5 not available')

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
        util.check(weight is None, 'solver does not support weights')

        if len(out_lls) == 0:
            self._s.add(cvc5.pythonic.Implies(in_ll, False))
        elif len(out_lls) == 1:
            self._s.add(cvc5.pythonic.Implies(in_ll, out_lls[0]))
        else:
            self._s.add(cvc5.pythonic.Implies(in_ll, cvc5.pythonic.Or(*out_lls)))

    def _IMPL_cnstr_count(self, lls, lo, hi, weight):
        util.check(weight is None, 'solver does not support weights')

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
                util.check(False, 'count vars')

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
        util.write_time('\n')
        util.write_time(str(chk) + '\n')

        if chk == cvc5.pythonic.unsat:
            return False

        if chk == cvc5.pythonic.unknown:
            util.write_time(str(self._s.reason_unknown()) + '\n')
            return False

        self._result = self._s.model()
        self._objective = 0

        return True

    def _IMPL_get_var(self, vv):
        return bool(self._result[vv])



class ClingoFrontendSolver(SolverImpl):
    def __init__(self):
        util.check(available_clingo, 'clingo not available')

        super().__init__(SOLVER_CLINGO_FE, True, False)

        self._ctl_init()

        self._curr_id = 0
        self._soft_var_weights = {}

    def _ctl_init(self):
        args = ['--rand-freq=0.2', '--seed=0']
        self._ctl = clingo.Control(args)

    def _ctl_add_rule(self, rule):
        self._ctl.add('base', [], rule)

    def _ctl_ground(self):
        self._ctl.ground([('base', [])])

    def _ctl_solve(self, on_model):
        self._ctl.solve(on_model=on_model)

    def _help_new_soft_var(self, weight):
        weight_func = 'soft%d' % weight

        if weight in self._soft_var_weights:
            util.check(self._soft_var_weights[weight] == weight_func, 'weight and weight_func mismatch')
        else:
            self._soft_var_weights[weight] = weight_func

        self._curr_id += 1
        soft_var = '%s(%d)' % (weight_func, self._curr_id)
        self._ctl_add_rule('0{ %s }1.' % soft_var)

        return soft_var

    def _help_new_var(self):
        self._curr_id += 1
        new_var = 'var(%d)' % self._curr_id
        self._ctl_add_rule('0{ %s }1.' % new_var)

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
                util.check(False, 'count vars')

        else:
            lo_str = ''
            if lo > 0:
                lo_str = str(lo)

            hi_str = ''
            if hi < len(lls):
                hi_str = str(hi)

            if lo_str != '' or hi_str != '':
                self._ctl_add_rule('%s{ %s }%s%s.' % (lo_str, ';'.join(lls), hi_str, get_soft_var_body()))

    def _IMPL_solve(self):
        def on_model(_m):
            util.write_time('.')

            if len(_m.cost) == 0:
                self._objective = 0
            else:
                util.check(len(_m.cost) == 1, 'cost length')
                self._objective = _m.cost[0]

            self._result = {}
            for symbol in _m.symbols(atoms=True):
                self._result[str(symbol)] = None

        for weight, weight_func in self._soft_var_weights.items():
            self._ctl_add_rule('#minimize{ %d, ID : %s(ID) }.' % (weight, weight_func))

        self._ctl_ground()
        self._ctl_solve(on_model)
        util.write_time('\n')

        return self._result is not None

    def _IMPL_get_var(self, vv):
        return vv in self._result



class ClingoBackendSolver(SolverImpl):
    def __init__(self):
        util.check(available_clingo, 'clingo not available')

        super().__init__(SOLVER_CLINGO_BE, True, False)

        self._ctl = clingo.Control()

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
                util.check(len(soft_var) == 1, 'soft var')
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
                    util.check(False, 'count vars')

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
            util.write_time('.')

            if len(_m.cost) == 0:
                self._objective = 0
            else:
                util.check(len(_m.cost) == 1, 'cost length')
                self._objective = _m.cost[0]

            self._result = {}
            for atom in self._all_atoms:
                if _m.is_true(atom):
                    self._result[atom] = None

        self._ctl.solve(on_model=on_model)
        util.write_time('\n')

        return self._result is not None

    def _IMPL_get_var(self, vv):
        return vv in self._result



class PySatSolverMiniCard(SolverImpl):
    def __init__(self):
        util.check(available_pysat, 'pysat not available')

        super().__init__(SOLVER_PYSAT_MC, False, False)

        self._s = pysat.solvers.Solver(name='mc')

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
                self._s.add_clause([-conj_var, ll]) # ... conj_var -> A ll
            self._s.add_clause([-ll for ll in lls] + [conj_var]) # A lls -> conj_var
            return conj_var

    def _IMPL_cnstr_implies_disj(self, in_ll, out_lls, weight):
        util.check(weight is None, 'solver does not support weights')

        self._s.add_clause([-in_ll] + out_lls)

    def _IMPL_cnstr_count(self, lls, lo, hi, weight):
        util.check(weight is None, 'solver does not support weights')

        if len(lls) == 0:
            pass

        elif len(lls) == 1:
            if lo == 0 and hi == 1:
                pass
            elif lo == 0 and hi == 0:
                self._s.add_clause([-lls[0]])
            elif lo == 1 and hi == 1:
                self._s.add_clause([lls[0]])
            else:
                util.check(False, 'count vars')

        else:
            if lo == 0:
                pass
            elif lo == 1:
                self._s.add_clause(lls)
            else:
                self._s.add_atmost([-ll for ll in lls], len(lls) - lo)

            if hi < len(lls):
                self._s.add_atmost(lls, hi)

    def _IMPL_solve(self):
        if not self._s.solve():
            return False

        self._result = self._s.get_model()
        self._objective = 0

        return True

    def _IMPL_get_var(self, vv):
        return self._result[vv - 1] > 0



class _PySatSolverWeighted(SolverImpl):
    def __init__(self, solver_id, solver_option):
        util.check(available_pysat, 'pysat not available')

        util.check(solver_option in [PYSAT_OPTION_CARD, PYSAT_OPTION_BOOLONLY], 'invalid option for solver: ' + solver_option)

        super().__init__(solver_id, True, False)

        self._option = solver_option

        if self._option == PYSAT_OPTION_CARD:
            self._wcnf = pysat.formula.WCNFPlus()
        else:
            self._wcnf = pysat.formula.WCNF()

        self._curr_id = 0

    def _help_get_args_dict(self):
        args_dict = {}
        if self._option == PYSAT_OPTION_CARD:
            args_dict['solver'] = 'minicard'
        return args_dict

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
                self._wcnf.append([-conj_var, ll]) # ... conj_var -> A ll
            self._wcnf.append([-ll for ll in lls] + [conj_var]) # A lls -> conj_var
            return conj_var

    def _IMPL_cnstr_implies_disj(self, in_ll, out_lls, weight):
        self._wcnf.append([-in_ll] + out_lls, weight=weight)

    def _IMPL_cnstr_count(self, lls, lo, hi, weight):
        if len(lls) == 0:
            pass

        elif len(lls) == 1:
            if lo == 0 and hi == 1:
                pass
            elif lo == 0 and hi == 0:
                self._wcnf.append([-lls[0]], weight=weight)
            elif lo == 1 and hi == 1:
                self._wcnf.append([lls[0]], weight=weight)
            else:
                util.check(False, 'count vars')

        else:
            if self._option == PYSAT_OPTION_CARD and weight is None: # PySat currently only supports hard cardinality constraints
                if lo == 0:
                    pass
                elif lo == 1:
                    self._wcnf.append(lls)
                else:
                    self._wcnf.append([[-ll for ll in lls], len(lls) - lo], is_atmost=True)

                if hi < len(lls):
                    self._wcnf.append([lls, hi], is_atmost=True)

            else:
                label_var_cls = []

                if lo == 0:
                    pass
                elif lo == 1:
                    self._wcnf.append(lls, weight=weight)
                else:
                    if weight is not None and len(label_var_cls) == 0:
                        label_var_cls = [self._next_var()]

                    cnf = pysat.card.CardEnc.atleast(lits=lls, bound=lo, top_id=self._curr_id, encoding=PYSAT_ENCODING)
                    for cls in cnf:
                        self._wcnf.append(cls + label_var_cls)
                        self._curr_id = max(self._curr_id, max(cls))

                if hi < len(lls):
                    if weight is not None and len(label_var_cls) == 0:
                        label_var_cls = [self._next_var()]

                    cnf = pysat.card.CardEnc.atmost(lits=lls, bound=hi, top_id=self._curr_id, encoding=PYSAT_ENCODING)
                    for cls in cnf:
                        self._wcnf.append(cls + label_var_cls)
                        self._curr_id = max(self._curr_id, max(cls))

                for label_var in label_var_cls:
                    self._wcnf.append([-label_var], weight=weight)

    def _IMPL_solve(self):
        model, cost = self._do_solve()

        if not model:
            return False

        self._result = model
        self._objective = cost

        return True

    def _IMPL_get_var(self, vv):
        return self._result[vv - 1] > 0

class _PySatSolverFM(_PySatSolverWeighted):
    def __init__(self, solver_id, solver_option):
        super().__init__(solver_id, solver_option)

    def _do_solve(self):
        fm = pysat.examples.fm.FM(self._wcnf, **self._help_get_args_dict())
        if fm.compute():
            return fm.model, fm.cost

        return None, None

class PySatSolverFM(_PySatSolverFM):
    def __init__(self):
        super().__init__(SOLVER_PYSAT_FM, PYSAT_OPTION_CARD)

class PySatSolverFMBoolOnly(_PySatSolverFM):
    def __init__(self):
        super().__init__(SOLVER_PYSAT_FM_BOOL, PYSAT_OPTION_BOOLONLY)

class _PySatSolverRC2(_PySatSolverWeighted):
    def __init__(self, solver_id, solver_option):
        super().__init__(solver_id, solver_option)

    def _do_solve(self):
        with pysat.examples.rc2.RC2(self._wcnf, **self._help_get_args_dict()) as rc2:
            for m in rc2.enumerate():
                return list(m), rc2.cost

        return None, None

class PySatSolverRC2(_PySatSolverRC2):
    def __init__(self):
        super().__init__(SOLVER_PYSAT_RC2, PYSAT_OPTION_CARD)

class PySatSolverRC2BoolOnly(_PySatSolverRC2):
    def __init__(self):
        super().__init__(SOLVER_PYSAT_RC2_BOOL, PYSAT_OPTION_BOOLONLY)
