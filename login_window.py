"""Экран авторизации."""

import tkinter as tk
from tkinter import messagebox
from auth import login_user
import os


class LoginWindow:
    BG_MAIN = "#F0F0F0"
    BG_CARD = "#FFFFFF"
    BG_INPUT = "#E0E0E0"
    BG_BUTTON = "#7E57C2"
    BG_BUTTON_HOVER = "#5E35B1"
    FG_TEXT = "#333333"
    FG_MUTED = "#9E9E9E"
    FG_WHITE = "#FFFFFF"
    FG_ACCENT = "#7E57C2"
    BORDER_BLACK = "#000000"
    REMEMBER_FILE = "remember.txt"

    def __init__(self, db):
        self.db = db
        self.root = tk.Tk()
        self.root.title("Дневник питания")
        self.root.geometry("500x650")
        self.root.configure(bg=self.BG_MAIN)
        self.root.resizable(False, False)

        self.login_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.remember_var = tk.BooleanVar()

        self._load_remembered()
        self._build_ui()

    def _load_remembered(self):
        if os.path.exists(self.REMEMBER_FILE):
            try:
                with open(self.REMEMBER_FILE, "r", encoding="utf-8") as f:
                    data = f.read().strip()
                    if data:
                        self.login_var.set(data)
                        self.remember_var.set(True)
            except Exception:
                pass

    def _save_remembered(self):
        try:
            if self.remember_var.get():
                with open(self.REMEMBER_FILE, "w", encoding="utf-8") as f:
                    f.write(self.login_var.get())
            else:
                if os.path.exists(self.REMEMBER_FILE):
                    os.remove(self.REMEMBER_FILE)
        except Exception:
            pass

    def _build_ui(self):
        card = tk.Frame(self.root, bg=self.BG_CARD, bd=0)
        card.place(relx=0.5, rely=0.5, anchor="center", width=440, height=580)

        tk.Label(card, text="Дневник питания",
                 font=("TkDefaultFont", 18, "bold"),
                 bg=self.BG_CARD, fg=self.FG_TEXT).pack(pady=(50, 50))

        self.login_entry = self._create_entry(card, self.login_var, "Логин")
        self.password_entry = self._create_entry(card, self.password_var,
                                                 "Пароль", is_password=True)

        check_frame = tk.Frame(card, bg=self.BG_CARD)
        check_frame.pack(pady=(10, 25))
        tk.Checkbutton(check_frame, text="Запомнить меня",
                       variable=self.remember_var,
                       font=("TkDefaultFont", 10),
                       bg=self.BG_CARD, fg=self.FG_TEXT,
                       activebackground=self.BG_CARD,
                       selectcolor=self.FG_ACCENT,
                       cursor="hand2").pack()

        btn_outer = tk.Frame(card, bg=self.BORDER_BLACK)
        btn_outer.pack(pady=(0, 20), padx=50, fill="x")
        btn_inner = tk.Frame(btn_outer, bg=self.BG_BUTTON)
        btn_inner.pack(fill="x", padx=1, pady=1)

        tk.Button(btn_inner, text="Войти",
                  font=("TkDefaultFont", 13, "bold"),
                  bg=self.BG_BUTTON, fg=self.FG_WHITE,
                  activebackground=self.BG_BUTTON_HOVER,
                  activeforeground=self.FG_WHITE,
                  bd=0, relief="flat", cursor="hand2",
                  command=self._on_login,
                  highlightthickness=0).pack(fill="x", ipady=12)

        link = tk.Label(card, text="Нет аккаунта? Зарегистрироваться",
                        font=("TkDefaultFont", 10),
                        bg=self.BG_CARD, fg=self.FG_ACCENT,
                        cursor="hand2")
        link.pack(pady=(10, 0))
        link.bind("<Button-1>", lambda e: self._open_register())

    def _create_entry(self, parent, var, placeholder, is_password=False):
        outer = tk.Frame(parent, bg=self.BORDER_BLACK)
        outer.pack(pady=(0, 20), padx=50, fill="x")
        inner = tk.Frame(outer, bg=self.BG_INPUT)
        inner.pack(fill="x", padx=1, pady=1)

        entry = tk.Entry(inner, textvariable=var, font=("TkDefaultFont", 12),
                         bg=self.BG_INPUT, fg=self.FG_MUTED,
                         bd=0, relief="flat", highlightthickness=0)
        entry.pack(fill="x", ipady=14, padx=15)

        def on_in(e):
            if entry.get() == placeholder:
                entry.delete(0, tk.END)
                entry.config(fg=self.FG_TEXT)
                if is_password:
                    entry.config(show="*")

        def on_out(e):
            if entry.get() == "":
                entry.insert(0, placeholder)
                entry.config(fg=self.FG_MUTED)
                if is_password:
                    entry.config(show="")

        if is_password:
            entry.config(show="")
            entry.insert(0, placeholder)
            entry.config(fg=self.FG_MUTED)
        elif var.get():
            entry.config(fg=self.FG_TEXT)
        else:
            entry.insert(0, placeholder)

        entry.bind("<FocusIn>", on_in)
        entry.bind("<FocusOut>", on_out)
        return entry

    def _on_login(self):
        login = self.login_var.get().strip()
        password = self.password_var.get()

        if not login or login == "Логин":
            messagebox.showwarning("Ошибка", "Введите логин")
            return
        if not password or password == "Пароль":
            messagebox.showwarning("Ошибка", "Введите пароль")
            return

        user = login_user(self.db, login, password)
        if user:
            self._save_remembered()

            goal = self.db.execute(
                "SELECT Код_цели FROM Цели WHERE Код_пользователя = ?",
                (user.user_id,)
            )

            self.root.destroy()

            if not goal:
                from forecast_window import ForecastWindow
                ForecastWindow(self.db, user, is_new=True).run()
            else:
                from main_window import MainWindow
                MainWindow(self.db, user).run()
        else:
            messagebox.showerror("Ошибка", "Неверный логин или пароль")

    def _open_register(self):
        self.root.destroy()
        from register_window import RegisterWindow
        RegisterWindow(self.db).run()

    def run(self):
        self.root.mainloop()