# !/usr/bin/env python
# -*-coding:utf-8 -*-
# File  : poker.py
# Author:author name
# Time  :2021/9/3 15:00
# Desc  :
import collections
from random import choice
Card = collections.namedtuple('Card', ['rank', 'suit'])


class FrenchDeck:
    ranks = [str(n) for n in range(2, 11)]+list('JQKA')
    suits = 'spades diamonds clubs hearts'.split()


    def __init__(self):
        self._cards = [Card(rank, suit) for suit in self.suits for rank in self.ranks]


    def __len__(self):
        return len(self._cards)


    def __getitem__(self, position):
        return self._cards[position]


def spades_high(card):
    rank_value = FrenchDeck.ranks.index(card.rank)
    return rank_value * len(suit_values) + suit_values[card.suit]

if __name__ == "__main__":
    beer_card = Card('7', 'diamonds')
    deck = FrenchDeck()
    print(len(deck))
    print(deck[0])
    print(deck[-1])
    print(choice(deck))
    print(deck[:3])
    print(deck[12::13])
    for card in deck:
        print(card)
    suit_values = dict(spades=0, diamonds=1, clubs=2, hearts=3)

    for card in sorted(deck, key=spades_high):
        print(card)
