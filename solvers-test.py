import os, sys
import util, solvers

if __name__ == '__main__':
    if len(sys.argv) > 1:
        solvers_to_test = sys.argv[1:]
    else:
        solvers_to_test = list(sorted(set(solvers.SOLVER_LIST) - set(solvers.SOLVER_NOTEST_LIST)))

    os.environ['STG_MUTE_TIME'] = '1'
    os.environ['STG_MUTE_PORT'] = '1'

    tests = []

    def setup(solver, wt, a, b):
        solver.cnstr_count([a], False, 1, 1, wt)
        solver.cnstr_implies_disj(a, False, [b], False, wt)
    tests.append((2, setup, [False, False]))

    def setup(solver, wt, a, b, c):
        solver.cnstr_implies_disj(a, True, [b], True, wt)
        solver.cnstr_implies_disj(b, True, [c], True, wt)
        solver.cnstr_count([a, b, c], True, 2, 2, wt)
    tests.append((3, setup, [False, True, True]))

    def setup(solver, wt, a, b, c):
        solver.cnstr_count([a, b, c], True, 3, 3, wt)
    tests.append((3, setup, [True, True, True]))

    def setup(solver, wt, a, b, c):
        solver.cnstr_count([a, b, c], False, 3, 3, wt)
    tests.append((3, setup, [False, False, False]))

    def setup(solver, wt, a, b, c):
        solver.cnstr_count([a, b], True, 1, 1, wt)
        solver.cnstr_count([b], True, 0, 0, wt)
        solver.cnstr_implies_disj(a, True, [b, c], True, wt)
    tests.append((3, setup, [True, False, True]))

    def setup(solver, wt, a, b, c):
        d = solver.make_conj([a, b, c], [True, False, True])
        solver.cnstr_count([d], True, 1, 1, wt)
    tests.append((3, setup, [True, False, True]))

    def setup(solver, wt, a, b, c):
        d = solver.make_conj([a, b, c], False)
        solver.cnstr_count([b], False, 1, 1, wt)
        solver.cnstr_count([c], True, 0, 0, wt)
        solver.cnstr_count([d], False, 1, 1, wt)
    tests.append((3, setup, [True, False, False]))

    def setup(solver, wt, a, b, c, d):
        solver.cnstr_count([a, b, c, d], False, 3, 4, wt)
        solver.cnstr_count([a], True, 1, 1, wt)
    tests.append((4, setup, [True, False, False, False]))

    def setup(solver, wt, a, b, c, d):
        solver.cnstr_count([a, b], True, 1, 1, wt)
        solver.cnstr_count([b], False, 1, 1, wt)
        solver.cnstr_count([d], False, 1, 1, wt)
        solver.cnstr_count([a, b, c, d], [True, True, False, False], 2, 2, wt)
    tests.append((4, setup, [True, False, True, False]))

    for solver_id in solvers_to_test:
        for use_portfolio in [False, True]:
            for use_weight in [None, 1]:
                if solver_id in [solvers.SOLVER_CVC5, solvers.SOLVER_PYSAT_MC] and use_weight is not None:
                    continue

                print(solver_id, use_portfolio, use_weight)

                for nvars, setup, expect in tests:
                    print('.', end='')
                    if use_portfolio:
                        solver = solvers.PortfolioSolver([solver_id], None)
                    else:
                        solver = solvers.solver_id_to_solver(solver_id)
                    vvs = [solver.make_var() for ii in range(nvars)]
                    setup(solver, use_weight, *vvs)
                    solver.solve()
                    res = [solver.get_var(vv) for vv in vvs]
                    util.check(res == expect, 'var')
                    obj = solver.get_objective()
                    util.check(obj == 0, 'objective')
                print()
