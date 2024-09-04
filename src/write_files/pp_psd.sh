#!/bin/bash
NEW_CORPUS_DIR=$1

THIS="$(dirname ${BASH_SOURCE[0]})"
java -classpath $THIS/CS_2.003.04.jar csearch/CorpusSearch $THIS/reformat.c $NEW_CORPUS_DIR/data/psd_flat/*.psd

# CorpusSearch writes .psd.fmt files in psd_tmp directory
# get rid of .fmt extension and move them to psd directory
mkdir -p $NEW_CORPUS_DIR/data/psd
for fname in $NEW_CORPUS_DIR/data/psd_flat/*.fmt ; do
    psdname=`basename $fname .fmt`
    mv $fname $NEW_CORPUS_DIR/data/psd/$psdname
done

	     
