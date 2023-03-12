set -e
set -x

export STG_MUTE_TIME=1

rm -rf work
mkdir -p work

# wfc-flowers
python3 input2tiles.py --outfile work/wfc-flowers_i.tiles --imagefile levels/wfc/wfc-flowers.png --tilesize 2
python3 tiles2scheme.py --outfile work/wfc-flowers_i.scheme --tilefile work/wfc-flowers_i.tiles --countdivs 1 1 --pattern noout-bl-3
python3 scheme2output.py --outfile work/wfc-flowers_i --schemefile work/wfc-flowers_i.scheme --size 15 15

# wfc-skyline
python3 input2tiles.py --outfile work/wfc-skyline_i.tiles --imagefile levels/wfc/wfc-skyline.png --tilesize 2
python3 tiles2scheme.py --outfile work/wfc-skyline_i.scheme --tilefile work/wfc-skyline_i.tiles --countdivs 1 1 --pattern noout-bl-3
python3 scheme2output.py --outfile work/wfc-skyline_i --schemefile work/wfc-skyline_i.scheme --size 15 15

# cave
python3 input2tiles.py --outfile work/cave_ti.tiles --textfile levels/kenney/cave.lvl --imagefile levels/kenney/cave.png --tilesize 16
python3 tiles2scheme.py --outfile work/cave_ti.scheme --tilefile work/cave_ti.tiles --countdivs 1 1 --pattern nbr-plus
python3 scheme2output.py --outfile work/cave_ti --schemefile work/cave_ti.scheme --size 15 15 --reach-move maze --reach-goal br-tl 5

# tomb
python3 input2tiles.py --outfile work/tomb-1_ti.tiles --textfile levels/manual/tomb-1.lvl --imagefile levels/manual/tomb-1.png --tilesize 12
python3 tiles2scheme.py --outfile work/tomb-1_ti.scheme --tilefile work/tomb-1_ti.tiles --pattern nbr-plus
python3 scheme2output.py --outfile work/tomb-1_ti --schemefile work/tomb-1_ti.scheme --size 30 15 --reach-move tomb --reach-goal b-t 6

# supercat
python3 input2tiles.py --outfile work/supercat-1-7_t.tiles --textfile levels/manual/supercat-1-7.lvl
python3 tiles2scheme.py --outfile work/supercat-1-7_t.scheme --tilefile work/supercat-1-7_t.tiles --countdivs 5 5 --pattern diamond
python3 scheme2output.py --outfile work/supercat-1-7 --schemefile work/supercat-1-7_t.scheme --size 20 20 --reach-move supercat --reach-goal b-t 8

python3 input2tiles.py --outfile work/supercat-1-7_i.tiles --imagefile levels/manual/supercat-1-7.png --tilesize 16 --tagfile levels/manual/supercat-1-7.lvl
python3 tiles2scheme.py --outfile work/supercat-1-7_i.scheme --tilefile work/supercat-1-7_i.tiles --pattern nbr-l
python3 scheme2output.py --outfile work/supercat-1-7 --schemefile work/supercat-1-7_i.scheme --tagfile work/supercat-1-7.lvl

# mario - ring
python3 input2tiles.py --outfile work/mario-1-1_t_ring.tiles --textfile levels/vglc/mario-1-1-generic.lvl
python3 tiles2scheme.py --outfile work/mario-1-1_t_ring.scheme --tilefile work/mario-1-1_t_ring.tiles --countdivs 1 1 --pattern ring
python3 scheme2output.py --outfile work/mario-1-1_ring --schemefile work/mario-1-1_t_ring.scheme --size 14 32 --reach-move platform --reach-goal l-r 6

python3 input2tiles.py --outfile work/mario-1-1_i_ring.tiles --imagefile levels/vglc/mario-1-1-clean.png --tilesize 16 --tagfile levels/vglc/mario-1-1-generic.lvl
python3 tiles2scheme.py --outfile work/mario-1-1_i_ring.scheme --tilefile work/mario-1-1_i_ring.tiles --countdivs 7 10 --pattern nbr-l
python3 scheme2output.py --outfile work/mario-1-1_ring --schemefile work/mario-1-1_i_ring.scheme --tagfile work/mario-1-1_ring.lvl

