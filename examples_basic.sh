set -e
set -x

export STG_MUTE_TIME=1

rm -rf work
mkdir -p work

# wfc-flowers
python input2tile.py --outfile work/wfc-flowers_i.tile --imagefile levels/wfc/wfc-flowers.png --tilesize 2
python tile2scheme.py --outfile work/wfc-flowers_i.scheme --tilefile work/wfc-flowers_i.tile --count-divs 1 1 --pattern noout-bl-3
python scheme2output.py --outfile work/wfc-flowers_i --schemefile work/wfc-flowers_i.scheme --pattern-hard --count-soft --size 15 15

# wfc-skyline
python input2tile.py --outfile work/wfc-skyline_i.tile --imagefile levels/wfc/wfc-skyline.png --tilesize 2
python tile2scheme.py --outfile work/wfc-skyline_i.scheme --tilefile work/wfc-skyline_i.tile --count-divs 1 1 --pattern noout-bl-3
python scheme2output.py --outfile work/wfc-skyline_i --schemefile work/wfc-skyline_i.scheme --pattern-hard --count-soft --size 15 15

# cave
python input2tile.py --outfile work/cave_ti.tile --textfile levels/kenney/cave.lvl --imagefile levels/kenney/cave.png
python tile2scheme.py --outfile work/cave_ti.scheme --tilefile work/cave_ti.tile --count-divs 1 1 --pattern nbr-plus
python scheme2output.py --outfile work/cave_ti --schemefile work/cave_ti.scheme --size 15 15 --pattern-hard --count-soft --reach-start-goal br-tl 5 --reach-move maze

# tomb
python input2tile.py --outfile work/tomb-1_ti.tile --textfile levels/manual/tomb-1.lvl --imagefile levels/manual/tomb-1.png
python tile2scheme.py --outfile work/tomb-1_ti.scheme --tilefile work/tomb-1_ti.tile --pattern nbr-plus
python scheme2output.py --outfile work/tomb-1_ti --schemefile work/tomb-1_ti.scheme --size 30 15 --pattern-hard --reach-start-goal b-t 6 --reach-move tomb

# supercat
python input2tile.py --outfile work/supercat-1-7_t.tile --textfile levels/manual/supercat-1-7.lvl
python tile2scheme.py --outfile work/supercat-1-7_t.scheme --tilefile work/supercat-1-7_t.tile --count-divs 5 5 --pattern diamond
python scheme2output.py --outfile work/supercat-1-7 --schemefile work/supercat-1-7_t.scheme --size 20 20 --pattern-hard --count-soft --reach-start-goal b-t 8 --reach-move supercat-new

python input2tile.py --outfile work/supercat-1-7_i.tile --imagefile levels/manual/supercat-1-7.png --tilesize 16 --tagfile levels/manual/supercat-1-7.lvl
python tile2scheme.py --outfile work/supercat-1-7_i.scheme --tilefile work/supercat-1-7_i.tile --pattern nbr-l
python scheme2output.py --outfile work/supercat-1-7 --schemefile work/supercat-1-7_i.scheme --tagfile work/supercat-1-7.lvl --pattern-hard

# mario - ring
python input2tile.py --outfile work/mario-1-1_t_ring.tile --textfile levels/vglc/mario-1-1-generic.lvl
python tile2scheme.py --outfile work/mario-1-1_t_ring.scheme --tilefile work/mario-1-1_t_ring.tile --count-divs 1 1 --pattern ring
python scheme2output.py --outfile work/mario-1-1_ring --schemefile work/mario-1-1_t_ring.scheme --size 14 32 --pattern-hard --count-soft --reach-start-goal l-r 6 --reach-move platform

python input2tile.py --outfile work/mario-1-1_i_ring.tile --imagefile levels/vglc/mario-1-1-clean.png --tilesize 16 --tagfile levels/vglc/mario-1-1-generic.lvl
python tile2scheme.py --outfile work/mario-1-1_i_ring.scheme --tilefile work/mario-1-1_i_ring.tile --count-divs 7 10 --pattern nbr-l
python scheme2output.py --outfile work/mario-1-1_ring --schemefile work/mario-1-1_i_ring.scheme --tagfile work/mario-1-1_ring.lvl --pattern-hard --count-soft

# mario - ring with template
python scheme2output.py --outfile work/mario-1-1_ring-template --schemefile work/mario-1-1_t_ring.scheme --tagfile levels/vglc/mario-1-1-tag-template.lvl --pattern-soft --count-soft --reach-move platform --reach-start-goal l-r 4

# mario - gram
python input2tile.py --outfile work/mario-1-1_t_gram.tile --textfile levels/vglc/mario-1-1-generic.lvl
python tile2scheme.py --outfile work/mario-1-1_t_gram.scheme --tilefile work/mario-1-1_t_gram.tile --count-divs 1 1 --pattern 3gc
python scheme2output.py --outfile work/mario-1-1_gram --schemefile work/mario-1-1_t_gram.scheme --size 14 32 --pattern-hard --count-soft --reach-start-goal l-r 6 --reach-move platform

python input2tile.py --outfile work/mario-1-1_i_gram.tile --imagefile levels/vglc/mario-1-1-clean.png --tilesize 16 --tagfile levels/vglc/mario-1-1-generic.lvl
python tile2scheme.py --outfile work/mario-1-1_i_gram.scheme --tilefile work/mario-1-1_i_gram.tile --count-divs 7 10 --pattern nbr-l
python scheme2output.py --outfile work/mario-1-1_gram --schemefile work/mario-1-1_i_gram.scheme --tagfile work/mario-1-1_gram.lvl --pattern-hard --count-soft

