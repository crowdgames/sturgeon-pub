set -e
set -x

export STG_MUTE_TIME=1

rm -rf work
mkdir -p work

python input2tile.py --outfile work/mario-1-1_ti.tile --textfile levels/vglc/mario-1-1-generic.lvl --imagefile levels/vglc/mario-1-1-flag.png --tilesize 16
python tile2scheme.py --outfile work/mario-1-1_ti.scheme --tilefile work/mario-1-1_ti.tile --count-divs 3 3 --pattern nbr-2
python app_editor.py --outfile work/mario-1-1_ti --schemefile work/mario-1-1_ti.scheme --pattern-hard --count-soft --size 14 21 --reach-move platform --reach-start-goal all --app --test

python input2tile.py --outfile work/cave_ti.tile --textfile levels/kenney/cave2.lvl --imagefile levels/kenney/cave2.png --tilesize 16
python tile2scheme.py --outfile work/cave_ti.scheme --tilefile work/cave_ti.tile --count-divs 1 1 --pattern nbr-2
python app_editor.py --outfile work/cave_ti --schemefile work/cave_ti.scheme --pattern-hard --count-soft --size 10 10 --reach-move maze --reach-start-goal all --app --test
python app_editor.py --outfile work/cave_ti --schemefile work/cave_ti.scheme --pattern-hard --count-soft --size 10 10 --reach-move tomb --reach-start-goal all --app --test

python input2tile.py --outfile work/wrap-maze_ti.tile --textfile levels/kenney/wrap-maze.lvl --imagefile levels/kenney/wrap-maze.png
python tile2scheme.py --outfile work/wrap-maze_ti.scheme --tilefile work/wrap-maze_ti.tile
python app_editor.py --outfile work/wrap-maze_ti --schemefile work/wrap-maze_ti.scheme --size 9 6 --reach-move maze --reach-start-goal all --reach-wrap-rows --reach-wrap-cols --app --test
