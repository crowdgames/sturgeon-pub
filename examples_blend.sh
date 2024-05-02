set -e
set -x

export STG_MUTE_TIME=1

rm -rf work
mkdir -p work

# multiple example levels
python3 input2tile.py --outfile work/cave-gems_ti.tile --textfile levels/kenney/cave.lvl levels/kenney/cave-gems.lvl --imagefile levels/kenney/cave.png levels/kenney/cave-gems.png
python3 tile2scheme.py --outfile work/cave-gems_ti.scheme --tilefile work/cave-gems_ti.tile --count-divs 1 1 --pattern nbr-plus
python3 scheme2output.py --outfile work/cave-gems_ti --schemefile work/cave-gems_ti.scheme --size 15 15 --pattern-hard --count-soft --reach-move maze --reach-start-goal br-tl 5

# mario and cave
python3 input2tile.py --outfile work/mario-cave_ti.tile --textfile levels/vglc/mario-1-1-generic.lvl levels/kenney/cave.lvl --imagefile levels/vglc/mario-1-1-clean.png levels/kenney/cave.png --game M C
python3 tile2scheme.py --outfile work/mario-cave_ti.scheme --tilefile work/mario-cave_ti.tile --count-divs 1 1 --pattern M=ring C=nbr-plus
python3 scheme2output.py --outfile work/mario-cave_ti --schemefile work/mario-cave_ti.scheme --game levels/vglc/mario-cave.game --pattern-soft --count-soft --reach-move M=platform C=maze --reach-start-goal l-r 6

# mario by icarus
python3 input2tile.py --outfile work/mario-icarus-ti.tile --textfile levels/vglc/mario-1-1-generic.lvl levels/vglc/kidicarus-1-doors.lvl --imagefile levels/vglc/mario-1-1-clean.png levels/vglc/kidicarus-1-clean.png --tagfile levels/vglc/mario-1-1-generic.lvl levels/vglc/kidicarus-1-doors.lvl --game M I
python3 tile2scheme.py --outfile work/mario-icarus-ti.scheme --tilefile work/mario-icarus-ti.tile --count-divs 5 5 --pattern M=nbr-l I=nbr-l
python3 tag2game.py --outfile work/mario-by-icarus.game --tagfile levels/vglc/mario-1-1-generic.lvl --schemefile work/mario-icarus-ti.scheme --game I M
python3 scheme2output.py --outfile work/mario-by-icarus-ti --schemefile work/mario-icarus-ti.scheme --tagfile levels/vglc/mario-1-1-generic.lvl --gamefile work/mario-by-icarus.game --pattern-soft --count-soft
