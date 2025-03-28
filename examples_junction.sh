set -e
set -x

export STG_MUTE_TIME=1

rm -rf work
mkdir -p work

# cave
python input2tile.py --outfile work/cave.tile --textfile levels/kenney/cave.lvl --imagefile levels/kenney/cave.png
python tile2scheme.py --outfile work/cave.scheme --tilefile work/cave.tile --count-divs 1 1 --pattern nbr-plus

python scheme2output.py --outfile work/cave-a --schemefile work/cave.scheme --size 15 15 --pattern-hard --count-soft --reach-junction "{" tl 5 --reach-junction "}" br 5 --reach-connect "--src { --dst } --move maze" --reach-print-internal
python level2repath.py --outfile work/cave-a-rp1.lvl --textfile work/cave-a.lvl --reach-connect "--src { --dst } --move maze" --print-level
python level2repath.py --outfile work/cave-a-rp2.lvl --textfile work/cave-a.lvl --reach-connect "--src { --dst } --move maze" --print-level --type edges

python scheme2output.py --outfile work/cave-b --schemefile work/cave.scheme --size 15 15 --pattern-hard --count-soft --reach-junction "{" tl 5 --reach-junction "}" br 5 --reach-connect "--src { --dst } --move maze --unreachable" --reach-print-internal
python level2repath.py --outfile work/cave-b-rp1.lvl --textfile work/cave-b.lvl --reach-connect "--src { --dst } --move maze --unreachable" --print-level
python level2repath.py --outfile work/cave-b-rp2.lvl --textfile work/cave-b.lvl --reach-connect "--src { --dst } --move maze --unreachable" --print-level --type edges

# cave special move
python scheme2output.py --outfile work/cave-special --schemefile work/cave.scheme --size 15 15 --pattern-hard --count-soft --reach-junction "{" tl 5 --reach-junction "}" br 5 --reach-connect "--src { --dst } --move maze --unreachable" --reach-connect "--src { --dst } --move maze-blink"
python level2repath.py --outfile work/cave-special-rp1.lvl --textfile work/cave-special.lvl --reach-connect "--src { --dst } --move maze --unreachable" --reach-connect "--src { --dst } --move maze-blink" --print-level
python level2repath.py --outfile work/cave-special-rp2.lvl --textfile work/cave-special.lvl --reach-connect "--src { --dst } --move maze --unreachable" --reach-connect "--src { --dst } --move maze-blink" --print-level --type edges

# cave-junction
python input2tile.py --outfile work/cave-junction.tile --textfile levels/kenney/cave-junction.lvl --imagefile levels/kenney/cave-junction.png
python tile2scheme.py --outfile work/cave-junction.scheme --tilefile work/cave-junction.tile --count-divs 1 1 --pattern nbr-plus

python scheme2output.py --outfile work/cave-junction-a --schemefile work/cave-junction.scheme --size 15 15 --pattern-hard --count-soft --reach-junction 0 tl 4 --reach-junction 1 br 4 --custom text-exclude 23 hard --reach-connect "--src 0 --dst 1 --move maze"

python scheme2output.py --outfile work/cave-junction-b --schemefile work/cave-junction.scheme --size 15 15 --pattern-hard --count-soft --reach-junction 0 tl 4 --reach-junction 1 br 4 --custom text-exclude 23 hard --reach-connect "--src 0 --dst 1 --move maze" --reach-connect "--src 1 --dst 0 --move maze"

python scheme2output.py --outfile work/cave-junction-d --schemefile work/cave-junction.scheme --size 15 15 --pattern-hard --count-soft --reach-junction 0 tl 4 --reach-junction 1 tr 4 --reach-junction 2 bl 4 --reach-junction 3 br 4 --reach-connect "--src 0 --dst 1 --move maze" --reach-connect "--src 1 --dst 3 --move maze" --reach-connect "--src 3 --dst 2 --move maze" --reach-connect "--src 2 --dst 0 --move maze"

