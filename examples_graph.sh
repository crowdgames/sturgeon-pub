set -e
set -x

export STG_MUTE_TIME=1

rm -rf work
mkdir -p work

# examples
python graph2gdesc.py --outfile work/test-chain.gd --graphfile levels/graphs/test-chain.gr
python gdesc2graph.py --outfile work/chain-reach --gdescfile work/test-chain.gd --solver pysat-minicard --minsize 20 --maxsize 30 --edgeopt band,5 --label-min 1 --connect reach
python gdesc2graph.py --outfile work/chain-layer --gdescfile work/test-chain.gd --solver pysat-minicard --minsize 20 --maxsize 30 --edgeopt band,5 --label-min 1 --connect layer

python graph2gdesc.py --outfile work/test-chain-long.gd --graphfile levels/graphs/test-chain-long.gr
python gdesc2graph.py --outfile work/chain-long-1c --gdescfile work/test-chain-long.gd --solver pysat-minicard --minsize 20 --maxsize 30 --edgeopt band,5 --label-min C=1 --label-max C=1
python gdesc2graph.py --outfile work/chain-long-3c --gdescfile work/test-chain-long.gd --solver pysat-minicard --minsize 20 --maxsize 30 --edgeopt band,5 --label-min C=3 --label-max C=3

python graph2gdesc.py --outfile work/test-branch-various.gd --graphfile levels/graphs/test-branch-various.gr
python gdesc2summary.py --gdescfile work/test-branch-various.gd
python gdesc2graph.py --outfile work/branch-various    --gdescfile work/test-branch-various.gd --solver pysat-minicard --minsize 20 --maxsize 40 --edgeopt band,5 --label-count --label-min 1
python gdesc2graph.py --outfile work/branch-various-3c --gdescfile work/test-branch-various.gd --solver pysat-minicard --minsize 20 --maxsize 40 --edgeopt band,5 --label-min C=3 --label-max C=3

python graph2gdesc.py --outfile work/test-branch-long.gd --graphfile levels/graphs/test-branch-long.gr
python gdesc2summary.py --gdescfile work/test-branch-long.gd
python gdesc2graph.py --outfile work/branch-long    --gdescfile work/test-branch-long.gd --solver pysat-minicard --minsize 20 --maxsize 40 --edgeopt band,5 --label-count --label-min 1
python gdesc2graph.py --outfile work/branch-long-3c --gdescfile work/test-branch-long.gd --solver pysat-minicard --minsize 20 --maxsize 40 --edgeopt band,5 --label-min C=3 --label-max C=3

python graph2gdesc.py --outfile work/test-branch-small.gd --graphfile levels/graphs/test-branch-small.gr
python gdesc2summary.py --gdescfile work/test-branch-small.gd
python gdesc2graph.py --outfile work/branch-small    --gdescfile work/test-branch-small.gd --solver pysat-minicard --minsize 10 --maxsize 30 --edgeopt band,5 --label-count --label-min 1
python gdesc2graph.py --outfile work/branch-small-3c --gdescfile work/test-branch-small.gd --solver pysat-minicard --minsize 10 --maxsize 30 --edgeopt band,5 --label-min C=3 --label-max C=3

python graph2gdesc.py --outfile work/test-prot.gd --graphfile levels/graphs/test-prot.gr
python gdesc2graph.py --outfile work/prot --gdescfile work/test-prot.gd --solver pysat-minicard --minsize 30 --maxsize 40 --edgeopt band,5

