set -e
set -x

export STG_MUTE_TIME=1

rm -rf work
mkdir -p work

# mario tests
python input2tile.py --outfile work/mario-nbr.tile --textfile levels/vglc/mario-1-1-generic.lvl
python tile2scheme.py --outfile work/mario-nbr.scheme --tilefile work/mario-nbr.tile --count-divs 1 1 --pattern nbr-l

python scheme2output.py --outfile work/mario-1-1-TEST --schemefile work/mario-nbr.scheme --size 8 8 --pattern-hard --count-hard --solver pysat-rc2
python scheme2output.py --outfile work/mario-1-1-TEST --schemefile work/mario-nbr.scheme --size 8 8 --pattern-hard --count-hard --solver pysat-rc2-boolonly
python scheme2output.py --outfile work/mario-1-1-TEST --schemefile work/mario-nbr.scheme --size 8 8 --pattern-hard --count-hard --solver pysat-fm
python scheme2output.py --outfile work/mario-1-1-TEST --schemefile work/mario-nbr.scheme --size 8 8 --pattern-hard --count-hard --solver pysat-fm-boolonly
python scheme2output.py --outfile work/mario-1-1-TEST --schemefile work/mario-nbr.scheme --size 8 8 --pattern-hard --count-hard --solver pysat-minicard
python scheme2output.py --outfile work/mario-1-1-TEST --schemefile work/mario-nbr.scheme --size 8 8 --pattern-hard --count-hard --solver pysat-gluecard41
python scheme2output.py --outfile work/mario-1-1-TEST --schemefile work/mario-nbr.scheme --size 8 8 --pattern-hard --count-hard --solver clingo-fe
python scheme2output.py --outfile work/mario-1-1-TEST --schemefile work/mario-nbr.scheme --size 8 8 --pattern-hard --count-hard --solver clingo-be
python scheme2output.py --outfile work/mario-1-1-TEST --schemefile work/mario-nbr.scheme --size 8 8 --pattern-hard --count-hard --solver z3-opt
python scheme2output.py --outfile work/mario-1-1-TEST --schemefile work/mario-nbr.scheme --size 8 8 --pattern-hard --count-hard --solver z3-slv
python scheme2output.py --outfile work/mario-1-1-TEST --schemefile work/mario-nbr.scheme --size 8 8 --pattern-hard --count-hard --solver cvc5
python scheme2output.py --outfile work/mario-1-1-TEST --schemefile work/mario-nbr.scheme --size 8 8 --pattern-hard --count-hard --solver scipy
python scheme2output.py --outfile work/mario-1-1-TEST --schemefile work/mario-nbr.scheme --size 8 8 --pattern-hard --count-hard --solver cvxpy

python scheme2output.py --outfile work/mario-1-1-TEST --schemefile work/mario-nbr.scheme --size 8 8 --pattern-hard --count-hard --reach-start-goal l-r 6 --reach-move platform --solver pysat-rc2
python scheme2output.py --outfile work/mario-1-1-TEST --schemefile work/mario-nbr.scheme --size 8 8 --pattern-hard --count-hard --reach-start-goal l-r 6 --reach-move platform --solver pysat-rc2-boolonly
python scheme2output.py --outfile work/mario-1-1-TEST --schemefile work/mario-nbr.scheme --size 8 8 --pattern-hard --count-hard --reach-start-goal l-r 6 --reach-move platform --solver pysat-fm
python scheme2output.py --outfile work/mario-1-1-TEST --schemefile work/mario-nbr.scheme --size 8 8 --pattern-hard --count-hard --reach-start-goal l-r 6 --reach-move platform --solver pysat-fm-boolonly
python scheme2output.py --outfile work/mario-1-1-TEST --schemefile work/mario-nbr.scheme --size 8 8 --pattern-hard --count-hard --reach-start-goal l-r 6 --reach-move platform --solver pysat-minicard
python scheme2output.py --outfile work/mario-1-1-TEST --schemefile work/mario-nbr.scheme --size 8 8 --pattern-hard --count-hard --reach-start-goal l-r 6 --reach-move platform --solver clingo-fe
python scheme2output.py --outfile work/mario-1-1-TEST --schemefile work/mario-nbr.scheme --size 8 8 --pattern-hard --count-hard --reach-start-goal l-r 6 --reach-move platform --solver clingo-be
python scheme2output.py --outfile work/mario-1-1-TEST --schemefile work/mario-nbr.scheme --size 8 8 --pattern-hard --count-hard --reach-start-goal l-r 6 --reach-move platform --solver z3-opt
python scheme2output.py --outfile work/mario-1-1-TEST --schemefile work/mario-nbr.scheme --size 8 8 --pattern-hard --count-hard --reach-start-goal l-r 6 --reach-move platform --solver z3-slv
python scheme2output.py --outfile work/mario-1-1-TEST --schemefile work/mario-nbr.scheme --size 8 8 --pattern-hard --count-hard --reach-start-goal l-r 6 --reach-move platform --solver cvc5
python scheme2output.py --outfile work/mario-1-1-TEST --schemefile work/mario-nbr.scheme --size 8 8 --pattern-hard --count-hard --reach-start-goal l-r 6 --reach-move platform --solver scipy
python scheme2output.py --outfile work/mario-1-1-TEST --schemefile work/mario-nbr.scheme --size 8 8 --pattern-hard --count-hard --reach-start-goal l-r 6 --reach-move platform --solver cvxpy