python scheme2output.py --outfile work/cave-junction-c --schemefile work/cave-junction.scheme --size 15 15 --pattern-hard --count-soft --reach-junction 0 tl 4 --reach-junction 1 tr 4 --reach-junction 2 bl 4 --reach-junction 3 br 4 --reach-connect "--src 0 --dst 2 --move maze --unreachable" --reach-connect "--src 0 --dst 1 --move maze" --reach-connect "--src 2 --dst 3 --move maze" --reach-print-internal

# cave-doors
python input2tile.py --outfile work/cave-doors.tile --textfile levels/kenney/cave-doors.lvl --imagefile levels/kenney/cave-doors.png
python tile2scheme.py --outfile work/cave-doors.scheme --tilefile work/cave-doors.tile --pattern nbr-plus

python scheme2output.py --outfile work/cave-doors --schemefile work/cave-doors.scheme --size 15 15 --pattern-hard \
  --reach-junction "{" tl 4 \
  --reach-junction "}" br 4 \
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
python input2tile.py --outfile work/mario.tile --textfile levels/vglc/mario-1-1-generic.lvl
python tile2scheme.py --outfile work/mario.scheme --tilefile work/mario.tile --count-divs 1 1 --pattern ring

python scheme2output.py --outfile work/mario --schemefile work/mario.scheme --size 14 32 --pattern-hard --count-soft --reach-start-goal l-r 6 --reach-move platform --reach-unreachable
python level2repath.py --outfile work/mario-rp1.lvl --textfile work/mario.lvl --reach-connect "--src { --dst } --move platform --unreachable" --print-level
python level2repath.py --outfile work/mario-rp2.lvl --textfile work/mario.lvl --reach-connect "--src { --dst } --move platform --unreachable" --print-level --type edges

python scheme2output.py --outfile work/mario-a --schemefile work/mario.scheme --size 14 32 --pattern-hard --count-soft --reach-junction "{" l 6 --reach-junction "}" r 6 --reach-connect "--src { --dst } --move platform" --reach-connect "--src } --dst { --move platform"
python level2repath.py --outfile work/mario-a-rp1.lvl --textfile work/mario-a.lvl --reach-connect "--src { --dst } --move platform" --reach-connect "--src } --dst { --move platform" --print-level
python level2repath.py --outfile work/mario-a-rp2.lvl --textfile work/mario-a.lvl --reach-connect "--src { --dst } --move platform" --reach-connect "--src } --dst { --move platform" --print-level --type edges

python scheme2output.py --outfile work/mario-b --schemefile work/mario.scheme --size 14 32 --pattern-hard --count-soft --reach-junction "{" l 6 --reach-junction "}" r 6 --reach-connect "--src { --dst } --move platform" --reach-connect "--src } --dst { --move platform --unreachable"
python level2repath.py --outfile work/mario-b-rp1.lvl --textfile work/mario-b.lvl --reach-connect "--src { --dst } --move platform" --reach-connect "--src } --dst { --move platform --unreachable" --print-level
python level2repath.py --outfile work/mario-b-rp2.lvl --textfile work/mario-b.lvl --reach-connect "--src { --dst } --move platform" --reach-connect "--src } --dst { --move platform --unreachable" --print-level --type edges

# mario special move
python scheme2output.py --outfile work/mario-special --schemefile work/mario.scheme --size 14 32 --pattern-hard --count-soft --reach-junction "{" l 6 --reach-junction "}" r 6 --reach-connect "--src { --dst } --move platform --unreachable" --reach-connect "--src { --dst } --move platform-highjump"
python level2repath.py --outfile work/mario-special-rp1.lvl --textfile work/mario-special.lvl --reach-connect "--src { --dst } --move platform --unreachable" --reach-connect "--src { --dst } --move platform-highjump" --print-level
python level2repath.py --outfile work/mario-special-rp2.lvl --textfile work/mario-special.lvl --reach-connect "--src { --dst } --move platform --unreachable" --reach-connect "--src { --dst } --move platform-highjump" --print-level --type edges
