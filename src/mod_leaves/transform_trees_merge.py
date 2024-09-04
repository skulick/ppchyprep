"""Code for merging leaves that had been split in the treebank"""
from yid_leaf import YidLeaf

def ssplit(leaf):
    """Check if leaf is start of split"""
    #if not allow_apos and "'" in leaf.rom:
    #    return False
    return (not leaf.split_before and leaf.split_after)

def isplit(leaf):
    """Check if leaf is in middle of split"""
    #if not allow_apos and "'" in leaf.rom:
    #    return False
    return (leaf.split_before and leaf.split_after)

def esplit(leaf):
    """Check if leaf is end of split"""
    #if not allow_apos and "'" in leaf.rom:
    #    return False
    return (leaf.split_before and not leaf.split_after)

def merge_leaves(leaves):
    """Combine words/tags that were split"""
    merge_leaves_misc(leaves)
    merge_leaves_verb_du(leaves)
    merge_leaves_contraction_det_noun(leaves)
    merge_leaves_contraction_partial_pronoun_and_full_verb(leaves)
    merge_leaves_contraction_partial_pronoun_and_partial_verb(leaves)
    merge_leaves_contraction_full_word_and_partial_verb(leaves)
    merge_leaves_contraction_partial_verb_and_full_word(leaves)
    merge_leaves_apostrophe_not_contraction(leaves)

    leaves = [leaf for leaf in leaves
              if leaf is not None]
    return leaves

