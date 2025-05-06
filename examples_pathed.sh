set -e
set -x

export STG_MUTE_TIME=1

rm -rf work
mkdir -p work

python input2tile.py --outfile work/mario-1-1_ti.tile --textfile levels/vglc/mario-1-1-generic.lvl --imagefile levels/vglc/mario-1-1-flag.png --tilesize 16
python tile2scheme.py --outfile work/mario-1-1_ti.scheme --tilefile work/mario-1-1_ti.tile --count-divs 3 3 --pattern nbr-2
python app_pathed.py --outfolder work --size 14 21 --reach-move platform --schemefile work/mario-1-1_ti.scheme --test

python input2tile.py --outfile work/cave_ti.tile --textfile levels/kenney/cave2.lvl --imagefile levels/kenney/cave2.png --tilesize 16
python tile2scheme.py --outfile work/cave_ti.scheme --tilefile work/cave_ti.tile --count-divs 1 1 --pattern nbr-2
python app_pathed.py --outfolder work --size 10 10 --reach-move maze --schemefile work/cave_ti.scheme --test
python app_pathed.py --outfolder work --size 10 10 --reach-move tomb --schemefile work/cave_ti.scheme --test

python input2tile.py --outfile work/wrap-maze_ti.tile --textfile levels/kenney/wrap-maze.lvl --imagefile levels/kenney/wrap-maze.png
python tile2scheme.py --outfile work/wrap-maze_ti.scheme --tilefile work/wrap-maze_ti.tile
python app_pathed.py --outfolder work --size 9 6 --reach-move maze --schemefile work/wrap-maze_ti.scheme --reach-wrap-rows --reach-wrap-cols --test