python graph2gdesc.py --outfile work/test-tree.gd --graphfile levels/graphs/test-tree-?.gr
python gdesc2graph.py --outfile work/tree-4-2 --gdescfile work/test-tree.gd --solver pysat-minicard --minsize 7 --maxsize 31 --edgeopt band,5 --label-min 1=1 4=2 5=1 --label-max 1=1 4=2
python gdesc2graph.py --outfile work/tree-4-4 --gdescfile work/test-tree.gd --solver pysat-minicard --minsize 7 --maxsize 31 --edgeopt band,5 --label-min 1=1 4=4 5=1 --label-max 1=1 4=4
python gdesc2graph.py --outfile work/tree-5-f --gdescfile work/test-tree.gd --solver pysat-minicard --minsize 7 --maxsize 31 --edgeopt band,7 --label-min 1=1 5=14 --label-max 1=1 5=14

python graph2gdesc.py --outfile work/test-dag.gd --graphfile levels/graphs/test-dag.gr
python gdesc2graph.py --outfile work/test-dag --gdescfile work/test-dag.gd --solver pysat-minicard --minsize 10 --maxsize 15 --edgeopt band,5 --label-min S=1 E=1 --label-max S=1 E=1

python graph2gdesc.py --outfile work/test-branch-merge.gd --graphfile levels/graphs/test-branch-merge.gr
python gdesc2graph.py --outfile work/test-branch-merge --gdescfile work/test-branch-merge.gd --solver pysat-minicard --minsize 10 --maxsize 15 --edgeopt band,5 --label-min S=1 E=1 B2=1 B3=1 --label-max S=1 E=1

python graph2gdesc.py --outfile work/test-nolabel-utree.gd --graphfile levels/graphs/test-nolabel-utree.gr
python gdesc2summary.py --gdescfile work/test-nolabel-utree.gd
python gdesc2graph.py --outfile work/test-nolabel-utree --gdescfile work/test-nolabel-utree.gd --solver pysat-minicard --minsize 10 --maxsize 15 --edgeopt tri

python graph2gdesc.py --outfile work/test-nolabel-dtree.gd --graphfile levels/graphs/test-nolabel-dtree.gr
python gdesc2summary.py --gdescfile work/test-nolabel-dtree.gd
python gdesc2graph.py --outfile work/test-nolabel-dtree --gdescfile work/test-nolabel-dtree.gd --solver pysat-minicard --minsize 10 --maxsize 15 --edgeopt tri

python graph2gdesc.py --outfile work/test-edge.gd --graphfile levels/graphs/test-edge.gr
python gdesc2graph.py --outfile work/test-edge --gdescfile work/test-edge.gd --solver pysat-minicard --minsize 15 --maxsize 20 --edgeopt band,5

python graph2gdesc.py --outfile work/test-grid.gd --graphfile levels/graphs/test-grid.gr
python gdesc2graph.py --outfile work/test-grid --gdescfile work/test-grid.gd --solver pysat-minicard --minsize 36 --maxsize 48 --edgeopt grid,6

python graph2gdesc.py --outfile work/test-grid-frame.gd --graphfile levels/graphs/test-grid-frame.gr
python gdesc2graph.py --outfile work/test-grid-frame --gdescfile work/test-grid-frame.gd --solver pysat-minicard --minsize 36 --maxsize 48 --edgeopt grid,6

python graph2gdesc.py --outfile work/test-dgraph.gd --graphfile levels/graphs/test-dgraph.gr
python gdesc2graph.py --outfile work/test-dgraph --gdescfile  work/test-dgraph.gd --solver pysat-minicard --minsize 5 --maxsize 10 --edgeopt dband,4 --label-min S=1 E=1 O=1 --label-max S=1 E=1

# dag - grid - mario
python input2tile.py --outfile work/mario-1-1.tile --textfile levels/vglc/mario-1-1-generic-nostartgoal.lvl
python tile2graph.py --outfile work/mario-1-1.gr --tilefile work/mario-1-1.tile --text-labels
python graph2gdesc.py --outfile work/mario-1-1.gd --graphfile levels/graphs/mario-colors.gr work/mario-1-1.gr
python gdesc2graph.py --outfile work/mario-1-1-grid --gdescfile work/mario-1-1.gd --solver pysat-minicard --minsize 100 --maxsize 120 --edgeopt grid,8 --label-min 1
python gdesc2graph.py --outfile work/mario-1-1-rect --gdescfile work/mario-1-1.gd --solver pysat-minicard --minsize 100 --maxsize 120 --edgeopt rect,8 --label-min 1

