"""Code for merging leaves that had been split in the treebank"""
from yid_leaf import YidLeaf

def ssplit(leaf):
    """Check if leaf is start of split"""
    return (leaf.text[0] != '@' and leaf.text[-1] == '@')

def isplit(leaf):
    """Check if leaf is in middle of split"""
    return (leaf.text[0] == '@' and leaf.text[-1] == '@')

def esplit(leaf):
    """Check if leaf is end of split"""
    return (leaf.text[0] == '@' and leaf.text[-1] != '@')

def merge_leaves(leaves):
    """Combine words/tags that were split

    Eventually this will be done with tree transformations, but for now
    just modifying the leaves.
    """
    merge_leaves_marked_split(leaves)
    merge_leaves_apostrophe_pronoun_and_verb(leaves)
    merge_leaves_apostrophe_verb_and_pronoun(leaves)
    merge_leaves_apostrophe_other(leaves)
    merge_leaves_no_mark(leaves)

    leaves = [leaf for leaf in leaves
              if leaf is not None]
    return leaves

def merge_leaves_marked_split(leaves):
    """Merge leaves explicitly marked as split with @"""
    func0 = lambda leaf: (leaf.pos in ('ADV', 'RP') and ssplit(leaf))
    func1 = lambda leaf: (leaf.pos == 'TO' and isplit(leaf))
    func2 = lambda leaf: (leaf.pos == 'VB' and esplit(leaf))
    check_for_three(leaves, func0, func1, func2)

    func0 = lambda leaf: (leaf.pos == 'P' and ssplit(leaf))
    func1 = lambda leaf: (leaf.pos == 'PRO' and isplit(leaf))
    func2 = lambda leaf: (leaf.pos == 'VB' and esplit(leaf))
    check_for_three(leaves, func0, func1, func2)

    func0 = lambda leaf: (leaf.pos == 'P' and ssplit(leaf))
    func1 = lambda leaf: (leaf.pos == 'D' and isplit(leaf))
    func2 = lambda leaf: (leaf.pos == 'N' and esplit(leaf))
    check_for_three(leaves, func0, func1, func2)

    #====================================================
    # special case fixup  70.285
    # (ES s'@) + (VBF @i') should be (ES 's) (VBF i')
    # to be consistent with the other splits
    # and converted to s'i'
    #====================================================
    func0 = lambda leaf: (leaf.pos == 'ES' and leaf.text == "s'@")
    func1 = lambda leaf: (leaf.pos == 'VBF' and leaf.text == "@i'")
    func_c = lambda text0, text1: "s'i'"
    check_for_two(leaves, func0, func1, func_c)

    #====================================================
    # P +  D(n,m,em)
    # P +  D(a)
    # P +  PRO
    # P +  N
    # P +  NPR
    #====================================================
    func0 = lambda leaf: (leaf.pos == 'P' and ssplit(leaf))
    func1 = lambda leaf: (leaf.pos == 'D' and leaf.text in ('@n', '@m', '@em'))
    check_for_two(leaves, func0, func1)

    func0 = lambda leaf: (leaf.pos == 'P' and ssplit(leaf))
    func1 = lambda leaf: (leaf.pos == 'D' and leaf.text == '@a')
    check_for_two(leaves, func0, func1)

    func0 = lambda leaf: (leaf.pos == 'P' and ssplit(leaf))
    func1 = lambda leaf: (leaf.pos == 'PRO' and esplit(leaf))
    check_for_two(leaves, func0, func1)

    func0 = lambda leaf: (leaf.pos == 'P' and ssplit(leaf))
    func1 = lambda leaf: (leaf.pos == 'N' and esplit(leaf))
    check_for_two(leaves, func0, func1)

    # for-@ @pskh
    func0 = lambda leaf: (leaf.pos == 'P' and ssplit(leaf))
    func1 = lambda leaf: (leaf.pos == 'NPR' and esplit(leaf))
    check_for_two(leaves, func0, func1)

    #====================================================
    # P(far,tsu) + WPRO(vos)
    #====================================================

    func0 = lambda leaf: (leaf.pos == 'P' and leaf.text in ('far@', 'tsu@'))
    func1 = lambda leaf: (leaf.pos == 'WPRO' and leaf.text == '@vos')
    check_for_two(leaves, func0, func1)

    #====================================================
    # P-DBL + DR+P
    #====================================================
    func0 = lambda leaf: (leaf.pos == 'P-DBL' and ssplit(leaf))
    func1 = lambda leaf: (leaf.pos == 'DR+P' and esplit(leaf))
    check_for_two(leaves, func0, func1)

    #====================================================
    # D + N
    #====================================================
    func0 = lambda leaf: (leaf.pos == 'D' and ssplit(leaf))
    func1 = lambda leaf: (leaf.pos == 'N' and esplit(leaf))
    check_for_two(leaves, func0, func1)

    #====================================================
    # Q + D
    #====================================================
    func0 = lambda leaf: (leaf.pos == 'Q' and ssplit(leaf))
    func1 = lambda leaf: (leaf.pos == 'D' and esplit(leaf))
    check_for_two(leaves, func0, func1)

    #====================================================
    # (VB|RD|MD|HV|BE)F + PRO(du/tu)
    #====================================================

    func0 = lambda leaf: (leaf.pos in ('VBF', 'RDF', 'MDF', 'HVF', 'BEF') and ssplit(leaf))
    func1 = lambda leaf: (leaf.pos == 'PRO' and leaf.text in ('@du', '@tu'))
    check_for_two(leaves, func0, func1)

    #====================================================
    # RP|ADV|RP-N + VB|VBN|VAN|VAG
    #====================================================

    func0 = lambda leaf: (leaf.pos in ('RP', 'ADV', 'RP-N') and ssplit(leaf))
    func1 = lambda leaf: (leaf.pos in ('VB', 'VBN', 'VAN', 'VAG') and esplit(leaf))
    check_for_two(leaves, func0, func1)

    #====================================================
    # NEG + VAG
    #====================================================

    func0 = lambda leaf: (leaf.pos in ('NEG',) and ssplit(leaf))
    func1 = lambda leaf: (leaf.pos in ('VAG',) and esplit(leaf))
    check_for_two(leaves, func0, func1)


    #====================================================
    # RP-ADV + VB|VBN
    #====================================================

    func0 = lambda leaf: (leaf.pos == 'RP-ADV' and ssplit(leaf))
    func1 = lambda leaf: (leaf.pos in ('VB', 'VBN') and esplit(leaf))
    check_for_two(leaves, func0, func1)

    #====================================================
    # VBI(lo) + PRO (mikh, mir)
    #====================================================

    func0 = lambda leaf: (leaf.pos == 'VBI' and leaf.text == 'lo@')
    func1 = lambda leaf: (leaf.pos == 'PRO' and leaf.text in ('@mikh', '@mir'))
    check_for_two(leaves, func0, func1)

    #====================================================
    # WADV(vi) + Q(fl)
    #====================================================

    func0 = lambda leaf: (leaf.pos == 'WADV' and leaf.text == 'vi@')
    func1 = lambda leaf: (leaf.pos == 'Q' and leaf.text == '@fl')
    check_for_two(leaves, func0, func1)

    #====================================================
    # NEG(nisht,nit) + ADV(o)
    #====================================================
    func0 = lambda leaf: (leaf.pos == 'NEG' and leaf.text in ('nisht@', 'nit@'))
    func1 = lambda leaf: (leaf.pos == 'ADV' and leaf.text == '@o')
    check_for_two(leaves, func0, func1)

    #====================================================
    # C(a) + NEG(nit)
    #====================================================
    func0 = lambda leaf: (leaf.pos == 'C' and leaf.text == 'a@')
    func1 = lambda leaf: (leaf.pos == 'NEG' and leaf.text == '@nit')
    check_for_two(leaves, func0, func1)

    #====================================================
    # ADV + FP(zhe)
    # WADV + FP(zhe)
    # WPRO + FP(zhe)
    # VBI + FP(zhe)
    #====================================================
    func0 = lambda leaf: (leaf.pos == 'ADV' and ssplit(leaf))
    func1 = lambda leaf: (leaf.pos == 'FP' and leaf.text == '@zhe')
    check_for_two(leaves, func0, func1)

    func0 = lambda leaf: (leaf.pos == 'WADV' and ssplit(leaf))
    func1 = lambda leaf: (leaf.pos == 'FP' and leaf.text == '@zhe')
    check_for_two(leaves, func0, func1)

    func0 = lambda leaf: (leaf.pos == 'WPRO' and ssplit(leaf))
    func1 = lambda leaf: (leaf.pos == 'FP' and leaf.text == '@zhe')
    check_for_two(leaves, func0, func1)

    func0 = lambda leaf: (leaf.pos == 'VBI' and ssplit(leaf))
    func1 = lambda leaf: (leaf.pos == 'FP' and leaf.text == '@zhe')
    check_for_two(leaves, func0, func1)

    #====================================================
    # FP + D
    # FP + ADV
    #====================================================
    func0 = lambda leaf: (leaf.pos == 'FP' and ssplit(leaf))
    func1 = lambda leaf: (leaf.pos == 'D' and esplit(leaf))
    check_for_two(leaves, func0, func1)

    func0 = lambda leaf: (leaf.pos == 'FP' and ssplit(leaf))
    func1 = lambda leaf: (leaf.pos == 'ADV' and esplit(leaf))
    check_for_two(leaves, func0, func1)

    #====================================================
    # TO + VB
    #====================================================
    func0 = lambda leaf: (leaf.pos == 'TO' and ssplit(leaf))
    func1 = lambda leaf: (leaf.pos == 'VB' and esplit(leaf))
    check_for_two(leaves, func0, func1)



