"""Utility functions for prep_psd.py"""
import sys
import re
import logging
from collections import namedtuple
from ppctree.tree.ppc_tree import PPCTree

PsdInfo = namedtuple(
    'PsdInfo', 'tree_id tree_str')

RE_LEAVES = re.compile(r"\(([^ ]+?) ([^ ]+?)\)")
ID_FIND = re.compile(r" \(ID ([^)]+)\)$")
ZERO_FIX = re.compile(r"\(([^ ]+?) (0)\)")
TRACE_FIX = re.compile(r"\(([^ ]+?) (\*[^)]*)\)")
CODE_FIX = re.compile(r"\(CODE (?P<code>[^ ]+?)\)")
RE_ILLEGAL_LEAF = re.compile(r"\([^ ]+? ?\)")

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name

def find_end_of_next_tree(tree, current_index):
    """Find string from starting paren to matching closing paren."""
    while tree[current_index] == " " and current_index < len(tree):
        current_index += 1
    if tree[current_index] != "(":
        print("expected open paren " + str(current_index) + " START"+tree[current_index]+"END")
        sys.exit(-1)
    count_open = 1
    count_closed = 0
    current_index += 1
    while count_open != count_closed:
        char = tree[current_index]
        #print "char="+char+" open="+str(count_open)+" closed="+str(count_closed)
        if char == "(":
            count_open += 1
        elif char == ")":
            count_closed += 1
        current_index += 1
    return current_index



def process(tree_str):
    """Modifies tree_str and determines whether to use it."""
    #There are some cases with the function tags split up,
    #always with -SPE at the end.  e.g.
    #IP-MAT=1-SPE
    #Since we don't care right now about SPE, just remove it and avoid
    #any complications
    #tree_str = tree_str.replace('-SPE', '')


    assert (tree_str[0] == '(' and
            tree_str[-1] == ")"), \
            f'something wrong with tree {tree_str}'

    # take off surrounding parens
    tree_str = tree_str[1:-1].strip()

    # Check for tree id and remove it from tree_str
    # if a tree has no ID then it's just meta data and ignored
    # e.g. (CODE <P_26>)
    match_id = ID_FIND.search(tree_str)
    if match_id is None:
        return PsdInfo('notreeid', tree_str)

    tree_id = match_id.group(1)
    tree_str = tree_str.replace(match_id.group(0), "")

    # change CODE for parens to OPAREN/CPAREN so they'll be kept when
    # CODE stuff is modified below
    tree_str = tree_str.replace(
        '(CODE <paren>)', '(OPAREN -LRB-)')
    tree_str = tree_str.replace(
        '(CODE <$$paren>)', '(CPAREN -RRB-)')

    # Check that tree has at least one leaf
    leaves = RE_LEAVES.findall(tree_str)

    # pos here can also be a NT, if (NT 0)
    words = [word for (pos, word) in leaves
             if word != '0' and not word.startswith('*')]
    assert words, 'no words'

    # missing word in leaf, like (pos )
    match_bad_leaf = RE_ILLEGAL_LEAF.search(tree_str)
    assert match_bad_leaf is None, 'bad leaf'

    # Check that there is only one tree in tree_str.
    start_next_tree = find_end_of_next_tree(tree_str, 0)
    assert start_next_tree == len(tree_str), \
        f'more than one tree {tree_str}'

    # Add -NONE- pos for 0 and *
    # Also change (CODE {stuff}) to (CODE (-NONE {stuff}))
    # so it'll be treated as an empty leaf
    tree_str = ZERO_FIX.sub(r'(\1 (-NONE- \2))', tree_str)
    tree_str = TRACE_FIX.sub(r'(\1 (-NONE- \2))', tree_str)
    tree_str = CODE_FIX.sub(r'(CODE (-NONE- \1))', tree_str)

    fulltree = PPCTree(tree_str)
    # this is just a check of the tree conversion, to make sure that the string resulting
    # from the PPCTree object is the same as the original.
    ft_mystr = fulltree.mystr()
    if ft_mystr != tree_str:
        logger.warning("tree_str=\n%s", tree_str)
        logger.warning("ft_mystr=\n%s\n", ft_mystr)
    # number of leaves should be the same as the leaves found
    # from the string
    assert len(fulltree.all_leaf_nodes) == len(leaves), \
        '# leaves is different'

    return PsdInfo(tree_id, tree_str)