# dag - mission
python graph2gdesc.py --outfile work/mission.gd --graphfile levels/graphs/mission/mission-colors.gr levels/graphs/mission/mission-01.gr levels/graphs/mission/mission-02.gr
python gdesc2graph.py --outfile work/mission --gdescfile work/mission.gd --solver pysat-minicard --minsize 15 --maxsize 20 --edgeopt band,5 --label-min e=1 g=1 --label-max e=1 g=1

# ugraph - zelda
python dot2graph.py --outfile work/LoZ_1.gr --dot levels/graphs/LoZ/LoZ_1.dot
python dot2graph.py --outfile work/LoZ_2.gr --dot levels/graphs/LoZ/LoZ_2.dot
python graph2gdesc.py --outfile work/LoZ.gd --graphfile levels/graphs/LoZ/LoZ-colors.gr work/LoZ_1.gr work/LoZ_2.gr
python gdesc2graph.py --outfile work/LoZ --gdescfile work/LoZ.gd --solver pysat-minicard --minsize 20 --maxsize 25 --edgeopt band,3 --label-min s=1 t=1 --label-max s=1 t=1

# dag - fract
python graph2gdesc.py --outfile work/fract.gd --graphfile levels/graphs/fract/fract-*.gr --nrad edge --edge-delta-rotate
python gdesc2graph.py --outfile work/fract --gdescfile work/fract.gd --solver z3-slv --connect layer --minsize 8 --maxsize 10 --edgeopt band,4 --label-min m=1 s=1 '1>=2'

# loops and lengths
python graph2gdesc.py --outfile work/test-chain-tri.gd --graphfile levels/graphs/test-chain-tri.gr --nrad sub1
python gdesc2graph.py --outfile work/test-chain-tri --gdescfile work/test-chain-tri.gd --solver pysat-minicard --minsize 20 --maxsize 30 --edgeopt band,5

python graph2gdesc.py --outfile work/test-chain-loop.gd --graphfile levels/graphs/test-chain-loop.gr --nrad sub1 --edge-delta --cycle-label
python gdesc2graph.py --outfile work/test-chain-loop-cn --gdescfile work/test-chain-loop.gd --solver z3-slv --minsize 20 --maxsize 30 --edgeopt band,5 --cycle-no
python gdesc2graph.py --outfile work/test-chain-loop-cy --gdescfile work/test-chain-loop.gd --solver z3-slv --minsize 20 --maxsize 30 --edgeopt band,5 --cycle-yes

python graph2gdesc.py --outfile work/snake.gd --graphfile levels/graphs/snake.gr --edge-polar
python gdesc2graph.py --outfile work/snake --gdescfile work/snake.gd --solver z3-slv --minsize 10 --maxsize 10 --edgeopt band,2

# pdb
python pdb2graph.py --outfile work/echinatin.gr --pdbfile levels/graphs/pdb/echinatin.pdb
python graph2gdesc.py --outfile work/mol.gd --graphfile work/echinatin.gr --edge-polar --nrad edge --cycle-label
python gdesc2graph.py --outfile work/mol-cn --gdescfile work/mol.gd --solver z3-slv --minsize 5 --maxsize 10 --edgeopt band,4 --cycle-no
python gdesc2graph.py --outfile work/mol-cy --gdescfile work/mol.gd --solver z3-slv --minsize 5 --maxsize 10 --edgeopt band,4 --cycle-yes
python graph2pdb.py --outfile work/mol-cn.pdb --graphfile work/mol-cn.gr
python graph2pdb.py --outfile work/mol-cy.pdb --graphfile work/mol-cy.gr