# mario - gram
python3 input2tiles.py --outfile work/mario-1-1_t_gram.tiles --textfile levels/vglc/mario-1-1-generic.lvl
python3 tiles2scheme.py --outfile work/mario-1-1_t_gram.scheme --tilefile work/mario-1-1_t_gram.tiles --countdivs 1 1 --pattern 3gc
python3 scheme2output.py --outfile work/mario-1-1_gram --schemefile work/mario-1-1_t_gram.scheme --size 14 32 --reach-move platform --reach-goal l-r 6

python3 input2tiles.py --outfile work/mario-1-1_i_gram.tiles --imagefile levels/vglc/mario-1-1-clean.png --tilesize 16 --tagfile levels/vglc/mario-1-1-generic.lvl
python3 tiles2scheme.py --outfile work/mario-1-1_i_gram.scheme --tilefile work/mario-1-1_i_gram.tiles --countdivs 7 10 --pattern nbr-l
python3 scheme2output.py --outfile work/mario-1-1_gram --schemefile work/mario-1-1_i_gram.scheme --tagfile work/mario-1-1_gram.lvl

# icarus - ring
python3 input2tiles.py --outfile work/kidicarus-1_t_ring.tiles --textfile levels/vglc/kidicarus-1-doors.lvl
python3 tiles2scheme.py --outfile work/kidicarus-1_t_ring.scheme --tilefile work/kidicarus-1_t_ring.tiles --countdivs 1 1 --pattern ring
python3 scheme2output.py --outfile work/kidicarus-1_ring --schemefile work/kidicarus-1_t_ring.scheme --size 24 16 --reach-move platform --reach-wrap-cols --reach-goal b-t 6

python3 input2tiles.py --outfile work/kidicarus-1_i_ring.tiles --imagefile levels/vglc/kidicarus-1-clean.png --tilesize 16 --tagfile levels/vglc/kidicarus-1-doors.lvl
python3 tiles2scheme.py --outfile work/kidicarus-1_i_ring.scheme --tilefile work/kidicarus-1_i_ring.tiles --countdivs 10 4 --pattern nbr-l
python3 scheme2output.py --outfile work/kidicarus-1_ring --schemefile work/kidicarus-1_i_ring.scheme --tagfile work/kidicarus-1_ring.lvl

# icarus - gram
python3 input2tiles.py --outfile work/kidicarus-1_t_gram.tiles --textfile levels/vglc/kidicarus-1-doors.lvl
python3 tiles2scheme.py --outfile work/kidicarus-1_t_gram.scheme --tilefile work/kidicarus-1_t_gram.tiles --countdivs 1 1 --pattern 2gr
python3 scheme2output.py --outfile work/kidicarus-1_gram --schemefile work/kidicarus-1_t_gram.scheme --size 32 16 --reach-move platform --reach-wrap-cols --reach-goal b-t 6

python3 input2tiles.py --outfile work/kidicarus-1_i_gram.tiles --imagefile levels/vglc/kidicarus-1-clean.png --tilesize 16 --tagfile levels/vglc/kidicarus-1-doors.lvl
python3 tiles2scheme.py --outfile work/kidicarus-1_i_gram.scheme --tilefile work/kidicarus-1_i_gram.tiles --countdivs 10 4 --pattern nbr-l
python3 scheme2output.py --outfile work/kidicarus-1_gram --schemefile work/kidicarus-1_i_gram.scheme --tagfile work/kidicarus-1_gram.lvl

# mario land
python3 input2tiles.py --outfile work/super-mario-land-11_t.tiles --textfile levels/vglc/super-mario-land-11-generic.lvl
python3 tiles2scheme.py --outfile work/super-mario-land-11_t.scheme --tilefile work/super-mario-land-11_t.tiles --countdivs 1 1 --pattern diamond
python3 scheme2output.py --outfile work/super-mario-land-11 --schemefile work/super-mario-land-11_t.scheme --size 16 24 --reach-move platform --reach-goal l-r 6

python3 input2tiles.py --outfile work/super-mario-land-11_i.tiles --imagefile levels/vglc/super-mario-land-11-clean.png --tilesize 8 --tagfile levels/vglc/super-mario-land-11-generic.lvl
python3 tiles2scheme.py --outfile work/super-mario-land-11_i.scheme --tilefile work/super-mario-land-11_i.tiles --pattern block2 # --countdivs 8 10
python3 scheme2output.py --outfile work/super-mario-land-11 --schemefile work/super-mario-land-11_i.scheme --tagfile work/super-mario-land-11.lvl

