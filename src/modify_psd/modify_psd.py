"""Modify corpus with search/replace and regexes

Reads the PPCHY .psd files and writes files to <new_corpus_dir>/tmp/mod_psd/

It flattens the files in order to apply the changes.

Currently only 1910e-grine-felder.psd and 1947e-royte-pomerantsen.psd are
modified.
"""
import os
import re
import logging
import argparse
import pathlib
from tqdm import trange
from corpus_mods import make_changes

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name

def join_and_flatten_tree(tree_lines):
    """Flattens multi-line psd lines for one tree"""
    tree = ' '.join([line.strip() for line in tree_lines]) + ' '
    tree = re.sub(r"\t", " ", tree)
    tree = re.sub(r" +", " ", tree)
    tree = tree.strip()
    return tree

def read_file(fname):
    """Read all the trees in one .psd file.

    Assumes the trees in the input .psd file are pretty-printed
    over multiple lines, and converts them to a flat representation

    Parameters
    ==========
    fname: Path
        input psd file
    """
    all_trees = []
    tree_lines = []
    with open(fname, 'r', encoding='utf-8') as in_file:
        for line in in_file:
            line = line.rstrip('\n')
            if line.startswith("("):
                if tree_lines:
                    all_trees.append(join_and_flatten_tree(tree_lines))
                tree_lines = [line]
            elif line:
                tree_lines.append(line)
    if tree_lines:
        all_trees.append(join_and_flatten_tree(tree_lines))
    return all_trees


def main():
    """main loop"""
    parser = argparse.ArgumentParser(
        description='Convert .psd files to form for futher processing.',
        add_help=True)
    parser.add_argument('corpus_dir', type=pathlib.Path, help='corpus psd directory')
    parser.add_argument('new_corpus_dir', type=pathlib.Path, help='output root directory')

    args = parser.parse_args()

    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
                        level=logging.INFO)

    fnames = list(args.corpus_dir.glob('./*.psd'))

    os.makedirs(args.new_corpus_dir / 'tmp' / 'mod_psd', exist_ok=True)

    for fnum in trange(len(fnames)):
        fname = fnames[fnum]
        # changes only apply to 1910e-grine-felder.psd and
        # 1947e-royte-pomerantsen.psd
        trees = read_file(fname)
        if fname.stem.startswith('1910') or fname.stem.startswith('1947'):
            trees = [make_changes(tree) for tree in trees]
        with open(args.new_corpus_dir / 'tmp' / 'mod_psd' / fname.name, 'w', encoding='utf-8') as fout:
            fout.write('\n'.join(trees) + '\n')

if __name__ == '__main__':
    main()