def merge_leaves_misc(leaves):
    """Merge misc cases.

    These are mostly the ones that had already been marked with @ before the
    additional @ cases were put in by modify_psd
    """
    #====================================================
    # P +  D(n,m,em)
    #====================================================
    func0 = lambda leaf: (leaf.pos == 'P')
    func1 = lambda leaf: (leaf.pos == 'D' and leaf.rom in ('n', 'm', 'em'))
    check_for_two(leaves, func0, func1)

    #====================================================
    # P +  D(a)
    # (PP-2 (P far@) (NP (D @a) (N gang))) 1947E-ROYTE-POMERANTSEN,46.1179
    #====================================================
    func0 = lambda leaf: (leaf.pos == 'P')
    func1 = lambda leaf: (leaf.pos == 'D' and leaf.rom == 'a')
    check_for_two(leaves, func0, func1)

    #====================================================
    # P +  PRO
    # (PP (P nokh@) (NP (PRO @dem) ...)) 1947E-ROYTE-POMERANTSEN,71.1743
    # (PP (P nokh@) (NP (PRO @dem)))     1947E-ROYTE-POMERANTSEN,220.5603
    # (PP (P nokh@) (NP (PRO @anand)))   1947E-ROYTE-POMERANTSEN,169.4167
    # (PP (P nokh@) (NP (PRO @anand)))   1947E-ROYTE-POMERANTSEN,246.6322
    #====================================================
    func0 = lambda leaf: (leaf.pos == 'P')
    func1 = lambda leaf: (leaf.pos == 'PRO')
    check_for_two(leaves, func0, func1)

    #====================================================
    # P +  N
    # (PP (P tsu-@) (NP (N @kind)))      1947E-ROYTE-POMERANTSEN,16.360
    # (PP (P tsu-@) (NP (N @kind)))      1947E-ROYTE-POMERANTSEN,60.1476
    # (PP (P tsu@) (NP (N @fus)))        1947E-ROYTE-POMERANTSEN,237.6107
    #====================================================
    func0 = lambda leaf: (leaf.pos == 'P')
    func1 = lambda leaf: (leaf.pos == 'N')
    check_for_two(leaves, func0, func1)

    #====================================================
    # P +  NPR
    # (PP (ADV nokh) (P far-@) (NP (NPR @peysekh)))   1910E-GRINE-FELDER,64.34))
    #====================================================
    func0 = lambda leaf: (leaf.pos == 'P')
    func1 = lambda leaf: (leaf.pos == 'NPR')
    check_for_two(leaves, func0, func1)

    #====================================================
    # P(far,tsu) + WPRO(vos)
    # mostly the many cases of favos, also some tsuvos
    # (WPP-1 (P far@) (WNP (WPRO @vos)))
    # (WPP-1 (P tsu@) (WNP (WPRO @vos)))
    #====================================================
    func0 = lambda leaf: (leaf.pos == 'P' and leaf.rom in ('far', 'tsu'))
    func1 = lambda leaf: (leaf.pos == 'WPRO' and leaf.rom == 'vos')
    check_for_two(leaves, func0, func1)

    #====================================================
    # P-DBL + DR+P
    # (PP (P-DBL tsu@) (PP (DR+P @dertsu)))    1947E-ROYTE-POMERANTSEN,202.5066
    # -DBL was removed by preprocessing
    #====================================================
    func0 = lambda leaf: (leaf.pos == 'P')
    func1 = lambda leaf: (leaf.pos == 'DR+P')
    check_for_two(leaves, func0, func1)

    #====================================================
    # P + PRO + VB
    #====================================================
    # this was for funanderlakhn. going to reanalyze this as
    # as ADV~VB
    #func0 = lambda leaf: (leaf.pos == 'P')
    #func1 = lambda leaf: (leaf.pos == 'PRO' and isplit(leaf))
    #func2 = lambda leaf: (leaf.pos == 'VB')
    #check_for_three(leaves, func0, func1, func2)

    #====================================================
    # P + D + N
    # (PP (P far@) (NP (D @a) (N @yorn))) 78.601
    # (PP (P far@) (NP (D @a) (N @yorn))) 79.630
    #====================================================
    func0 = lambda leaf: (leaf.pos == 'P')
    func1 = lambda leaf: (leaf.pos == 'D')
    func2 = lambda leaf: (leaf.pos == 'N')
    check_for_three(leaves, func0, func1, func2)

    #====================================================
    # Q + D
    # (NP (Q al@) (D @des) (N guts))         1947E-ROYTE-POMERANTSEN,172.4259
    #====================================================
    func0 = lambda leaf: (leaf.pos == 'Q')
    func1 = lambda leaf: (leaf.pos == 'D')
    check_for_two(leaves, func0, func1)

    #====================================================
    # RP-N + VBN
    # (RP-N) (VBN @geton)   1947E-ROYTE-POMERANTSEN,204.5123
    #====================================================
    func0 = lambda leaf: (leaf.pos in ('RP-N'))
    func1 = lambda leaf: (leaf.pos in ('VBN',))
    check_for_two(leaves, func0, func1)

    #====================================================
    # RP|ADV + VB|VBN|VAN|VAG
    # RP +  (VB|VBN|VAN|VAG)
    # ADV + (VB|VBN|VAN|VAG)
    # RP is op, on, um, ayn, bay, oyf, oys, tsu, iber, nokh, durkh, unter
    # ADV is arop, arum, avek, aroys, arayn, aroyf, vider,
    # anider, ariber, farbay, tsurekht, tsuzamen, farnander, faranander
    #====================================================
    func0 = lambda leaf: (leaf.pos in ('RP', 'ADV'))
    func1 = lambda leaf: (leaf.pos in ('VB', 'VBN', 'VAN', 'VAG'))
    check_for_two(leaves, func0, func1)

    #====================================================
    # RP|ADV + TO + VB
    #====================================================
    func0 = lambda leaf: (leaf.pos in ('ADV', 'RP'))
    func1 = lambda leaf: (leaf.pos == 'TO')
    func2 = lambda leaf: (leaf.pos == 'VB')
    check_for_three(leaves, func0, func1, func2)


    #====================================================
    # NEG + VAG
    # (NEG nisht-@) (VAG @farshteyendik) 1910E-GRINE-FELDER,94.1221
    # (in META, not tree)
    #====================================================
    func0 = lambda leaf: (leaf.pos in ('NEG',))
    func1 = lambda leaf: (leaf.pos in ('VAG',))
    check_for_two(leaves, func0, func1)

    #====================================================
    # RP-ADV + VB|VBN
    # RP-ADV is mit, tsurik
    #====================================================
    func0 = lambda leaf: (leaf.pos == 'RP-ADV')
    func1 = lambda leaf: (leaf.pos in ('VB', 'VBN'))
    check_for_two(leaves, func0, func1)

    #====================================================
    # VBI(lo) + PRO (mikh, mir)
    # (VBI lo@) (IP-INF (NP-SBJ (PRO @mir) ... (VB ...)))
    # (VBI lo@) (IP-INF (NP-SBJ (PRO @mikh) ... (VB ...)))
    #====================================================
    func0 = lambda leaf: (leaf.pos == 'VBI' and leaf.rom == 'lo')
    func1 = lambda leaf: (leaf.pos == 'PRO' and leaf.rom in ('mikh', 'mir'))
    check_for_two(leaves, func0, func1)

    #====================================================
    # WADV(vi) + Q(fl)
    # (WNP (WQP (WADV vi@) (Q @fl))) or
    # (WQP (WADV vi @) (Q @fl)) or
    # (CP-FRL (WQP (WADV vi@) (Q @fl)) ..)
    #====================================================
    func0 = lambda leaf: (leaf.pos == 'WADV' and leaf.rom == 'vi')
    func1 = lambda leaf: (leaf.pos == 'Q' and leaf.rom == 'fl')
    check_for_two(leaves, func0, func1)

    #====================================================
    # NEG(nisht,nit) + ADV(o)
    # (NEG nisht) (ADVP (ADV @o))
    #====================================================
    func0 = lambda leaf: (leaf.pos == 'NEG' and leaf.rom in ('nisht', 'nit'))
    func1 = lambda leaf: (leaf.pos == 'ADV' and leaf.rom == 'o')
    check_for_two(leaves, func0, func1)

    #====================================================
    # C(a) + NEG(nit)
    # (CP-ADV (C a@) (FRAG (NEG @nit)))  1910E-GRINE-FELDER,65.112
    #                                    1910E-GRINE-FELDER,82.758
    #                                    1910E-GRINE-FELDER,104.1672
    #====================================================
    func0 = lambda leaf: (leaf.pos == 'C' and leaf.rom == 'a')
    func1 = lambda leaf: (leaf.pos == 'NEG' and leaf.rom == 'nit')
    check_for_two(leaves, func0, func1)

    #====================================================
    # ADV + FP(zhe)
    # WADV + FP(zhe)
    # WPRO + FP(zhe)
    #====================================================
    func0 = lambda leaf: (leaf.pos == 'ADV')
    func1 = lambda leaf: (leaf.pos == 'FP' and leaf.rom == 'zhe')
    check_for_two(leaves, func0, func1)

    func0 = lambda leaf: (leaf.pos == 'WADV')
    func1 = lambda leaf: (leaf.pos == 'FP' and leaf.rom == 'zhe')
    check_for_two(leaves, func0, func1)

    func0 = lambda leaf: (leaf.pos == 'WPRO')
    func1 = lambda leaf: (leaf.pos == 'FP' and leaf.rom == 'zhe')
    check_for_two(leaves, func0, func1)

    # this was in for zogtzhe, but actually they're written separatley
    # func0 = lambda leaf: (leaf.pos == 'VBI')
    # func1 = lambda leaf: (leaf.pos == 'FP' and leaf.rom == 'zhe')
    # check_for_two(leaves, func0, func1)

    #====================================================
    # FP + D
    # FP + ADV
    # (NP (FP (ota@) (D @yene) (N shtiklekh)))  1947E-ROYTE-POMERANTSEN,141.3344
    # (ADVP-LOC (FP ota@) (ADV @do) (PP ...))   1947E-ROYTE-POMERANTSEN,152.3659
    #====================================================
    func0 = lambda leaf: (leaf.pos == 'FP')
    func1 = lambda leaf: (leaf.pos == 'D')
    check_for_two(leaves, func0, func1)

    func0 = lambda leaf: (leaf.pos == 'FP')
    func1 = lambda leaf: (leaf.pos == 'ADV')
    check_for_two(leaves, func0, func1)

    #====================================================
    # TO + VB
    # (IP-INF (TO tsu@) (VB @forn))    1947E-ROYTE-POMERANTSEN,121.2853
    # (IP-INF (TO tsu@) (VB @geyn) ..) 1947E-ROYTE-POMERANTSEN,141.3349
    # (IP-INF (TO tsu@) (VB @kukn))    1947E-ROYTE-POMERANTSEN,214.5367
    # (IP-INF (TO tsu@) (VB @nemen ..) 1947E-ROYTE-POMERANTSEN,244.6278
    #====================================================
    func0 = lambda leaf: (leaf.pos == 'TO')
    func1 = lambda leaf: (leaf.pos == 'VB')
    check_for_two(leaves, func0, func1)

