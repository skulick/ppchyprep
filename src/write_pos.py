"""Write the POS files for training/testing"""
import os
import logging
import argparse
import pathlib
from tqdm import trange
from ppctree.tree.ppc_tree import PPCTree
from yiddishycode.translit import Transliterator
from yid_leaf import YidLeaf
from transform_trees_split import split_leaves
from transform_trees_merge import merge_leaves
from convert_to_script import convert
from sent_word import Word

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name

# Ya -> Y
PASEKH_TSVEY_YUDN = '\u05f2\u05b7'
TSVEY_YUDN = '\u05f2'

# Aa -> A
PASEKH_ALEF = '\u05d0\u05b7'
BARE_ALEF = '\u05d0'

# yi -> y
KHIREK_YUD = '\u05d9\u05b4'
YUD = '\u05d9'

def write_pos_one_file_mode1(fout, tree_lines, id_lines):
    """Write POS info for one file, without transforming the tree

    The files output by this function are not used for any further processing,
    except for getting the count of the tokens w/o the tree transformations.
    It also prints the gloss from the treebank if there is any, which the
    the mode2 function does not do.

    Paramters
    =========
    fout: file
        pos output file
    tree_lines: list string
        Each element is a flat representation of a tree
    id_lines: list string
        The corresponding tree id for each tree in tree_lines
    """
    tree_num = 0
    for (tree_line, tree_id)  in zip(tree_lines, id_lines):
        tree_str = tree_line.rstrip('\n')
        ppc_tree = PPCTree(tree_str, term_class=YidLeaf)
        mystr = ppc_tree.mystr()
        # just a check that conversion back from tree is the same
        assert mystr == tree_str, \
            f'weirdness with tree conversion\ntree_str={tree_str}\nppc_tree={ppc_tree}'

        yid_leaves = ppc_tree.nonempty_leaf_nodes
        fout.write(
            f'SENT\t{tree_num}\t{tree_id}\n')

        for (leaf_num, leaf) in enumerate(yid_leaves):
            if leaf.gloss is not None:
                fout.write(f'{leaf_num}\t{leaf.text}\t{leaf.pos}\t{leaf.gloss}\n')
            else:
                fout.write(f'{leaf_num}\t{leaf.text}\t{leaf.pos}\n')
        fout.write("\n")
        tree_num += 1


def write_pos_one_file_mode2(fout, tree_lines, id_lines, translit):
    """Write POS info for one file, after transforming the tree

    The tree transforms include the merging and splitting of leaves, as
    described in the paper.

    Paramters
    =========
    fout: file
        pos output file
    tree_lines: list string
        Each element is a flat representation of a tree
    id_lines: list string
        The corresponding tree id for each tree in tree_lines
    translit: Transliterator
        for converting yiddish script to ycode
    """
    tree_num = 0
    for (tree_line, tree_id)  in zip(tree_lines, id_lines):
        tree_str = tree_line.rstrip('\n')
        ppc_tree = PPCTree(tree_str, term_class=YidLeaf)
        mystr = ppc_tree.mystr()
        # just a check that conversion back from tree is the same
        assert mystr == tree_str, \
            f'weirdness with tree conversion\ntree_str={tree_str}\nppc_tree={ppc_tree}'

        yid_leaves = ppc_tree.nonempty_leaf_nodes
        yid_leaves = transform_tree(yid_leaves)
        # adds fields to each leaf
        make_yiddish_script_forms(yid_leaves, translit)

        fout.write(
            f'SENT\t{tree_num}\t{tree_id}\n')

        for (leaf_num, leaf) in enumerate(yid_leaves):
            # Word is just a convenience namedtuple to make sure that the
            # different columns are written and readin the same order for the rest
            # of the processing (making splits, etc.). Could also just replace with
            # YidLeaf
            word = Word(yivo=leaf.yivo,
                        pos=leaf.pos,
                        yid1=leaf.yid1,
                        yid2=leaf.yid2,
                        yid3=leaf.yid3,
                        ycode1=leaf.ycode1,
                        ycode2=leaf.ycode2,
                        ycode3=leaf.ycode3)
            fout.write(f'{leaf_num}\t{word}\n')
        fout.write("\n")

        tree_num += 1

def transform_tree(leaves):
    """Transform the tree to get training data

    Eventually this take in the entire tree and do tree transformations,
    but for now it only takes the leaves and transforms them

    Parameters
    ==========
    leaves: list of YidLeaf
        all the nonempty terminals of the tree
    """
    leaves = merge_leaves(leaves)
    leaves = split_leaves(leaves)
    return leaves

