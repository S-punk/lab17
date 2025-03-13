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

    def betting_round(self):
        """Раунд ставок."""
        for player in self.players:
            if not player.folded:
                if isinstance(player, Bot):
                    action = player.decide_action(self.current_bet)
                    print(f"{player.name} решил {action}")
                    self.process_bot_action(player, action)
                else:
                    # Логика для игрока (управляется через интерфейс)
                    pass

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


    def determine_winner(self):
        """Определение победителя на основе комбинаций карт."""
        active_players = [player for player in self.game.players if not player.folded]
        if len(active_players) == 1:
            winner = active_players[0]
            self.update_log(f"{winner.name} выиграл раунд!")
            winner.money += self.game.pot
            self.game.pot = 0
            return

        # Сравниваем комбинации карт
        best_hand = None
        winners = []
        for player in active_players:
            hand = PokerHand(player.hand + self.game.community_cards)
            combination, strength = hand.evaluate()
            self.update_log(f"{player.name}: {combination} (сила: {strength})")
            if not best_hand or strength > best_hand[1]:
                best_hand = (player, strength)
                winners = [player]
            elif strength == best_hand[1]:
                winners.append(player)

        # Определяем победителя
        if len(winners) == 1:
            winner = winners[0]
            self.update_log(f"{winner.name} выиграл раунд с комбинацией {best_hand[0]}!")
            winner.money += self.game.pot
        else:
            self.update_log(f"Ничья между {', '.join([winner.name for winner in winners])}!")
            split_pot = self.game.pot // len(winners)
            for winner in winners:
                winner.money += split_pot
        self.game.pot = 0