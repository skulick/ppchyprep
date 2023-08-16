"""Create the cross-validation and final splits for ppchy

Takes one argument, root_dir, and expects there to be
<root_dir>/penn2/pos/twofiles.txt with the contents of the 1910
and 1947 files.
"""
import os
import pathlib
import argparse
import logging
import numpy as np
from sklearn.model_selection import StratifiedKFold
from sklearn.model_selection import train_test_split
from utils import read_pos_file

FINAL_SPLIT_X = 10

def make_split_info(X, y):
    """split up indices into 10 folds

    Parameters
    ==========
    X: array of int
       sent_num for each Sent
    y: array of int
       of source_id for each Sent

    Returns
    =======
    split_info: list of list of str
        dimensions [sent_num][11], where
        [x][y] is the 'r', 'd', or 't', indicating which section
        sentence #x is in for split #y (train, dev, test)
    """
    # pylint: disable=invalid-name
    split_info = [[None] * 11
                  for _ in range(len(X))]
    skf = StratifiedKFold(n_splits=10, shuffle=True, random_state=42)
    splits = skf.split(X, y)
    for split_num, (train, devtest) in enumerate(splits):
        X_train = X[train]
        X_devtest = X[devtest]
        y_devtest = y[devtest]
        #  now we need to split X_devtest and  y_devtest in half
        X_dev, X_test, _, _ = train_test_split(
            X_devtest, y_devtest,
            test_size=0.5,
            stratify=y_devtest,
            random_state=42)

        for sent_num in X_train:
            split_info[sent_num][split_num] = 'r'

        for sent_num in X_dev:
            split_info[sent_num][split_num] = 'd'

        for sent_num in X_test:
            split_info[sent_num][split_num] = 't'

    # make train/dev for final split
    X_train, X_dev, _, _ = train_test_split(
        X, y, test_size=.05, stratify=y, random_state=42)
    for sent_num in X_train:
        split_info[sent_num][FINAL_SPLIT_X] = 'r'
    for sent_num in X_dev:
        split_info[sent_num][FINAL_SPLIT_X] = 'd'
    return split_info


def write_split_defns(split_info, fname):
    """Write 2-d array of split info

    Writes row for each sent_num, one column for each split

    Parameters
    ==========
    split_info: list of list of str
        dimensions [sent_num][11], where
        [x][y] is the 'r', 'd', or 't', indicating which section
        sentence #x is in for split #y (train, dev, test)
    fname: Path
        output
    """
    with open(fname, 'w', encoding='utf-8') as fout:
        for (sent_num, lst) in enumerate(split_info):
            lst_str = '\t'.join(lst)
            fout.write(f'{sent_num}\t{lst_str}\n')

def write_splits(splits_dir, sents, split_info):
    """Write train/dev/test pos file for each split

    writes to <splits_dir>/split_[0-9]/pos/{train,dev,tst}
    and <splits_dir>/split_final/pos/{train,dev,tst}

    Parameters
    ==========
    splits_dir: Path
        <root_dir>/penn2/splits directory
    sents: list of Sent
        Each element has tokens for one sentence
    split_info: list of list of str
        dimensions [sent_num][11], where
        [x][y] is the 'r', 'd', or 't', indicating which section
        sentence #x is in for split #y (train, dev, test)
    """
    for split_num in range(10):
        split_dir = splits_dir / f'split_{split_num}'
        os.makedirs(split_dir / 'pos', exist_ok=True)
        for sec in ('train', 'dev', 'tst'):
            write_one_split_sec(split_dir, sec, sents, split_info, split_num)

    split_dir = splits_dir / 'split_final'
    os.makedirs(split_dir / 'pos', exist_ok=True)
    for sec in ('train', 'dev'):
        write_one_split_sec(split_dir, sec, sents, split_info, FINAL_SPLIT_X)


def write_one_split_sec(split_dir, sec, sents, split_info, split_num):
    """Write train or dev or tst for one split

    Appends the original sent_num to the end of the tree_id
    index is the new numbering for each sent in the section

    Parameters
    ==========
    splits_dir: Path
        output directory fo rthis split
    sec: str
        train, dev, tst
    sents: list of Sent
        Each element has tokens for one sentence
    split_info: list of list of str
        dimensions [sent_num][11], where
        [x][y] is the 'r', 'd', or 't', indicating which section
        sentence #x is in for split #y (train, dev, test)
    split_num: int
        index into second dimension of split_info
    """
    if sec == 'train':
        abbrev = 'r'
    elif sec == 'dev':
        abbrev = 'd'
    else:
        abbrev = 't'
    with open(split_dir / 'pos' / f'{sec}.txt',
              'w', encoding='utf-8') as fout:
        index = 0
        for sent in sents:
            if split_info[sent.sent_num][split_num] == abbrev:
                fout.write(f'SENT\t{index}\t'
                           f'{sent.tree_id}.{sent.sent_num}\n')
                for (word_num, word) in enumerate(sent.words):
                    fout.write(f'{word_num}\t{word}\n')
                fout.write('\n')
                index += 1
def main():
    """todo"""
    # pylint: disable=invalid-name
    parser = argparse.ArgumentParser(
        description='Make cross-validation splits',
        add_help=True)
    parser.add_argument('root_dir', nargs=None, type=pathlib.Path, help='output root directory')
    args = parser.parse_args()

    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
                        level=logging.INFO)

    sents = read_pos_file(args.root_dir / 'penn2' / 'pos' / 'twofiles.txt')
    X = np.asarray([sent.sent_num for sent in sents])
    y = np.asarray([sent.source_id for sent in sents])
    split_info = make_split_info(X, y)

    splits_dir = args.root_dir / 'penn2' / 'splits'
    os.makedirs(splits_dir, exist_ok=True)
    write_split_defns(split_info,
                      splits_dir / 'split_defns.txt')
    write_splits(splits_dir, sents, split_info)


if __name__ == '__main__':
    main()
