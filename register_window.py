"""Экран регистрации."""

import tkinter as tk
from tkinter import messagebox
from auth import register_user
from datetime import datetime
import re


class RegisterWindow:
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

    def __init__(self, db):
        self.db = db
        self.root = tk.Tk()
        self.root.title("Регистрация")
        self.root.geometry("500x800")
        self.root.configure(bg=self.BG_MAIN)
        self.root.resizable(False, False)

        self.vars = {
            "login": tk.StringVar(),
            "password": tk.StringVar(),
            "confirm": tk.StringVar(),
            "gender": tk.StringVar(value="Мужской"),
            "birth": tk.StringVar(),
            "height": tk.StringVar(),
            "weight": tk.StringVar(),
            "activity": tk.StringVar(value="Средний"),
        }
        self._build_ui()

    def _build_ui(self):
        card = tk.Frame(self.root, bg=self.BG_CARD, bd=0)
        card.place(relx=0.5, rely=0.5, anchor="center",
                   width=440, height=740)

        tk.Label(card, text="Регистрация",
                 font=("TkDefaultFont", 16, "bold"),
                 bg=self.BG_CARD, fg=self.FG_TEXT).pack(pady=(25, 15))

        self._entry(card, self.vars["login"], "Логин",
                    "Введите логин", max_len=50)
        self._entry(card, self.vars["password"], "Пароль",
                    "Введите пароль", is_pwd=True, max_len=50)
        self._entry(card, self.vars["confirm"], "Подтвердите пароль",
                    "Повторите пароль", is_pwd=True, max_len=50)
        self._dropdown(card, self.vars["gender"], "Пол",
                       ["Мужской", "Женский"])
        self._date_field(card, self.vars["birth"],
                         "Дата рождения", "ДД.ММ.ГГГГ")
        self._two_fields(card)
        self._dropdown(card, self.vars["activity"], "Уровень активности",
                       ["Низкий", "Средний", "Высокий"])

        btn_outer = tk.Frame(card, bg=self.BORDER_BLACK)
        btn_outer.pack(pady=(15, 0), padx=50, fill="x")
        btn_inner = tk.Frame(btn_outer, bg=self.BG_BUTTON)
        btn_inner.pack(fill="x", padx=1, pady=1)
        tk.Button(btn_inner, text="ЗАРЕГИСТРИРОВАТЬСЯ",
                  font=("TkDefaultFont", 11, "bold"),
                  bg=self.BG_BUTTON, fg=self.FG_WHITE,
                  activebackground=self.BG_BUTTON_HOVER,
                  activeforeground=self.FG_WHITE,
                  bd=0, relief="flat", cursor="hand2",
                  command=self._on_register,
                  highlightthickness=0).pack(fill="x", ipady=12)

    def _entry(self, parent, var, label, placeholder,
               is_pwd=False, max_len=None):
        f = tk.Frame(parent, bg=self.BG_CARD)
        f.pack(fill="x", padx=50, pady=(5, 3))
        tk.Label(f, text=label, font=("TkDefaultFont", 10, "bold"),
                 bg=self.BG_CARD, fg=self.FG_TEXT).pack(anchor="w")

        outer = tk.Frame(parent, bg=self.BORDER_BLACK)
        outer.pack(pady=(0, 10), padx=50, fill="x")
        inner = tk.Frame(outer, bg=self.BG_INPUT)
        inner.pack(fill="x", padx=1, pady=1)

        e = tk.Entry(inner, textvariable=var, font=("TkDefaultFont", 11),
                     bg=self.BG_INPUT, fg=self.FG_MUTED,
                     bd=0, relief="flat", highlightthickness=0)
        e.pack(fill="x", ipady=10, padx=12)

        if max_len:
            def lim(*a):
                v = var.get()
                if len(v) > max_len:
                    var.set(v[:max_len])
            var.trace_add("write", lim)

        def on_in(ev):
            if e.get() == placeholder:
                e.delete(0, tk.END)
                e.config(fg=self.FG_TEXT)
                if is_pwd:
                    e.config(show="*")

        def on_out(ev):
            if e.get() == "":
                e.insert(0, placeholder)
                e.config(fg=self.FG_MUTED)
                if is_pwd:
                    e.config(show="")

        if is_pwd:
            e.insert(0, placeholder)
            e.config(fg=self.FG_MUTED, show="")
        else:
            e.insert(0, placeholder)

        e.bind("<FocusIn>", on_in)
        e.bind("<FocusOut>", on_out)

    def _dropdown(self, parent, var, label, values):
        f = tk.Frame(parent, bg=self.BG_CARD)
        f.pack(fill="x", padx=50, pady=(5, 3))
        tk.Label(f, text=label, font=("TkDefaultFont", 10, "bold"),
                 bg=self.BG_CARD, fg=self.FG_TEXT).pack(anchor="w")

        outer = tk.Frame(parent, bg=self.BORDER_BLACK)
        outer.pack(pady=(0, 10), padx=50, fill="x")
        inner = tk.Frame(outer, bg=self.BG_INPUT, cursor="hand2")
        inner.pack(fill="x", padx=1, pady=1)

        lbl = tk.Label(inner, textvariable=var,
                       font=("TkDefaultFont", 11),
                       bg=self.BG_INPUT, fg=self.FG_TEXT,
                       anchor="w", cursor="hand2")
        lbl.pack(fill="x", ipady=10, padx=12, side="left", expand=True)

        arrow = tk.Label(inner, text="▼",
                         font=("TkDefaultFont", 10),
                         bg=self.BG_INPUT, fg=self.FG_TEXT,
                         cursor="hand2")
        arrow.pack(side="right", padx=12)

        menu = tk.Menu(self.root, tearoff=0)
        for v in values:
            menu.add_command(label=v,
                             command=lambda x=v: var.set(x))

        def open_menu(ev):
            menu.tk_popup(ev.x_root, ev.y_root)

        for w in [inner, lbl, arrow]:
            w.bind("<Button-1>", open_menu)

    def _date_field(self, parent, var, label, placeholder):
        f = tk.Frame(parent, bg=self.BG_CARD)
        f.pack(fill="x", padx=50, pady=(5, 3))
        tk.Label(f, text=label, font=("TkDefaultFont", 10, "bold"),
                 bg=self.BG_CARD, fg=self.FG_TEXT).pack(anchor="w")

        outer = tk.Frame(parent, bg=self.BORDER_BLACK)
        outer.pack(pady=(0, 10), padx=50, fill="x")
        inner = tk.Frame(outer, bg=self.BG_INPUT)
        inner.pack(fill="x", padx=1, pady=1)

        e = tk.Entry(inner, textvariable=var,
                     font=("TkDefaultFont", 11),
                     bg=self.BG_INPUT, fg=self.FG_MUTED,
                     bd=0, relief="flat", highlightthickness=0)
        e.pack(fill="x", ipady=10, padx=12)
        e.insert(0, placeholder)

        def on_in(ev):
            if e.get() == placeholder:
                e.delete(0, tk.END)
                e.config(fg=self.FG_TEXT)

        def on_out(ev):
            if e.get() == "":
                e.insert(0, placeholder)
                e.config(fg=self.FG_MUTED)

        def on_key(ev):
            if ev.keysym == "BackSpace":
                return
            v = e.get()
            digits = re.sub(r"\D", "", v)
            if len(digits) > 8:
                digits = digits[:8]
            fmt = ""
            for i, ch in enumerate(digits):
                if i in (2, 4):
                    fmt += "."
                fmt += ch
            if len(digits) >= 2 and int(digits[:2]) > 31:
                digits = "31" + digits[2:]
                fmt = "31"
                for i, ch in enumerate(digits[2:], start=2):
                    if i in (2, 4):
                        fmt += "."
                    fmt += ch
            if len(digits) >= 4 and int(digits[2:4]) > 12:
                digits = digits[:2] + "12" + digits[4:]
                fmt = digits[:2] + ".12"
                for i, ch in enumerate(digits[4:], start=4):
                    if i in (2, 4):
                        fmt += "."
                    fmt += ch
            if len(digits) == 8 and int(digits[4:8]) > 2026:
                digits = digits[:4] + "2026"
                fmt = digits[:2] + "." + digits[2:4] + "." + digits[4:]
            if fmt != v:
                e.delete(0, tk.END)
                e.insert(0, fmt)

        e.bind("<FocusIn>", on_in)
        e.bind("<FocusOut>", on_out)
        e.bind("<KeyRelease>", on_key)

    def _two_fields(self, parent):
        f = tk.Frame(parent, bg=self.BG_CARD)
        f.pack(fill="x", padx=50, pady=(5, 3))
        tk.Label(f, text="Рост и вес", font=("TkDefaultFont", 10, "bold"),
                 bg=self.BG_CARD, fg=self.FG_TEXT).pack(anchor="w")

        fr = tk.Frame(parent, bg=self.BG_CARD)
        fr.pack(pady=(0, 10), padx=50, fill="x")

        # --- Рост ---
        o1 = tk.Frame(fr, bg=self.BORDER_BLACK)
        o1.pack(side="left", fill="x", expand=True, padx=(0, 5))
        i1 = tk.Frame(o1, bg=self.BG_INPUT)
        i1.pack(fill="x", padx=1, pady=1)
        e1 = tk.Entry(i1, textvariable=self.vars["height"],
                      font=("TkDefaultFont", 11), bg=self.BG_INPUT,
                      fg=self.FG_MUTED, bd=0, relief="flat",
                      highlightthickness=0)
        e1.pack(fill="x", ipady=10, padx=12)
        e1.insert(0, "170")

        def o1_in(ev):
            if e1.get() == "170":
                e1.delete(0, tk.END)
                e1.config(fg=self.FG_TEXT)

        def o1_out(ev):
            if e1.get() == "":
                e1.insert(0, "170")
                e1.config(fg=self.FG_MUTED)

        def o1_key(ev):
            if ev.keysym == "BackSpace":
                return
            v = e1.get()
            digits = re.sub(r"\D", "", v)
            if len(digits) > 3:
                digits = digits[:3]
            if digits and int(digits) > 230:
                digits = "230"
            if digits != v:
                e1.delete(0, tk.END)
                e1.insert(0, digits)

        e1.bind("<FocusIn>", o1_in)
        e1.bind("<FocusOut>", o1_out)
        e1.bind("<KeyRelease>", o1_key)

        # --- Вес ---
        o2 = tk.Frame(fr, bg=self.BORDER_BLACK)
        o2.pack(side="left", fill="x", expand=True, padx=(5, 0))
        i2 = tk.Frame(o2, bg=self.BG_INPUT)
        i2.pack(fill="x", padx=1, pady=1)
        e2 = tk.Entry(i2, textvariable=self.vars["weight"],
                      font=("TkDefaultFont", 11), bg=self.BG_INPUT,
                      fg=self.FG_MUTED, bd=0, relief="flat",
                      highlightthickness=0)
        e2.pack(fill="x", ipady=10, padx=12)
        e2.insert(0, "65")

        def o2_in(ev):
            if e2.get() == "65":
                e2.delete(0, tk.END)
                e2.config(fg=self.FG_TEXT)

        def o2_out(ev):
            if e2.get() == "":
                e2.insert(0, "65")
                e2.config(fg=self.FG_MUTED)

        def o2_key(ev):
            if ev.keysym == "BackSpace":
                return
            v = e2.get()
            cleaned = re.sub(r"[^\d.]", "", v)
            if cleaned.count(".") > 1:
                cleaned = cleaned.replace(".", "",
                                          cleaned.count(".") - 1)
            parts = cleaned.split(".")
            parts[0] = parts[0][:3]
            if len(parts) > 1:
                parts[1] = parts[1][:1]
            cleaned = ".".join(parts)
            try:
                if parts[0] and int(parts[0]) > 230:
                    cleaned = "230" + (
                        "." + parts[1] if len(parts) > 1 else ""
                    )
            except ValueError:
                pass
            if cleaned != v:
                e2.delete(0, tk.END)
                e2.insert(0, cleaned)

        e2.bind("<FocusIn>", o2_in)
        e2.bind("<FocusOut>", o2_out)
        e2.bind("<KeyRelease>", o2_key)

    def _on_register(self):
        v = self.vars

        login = v["login"].get().strip()
        password = v["password"].get()
        confirm = v["confirm"].get()

        if not login or login == "Введите логин":
            messagebox.showwarning("Ошибка", "Введите логин")
            return

        if not password or password == "Введите пароль":
            messagebox.showwarning("Ошибка", "Введите пароль")
            return

        if password != confirm:
            messagebox.showerror("Ошибка", "Пароли не совпадают")
            return

        # Проверка уникальности логина
        existing = self.db.execute(
            "SELECT Код_пользователя FROM Пользователи WHERE Логин = ?",
            (login,)
        )
        if existing and len(existing) > 0:
            messagebox.showerror(
                "Ошибка",
                f"Логин «{login}» уже зарегистрирован.\n"
                f"Выберите другой логин."
            )
            return

        # Дата
        birth = v["birth"].get()
        if birth and birth != "ДД.ММ.ГГГГ":
            parts = birth.split(".")
            if len(parts) != 3:
                messagebox.showwarning(
                    "Ошибка",
                    "Введите дату в формате ДД.ММ.ГГГГ"
                )
                return
            try:
                day, month, year = int(parts[0]), int(parts[1]), int(parts[2])
            except ValueError:
                messagebox.showwarning("Ошибка", "Неверная дата")
                return

            if not (1 <= day <= 31):
                messagebox.showwarning("Ошибка", "День 1-31")
                return
            if not (1 <= month <= 12):
                messagebox.showwarning("Ошибка", "Месяц 1-12")
                return
            if not (1900 <= year <= 2026):
                messagebox.showwarning("Ошибка", "Год 1900-2026")
                return

            birth_db = f"{year}-{month:02d}-{day:02d}"
        else:
            messagebox.showwarning("Ошибка", "Введите дату рождения")
            return

        # Рост
        try:
            height = int(re.sub(r"\D", "", v["height"].get()) or 170)
            if height < 50 or height > 230:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Ошибка", "Рост 50-230 см")
            return

        # Вес
        try:
            weight_str = re.sub(r"[^\d.]", "", v["weight"].get())
            weight = float(weight_str) if weight_str else 65.0
            if weight < 20 or weight > 230:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Ошибка", "Вес 20-230 кг")
            return

        # Регистрация
        ok = register_user(
            self.db, login, password,
            v["gender"].get(), birth_db, height, v["activity"].get()
        )

        if ok:
            # Сохраняем вес
            user_result = self.db.execute(
                "SELECT Код_пользователя FROM Пользователи WHERE Логин = ?",
                (login,)
            )
            if user_result:
                user_id = user_result[0][0]
                today = datetime.now().strftime("%Y-%m-%d")
                self.db.execute(
                    "INSERT INTO ИсторияВеса "
                    "(Код_пользователя, ДатаЗаписи, ВесКг) "
                    "VALUES (?, ?, ?)",
                    (user_id, today, weight)
                )

            messagebox.showinfo(
                "Успех",
                f"Пользователь «{login}» зарегистрирован!"
            )
            self.root.destroy()
            from login_window import LoginWindow
            LoginWindow(self.db).run()
        else:
            messagebox.showerror(
                "Ошибка",
                "Не удалось зарегистрироваться.\n"
                "Возможно, такой логин уже существует."
            )

    def run(self):
        self.root.mainloop()