def make_yiddish_script_forms(leaves, translit):
    """Make the three different yiddish script forms of the leaves

    Could also just do this when writing the info

    Parameters
    ==========
    yid_leaves: list of YidLeaf
        all the nonempty terminals of the tree
    translit: Transliterator
        for converting yiddish script to ycode
    """
    for leaf in leaves:
        pos = leaf.pos
        yivo = leaf.text
        assert yivo != '', 'empty leaf'

        if yivo == '-LRB-':
            yivo = '('
        elif yivo == '-RRB-':
            yivo = ')'
        elif yivo == '%EXCL%':
            yivo = '!'

        leaf.yivo = yivo
        # convert to yiddish script
        leaf.yid1 = convert(yivo.replace('~', ''), pos)
        # make slightly simplified form
        leaf.yid2 = leaf.yid1.replace(PASEKH_TSVEY_YUDN, TSVEY_YUDN)
        # and more simplified
        leaf.yid3 = leaf.yid2.replace(PASEKH_ALEF, BARE_ALEF)
        leaf.yid3 = leaf.yid3.replace(KHIREK_YUD, YUD)

        # and make ycode versions
        leaf.ycode1 = translit.yiddish2ycode(leaf.yid1)
        leaf.ycode2 = translit.yiddish2ycode(leaf.yid2)
        leaf.ycode3 = translit.yiddish2ycode(leaf.yid3)

def read_file(root_dir, bname):
    """read tree and id files for one bname"""
    fname_txt = f'{bname}.txt'
    with open(root_dir / 'mod' / 'trees' / fname_txt,
              'r', encoding='utf-8') as fin:
        tree_lines = fin.readlines()

    with open(root_dir / 'mod' / 'ids' / fname_txt,
              'r', encoding='utf-8') as fin:
        id_lines = fin.readlines()

    tree_lines = [one.rstrip('\n') for one in tree_lines]
    id_lines = [one.rstrip('\n') for one in id_lines]

    assert len(tree_lines) == len(id_lines), \
        (f'# tree_lines={len(tree_lines)} but '
         f'# id_lines={len(id_lines)} '
         f'for file {bname}')
    return (tree_lines, id_lines)

def make_twofiles(root_dir, penn12):
    """Make the single file containing the two files being used now

    Reads in the 1910 and 1947 files, and writes them out to one file,
    twofiles.txt, renumbing the sentences in the second file.
    Just done for convenience right now.
    """
    with open(root_dir / penn12 / 'pos' /'1910e-grine-felder.txt',
              'r', encoding='utf-8') as fin:
        f1_lines = fin.readlines()
    f1_lines = [line.rstrip('\n') for line in f1_lines]
    num_f1_sents = len([line for line in f1_lines
                        if line.startswith('SENT')])

    with open(root_dir / penn12 / 'pos' /'1947e-royte-pomerantsen.txt',
              'r', encoding='utf-8') as fin:
        f2_lines = fin.readlines()
    f2_lines = [line.rstrip('\n') for line in f2_lines]


    with open(root_dir / penn12 / 'pos' / 'twofiles.txt',
                  'w', encoding='utf-8') as fout:
        for line in f1_lines:
            fout.write(f'{line}\n')

        for line in f2_lines:
            if line.startswith('SENT'):
                (_, tree_num_str, tree_id) = line.split('\t')
                new_tree_num = int(tree_num_str) + num_f1_sents
                fout.write(f'SENT\t{new_tree_num}\t{tree_id}\n')
            else:
                fout.write(f'{line}\n')

def main():
    """main loop"""
    parser = argparse.ArgumentParser(
        description='Convert .psd files to form for futher processing.',
        add_help=True)
    parser.add_argument('root_dir', type=pathlib.Path,  help='output root directory')

    args = parser.parse_args()

    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
                        level=logging.INFO)

    os.makedirs(args.root_dir / 'penn1' / 'pos', exist_ok=True)
    os.makedirs(args.root_dir / 'penn2' / 'pos', exist_ok=True)

    translit = Transliterator()

    trees_dir = args.root_dir / 'mod' / 'trees'
    fnames = trees_dir.glob('./*.txt')
    fnames = list(fnames)

    for fnum in trange(len(fnames)):
        fname = fnames[fnum]
        bname = fname.stem
        (tree_lines, id_lines) = read_file(args.root_dir, bname)

        with open(args.root_dir / 'penn1' / 'pos' / f'{bname}.txt',
                  'w', encoding='utf-8') as fout:
            write_pos_one_file_mode1(fout, tree_lines, id_lines)


        with open(args.root_dir / 'penn2' / 'pos' / f'{bname}.txt',
                  'w', encoding='utf-8') as fout:
            write_pos_one_file_mode2(fout, tree_lines, id_lines, translit)


    make_twofiles(args.root_dir, 'penn1')
    make_twofiles(args.root_dir, 'penn2')

if __name__ == '__main__':
    main()
