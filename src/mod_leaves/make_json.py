"""Merge leaves and convert to Yiddish script, write final json.
For each
<new_corpus_dir>/ 'tmp' / 'prep_psd' / FILE.txt, writes
<new_corpus_dir>/ 'data' / 'json' / FILE.json

The .json is a list of dicts for each tree, where each dict has:
'tree_id': the tree_id or notreeid
'tree': the tree as a string, with the romanized leaves. This has all the info
from the original tree, as modified by by prep_psd.
'leaves': a listing of all the leaves for the tree, with both the romanized
and Yiddish script forms
"""
import os
import logging
import argparse
import pathlib
import copy
import json
from tqdm import trange
from ppctree.tree.ppc_tree import PPCTree
from yiddishycode.translit import Transliterator
from yid_leaf import YidLeaf
from transform_trees_merge import merge_leaves
from make_json_utils import (add_rom_field,
                             make_yiddish_script_forms,
                             put_rom_leaves_back_into_tree)

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name

def make_leaves_dict_lst(yid_leaves):
    """Make list of leaf info

    Takes the list of YidLeaf objects and converts each one into
    a dict, and returns a list of the dicts. Some of the leaves
    have children leaves, since they were merged from split tokens.
    The ltype indicates whether the leaf is a ("s")ource token
    (a token resulting from merging two tree tokens), a ("t") token,
    (a token that was merged to form a source token), or ("st"), both
    a source and tree token - i.e. a tree token that did not need to be
    merged. Only "s" tokens have an end key.
    """
    def make_tree_leaf_dict(leaf, ltype):
        one_dict = {
            'start': leaf.start,
            'rom': leaf.rom,
            'pos': leaf.pos,
            'yid': leaf.yid,
            'ycode': leaf.ycode,
            'ltype': ltype
        }
        if leaf.gloss is not None:
            one_dict['gloss'] = leaf.gloss
        if leaf.pos_extra is not None:
            one_dict['pos_extra'] = leaf.pos_extra
        if leaf.split_before:
            one_dict['split_before'] = True
        if leaf.split_after:
            one_dict['split_after'] = True
        return one_dict

    lst = []
    for leaf in yid_leaves:
        if leaf.children:
            one_dict = {
                'start': leaf.children[0].start,
                'end': leaf.children[-1].end-1,
                'rom': leaf.rom,
                'pos': leaf.pos,
                'yid': leaf.yid,
                'ycode': leaf.ycode,
                'ltype': 's'
            }
            # a combined word will never have a gloss, but possible could have
            # have extra tag info, although I don't think that happens
            if leaf.pos_extra is not None:
                one_dict['pos_extra'] = leaf.pos_extra
            if leaf.split_before:
                one_dict['split_before'] = True
            if leaf.split_after:
                one_dict['split_after'] = True

            lst.append(one_dict)
            for child in leaf.children:
                lst.append(make_tree_leaf_dict(child, 't'))
        else:
            lst.append(make_tree_leaf_dict(leaf, 'st'))
    return lst


