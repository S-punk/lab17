import random
from enum import Enum
from typing import List, Tuple

class Suit(Enum):
    HEARTS = '♥'
    DIAMONDS = '♦'
    CLUBS = '♣'
    SPADES = '♠'

class Rank(Enum):
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13
    ACE = 14

class Card:
    def __init__(self, rank: Rank, suit: Suit):
        self.rank = rank
        self.suit = suit

    def __repr__(self):
        return f"{self.rank.name} of {self.suit.value}"

class Deck:
    def __init__(self):
        self.cards = [Card(rank, suit) for rank in Rank for suit in Suit]
        random.shuffle(self.cards)

    def draw(self) -> Card:
        return self.cards.pop()

class PokerHand:
    def __init__(self, cards: List[Card]):
        self.cards = sorted(cards, key=lambda x: x.rank.value, reverse=True)

    def evaluate(self) -> Tuple[str, int]:
        """Определяет комбинацию и её силу."""
        if self.is_royal_flush():
            return "Royal Flush", 10
        elif self.is_straight_flush():
            return "Straight Flush", 9
        elif self.is_four_of_a_kind():
            return "Four of a Kind", 8
        elif self.is_full_house():
            return "Full House", 7
        elif self.is_flush():
            return "Flush", 6
        elif self.is_straight():
            return "Straight", 5
        elif self.is_three_of_a_kind():
            return "Three of a Kind", 4
        elif self.is_two_pair():
            return "Two Pair", 3
        elif self.is_one_pair():
            return "One Pair", 2
        else:
            return "High Card", 1

    def is_royal_flush(self) -> bool:
        """Проверяет, является ли комбинация роял-флэш."""
        return self.is_straight_flush() and self.cards[0].rank == Rank.ACE

    def is_straight_flush(self) -> bool:
        """Проверяет, является ли комбинация стрит-флэш."""
        return self.is_flush() and self.is_straight()

    def is_four_of_a_kind(self) -> bool:
        """Проверяет, есть ли четыре карты одного ранга."""
        ranks = [card.rank for card in self.cards]
        return any(ranks.count(rank) == 4 for rank in ranks)

    def is_full_house(self) -> bool:
        """Проверяет, есть ли фулл-хаус (три карты одного ранга и две другого)."""
        ranks = [card.rank for card in self.cards]
        return len(set(ranks)) == 2 and any(ranks.count(rank) == 3 for rank in ranks)

    def is_flush(self) -> bool:
        """Проверяет, есть ли флэш (пять карт одной масти)."""
        suits = [card.suit for card in self.cards]
        return len(set(suits)) == 1

    def is_straight(self) -> bool:
        """Проверяет, есть ли стрит (пять карт по порядку)."""
        if len(self.cards) < 5:
            return False
        ranks = [card.rank.value for card in self.cards]
        unique_ranks = sorted(set(ranks), reverse=True)
        # Проверка для комбинации 2-3-4-5-Туз
        if set(unique_ranks) == {2, 3, 4, 5, 14}:
            return True
        # Проверка для обычных стритов
        for i in range(len(unique_ranks) - 4):
            if unique_ranks[i] - unique_ranks[i + 4] == 4:
                return True
        return False

    def is_three_of_a_kind(self) -> bool:
        """Проверяет, есть ли три карты одного ранга."""
        ranks = [card.rank for card in self.cards]
        return any(ranks.count(rank) == 3 for rank in ranks)

    def is_two_pair(self) -> bool:
        """Проверяет, есть ли две пары карт одного ранга."""
        ranks = [card.rank for card in self.cards]
        return len([rank for rank in set(ranks) if ranks.count(rank) == 2]) == 2

    def is_one_pair(self) -> bool:
        """Проверяет, есть ли одна пара карт одного ранга."""
        ranks = [card.rank for card in self.cards]
        return any(ranks.count(rank) == 2 for rank in ranks)