CORPUS_DIR=./data/penn-parsed-corpus-of-historical-yiddish/data
OUT_DIR=./out
mkdir $OUT_DIR
echo STEP 1
python ./src/convert_psd2mod.py --keep_parens  ${CORPUS_DIR} ${OUT_DIR}
echo STEP 2
python ./src/write_pos.py ${OUT_DIR}
echo STEP 3
python ./src/make_splits.py ${OUT_DIR}
echo STEP 4
python ./src/get_split_stats.py ${OUT_DIR}
echo STEP 5
python ./src/write_lexicon.py ${OUT_DIR}
echo STEP 6