def merge_leaves_verb_du(leaves):
    """verb + du/tu ending

    There are two cases

    # sometimes t is already taken from verb and was already
    # marked as split, as in
    # (HVF hos@) (NP-SBJ (PRO @tu))

    # but sometimes not du was already normalized, and
    # I added the @ in, as in
    # (HVF host@) (NP-SBJ (PRO @du))

    For the former, can just combine them for the merged word
    and for the latter, change the d to t.
    # in the split_word code the normalization can be done
    """
    #====================================================
    # (VB|RD|MD|HV|BE)F + PRO(du/tu)
    # VBF + PRO (du|tu)
    # MDF + PRO (du|tu)
    # HVF + PRO (du|tu)
    # BEF + PRO (du|tu)
    # RDF + PRO (du|tu)  (doesn't occur in 1910, 1947)
    #====================================================
    func0 = lambda leaf: (leaf.pos in ('VBF', 'RDF', 'MDF', 'HVF', 'BEF')
                          and leaf.rom.endswith('s'))
    func1 = lambda leaf: (leaf.pos == 'PRO' and leaf.rom == 'tu')
    check_for_two(leaves, func0, func1)

    #====================================================
    # (VB|RD|MD|HV|BE)F + PRO(du/tu)
    #====================================================

    func0 = lambda leaf: (leaf.pos in ('VBF', 'RDF', 'MDF', 'HVF', 'BEF')
                          and leaf.rom.endswith('st'))
    func1 = lambda leaf: (leaf.pos == 'PRO' and leaf.rom == 'du')
    func_c = lambda text0, text1: f"{text0}u"
    check_for_two(leaves, func0, func1, func_c=func_c)

    # (MDF muzt) (NP-SBJ (PRO du))
    func0 = lambda leaf: (leaf.pos == 'MDF' and
                          leaf.rom.endswith('zt'))
    func1 = lambda leaf: (leaf.pos == 'PRO' and leaf.rom == 'du')
    func_c = lambda text0, text1: f"{text0}u"
    check_for_two(leaves, func0, func1, func_c=func_c)



