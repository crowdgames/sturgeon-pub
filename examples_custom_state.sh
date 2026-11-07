set -e
set -x

export STG_MUTE_TIME=1

rm -rf work
mkdir -p work

python input2tile.py --outfile work/mario.tile --textfile levels/vglc/mario-1-1-generic.lvl
python tile2scheme.py --outfile work/mario.scheme --tilefile work/mario.tile --pattern block-noout,2,2

python scheme2output.py --outfile work/mario-count-edge-tile --schemefile work/mario.scheme --size 10 16 --pattern-hard --reach-move platform --reach-start-goal all --reach-null --custom path-state count-edge,5,5 tile 20 0 hard
python scheme2output.py --outfile work/mario-count-edge-up-tile --schemefile work/mario.scheme --size 10 16 --pattern-hard --reach-move platform --reach-start-goal all --reach-null --custom path-state count-edge-up,5,5 tile 20 0 hard
python scheme2output.py --outfile work/mario-count-edge-down-tile --schemefile work/mario.scheme --size 10 16 --pattern-hard --reach-move platform --reach-start-goal all --reach-null --custom path-state count-edge-down,5,5 tile 20 0 hard
python scheme2output.py --outfile work/mario-count-edge-left-tile --schemefile work/mario.scheme --size 10 16 --pattern-hard --reach-move platform --reach-start-goal all --reach-null --custom path-state count-edge-left,5,5 tile 20 0 hard
python scheme2output.py --outfile work/mario-count-edge-right-tile --schemefile work/mario.scheme --size 10 16 --pattern-hard --reach-move platform --reach-start-goal all --reach-null --custom path-state count-edge-right,5,5 tile 20 0 hard

python scheme2output.py --outfile work/mario-count-edge-jump-edge --schemefile work/mario.scheme --size 10 16 --pattern-hard --reach-move platform --reach-start-goal l-r 2 --reach-null --custom path-state count-edge-jump,5,5 edge 20 20 hard
python scheme2output.py --outfile work/mario-count-edge-jump-tile --schemefile work/mario.scheme --size 10 16 --pattern-hard --reach-move platform --reach-start-goal l-r 2 --reach-null --custom path-state count-edge-jump,5,5 tile 25 20 hard

python level2repath.py --outfile work/mario-count-edge-jump-tile-rp.lvl --textfile work/mario-count-edge-jump-tile.lvl --reach-connect "--src { --dst } --move platform" --cost tile --enum
python level2metric.py --textfile work/mario-count-edge-jump-tile-rp.lvl --metric count-edge-jump --open "-" --src "{" --dst "}"

python scheme2output.py --outfile work/mario-count-edge-onground-edge --schemefile work/mario.scheme --size 10 16 --pattern-hard --reach-move platform --reach-start-goal l-r 2 --reach-null --custom path-state count-edge-onground,5,5 edge 20 20 hard
python scheme2output.py --outfile work/mario-count-edge-onground-tile --schemefile work/mario.scheme --size 10 16 --pattern-hard --reach-move platform --reach-start-goal l-r 2 --reach-null --custom path-state count-edge-onground,5,5 tile 25 20 hard

python level2repath.py --outfile work/mario-count-edge-onground-tile-rp.lvl --textfile work/mario-count-edge-onground-tile.lvl --reach-connect "--src { --dst } --move platform" --cost tile --enum
python level2metric.py --textfile work/mario-count-edge-onground-tile-rp.lvl --metric count-edge-onground --open "-" --src "{" --dst "}"

python scheme2output.py --outfile work/mario-count-tile-edge --schemefile work/mario.scheme --size 10 16 --pattern-hard --reach-move platform --reach-start-goal l-r 2 --reach-null --custom path-state count-tile,16,16 edge 20 20 hard
python scheme2output.py --outfile work/mario-count-tile-tile --schemefile work/mario.scheme --size 10 16 --pattern-hard --reach-move platform --reach-start-goal l-r 2 --reach-null --custom path-state count-tile,16,16 tile 25 20 hard

python level2repath.py --outfile work/mario-count-tile-tile-rp.lvl --textfile work/mario-count-tile-tile.lvl --reach-connect "--src { --dst } --move platform" --cost tile --enum
python level2metric.py --textfile work/mario-count-tile-tile-rp.lvl --metric count-tile --open "-" --src "{" --dst "}"

python scheme2output.py --outfile work/mario-airtime-jump-edge --schemefile work/mario.scheme --size 10 16 --pattern-hard --reach-move platform --reach-start-goal l-r 2 --reach-null --custom path-state airtime-jump,10,10 edge 20 0 hard
python scheme2output.py --outfile work/mario-airtime-jump-tile --schemefile work/mario.scheme --size 10 16 --pattern-hard --reach-move platform --reach-start-goal l-r 2 --reach-null --custom path-state airtime-jump,10,10 tile 25 0 hard

