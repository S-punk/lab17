import random
import time
import tkinter as tk
import cards
import os
from tkinter import messagebox, simpledialog  # Добавьте simpledialog
from game import PokerGame
from players import Player, Bot
from cards import PokerHand
from PIL import Image, ImageTk

class PokerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Покер")
        self.game = PokerGame([Player("Игрок"), Bot("Бот 1"), Bot("Бот 2")])
        self.round_number = 1  # Счетчик раундов
        self.max_rounds = 10  # Максимальное количество раундов
        self.enter_pressed = tk.IntVar()

        # Загрузка изображений карт
        # Получаем путь к директории, где находится текущий скрипт
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Формируем путь к папке cards
        cards_dir = os.path.join(script_dir, "cards")
        self.card_images = self.load_card_images(cards_dir)

        # Основной canvas для отрисовки карт
        self.canvas = tk.Canvas(root, width=800, height=400, bg="green")
        self.canvas.pack()

        # Текстовое поле для логов
        self.log_text = tk.Text(root, height=10, width=80, state="disabled")
        self.log_text.pack()

        # Метка для отображения текущего раунда
        self.round_label = tk.Label(root, text=f"Раунд: {self.round_number}")
        self.round_label.pack()

        # Фрейм для кнопок действий
        self.button_frame = tk.Frame(root)
        self.button_frame.pack()

        # Кнопки действий
        self.fold_button = tk.Button(self.button_frame, text="Fold", command=self.fold)
        self.fold_button.pack(side=tk.LEFT)

        self.call_button = tk.Button(self.button_frame, text="Call", command=self.call)
        self.call_button.pack(side=tk.LEFT)

        self.raise_button = tk.Button(self.button_frame, text="Raise", command=self.raise_bet)
        self.raise_button.pack(side=tk.LEFT)

        # Запуск игры
        self.start_game()

    def wait_for_enter(self):
        """Ожидает нажатия клавиши Enter."""
        self.update_log("Нажмите Enter, чтобы продолжить...")
        self.root.bind("<Return>", self.on_enter_pressed)  # Привязываем Enter к обработчику
        self.root.wait_variable(self.enter_pressed)  # Ожидаем, пока переменная не изменится
        self.root.unbind("<Return>")  # Отвязываем Enter после нажатия

    def on_enter_pressed(self, event):
        """Обработчик нажатия Enter."""
        self.enter_pressed.set(1)  # Устанавливаем переменную в 1, чтобы продолжить выполнение
        if not self.game.players[0].folded: 
            self.update_log("Выберите действие")

    def load_card_images(self, folder_path: str) -> dict:
        """Загружает изображения карт из папки и изменяет их размер."""
        card_images = {}
        for rank in cards.Rank:
            for suit in cards.Suit:
                # Формируем имя файла (например, "2_of_hearts.png")
                card_name = f"{rank.name.lower()}_of_{suit.name.lower()}.png"
                card_path = f"{folder_path}/{card_name}"
                try:
                    # Загружаем изображение и изменяем его размер
                    image = Image.open(card_path)
                    image = image.resize((80, 120), Image.Resampling.LANCZOS)  # Изменяем размер до 80x120
                    card_images[(rank, suit)] = ImageTk.PhotoImage(image)
                except FileNotFoundError:
                    print(f"Файл {card_path} не найден.")
        return card_images

    def start_game(self):
        """Начало игры: раздача карт и первый раунд ставок."""
        self.game.players[0].money -= 200
        self.game.pot = 200
        self.game.deal_cards()
        self.game.deal_community_cards(3)
        self.draw_cards()
        self.update_log("Игра началась!")
        self.betting_round()
        

    def draw_cards(self):
        """Отрисовка карт игрока и общих карт на canvas."""
        self.canvas.delete("all")  # Очистка canvas

        # Отрисовка карт игрока
        player = self.game.players[0]
        x, y = 50, 300  # Позиция для карт игрока
        for card in player.hand:
            self.draw_card(card, x, y)
            x += 100

        x, y = 150, 50 # Позиция для покерной руки
        hand = PokerHand(player.hand + self.game.community_cards)
        self.canvas.create_text(x, y, text =f"Ваша покерная рука: {hand.evaluate()}", font=("Arial", 12))

        x, y = 250, 15
        self.canvas.create_text(x, y, text=f"Текущая ставка: {self.game.current_bet}", font=("Arial", 12))

        x, y = 500, 15
        self.canvas.create_text(x, y, text=f"Текущий банк: {self.game.pot}", font=("Arial", 12))

        x, y = 700, 150
        self.canvas.create_text(x, y, text =f"Ваши деньги: {self.game.players[0].money}", font=("Arial", 12))

        x, y = 700, 170
        self.canvas.create_text(x, y, text =f"Деньги Бота 1: {self.game.players[1].money}", font=("Arial", 12))

        x, y = 700, 190
        self.canvas.create_text(x, y, text =f"Деньги Бота 2: {self.game.players[2].money}", font=("Arial", 12))

        # Отрисовка общих карт на столе
        x, y = 50, 100  # Позиция для общих карт
        for card in self.game.community_cards:
            self.draw_card(card, x, y)
            x += 100

    def draw_card(self, card, x, y, hidden=False):
        """Отрисовка одной карты."""
        if hidden:
            self.canvas.create_rectangle(x, y, x + 80, y + 120, fill="blue")
            self.canvas.create_text(x + 40, y + 60, text="?", font=("Arial", 12))
        else:
            # Если карта открыта, рисуем её изображение
            card_image = self.card_images.get((card.rank, card.suit))
            if card_image:
                self.canvas.create_image(x, y, anchor=tk.NW, image=card_image)
            else:
                # Если изображение карты отсутствует, рисуем белый прямоугольник с текстом
                self.canvas.create_rectangle(x, y, x + 80, y + 120, fill="white")
                self.canvas.create_text(x + 40, y + 60, text=f"{card.rank.name}\n{card.suit.value}", font=("Arial", 12))

    def update_log(self, message: str):
        """Обновление логов."""
        self.log_text.config(state="normal")  # Включаем редактирование
        self.log_text.insert(tk.END, message + "\n")  # Добавляем сообщение
        self.log_text.config(state="disabled")  # Отключаем редактирование
        self.log_text.see(tk.END)  # Прокрутка вниз

    def betting_round(self):
        """Раунд ставок."""
        if self.game.players[0].folded:
            self.continue_betting_round()
        else:
            for player in self.game.players:
                player.acted = False  # Сбрасываем флаг "сделан ход"

            for player in self.game.players:
                if not player.folded:
                    if isinstance(player, Bot):
                        action = player.decide_action(self.game.current_bet)
                        self.update_log(f"{player.name} решил {action}")
                        self.process_bot_action(player, action)
                        player.acted = True  # Отмечаем, что бот сделал ход
                    else:
                        # Включение кнопок для игрока
                        self.fold_button.config(state=tk.NORMAL)
                        self.call_button.config(state=tk.NORMAL)
                        self.raise_button.config(state=tk.NORMAL)
                        break  # Ожидание действия игрока
        
        
        # Проверяем, завершился ли раунд
        

    def fold(self):
        """Действие Fold."""
        self.game.players[0].fold()
        self.update_log("Игрок решил Fold.")
        self.disable_buttons()
        
        self.game.players[0].acted = True 
        self.continue_betting_round()  # Продолжение раунда ставок

    def call(self):
        """Действие Call."""
        if self.game.players[0].bet(self.game.current_bet):
            self.update_log("Игрок решил Call.")
            self.disable_buttons()
            self.game.players[0].acted = True  # Отмечаем, что игрок сделал ход
            
            self.continue_betting_round()  # Продолжение раунда ставок
        else:
            messagebox.showerror("Ошибка", "Недостаточно денег!")

    def raise_bet(self):
        """Действие Raise."""
        amount = simpledialog.askinteger(
            "Raise",
            f"На сколько поднять ставку? (У вас есть {self.game.players[0].money} долларов)",
            parent=self.root,
            minvalue=1,
            maxvalue=self.game.players[0].money)
        if amount is not None:  # Если пользователь не нажал "Отмена"
            self.game.pot += amount
            if self.game.players[0].bet(amount):
                self.game.current_bet += amount
                self.update_log(f"Игрок решил Raise на {amount}.")
                self.disable_buttons()
                self.game.players[0].acted = True  # Отмечаем, что игрок сделал ход
                
                self.continue_betting_round()  # Продолжение раунда ставок
            else:
                messagebox.showerror("Ошибка", "Недостаточно денег!")

    def continue_betting_round(self):
        """Продолжение раунда ставок после действия игрока."""
        active_players = [player for player in self.game.players if not player.folded]
        if len(active_players) == 1:
            self.update_log(f"Все сбросили карты!")
            self.update_log("Раунд закончен")
            self.end_round()
        else:
            for player in self.game.players[1:]:
                active_players = [player for player in self.game.players if not player.folded]
                if len(active_players) == 1:
                    self.update_log(f"Все сбросили карты!")
                    self.update_log("Раунд закончен")
                    self.end_round()
                    return
                if player.folded:
                    continue
                if not player.folded:
                    if isinstance(player, Bot):
                        action = player.decide_action(self.game.current_bet)
                        self.update_log(f"{player.name} решил {action}")
                        self.process_bot_action(player, action)
            if self.check_round_end():
                self.update_log("Раунд закончен")
                self.end_betting_round()  # Завершение раунда ставок
        

    def process_bot_action(self, bot: Bot, action: str):
        """Обработка действий бота."""
        if action == "fold":
            
            bot.fold()
            bot.acted = True
            self.update_log(f"{bot.name} сбросил карты.")
        elif action == "call":
            if bot.bet(self.game.current_bet):
                self.game.pot += (self.game.current_bet - bot.current_bet)
                self.update_log(f"{bot.name} поддержал ставку.")
                
                bot.acted = True
            else:
                self.update_log(f"{bot.name} не может поддержать ставку и выбывает.")
                self.root.after(1500, bot.fold())
                bot.acted = True
        elif action == "raise":
            raise_amount = random.randint(self.game.current_bet + 1, self.game.current_bet + 10000)
            if bot.bet(raise_amount):
                self.game.pot += raise_amount
                self.game.current_bet = raise_amount
                bot.current_bet = self.game.current_bet
                self.update_log(f"{bot.name} поднял ставку до {raise_amount}.")
                
                bot.acted = True
            else:
                self.update_log(f"{bot.name} не может поднять ставку и выбывает.")
                
                bot.acted = True
                bot.fold()

    def disable_buttons(self):
        """Отключение кнопок после выбора действия."""
        self.fold_button.config(state=tk.DISABLED)
        self.call_button.config(state=tk.DISABLED)
        self.raise_button.config(state=tk.DISABLED)

    def check_round_end(self) -> bool:
        """Проверяет, завершился ли раунд ставок."""
        active_players = [player for player in self.game.players if not player.folded or not player.acted]
        if len(active_players) <= 1:
            return True  # Остался только один игрок
        # Проверяем, все ли игроки сделали ход
        for player in active_players:
            if not hasattr(player, 'acted') or not player.acted:
                return False
        return True
    
    def determine_winner(self):
        """Определение победителя на основе комбинаций карт."""
        active_players = [player for player in self.game.players if not player.folded]
        if len(active_players) == 1:
            winner = active_players[0]
            self.update_log(f"{winner.name} выиграл раунд! Нажмите Enter, чтобы продолжить.")
            self.wait_for_enter()  # Ожидаем нажатия Enter
            winner.money = winner.money + self.game.pot
            self.game.pot = 0
            for player in self.game.players:
                player.folded = False
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
            self.update_log(f"{winner.name} выиграл раунд с комбинацией {combination}! Нажмите Enter, чтобы продолжить.")
            self.wait_for_enter()  # Ожидаем нажатия Enter
            winner.money += self.game.pot
        else:
            self.update_log(f"Ничья между {', '.join([winner.name for winner in winners])}! Нажмите Enter, чтобы продолжить.")
            self.wait_for_enter()  # Ожидаем нажатия Enter
            split_pot = self.game.pot // len(winners)
            for winner in winners:
                winner.money += split_pot
        for player in self.game.players:
            player.folded = False
        self.game.pot = 0

    def end_betting_round(self):
        """Завершение раунда ставок и выкладывание карт на стол."""
        self.update_log("Раунд ставок завершен.")
        self.disable_buttons()

        # Крупье выкладывает следующие карты на стол
        self.game.dealer.deal_next_community_cards()
        self.draw_cards()  # Отрисовываем карты
        if len(self.game.community_cards) == 3:
            self.update_log("Флоп выложен. Нажмите Enter, чтобы продолжить.")
            self.wait_for_enter()  # Ожидаем нажатия Enter
        elif len(self.game.community_cards) == 4:
            self.update_log("Терн выложен. Нажмите Enter, чтобы продолжить.")
            self.wait_for_enter()  # Ожидаем нажатия Enter
        else:
            self.update_log("Ривер выложен. Нажмите Enter, чтобы продолжить.")
            self.wait_for_enter()  # Ожидаем нажатия Enter

        # Если все карты на столе выложены, завершаем раунд
        if len(self.game.community_cards) == 5:
            self.end_round()  # Определяем победителя и начинаем новый раунд
        else:
            self.betting_round()  # Продолжаем следующий раунд ставок

    def end_round(self):
        """Завершение раунда."""
        self.update_log("Раунд завершен.")
        active_players = [player for player in self.game.players if not player.folded]
        print(active_players)
        if len(active_players) == 0:
            self.update_log(f"Все сбросили карты!")
            self.start_new_round()  # Начинаем новый раунд
            return
        self.determine_winner()  # Определяем победителя
        self.start_new_round()  # Начинаем новый раунд

    def start_new_round(self):
        """Начало нового раунда."""
        self.game.players[0].money -= 200
        self.game.pot = 200
        if self.round_number >= self.max_rounds or len([player for player in self.game.players if not player.folded]) <= 1:
            self.end_game()  # Завершение игры
            return
        self.round_number += 1
        self.round_label.config(text=f"Раунд: {self.round_number}")

        self.game.start_round()  # Крупье начинает новый раунд
        self.game.deck.__init__()
        self.draw_cards()  # Отрисовываем карты
        self.betting_round()  # Начинаем раунд ставок

    def end_game(self):
        """Завершение игры."""
        active_players = [player for player in self.game.players if not player.folded]
        if len(active_players) == 1:
            winner = active_players[0]
            self.update_log(f"Игра завершена! Победитель: {winner.name}!")
        else:
            self.update_log(f"Игра завершена после {self.max_rounds} раундов.")
            # Определяем победителя по количеству денег
            winner = max(self.game.players, key=lambda player: player.money)
            self.update_log(f"Победитель: {winner.name} с ${winner.money}!")

        # Отключаем кнопки
        self.disable_buttons()