def merge_leaves_contraction_det_noun(leaves):
    #====================================================
    # D(dr') + N
    # (NP (D dr') (N @erd)) 1910E-GRINE-FELDER,64.40))
    #====================================================
    func0 = lambda leaf: (leaf.pos == 'D'
                          and leaf.rom == "dr'")
    func1 = lambda leaf: (leaf.pos == 'N')
    check_for_two(leaves, func0, func1)

    # #====================================================
    # # D(s') + N
    # # (NP (D s') (N @taytsh) 1947E-ROYTE-POMERANTSEN,9.206
    # #====================================================
    func0 = lambda leaf: (leaf.pos == 'D'
                          and leaf.rom == "s'")
    func1 = lambda leaf: (leaf.pos == 'N')
    check_for_two(leaves, func0, func1)



def merge_leaves_contraction_partial_pronoun_and_full_verb(leaves):
    """Merge leaves split by apostrophe"""
    #====================================================
    # ES + (BEF|HVF|MDF|VBF)
    # s' + @verb -> s'verb
    #====================================================
    func0 = lambda leaf: (leaf.pos == 'ES' and  leaf.rom == "s'")
    func1 = lambda leaf: (leaf.pos in ('BEF', 'HVF', 'MDF', 'VBF'))
    check_for_two(leaves, func0, func1)

    #====================================================
    # PRO(s') + (BEF|HVF|MDF|VBF|VLF)
    # same as previous case with ES, but where PRO is s'
    #====================================================
    func0 = lambda leaf: (leaf.pos == 'PRO' and leaf.rom == "s'")
    func1 = lambda leaf: (leaf.pos in ('BEF', 'HVF', 'MDF', 'VBF', 'VLF'))
    check_for_two(leaves, func0, func1)
    check_for_two(leaves, func0, func1)


    #====================================================
    # PRO(kh') + BEF|HVF|MDF|VBF|VLF
    #====================================================
    func0 = lambda leaf: (leaf.pos == 'PRO' and leaf.rom == "kh'")
    func1 = lambda leaf: (leaf.pos in ('BEF', 'HVF', 'MDF', 'VBF', 'VLF'))
    check_for_two(leaves, func0, func1)

