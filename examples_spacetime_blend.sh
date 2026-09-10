set -e
set -x

export STG_MUTE_TIME=1

rm -rf work
mkdir -p work

# field setup

python level2concat.py --outfile work/field-rc-00.lvl --jsonfile levels/manual/field-5x5.json --game 0 1 2 X --pad-rows 1 --term-inst 3
python level2concat.py --outfile work/field-rc-01.lvl --jsonfile levels/manual/field-5x5.json --game 0 1 2 X --pad-rows 1 --term-inst 3 --xform-rotate 1
python level2concat.py --outfile work/field-rc-02.lvl --jsonfile levels/manual/field-5x5.json --game 0 1 2 X --pad-rows 1 --term-inst 3 --xform-rotate 2
python level2concat.py --outfile work/field-rc-03.lvl --jsonfile levels/manual/field-5x5.json --game 0 1 2 X --pad-rows 1 --term-inst 3 --xform-rotate 3

python concat2level.py --outfile work/field-rs-00.lvl --textfile work/field-rc-00.lvl --slice-cols --pad-cols 5
python concat2level.py --outfile work/field-rs-01.lvl --textfile work/field-rc-01.lvl --slice-cols --pad-cols 5
python concat2level.py --outfile work/field-rs-02.lvl --textfile work/field-rc-02.lvl --slice-cols --pad-cols 5
python concat2level.py --outfile work/field-rs-03.lvl --textfile work/field-rc-03.lvl --slice-cols --pad-cols 5

python level2concat.py --outfile work/field-rs-00.game --size 5 1 --term-inst 7 --across-cols 5 --pad-rows 1 --pad-cols 5 --game 0 1 2 X
python level2concat.py --outfile work/field-rs-01.game --size 5 1 --term-inst 7 --across-cols 5 --pad-rows 1 --pad-cols 5 --game 0 1 2 X
python level2concat.py --outfile work/field-rs-02.game --size 5 1 --term-inst 7 --across-cols 5 --pad-rows 1 --pad-cols 5 --game 0 1 2 X
python level2concat.py --outfile work/field-rs-03.game --size 5 1 --term-inst 7 --across-cols 5 --pad-rows 1 --pad-cols 5 --game 0 1 2 X

python concat2level.py --outfile work/field-cs-00.lvl --textfile work/field-rc-00.lvl --slice-rows --pad-rows 5
python concat2level.py --outfile work/field-cs-01.lvl --textfile work/field-rc-01.lvl --slice-rows --pad-rows 5
python concat2level.py --outfile work/field-cs-02.lvl --textfile work/field-rc-02.lvl --slice-rows --pad-rows 5
python concat2level.py --outfile work/field-cs-03.lvl --textfile work/field-rc-03.lvl --slice-rows --pad-rows 5

python level2concat.py --outfile work/field-cs-00.game --size 1 5 --term-inst 7 --across-cols 5 --pad-rows 5 --pad-cols 1 --game 0 1 2 X
python level2concat.py --outfile work/field-cs-01.game --size 1 5 --term-inst 7 --across-cols 5 --pad-rows 5 --pad-cols 1 --game 0 1 2 X
python level2concat.py --outfile work/field-cs-02.game --size 1 5 --term-inst 7 --across-cols 5 --pad-rows 5 --pad-cols 1 --game 0 1 2 X
python level2concat.py --outfile work/field-cs-03.game --size 1 5 --term-inst 7 --across-cols 5 --pad-rows 5 --pad-cols 1 --game 0 1 2 X

# soko setup

python level2concat.py --outfile work/soko-rc-00.lvl --jsonfile levels/manual/soko-5x5.json --game 0 1 2 X --pad-rows 1 --term-inst 3
python level2concat.py --outfile work/soko-rc-01.lvl --jsonfile levels/manual/soko-5x5.json --game 0 1 2 X --pad-rows 1 --term-inst 3 --xform-rotate 1
python level2concat.py --outfile work/soko-rc-02.lvl --jsonfile levels/manual/soko-5x5.json --game 0 1 2 X --pad-rows 1 --term-inst 3 --xform-rotate 2
python level2concat.py --outfile work/soko-rc-03.lvl --jsonfile levels/manual/soko-5x5.json --game 0 1 2 X --pad-rows 1 --term-inst 3 --xform-rotate 3

# tileset

python input2tile.py --outfile work/field-x-soko.tileset --out-tileset --text-key-only --textfile work/field-*.lvl work/soko-*.lvl

# schemes

python input2tile.py --outfile work/field-rc.tile --textfile work/field-rc-*.lvl --gamefile work/field-rc-*.game --tileset work/field-x-soko.tileset
python tile2scheme.py --outfile work/field-rc-pattern.scheme --tilefile work/field-rc.tile --pattern 0=single 2=single X=single
python tilediff2scheme.py --outfile work/field-rc-diff.scheme --tilefile work/field-rc.tile --diff-offset-row 6 --game 1
python scheme2merge.py --outfile work/field-rc.scheme --schemefile work/field-rc-diff.scheme work/field-rc-pattern.scheme --remove-void

