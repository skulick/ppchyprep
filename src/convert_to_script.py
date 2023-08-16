"""Code to convert romanized version in treebank to yiddish script
Mostly relies on the yiddish.py package but with some accessory files.
Our concern here is to convert the Yiddish treebank representation back
to the yiddish script version.

detransliteration-overrides: various cases where the desired form is not returned
by yiddish.detransliterate.  Sometimes this is because detransliterate
returns one form, and the romanization can be ambiguous, so here we hard-code
which one we want, which may depend also on the POS tag. Also some assorted
special cases.

detransliteration-remove-hyphen: a few cases for which detransliterate
returns the desired form only if the hyphen is removed.

detransliteration-keep-hyphen: the inverse, in which the romanization has
a hyphen and we need to keep it as a unit

detransliteration-no-lk:  (word, pos) for which we need to call detransliterate
with loshn_koydesh=False
"""
import unicodedata
import yiddish

with open('./src/conversion_lists/detransliteration-overrides.txt',
          'r', encoding='utf-8') as fin:
    lines = fin.readlines()
lines = [line.rstrip('\n') for line in lines]
lines = [line.split('\t') for line in lines
         if line and line[0] != ';']
word_pos2script = {(word, pos):script
                   for (word, pos, script) in lines}

with open('./src/conversion_lists/detransliteration-remove-hyphen.txt',
          'r', encoding='utf-8') as fin:
    lines = fin.readlines()
lines = [line.rstrip('\n') for line in lines]
lines = [line.split('\t') for line in lines
         if line[0] != ';']
word_pos_remove_hyphen = set((word, pos) for (word, pos) in lines)

with open('./src/conversion_lists/detransliteration-keep-hyphen.txt',
          'r', encoding='utf-8') as fin:
    lines = fin.readlines()
lines = [line.rstrip('\n') for line in lines]
lines = [line.split('\t') for line in lines
         if line and line[0] != ';']
word_pos_keep_hyphen = set((word, pos) for (word, pos) in lines)


with open('./src/conversion_lists/detransliteration-no-lk.txt',
          'r', encoding='utf-8') as fin:
    lines = fin.readlines()
lines = [line.rstrip('\n') for line in lines]
lines = [line.split('\t') for line in lines
         if line[0] != ';']
word_pos_no_lk = set((word, pos) for (word, pos) in lines)



# def call_sep(yivo_parts):
#     """Determine if should call yiddish.py on separate parts of hyphenated romanization
#     In general, gets confused with hyphenated ones
#     So actually should make it so it always does separate parts unless overridden
#     Doesn't get ones with
#     first part far
#     second part lebn
#     proper name - e.g. avrom-yankev (can get each part individually)
#     proper name possessive - e.g. avrom-yankevs
#     """
#     if len(yivo_parts) != 2:
#         return False
#     if (yivo_parts[1] == 'lebn' or
#         yivo_parts[0] == 'far'):
#         return True
#     if pos in ('NPR', 'NPR$'):
#         return True
#     return False

def convert(yivo, pos):
    """convert yivo text to Yiddish script unicode
    (1) yivo text coming from treebank may have ~ for joined words.  get rid of that
    (2) if in hard-coded exceptions, use that (detranslitation-overrides)
    (3) check if hyphen needs to be removed (detransliteration-remove-hyphen)
    (4) if two-part with hyphen, make recursive call unless
        in list of exceptions  (detransliteration-keep-hyphen)
    (5) if in exceptions for which it's okay to use the yiddish package,
    but only with loshn_koydesh=False, do that (detransliteration-no-lk)
    (6) otherwise call yiddish package
    """
    # (1)
    yivo = yivo.replace('~', '')

    # (2)
    if (yivo, pos) in word_pos2script:
        yid_text_ret = word_pos2script[(yivo, pos)]
        # already normalized
        return yid_text_ret

    # (3)
    if (yivo, pos) in word_pos_remove_hyphen:
        yivo = yivo.replace('-', '')


    # (4)
    # sometimes split words each have their own POS tag
    # e.g. far-~peysekh  P~NPR
    # othertimes not
    # e.g. galekh-lebn  N
    # if the first case, send each POS in separately
    # otherwise use the same POS for each part
    yivo_parts = yivo.split('-')
    pos_parts = pos.split('~')
    if len(yivo_parts) == 2 and (yivo, pos) not in word_pos_keep_hyphen:
        if len(pos_parts) == len(yivo_parts):
            yid_text_ret = '-'.join(
                [convert(yivo_part, pos_part)
                 for (yivo_part, pos_part) in zip(yivo_parts, pos_parts)])
        else:
            yid_text_ret = '-'.join(
                [convert(yivo_part, pos)
                 for yivo_part in yivo_parts])
        yid_text = unicodedata.normalize('NFC', yid_text_ret)
        return yid_text


    # (5), (6)
    if (yivo, pos) in word_pos_no_lk:
        yid_text_ret = yiddish.detransliterate(yivo, loshn_koydesh=False)
    else:
        yid_text_ret = yiddish.detransliterate(yivo, loshn_koydesh=True)

    yid_text = unicodedata.normalize('NFC', yid_text_ret)
    return yid_text

def main():
    for (text, pos) in [
            ('kol', 'N'),
            ("mir'n", 'PRO~MDF'),
            ('hey', 'N'),
            ('shemen', 'VB'),
            ('meyashev', 'RP-H'),
            ('galekh', 'N'),
            ('galekh-lebn', 'N'),
            ('far-~peysekh', 'P~NPR'),
            ('poshete', 'ADJ'),
            ('alef-beys', 'N'),
            ('avrom-yankev', 'NPR'),
            ('avrom-yankevs', 'NPR$'),
            ('loshn-hore', 'N'),
            ('yires-hakoved', 'N'),
            ('sholem-aleykhem', 'N'),
            ('aleykhem-sholem', 'N'),
            ('bas-yekhide', 'N')

    ]:
        print(f'{text} {pos}')
        yid2 = convert(text, pos)
        print(yid2)

if __name__ == '__main__':
    main()
