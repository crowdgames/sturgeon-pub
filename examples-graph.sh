set -e
set -x

export STG_MUTE_TIME=1

rm -rf work
mkdir -p work

# examples
python graph2gdesc.py --outfile work/test-chain.gd --graphfile levels/graphs/test-chain.gr
python gdesc2graph.py --outfile work/chain-reach.dot --gdescfile work/test-chain.gd --solver pysat-minicard --minsize 20 --maxsize 30 --edgeopt band 5 --label-min 1 --connect reach
python gdesc2graph.py --outfile work/chain-layer.dot --gdescfile work/test-chain.gd --solver pysat-minicard --minsize 20 --maxsize 30 --edgeopt band 5 --label-min 1 --connect layer

python graph2gdesc.py --outfile work/test-chain-long.gd --graphfile levels/graphs/test-chain-long.gr
python gdesc2graph.py --outfile work/chain-long-1c.dot --gdescfile work/test-chain-long.gd --solver pysat-minicard --minsize 20 --maxsize 30 --edgeopt band 5 --label-min C=1 --label-max C=1
python gdesc2graph.py --outfile work/chain-long-3c.dot --gdescfile work/test-chain-long.gd --solver pysat-minicard --minsize 20 --maxsize 30 --edgeopt band 5 --label-min C=3 --label-max C=3

python graph2gdesc.py --outfile work/test-branch-various.gd --graphfile levels/graphs/test-branch-various.gr
python gdesc2graph.py --outfile work/branch-various.dot    --gdescfile work/test-branch-various.gd --solver pysat-minicard --minsize 20 --maxsize 40 --edgeopt band 5 --label-count --label-min 1
python gdesc2graph.py --outfile work/branch-various-3c.dot --gdescfile work/test-branch-various.gd --solver pysat-minicard --minsize 20 --maxsize 40 --edgeopt band 5 --label-min C=3 --label-max C=3
python gdesc2graph.py --outfile work/branch-various-5c.dot --gdescfile work/test-branch-various.gd --solver pysat-minicard --minsize 20 --maxsize 40 --edgeopt band 5 --label-min C=5 --label-max C=5
python gdesc2summary.py --gdescfile work/test-branch-various.gd

python graph2gdesc.py --outfile work/test-branch-long.gd --graphfile levels/graphs/test-branch-long.gr
python gdesc2graph.py --outfile work/branch-long.dot    --gdescfile work/test-branch-long.gd --solver pysat-minicard --minsize 20 --maxsize 40 --edgeopt band 5 --label-count --label-min 1
python gdesc2graph.py --outfile work/branch-long-3c.dot --gdescfile work/test-branch-long.gd --solver pysat-minicard --minsize 20 --maxsize 40 --edgeopt band 5 --label-min C=3 --label-max C=3
python gdesc2graph.py --outfile work/branch-long-5c.dot --gdescfile work/test-branch-long.gd --solver pysat-minicard --minsize 20 --maxsize 40 --edgeopt band 5 --label-min C=5 --label-max C=5
python gdesc2summary.py --gdescfile work/test-branch-long.gd

python graph2gdesc.py --outfile work/test-branch-small.gd --graphfile levels/graphs/test-branch-small.gr
python gdesc2graph.py --outfile work/branch-small.dot    --gdescfile work/test-branch-small.gd --solver pysat-minicard --minsize 10 --maxsize 30 --edgeopt band 5 --label-count --label-min 1
python gdesc2graph.py --outfile work/branch-small-3c.dot --gdescfile work/test-branch-small.gd --solver pysat-minicard --minsize 10 --maxsize 30 --edgeopt band 5 --label-min C=3 --label-max C=3
python gdesc2graph.py --outfile work/branch-small-5c.dot --gdescfile work/test-branch-small.gd --solver pysat-minicard --minsize 10 --maxsize 30 --edgeopt band 5 --label-min C=5 --label-max C=5
python gdesc2summary.py --gdescfile work/test-branch-small.gd

python graph2gdesc.py --outfile work/test-prot.gd --graphfile levels/graphs/test-prot.gr
python gdesc2graph.py --outfile work/prot.dot --gdescfile work/test-prot.gd --solver pysat-minicard --minsize 30 --maxsize 40 --edgeopt band 5

python graph2gdesc.py --outfile work/test-tree.gd --graphfile levels/graphs/test-tree-?.gr
python gdesc2graph.py --outfile work/tree-4-2.dot --gdescfile work/test-tree.gd --solver pysat-minicard --minsize 7 --maxsize 31 --edgeopt band 5 --label-min 1=1 4=2 5=1 --label-max 1=1 4=2
python gdesc2graph.py --outfile work/tree-4-4.dot --gdescfile work/test-tree.gd --solver pysat-minicard --minsize 7 --maxsize 31 --edgeopt band 5 --label-min 1=1 4=4 5=1 --label-max 1=1 4=4
python gdesc2graph.py --outfile work/tree-5-f.dot --gdescfile work/test-tree.gd --solver pysat-minicard --minsize 7 --maxsize 31 --edgeopt band 7 --label-min 1=1 5=14 --label-max 1=1 5=14

