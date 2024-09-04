"""Prep flattened psd file for processing

For each
<new_corpus_dir>/ 'tmp' / 'mod_psd' / FILE.psd', writes
<new_corpus_dir>/ 'tmp' / 'prep_psd' / FILE.txt'

with two columns for each tree, the tree_id (or 'notreeid')
and a modified version of the tree ready for the lex extraction.

The tree is modified with:
(1) separates out the tree_id, if any
(2) (CODE <paren>) replaced with (OPAREN -LRB-)
    (CODE <$$paren>) replaced with  (CPAREN -RRB-)
(3) 0 and * leaves replaced with (-NONE- 0) or (-NONE- *)
(4) (CODE {...}) replaced with (-NONE- (CODE {...}))
"""
import os
import logging
import argparse
import pathlib
from tqdm import trange

from prep_psd_utils import process

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


def main():
    """main loop"""
    parser = argparse.ArgumentParser(
        description='Convert .psd files to form for futher processing.',
        add_help=True)
    parser.add_argument('new_corpus_dir', type=pathlib.Path, help='new corpus')

    args = parser.parse_args()

    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
                        level=logging.INFO)

    tmp1_dir = args.new_corpus_dir / 'tmp' / 'mod_psd'
    tmp2_dir = args.new_corpus_dir / 'tmp' / 'prep_psd'

    os.makedirs(tmp2_dir, exist_ok=True)

    fnames = list(tmp1_dir.glob('./*.psd'))

    for fnum in trange(len(fnames)):
        fname = fnames[fnum]

        with open(fname, 'r', encoding='utf-8') as fin:
            lines = fin.readlines()
        trees = [line.rstrip('\n') for line in lines]
        info_lst = [process(tree) for tree in trees]

        stem = fname.stem
        with open(tmp2_dir / f'{stem}.txt',
                  'w', encoding='utf-8') as fout:
            for info in info_lst:
                fout.write(f'{info.tree_id}\t{info.tree_str}\n')

if __name__ == '__main__':
    main()