# icarus - ring
python input2tile.py --outfile work/kidicarus-1_t_ring.tile --textfile levels/vglc/kidicarus-1-doors.lvl
python tile2scheme.py --outfile work/kidicarus-1_t_ring.scheme --tilefile work/kidicarus-1_t_ring.tile --count-divs 1 1 --pattern ring
python scheme2output.py --outfile work/kidicarus-1_ring --schemefile work/kidicarus-1_t_ring.scheme --size 24 16 --pattern-hard --count-soft --reach-start-goal b-t 6 --reach-move platform --reach-wrap-cols

python input2tile.py --outfile work/kidicarus-1_i_ring.tile --imagefile levels/vglc/kidicarus-1-clean.png --tilesize 16 --tagfile levels/vglc/kidicarus-1-doors.lvl
python tile2scheme.py --outfile work/kidicarus-1_i_ring.scheme --tilefile work/kidicarus-1_i_ring.tile --count-divs 10 4 --pattern nbr-l
python scheme2output.py --outfile work/kidicarus-1_ring --schemefile work/kidicarus-1_i_ring.scheme --tagfile work/kidicarus-1_ring.lvl --pattern-hard --count-soft

# icarus - gram
python input2tile.py --outfile work/kidicarus-1_t_gram.tile --textfile levels/vglc/kidicarus-1-doors.lvl
python tile2scheme.py --outfile work/kidicarus-1_t_gram.scheme --tilefile work/kidicarus-1_t_gram.tile --count-divs 1 1 --pattern 2gr
python scheme2output.py --outfile work/kidicarus-1_gram --schemefile work/kidicarus-1_t_gram.scheme --size 32 16 --pattern-hard --count-soft --reach-start-goal b-t 6 --reach-move platform --reach-wrap-cols

python input2tile.py --outfile work/kidicarus-1_i_gram.tile --imagefile levels/vglc/kidicarus-1-clean.png --tilesize 16 --tagfile levels/vglc/kidicarus-1-doors.lvl
python tile2scheme.py --outfile work/kidicarus-1_i_gram.scheme --tilefile work/kidicarus-1_i_gram.tile --count-divs 10 4 --pattern nbr-l
python scheme2output.py --outfile work/kidicarus-1_gram --schemefile work/kidicarus-1_i_gram.scheme --tagfile work/kidicarus-1_gram.lvl --pattern-hard --count-soft

# mario land
python input2tile.py --outfile work/super-mario-land-11_t.tile --textfile levels/vglc/super-mario-land-11-generic.lvl
python tile2scheme.py --outfile work/super-mario-land-11_t.scheme --tilefile work/super-mario-land-11_t.tile --count-divs 1 1 --pattern diamond
python scheme2output.py --outfile work/super-mario-land-11 --schemefile work/super-mario-land-11_t.scheme --size 16 24 --pattern-hard --count-soft --reach-start-goal l-r 6 --reach-move platform

python input2tile.py --outfile work/super-mario-land-11_i.tile --imagefile levels/vglc/super-mario-land-11-clean.png --tilesize 8 --tagfile levels/vglc/super-mario-land-11-generic.lvl
python tile2scheme.py --outfile work/super-mario-land-11_i.scheme --tilefile work/super-mario-land-11_i.tile --pattern block2 # --count-divs 8 10
python scheme2output.py --outfile work/super-mario-land-11 --schemefile work/super-mario-land-11_i.scheme --tagfile work/super-mario-land-11.lvl --pattern-hard

# zelda
python input2tile.py --outfile work/tloz1-1_ti.tile --textfile levels/vglc/tloz1-1-doors.lvl --imagefile levels/vglc/tloz1-1.png
python tile2scheme.py --outfile work/tloz1-1_ti.scheme --tilefile work/tloz1-1_ti.tile --pattern zgc # --count-divs 6 6
python scheme2output.py --outfile work/tloz1-1 --schemefile work/tloz1-1_ti.scheme --size 22 32 --pattern-hard --reach-start-goal b-t 11 --reach-move maze --reach-open-zelda

# mario tests
python input2tile.py --outfile work/mario-nbr.tile --textfile levels/vglc/mario-1-1-generic.lvl
python tile2scheme.py --outfile work/mario-nbr.scheme --tilefile work/mario-nbr.tile --count-divs 1 1 --pattern nbr-l

python scheme2output.py --outfile work/mario-1-1-TEST --schemefile work/mario-nbr.scheme --size 8 8 --pattern-hard --count-hard --solver pysat-rc2
python scheme2output.py --outfile work/mario-1-1-TEST --schemefile work/mario-nbr.scheme --size 8 8 --pattern-hard --count-hard --solver pysat-rc2-boolonly
python scheme2output.py --outfile work/mario-1-1-TEST --schemefile work/mario-nbr.scheme --size 8 8 --pattern-hard --count-hard --solver pysat-fm
python scheme2output.py --outfile work/mario-1-1-TEST --schemefile work/mario-nbr.scheme --size 8 8 --pattern-hard --count-hard --solver pysat-fm-boolonly
python scheme2output.py --outfile work/mario-1-1-TEST --schemefile work/mario-nbr.scheme --size 8 8 --pattern-hard --count-hard --solver pysat-minicard
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
