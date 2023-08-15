set -e
set -x

export STG_MUTE_TIME=1

rm -rf work
mkdir -p work

python3 input2tile.py --outfile work/tiny1.tile --textfile levels/kenney/tiny-00.lvl levels/kenney/tiny-01.lvl levels/kenney/tiny-02.lvl --imagefile levels/kenney/tiny-00.png levels/kenney/tiny-01.png levels/kenney/tiny-02.png
python3 levels2explore.py --outfile work/tiny1.explore --tilefile work/tiny1.tile

python3 file2file.py --outfile work/tiny1.jtile --infile work/tiny1.tile
python3 file2file.py --outfile work/tiny2.tile --infile work/tiny1.jtile
python3 file2file.py --outfile work/tiny2.jtile --infile work/tiny2.tile
md5 work/tiny1.tile work/tiny2.tile work/tiny1.jtile work/tiny2.jtile

python3 file2file.py --outfile work/tiny1.jexplore --infile work/tiny1.explore
python3 file2file.py --outfile work/tiny2.explore --infile work/tiny1.jexplore
python3 file2file.py --outfile work/tiny2.jexplore --infile work/tiny2.explore
md5 work/tiny1.explore work/tiny2.explore work/tiny1.jexplore work/tiny2.jexplore
