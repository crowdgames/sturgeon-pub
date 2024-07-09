set -e
set -x

export STG_MUTE_TIME=1

rm -rf work
mkdir -p work


python input2tile.py --outfile work/tiny1.tileset --textfile levels/kenney/tiny-00.lvl levels/kenney/tiny-01.lvl levels/kenney/tiny-02.lvl --imagefile levels/kenney/tiny-00.png levels/kenney/tiny-01.png levels/kenney/tiny-02.png --out-tileset
python input2tile.py --outfile work/tiny1.tile --textfile levels/kenney/tiny-00.lvl levels/kenney/tiny-01.lvl levels/kenney/tiny-02.lvl --imagefile levels/kenney/tiny-00.png levels/kenney/tiny-01.png levels/kenney/tiny-02.png
python levels2explore.py --outfile work/tiny1.explore --tilefile work/tiny1.tile

python file2file.py --outfile work/tiny1.jtileset --infile work/tiny1.tileset
python file2file.py --outfile work/tiny2.tileset --infile work/tiny1.jtileset
python file2file.py --outfile work/tiny2.jtileset --infile work/tiny2.tileset
python file2file.py --outfile work/tiny3.tileset --infile work/tiny1.tile
python file2file.py --outfile work/tiny3.jtileset --infile work/tiny1.tile
md5 work/tiny1.tileset work/tiny2.tileset work/tiny3.tileset work/tiny1.jtileset work/tiny2.jtileset work/tiny3.jtileset

python file2file.py --outfile work/tiny1.jtile --infile work/tiny1.tile
python file2file.py --outfile work/tiny2.tile --infile work/tiny1.jtile
python file2file.py --outfile work/tiny2.jtile --infile work/tiny2.tile
md5 work/tiny1.tile work/tiny2.tile work/tiny1.jtile work/tiny2.jtile

python file2file.py --outfile work/tiny1.jexplore --infile work/tiny1.explore
python file2file.py --outfile work/tiny2.explore --infile work/tiny1.jexplore
python file2file.py --outfile work/tiny2.jexplore --infile work/tiny2.explore
md5 work/tiny1.explore work/tiny2.explore work/tiny1.jexplore work/tiny2.jexplore


python input2tile.py --outfile work/tiny-text1.tileset --textfile levels/kenney/tiny-00.lvl levels/kenney/tiny-01.lvl levels/kenney/tiny-02.lvl --out-tileset
python input2tile.py --outfile work/tiny-text1.tile --textfile levels/kenney/tiny-00.lvl levels/kenney/tiny-01.lvl levels/kenney/tiny-02.lvl
python levels2explore.py --outfile work/tiny-text1.explore --tilefile work/tiny-text1.tile

python file2file.py --outfile work/tiny-text1.jtileset --infile work/tiny-text1.tileset
python file2file.py --outfile work/tiny-text2.tileset --infile work/tiny-text1.jtileset
python file2file.py --outfile work/tiny-text2.jtileset --infile work/tiny-text2.tileset
python file2file.py --outfile work/tiny-text3.tileset --infile work/tiny-text1.tile
python file2file.py --outfile work/tiny-text3.jtileset --infile work/tiny-text1.tile
md5 work/tiny-text1.tileset work/tiny-text2.tileset work/tiny-text3.tileset work/tiny-text1.jtileset work/tiny-text2.jtileset work/tiny-text3.jtileset

python file2file.py --outfile work/tiny-text1.jtile --infile work/tiny-text1.tile
python file2file.py --outfile work/tiny-text2.tile --infile work/tiny-text1.jtile
python file2file.py --outfile work/tiny-text2.jtile --infile work/tiny-text2.tile
md5 work/tiny-text1.tile work/tiny-text2.tile work/tiny-text1.jtile work/tiny-text2.jtile

python file2file.py --outfile work/tiny-text1.jexplore --infile work/tiny-text1.explore
python file2file.py --outfile work/tiny-text2.explore --infile work/tiny-text1.jexplore
python file2file.py --outfile work/tiny-text2.jexplore --infile work/tiny-text2.explore
md5 work/tiny-text1.explore work/tiny-text2.explore work/tiny-text1.jexplore work/tiny-text2.jexplore


python input2tile.py --outfile work/tiny-image1.tileset --imagefile levels/kenney/tiny-00.png levels/kenney/tiny-01.png levels/kenney/tiny-02.png --tilesize 18 --out-tileset
python input2tile.py --outfile work/tiny-image1.tile --imagefile levels/kenney/tiny-00.png levels/kenney/tiny-01.png levels/kenney/tiny-02.png --tilesize 18
python levels2explore.py --outfile work/tiny-image1.explore --tilefile work/tiny-image1.tile

python file2file.py --outfile work/tiny-image1.jtileset --infile work/tiny-image1.tileset
python file2file.py --outfile work/tiny-image2.tileset --infile work/tiny-image1.jtileset
python file2file.py --outfile work/tiny-image2.jtileset --infile work/tiny-image2.tileset
python file2file.py --outfile work/tiny-image3.tileset --infile work/tiny-image1.tile
python file2file.py --outfile work/tiny-image3.jtileset --infile work/tiny-image1.tile
md5 work/tiny-image1.tileset work/tiny-image2.tileset work/tiny-image3.tileset work/tiny-image1.jtileset work/tiny-image2.jtileset work/tiny-image3.jtileset

python file2file.py --outfile work/tiny-image1.jtile --infile work/tiny-image1.tile
python file2file.py --outfile work/tiny-image2.tile --infile work/tiny-image1.jtile
python file2file.py --outfile work/tiny-image2.jtile --infile work/tiny-image2.tile
md5 work/tiny-image1.tile work/tiny-image2.tile work/tiny-image1.jtile work/tiny-image2.jtile

python file2file.py --outfile work/tiny-image1.jexplore --infile work/tiny-image1.explore
python file2file.py --outfile work/tiny-image2.explore --infile work/tiny-image1.jexplore
python file2file.py --outfile work/tiny-image2.jexplore --infile work/tiny-image2.explore
md5 work/tiny-image1.explore work/tiny-image2.explore work/tiny-image1.jexplore work/tiny-image2.jexplore
