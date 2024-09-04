NOKH = 'נאָכ'
TET = 'ט'
VAV = 'ו'
DU = 'דו'
TSU = 'צו'
TSU_DAGESH = 'צוּ'
NOKH_PREFIX = 'נאָכ'
ALEF = 'א'
ZHE = 'זשע'
FAR = 'פֿאַר'
NIT = 'ניט'
NISHT = 'נישט'
KAF = 'כ'
SAMEKH = 'ס'
APOSTROPHE = "'"
MEM = "מ"
VU = "װוּ"
DR = 'דר'
VOS = 'װאָס'
TU = 'טו'

D_PREFIX = '|'.join(
    [DR, SAMEKH])

PRO_PREFIX = '|'.join(
    [
    'איכ', #ikh
    'איר', #ir
    'ער', #er
    'מיר', #mir
    'דו', #du
    ])

P_PREFIX = '|'.join(
    [TSU, NOKH_PREFIX, FAR]
    )

NIT_NISHT = '|'.join(
    [NIT, NISHT]
    )

D_SUFFIX = '|'.join(
    ['ן',
     'עם',
     'ם',
     'אַ'])

RP_PREFIX = '|'.join(
    ['אָפּ',   #op
     'אָנ',   #on
     'אומ', #um
     'אײַנ',  #ayn
     'בײַ', #bay
     'אױפֿ',  #oyf
     'אױס',   #oys
     TSU,
     TSU_DAGESH,
     'איבער', #iber
     'נאָכ', #nokh
     'דורכ', #durkh
     'אונטער', #unter
     ])

ADV_PREFIX = '|'.join(
    ['אַראָפּ', #arop
     'אַרומ', #arum
     'אַװעק', #avek
     'אַרױס', #aroys
     'אַרײַנ', #arayn
     'אַרױפֿ', #aroyf
     'װידער', #vider
     'אַריבער', #ariber
     'אַנידער', #anider
     'פֿאַרבײַ', #farbay
     'אַרונטער', #arunter
     'צורעכט', #tsurekht
     'צוזאַמענ', #tsuzamen
     'פֿאַרנאַנדער', #farnander
     'פֿונאַנדער', #funander
     'פֿאַראַנאַנדער', #faranander
     ])

RP_ADV_PREFIX = '|'.join(
    [
    'מיט', #mit
    'צוריק', #tsurik
    ])

RP_OR_ADV_OR_RP_ADV_PREFIX = f'{RP_PREFIX}|{ADV_PREFIX}|{RP_ADV_PREFIX}'

# should include them all in here even though only only
# vey occurs with RP-N+VBN
RP_N_PREFIX = '|'.join(
    ['װײ',  #vey
    ])