def merge_leaves_apostrophe_pronoun_and_verb(leaves):
    """Merge leaves split by apostrophe"""
    #====================================================
    # 's + verb -> s'verb
    #====================================================
    func0 = lambda leaf: (leaf.pos in ('ES', 'PRO') and leaf.text == "'s")
    func1 = lambda leaf: (leaf.pos in ('BEF', 'HVF', 'MDF', 'RDF', 'VBF', 'VLF')
                          and leaf.text.find("'") == -1)
    func_c = lambda text0, text1: f"s'{text1}"
    check_for_two(leaves, func0, func1, func_c=func_c)

    #====================================================
    # 's(N) + verb -> s'verb
    # could combine with previous
    #====================================================
    func0 = lambda leaf: (leaf.pos == 'N' and leaf.text == "'s")
    func1 = lambda leaf: (leaf.pos in ('BEF', 'HVF', 'MDF', 'RDF', 'VBF', 'VLF')
                          and leaf.text.find("'") == -1)
    func_c = lambda text0, text1: f"s'{text1}"
    check_for_two(leaves, func0, func1, func_c=func_c)


    #====================================================
    # 's + i' -> s'i' (== s'Ay')
    #====================================================
    # could be grouped under the previous
    func0 = lambda leaf: (leaf.pos in ('ES', 'PRO') and leaf.text == "'s")
    func1 = lambda leaf: (leaf.pos in ('BEF', 'VBF') and leaf.text == "i'")
    func_c = lambda text0, text1: "s'i'"
    check_for_two(leaves, func0, func1, func_c=func_c)

    #====================================================
    # 's + i' -> s'i' (== s'Ay')
    # could combine with previous but waiting for word on tb
    #====================================================
    # could be grouped under the previous
    func0 = lambda leaf: (leaf.pos == 'N' and leaf.text == "'s")
    func1 = lambda leaf: (leaf.pos in ('BEF', 'VBF') and leaf.text == "i'")
    func_c = lambda text0, text1: "s'i'"
    check_for_two(leaves, func0, func1, func_c=func_c)


    #====================================================
    # 'kh(PRO) + verb -> kh'verb
    # kh'(PRO) + verb -> kh'verb
    #====================================================
    func0 = lambda leaf: (leaf.pos == 'PRO' and leaf.text in ("'kh", "kh'"))
    func1 = lambda leaf: (leaf.pos in ('BEF', 'HVF', 'MDF', 'VBF', 'VLF')
                          and leaf.text.find("'") == -1)
    func_c = lambda text0, text1: f"kh'{text1}"
    check_for_two(leaves, func0, func1, func_c=func_c)

    #====================================================
    # m'(PRO) + 'et(RDF) -> m'et
    #====================================================
    func0 = lambda leaf: (leaf.pos == 'PRO' and leaf.text == "m'")
    func1 = lambda leaf: (leaf.pos == 'MDF' and leaf.text == "'et")
    func_c = lambda text0, text1: "m'et"
    check_for_two(leaves, func0, func1, func_c=func_c)

    #====================================================
    # PRO + 'l(MDF) -> PRO'l
    #====================================================
    func0 = lambda leaf: (leaf.pos == 'PRO' and leaf.text == 'ikh')
    func1 = lambda leaf: (leaf.pos in ('MDF',) and leaf.text == "'l")
    func_c = lambda text0, text1: "ikh'l"
    check_for_two(leaves, func0, func1, func_c=func_c)

    #====================================================
    # PRO + 't(RDF) -> PRO't
    #====================================================
    func0 = lambda leaf: (leaf.pos == 'PRO' and leaf.text in ('er', 'ir'))
    func1 = lambda leaf: (leaf.pos == 'MDF' and leaf.text == "'t")
    func_c = lambda text0, text1: f"{text0}'t"
    check_for_two(leaves, func0, func1, func_c=func_c)

    #====================================================
    # PRO + 'n(RDF) -> PRO'n
    #====================================================
    func0 = lambda leaf: (leaf.pos == 'PRO' and leaf.text == 'mir')
    func1 = lambda leaf: (leaf.pos == 'MDF' and leaf.text == "'n")
    func_c = lambda text0, text1: f"{text0}'n"
    check_for_two(leaves, func0, func1, func_c=func_c)

    #====================================================
    # PRO + 'st(RDF) -> PRO'st
    #====================================================
    func0 = lambda leaf: (leaf.pos == 'PRO' and leaf.text == 'du')
    func1 = lambda leaf: (leaf.pos == 'MDF' and leaf.text == "'st")
    func_c = lambda text0, text1: f"{text0}'st"
    check_for_two(leaves, func0, func1, func_c=func_c)

