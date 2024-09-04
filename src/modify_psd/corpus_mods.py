"""Modify trees

(1) Misc. fixups in corpus-changes.  Mostly romanization fixups, along with a
few syntactic changes until they get integrated in the PPCHY github.
(2) Underscores in underscores.txt.  These separate words that appear in the
source text as separate words but are combined with an underscore in PPCHY.
(3) Separates colon from name.  This occurs a lot in 1910, with the speaker
names. When processing new text, a tokenization preprocessing step would do
this.  Other punctuations are already separated.
(4) separates hyphenated names into different words.  This is a leftover from
earlier processing, when this was done to better word-align the PPCHY
version of 1910 to another copy in the Yiddish Book Center corpus. Not really
necessary now.
(5) Marks contractions to be rejoined with @.  Other words that were originally
split are marked with @, but not (for the most part) contractions.  Doing this 
for contractions makes it easier for the processing later to create the
original tokens for the POS tokens.
"""

import re
import pathlib
from contractions import contraction_changes

RE_COLON = re.compile(r'\(NPR (?P<name>[A-Z\-a-z]+):\)')

RE_NAMES3 = re.compile(r'\((?P<pos>NPR\$?) (?P<name1>[A-Za-zb]+)[-](?P<name2>[A-Za-z]+)[-](?P<name3>[A-Za-z]+)\)')
RE_NAMES2 = re.compile(r'\((?P<pos>NPR\$?) (?P<name1>[A-Za-z]+)[-](?P<name2>[A-Za-z]+)\)')

RE_NUMP4 = re.compile(r'\(NUMP \(NUM (?P<p1>[a-z]+)_(?P<p2>[a-z]+)_(?P<p3>[a-z]+)_(?P<p4>[a-z]+)\)\)')
RE_NUMP3 = re.compile(r'\(NUMP \(NUM (?P<p1>[a-z]+)_(?P<p2>[a-z]+)_(?P<p3>[a-z]+)\)\)')
RE_NUMP2 = re.compile(r'\(NUMP \(NUM (?P<p1>[a-z]+)_(?P<p2>[a-z]+)\)\)')

RE_NUM4 = re.compile(r'\(NUM (?P<p1>[a-z]+)_(?P<p2>[a-z]+)_(?P<p3>[a-z]+)_(?P<p4>[a-z]+)\)')
RE_NUM3 = re.compile(r'\(NUM (?P<p1>[a-z]+)_(?P<p2>[a-z]+)_(?P<p3>[a-z]+)\)')
RE_NUM2 = re.compile(r'\(NUM (?P<p1>[a-z]+)_(?P<p2>[a-z]+)\)')

def read_changes(fname):
    """Reads either corpus-changes.txt or underscores.txt

    Changes are just two column from/two string replacements.
    """
    with open(fname, 'r', encoding='utf-8') as fin:
        lines = fin.readlines()
    lines = [line.rstrip('\n') for line in lines]
    lines = [line for line in lines
             if line and line[0] != ';']
    changes_ = [line.split('\t') for line in lines]
    return changes_

cwd = pathlib.Path(__file__).resolve().parent
changes = read_changes(cwd / 'corpus-changes.txt')
underscore_changes = read_changes(cwd / 'underscores.txt')

def make_changes(tree):
    """Apply modifications to each line of the tree"""
    for (from_, to_) in changes + underscore_changes:
        tree = tree.replace(from_, to_)

    # change (NPR rokhl:) to (NPR rokhl) (PUNC :)
    tree = RE_COLON.sub(r'(NPR \g<name>) (PUNC :)', tree)

    # separate hyphenated names. Names could be NPR or NPR$ so keep pos for last part
    # TODO: may just want to leave names hyphenated
    tree = RE_NAMES3.sub(r'(NPR \g<name1>) (NPR \g<name2>) (\g<pos> \g<name3>)', tree)
    tree = RE_NAMES2.sub(r'(NPR \g<name1>) (\g<pos> \g<name2>)', tree)

    # numbers already under a NUMP
    tree = RE_NUMP4.sub(r'(NUMP (NUM \g<p1>) (NUM \g<p2>) (NUM \g<p3>) (NUM \g<p4>))', tree)
    tree = RE_NUMP3.sub(r'(NUMP (NUM \g<p1>) (NUM \g<p2>) (NUM \g<p3>))', tree)
    tree = RE_NUMP2.sub(r'(NUMP (NUM \g<p1>) (NUM \g<p2>))', tree)

    # numbers not already under a NUMP.  These regexes need to be done after
    # the above
    tree = RE_NUM4.sub(r'(NUMP (NUM \g<p1>) (NUM \g<p2>) (NUM \g<p3>) (NUM \g<p4>))', tree)
    tree = RE_NUM3.sub(r'(NUMP (NUM \g<p1>) (NUM \g<p2>) (NUM \g<p3>))', tree)
    tree = RE_NUM2.sub(r'(NUMP (NUM \g<p1>) (NUM \g<p2>))', tree)

    for (from_, to_) in contraction_changes:
        tree = re.sub(from_, to_, tree)

    return tree
