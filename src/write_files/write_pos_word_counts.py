"""Reads the json files and writes word/pos info

Reads
<new_corpus_dir> / 'data' / 'json' / FILE.json
and writes
<new_corpus_dir> / 'data' / 'misc' / 'pos_info.txt'
<new_corpus_dir> / 'data' / 'misc' / 'word_info.txt'

It uses the info only for the two files currently used for the NLP pipeline,
1910e-grine-felder and 1947e-royte-pomerantsen.
"""
import os
import sys
import logging
import argparse
import unicodedata
import pathlib
import json
from collections import Counter

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name

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

def get_counters(fnames):
    pos2word2count = Counter()
    word2pos2count = Counter()
    for fname in fnames:
        with open(fname, 'r', encoding='utf-8') as fin:
            file_info = json.load(fin)

        for tinfo in file_info:
            #tree_id = tinfo['tree_id']
            s_leaves = [leaf for leaf in tinfo['leaves']
                        if leaf['ltype'] in ('st', 's')]

            for leaf in s_leaves:
                rom = leaf['rom']
                pos = leaf['pos']
                if pos not in pos2word2count:
                    pos2word2count[pos] = Counter()
                pos2word2count[pos][rom] += 1
                if rom not in word2pos2count:
                    word2pos2count[rom] = Counter()
                word2pos2count[rom][pos] += 1
    return pos2word2count, word2pos2count

def write_pos(pos2word2count, misc_dir):
    lst = []
    for (pos, word2count) in pos2word2count.items():
        num_pos= sum(word2count.values())
        word_lst = ' '.join(
            [f'{word}:{count}' for (word, count) in word2count.most_common()])
        lst.append((num_pos, pos, word_lst))
    lst2 = sorted(lst, key=lambda x:x[0], reverse=True)


    with open(misc_dir / 'pos_info.txt', 'w', encoding='utf-8') as fout:
        fout.write('=================\n'
                   'POS tags\n'
                   '=================\n')
        for (num_pos, pos, word_lst) in lst2:
            fout.write(f'{num_pos:>5} {pos:<20}\n')

        fout.write('=================\n'
                   'POS tags with words\n'
                   '=================\n')
        for (num_pos, pos, word_lst) in lst2:
            fout.write(f'{num_pos:>5} {pos:<20} {word_lst}\n')

def write_words(word2pos2count, misc_dir):
    lst = []
    for (word, pos2count) in word2pos2count.items():
        num_word= sum(pos2count.values())
        pos_lst = ' '.join(
            [f'{pos}:{count}' for (pos, count) in pos2count.most_common()])
        lst.append((num_word, word, pos_lst))
    lst2 = sorted(lst, key=lambda x:x[0], reverse=True)


    with open(misc_dir / 'word_info.txt', 'w', encoding='utf-8') as fout:
        fout.write('=================\n'
                   'Words\n'
                   '=================\n')
        for (num_word, word, pos_lst) in lst2:
            fout.write(f'{num_word:>5} {word:<20}\n')

        fout.write('=================\n'
                   'Words with POS tags\n'
                   '=================\n')
        for (num_word, word, pos_lst) in lst2:
            fout.write(f'{num_word:>5} {word:<20} {pos_lst}\n')


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

    (pos2word2count, word2pos2count) = get_counters(fnames)
    write_pos(pos2word2count, misc_dir)
    write_words(word2pos2count, misc_dir)


if __name__ == '__main__':
    main()