def merge_leaves_contraction_partial_pronoun_and_partial_verb(leaves):
    """s'i', m'et"""
    # #====================================================
    # # s' + i' -> s'i' (== s'Ay')
    # #====================================================
    # func0 = lambda leaf: (leaf.pos in ('ES', 'PRO') and leaf.rom == "s'")
    # func1 = lambda leaf: (leaf.pos in ('BEF', 'VBF') and leaf.rom == "i'")
    # func_c = lambda text0, text1: "s'i'"
    # check_for_two(leaves, func0, func1, func_c=func_c)

    # #====================================================
    # # special case fixup  70.285
    # # (ES s'@) + (VBF @i') should be (ES 's) (VBF i')
    # # to be consistent with the other splits
    # # and converted to s'i'
    # # just change this in the treebank modifications to be 's
    # # instead of s' and then it will be handled under the other
    # # cases of 's@
    # # compare 70.285  (ES s'@) (VBF @i') and e.g. 77.578  (ES 's) (VBF i')
    # #====================================================
    # func0 = lambda leaf: (leaf.pos == 'ES' and leaf.rom == "s'@")
    # func1 = lambda leaf: (leaf.pos == 'VBF' and leaf.rom == "@i'")
    # func_c = lambda text0, text1: "s'i'"
    # check_for_two(leaves, func0, func1, func_c)

    #====================================================
    # PRO(m') + MDF('et)
    #====================================================
    func0 = lambda leaf: (leaf.pos == 'PRO' and leaf.rom == "m'")
    func1 = lambda leaf: (leaf.pos == 'MDF' and leaf.rom == "'et")
    # don't wnat to duplicate apostrophe
    func_c = lambda text0, text1: "m'et"
    check_for_two(leaves, func0, func1, func_c=func_c)

def merge_leaves_contraction_full_word_and_partial_verb(leaves):
    """PRO+MDF, WADV+MDF"""
    #====================================================
    # PRO(ikh) + 'l(MDF) -> PRO'l
    #====================================================
    func0 = lambda leaf: (leaf.pos == 'PRO' and leaf.rom == 'ikh')
    func1 = lambda leaf: (leaf.pos in ('MDF',) and leaf.rom == "'l")
    check_for_two(leaves, func0, func1)

    #====================================================
    # PRO(er,ir) + 't(MDF) -> PRO't
    #====================================================
    func0 = lambda leaf: (leaf.pos == 'PRO' and leaf.rom in ('er', 'ir'))
    func1 = lambda leaf: (leaf.pos == 'MDF' and leaf.rom == "'t")
    check_for_two(leaves, func0, func1)

    #====================================================
    # PRO(mir) + 'n(MDF) -> PRO'n
    #====================================================
    func0 = lambda leaf: (leaf.pos == 'PRO' and leaf.rom == 'mir')
    func1 = lambda leaf: (leaf.pos == 'MDF' and leaf.rom == "'n")
    check_for_two(leaves, func0, func1)

    #====================================================
    # PRO(du) + 'st(MDF) -> PRO'st
    #====================================================
    func0 = lambda leaf: (leaf.pos == 'PRO' and leaf.rom == 'du')
    func1 = lambda leaf: (leaf.pos == 'MDF' and leaf.rom == "'st")
    check_for_two(leaves, func0, func1)

    #====================================================
    # WADV + 'l(MDF) -> vu'l
    #====================================================
    func0 = lambda leaf: (leaf.pos == 'WADV' and leaf.rom == 'vu')
    func1 = lambda leaf: (leaf.pos == 'MDF' and leaf.rom == "'l")
    check_for_two(leaves, func0, func1)