def merge_leaves_apostrophe_verb_and_pronoun(leaves):
    """Merge leaves split by apostrophe"""
    #====================================================
    # 'st(RDF) + PRO(du) -> 'stu
    #====================================================
    func0 = lambda leaf: (leaf.pos == 'MDF' and leaf.text == "'st")
    func1 = lambda leaf: (leaf.pos == 'PRO' and leaf.text == 'du')
    func_c = lambda text0, text1: "'stu"
    check_for_two(leaves, func0, func1, func_c=func_c)

    #====================================================
    # 't(RDF) + PRO -> t'PRO
    #====================================================
    func0 = lambda leaf: (leaf.pos in ('HVF', 'MDF') and leaf.text == "'t")
    func1 = lambda leaf: (leaf.pos == 'PRO' and leaf.text in ("er", "ir", "men"))
    func_c = lambda text0, text1: f"t'{text1}"
    check_for_two(leaves, func0, func1, func_c=func_c)

def merge_leaves_apostrophe_other(leaves):
    """Merge leaves split by apostrophe"""
    #====================================================
    # 't(RDF) + ADJ -> t'ADJ
    #====================================================
    func0 = lambda leaf: (leaf.pos == 'MDF' and leaf.text == "'t")
    func1 = lambda leaf: (leaf.pos == 'ADJ' and leaf.text.find("'") == -1)
    func_c = lambda text0, text1: f"t'{text1}"
    check_for_two(leaves, func0, func1, func_c=func_c)

    #====================================================
    # 't(RDF) + VB -> t'VB
    #====================================================
    func0 = lambda leaf: (leaf.pos == 'MDF' and leaf.text == "'t")
    func1 = lambda leaf: (leaf.pos == 'VB' and leaf.text.find("'") == -1)
    func_c = lambda text0, text1: f"t'{text1}"
    check_for_two(leaves, func0, func1, func_c=func_c)

    #====================================================
    # 't(RDF) + NEG(nit) -> t'NEG
    #====================================================
    func0 = lambda leaf: (leaf.pos == 'MDF' and leaf.text == "'t")
    func1 = lambda leaf: (leaf.pos == 'NEG' and leaf.text == 'nit')
    func_c = lambda text0, text1: f"t'{text1}"
    check_for_two(leaves, func0, func1, func_c=func_c)

    #====================================================
    # WADV + 'l(MDF) -> vu'l
    #====================================================
    func0 = lambda leaf: (leaf.pos == 'WADV' and leaf.text.find("'") == -1)
    func1 = lambda leaf: (leaf.pos == 'MDF' and leaf.text == "'l")
    func_c = lambda text0, text1: f"{text0}'l"
    check_for_two(leaves, func0, func1, func_c=func_c)

    #====================================================
    # 's(D) + N -> s'N
    #====================================================
    func0 = lambda leaf: (leaf.pos == 'D' and leaf.text == "'s")
    func1 = lambda leaf: (leaf.pos == 'N' and leaf.text.find("'") == -1)
    func_c = lambda text0, text1: f"s'{text1}"
    check_for_two(leaves, func0, func1, func_c=func_c)

    #====================================================
    # WPRO + 'tu(PRO) -> WPRO'tu
    #====================================================
    func0 = lambda leaf: (leaf.pos == 'WPRO' and leaf.text == "vos")
    func1 = lambda leaf: (leaf.pos == "PRO" and leaf.text == "'tu")
    func_c = lambda text0, text1: f"{text0}'tu"
    check_for_two(leaves, func0, func1, func_c=func_c)

