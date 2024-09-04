import re
from .constants import (
    TET,
    VAV,
    DU,
    TSU,
    TSU_DAGESH,
    FAR,
    ALEF,
    ZHE,
    VOS,
    P_PREFIX,
    D_SUFFIX,
    RP_OR_ADV_OR_RP_ADV_PREFIX,
    RP_N_PREFIX,
    NIT_NISHT
)


def add_generalized_cases(pos2re):
    for pos in ['RP~VBN',
                'RP~VB',
                'RP~VAN',
                'RP~VAG',
                'ADV~VBN',
                'ADV~VB',
                'ADV~VAN',
                'ADV~VAG',
                'RP-ADV~VB',
                'RP-ADV~VBN',
    ]:
        pos2re[pos].append((re.compile(rf'^(?P<word1>{RP_OR_ADV_OR_RP_ADV_PREFIX})(?P<word2>.*)$'),
                            r'\g<word1> \g<word2>'))

    for pos in ['RP~TO~VB', 'ADV~TO~VB']:
        # annoying, doesn't get the TSU_DAGESH if it's in a disjunctive with TSU
        # need to order TSU_DAGESH first
        pos2re[pos].append((re.compile(rf'^(?P<word1>{RP_OR_ADV_OR_RP_ADV_PREFIX})(?P<word2>{TSU_DAGESH})(?P<word3>.*)$'),
                            rf'\g<word1> {TSU} \g<word3>'))
        pos2re[pos].append((re.compile(rf'^(?P<word1>{RP_OR_ADV_OR_RP_ADV_PREFIX})(?P<word2>{TSU})(?P<word3>.*)$'),
                            rf'\g<word1> {TSU} \g<word3>'))        

    pos2re['TO~VB'].append((re.compile(rf'^(?P<word1>{TSU_DAGESH})(?P<word2>.*)$'),
                            rf'{TSU} \g<word2>'))
    pos2re['TO~VB'].append((re.compile(rf'^(?P<word1>{TSU})(?P<word2>.*)$'),
                            rf'{TSU} \g<word2>'))    

    # partial 2nd word
    pos2re['P~D'].append(
        (re.compile(rf'^(?P<word1>.*)(?P<word2>{D_SUFFIX})$'),
         r'\g<word1> \g<word2>'))

    # partial 2nd word - tu/du
    # there were two cases in PPCHY with either
    # s@ @tu            merged as stu
    # st@ @du (zt@ @du) merged as stu (ztu)
    #
    # now they're treated the same, and noralized back to du
    
    for pos in [
            'VBF~PRO',
            'MDF~PRO',
            'HVF~PRO',
            'BEF~PRO']:
        pos2re[pos].append(
            (re.compile(rf'^(?P<word1>.*{TET})(?P<word2>{VAV})$'),
             rf'\g<word1> {DU}'))

    for pos in ['P~PRO', 'P~N', 'P~NPR', 'P~DR+P']:
        pos2re[pos].append(
            (re.compile(rf'^(?P<word1>{P_PREFIX})(?P<word2>.*)$'),
             r'\g<word1> \g<word2>'))
        pos2re[pos].append(
            (re.compile(rf'^(?P<word1>{P_PREFIX})[-](?P<word2>.*)$'),
            r'\g<word1>- \g<word2>'))

    pos2re['P~D~N'].append(
        # far a yorn
        (re.compile(rf'^(?P<word1>.*{P_PREFIX})(?P<word2>{ALEF})(?P<word3>.*)$'),
         r'\g<word1> \g<word2> \g<word3>'))

    for pos in ['ADV~FP', 'WADV~FP', 'WPRO~FP']:
        pos2re[pos].append(
            (re.compile(rf'^(?P<word1>.*)(?P<word2>{ZHE})$'),
             r'\g<word1> \g<word2>'))
        pos2re[pos].append(
            (re.compile(rf'^(?P<word1>.*)[-](?P<word2>{ZHE})$'),
             r'\g<word1>- \g<word2>'))

    pos2re['RP-N~VBN'].append(
        (re.compile(rf'^(?P<word1>{RP_N_PREFIX})(?P<word2>.*)$'),
         r'\g<word1> \g<word2>'))

    pos2re['NEG~VAG'].append(
            (re.compile(rf'^(?P<word1>{NIT_NISHT})[-](?P<word2>.*)$'),
             r'\g<word1>- \g<word2>'))

    pos2re['P~WPRO'].append(
        (re.compile(rf'^(?P<word1>{FAR})(?P<word2>{VOS})$'),
         r'\g<word1> \g<word2>'))

    pos2re['P~WPRO'].append(
        (re.compile(rf'^(?P<word1>{TSU_DAGESH})(?P<word2>{VOS})$'),
         rf'{TSU} \g<word2>'))
    pos2re['P~WPRO'].append(
        (re.compile(rf'^(?P<word1>{TSU})(?P<word2>{VOS})$'),
         rf'{TSU} \g<word2>'))        
    
