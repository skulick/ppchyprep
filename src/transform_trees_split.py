"""Code for splitting leaves that had been joined together in the treebank

    Splits the colon from names, and also the hyphen in names.
    This won't be needed for  turning it into proper training data, since the
    name/colon is only part of the metadata, which will be eliminated for the
    training data (probably).  But it's used now to make it easier to align the files
    and check everything
"""
from yid_leaf import YidLeaf

def split_leaves(leaves):
    """Split leaves"""
    leaves = split_colon(leaves)
    leaves = split_names(leaves)
    leaves = split_underscore(leaves)
    return leaves

def split_colon(leaves):
    """Split names with a colon at the end

    These only occur as part of the META info.  Eventually with parsing
    we won't be concerned with these since they won't be part of the
    trees, but for now with the alignment we're including all the META stuff
    and the alignment will be improved if the colon is separated.
    """
    while True:
        ones = [(num, leaf) for (num, leaf) in enumerate(leaves)
                if leaf.text[-1] == ':' and leaf.pos == 'NPR']
        if not ones:
            return leaves
        (npr_x, npr_leaf) = ones[0]
        npr_leaf.text = npr_leaf.text[:-1]
        colon_leaf = YidLeaf('PUNC', ':')
        #colon_leaf.text = ':'
        #colon_leaf.pos = 'PUNC'
        #colon_leaf.gloss = ''
        new_leaves = leaves[:npr_x] + [npr_leaf] + [colon_leaf] + leaves[npr_x+1:]
        leaves = new_leaves

def split_names(leaves):
    """Split names with a hyphen in the middle

    Eventually we won't do this, since the names should just be left as they
    are, but with the alignment it helps temporarily to split them out
    """
    while True:
        # text[1:-1] is in case the word has a hyphen at beginning or end
        ones = [(num, leaf) for (num, leaf) in enumerate(leaves)
                if '-' in leaf.text[:-1] and leaf.pos in ('NPR', 'NPR$')]
        if not ones:
            return leaves
        (npr_x, npr_leaf) = ones[0]
        parts = npr_leaf.text.split('-')
        # filter out spurious split if hyphen was at edge
        parts = [part for part in parts
                 if part]
        old_pos = npr_leaf.pos


        npr_leaves = []
        for text in parts:
            npr_leaf = YidLeaf('NPR', text)
            #npr_leaf.text = text
            #npr_leaf.pos = 'NPR'
            #npr_leaf.gloss = ''
            npr_leaves.append(npr_leaf)
        # restore last leaf to NPR or NPR$
        npr_leaves[-1].pos = old_pos
        new_leaves = leaves[:npr_x] + npr_leaves + leaves[npr_x+1:]
        leaves = new_leaves

def split_underscore(leaves):
    """Split words that were joined together in the treebank
    e.g. gor_nit, gor_nisht, vos_zhe, say_vi, a_mol
    """
    while True:
        ones = [(num, leaf) for (num, leaf) in enumerate(leaves)
                if '_' in leaf.text]
        if not ones:
            return leaves

        (one_x, one) = ones[0]
        parts = one.text.split('_')
        pos = one.pos
        gloss = one.gloss

        new_split_leaves = []
        for (num, text) in enumerate(parts):
            new_leaf = YidLeaf(f'{pos}_S{num}', text)
            new_split_leaves.append(new_leaf)
        # just add gloss to first one
        new_split_leaves[0].gloss = gloss

        new_leaves = leaves[:one_x] + new_split_leaves + leaves[one_x+1:]
        leaves = new_leaves