def merge_leaves_no_mark(leaves):
    """merge special case without any overt mark of split"""
    #====================================================
    # (VB|RD|MD|HV|BE)F + PRO(du/tu)
    #====================================================

    func0 = lambda leaf: (leaf.pos in ('VBF', 'RDF', 'MDF', 'HVF', 'BEF')
                          and leaf.text.endswith('st'))
    func1 = lambda leaf: (leaf.pos == 'PRO' and leaf.text == 'du')
    func_c = lambda text0, text1: f"{text0}u"
    check_for_two(leaves, func0, func1, func_c=func_c)

def check_for_two(leaves, func0, func1, func_c=None):
    """Find cases of two leaves to merge and merge them"""
    num = 0
    while num < len(leaves) - 1:
        leaf0 = leaves[num]
        leaf1 = leaves[num+1]
        if leaf0 is None or leaf1 is None:
            num += 1
        elif func0(leaf0) and func1(leaf1):
            leaves[num] = combine_two(leaves[num], leaves[num+1], func_c)
            leaves[num+1] = None
            num += 2
        else:
            num += 1

def check_for_three(leaves, func0, func1, func2):
    """Find cases of three leaves to merge and merge them"""
    num = 0
    while num < len(leaves) - 2:
        leaf0 = leaves[num]
        leaf1 = leaves[num+1]
        leaf2 = leaves[num+2]
        if leaf0 is None or leaf1 is None or leaf2 is None:
            num += 1
        elif func0(leaf0) and func1(leaf1) and func2(leaf2):
            leaves[num] = combine_three(leaf0, leaf1, leaf2)
            leaves[num+1] = None
            leaves[num+2] = None
            num += 2
        else:
            num += 1


