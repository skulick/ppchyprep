"""Code to convert romanized version in treebank to yiddish script"""
import unicodedata
import pathlib
import yiddish

cwd = pathlib.Path(__file__).resolve().parent

with open(cwd / 'rompos2uni_lookup.txt', 'r', encoding='utf-8') as fin:
    lines = fin.readlines()
lines = [line.rstrip('\n') for line in lines]
lines = [line.split('\t') for line in lines
         if line and line[0] != ';']
rompos2uni = {(word, pos):script
                   for (word, pos, script) in lines}

with open(cwd / 'rompos_removehyphen.txt', 'r', encoding='utf-8') as fin:
    lines = fin.readlines()
lines = [line.rstrip('\n') for line in lines]
lines = [line.split('\t') for line in lines
         if line[0] != ';']
rompos_removehyphen = set((word, pos) for (word, pos) in lines)

with open(cwd / 'rompos_keephyphen.txt', 'r', encoding='utf-8') as fin:
    lines = fin.readlines()
lines = [line.rstrip('\n') for line in lines]
lines = [line.split('\t') for line in lines
         if line and line[0] != ';']
rompos_keephyphen = set((word, pos) for (word, pos) in lines)


with open(cwd / 'rompos_lkfalse.txt', 'r', encoding='utf-8') as fin:
    lines = fin.readlines()
lines = [line.rstrip('\n') for line in lines]
lines = [line.split('\t') for line in lines
         if line[0] != ';']
rompos_lkfalse = set((word, pos) for (word, pos) in lines)


def convert(rom, pos):
    """convert romanized text to Yiddish script unicode"""
    # check if hard-coded as a lookup, bypassing detransliterate
    if (rom, pos) in rompos2uni:
        # assume already normalized
        return rompos2uni[(rom, pos)]

    # check if need to remove hyphen
    if (rom, pos) in rompos_removehyphen:
        rom = rom.replace('-', '')

    # If there is a hyphen, either keep it and continue
    # with regular processing, or do a recursive call
    if '-' in rom and (rom, pos) not in rompos_keephyphen:
        # recursive call on each individual part, combine them, and return.
        # Someties the word will exist from a merge of tree leaves, 
        # in which one of the words had a hyphen, such as
        # (P~NPR far-peysekh).  In this case each split-component will
        # have its own POS tag, so split the POS tag as well for the
        # recursive call. Otherwise just use the one POS tag for the
        # whole word for each component of the recursive call, which is
        # not ideal.
        rom_parts = rom.split('-')
        pos_parts = pos.split('~')
        #if len(rom_parts) == 2:
        if len(pos_parts) == len(rom_parts):
            yid_text_ret = '-'.join(
                [convert(rom_part, pos_part)
                 for (rom_part, pos_part) in zip(rom_parts, pos_parts)])
        else:
            yid_text_ret = '-'.join(
                [convert(rom_part, pos)
                 for rom_part in rom_parts])
        yid_text = unicodedata.normalize('NFC', yid_text_ret)
        return yid_text

    if (rom, pos) in rompos_lkfalse:
        yid_text_ret = yiddish.detransliterate(rom, loshn_koydesh=False)
    else:
        yid_text_ret = yiddish.detransliterate(rom, loshn_koydesh=True)

    yid_text = unicodedata.normalize('NFC', yid_text_ret)
    return yid_text

def main():
    for (text, pos) in [
            ('oder', 'N'),
            ('yid', 'N'),
            ('kol', 'N'),
            ('kol', 'Q'),
            ("v'kol", 'H'),
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
