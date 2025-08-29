set -e
set -x

export STG_MUTE_TIME=1

rm -rf work
mkdir -p work

# wfc-flowers
python input2tile.py --outfile work/wfc-flowers.tile --imagefile levels/wfc/wfc-flowers.png --tilesize 2
python tile2scheme.py --outfile work/wfc-flowers.scheme --tilefile work/wfc-flowers.tile --count-divs 1 1 --pattern block-noout,3

! python scheme2output.py --outfile work/wfc-flowers-soft --schemefile work/wfc-flowers.scheme --pattern-hard --count-soft --size 8 8 --solver dimacs-write-wcnf --solver-file work/wfc-flowers-soft.wcnf
rc2.py -vv work/wfc-flowers-soft.wcnf > work/wfc-flowers-soft.soln 2> /dev/null
python scheme2output.py --outfile work/wfc-flowers-soft --schemefile work/wfc-flowers.scheme --pattern-hard --count-soft --size 8 8 --solver dimacs-read --solver-file work/wfc-flowers-soft.soln

! python scheme2output.py --outfile work/wfc-flowers-hard --schemefile work/wfc-flowers.scheme --pattern-hard --count-hard --size 14 14 --solver dimacs-write-cnf --solver-file work/wfc-flowers-hard.cnf
rc2.py -vv work/wfc-flowers-hard.cnf > work/wfc-flowers-hard.soln 2> /dev/null
python scheme2output.py --outfile work/wfc-flowers-hard --schemefile work/wfc-flowers.scheme --pattern-hard --count-hard --size 14 14 --solver dimacs-read --solver-file work/wfc-flowers-hard.soln
