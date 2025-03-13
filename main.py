import tkinter as tk
from interface import PokerApp

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = PokerApp(root)
        root.mainloop()
    except Exception as e:
        print(f"Произошла ошибка: {e}")