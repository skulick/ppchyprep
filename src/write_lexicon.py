"""Write info about the words and pos in the two files being used

Takes one argument <root_dir>, and expects there to be

<root_dir> / penn2 / pos / twofiles.txt

writes
<root_dir> / penn2 / misc / lex-two-files / {five files listed below}

and likewise for lex-1910e-grine-felder, lex-1947e-royte-pomerantsen

Writes:
(1) word-counts.txt: summary file of # of types and instances of words
(2) word-list.txt: listing of words by frequency, and for each word,
    the pos tags that the word has
(3) pos-counts-all.txt: list of pos tags by frequency, and for each tag, the
    words that have that tag.
(4) pos-counts-combined.txt: same as (3), but only for the tags with a tilde
(5) pos-counts-split.txt: same as (3), but only the tags with an underscore
"""
import os
import logging
import argparse
import pathlib
from collections import Counter, defaultdict
from tabulate import tabulate
from utils import read_pos_file

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name

def write_info(in_dir, bnames, source_id, out_dir):
    """Collect and write info about the words

    Parameters
    ==========
    in_dir: Path
        where the bnames are located
    bnames: list string
        basenames of files to look at
    source_id: None or int
        if not None, only use sentences with this source_id (0 or 1)
    out_dir: Path
        where to write the output files
    """
    os.makedirs(out_dir, exist_ok=True)

    pos2counter = defaultdict(Counter)
    yivo2pos2count = defaultdict(Counter)

    for bname in bnames:
        sents = read_pos_file(in_dir / bname)
        if source_id is not None:
            sents = [sent for sent in sents
                     if sent.source_id == source_id]
        for sent in sents:
            for word in sent.words:
                yivo2pos2count[word.yivo][word.pos] += 1
                pos2counter[word.pos][word.yivo] += 1

    write_words_by_frequency(out_dir, yivo2pos2count)
    write_pos_counts(out_dir / 'pos-counts-all.txt', pos2counter)

    tmp = {pos:counter
           for (pos, counter) in pos2counter.items()
           if '~' in pos}
    write_pos_counts(out_dir / 'pos-counts-combined.txt', tmp)

    tmp = {pos:counter
           for (pos, counter) in pos2counter.items()
           if '_' in pos}
    write_pos_counts(out_dir / 'pos-counts-split.txt', tmp)


def write_pos_counts(fname, pos2counter):
    """Write counts of each POS tag

    Parameters
    ==========
    fname: Path
         output file
    pos2counter: dict str -> Counter
        key is pos
        val is counter  (word, count)
    """
    with open(fname, 'w', encoding='utf-8') as fout:
        num_words_all = sum(
            [sum(counter.values()) for counter in pos2counter.values()])

        # sort pos tags by # of words have the tag
        # the key keeps tags like ADV_S0, ADV_S1 in order
        tmp = sorted(
            [(sum(counter.values()), pos)
             for (pos, counter) in pos2counter.items()],
            key=lambda x:(-x[0], x[1]))


        table = []
        tot = 0
        for (count, pos) in tmp:
            tot += count
            pct = 100.0 * tot / num_words_all
            counter = pos2counter[pos]
            (word, _) = counter.most_common(1)[0]
            tmp = ' '.join([f'{word}:{count}' for (word, count) in counter.most_common()])
            row = [pos, count, pct, tmp]
            table.append(row)
        assert tot == num_words_all, 'impossible'
        table.append(['total', tot, 100.0, ''])
        fout.write(tabulate(table, tablefmt='plain', floatfmt='.2f'))


def write_words_by_frequency(out_dir, yivo2pos2count):
    """Write word-counts.txt and word-listing.txt

    Parameters
    ==========
    yivo2pos2count: dict string -> Counter
        key is yivo text
        val is Counter, key = pos, val = count
    """
    # sort by frequency of occurrence of each word
    all_texts = [(sum(pos2count.values()), text, pos2count)
                 for (text, pos2count) in yivo2pos2count.items()]
    all_texts.sort(reverse=True)

    # num different words
    num_types = len(all_texts)
    # num differnet words that have pos tag PUNC
    num_types_punc = len(
        [word_count
         for (word_count, _, pos2count) in all_texts
         if 'PUNC' in pos2count])
    num_types_wo_punc = num_types - num_types_punc

    num_tokens = sum([word_count
                      for (word_count, _, _) in all_texts])
    # a little imprecise, since it will include all occurrences of a
    # word that may only sometimes be a PUNC. This almost never happens
    # same is true for num_types_punc
    num_tokens_punc = sum(
        [word_count
         for (word_count, _, pos2count) in all_texts
         if 'PUNC' in pos2count])
    num_tokens_wo_punc = num_tokens - num_tokens_punc


    with open(out_dir / 'word-counts.txt', 'w', encoding='utf-8') as fout:
        fout.write(f'# word types all      = {num_types:>6}\n')
        fout.write(f'# word types punc     = {num_types_punc:>6}\n')
        fout.write(f'# word types wo punc  = {num_types_wo_punc:>6}\n\n')

        fout.write(f'# word tokens all     = {num_tokens:>6}\n')
        fout.write(f'# word tokens punc    = {num_tokens_punc:>6}\n')
        fout.write(f'# word tokens wo_punc = {num_tokens_wo_punc:>6}\n\n')

    with open(out_dir / 'word-listing.txt', 'w', encoding='utf-8') as fout:
        for (word_count, text, pos2count) in all_texts:
            pos_tags = ' | '.join([f'{tag}:{count}'
                                   for (tag, count) in pos2count.most_common()])
            fout.write(f'w\t{text:<30}\t{word_count:>6}\tp={pos_tags:<60}\n')

def main():
    """main loop"""
    parser = argparse.ArgumentParser(
        description='Convert .psd files to form for futher processing.',
        add_help=True)
    parser.add_argument('root_dir', nargs=None, type=pathlib.Path, help='output root directory')

    args = parser.parse_args()

    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
                        level=logging.INFO)

    write_info(
        args.root_dir / 'penn2' / 'pos',
        ['twofiles.txt',],
        None,
        args.root_dir / 'penn2' / 'misc' / 'lex-two-files')

    write_info(
        args.root_dir / 'penn2' / 'pos',
        ['twofiles.txt',],
        0,
        args.root_dir / 'penn2' / 'misc' / 'lex-1910e-grine-felder')

    write_info(
        args.root_dir / 'penn2' / 'pos',
        ['twofiles.txt',],
        1,
        args.root_dir / 'penn2' / 'misc' / 'lex-1947e-royte-pomerantsen')

if __name__ == '__main__':
    main()
