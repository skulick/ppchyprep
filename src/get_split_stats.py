"""Reads the split info and writes stats

Takes one argument, root_dir, and expects there to be directories
<root_dir>/penn2/splits/split{0-9,final}
Writes stats to <root_dir>/penn2/splits/splits-stats.txt
"""
import pathlib
import argparse
import logging
from utils import read_pos_file

FINAL_SPLIT_X = 10

def write_splits_stats(splits_dir):
    """Reads splits file and write info"""
    # pylint: disable=invalid-name
    with open(splits_dir / 'splits-stats.txt',
              'w', encoding='utf-8') as fout:
        for split_num in range(11):
            if split_num == FINAL_SPLIT_X:
                split_dir = splits_dir / 'split_final'
            else:
                split_dir = splits_dir / f'split_{split_num}'
            train_sents = read_pos_file(
                split_dir / 'pos' / 'train.txt')
            dev_sents = read_pos_file(
                split_dir / 'pos' / 'dev.txt')
            test_fname = split_dir / 'pos' / 'tst.txt'
            if test_fname.is_file():
                # no test file for split_final
                test_sents = read_pos_file(test_fname)
            else:
                test_sents = []

            train_0 = len([sent for sent in train_sents
                           if sent.source_id == 0])
            train_1 = len([sent for sent in train_sents
                           if sent.source_id == 1])

            dev_0 = len([sent for sent in dev_sents
                         if sent.source_id == 0])
            dev_1 = len([sent for sent in dev_sents
                         if sent.source_id == 1])

            test_0 = len([sent for sent in test_sents
                          if sent.source_id == 0])
            test_1 = len([sent for sent in test_sents
                          if sent.source_id == 1])

            total = len(train_sents) + len(dev_sents) + len(test_sents)

            train_0_pct = 100.0 * train_0 / (train_0 + train_1)
            train_1_pct = 100.0 * train_1 / (train_0 + train_1)
            train_pct = 100.0 * (train_0 + train_1) / total

            dev_0_pct = 100.0 * dev_0 / (dev_0 + dev_1)
            dev_1_pct = 100.0 * dev_1 / (dev_0 + dev_1)
            dev_pct = 100.0 * (dev_0 + dev_1) / total

            fout.write(f'{split_num:>2} '
                       f'{train_0:>4} '
                       f'({train_0_pct:>.2f}%) | '
                       f'{train_1:>4} '
                       f'({train_1_pct:>.2f}%) || '
                       f'{train_pct:>.2f}% || '
                       f'{dev_0:>4} '
                       f'({dev_0_pct:>.2f}%) | '
                       f'{dev_1:>4} '
                       f'({dev_1_pct:>.2f}%) || '
                       f'{dev_pct:>.2f}% || ')

            if test_sents:
                test_0_pct = 100.0 * test_0 / (test_0 + test_1)
                test_1_pct = 100.0 * test_1 / (test_0 + test_1)
                test_pct = 100.0 * (test_0 + test_1) / total
                fout.write(f'{test_0:>4} '
                           f'({test_0_pct:>.2f}%) | '
                           f'{test_1:>4} '
                           f'({test_1_pct:>.2f}%) || '
                           f'{test_pct:>.2f}% ||\n')
            else:
                fout.write('\n')

def main():
    """todo"""
    # pylint: disable=invalid-name
    parser = argparse.ArgumentParser(
        description='Convert .psd files to form for futher processing.',
        add_help=True)
    parser.add_argument('root_dir', nargs=None, type=pathlib.Path,help='output root directory')
    args = parser.parse_args()

    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
                        level=logging.INFO)

    splits_dir = pathlib.Path(args.root_dir / 'penn2' / 'splits')
    write_splits_stats(splits_dir)

if __name__ == '__main__':
    main()
