set -e
set -x

export STG_MUTE_TIME=1

rm -rf work
mkdir -p work

# cave
python3 input2tile.py --outfile work/cave.tile --textfile levels/kenney/cave.lvl --imagefile levels/kenney/cave.png
python3 tile2scheme.py --outfile work/cave.scheme --tilefile work/cave.tile --count-divs 1 1 --pattern nbr-plus
python3 scheme2output.py --outfile work/cave --schemefile work/cave.scheme --size 15 15 --pattern-hard --count-soft --reach-start-goal tl-br 5 --reach-move maze --reach-unreachable
python3 level2repath.py --outfile work/cave-rp.lvl --textfile work/cave.lvl --reach-move maze --path f

# cave-junction
python3 input2tile.py --outfile work/cave-junction.tile --textfile levels/kenney/cave-junction.lvl --imagefile levels/kenney/cave-junction.png
python3 tile2scheme.py --outfile work/cave-junction.scheme --tilefile work/cave-junction.tile --count-divs 1 1 --pattern nbr-plus

python3 scheme2output.py --outfile work/cave-junction-a --schemefile work/cave-junction.scheme --size 15 15 --pattern-hard --count-soft --reach-junction 0 tl 4 --reach-junction 1 br 4 --custom text-exclude 23 hard --reach-connect "--src 0 --dst 1 --move maze"

python3 scheme2output.py --outfile work/cave-junction-b --schemefile work/cave-junction.scheme --size 15 15 --pattern-hard --count-soft --reach-junction 0 tl 4 --reach-junction 1 br 4 --custom text-exclude 23 hard --reach-connect "--src 0 --dst 1 --move maze" --reach-connect "--src 1 --dst 0 --move maze"

python3 scheme2output.py --outfile work/cave-junction-c --schemefile work/cave-junction.scheme --size 15 15 --pattern-hard --count-soft --reach-junction 0 tl 4 --reach-junction 1 tr 4 --reach-junction 2 bl 4 --reach-junction 3 br 4 --reach-connect "--src 0 --dst 1 --move maze" --reach-connect "--src 2 --dst 3 --move maze" --reach-connect "--src 0 --dst 2 --move maze --unreachable"

python3 scheme2output.py --outfile work/cave-junction-d --schemefile work/cave-junction.scheme --size 15 15 --pattern-hard --count-soft --reach-junction 0 tl 4 --reach-junction 1 tr 4 --reach-junction 2 bl 4 --reach-junction 3 br 4 --reach-connect "--src 0 --dst 1 --move maze" --reach-connect "--src 1 --dst 3 --move maze" --reach-connect "--src 3 --dst 2 --move maze" --reach-connect "--src 2 --dst 0 --move maze"

# cave-doors
python3 input2tile.py --outfile work/cave-doors.tile --textfile levels/kenney/cave-doors.lvl --imagefile levels/kenney/cave-doors.png
python3 tile2scheme.py --outfile work/cave-doors.scheme --tilefile work/cave-doors.tile --pattern nbr-plus

python3 scheme2output.py --outfile work/cave-doors --schemefile work/cave-doors.scheme --size 15 15 --pattern-hard \
  --reach-junction { tl 4 \
  --reach-junction } br 4 \
  --reach-junction B bl 6 \
  --reach-junction b tr 6 \
  --custom text-exclude Y hard \
  --custom text-exclude y hard \
  --custom text-exclude 1 hard \
  --custom text-exclude 2 hard \
  --reach-connect "--src { --dst b --move maze" \
  --reach-connect "--src b --dst B --move maze" \
  --reach-connect "--src B --dst } --move maze" \
  --reach-connect "--src { --dst } --move maze --unreachable" \
  --reach-connect "--src b --dst } --move maze --unreachable"

# mario
python3 input2tile.py --outfile work/mario.tile --textfile levels/vglc/mario-1-1-generic.lvl
python3 tile2scheme.py --outfile work/mario.scheme --tilefile work/mario.tile --count-divs 1 1 --pattern ring
python3 scheme2output.py --outfile work/mario --schemefile work/mario.scheme --size 14 32 --pattern-hard --count-soft --reach-start-goal l-r 6 --reach-move platform --reach-unreachable
python3 level2repath.py --outfile work/mario-rp.lvl --textfile work/mario.lvl --reach-move platform --path f

python3 scheme2output.py --outfile work/mario-a --schemefile work/mario.scheme --size 14 32 --pattern-hard --count-soft --reach-junction { l 6 --reach-junction } r 6 --reach-connect "--src { --dst } --move platform" --reach-connect "--src } --dst { --move platform"
python3 level2repath.py --outfile work/mario-a-rp.lvl --textfile work/mario-a.lvl --reach-move platform --src { } --dst } {

python3 scheme2output.py --outfile work/mario-b --schemefile work/mario.scheme --size 14 32 --pattern-hard --count-soft --reach-junction { l 6 --reach-junction } r 6 --reach-connect "--src { --dst } --move platform" --reach-connect "--src } --dst { --move platform --unreachable"
python3 level2repath.py --outfile work/mario-b-rp.lvl --textfile work/mario-b.lvl --reach-move platform --src { } --dst } { --path t f
