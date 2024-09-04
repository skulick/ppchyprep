import re

FULL_VERB_3RD = '|'.join([
    #BEF
    'i\'',
    # HVF
    'hot',
    # MDF
    'vet', 'muz', 'badarf', 'ken',
    # VBF
    'iz', 'i\'', 'makht', 'lernt', 'derhert', 'heyst', 'tsitert',
    # VLF
    'volt',
])

FULL_VERB_1ST = '|'.join([
    # BEF
    'bin',
    # HVF
    'hob',
    # MDF
    'vel', 'vil', 'ken', 'zol',
    # VBF
    'veys', 'hob', 'bin', 'bet', 'drey', 'trog', 'meyn', 'kleyb', 'freg', 'nem',
    # VLF
    'volt',
    ])

PRONOUNS_BEFORE_MDF = 'ikh|er|ir|mir|du'
MDF_SUFFIX = "'l|'t|'n|'st"

PRONOUNS_AFTER_MDF = 'er|ir|men'

# (MDF 's@) (NP-SBJ (PRO @tu)) already marked with @
contraction_changes = [
    # partial pronoun, full verb
    # (NP-SBJ (ES 's)) (MDF vet), etc.
    (re.compile(rf"\(NP-SBJ(?P<tags>[1-9A-Z\-]*) \(ES 's\)\) \((?P<pos2>BEF|HVF|MDF|VBF|VLF) (?P<word2>{FULL_VERB_3RD})\)"),
     r"(NP-SBJ\g<tags> (ES s'@)) (\g<pos2> @\g<word2>)"),
    # written as s' a few times in 1947
    (re.compile(rf"\(NP-SBJ(?P<tags>[1-9A-Z\-]*) \(PRO ('s|s')\)\) \((?P<pos2>BEF|HVF|MDF|VBF|VLF) (?P<word2>{FULL_VERB_3RD})\)"),
     r"(NP-SBJ\g<tags> (PRO s'@)) (\g<pos2> @\g<word2>)"),
    (re.compile(rf"\(NP-SBJ(?P<tags>[1-9A-Z\-]*) \(PRO 's\)\) \((?P<pos2>BEF|HVF|MDF|VBF|VLF) (?P<word2>{FULL_VERB_3RD})\)"),
     r"(NP-SBJ\g<tags> (PRO s'@)) (\g<pos2> @\g<word2>)"),
    # if under meta, without tree
    (re.compile(rf"\(ES 's\) \((?P<pos2>BEF|HVF|MDF|VBF|VLF) (?P<word2>{FULL_VERB_3RD})\)"),
     r"(ES s'@) (\g<pos2> @\g<word2>)"),


    # (NP-SBJ (PRO 'kh) (VBF hob), etc.
    (re.compile(rf"\(NP-SBJ(?P<tags>[1-9A-Z\-]*) \(PRO 'kh\)\) \((?P<pos2>BEF|HVF|MDF|VBF|VLF) (?P<word2>{FULL_VERB_1ST})\)"),
     r"(NP-SBJ\g<tags> (PRO kh'@)) (\g<pos2> @\g<word2>)"),
    # two cases where it's written with kh'. this is overkill, but doesnt matter
    (re.compile(rf"\(NP-SBJ(?P<tags>[1-9A-Z\-]*) \(PRO kh'\)\) \((?P<pos2>BEF|HVF|MDF|VBF|VLF) (?P<word2>{FULL_VERB_1ST})\)"),
     r"(NP-SBJ\g<tags> (PRO kh'@)) (\g<pos2> @\g<word2>)"),

    # partial pronoun, partial verb
    # just one case - m' et.  also overkill

    (re.compile(r"\(NP-SBJ(?P<tags>[1-9A-Z\-]*) \(PRO m'\)\) \((?P<pos2>MDF) (?P<word2>'et)\)"),
     r"(NP-SBJ\g<tags> (PRO m'@)) (\g<pos2> @\g<word2>)"),

    # full pronoun and partial MDF
    (re.compile(rf"\(NP-SBJ(?P<tags>[1-9A-Z\-]*) \(PRO (?P<word1>{PRONOUNS_BEFORE_MDF})\)\) \((?P<pos2>MDF) (?P<word2>{MDF_SUFFIX})\)"),
     r"(NP-SBJ\g<tags> (PRO \g<word1>@)) (\g<pos2> @\g<word2>)"),

    # (WADVP-1 (WADV vu)) (IP-SUB (ADV-LOC *T*-1) (MDF 'l)
    (re.compile(r"\(WADVP-1 \(WADV vu\)\) \(IP-SUB \(ADVP-LOC \*T\*-1\) \(MDF 'l\)"),
     "(WADVP-1 (WADV vu@)) (IP-SUB (ADV-LOC *T*-1) (MDF @'l)"),

    # MDF_PREFIX 't + full word
    # could also be HVF
    # written as t' in 1910E-GRINE-FELDER,104.1648
    #(re.compile(rf"\(MDF (?P<word1>'t|t')\) \(NP-SBJ(?P<tags>[1-9A-Z\-]*) \((?P<pos2>PRO) (?P<word2>{PRONOUNS_AFTER_MDF})\)\)"),
    # "(MDF t'@) (NP-SBJ\g<tags> (PRO @\g<word2>))"),
    (re.compile(rf"\((?P<pos1>MDF|HVF) (?P<word1>'t|t')\) \(NP-SBJ(?P<tags>[1-9A-Z\-]*) \((?P<pos2>PRO) (?P<word2>{PRONOUNS_AFTER_MDF})\)\)"),
     r"(\g<pos1> t'@) (NP-SBJ\g<tags> (PRO @\g<word2>))"),



    # (NP-SBJ (Q keyner)) (MDF 't) (NEG nit)                  1910E-GRINE-FELDER,80.697
    (re.compile(r"\(NP-SBJ \(Q keyner\)\) \(MDF 't\) \(NEG nit\)"),
     "(NP-SBJ (Q keyner)) (MDF t'@) (NEG @nit)"),

    # (NP-SBJ *pro*) (MDF 't) (ADJP-PRD (ADJ glaykher))       1910E-GRINE-FELDER,90.1088
    (re.compile(r"\(NP-SBJ \*pro\*\) \(MDF 't\) \(ADJP-PRD \(ADJ glaykher\)\)"),
     "(NP-SBJ *pro*) (MDF t'@) (ADJP-PRD (ADJ @glaykher))"),

    # (NP-SBJ-1 *exp*) (MDF 't) (VB zayn)                     1910E-GRINE-FELDER,90.1106
    (re.compile(r"\(NP-SBJ-1 \*exp\*\) \(MDF 't\) \(VB zayn\)"),
     "(NP-SBJ-1 *exp*) (MDF t'@) (VB @zayn)"),

    # partial det and full noun
    # (D s') (N kleydl)   1910E-GRINE-FELDER,79.640, under eta
    (re.compile(r"\(D 's\) \(N kleydl\)"),
     "(D s'@) (N @kleydl)"),
    # (D s') (N taytsh)  1947E-ROYTE-POMERANTSEN,241.6203
    (re.compile(r"\(D s'\) \(N taytsh\)"),
     "(D s'@) (N @taytsh)"),

    # vos + 'tu, not contraction, but written with apostrophe
    # (WNP-1 (WPRO vos)) (IP-SUB (NP-ADV *T*-1) (MDF 0) (NP-SBJ (PRO 'tu)) 1910E-GRINE-FELDER,97.1340
    (re.compile(r"\(WNP-1 \(WPRO vos\)\) \(IP-SUB \(NP-ADV \*T\*-1\) \(MDF 0\) \(NP-SBJ \(PRO 'tu\)\)"),
     r"(WNP-1 (WPRO vos@)) (IP-SUB (NP-ADV *T*-1) (MDF 0) (NP-SBJ (PRO @'tu))"),

    # sometimes t is already taken from verb and marked as split, as in
    # (HVF hos@) (NP-SBJ (PRO @tu))
    # but sometimes not, as in
    # (HVF host) (NP-SBJ (PRO du))
    #
    # for now just mark the latter with @ and fix it up merging code.
    #n(re.compile("\((?P<pos1>BEF|HVF|MDF|RDF|VBF) (?P<word1>[a-z]+st)\) \(NP-SBJ \(PRO (?P<word2>du|tu)\)\)"),
    # "(\g<pos1> \g<word1>@) (NP-SBJ (PRO @\g<word2>))"),

    (re.compile(r"\((?P<pos1>BEF|HVF|MDF|RDF|VBF) (?P<word1>([a-z]+)|(')st)\) \(NP-SBJ \(PRO (?P<word2>du|tu)\)\)"),
     r"(\g<pos1> \g<word1>@) (NP-SBJ (PRO @\g<word2>))"),

    ]
