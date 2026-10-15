"""Экран дневника самочувствия — по макету Figma."""

import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta


class WellbeingWindow:
    BG_MAIN = "#F0F0F0"
    BG_CARD = "#FFFFFF"
    BG_INPUT = "#E0E0E0"
    BG_BUTTON = "#7E57C2"
    BG_BUTTON_HOVER = "#5E35B1"
    BG_ACCENT = "#7E57C2"
    BG_ACCENT_LIGHT = "#EDE7F6"
    FG_TEXT = "#333333"
    FG_MUTED = "#9E9E9E"
    FG_WHITE = "#FFFFFF"
    FG_ACCENT = "#7E57C2"
    BORDER_BLACK = "#000000"

    def __init__(self, db, user):
        self.db = db
        self.user = user
        self.root = tk.Toplevel()
        self.root.title("Дневник самочувствия")
        self.root.geometry("720x700")
        self.root.configure(bg=self.BG_MAIN)
        self.root.resizable(False, False)

        self.current_date = datetime.now()
        self.meal_id = None

        self.scales = {
            "Энергия": tk.IntVar(value=0),
            "Сытость": tk.IntVar(value=0),
            "Настроение": tk.IntVar(value=0),
            "ЖКТ": tk.IntVar(value=0),
        }
        self.circle_canvases = {}

        self._build_ui()
        self._load_day()

    def _build_ui(self):
        card = tk.Frame(self.root, bg=self.BG_CARD)
        card.pack(fill="both", expand=True, padx=20, pady=20)

        # ===== ЗАГОЛОВОК =====
        head = tk.Frame(card, bg=self.BG_CARD)
        head.pack(fill="x", padx=25, pady=(15, 10))

        tk.Label(head, text="Дневник самочувствия",
                 font=("TkDefaultFont", 15, "bold"),
                 bg=self.BG_CARD, fg=self.FG_TEXT).pack(side="left")

        close = tk.Label(head, text="✕",
                         font=("TkDefaultFont", 18, "bold"),
                         bg=self.BG_CARD, fg="#E53935",
                         cursor="hand2")
        close.pack(side="right")
        close.bind("<Button-1>", lambda e: self.root.destroy())

        tk.Frame(card, bg="#E0E0E0", height=1).pack(fill="x", padx=25)

        # ===== ЛИСТАНИЕ =====
        nav = tk.Frame(card, bg=self.BG_CARD)
        nav.pack(fill="x", padx=25, pady=(15, 10))

        tk.Button(nav, text="‹",
                  font=("TkDefaultFont", 14, "bold"),
                  bg=self.BG_CARD, fg=self.FG_TEXT,
                  bd=0, cursor="hand2", relief="flat",
                  highlightthickness=0,
                  command=self._prev_day).pack(side="left", padx=(0, 10))

        self.date_label = tk.Label(nav, text="",
                                   font=("TkDefaultFont", 11, "bold"),
                                   bg=self.BG_CARD, fg=self.FG_TEXT)
        self.date_label.pack(side="left", padx=10)

        tk.Button(nav, text="›",
                  font=("TkDefaultFont", 14, "bold"),
                  bg=self.BG_CARD, fg=self.FG_TEXT,
                  bd=0, cursor="hand2", relief="flat",
                  highlightthickness=0,
                  command=self._next_day).pack(side="left", padx=(10, 0))

        # ===== ПРИЁМ ПИЩИ =====
        tk.Label(card, text="Приём пищи",
                 font=("TkDefaultFont", 9),
                 bg=self.BG_CARD, fg=self.FG_MUTED).pack(anchor="w",
                                                         padx=25,
                                                         pady=(5, 3))

        self.meal_label = tk.Label(card, text="Загрузка...",
                                   font=("TkDefaultFont", 11),
                                   bg=self.BG_INPUT, fg=self.FG_TEXT,
                                   anchor="w", padx=15, pady=12)
        self.meal_label.pack(fill="x", padx=25, pady=(0, 15))

        # ===== ОЦЕНКА =====
        title_row = tk.Frame(card, bg=self.BG_CARD)
        title_row.pack(fill="x", padx=25, pady=(0, 5))

        tk.Label(title_row, text="Оценка самочувствия",
                 font=("TkDefaultFont", 11, "bold"),
                 bg=self.BG_CARD, fg=self.FG_TEXT).pack(side="left")

        tk.Label(title_row, text="Выберите значение от 1 до 5",
                 font=("TkDefaultFont", 9),
                 bg=self.BG_CARD, fg=self.FG_MUTED).pack(side="right")

        # Рамка со шкалами
        scales_outer = tk.Frame(card, bg=self.BORDER_BLACK)
        scales_outer.pack(fill="x", padx=25, pady=(5, 15))
        scales_inner = tk.Frame(scales_outer, bg=self.BG_CARD)
        scales_inner.pack(fill="x", padx=1, pady=1)

        for i, (name, left_hint, right_hint) in enumerate([
            ("Энергия", "Мало", "Много"),
            ("Сытость", "Голод", "Сытость"),
            ("Настроение", "Плохое", "Отличное"),
            ("ЖКТ", "Дискомфорт", "Комфорт"),
        ]):
            self._create_scale_row(scales_inner, name,
                                   left_hint, right_hint,
                                   first=(i == 0))

        # ===== КОММЕНТАРИЙ =====
        tk.Label(card, text="Комментарий",
                 font=("TkDefaultFont", 9),
                 bg=self.BG_CARD, fg=self.FG_MUTED).pack(anchor="w",
                                                         padx=25,
                                                         pady=(0, 3))

        self.comment_text = tk.Text(card, height=3,
                                    font=("TkDefaultFont", 11),
                                    bg=self.BG_INPUT, bd=0,
                                    relief="flat", wrap="word")
        self.comment_text.pack(fill="x", padx=25, pady=(0, 15))

        # ===== КНОПКИ =====
        btns = tk.Frame(card, bg=self.BG_CARD)
        btns.pack(fill="x", padx=25, pady=(0, 20))

        # Отмена
        c_frame = tk.Frame(btns, bg=self.BORDER_BLACK)
        c_frame.pack(side="left", padx=(0, 12))
        c_inner = tk.Frame(c_frame, bg=self.BG_CARD)
        c_inner.pack(padx=1, pady=1)
        tk.Button(c_inner, text="Отмена",
                  font=("TkDefaultFont", 11),
                  bg=self.BG_CARD, fg=self.FG_TEXT,
                  activebackground="#E0E0E0",
                  activeforeground=self.FG_TEXT,
                  bd=0, cursor="hand2", relief="flat",
                  highlightthickness=0,
                  command=self.root.destroy).pack(ipady=10, ipadx=35)

        # Сохранить
        s_frame = tk.Frame(btns, bg=self.BORDER_BLACK)
        s_frame.pack(side="left")
        s_inner = tk.Frame(s_frame, bg=self.BG_BUTTON)
        s_inner.pack(padx=1, pady=1)
        tk.Button(s_inner, text="Сохранить",
                  font=("TkDefaultFont", 11, "bold"),
                  bg=self.BG_BUTTON, fg=self.FG_WHITE,
                  activebackground=self.BG_BUTTON_HOVER,
                  activeforeground=self.FG_WHITE,
                  bd=0, cursor="hand2", relief="flat",
                  highlightthickness=0,
                  command=self._save).pack(ipady=10, ipadx=35)

    def _create_scale_row(self, parent, label, left_hint,
                          right_hint, first=False):
        """Создаёт строку со шкалой 1–5 (круглые кружки через Canvas)."""
        row = tk.Frame(parent, bg=self.BG_CARD)
        row.pack(fill="x")

        if not first:
            tk.Frame(row, bg="#E0E0E0", height=1).pack(fill="x")

        content = tk.Frame(row, bg=self.BG_CARD)
        content.pack(fill="x", padx=15, pady=15)

        # Название
        tk.Label(content, text=label,
                 font=("TkDefaultFont", 11, "bold"),
                 bg=self.BG_CARD, fg=self.FG_TEXT,
                 width=12, anchor="w").pack(side="left")

        # Левая подпись
        tk.Label(content, text=left_hint,
                 font=("TkDefaultFont", 8),
                 bg=self.BG_CARD, fg=self.FG_MUTED,
                 width=10, anchor="w").pack(side="left", padx=(5, 10))

        # Кружки (Canvas)
        circles_frame = tk.Frame(content, bg=self.BG_CARD)
        circles_frame.pack(side="left")

        self.circle_canvases[label] = {}

        for i in range(1, 6):
            canvas = tk.Canvas(circles_frame, width=32, height=32,
                               bg=self.BG_CARD,
                               highlightthickness=0,
                               cursor="hand2")
            canvas.pack(side="left", padx=4)

            oval = canvas.create_oval(4, 4, 28, 28,
                                      outline="#333333",
                                      fill=self.BG_CARD,
                                      width=2)

            def make_handler(value, scale_name):
                def h(e):
                    self.scales[scale_name].set(value)
                    self._redraw_scale(scale_name)
                return h

            canvas.bind("<Button-1>", make_handler(i, label))

            self.circle_canvases[label][i] = (canvas, oval)

        # Правая подпись
        tk.Label(content, text=right_hint,
                 font=("TkDefaultFont", 8),
                 bg=self.BG_CARD, fg=self.FG_MUTED,
                 width=10, anchor="e").pack(side="right")

    def _redraw_scale(self, scale_name):
        """Перерисовывает кружки для выбранной шкалы."""
        var = self.scales[scale_name]
        current = var.get()

        for i, (canvas, oval) in self.circle_canvases[scale_name].items():
            if i == current:
                canvas.itemconfig(oval, fill=self.BG_ACCENT,
                                  outline=self.BG_ACCENT)
            else:
                canvas.itemconfig(oval, fill=self.BG_CARD,
                                  outline="#333333")

    def _prev_day(self):
        self.current_date -= timedelta(days=1)
        self._load_day()

    def _next_day(self):
        self.current_date += timedelta(days=1)
        self._load_day()

    def _load_day(self):
        """Загружает данные за выбранный день."""
        date_str = self.current_date.strftime("%Y-%m-%d")
        date_display = self.current_date.strftime("%d.%m.%Y")

        today = datetime.now().date()
        current = self.current_date.date()
        if current == today:
            self.date_label.config(text=f"Сегодня, {date_display}")
        elif current == today - timedelta(days=1):
            self.date_label.config(text=f"Вчера, {date_display}")
        else:
            self.date_label.config(text=date_display)

        result = self.db.execute(
            "SELECT Код_приёма, ТипПриёма FROM ПриёмыПищи "
            "WHERE Код_пользователя = ? AND ДатаПриёма = ? "
            "ORDER BY Код_приёма DESC LIMIT 1",
            (self.user.user_id, date_str)
        )

        if result and len(result) > 0:
            self.meal_id = result[0][0]
            meal_type = result[0][1]
            self.meal_label.config(
                text=f"{meal_type}, {date_display}"
            )
        else:
            self.meal_id = None
            self.meal_label.config(
                text=f"Нет приёма пищи за {date_display}"
            )

        for var in self.scales.values():
            var.set(0)

        self.comment_text.delete("1.0", tk.END)

        if self.meal_id:
            wb = self.db.execute(
                "SELECT Энергия, Сытость, Настроение, "
                "ЖКТ, Комментарий FROM ДневникСамочувствия "
                "WHERE Код_приёма = ?",
                (self.meal_id,)
            )
            if wb and len(wb) > 0:
                row = wb[0]
                self.scales["Энергия"].set(row[0] or 0)
                self.scales["Сытость"].set(row[1] or 0)
                self.scales["Настроение"].set(row[2] or 0)
                self.scales["ЖКТ"].set(row[3] or 0)
                if row[4]:
                    self.comment_text.insert("1.0", row[4])

        for scale_name in self.scales:
            self._redraw_scale(scale_name)

    def _save(self):
        if not self.meal_id:
            messagebox.showwarning(
                "Ошибка",
                "За этот день нет приёма пищи.\n"
                "Сначала добавьте приём пищи."
            )
            return

        for name, var in self.scales.items():
            if var.get() == 0:
                messagebox.showwarning(
                    "Ошибка",
                    f"Выберите значение для «{name}»"
                )
                return

        date_str = self.current_date.strftime("%Y-%m-%d")
        comment = self.comment_text.get("1.0", tk.END).strip()

        existing = self.db.execute(
            "SELECT Код_записи FROM ДневникСамочувствия "
            "WHERE Код_приёма = ?",
            (self.meal_id,)
        )

        if existing and len(existing) > 0:
            self.db.execute(
                "UPDATE ДневникСамочувствия SET "
                "Энергия = ?, Сытость = ?, Настроение = ?, "
                "ЖКТ = ?, Комментарий = ?, ДатаЗаписи = ? "
                "WHERE Код_приёма = ?",
                (self.scales["Энергия"].get(),
                 self.scales["Сытость"].get(),
                 self.scales["Настроение"].get(),
                 self.scales["ЖКТ"].get(),
                 comment, date_str, self.meal_id)
            )
        else:
            self.db.execute(
                "INSERT INTO ДневникСамочувствия "
                "(Код_приёма, Код_пользователя, Энергия, Сытость, "
                "Настроение, ЖКТ, Комментарий, ДатаЗаписи) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (self.meal_id, self.user.user_id,
                 self.scales["Энергия"].get(),
                 self.scales["Сытость"].get(),
                 self.scales["Настроение"].get(),
                 self.scales["ЖКТ"].get(),
                 comment, date_str)
            )

        messagebox.showinfo("Успех", "Самочувствие сохранено")
        self.root.destroy()

    def run(self):
        self.root.wait_window()