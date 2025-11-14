set -e
set -x

export STG_MUTE_TIME=1

rm -rf work
mkdir -p work

# sokoban

cp levels/manual/sokoban_1.lvl work/sokoban-in.lvl
python level2concat.py --outfile work/sokoban-in --game 0 1 2 X --pad-between 1 --size 11 19 --term-inst 235

python input2tile.py --outfile work/sokoban-11.tile --textfile work/sokoban-in.lvl --gamefile work/sokoban-in.game
python tile2scheme.py --outfile work/sokoban-P.scheme --tilefile work/sokoban-11.tile --pattern 0=single 2=single X=single
python tilediff2scheme.py --outfile work/sokoban-11-D.scheme --tilefile work/sokoban-11.tile --diff-offset-row 12 --game 1
python scheme2merge.py --outfile work/sokoban-11.scheme --schemefile work/sokoban-P.scheme work/sokoban-11-D.scheme --remove-void

python scheme2merge.py --outfile work/sokoban-8.scheme --schemefile work/sokoban-11.scheme --remap-row " -14,-10=3" " -2,2=0" "10,14=-3"

python level2concat.py --outfile work/sokoban-tpl-8.tag --pad-between 1 --size 8 8 --term-inst 10 --game 0 1 2 X
python level2concat.py --outfile work/sokoban-tpl-8.lvl --pad-between 1 --size 6 6 --term-inst 10 --pad-around W

python scheme2output.py --outfile work/sokoban-8 --schemefile work/sokoban-8.scheme \
       --pattern-hard --pattern-single --pattern-ignore-no-in-void \
       --custom text-count 0 0 8 8 "P" 1 1 hard \
       --custom text-count 0 0 8 8 "B" 2 2 hard \
       --custom text-level work/sokoban-tpl-8.lvl hard \
       --tagfile work/sokoban-tpl-8.tag \
       --gamefile work/sokoban-tpl-8.game

# block dude

python level2concat.py --outfile work/blockdude-in-0.lvl --textfile levels/manual/blockdude_1/*.lvl --game 0 1 2 X --pad-between 1 --term-inst 3
python level2concat.py --outfile work/blockdude-in-1.lvl --textfile levels/manual/blockdude_1/*.lvl --game 0 1 2 X --pad-between 1 --term-inst 3 --xform-flip-cols

python input2tile.py --outfile work/blockdude-6.tile --textfile work/blockdude-in-*.lvl --gamefile work/blockdude-in-*.game
python tile2scheme.py --outfile work/blockdude-P.scheme --tilefile work/blockdude-6.tile --pattern 0=block-noout,2,1 2=single X=single
python tilediff2scheme.py --outfile work/blockdude-6-D.scheme --tilefile work/blockdude-6.tile --diff-offset-row 7 --game 1 --context "1 0"
python scheme2merge.py --outfile work/blockdude-6.scheme --schemefile work/blockdude-P.scheme work/blockdude-6-D.scheme --remove-void

python level2concat.py --outfile work/blockdude-tpl-6.tag --pad-between 1 --size 6 10 --term-inst 10 --game 0 1 2 X
python level2concat.py --outfile work/blockdude-tpl-6.lvl --pad-between 1 --size 4  8 --term-inst 10 --pad-around W _ W W W W W W

python scheme2output.py --outfile work/blockdude-6 --schemefile work/blockdude-6.scheme \
       --pattern-hard --pattern-single --pattern-ignore-no-in-void \
       --custom text-count 0 0  6 10 "P" 1 1 hard \
       --custom text-count 0 0  6  2 "P" 1 1 hard \
       --custom text-count 0 0  6 10 "D" 1 1 hard \
       --custom text-count 0 8  6 10 "D" 1 1 hard \
       --custom text-count 0 0  6 10 "B" 1 1 hard \
       --custom text-count 0 0 63 10 "Q" 1 9 hard \
       --custom text-level work/blockdude-tpl-6.lvl hard \
       --tagfile work/blockdude-tpl-6.tag \
       --gamefile work/blockdude-tpl-6.game
