import re
from .constants import (
    KAF, SAMEKH,
    APOSTROPHE, TET,
    VU, MEM,
    PRO_PREFIX,
    D_PREFIX,
    VOS, TU)


def add_apostrophe(pos2re):

    # partial pronoun and full verb or i'
    # s' + verb
    # s' + i'
    for pos in ['ES~MDF', 'ES~VBF',
                'ES~HVF', 'ES~BEF']:
        pos2re[pos].append(
            (re.compile(rf'^(?P<word1>{SAMEKH}){APOSTROPHE}(?P<word2>.*)$'),
             rf'\g<word1>{APOSTROPHE} \g<word2>'))

    # s' + verb
    # kh' + verb
    for pos in ['PRO~MDF','PRO~VBF',
                'PRO~HVF','PRO~BEF',
                'PRO~VLF']:
        pos2re[pos].append(
            (re.compile(rf'^(?P<word1>{SAMEKH}){APOSTROPHE}(?P<word2>.*)$'),
             rf'\g<word1>{APOSTROPHE} \g<word2>'))
        pos2re[pos].append(
            (re.compile(rf'^(?P<word1>{KAF}){APOSTROPHE}(?P<word2>.*)$'),
             rf'\g<word1>{APOSTROPHE} \g<word2>'))

    # partial pronoun and partial verb
    # PRO~MDF m'et

    pos2re['PRO~MDF'].append(
        (re.compile(rf'^(?P<word1>{MEM}){APOSTROPHE}(?P<word2>.*)$'),
              rf'\g<word1>{APOSTROPHE} \g<word2>'))

    # full word and partial verb
    # PRO(ikh) + MDF('l)
    # PRO(er,ir) + MDF('t)
    # PRO(mir) + MDF('n)
    # PRO(du) + MDF('st)
    pos2re['PRO~MDF'].append(
        (re.compile(rf'^(?P<word1>{PRO_PREFIX}){APOSTROPHE}(?P<word2>.*)$'),
              rf'\g<word1> {APOSTROPHE}\g<word2>'))
    # WADV(vu) + MDF('l)
    pos2re['WADV~MDF'].append(
        (re.compile(rf'^(?P<word1>{VU}){APOSTROPHE}(?P<word2>.*)$'),
              rf'\g<word1> {APOSTROPHE}\g<word2>'))

    # partial verb and full word
    # MDF(t') + PRO
    # MDF(t') + ADJ
    # MDF(t') + VB
    # MDF(t') + NEG
    for pos in ['MDF~PRO', 'HVF~PRO', 'MDF~ADJ', 'MDF~VB', 'MDF~NEG']:
        pos2re[pos].append(
            (re.compile(rf'^(?P<word1>{TET}){APOSTROPHE}(?P<word2>.*)$'),
              rf'\g<word1>{APOSTROPHE} \g<word2>'))

    # det noun
    pos2re['D~N'].append(
        (re.compile(rf'^(?P<word1>{D_PREFIX}){APOSTROPHE}(?P<word2>.*)$'),
              rf'\g<word1>{APOSTROPHE} \g<word2>'))

    pos2re['WPRO~PRO'].append(
        (re.compile(rf'^(?P<word1>{VOS}){APOSTROPHE}(?P<word2>{TU})$'),
              rf'\g<word1> {APOSTROPHE}\g<word2>'))    
