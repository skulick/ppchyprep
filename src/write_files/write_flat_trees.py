"""Reads the json files and writes the flat tree files

Reads
<new_corpus_dir> / 'data' / 'json' / FILE.json
and writes
<new_corpus_dir> / 'data' / 'psd_flat' / FILE.psd

After this step, CorpusSearch is used to pretty-print the trees.
"""
import os
import logging
import argparse
import pathlib
import json
from tqdm import trange

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name

def main():
    """main loop"""
    parser = argparse.ArgumentParser(
        description='Convert .psd files to form for futher processing.',
        add_help=True)
    parser.add_argument('new_corpus_dir', type=pathlib.Path, help='new corpus')

    args = parser.parse_args()

    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
                        level=logging.INFO)

    json_dir = args.new_corpus_dir / 'data' / 'json'
    psd_flat_dir = args.new_corpus_dir / 'data' / 'psd_flat'

    os.makedirs(psd_flat_dir, exist_ok=True)

    fnames = (json_dir).glob('./*.json')
    fnames = list(fnames)

    for fnum in trange(len(fnames)):
        fname = fnames[fnum]

        with open(fname, 'r', encoding='utf-8') as fin:
            file_info = json.load(fin)

        with open(psd_flat_dir / f'{fname.stem}.psd',
                  'w', encoding='utf-8') as fout:

            for tinfo in file_info:
                tree_id = tinfo['tree_id']
                tree = tinfo['tree']
                if tree_id == 'notreeid':
                    fout.write(f'( {tree})\n')
                else:
                    fout.write(f'( {tree}(ID {tree_id}))\n')

if __name__ == '__main__':
    main()