python input2tile.py --outfile work/field-rs.tile --textfile work/field-rs-*.lvl --gamefile work/field-rs-*.game --tileset work/field-x-soko.tileset
python tile2scheme.py --outfile work/field-rs-pattern.scheme --tilefile work/field-rs.tile --pattern 0=single 2=single X=single
python tilediff2scheme.py --outfile work/field-rs-diff.scheme --tilefile work/field-rs.tile --diff-offset-row 6 --game 1
python scheme2merge.py --outfile work/field-rs.scheme --schemefile work/field-rs-diff.scheme work/field-rs-pattern.scheme --remove-void

python input2tile.py --outfile work/field-cs.tile --textfile work/field-cs-*.lvl --gamefile work/field-cs-*.game --tileset work/field-x-soko.tileset
python tile2scheme.py --outfile work/field-cs-pattern.scheme --tilefile work/field-cs.tile --pattern 0=single 2=single X=single
python tilediff2scheme.py --outfile work/field-cs-diff.scheme --tilefile work/field-cs.tile --diff-offset-row 6 --game 1
python scheme2merge.py --outfile work/field-cs.scheme --schemefile work/field-cs-diff.scheme work/field-cs-pattern.scheme --remove-void

python input2tile.py --outfile work/soko-rc.tile --textfile work/soko-rc-*.lvl --gamefile work/soko-rc-*.game --tileset work/field-x-soko.tileset
python tile2scheme.py --outfile work/soko-rc-pattern.scheme --tilefile work/soko-rc.tile --pattern 0=single 2=single X=single
python tilediff2scheme.py --outfile work/soko-rc-diff.scheme --tilefile work/soko-rc.tile --diff-offset-row 6 --game 1
python scheme2merge.py --outfile work/soko-rc.scheme --schemefile work/soko-rc-diff.scheme work/soko-rc-pattern.scheme --remove-void

# blend field-rc x field-rs 3D

python scheme2merge.py --outfile work/field-rc-x-field-rs.scheme --schemefile work/field-rc.scheme work/field-rs.scheme

python level2concat.py --outfile work/field-rc-x-field-rs.tag --size 5 5 --across-cols 5 --pad-rows 1 --pad-cols 1 --term-inst 10 --game 0 1 2 X

python scheme2output.py --outfile work/field-rc-x-field-rs-out --schemefile work/field-rc-x-field-rs.scheme \
       --pattern-hard --pattern-single --pattern-ignore-no-in-void \
       --custom text-count 0  0 5 29 "P" 1 1 hard \
       --custom text-count 1  1 2  2 "P" 1 1 hard \
       --custom text-count 0  0 5 29 "D" 1 1 hard \
       --custom text-count 3 27 4 28 "D" 1 1 hard \
       --tagfile work/field-rc-x-field-rs.tag \
       --gamefile work/field-rc-x-field-rs.game

python level2vtk.py --outfile work/field-rc-x-field-rs-out- --textfile work/field-rc-x-field-rs-out.lvl --tileset work/field-x-soko.tileset --print-vtk

# blend field-rc x field-cs 3D

python scheme2merge.py --outfile work/field-rc-x-field-cs.scheme --schemefile work/field-rc.scheme work/field-cs.scheme

python level2concat.py --outfile work/field-rc-x-field-cs.tag --size 5 5 --across-cols 5 --pad-rows 1 --pad-cols 1 --term-inst 10 --game 0 1 2 X

python scheme2output.py --outfile work/field-rc-x-field-cs-out --schemefile work/field-rc-x-field-cs.scheme \
       --pattern-hard --pattern-single --pattern-ignore-no-in-void \
       --custom text-count 0  0 5 29 "P" 1 1 hard \
       --custom text-count 1  1 2  2 "P" 1 1 hard \
       --custom text-count 0  0 5 29 "D" 1 1 hard \
       --custom text-count 3 27 4 28 "D" 1 1 hard \
       --tagfile work/field-rc-x-field-cs.tag \
       --gamefile work/field-rc-x-field-cs.game

python level2vtk.py --outfile work/field-rc-x-field-cs-out- --textfile work/field-rc-x-field-cs-out.lvl --tileset work/field-x-soko.tileset --print-vtk

# blend field-rs x field-cs 3D

python scheme2merge.py --outfile work/field-rs-x-field-cs.scheme --schemefile work/field-rs.scheme work/field-cs.scheme

python level2concat.py --outfile work/field-rs-x-field-cs.tag --size 5 5 --across-cols 5 --pad-rows 1 --pad-cols 1 --term-inst 10 --game 0 1 2 X

