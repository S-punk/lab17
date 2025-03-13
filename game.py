from typing import List
from cards import Deck, PokerHand
from players import Player, Bot, Dealer

class PokerGame:
    def __init__(self, players: List[Player]):
        self.players = players
        self.deck = Deck()
        self.pot = 0
        self.community_cards = []  # Общие карты на столе
        self.dealer_cards = []  # Карты, которые видит только крупье
        self.current_bet = 200
        self.dealer = Dealer(self)  # Добавляем крупье

    def start_round(self):
        """Начало нового раунда."""
        self.dealer.reset_round()
        self.dealer.deal_cards()  # Раздача карт игрокам
        self.dealer.deal_community_cards(3)  # Раздача флопа (3 карты)

    def deal_cards(self):
        for player in self.players:
            player.add_card(self.deck.draw())
            player.add_card(self.deck.draw())

    def deal_community_cards(self, count: int):
        """Раздача общих карт на стол."""
        for _ in range(count):
            card = self.deck.draw()
            self.community_cards.append(card)
            self.dealer_cards.append(card) 