def merge_leaves_contraction_partial_verb_and_full_word(leaves):
    """MDF|HVF+PRO, MDF+ADJ, MDF+VB, MDF+NEG"""

    #====================================================
    # t'(MDF|HVF) + PRO
    #====================================================
    func0 = lambda leaf: (leaf.pos in ('MDF', 'HVF')  and leaf.rom == "t'")
    func1 = lambda leaf: (leaf.pos == 'PRO' and leaf.rom in ("er", "ir", "men"))
    check_for_two(leaves, func0, func1)

    #====================================================
    # t'(MDF) + ADJ
    #====================================================
    func0 = lambda leaf: (leaf.pos == 'MDF' and leaf.rom == "t'")
    func1 = lambda leaf: (leaf.pos == 'ADJ')
    check_for_two(leaves, func0, func1)

    #====================================================
    # t'(MDF) + VB
    #====================================================
    func0 = lambda leaf: (leaf.pos == 'MDF' and  leaf.rom == "t'")
    func1 = lambda leaf: (leaf.pos == 'VB')
    check_for_two(leaves, func0, func1)

    #====================================================
    # t'(MDF) + NEG(nit)
    #====================================================
    func0 = lambda leaf: (leaf.pos == 'MDF' and leaf.rom == "t'")
    func1 = lambda leaf: (leaf.pos == 'NEG')
    check_for_two(leaves, func0, func1)

def merge_leaves_apostrophe_not_contraction(leaves):
    """vos'tu"""
    #====================================================
    # WPRO + 'tu(PRO) -> WPRO'tu
    #====================================================
    func0 = lambda leaf: (leaf.pos == 'WPRO' and leaf.rom == "vos")
    func1 = lambda leaf: (leaf.pos == "PRO" and leaf.rom == "'tu")
    check_for_two(leaves, func0, func1)

def check_for_two(leaves, func0, func1, func_c=None):
    """Find cases of two leaves to merge and merge them"""
    num = 0
    while num < len(leaves) - 1:
        leaf0 = leaves[num]
        leaf1 = leaves[num+1]
        if leaf0 is None or leaf1 is None:
            num += 1
        elif (ssplit(leaf0) and esplit(leaf1) and
              func0(leaf0) and func1(leaf1)):
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
        elif (ssplit(leaf0) and isplit(leaf1) and esplit(leaf2) and
              func0(leaf0) and func1(leaf1) and func2(leaf2)):
            leaves[num] = combine_three(leaf0, leaf1, leaf2)
            leaves[num+1] = None
            leaves[num+2] = None
            num += 2
        else:
            num += 1


def combine_two(leaf0, leaf1, func_c):
    """Combine two leaves"""
    if func_c is None:
        text = f'{leaf0.rom}{leaf1.rom}'
    else:
        text = func_c(leaf0.rom, leaf1.rom)
    pos = f'{leaf0.pos}~{leaf1.pos}'
    leaf = YidLeaf(pos, text)
    leaf.rom = leaf.text
    leaf.children = [leaf0, leaf1]
    return leaf

def combine_three(leaf0, leaf1, leaf2):
    """Combine three leaves"""
    text = f'{leaf0.rom}{leaf1.rom}{leaf2.rom}'
    pos = f'{leaf0.pos}~{leaf1.pos}~{leaf2.pos}'
    leaf = YidLeaf(pos, text)
    leaf.rom = leaf.text
    leaf.children = [leaf0, leaf1, leaf2]
    return leaf
