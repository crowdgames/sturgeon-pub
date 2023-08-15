set -e
set -x

export STG_MUTE_TIME=1

rm -rf work
mkdir -p work

# examples
python3 input2tile.py --outfile work/mkjr-walk.tile --textfile levels/mkiii/mkjr-walk.lvl
python3 tile2scheme.py --outfile work/mkjr-walk.scheme --tilefile work/mkjr-walk.tile
python3 scheme2output.py --outfile work/mkjr-walk --schemefile work/mkjr-walk.scheme --mkiii-example mkjr-walk --size 15 15 --mkiii-layers 40 --solver pysat-minicard

python3 input2tile.py --outfile work/mkjr-walk-thru.tile --textfile levels/mkiii/mkjr-walk-thru.lvl
python3 tile2scheme.py --outfile work/mkjr-walk-thru.scheme --tilefile work/mkjr-walk-thru.tile
python3 scheme2output.py --outfile work/mkjr-walk-thru --schemefile work/mkjr-walk-thru.scheme --mkiii-example mkjr-walk-thru --size 15 15 --mkiii-layers 40 --solver pysat-minicard

python3 input2tile.py --outfile work/mkjr-maze.tile --textfile levels/mkiii/mkjr-maze.lvl
python3 tile2scheme.py --outfile work/mkjr-maze.scheme --tilefile work/mkjr-maze.tile
python3 scheme2output.py --outfile work/mkjr-maze --schemefile work/mkjr-maze.scheme --mkiii-example mkjr-maze --size 15 15 --mkiii-layers 40 --solver pysat-minicard

python3 scheme2output.py --outfile work/mkjr-maze --schemefile work/mkjr-maze.scheme --mkiii-example mkjr-maze-coin --size 15 15 --mkiii-layers 40 --solver pysat-minicard

python3 input2tile.py --outfile work/link.tile --textfile levels/mkiii/link.lvl
python3 tile2scheme.py --outfile work/link.scheme --tilefile work/link.tile
python3 scheme2output.py --outfile work/link --schemefile work/link.scheme --mkiii-example link --size 5 5 --mkiii-layers 10 --solver pysat-minicard

python3 input2tile.py --outfile work/soko.tile --textfile levels/mkiii/soko.lvl
python3 tile2scheme.py --outfile work/soko.scheme --tilefile work/soko.tile
python3 scheme2output.py --outfile work/soko --schemefile work/soko.scheme --mkiii-example soko --size 8 8 --mkiii-layers 15 --solver pysat-minicard

python3 input2tile.py --outfile work/slide.tile --textfile levels/mkiii/slide.lvl
python3 tile2scheme.py --outfile work/slide.scheme --tilefile work/slide.tile --pattern noout-bl-2 --level-rotate
python3 scheme2output.py --outfile work/slide --schemefile work/slide.scheme --mkiii-example slide --size 8 8 --mkiii-layers 51 --solver pysat-minicard

python3 input2tile.py --outfile work/fill.tile --textfile levels/mkiii/fill.lvl
python3 tile2scheme.py --outfile work/fill.scheme --tilefile work/fill.tile
python3 scheme2output.py --outfile work/fill --schemefile work/fill.scheme --mkiii-example fill --size 6 6 --mkiii-layers 25 --solver pysat-minicard

python3 input2tile.py --outfile work/lock.tile --textfile levels/mkiii/lock.lvl
python3 tile2scheme.py --outfile work/lock.scheme --tilefile work/lock.tile --pattern noout-bl-2 --level-rotate
python3 scheme2output.py --outfile work/lock --schemefile work/lock.scheme --mkiii-example lock --size 8 10 --mkiii-layers 31 --solver pysat-minicard

python3 input2tile.py --outfile work/plat.tile --textfile levels/mkiii/plat.lvl
python3 tile2scheme.py --outfile work/plat.scheme --tilefile work/plat.tile --pattern noout-gc-2
python3 scheme2output.py --outfile work/plat --schemefile work/plat.scheme --mkiii-example plat --size 8 12 --mkiii-layers 40 --solver pysat-minicard

python3 input2tile.py --outfile work/vvv.tile --textfile levels/mkiii/vvv.lvl
python3 tile2scheme.py --outfile work/vvv.scheme --tilefile work/vvv.tile --pattern noout-gc-2
python3 scheme2output.py --outfile work/vvv --schemefile work/vvv.scheme --mkiii-example vvv --size 9 14 --mkiii-layers 47 --solver pysat-minicard

python3 input2tile.py --outfile work/match.tile --textfile levels/mkiii/match.lvl
python3 tile2scheme.py --outfile work/match.scheme --tilefile work/match.tile
python3 scheme2output.py --outfile work/match --schemefile work/match.scheme --mkiii-example match --size 4 4 --mkiii-layers 10 --solver pysat-minicard

python3 input2tile.py --outfile work/doku.tile --textfile levels/mkiii/doku.lvl
python3 tile2scheme.py --outfile work/doku.scheme --tilefile work/doku.tile
python3 scheme2output.py --outfile work/doku --schemefile work/doku.scheme --mkiii-example doku --size 9 9 --mkiii-layers 10 --solver pysat-minicard
