set -e
set -x

export STG_MUTE_TIME=1

rm -rf work
mkdir -p work

python input2tile.py --outfile work/mario.tile --textfile levels/vglc/mario-1-1-generic.lvl
python tile2scheme.py --outfile work/mario.scheme --tilefile work/mario.tile --count-divs 1 1 --pattern ring

# text

python scheme2output.py --outfile work/mario-3q       --schemefile work/mario.scheme --size 14 24 --pattern-hard --count-soft --reach-move platform --reach-start-goal l-r 4 --custom text-count 0 0 14 24 Q 3 3 hard

python scheme2output.py --outfile work/mario-tallpipe --schemefile work/mario.scheme --size 14 24 --pattern-hard --count-soft --reach-move platform --reach-start-goal l-r 4 --custom text-count 2 0 3 24 '<' 1 1 hard

python scheme2output.py --outfile work/mario-3pipe    --schemefile work/mario.scheme --size 14 24 --pattern-hard --count-soft --reach-move platform --reach-start-goal l-r 4 --custom text-count 6 0 7 24 '<' 0 2 hard --custom text-count 8 0 9 24 '<' 0 2 hard --custom text-count 6 0 7 24 '<' 8 0 9 24 '<' 3 3 hard --custom text-count 0 0 6 24 '<' 7 0 8 24 '<' 9 0 14 24 '<' 0 0 hard

python scheme2output.py --outfile work/mario-exclude  --schemefile work/mario.scheme --size 14 24 --pattern-hard --count-soft --reach-move platform --reach-start-goal l-r 4 --custom text-exclude QS hard

python scheme2output.py --outfile work/mario-gap-min  --schemefile work/mario.scheme --size 14 24 --pattern-hard --count-soft --reach-move platform --reach-start-goal l-r 4 --custom text-min 13 0 14 24 QSX soft

python scheme2output.py --outfile work/mario-gap-max  --schemefile work/mario.scheme --size 14 24 --pattern-hard --count-soft --reach-move platform --reach-start-goal l-r 4 --custom text-max 13 0 14 24 - soft

# text-level

python scheme2output.py --outfile work/mario-infill   --schemefile work/mario.scheme --size 14 32 --pattern-soft --count-soft --reach-move platform --reach-start-goal l-r 4 --custom text-level levels/vglc/mario-1-1-cst-infill.lvl hard

python scheme2output.py --outfile work/mario-link     --schemefile work/mario.scheme --size 14 37 --pattern-soft --count-soft --reach-move platform --reach-start-goal l-r 4 --custom text-level levels/vglc/mario-1-1-cst-link.lvl hard

python scheme2output.py --outfile work/mario-repair   --schemefile work/mario.scheme --size 14 18 --pattern-hard                                                             --custom text-level levels/vglc/mario-1-1-cst-repair.lvl soft

python scheme2output.py --outfile work/mario-wt       --schemefile work/mario.scheme --size  8 18 --pattern-hard              --reach-move platform --reach-start-goal l-r 4 --custom text-level-weighted levels/vglc/mario-1-1-cst-repair-gap.lvl levels/vglc/mario-weight.json

python scheme2output.py --outfile work/mario-subQ     --schemefile work/mario.scheme --size  8 18 --pattern-hard              --reach-move platform --reach-start-goal l-r 4 --custom text-level-subst levels/vglc/mario-1-1-cst-repair-gap.lvl levels/vglc/mario-subst-Q.json

python scheme2output.py --outfile work/mario-subX     --schemefile work/mario.scheme --size  8 18 --pattern-hard              --reach-move platform --reach-start-goal l-r 4 --custom text-level-subst levels/vglc/mario-1-1-cst-repair-gap.lvl levels/vglc/mario-subst-X.json

python scheme2output.py --outfile work/mario-repair   --schemefile work/mario.scheme --size 14 18 --pattern-hard                                                             --custom text-level-range levels/vglc/mario-1-1-cst-repair.lvl 0 2 hard

# flat

python scheme2output.py --outfile work/mario-fl-path     --schemefile work/mario.scheme --size 14 10 --pattern-hard --count-soft --reach-move platform --reach-start-goal all   --custom flat-path "12 2 12 3, 12 3 12 4, 12 4 8 4, 8 4 9 5, 9 5 10 6, 10 6 11 7" hard

python scheme2output.py --outfile work/mario-fl-ends     --schemefile work/mario.scheme --size 14 10 --pattern-hard --count-soft --reach-move platform --reach-start-goal all   --custom flat-ends 12 2 11 7 hard

