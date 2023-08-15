set -e
set -x

export STG_MUTE_TIME=1

rm -rf work
mkdir -p work

python3 input2tile.py --outfile work/mario-1-1_t_ring.tile --textfile levels/vglc/mario-1-1-generic.lvl
python3 tile2scheme.py --outfile work/mario-1-1_t_ring.scheme --tilefile work/mario-1-1_t_ring.tile --countdivs 1 1 --pattern ring


python3 scheme2output.py --outfile work/mario-1-1-app-template --schemefile work/mario-1-1_t_ring.scheme --reach-move platform --reach-goal l-r 4 --tagfile levels/vglc/mario-1-1-app-template.lvl --soft-patterns

python3 scheme2output.py --outfile work/mario-1-1-app-maxgap   --schemefile work/mario-1-1_t_ring.scheme --reach-move platform --reach-goal l-r 4 --size 14 24 --custom text-max 13 0 14 24 - soft

python3 scheme2output.py --outfile work/mario-1-1-app-3q       --schemefile work/mario-1-1_t_ring.scheme --reach-move platform --reach-goal l-r 4 --size 14 24 --custom text-count 0 0 14 24 3 3 Q hard

python3 scheme2output.py --outfile work/mario-1-1-app-tallpipe --schemefile work/mario-1-1_t_ring.scheme --reach-move platform --reach-goal l-r 4 --size 14 24 --custom text-count 2 0 3 24 1 1 '<' hard

python3 scheme2output.py --outfile work/mario-1-1-app-infill   --schemefile work/mario-1-1_t_ring.scheme --reach-move platform --reach-goal l-r 4 --size 14 32 --custom text-level levels/vglc/mario-1-1-app-infill.lvl hard --soft-patterns

python3 scheme2output.py --outfile work/mario-1-1-app-link     --schemefile work/mario-1-1_t_ring.scheme --reach-move platform --reach-goal l-r 4 --size 14 37 --custom text-level levels/vglc/mario-1-1-app-link.lvl hard --soft-patterns

python3 scheme2output.py --outfile work/mario-1-1-app-repair   --schemefile work/mario-1-1_t_ring.scheme                                          --size 14 18 --custom text-level levels/vglc/mario-1-1-app-repair.lvl soft --soft-patterns

python3 scheme2output.py --outfile work/mario-1-1-app-short    --schemefile work/mario-1-1_t_ring.scheme --reach-move platform --reach-goal l-r 4 --size 14 24 --custom path-short l-r 2 soft

python3 scheme2output.py --outfile work/mario-1-1-path         --schemefile work/mario-1-1_t_ring.scheme --reach-move platform --reach-goal all   --size 14 10 --custom path "12 2, 12 3, 12 4, 8 4, 9 5, 10 6, 11 7" hard


python3 scheme2output.py --outfile work/mario-1-1-14x30 --schemefile work/mario-1-1_t_ring.scheme --size 14 30 --reach-move platform --reach-goal l-r 8
python3 scheme2output.py --outfile work/mario-1-1-14x50 --schemefile work/mario-1-1_t_ring.scheme --size 14 50 --reach-move platform --reach-goal l-r 8 --custom result work/mario-1-1-14x30.result TPo 0 0 14 20 0 0 hard


python3 scheme2output.py --outfile work/mario-1-1-P0 --schemefile work/mario-1-1_t_ring.scheme --size 14 28 --reach-move platform --reach-goal l-r 4
python3 scheme2output.py --outfile work/mario-1-1-PA --schemefile work/mario-1-1_t_ring.scheme --size 14 28 --reach-move platform --reach-goal l-r 4 --custom result work/mario-1-1-P0.result Pa 0 0 14 28 0 0 hard
