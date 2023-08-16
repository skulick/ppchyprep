"""Namedtuples for storing POS data"""
from collections import namedtuple

Sent = namedtuple('Sent', 'sent_num tree_id source_id words')

class Word(namedtuple('Word', 'yivo pos yid1 yid2 yid3 ycode1 ycode2 ycode3')):
    def __str__(self):
        return (f'{self.yivo}\t{self.pos}\t'
                f'{self.yid1}\t{self.yid2}\t{self.yid3}\t'
                f'{self.ycode1}\t{self.ycode2}\t{self.ycode3}')