python graph2gdesc.py --outfile work/test-dag.gd --graphfile levels/graphs/test-dag.gr
python gdesc2graph.py --outfile work/test-dag.dot --gdescfile work/test-dag.gd --solver pysat-minicard --minsize 10 --maxsize 15 --edgeopt band 5 --label-min S=1 E=1 --label-max S=1 E=1

python graph2gdesc.py --outfile work/test-branch-merge.gd --graphfile levels/graphs/test-branch-merge.gr
python gdesc2graph.py --outfile work/test-branch-merge.dot --gdescfile work/test-branch-merge.gd --solver pysat-minicard --minsize 10 --maxsize 15 --edgeopt band 5 --label-min S=1 E=1 B2=1 B3=1 --label-max S=1 E=1

python graph2gdesc.py --outfile work/test-nolabel-utree.gd --graphfile levels/graphs/test-nolabel-utree.gr
python gdesc2graph.py --outfile work/test-nolabel-utree.dot --gdescfile work/test-nolabel-utree.gd --solver pysat-minicard --minsize 10 --maxsize 15 --edgeopt full
python gdesc2summary.py --gdescfile work/test-nolabel-utree.gd

python graph2gdesc.py --outfile work/test-nolabel-dtree.gd --graphfile levels/graphs/test-nolabel-dtree.gr
python gdesc2graph.py --outfile work/test-nolabel-dtree.dot --gdescfile work/test-nolabel-dtree.gd --solver pysat-minicard --minsize 10 --maxsize 15 --edgeopt full
python gdesc2summary.py --gdescfile work/test-nolabel-dtree.gd

python graph2gdesc.py --outfile work/test-edge.gd --graphfile levels/graphs/test-edge.gr
python gdesc2graph.py --outfile work/test-edge.dot --gdescfile work/test-edge.gd --solver pysat-minicard --minsize 15 --maxsize 20 --edgeopt band 5

python graph2gdesc.py --outfile work/test-grid.gd --graphfile levels/graphs/test-grid.gr
python gdesc2graph.py --outfile work/test-grid.dot --gdescfile work/test-grid.gd --solver pysat-minicard --minsize 36 --maxsize 48 --edgeopt grid 6

python graph2gdesc.py --outfile work/test-grid-frame.gd --graphfile levels/graphs/test-grid-frame.gr
python gdesc2graph.py --outfile work/test-grid-frame.dot --gdescfile work/test-grid-frame.gd --solver pysat-minicard --minsize 36 --maxsize 48 --edgeopt grid 6

# dag - grid - mario
python input2tiles.py --outfile work/mario-1-1.tiles --textfile levels/vglc/mario-1-1-generic-nostartgoal.lvl
python tiles2graph.py --outfile work/mario-1-1.gr --tilefile work/mario-1-1.tiles --text-labels
python graph2gdesc.py --outfile work/mario-1-1.gd --graphfile levels/graphs/mario-colors.gr work/mario-1-1.gr
python gdesc2graph.py --outfile work/mario-1-1-grid.dot --gdescfile work/mario-1-1.gd --solver pysat-minicard --minsize 100 --maxsize 120 --edgeopt grid 8 --label-min 1
python gdesc2graph.py --outfile work/mario-1-1-rect.dot --gdescfile work/mario-1-1.gd --solver pysat-minicard --minsize 100 --maxsize 120 --edgeopt rect 8 --label-min 1

# dag - mission
python graph2gdesc.py --outfile work/mission.gd --graphfile levels/graphs/mission/mission-colors.gr levels/graphs/mission/mission-01.gr levels/graphs/mission/mission-02.gr
python gdesc2graph.py --outfile work/mission.dot --gdescfile work/mission.gd --solver pysat-minicard --minsize 15 --maxsize 20 --edgeopt band 5 --label-min e=1 g=1 --label-max e=1 g=1

# ugraph - zelda
python dot2graph.py --out work/LoZ_1.gr --dot levels/graphs/LoZ/LoZ_1.dot
python dot2graph.py --out work/LoZ_2.gr --dot levels/graphs/LoZ/LoZ_2.dot
python graph2gdesc.py --outfile work/LoZ.gd --graphfile levels/graphs/LoZ/LoZ-colors.gr work/LoZ_1.gr work/LoZ_2.gr
python gdesc2graph.py --outfile work/LoZ.dot --gdescfile work/LoZ.gd --solver pysat-minicard --minsize 20 --maxsize 25 --edgeopt band 3 --label-min s=1 t=1 --label-max s=1 t=1

# dag - fract
python graph2gdesc.py --outfile work/fract.gd --graphfile levels/graphs/fract/fract-*.gr --edgesonly
python gdesc2graph.py --outfile work/fract.dot --gdescfile work/fract.gd --minsize 8 --maxsize 10 --edgeopt band 5 --label-min jn=1 --label-max b=2