python input2tile.py --outfile work/mario-ring.tile --textfile levels/vglc/mario-1-1-generic.lvl
python tile2scheme.py --outfile work/mario-ring.scheme --tilefile work/mario-ring.tile --count-divs 1 1 --pattern ring

python scheme2output.py --outfile work/mario-1-1-TEST --schemefile work/mario-ring.scheme --size 4 4 --pattern-soft   --count-soft   --solver pysat-rc2
python scheme2output.py --outfile work/mario-1-1-TEST --schemefile work/mario-ring.scheme --size 4 4 --pattern-soft   --count-soft   --solver pysat-rc2-boolonly
python scheme2output.py --outfile work/mario-1-1-TEST --schemefile work/mario-ring.scheme --size 4 4 --pattern-soft   --count-soft   --solver pysat-fm
python scheme2output.py --outfile work/mario-1-1-TEST --schemefile work/mario-ring.scheme --size 4 4 --pattern-soft   --count-soft   --solver pysat-fm-boolonly
python scheme2output.py --outfile work/mario-1-1-TEST --schemefile work/mario-ring.scheme --size 4 4 --pattern-soft   --count-soft   --solver clingo-fe
python scheme2output.py --outfile work/mario-1-1-TEST --schemefile work/mario-ring.scheme --size 4 4 --pattern-soft   --count-soft   --solver clingo-be
python scheme2output.py --outfile work/mario-1-1-TEST --schemefile work/mario-ring.scheme --size 4 4 --pattern-soft   --count-soft   --solver z3-opt
python scheme2output.py --outfile work/mario-1-1-TEST --schemefile work/mario-ring.scheme --size 4 4 --pattern-soft   --count-soft   --solver scipy
python scheme2output.py --outfile work/mario-1-1-TEST --schemefile work/mario-ring.scheme --size 4 4 --pattern-soft   --count-soft   --solver cvxpy

python scheme2output.py --outfile work/mario-1-1-TEST --schemefile work/mario-ring.scheme --size 4 4 --pattern-soft 2 --count-soft 9 --solver pysat-rc2
python scheme2output.py --outfile work/mario-1-1-TEST --schemefile work/mario-ring.scheme --size 4 4 --pattern-soft 2 --count-soft 9 --solver pysat-rc2-boolonly
python scheme2output.py --outfile work/mario-1-1-TEST --schemefile work/mario-ring.scheme --size 4 4 --pattern-soft 2 --count-soft 9 --solver pysat-fm
python scheme2output.py --outfile work/mario-1-1-TEST --schemefile work/mario-ring.scheme --size 4 4 --pattern-soft 2 --count-soft 9 --solver pysat-fm-boolonly
python scheme2output.py --outfile work/mario-1-1-TEST --schemefile work/mario-ring.scheme --size 4 4 --pattern-soft 2 --count-soft 9 --solver clingo-fe
python scheme2output.py --outfile work/mario-1-1-TEST --schemefile work/mario-ring.scheme --size 4 4 --pattern-soft 2 --count-soft 9 --solver clingo-be
python scheme2output.py --outfile work/mario-1-1-TEST --schemefile work/mario-ring.scheme --size 4 4 --pattern-soft 2 --count-soft 9 --solver z3-opt
python scheme2output.py --outfile work/mario-1-1-TEST --schemefile work/mario-ring.scheme --size 4 4 --pattern-soft 2 --count-soft 9 --solver scipy
python scheme2output.py --outfile work/mario-1-1-TEST --schemefile work/mario-ring.scheme --size 4 4 --pattern-soft 2 --count-soft 9 --solver cvxpy
