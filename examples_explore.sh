set -e
set -x

export STG_MUTE_TIME=1

rm -rf work
mkdir -p work

# tiny levels
python input2tile.py --outfile work/tiny.tile --textfile levels/kenney/tiny-??.lvl --imagefile levels/kenney/tiny-??.png

python levels2explore.py --outfile work/tiny.explore --tilefile work/tiny.tile
python explore2summary.py --explorefile work/tiny.explore
python explorer.py --test --explorefile work/tiny.explore

python levels2explore.py --outfile work/tiny-text.explore --tilefile work/tiny.tile --text-only
python explore2summary.py --explorefile work/tiny-text.explore
python explorer.py --test --explorefile work/tiny-text.explore

python levels2explore.py --outfile work/tiny-image.explore --tilefile work/tiny.tile --image-only
python explore2summary.py --explorefile work/tiny-image.explore
python explorer.py --test --explorefile work/tiny-image.explore

# tiny levels from tileset
python input2tile.py --outfile work/tiny-tiles.tileset --textfile levels/kenney/tiny-tiles.lvl --imagefile levels/kenney/tiny-tiles.png --out-tileset
python input2tile.py --outfile work/tiny-tiles.tile --textfile levels/kenney/tiny-tiles-??.lvl --tileset work/tiny-tiles.tileset --text-key-only
python levels2explore.py --outfile work/tiny-tiles.explore --tilefile work/tiny-tiles.tile
python explore2summary.py --explorefile work/tiny-tiles.explore
python explorer.py --test --explorefile work/tiny-tiles.explore

# cave levels
python input2tile.py --outfile work/cave.tile --textfile levels/kenney/cave.lvl --imagefile levels/kenney/cave.png
python tile2scheme.py --outfile work/cave.scheme --tilefile work/cave.tile --count-divs 1 1 --pattern nbr-plus
python scheme2output.py --outfile work/cave-00 --randomize 0 --out-level-none --schemefile work/cave.scheme --size 10 10 --pattern-hard --count-soft --reach-start-goal br-tl 5 --reach-move maze
python scheme2output.py --outfile work/cave-01 --randomize 1 --out-level-none --schemefile work/cave.scheme --size 11 11 --pattern-hard --count-soft --reach-start-goal br-tl 5 --reach-move maze
python scheme2output.py --outfile work/cave-02 --randomize 2 --out-level-none --schemefile work/cave.scheme --size 12 12 --pattern-hard --count-soft --reach-start-goal br-tl 5 --reach-move maze
python scheme2output.py --outfile work/cave-03 --randomize 3 --out-level-none --schemefile work/cave.scheme --size 13 13 --pattern-hard --count-soft --reach-start-goal br-tl 5 --reach-move maze
python scheme2output.py --outfile work/cave-04 --randomize 4 --out-level-none --schemefile work/cave.scheme --size 14 14 --pattern-hard --count-soft --reach-start-goal br-tl 5 --reach-move maze
python levels2explore.py --outfile work/cave.explore --resultfile work/cave-*.result
python explore2summary.py --explorefile work/cave.explore
python explorer.py --test --explorefile work/cave.explore
