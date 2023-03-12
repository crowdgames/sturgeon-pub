import argparse, os, queue, signal, subprocess, tempfile, threading, time
import util
import pysat.formula



def run_portfolio(filename, timeout):
    time_start = time.time()

    solvers = []
    for solver in os.listdir('solvers'):
        solver_filename = os.path.join('solvers', solver)
        if os.path.isfile(solver_filename) and os.access(solver_filename, os.X_OK):
            solvers.append(solver_filename)

    util.check(len(solvers) > 0, 'no solvers found')

    procs = []
    for solver in solvers:
        print('c! starting', solver)
        tfile = tempfile.TemporaryFile()
        proc = subprocess.Popen(solver.split() + [filename], stdout=tfile, stderr=subprocess.STDOUT, encoding='ascii')
        procs.append((solver, proc, tfile))

    wcnf = pysat.formula.WCNF(from_file=filename)


    completed_procs = []

    while True:
        for solver, proc, tfile in procs:
            if proc.poll() != None:
                completed_procs.append((solver, proc, tfile))
        if len(completed_procs) != 0:
            break
        if time.time() - time_start >= timeout:
            break
        time.sleep(0.1)

    if len(completed_procs) == 0:
        print('c! timeout')
        for solver, proc, tfile in procs:
            proc.send_signal(signal.SIGINT)

        for solver, proc, tfile in procs:
            proc.wait()

        completed_procs = procs

    outs = []

    for solver, proc, tfile in completed_procs:
        tfile.seek(0)
        out = tfile.read().decode('ascii')
        tfile.close()
        outs.append((solver, out))

    for solver, proc, tfile in procs:
        proc.kill()

    models = []
    for solver, out in outs:
        print('c output from', solver)
        model = None
        for line in out.split('\n'):
            if len(line) > 0 and line[0] == 'o':
                print(line)
            if len(line) > 0 and line[0] == 'v':
                model = line
        if model != None:
            print('c model from', solver)
            models.append((solver, model))

    if len(models) == 0:
        print('c no models')

    elif len(models) == 1:
        print('c one model')
        solver, model = models[0]
        print('c! using model', solver)
        print(model)

    else:
        print('c multiple models')
        best_model, best_solver, best_unsat = None, None, None

        for solver, model in models:
            vvs = [int(ss) > 0 for ss in model.split()[1:]]
            unsat = 0
            for cls, wt in zip(wcnf.soft, wcnf.wght):
                sat = False
                for ind in cls:
                    if vvs[abs(ind) - 1] == (ind > 0):
                        sat = True
                        break
                if not sat:
                    unsat += wt

            print('c model', solver, unsat)
            if best_unsat == None or unsat < best_unsat:
                best_model, best_solver, best_unsat = model, solver, unsat

        print('c! using model', best_solver)
        print('o', best_unsat)
        print(best_model)



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run a portfolio of DIMACS solvers.')
    parser.add_argument('infile', type=str, help='Input DIMACS file.')
    parser.add_argument('--timeout', type=int, required=True, help='Timeout in seconds.')
    args = parser.parse_args()

    run_portfolio(args.infile, args.timeout)