python scheme2output.py --outfile work/mario-fl-fwd      --schemefile work/mario.scheme --size 14 10 --pattern-hard --count-soft --reach-move platform --reach-start-goal l-r 4 --custom flat-fwd l-r soft

python scheme2output.py --outfile work/mario-fl-min      --schemefile work/mario.scheme --size 14 10 --pattern-hard --count-soft --reach-move platform --reach-start-goal l-r 4 --custom flat-min soft

# layered

python scheme2output.py --outfile work/mario-la-min      --schemefile work/mario.scheme --size 14 10 --pattern-hard              --reach-junction "{" l 4 --reach-junction "}" r 4 --reach-connect '--src { --dst } --move platform --method layered --layers 20' --custom layered-fwd l-r soft

python scheme2output.py --outfile work/mario-la-min      --schemefile work/mario.scheme --size 14 10 --pattern-hard              --reach-junction "{" l 4 --reach-junction "}" r 4 --reach-connect '--src { --dst } --move platform --method layered --layers 20' --custom layered-min-edge soft

python scheme2output.py --outfile work/mario-la-min      --schemefile work/mario.scheme --size 14 10 --pattern-hard              --reach-junction "{" l 4 --reach-junction "}" r 4 --reach-connect '--src { --dst } --move platform --method layered --layers 20' --custom layered-min-tile soft

# fwdbwd

python scheme2output.py --outfile work/mario-fb-nostuck  --schemefile work/mario.scheme --size 10 20 --pattern-hard              --reach-junction "{" l 4 --reach-junction "}" r 4 --reach-connect '--src { --dst } --move platform --method fwdbwd --layers 20 --sink bottom' --custom fwdbwd-nostuck hard

python scheme2output.py --outfile work/mario-fb-stuck-no --schemefile work/mario.scheme --size 10 20 --pattern-hard              --reach-junction "{" l 4 --reach-junction "}" r 4 --reach-connect '--src { --dst } --move platform --method fwdbwd --layers 20 --sink bottom' --custom fwdbwd-stuck sink-no hard

python scheme2output.py --outfile work/mario-fb-stuck-ok --schemefile work/mario.scheme --size 10 20 --pattern-hard              --reach-junction "{" l 4 --reach-junction "}" r 4 --reach-connect '--src { --dst } --move platform --method fwdbwd --layers 20 --sink bottom' --custom fwdbwd-stuck sink-ok hard

python scheme2output.py --outfile work/mario-fb-r-open   --schemefile work/mario.scheme --size 10 20 --pattern-hard              --reach-junction "{" l 4 --reach-junction "}" r 4 --reach-connect '--src { --dst } --move platform --method fwdbwd --layers 20 --sink bottom' --custom fwdbwd-reach-open hard

python scheme2output.py --outfile work/mario-fb-r-sink   --schemefile work/mario.scheme --size 10 20 --pattern-hard              --reach-junction "{" l 4 --reach-junction "}" r 4 --reach-connect '--src { --dst } --move platform --method fwdbwd --layers 20 --sink bottom' --custom fwdbwd-reach-sink hard

python scheme2output.py --outfile work/mario-fb-sink-c   --schemefile work/mario.scheme --size 10 20 --pattern-hard              --reach-junction "{" l 4 --reach-junction "}" r 4 --reach-connect '--src { --dst } --move platform --method fwdbwd --layers 20 --sink bottom' --custom fwdbwd-count-sink 4 4 hard

python scheme2output.py --outfile work/mario-fb-c        --schemefile work/mario.scheme --size 10 20 --pattern-hard              --reach-junction "{" l 4 --reach-junction "}" r 4 --reach-connect '--src { --dst } --move platform --method fwdbwd --layers 20 --sink bottom --unreachable' --custom fwdbwd-count-fwdbwd 20 120 20 120 hard

# result

python scheme2output.py --outfile work/mario-14x30    --schemefile work/mario.scheme --size 14 30 --pattern-hard --count-soft --reach-move platform --reach-start-goal l-r 8
python scheme2output.py --outfile work/mario-14x50    --schemefile work/mario.scheme --size 14 50 --pattern-hard --count-soft --reach-move platform --reach-start-goal l-r 8 --custom result work/mario-14x30.result TPo 0 0 14 20 0 0 hard

python scheme2output.py --outfile work/mario-P0       --schemefile work/mario.scheme --size 14 28 --pattern-hard --count-soft --reach-move platform --reach-start-goal l-r 4
python scheme2output.py --outfile work/mario-PA       --schemefile work/mario.scheme --size 14 28 --pattern-hard --count-soft --reach-move platform --reach-start-goal l-r 4 --custom result work/mario-P0.result Pa 0 0 14 28 0 0 hard
