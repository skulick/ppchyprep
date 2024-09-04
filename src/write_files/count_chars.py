"""Writes character counts for Yiddish script leaves

Reads
<new_corpus_dir> / 'data' / 'json' / FILE.json
and writes
<new_corpus_dir> / 'data' / 'misc' / chars.txt

It uses the info only for the two files currently used for the NLP pipeline,
1910e-grine-felder and 1947e-royte-pomerantsen.

This counts the characters in both the source and tree versions of the leaves.
"""
import os
import sys
import logging
import argparse
import unicodedata
import pathlib
import json
from collections import Counter
from tqdm import trange

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name

def get_counter(fnames):
    counter = Counter()
    for fnum in trange(len(fnames)):
        fname = fnames[fnum]
        with open(fname, 'r', encoding='utf-8') as fin:
            file_info = json.load(fin)
        for tinfo in file_info:
            tree_id = tinfo['tree_id']
            for leaf in tinfo['leaves']:
                rom = leaf['rom']
                for ch1 in leaf['yid']:
                    counter[ch1] += 1
                    if hex(ord(ch1)) == '0xfb44':
                        print(f'pe with dagesh '
                              f'{rom} '
                              f'{fname} '
                              f'{tree_id}')
                    if ch1 in 'cjwW@':
                        print(f'has ascii {ch1} '
                              f'{rom} '
                              f'{fname} '
                              f'{tree_id}')


    return counter


def write_counter(out_fname, counter):
    """Write the combined counter

    Parameters
    ==========
    out_fname: Path
        output filename
    counter: Counter
         counter of characters
    """
    logger.info('writing counter')
    lst1 = list(counter.items())
    #lst2 = sorted(lst1, key=lambda x: (x[1], x[0]), reverse=True)
    lst = sorted(lst1)
    total = sum(counter.values())
    with open(out_fname, 'w', encoding='utf-8') as fout:
        fout.write(f'total # characters {total}\n')
        for (chr1, count) in lst:
            ord_chr1 = ord(chr1)
            fout.write(f'{count:>12}\t'
                       f'{hex(ord_chr1):>8}\t'
                       f'{unicodedata.name(chr1)}\n')

            #f'{unicodedata.category(chr1)}\n')


def main():
    """main loop"""
    parser = argparse.ArgumentParser(
        description='count characters in extracted files',
        add_help=False)
    parser.add_argument('new_corpus_dir', type=pathlib.Path, help='new corpus')    

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
                        level=logging.INFO)

    json_dir = args.new_corpus_dir / 'data' / 'json'
    misc_dir = args.new_corpus_dir / 'data' / 'misc'

    os.makedirs(misc_dir, exist_ok=True)

    files_to_use = [
        '1910e-grine-felder',
        '1947e-royte-pomerantsen'
        ]

    #fnames = (mod_dir / 'json2').glob('./*.json')
    fnames = [json_dir / f'{bname}.json'
              for bname in files_to_use]
    fnames = list(fnames)

    counter = get_counter(fnames)

    write_counter(misc_dir / 'chars.txt', counter)


if __name__ == '__main__':
    main()
