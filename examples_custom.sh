set -e
set -x

export STG_MUTE_TIME=1

rm -rf work
mkdir -p work

python input2tile.py --outfile work/mario-1-1_t_ring.tile --textfile levels/vglc/mario-1-1-generic.lvl
python tile2scheme.py --outfile work/mario-1-1_t_ring.scheme --tilefile work/mario-1-1_t_ring.tile --count-divs 1 1 --pattern ring


python scheme2output.py --outfile work/mario-1-1-cst-maxgap   --schemefile work/mario-1-1_t_ring.scheme --size 14 24                                     --pattern-hard --count-soft --reach-move platform --reach-start-goal l-r 4 --custom text-max 13 0 14 24 - soft

python scheme2output.py --outfile work/mario-1-1-cst-exclude  --schemefile work/mario-1-1_t_ring.scheme --size 14 24                                     --pattern-hard --count-soft --reach-move platform --reach-start-goal l-r 4 --custom text-exclude QS hard

python scheme2output.py --outfile work/mario-1-1-cst-3q       --schemefile work/mario-1-1_t_ring.scheme --size 14 24                                     --pattern-hard --count-soft --reach-move platform --reach-start-goal l-r 4 --custom text-count 0 0 14 24 Q 3 3 hard

python scheme2output.py --outfile work/mario-1-1-cst-tallpipe --schemefile work/mario-1-1_t_ring.scheme --size 14 24                                     --pattern-hard --count-soft --reach-move platform --reach-start-goal l-r 4 --custom text-count 2 0 3 24 '<' 1 1 hard

python scheme2output.py --outfile work/mario-1-1-cst-3pipe    --schemefile work/mario-1-1_t_ring.scheme --size 14 24                                     --pattern-hard --count-soft --reach-move platform --reach-start-goal l-r 4 --custom text-count 6 0 7 24 '<' 0 2 hard --custom text-count 8 0 9 24 '<' 0 2 hard --custom text-count 6 0 7 24 '<' 8 0 9 24 '<' 3 3 hard --custom text-count 0 0 6 24 '<' 7 0 8 24 '<' 9 0 14 24 '<' 0 0 hard


python scheme2output.py --outfile work/mario-1-1-cst-infill   --schemefile work/mario-1-1_t_ring.scheme --size 14 32                                     --pattern-soft --count-soft --reach-move platform --reach-start-goal l-r 4 --custom text-level levels/vglc/mario-1-1-cst-infill.lvl hard

python scheme2output.py --outfile work/mario-1-1-cst-link     --schemefile work/mario-1-1_t_ring.scheme --size 14 37                                     --pattern-soft --count-soft --reach-move platform --reach-start-goal l-r 4 --custom text-level levels/vglc/mario-1-1-cst-link.lvl hard

python scheme2output.py --outfile work/mario-1-1-cst-repair   --schemefile work/mario-1-1_t_ring.scheme --size 14 18                                     --pattern-hard                                                             --custom text-level levels/vglc/mario-1-1-cst-repair.lvl soft

python scheme2output.py --outfile work/mario-1-1-cst-wt       --schemefile work/mario-1-1_t_ring.scheme --size  8 18                                     --pattern-hard              --reach-move platform --reach-start-goal l-r 4 --custom text-level-weighted levels/vglc/mario-1-1-cst-repair-gap.lvl levels/vglc/mario-weight.json

python scheme2output.py --outfile work/mario-1-1-cst-subQ     --schemefile work/mario-1-1_t_ring.scheme --size  8 18                                     --pattern-hard              --reach-move platform --reach-start-goal l-r 4 --custom text-level-subst levels/vglc/mario-1-1-cst-repair-gap.lvl levels/vglc/mario-subst-Q.json

python scheme2output.py --outfile work/mario-1-1-cst-subX     --schemefile work/mario-1-1_t_ring.scheme --size  8 18                                     --pattern-hard              --reach-move platform --reach-start-goal l-r 4 --custom text-level-subst levels/vglc/mario-1-1-cst-repair-gap.lvl levels/vglc/mario-subst-X.json

python scheme2output.py --outfile work/mario-1-1-cst-repair   --schemefile work/mario-1-1_t_ring.scheme --size 14 18                                     --pattern-hard                                                             --custom text-level-range levels/vglc/mario-1-1-cst-repair.lvl 0 2 hard


python scheme2output.py --outfile work/mario-1-1-cst-short    --schemefile work/mario-1-1_t_ring.scheme --size 14 24                                     --pattern-hard --count-soft --reach-move platform --reach-start-goal l-r 4 --custom path-short l-r 2 soft

python scheme2output.py --outfile work/mario-1-1-cst-fwd      --schemefile work/mario-1-1_t_ring.scheme --size 14 24                                     --pattern-hard --count-soft --reach-move platform --reach-start-goal l-r 4 --custom path-fwd l-r soft

python scheme2output.py --outfile work/mario-1-1-cst-path     --schemefile work/mario-1-1_t_ring.scheme --size 14 10                                     --pattern-hard --count-soft --reach-move platform --reach-start-goal all --custom path "12 2 12 3, 12 3 12 4, 12 4 8 4, 8 4 9 5, 9 5 10 6, 10 6 11 7" hard

python scheme2output.py --outfile work/mario-1-1-cst-ends     --schemefile work/mario-1-1_t_ring.scheme --size 14 10                                     --pattern-hard --count-soft --reach-move platform --reach-start-goal all --custom path-ends 12 2 11 7 hard


python scheme2output.py --outfile work/mario-1-1-14x30 --schemefile work/mario-1-1_t_ring.scheme --size 14 30 --pattern-hard --count-soft --reach-move platform --reach-start-goal l-r 8
python scheme2output.py --outfile work/mario-1-1-14x50 --schemefile work/mario-1-1_t_ring.scheme --size 14 50 --pattern-hard --count-soft --reach-move platform --reach-start-goal l-r 8 --custom result work/mario-1-1-14x30.result TPo 0 0 14 20 0 0 hard


python scheme2output.py --outfile work/mario-1-1-P0 --schemefile work/mario-1-1_t_ring.scheme --size 14 28 --pattern-hard --count-soft --reach-move platform --reach-start-goal l-r 4
python scheme2output.py --outfile work/mario-1-1-PA --schemefile work/mario-1-1_t_ring.scheme --size 14 28 --pattern-hard --count-soft --reach-move platform --reach-start-goal l-r 4 --custom result work/mario-1-1-P0.result Pa 0 0 14 28 0 0 hard
