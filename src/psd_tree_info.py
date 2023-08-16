import sys
import re
import logging
from ppctree.tree.ppc_tree import PPCTree
from conv_status import ConvStatus

RE_LEAVES = re.compile(r"\(([^ ]+?) ([^ ]+?)\)")
ID_FIND = re.compile(r" \(ID ([^)]+)\)$")
ZERO_FIX = re.compile(r"\(([^ ]+?) (0)\)")
TRACE_FIX = re.compile(r"\(([^ ]+?) (\*[^)]*)\)")
RE_ILLEGAL_LEAF = re.compile(r"\([^ ]+? ?\)")

RE_CODE_LEAF = re.compile(r"\((?P<pos>[^ ]+?) \(CODE {[^ }]+?}\)\)")


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


def delete_meta_text(tree_str, meta_str, meta_info):
    """Remove (CODE/META/REF...) from tree_str

    Parameters
    ==========
    tree_str: string
        flat representation of tree
    meta_str: string
        one of CODE, METADATA, REF
    meta_info: list of string
        used for logging what metadata was removed
    """
    tree_str_sav = tree_str
    search_s = "("+meta_str
    index_next = tree_str.find(search_s)

    stuff_removed = ""
    # keep iterating until no more META_STR left
    # could be more efficient
    while index_next != -1:
        end_index = find_end_of_next_tree(tree_str, index_next)
        stuff_removed += tree_str[index_next:end_index]
        tree_str = tree_str[:index_next]+tree_str[end_index:]
        tree_str = re.sub(r" +", " ", tree_str)
        tree_str = re.sub(r" \)", ")", tree_str)
        index_next = tree_str.find(search_s)
    meta_info.append(
        f'had {meta_str}\nbefore={tree_str_sav}\t'
        f'after={tree_str}\tremoved={stuff_removed}')
    tree_str = tree_str.strip()
    return tree_str

def flatten_tree(tree_lines):
    psd_tree_flat = ' '.join([line.strip() for line in tree_lines]) + ' '
    psd_tree_flat = re.sub(r"\t", " ", psd_tree_flat)
    psd_tree_flat = re.sub(r" +", " ", psd_tree_flat)
    psd_tree_flat = psd_tree_flat.strip()
    return psd_tree_flat

def process(tree_str, keep_parens, meta_info):
    """Modifies tree_str and determines whether to use it."""
    assert (tree_str[0] == '(' and
            tree_str[-1] == ")"), \
            f'something wrong with tree {tree_str}'

    # take off surrounding parens
    tree_str = tree_str[1:-1].strip()

    # Check for tree id and remove it from tree_str
    # if a tree has no ID then it's just meta data nad ignored
    # e.g. (CODE <P_26>)
    match_id = ID_FIND.search(tree_str)
    if match_id is None:
        return (ConvStatus.NO_TREE_ID, tree_str, None)

    tree_id = match_id.group(1)
    tree_str = tree_str.replace(match_id.group(0), "")

    if tree_str.startswith("(CODE "):
        return (ConvStatus.ROOT_CODE, tree_str, tree_id)

    # for the POS tagging, we don't get rid of the META flat trees,
    # because they have POS tags that can be used.  When later preparing
    # data for for parsing, these can't be used.

    #if tree_str.startswith("(META "):
    #    self.status = ConvStatus.ROOT_META
    #    return

    if tree_str.startswith("(REF "):
        return (ConvStatus.ROOT_REF, tree_str, tree_id)

    if tree_str.find('(BREAK ') > -1:
        return (ConvStatus.HAS_BREAK, tree_str, tree_id)

    if keep_parens:
        # if dropping parens, leave as CODE and will be removed, like
        # other CODE meta data.
        # otherwise change CODE to OPAREN/CPAREN so they'll be kept when
        # CODE stuff is removed
        tree_str = tree_str.replace(
            '(CODE <paren>)', '(OPAREN -LRB-)')
        tree_str = tree_str.replace(
            '(CODE <$$paren>)', '(CPAREN -RRB-)')

    # this finds cases of (X (CODE {word})) where X is a pos or nonterminal
    # and changes it to (X 0).  If this is not done then the next step,
    # which removes CODE text, will modify this to (X ), resulting in an
    # illegal tree structure.
    tree_str = RE_CODE_LEAF.sub(r'(\g<pos> 0)', tree_str)

    for meta_str in ('CODE', 'METADATA', 'REF'):
        if f'({meta_str}' in tree_str:
            tree_str = delete_meta_text(tree_str, meta_str, meta_info)

    # Check that tree has at least one leaf
    leaves = RE_LEAVES.findall(tree_str)
    # pos here can also be a NT, if (NT 0)
    words = [word for (pos, word) in leaves
             if word != '0' and not word.startswith('*')]
    if not words:
        return (ConvStatus.TREE_EMPTY, tree_str, tree_id)

    # missing word in leaf, like (pos )
    match_bad_leaf = RE_ILLEGAL_LEAF.search(tree_str)
    if match_bad_leaf is not None:
        return (ConvStatus.BAD_LEAF, tree_str, tree_id)

    # Check that there is only one tree in tree_str.
    start_next_tree = find_end_of_next_tree(tree_str, 0)
    assert start_next_tree == len(tree_str), \
        f'more than one tree {tree_str}'

    # Add -NONE- pos for 0 and *
    tree_str = ZERO_FIX.sub(r'(\1 (-NONE- \2))', tree_str)
    tree_str = TRACE_FIX.sub(r'(\1 (-NONE- \2))', tree_str)

    # normalize OB1 and OB2
    tree_str = tree_str.replace('-OB1', '-ACC')
    tree_str = tree_str.replace('-OB2', '-DTV')

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

    # the words may have split information on them with a leading or
    # ending @.  We leave them as is here, because the next phase of processing
    # will use that info to reconstruct the original tokens.

    return (ConvStatus.OK, tree_str, tree_id)



class PsdTreeInfo:
    """Processes lines for one psd file

    Attributes
    ==========
    psd_tree: string
        exact copy of original psd tree, over multiple lines
    psd_tree_flat: string
        one_line version of psd_tree
    tree_str: string
        modified form of psd_tree that has undergone processing.
        If status is OK, used for further processing.
    status: ConvStatus or None
        if the status ends up being ConvStatus.OK, it will be used
    meta_info: list of str
        log info for meta material removed
    tree_id: string or None
        tree id taken from psd_tree
    """
    def __init__(self, tree_lines, keep_parens):
        self.psd_tree = ''.join(tree_lines)
        self.psd_tree_flat = flatten_tree(tree_lines)

        #There are some cases with the function tags split up,
        #always with -SPE at the end.  e.g.
        #IP-MAT=1-SPE
        #Since we don't care right now about SPE, just remove it and avoid
        #any complications
        self.psd_tree_flat = self.psd_tree_flat.replace('-SPE', '')

        self.meta_info = []
        res = process(self.psd_tree_flat, keep_parens, self.meta_info)
        (self.status, self.tree_str, self.tree_id) = res
