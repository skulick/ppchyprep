from rom2uni.convert_rom2uni import convert
from split_word.split_word import split_word

def add_rom_field(leaves):
    """set the rom(anization) for each leaf

    rom is just the text as it is in the treebank, except for parens
    and exclamation. This is then used by merge_leaves, which combines the
    rom fields to make new leaves
    """
    for leaf in leaves:
        rom = leaf.text
        assert rom != '', 'empty leaf'

        if rom == '-LRB-':
            rom = '('
        elif rom == '-RRB-':
            rom = ')'
        elif rom == '%EXCL%':
            rom = '!'
        leaf.rom = rom

def make_yiddish_script_forms(leaves, translit, do_yiddish_script_split):
    """Convert romanization to Yiddish script for all leaves
    Parameters
    ==========
    leaves: list of YidLeaf
        all the nonempty terminals of the tree
    translit: Transliterator
        for converting yiddish script to ycode
    """
    for leaf in leaves:
        assert '~' not in leaf.rom, 'has ~'
        leaf.yid = convert(leaf.rom, leaf.pos)
        leaf.ycode = translit.yiddish2ycode(leaf.yid)

        expected_num_children = len(leaf.pos.split('~'))
        # if ~, then result from split is list of one
        assert ((expected_num_children == 1 and not leaf.children) or
                (expected_num_children > 1 and len(leaf.children))), \
                f'inconsistency {leaf.pos} {leaf.rom} expected={expected_num_children} #children={len(leaf.children)}'

        if leaf.children:
            for child in leaf.children:
                assert '~' not in child.rom, 'has ~'
            if not do_yiddish_script_split:
                for child in leaf.children:
                    child.yid = convert(child.rom, child.pos)
                    child.ycode = translit.yiddish2ycode(child.yid)
            else:
                split_parts = split_word(leaf.pos, leaf.yid)
                assert split_parts is not None, \
                    f'not split {leaf.pos} {leaf.yid}'
                assert len(split_parts) == len(leaf.children), \
                    ("diff in # split parts\n"
                     f"{leaf.pos} {leaf.yid}\n"
                     f"{' '.join(split_parts)}\n"
                     f"{' '.join([child.rom for child in leaf.children])}")
                #yid2_parts = [convert(child.rom, child.pos)
                #              for child in leaf.children]
                #if split_parts != yid2_parts:
                #    split_parts_str = ' '.join([translit.yiddish2ycode(one) for one in split_parts])
                #    yid2_parts_str = ' '.join([translit.yiddish2ycode(one) for one in yid2_parts])
                #    print(f'diff in split_parts\t{leaf.pos}\t{leaf.rom}\t{split_parts_str}\t{yid2_parts_str}')
                for (split_part, child) in zip(split_parts, leaf.children):
                    child.yid = split_part
                    child.ycode = translit.yiddish2ycode(child.yid)



def put_rom_leaves_back_into_tree(ppc_tree, leaves_dict_lst):
    tree_leaves = ppc_tree.nonempty_leaf_nodes
    assert None not in tree_leaves, 'empty tree_leaf'

    # get the leaves that are part of the tree - i.e.,
    # not the merged leaves
    leaves = [leaf for leaf in leaves_dict_lst
              if leaf['ltype'] in ('t', 'st')]

    assert len(tree_leaves) == len(leaves), \
        f'#tree_leaves {len(tree_leaves)} but #leaves {len(leaves)}'

    for (tree_leaf, leaf) in zip(tree_leaves, leaves):
        text = leaf['rom']
        #text = leaf['yid']
        if text == '(':
            text = '-LRB-'
        elif text == ')':
            text = '-RRB-'
        tree_leaf.text = text

        # for the version of the tree written out now, which is meant to have
        # all the information present in the original trees, we include
        # the occasional extra tag info.  This info is already in tree_leaf
        # because it's set in yid_leaf, so there is no need to put it in from
        # the stored leaf info.
        # Later on, when makign the Yiddish script version for parser training,
        # we'll remove the pos_extra since we're not dealing with function tags
        # at the pos level now.
        #
        # However, we never want the gloss in the tree, since it's now part of the
        # pos listing, so we zap it from the tree leaf.
        tree_leaf.gloss = None
    return ppc_tree.mystr()

def make_tree_with_yiddish_script_leaves(ppc_tree, leaves_dict_lst):
    tree_leaves = ppc_tree.nonempty_leaf_nodes
    assert None not in tree_leaves, 'empty tree_leaf'

    # get the leaves that are part of the tree - i.e.,
    # not the merged leaves
    leaves = [leaf for leaf in leaves_dict_lst
              if leaf['ltype'] in ('t', 'st')]

    assert len(tree_leaves) == len(leaves), \
        f'#tree_leaves {len(tree_leaves)} but #leaves {len(leaves)}'

    for (tree_leaf, leaf) in zip(tree_leaves, leaves):
        text = leaf['yid']
        if text == '(':
            text = '-LRB-'
        elif text == ')':
            text = '-RRB-'
        tree_leaf.text = text

        # in case the pos was cleaned up (index removed, etc.)
        # use the cleaned up version for the tree so that it matches
        # what's in the pos list
        tree_leaf.pos = leaf['pos']
        # don't want gloss in the tree for parser
        tree_leaf.gloss = None



    return ppc_tree.mystr()
