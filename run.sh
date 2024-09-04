CORPUS_DIR=./data/penn-parsed-corpus-of-historical-yiddish/data
NEW_CORPUS_DIR=./out

python ./src/modify_psd/modify_psd.py ${CORPUS_DIR} ${NEW_CORPUS_DIR}
python ./src/prep_psd/prep_psd.py ${NEW_CORPUS_DIR}
python ./src/mod_leaves/make_json.py ${NEW_CORPUS_DIR}
python ./src/write_files/write_pos.py ${NEW_CORPUS_DIR}
python ./src/write_files/write_flat_trees.py ${NEW_CORPUS_DIR}
./src/write_files/pp_psd.sh ${NEW_CORPUS_DIR}
python ./src/write_files/write_pos_word_counts.py ${NEW_CORPUS_DIR}
python ./src/write_files/count_chars.py ${NEW_CORPUS_DIR}