# zelda
python3 input2tiles.py --outfile work/tloz1-1_ti.tiles --textfile levels/vglc/tloz1-1-doors.lvl --imagefile levels/vglc/tloz1-1.png --tilesize 16
python3 tiles2scheme.py --outfile work/tloz1-1_ti.scheme --tilefile work/tloz1-1_ti.tiles --pattern zgc # --countdivs 6 6
python3 scheme2output.py --outfile work/tloz1-1 --schemefile work/tloz1-1_ti.scheme --size 22 32 --reach-move maze --reach-goal b-t 11 --reach-open-zelda

# mario tests
python3 input2tiles.py --outfile work/mario-1-1-TEST_t.tiles --textfile levels/vglc/mario-1-1-generic.lvl
python3 tiles2scheme.py --outfile work/mario-1-1-TEST_t.scheme --tilefile work/mario-1-1-TEST_t.tiles --countdivs 1 1 --pattern ring

python3 scheme2output.py --outfile work/mario-1-1-TEST --schemefile work/mario-1-1-TEST_t.scheme --size 8 8 --solver pysat-minicard --no-counts
python3 scheme2output.py --outfile work/mario-1-1-TEST --schemefile work/mario-1-1-TEST_t.scheme --size 8 8 --solver cvc5           --no-counts
python3 scheme2output.py --outfile work/mario-1-1-TEST --schemefile work/mario-1-1-TEST_t.scheme --size 4 4 --solver clingo-fe
python3 scheme2output.py --outfile work/mario-1-1-TEST --schemefile work/mario-1-1-TEST_t.scheme --size 4 4 --solver clingo-be
python3 scheme2output.py --outfile work/mario-1-1-TEST --schemefile work/mario-1-1-TEST_t.scheme --size 4 4 --solver z3
python3 scheme2output.py --outfile work/mario-1-1-TEST --schemefile work/mario-1-1-TEST_t.scheme --size 4 4

python3 scheme2output.py --outfile work/mario-1-1-TEST --schemefile work/mario-1-1-TEST_t.scheme --size 8 8                 --solver pysat-minicard --no-counts
python3 scheme2output.py --outfile work/mario-1-1-TEST --schemefile work/mario-1-1-TEST_t.scheme --size 8 8                 --solver cvc5           --no-counts
python3 scheme2output.py --outfile work/mario-1-1-TEST --schemefile work/mario-1-1-TEST_t.scheme --size 4 4 --soft-patterns --solver clingo-fe
python3 scheme2output.py --outfile work/mario-1-1-TEST --schemefile work/mario-1-1-TEST_t.scheme --size 4 4 --soft-patterns --solver clingo-be
python3 scheme2output.py --outfile work/mario-1-1-TEST --schemefile work/mario-1-1-TEST_t.scheme --size 4 4 --soft-patterns --solver z3
python3 scheme2output.py --outfile work/mario-1-1-TEST --schemefile work/mario-1-1-TEST_t.scheme --size 4 4 --soft-patterns

python3 scheme2output.py --outfile work/mario-1-1-TEST --schemefile work/mario-1-1-TEST_t.scheme --size 8 8                 --reach-move platform --reach-goal l-r 6 --solver pysat-minicard --no-counts
python3 scheme2output.py --outfile work/mario-1-1-TEST --schemefile work/mario-1-1-TEST_t.scheme --size 8 8                 --reach-move platform --reach-goal l-r 6 --solver cvc5           --no-counts
python3 scheme2output.py --outfile work/mario-1-1-TEST --schemefile work/mario-1-1-TEST_t.scheme --size 4 4 --soft-patterns --reach-move platform --reach-goal l-r 6 --solver clingo-fe
python3 scheme2output.py --outfile work/mario-1-1-TEST --schemefile work/mario-1-1-TEST_t.scheme --size 4 4 --soft-patterns --reach-move platform --reach-goal l-r 6 --solver clingo-be
python3 scheme2output.py --outfile work/mario-1-1-TEST --schemefile work/mario-1-1-TEST_t.scheme --size 4 4 --soft-patterns --reach-move platform --reach-goal l-r 6 --solver z3
python3 scheme2output.py --outfile work/mario-1-1-TEST --schemefile work/mario-1-1-TEST_t.scheme --size 4 4 --soft-patterns --reach-move platform --reach-goal l-r 6
