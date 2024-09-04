"""Reads the json files and writes the POS files

Reads
<new_corpus_dir> / 'data' / 'json' / FILE.json
and writes
<new_corpus_dir> / 'data' / 'pos' / FILE.txt
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
    pos_dir = args.new_corpus_dir / 'data' / 'pos'

    os.makedirs(pos_dir, exist_ok=True)

    fnames = (json_dir).glob('./*.json')
    fnames = list(fnames)

    for fnum in trange(len(fnames)):
        fname = fnames[fnum]

        with open(fname, 'r', encoding='utf-8') as fin:
            file_info = json.load(fin)

        with open(pos_dir / f'{fname.stem}.txt',
                  'w', encoding='utf-8') as fout:

            for tinfo in file_info:
                tree_id = tinfo['tree_id']
                if tree_id == 'notreeid':
                    continue
                fout.write(f'SENT\t{tree_id}\n')

                #tree_leaves = [leaf for leaf in tinfo['leaves']
                #               if leaf['ltype'] in ('st', 's')]
                for leaf in tinfo['leaves']:
                    if "end" in leaf:
                        num = f"{leaf['start']}-{leaf['end']}"
                    else:
                        num = leaf['start']
                    rom  = leaf['rom']
                    ycode = leaf['ycode']
                    yid = leaf['yid']
                    pos = leaf['pos']
                    gloss = leaf.get('gloss', '_')
                    fout.write(f'{num}\t{rom}\t{pos}\t{yid}\t{ycode}\t{gloss}\n')
                fout.write('\n')

if __name__ == '__main__':
    main()