python scheme2output.py --outfile work/field-rs-x-field-cs-out --schemefile work/field-rs-x-field-cs.scheme \
       --pattern-hard --pattern-single --pattern-ignore-no-in-void \
       --custom text-count 0  0 5 29 "P" 1 1 hard \
       --custom text-count 1  1 2  2 "P" 1 1 hard \
       --custom text-count 0  0 5 29 "D" 1 1 hard \
       --custom text-count 3 27 4 28 "D" 1 1 hard \
       --tagfile work/field-rs-x-field-cs.tag \
       --gamefile work/field-rs-x-field-cs.game

python level2vtk.py --outfile work/field-rs-x-field-cs-out- --textfile work/field-rs-x-field-cs-out.lvl --tileset work/field-x-soko.tileset --print-vtk

# blend field-rc x field-rs x field-cs 3D

python scheme2merge.py --outfile work/field-rc-x-field-rs-x-field-cs.scheme --schemefile work/field-rc.scheme work/field-rs.scheme work/field-cs.scheme

python level2concat.py --outfile work/field-rc-x-field-rs-x-field-cs.tag --size 5 5 --across-cols 5 --pad-rows 1 --pad-cols 1 --term-inst 10 --game 0 1 2 X

python scheme2output.py --outfile work/field-rc-x-field-rs-x-field-cs-out --schemefile work/field-rc-x-field-rs-x-field-cs.scheme \
       --pattern-hard --pattern-single --pattern-ignore-no-in-void \
       --custom text-count 0  0 5 29 "P" 1 1 hard \
       --custom text-count 1  1 2  2 "P" 1 1 hard \
       --custom text-count 0  0 5 29 "D" 1 1 hard \
       --custom text-count 3 27 4 28 "D" 1 1 hard \
       --tagfile work/field-rc-x-field-rs-x-field-cs.tag \
       --gamefile work/field-rc-x-field-rs-x-field-cs.game

python level2vtk.py --outfile work/field-rc-x-field-rs-x-field-cs-out- --textfile work/field-rc-x-field-rs-x-field-cs-out.lvl --tileset work/field-x-soko.tileset --print-vtk

# blend soko-rc x field-rc 2D

python scheme2merge.py --outfile work/soko-rc-x-field-rc.scheme --schemefile work/field-rc.scheme work/soko-rc.scheme

python level2concat.py --outfile work/soko-rc-x-field-rc.tag --size 5 5 --pad-rows 1 --term-inst 8 --game 0 1 2 X

python scheme2output.py --outfile work/soko-rc-x-field-rc-out --schemefile work/soko-rc-x-field-rc.scheme \
       --pattern-hard --pattern-single --pattern-ignore-no-in-void \
       --custom text-count 0 0 5 5 "P" 1 1 hard \
       --custom text-count 1 1 2 2 "P" 1 1 hard \
       --custom text-count 0 0 5 5 "B" 2 2 hard \
       --custom text-count 0 0 5 5 "O" 2 2 hard \
       --custom text-count 0 0 5 5 "D" 1 1 hard \
       --custom text-count 3 3 4 4 "D" 1 1 hard \
       --custom text-count 0 0 5 5 "W" 0 0 hard \
       --tagfile work/soko-rc-x-field-rc.tag \
       --gamefile work/soko-rc-x-field-rc.game

python level2vtk.py --outfile work/soko-rc-x-field-rc-out- --textfile work/soko-rc-x-field-rc-out.lvl --tileset work/field-x-soko.tileset --print-vtk

# blend soko-rc x field-rs 3D

python scheme2merge.py --outfile work/soko-rc-x-field-rs.scheme --schemefile work/field-rs.scheme work/soko-rc.scheme

python level2concat.py --outfile work/soko-rc-x-field-rs.tag --size 5 5 --across-cols 5 --pad-rows 1 --pad-cols 1 --term-inst 10 --game 0 1 2 X

python scheme2output.py --outfile work/soko-rc-x-field-rs-out --schemefile work/soko-rc-x-field-rs.scheme \
       --pattern-hard --pattern-single --pattern-ignore-no-in-void \
       --custom text-count 0  0 5 29 "P" 1 1 hard \
       --custom text-count 0 12 5 14 "P" 1 1 hard \
       --custom text-count 0  0 5 29 "B" 1 1 hard \
       --custom text-count 0 12 5 17 "B" 0 0 hard \
       --custom text-count 0  0 5 29 "O" 1 1 hard \
       --custom text-count 0 12 5 17 "O" 0 0 hard \
       --custom text-count 0  0 5 29 "D" 1 1 hard \
       --custom text-count 0 15 5 17 "D" 1 1 hard \
       --custom text-count 0  0 5 29 "W" 5 5 hard \
       --custom text-count 0 14 5 15 "W" 5 5 hard \
       --tagfile work/soko-rc-x-field-rs.tag \
       --gamefile work/soko-rc-x-field-rs.game

python level2vtk.py --outfile work/soko-rc-x-field-rs-out- --textfile work/soko-rc-x-field-rs-out.lvl --tileset work/field-x-soko.tileset --print-vtk
