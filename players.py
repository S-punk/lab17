import random
import time
from cards import Card

class Player:
    def __init__(self, name: str, money: int = 50000):
        self.name = name
        self.money = money
        self.hand = []
        self.folded = False
        self.acted = False

    def add_card(self, card: Card):
        self.hand.append(card)

    def fold(self):
        self.folded = True

    def bet(self, amount: int) -> bool:
        if amount > self.money:
            return False
        self.money -= amount
        return True

    def __repr__(self):
        return f"{self.name} (${self.money})"
    
class Dealer:
    def __init__(self, game):
        self.game = game

    def deal_cards(self):
        """Раздача карт игрокам."""
        for player in self.game.players:
            player.add_card(self.game.deck.draw())
            player.add_card(self.game.deck.draw())

    def deal_community_cards(self, count: int):
        """Раздача общих карт на стол."""
        for _ in range(count):
            card = self.game.deck.draw()
            self.game.community_cards.append(card)
            self.game.dealer_cards.append(card)  # Карты, которые видит только крупье

    def deal_next_community_cards(self):
        """Выкладывает следующие карты на стол (флоп, терн, ривер)."""
        if len(self.game.community_cards) == 0:
            self.deal_community_cards(3)  # Флоп
        elif len(self.game.community_cards) == 3:
            self.deal_community_cards(1)  # Терн
        elif len(self.game.community_cards) == 4:
            self.deal_community_cards(1)  # Ривер

    def reset_round(self):
        """Сброс состояния раунда."""
        self.game.community_cards = []
        self.game.dealer_cards = []
        self.game.current_bet = 200
        for player in self.game.players:
            player.hand = []
            player.folded = False

class Bot(Player):
    
    def decide_action(self, current_bet: int) -> str:
        """Логика принятия решений для бота."""
        if current_bet > self.money:
            return "fold"
        if random.random() < 0.5:  # 50% шанс поднять ставку
            return "raise"
        return "call"