def process_file(lines, translit, do_yiddish_script_split):
    """Convert the json info for one file.

    for each tree that has an id:
    (1) convert tree representation to PPCTree
    (2) get leaves
    (3) Adds a rom field to each leaf - same as the text except for
    parens and the exclamation mark. The glosses for the Hebrew words
    had aready been removed (and put into a gloss field for each
    leaf) by the reading in of the tree.
    (4) Does the merging of the leaves
    (5) Each leaf, both the merged ones and original ones, have
    a rom field for the romanization.  Use these to add a  yid and
    ycode value to each one
    (6) Convert the leaf info into a list of dicts that will be used
    for storing int he json file, and making the trees with the
    Yiddish script forms.
    (7) Substitute the leaves back into the trees with the rom form.
    This reconverts the parens to -LRB- and -RRB-.
    This step could be done with the Yiddish script form of the leaves,
    which is what is done elsewhere to prepare the trees for training.
    (8) Store the info for one tree - the tree_id, tree, and a list of the
    leaves into a dict for the new json.

    If the tree has no tree_id, then it doesn't need any processing,
    and a dict is returned with an empty list for the leaves.

    Parameters
    =========
    lines: list of pairs
       Each pair (tree_id, tree)  where tree_id can be 'notreeid'
    translit: Transliterator
        for converting yiddish script to ycode
    do_yiddish_script_split: boolean
        if true, then processing 1910 or 1947, and in addition to
        merging the leaves, will resplit the merged Yiddish script, in order
        to get the proper Yiddish script for each of the leaves as used
        in the tree.  For example, "oyf" and "n" are merged to form
        the original source token "oyfn", and the Yiddish script version
        has the non-final form of "f", but if "oyf" and "n" are converted
        to Yiddish script separatel, then "oyf" will have the incorrect final
        form of "f".  For now only worrying about this for 1910 and 1947.
    """
    info = []
    for (tree_id, tree_str) in lines:
        if tree_id == 'notreeid':
            out_dict = {
                'tree_id': tree_id,
                'tree': tree_str,
                'leaves': []
            }
            info.append(out_dict)
            continue

        # (1)
        ppc_tree = PPCTree(tree_str, term_class=YidLeaf)
        mystr = ppc_tree.mystr()
        # just a check that conversion back from tree is the same
        assert mystr == tree_str, \
            f'weirdness with tree conversion\ntree_str={tree_str}\nppc_tree={mystr}'

        # (2)
        yid_leaves_orig = ppc_tree.nonempty_leaf_nodes
        # The merge_leaves function following is a destructive operation
        # on the list of leaves. This will modify the ppc_tree which
        # is also used below to put the leaves back in
        # So the leaf operations is done on a copy.
        yid_leaves = copy.deepcopy(yid_leaves_orig)

        # (3)
        add_rom_field(yid_leaves)

        # (4)
        # do the actual merging. New list of yid_leaves, in which some
        # leaves now have children (i.e. the original leaves that were meged
        # are now children of a new leaf).
        yid_leaves = merge_leaves(yid_leaves)

        # (5)
        # get actual yiddish script.  leaves will now have a
        # .yid and .ycode field
        make_yiddish_script_forms(yid_leaves, translit, do_yiddish_script_split)

        # (6)
        leaves_dict_lst = make_leaves_dict_lst(yid_leaves)

        # (7)
        tree = put_rom_leaves_back_into_tree(ppc_tree, leaves_dict_lst)

        # (8)
        out_dict = {
            'tree_id': tree_id,
            'tree': tree,
            'leaves': leaves_dict_lst
            }
        info.append(out_dict)
    return info



def main():
    """main loop"""
    parser = argparse.ArgumentParser(
        description='Convert .psd files to form for futher processing.',
        add_help=True)
    parser.add_argument('new_corpus_dir', type=pathlib.Path, help='new corpus')

    args = parser.parse_args()

    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
                        level=logging.INFO)

    tmp2_dir = args.new_corpus_dir / 'tmp' / 'prep_psd'
    json_dir = args.new_corpus_dir / 'data' / 'json'

    os.makedirs(json_dir, exist_ok=True)

    translit = Transliterator()

    fnames = list(tmp2_dir.glob('./*.txt'))

    for fnum in trange(len(fnames)):
        fname = fnames[fnum]
        with open(fname, 'r', encoding='utf-8') as fin:
            lines = fin.readlines()
        lines = [line.rstrip('\n').split('\t') for line in lines]

        do_yiddish_script_split = fname.stem.startswith('1910') or fname.stem.startswith('1947')
        info = process_file(lines, translit, do_yiddish_script_split)
        with open(json_dir / f'{fname.stem}.json',
                  'w', encoding='utf-8') as fout:
            json.dump(info, fout, sort_keys=True,
                      indent=4, ensure_ascii=False)

if __name__ == '__main__':
    main()
