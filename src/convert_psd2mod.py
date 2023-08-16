"""First step in processing the PPCHY

For each FILE.psd in the PPCHY, this will output a nuber of files to
subdirectories under <root_dir>/mod, where <root_dir> is a command-line
argument.  Most of this is debugging info of various sorts, but the
<root_dir>/mod/trees and ids directories are used for later processing.
"""
import os
import logging
import argparse
import pathlib
from tqdm import trange

from conv_status import ConvStatus
from psd_tree_info import PsdTreeInfo

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name

def read_fixes(fname):
    """Reads changes to make to the corpus words"""
    with open(fname, 'r', encoding='utf-8') as fin:
        lines = fin.readlines()
    lines = [line.rstrip('\n') for line in lines]
    lines = [line for line in lines
             if line and line[0] != ';']
    lines = [line.split('\t') for line in lines]
    changes = [
        (f'({pos} {old})', f'({pos} {new})')
        for (pos, old, new) in lines]
    return changes

def fix_tree(tree_lines, changes):
    """Apply modifications to each line of the tree

    Inefficient, but for now keeping tree as a list of lines
    """
    for (from_, to_) in changes:
        tree_lines = [line.replace(from_, to_)
                      for line in tree_lines]
    return tree_lines

def read_file(fname, keep_parens, changes):
    """Convert all the trees in one .psd file.

    Assumes the trees in the input .psd file are pretty-printed
    over multiple lines, so collects each one for further processing.

    Parameters
    ==========
    fname: Path
        input psd file
    keep_parens: boolean
        True if parens should be kept in trees
    changes_use: None list of (str, str)
        Each element in list is (pos word), (pos word) used for replacement
    """
    all_trees = []
    tree_lines = []
    with open(fname, 'r', encoding='utf-8') as in_file:
        for line in in_file:
            if line.startswith("("):
                if tree_lines:
                    if changes:
                        tree_lines = fix_tree(tree_lines, changes)
                    all_trees.append(PsdTreeInfo(tree_lines, keep_parens))
                tree_lines = [line]
            else:
                tree_lines.append(line)
    if tree_lines:
        if changes:
            tree_lines = fix_tree(tree_lines, changes)
        all_trees.append(PsdTreeInfo(tree_lines, keep_parens))

    return all_trees

def write_file(fname, root_dir, trees, meta_lst, ids_not_used_lst):
    """Write the trees for one .psd file

    Parameters
    ==========
    fname: Path
        input psd file
    root_dir: Path
        root directory of various output subdirectories
    meta_lst: list str
        used for accumulating meta info over all files
    ids_not_used_lst: list (str, str, str)
        (tree_id, status, tree_flat)
        used for accumulating info on trees not used over all files
    """
    stem = fname.stem
    with open(root_dir / 'mod' / 'log' / (stem + '.txt'),
              'w', encoding='utf-8') as out_log_file, \
         open(root_dir / 'mod' / 'psd' / (stem + '.psd'),
              'w', encoding='utf-8') as out_psd_file, \
         open(root_dir / 'mod' / 'trees' / (stem + '.txt'),
              'w', encoding='utf-8') as out_trees_file, \
         open(root_dir / 'mod' / 'ids' / (stem + '.txt'),
              'w', encoding='utf-8') as out_ids_file:

        for (num, tinfo) in enumerate(trees):
            meta_lst.extend(tinfo.meta_info)
            out_log_file.write(f'{num}\t{tinfo.status.name}\t'
                               f'orig_tree_str={tinfo.psd_tree_flat}\t'
                               f'tree_str={tinfo.tree_str}\n')
            if tinfo.status == ConvStatus.OK:
                out_trees_file.write(f'{tinfo.tree_str}\n')
                out_ids_file.write(f'{tinfo.tree_id}\n')
                out_psd_file.write(f'{tinfo.psd_tree}')
            elif tinfo.status != ConvStatus.NO_TREE_ID:
                ids_not_used_lst.append((tinfo.tree_id, tinfo.status.name,
                                         tinfo.psd_tree_flat))

def main():
    """main loop"""
    parser = argparse.ArgumentParser(
        description='Convert .psd files to form for futher processing.',
        add_help=True)
    parser.add_argument('in_dir', type=pathlib.Path, help='corpus psd directory')
    parser.add_argument('root_dir', type=pathlib.Path, help='output root directory')
    parser.add_argument('--keep_parens', action='store_true',
                        help="include paren elements in output tree")

    args = parser.parse_args()

    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
                        level=logging.INFO)

    keep_parens = args.keep_parens

    os.makedirs(args.root_dir / 'mod' / 'misc', exist_ok=True)
    os.makedirs(args.root_dir / 'mod' / 'trees', exist_ok=True)
    os.makedirs(args.root_dir / 'mod' / 'ids', exist_ok=True)
    os.makedirs(args.root_dir / 'mod' / 'psd', exist_ok=True)
    os.makedirs(args.root_dir / 'mod' / 'log', exist_ok=True)

    changes = read_fixes('./src/corpus-changes.txt')

    fnames = list(args.in_dir.glob('./*.psd'))

    meta_lst = []
    ids_not_used_lst = []
    for fnum in trange(len(fnames)):
        fname = fnames[fnum]
        # changes only apply to 1910e-grine-felder.psd and
        # 1947e-royte-pomerantsen.psd
        if fname.stem.startswith('1910') or fname.stem.startswith('1947'):
            changes_use = changes
        else:
            changes_use = None
        trees = read_file(
            fname, keep_parens, changes_use)
        write_file(
            fname, args.root_dir, trees, meta_lst, ids_not_used_lst)

    with open(args.root_dir / 'mod' / 'misc' / 'meta_info.txt',
              'w', encoding='utf-8') as fout:
        for one in meta_lst:
            fout.write(one + '\n')

    with open(args.root_dir / 'mod' / 'misc' / 'ids_not_used.txt',
              'w', encoding='utf-8') as fout:
        for (tree_id, status_str, tree_flat) in ids_not_used_lst:
            fout.write(f'{tree_id}\t{status_str}\t'
                       f'{tree_flat}\n')

if __name__ == '__main__':
    main()
