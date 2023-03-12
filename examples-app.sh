set -e
set -x

export STG_MUTE_TIME=1

rm -rf work
mkdir -p work

python3 input2tiles.py --outfile work/mario-1-1_t_ring.tiles --textfile levels/vglc/mario-1-1-generic.lvl
python3 tiles2scheme.py --outfile work/mario-1-1_t_ring.scheme --tilefile work/mario-1-1_t_ring.tiles --countdivs 1 1 --pattern ring

python3 scheme2output.py --outfile work/mario-1-1-app-template --schemefile work/mario-1-1_t_ring.scheme --reach-move platform --reach-goal l-r 4 --tagfile levels/vglc/mario-1-1-app-template.lvl --soft-patterns

python3 scheme2output.py --outfile work/mario-1-1-app-maxgap   --schemefile work/mario-1-1_t_ring.scheme --reach-move platform --reach-goal l-r 4 --size 14 24 --out-text-max 13 0 14 24 - soft

python3 scheme2output.py --outfile work/mario-1-1-app-3q       --schemefile work/mario-1-1_t_ring.scheme --reach-move platform --reach-goal l-r 4 --size 14 24 --out-text-count 0 0 14 24 3 3 Q hard

python3 scheme2output.py --outfile work/mario-1-1-app-tallpipe --schemefile work/mario-1-1_t_ring.scheme --reach-move platform --reach-goal l-r 4 --size 14 24 --out-text-count 2 0 3 24 1 1 '<' hard

python3 scheme2output.py --outfile work/mario-1-1-app-infill   --schemefile work/mario-1-1_t_ring.scheme --reach-move platform --reach-goal l-r 4 --size 14 32 --out-text-level levels/vglc/mario-1-1-app-infill.lvl hard --soft-patterns

python3 scheme2output.py --outfile work/mario-1-1-app-link     --schemefile work/mario-1-1_t_ring.scheme --reach-move platform --reach-goal l-r 4 --size 14 37 --out-text-level levels/vglc/mario-1-1-app-link.lvl hard --soft-patterns

python3 scheme2output.py --outfile work/mario-1-1-app-repair   --schemefile work/mario-1-1_t_ring.scheme --size 14 18 --out-text-level levels/vglc/mario-1-1-app-repair.lvl soft --soft-patterns
