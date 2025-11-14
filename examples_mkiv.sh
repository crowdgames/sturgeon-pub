set -e
set -x

export STG_MUTE_TIME=1

rm -rf work
mkdir -p work

# visit

python mkiv2dot.py --mkiv-example visit-edge --central-color
python mkiv2dot.py --mkiv-example visit-node --central-color

python graph2gdesc.py --outfile work/visit.gd --graphfile levels/graphs/mkiv/visit.gr --nrad edge

python gdesc2graph.py --outfile work/visit --gdescfile work/visit.gd --solver pysat-minicard --minsize 8 --maxsize 10 --edgeopt band,4 --mkiv-example visit-edge --mkiv-layers 10
python gdesc2graph.py --outfile work/visit --gdescfile work/visit.gd --solver pysat-minicard --minsize 8 --maxsize 10 --edgeopt band,4 --mkiv-example visit-node --mkiv-layers 10

# color

python graph2gdesc.py --outfile work/color.gd --graphfile levels/graphs/mkiv/color.gr --nrad edge
python gdesc2graph.py --outfile work/color --gdescfile work/color.gd --solver pysat-minicard --minsize 5 --maxsize 10 --edgeopt band,4 --mkiv-example color --mkiv-layers 10
for gr in work/color_play/*.gr; do python graph2dot.py --graphfile ${gr}; done

# pebble

python graph2gdesc.py --outfile work/pebble.gd --graphfile levels/graphs/mkiv/pebble.gr --nrad edge
python gdesc2graph.py --outfile work/pebble --gdescfile work/pebble.gd --solver pysat-minicard --minsize 6 --maxsize 8 --edgeopt band,3 --mkiv-example pebble --mkiv-layers 8

# soko

python input2tile.py --outfile work/soko-in.tile --textfile levels/graphs/mkiv/soko.lvl
python tile2graph.py --outfile work/soko-in.gr --tilefile work/soko-in.tile --mkiv-labels
python graph2gdesc.py --outfile work/soko.gd --graphfile work/soko-in.gr --nrad edge
python gdesc2graph.py --outfile work/soko --gdescfile work/soko.gd --solver pysat-minicard --minsize 25 --maxsize 36 --edgeopt grid,5 --connect layer --mkiv-example soko --mkiv-layers 8
for gr in work/soko_play/*.gr; do python graph2dot.py --graphfile ${gr} --soko; done

# lights out

python graph2gdesc.py --outfile work/lightsout.gd --graphfile levels/graphs/mkiv/lightsout.gr --nrad edge
python gdesc2graph.py --outfile work/lightsout --gdescfile work/lightsout.gd --solver pysat-minicard --minsize 4 --maxsize 6 --edgeopt band,4 --mkiv-example lightsout --mkiv-layers 4
for gr in work/lightsout_play/*.gr; do python graph2dot.py --graphfile ${gr} --lightsout; done

# maze

python graph2gdesc.py --outfile work/maze-fwd.gd --graphfile levels/graphs/mkiv/maze-fwd.gr --nrad edge --edge-delta-rotate
python gdesc2graph.py --outfile work/maze-fwd --gdescfile work/maze-fwd.gd --solver z3-slv --minsize 8 --maxsize 10 --edgeopt band,4 --mkiv-example maze --mkiv-layers 10

python graph2gdesc.py --outfile work/maze-rev.gd --graphfile levels/graphs/mkiv/maze-rev.gr --nrad edge --edge-delta-rotate
python gdesc2graph.py --outfile work/maze-rev --gdescfile work/maze-rev.gd --solver z3-slv --minsize 8 --maxsize 10 --edgeopt band,4 --connect layer --mkiv-example maze --mkiv-layers 10

# adventure

python graph2gdesc.py --outfile work/adventure-a.gd --graphfile levels/graphs/mkiv/adventure-a.gr --nrad edge --edge-delta-rotate
python gdesc2graph.py --outfile work/adventure-a --gdescfile work/adventure-a.gd --solver z3-slv --minsize 8 --maxsize 12 --edgeopt stripe,1,4 --mkiv-example adventure-a --mkiv-layers 14

##python graph2gdesc.py --outfile work/adventure-b.gd --graphfile levels/graphs/mkiv/adventure-b.gr --nrad edge --edge-delta-rotate
##python gdesc2graph.py --outfile work/adventure-b --gdescfile work/adventure-b.gd --solver z3-slv --minsize 8 --maxsize 12 --edgeopt stripe,1,4 --mkiv-example adventure-b --mkiv-layers 14

# codemaster

python graph2gdesc.py --outfile work/cm-dir.gd --graphfile levels/graphs/mkiv/codemaster/cm-dir-*.gr --nrad edge
python gdesc2graph.py --outfile work/cm --gdescfile work/cm-dir.gd --solver pysat-minicard --minsize 11 --maxsize 11 --edgeopt codemaster,4,6 --mkiv-example codemaster-nobranch --mkiv-layers 6
for gr in work/cm_play/*.gr; do python graph2dot.py --graphfile ${gr} --codemaster; done

##python gdesc2graph.py --outfile work/cm --gdescfile work/cm-dir.gd --solver pysat-minicard --minsize 12 --maxsize 15 --edgeopt codemaster,7,7 --mkiv-example codemaster-branch --mkiv-layers 12

# generate

python graph2gdesc.py --outfile work/start-nil-dag.gd --graphfile levels/graphs/mkiv/start-nil-dag.gr

python gdesc2graph.py --outfile work/gen-dag --gdescfile work/start-nil-dag.gd --solver pysat-minicard --minsize 5 --maxsize 5 --mkiv-example gen-dag --mkiv-start-nil --mkiv-layers 4
python gdesc2graph.py --outfile work/gen-run-dag --gdescfile work/start-nil-dag.gd --solver pysat-minicard --minsize 7 --maxsize 7 --mkiv-example gen-run-dag --mkiv-start-nil --mkiv-layers 9
python gdesc2graph.py --outfile work/gen-dag-chain --gdescfile work/start-nil-dag.gd --solver pysat-minicard --minsize 5 --maxsize 5 --mkiv-example gen-dag-chain --mkiv-start-nil --mkiv-layers 6
python gdesc2graph.py --outfile work/gen-dag-multi --gdescfile work/start-nil-dag.gd --solver pysat-minicard --minsize 6 --maxsize 6 --mkiv-example gen-dag-multi --mkiv-start-nil --mkiv-layers 3
python gdesc2graph.py --outfile work/gen-dag-force --gdescfile work/start-nil-dag.gd --solver pysat-minicard --minsize 10 --maxsize 10 --mkiv-example gen-dag-force --mkiv-start-nil --mkiv-layers 4
python gdesc2graph.py --outfile work/gen-dag-inter-hint --gdescfile work/start-nil-dag.gd --solver pysat-minicard --minsize 10 --maxsize 10 --mkiv-example gen-dag-inter-hint --mkiv-start-nil --mkiv-layers 3
python gdesc2graph.py --outfile work/gen-dag-inter-nohint --gdescfile work/start-nil-dag.gd --solver pysat-minicard --minsize 10 --maxsize 10 --mkiv-example gen-dag-inter-nohint --mkiv-start-nil --mkiv-layers 3

python gdesc2graph.py --outfile work/gen-pebble --gdescfile work/start-nil-dag.gd --solver pysat-minicard --minsize 8 --maxsize 8 --mkiv-example gen-pebble --mkiv-start-nil --mkiv-layers 11 --mkiv-rule-count 3=1

python gdesc2graph.py --outfile work/dormans-mini --gdescfile work/start-nil-dag.gd --solver pysat-minicard --minsize 15 --maxsize 15 --mkiv-example dormans-mini-run --mkiv-start-nil --mkiv-layers 20 --mkiv-rule-count 1=1 2=1 --mkiv-label-count k=2 --mkiv-label-layer 3