def combine_two(leaf0, leaf1, func_c):
    """Combine two leaves"""
    if func_c is None:
        text = f'{leaf0.text}~{leaf1.text}'
        text = text.replace('@', '')
    else:
        text = func_c(leaf0.text, leaf1.text)
    pos = f'{leaf0.pos}~{leaf1.pos}'
    gloss = f'{leaf0.gloss}~{leaf1.gloss}'
    gloss = gloss.strip('~')
    leaf = YidLeaf(pos, f'{text}^{gloss}')
    return leaf

def combine_three(leaf0, leaf1, leaf2):
    """Combine three leaves"""
    text = f'{leaf0.text}~{leaf1.text}~{leaf2.text}'
    text = text.replace('@', '')
    pos = f'{leaf0.pos}~{leaf1.pos}~{leaf2.pos}'
    gloss = f'{leaf0.gloss}~{leaf1.gloss}~{leaf2.gloss}'
    gloss = gloss.strip('~')
    leaf = YidLeaf(pos, f'{text}^{gloss}')
    return leaf

# def combine_two(leaf0, leaf1, func_c):
#     """Combine two leaves"""
#     if func_c is None:
#         text = f'{leaf0.text}~{leaf1.text}'
#         text = text.replace('@', '')
#     else:
#         text = func_c(leaf0.text, leaf1.text)
#     pos = f'{leaf0.pos}~{leaf1.pos}'
#     gloss = f'{leaf0.gloss}~{leaf1.gloss}'
#     gloss = gloss.strip('~')
#     leaf = YidLeaf(None)
#     leaf.text = text
#     leaf.pos = pos
#     leaf.gloss = gloss
#     return leaf

# def combine_three(leaf0, leaf1, leaf2):
#     """Combine three leaves"""
#     text = f'{leaf0.text}~{leaf1.text}~{leaf2.text}'
#     text = text.replace('@', '')
#     pos = f'{leaf0.pos}~{leaf1.pos}~{leaf2.pos}'
#     gloss = f'{leaf0.gloss}~{leaf1.gloss}~{leaf2.gloss}'
#     gloss = gloss.strip('~')
#     leaf = YidLeaf(None)
#     leaf.text = text
#     leaf.pos = pos
#     leaf.gloss = gloss
#     return leaf