python level2repath.py --outfile work/mario-airtime-jump-tile-rp.lvl --textfile work/mario-airtime-jump-tile.lvl --reach-connect "--src { --dst } --move platform" --cost tile --enum
python level2metric.py --textfile work/mario-airtime-jump-tile-rp.lvl --metric count-tile --open "-" --src "{" --dst "}"

python scheme2output.py --outfile work/mario-jumpentropy-edge --schemefile work/mario.scheme --size 10 16 --pattern-hard --reach-move platform --reach-start-goal l-r 2 --reach-null --custom path-state jumpentropy,0.166,0.167,0.2 edge 20 0 hard
python scheme2output.py --outfile work/mario-jumpentropy-tile --schemefile work/mario.scheme --size 10 16 --pattern-hard --reach-move platform --reach-start-goal l-r 2 --reach-null --custom path-state jumpentropy,0.166,0.167,0.2 tile 25 0 hard

python level2repath.py --outfile work/mario-jumpentropy-tile-rp.lvl --textfile work/mario-jumpentropy-tile.lvl --reach-connect "--src { --dst } --move platform" --cost tile --enum
python level2metric.py --textfile work/mario-jumpentropy-tile-rp.lvl --metric jumpentropy --open "-" --src "{" --dst "}"

python scheme2output.py --outfile work/mario-speed-edge --schemefile work/mario.scheme --size 10 16 --pattern-hard --reach-move platform --reach-start-goal l-r 2 --reach-null --custom path-state speed,0.65,0.65,0.2 edge 20 0 hard
python scheme2output.py --outfile work/mario-speed-tile --schemefile work/mario.scheme --size 10 16 --pattern-hard --reach-move platform --reach-start-goal l-r 2 --reach-null --custom path-state speed,0.65,0.65,0.2 tile 25 0 hard

python level2repath.py --outfile work/mario-speed-tile-rp.lvl --textfile work/mario-speed-tile.lvl --reach-connect "--src { --dst } --move platform" --cost tile --enum
python level2metric.py --textfile work/mario-speed-tile-rp.lvl --metric speed --open "-" --src "{" --dst "}"

python scheme2output.py --outfile work/mario-ongroundratio-edge --schemefile work/mario.scheme --size 10 16 --pattern-hard --reach-move platform --reach-start-goal l-r 2 --reach-null --custom path-state ongroundratio,0.4,0.4,0.2 edge 20 0 hard
python scheme2output.py --outfile work/mario-ongroundratio-tile --schemefile work/mario.scheme --size 10 16 --pattern-hard --reach-move platform --reach-start-goal l-r 2 --reach-null --custom path-state ongroundratio,0.4,0.4,0.2 tile 25 0 hard

python level2repath.py --outfile work/mario-ongroundratio-tile-rp.lvl --textfile work/mario-ongroundratio-tile.lvl --reach-connect "--src { --dst } --move platform" --cost tile --enum
python level2metric.py --textfile work/mario-ongroundratio-tile-rp.lvl --metric ongroundratio --open "-" --src "{" --dst "}"

python scheme2output.py --outfile work/mario-average-row-edge --schemefile work/mario.scheme --size 10 16 --pattern-hard --reach-move platform --reach-start-goal l-r 2 --reach-null --custom path-state average-row,5.1,5.1,-3.6 edge 20 0 hard
python scheme2output.py --outfile work/mario-average-row-tile --schemefile work/mario.scheme --size 10 16 --pattern-hard --reach-move platform --reach-start-goal l-r 2 --reach-null --custom path-state average-row,5.1,5.1,-3.6 tile 25 0 hard

python level2repath.py --outfile work/mario-average-row-tile-rp.lvl --textfile work/mario-average-row-tile.lvl --reach-connect "--src { --dst } --move platform" --cost tile --enum
python level2metric.py --textfile work/mario-average-row-tile-rp.lvl --metric average-row --open "-" --src "{" --dst "}"

python scheme2output.py --outfile work/mario-any-edge --schemefile work/mario.scheme --size 10 16 --pattern-hard --reach-move platform --reach-start-goal l-r 2 --reach-null --custom path-state any edge 20 0 hard
python scheme2output.py --outfile work/mario-any-tile --schemefile work/mario.scheme --size 10 16 --pattern-hard --reach-move platform --reach-start-goal l-r 2 --reach-null --custom path-state any tile 25 0 hard
