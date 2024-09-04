import re
import pathlib
from collections import defaultdict
from .apostrophe_cases import add_apostrophe
from .generalized_cases import add_generalized_cases

def add_simple_splits(pos2re):
    cwd = pathlib.Path(__file__).resolve().parent
    with open(cwd / 'simple_splits.txt', 'r', encoding='utf-8') as fin:
        lines = fin.readlines()
    lines = [line.rstrip('\n')
             for line in lines]
    lines = [line.split('\t')
             for line in lines
             if line and line[0]!=';']
    for pos_words in lines:
        if len(pos_words) == 3:
            (pos, word1, word2) = pos_words
            pos2re[pos].append((re.compile(rf'^(?P<word1>{word1})(?P<word2>{word2})$'),
                                r'\g<word1> \g<word2>'))
        else:
            (pos, word1, word2, word3) = pos_words
            pos2re[pos].append((re.compile(rf'^(?P<word1>{word1})(?P<word2>{word2})(?P<word3>{word3})$'),
                                r'\g<word1> \g<word2> \g<word3>'))
POS2RE = defaultdict(list)

add_simple_splits(POS2RE)
add_generalized_cases(POS2RE)
add_apostrophe(POS2RE)

def split_word(pos, word):
    if pos not in POS2RE:
        #eprint(f'unknown pos {pos}')
        return None
    regexes_lst = POS2RE[pos]
    for (re_from, rep_to) in regexes_lst:
        (new_words, nsub) = re.subn(re_from, rep_to, word)
        if nsub == 1:
            return new_words.split()
    return None

def main():
    pos_words = [
        ('P~D', 'אױפֿן'),
        ('P~DR+P', 'צודערצו'),
         ]
    for (pos, word) in pos_words:
        new_words = split_word(pos, word)
        if new_words is not None:
            tmp = ' '.join(new_words)
            print(f'{pos} {word} ->\n{tmp}')
        else:
            print(f'{pos} {word} -> couldn\'t split')


if __name__ == '__main__':
    main()
