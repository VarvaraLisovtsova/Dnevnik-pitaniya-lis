"""Экран статистики — всё скруглено, как в макете."""

import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta
import math


def rounded_rect_points(x1, y1, x2, y2, r):
    return [
        x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r,
        x2, y2 - r, x2, y2, x2 - r, y2, x1 + r, y2,
        x1, y2, x1, y2 - r, x1, y1 + r, x1, y1,
    ]


def create_rounded_rect(canvas, x1, y1, x2, y2, r, **kwargs):
    return canvas.create_polygon(
        rounded_rect_points(x1, y1, x2, y2, r),
        smooth=True, **kwargs
    )


class RoundedButton(tk.Canvas):
    def __init__(self, parent, text="", command=None,
                 bg="#7E57C2", fg="#FFFFFF",
                 hover_bg="#5E35B1", width=150, height=46,
                 radius=12, font=("TkDefaultFont", 11, "bold"),
                 border_color=None, border_width=0,
                 parent_bg="#FFFFFF"):
        super().__init__(parent, width=width, height=height,
                         bg=parent_bg, highlightthickness=0, bd=0,
                         cursor="hand2")
        self.command = command
        self.bg_color = bg
        self.hover_bg = hover_bg
        self.border_color = border_color

        create_rounded_rect(
            self, 1, 1, width - 1, height - 1, radius,
            fill=bg,
            outline=border_color if border_color else bg,
            width=border_width if border_width else 1,
            tags="shape"
        )
        self.create_text(width // 2, height // 2,
                         text=text, fill=fg, font=font)
        self.bind("<Button-1>", lambda e: command() if command else None)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _on_enter(self, e):
        outline = self.border_color if self.border_color else self.hover_bg
        self.itemconfig("shape", fill=self.hover_bg, outline=outline)

    def _on_leave(self, e):
        outline = self.border_color if self.border_color else self.bg_color
        self.itemconfig("shape", fill=self.bg_color, outline=outline)


class RoundedTile(tk.Canvas):
    """Скруглённая плитка."""

    def __init__(self, parent, width=200, height=90,
                 bg="#FFFFFF", border_color="#D0D0D0",
                 parent_bg="#FFFFFF", radius=12):
        super().__init__(parent, width=width, height=height,
                         bg=parent_bg, highlightthickness=0, bd=0)
        self.bg_color = bg
        self.radius = radius
        self.border_color = border_color

        create_rounded_rect(
            self, 1, 1, width - 1, height - 1, radius,
            fill=bg, outline=border_color, width=1
        )


class StatisticsWindow:
    BG_MAIN = "#F0F0F0"
    BG_CARD = "#FFFFFF"
    BG_INPUT = "#E0E0E0"
    BG_BUTTON = "#7E57C2"
    BG_BUTTON_HOVER = "#5E35B1"
    BG_ACCENT = "#7E57C2"
    BG_ACCENT_LIGHT = "#EDE7F6"
    BG_LIGHT_GRAY = "#F5F5F5"
    FG_TEXT = "#333333"
    FG_MUTED = "#9E9E9E"
    FG_WHITE = "#FFFFFF"
    FG_ACCENT = "#7E57C2"
    FG_GREEN = "#4CAF50"
    FG_RED = "#E53935"

    def __init__(self, db, user):
        self.db = db
        self.user = user
        self.root = tk.Toplevel()
        self.root.title("Статистика")
        self.root.geometry("980x920")
        self.root.configure(bg=self.BG_MAIN)
        self.root.resizable(False, False)

        self.period_days = tk.IntVar(value=7)
        self.date_from = tk.StringVar()
        self.date_to = tk.StringVar()

        self.stats = {}
        self.daily_data = []
        self.weight_data = []
        self.water_total = 0
        self.norm_cal = 2200

        self._set_default_dates()
        self._build_ui()
        self._load_stats()

    def _set_default_dates(self):
        today = datetime.now()
        start = today - timedelta(days=6)
        self.date_from.set(start.strftime("%d.%m.%Y"))
        self.date_to.set(today.strftime("%d.%m.%Y"))

    def _parse_date(self, s):
        try:
            return datetime.strptime(s, "%d.%m.%Y")
        except Exception:
            return datetime.now()

    def _build_ui(self):
        card = tk.Frame(self.root, bg=self.BG_CARD)
        card.pack(fill="both", expand=True, padx=20, pady=20)

        # ===== ЗАГОЛОВОК =====
        head = tk.Frame(card, bg=self.BG_CARD)
        head.pack(fill="x", padx=25, pady=(20, 15))

        tk.Label(head, text="Статистика",
                 font=("TkDefaultFont", 15, "bold"),
                 bg=self.BG_CARD, fg=self.FG_TEXT).pack(side="left")

        close = tk.Label(head, text="✕",
                         font=("TkDefaultFont", 18, "bold"),
                         bg=self.BG_CARD, fg=self.FG_RED,
                         cursor="hand2")
        close.pack(side="right")
        close.bind("<Button-1>", lambda e: self.root.destroy())

        tk.Frame(card, bg="#E0E0E0", height=1).pack(fill="x", padx=25)

        # ===== ПЕРИОД =====
        tk.Label(card, text="Период",
                 font=("TkDefaultFont", 11, "bold"),
                 bg=self.BG_CARD, fg=self.FG_TEXT).pack(anchor="w",
                                                        padx=25,
                                                        pady=(15, 5))

        period_row = tk.Frame(card, bg=self.BG_CARD)
        period_row.pack(fill="x", padx=25, pady=(0, 5))

        # Кнопки периодов
        self.period_buttons = {}
        for days, label in [(7, "7 дней"), (30, "30 дней"),
                            (90, "90 дней")]:
            btn = RoundedButton(
                period_row, text=label,
                width=110, height=38, radius=10,
                bg=self.BG_CARD, fg=self.FG_TEXT,
                hover_bg=self.BG_ACCENT_LIGHT,
                font=("TkDefaultFont", 10),
                border_color="#C0C0C0", border_width=1,
                parent_bg=self.BG_CARD,
                command=lambda d=days: self._set_period(d)
            )
            btn.pack(side="left", padx=(0, 6))
            self.period_buttons[days] = btn

        tk.Label(period_row, text="С",
                 font=("TkDefaultFont", 9),
                 bg=self.BG_CARD, fg=self.FG_MUTED).pack(side="left",
                                                         padx=(15, 5))

        from_canvas = tk.Canvas(period_row, width=180, height=40,
                                bg=self.BG_CARD, highlightthickness=0)
        from_canvas.pack(side="left", padx=(0, 10))
        create_rounded_rect(from_canvas, 1, 1, 179, 39, 10,
                            fill=self.BG_INPUT, outline="#C0C0C0",
                            width=1)
        tk.Entry(from_canvas, textvariable=self.date_from,
                 font=("TkDefaultFont", 11), bg=self.BG_INPUT,
                 bd=0, justify="center").place(x=10, y=8,
                                                width=130, height=22)
        from_canvas.create_text(160, 20, text="📅",
                                font=("TkDefaultFont", 12))

        tk.Label(period_row, text="По",
                 font=("TkDefaultFont", 9),
                 bg=self.BG_CARD, fg=self.FG_MUTED).pack(side="left",
                                                         padx=(0, 5))

        to_canvas = tk.Canvas(period_row, width=180, height=40,
                              bg=self.BG_CARD, highlightthickness=0)
        to_canvas.pack(side="left", padx=(0, 10))
        create_rounded_rect(to_canvas, 1, 1, 179, 39, 10,
                            fill=self.BG_INPUT, outline="#C0C0C0",
                            width=1)
        tk.Entry(to_canvas, textvariable=self.date_to,
                 font=("TkDefaultFont", 11), bg=self.BG_INPUT,
                 bd=0, justify="center").place(x=10, y=8,
                                                width=130, height=22)
        to_canvas.create_text(160, 20, text="📅",
                              font=("TkDefaultFont", 12))

        self.range_label = tk.Label(period_row, text="",
                                    font=("TkDefaultFont", 9),
                                    bg=self.BG_CARD, fg=self.FG_MUTED)
        self.range_label.pack(side="right")

        self._highlight_period_button(7)

        # ===== КАЛОРИИ И КБЖУ =====
        tk.Label(card, text="Калории и КБЖУ",
                 font=("TkDefaultFont", 11, "bold"),
                 bg=self.BG_CARD, fg=self.FG_TEXT).pack(anchor="w",
                                                        padx=25,
                                                        pady=(15, 5))

        tk.Label(card, text="Средние значения за день",
                 font=("TkDefaultFont", 9),
                 bg=self.BG_CARD, fg=self.FG_MUTED).pack(anchor="e",
                                                         padx=25)

        kbzhu_row = tk.Frame(card, bg=self.BG_CARD)
        kbzhu_row.pack(fill="x", padx=25, pady=(5, 15))

        self.kbzhu_tiles = {}
        for key, title in [
            ("cal", "Калории"),
            ("p", "Белки"),
            ("f", "Жиры"),
            ("c", "Углеводы"),
        ]:
            tile = RoundedTile(kbzhu_row, width=200, height=95,
                               bg=self.BG_CARD,
                               border_color="#D0D0D0",
                               parent_bg=self.BG_CARD, radius=12)
            tile.pack(side="left", padx=(0, 8), fill="x", expand=True)

            tk.Label(tile, text=title,
                     font=("TkDefaultFont", 10),
                     bg=self.BG_CARD, fg=self.FG_MUTED
                     ).place(x=15, y=10)

            value_lbl = tk.Label(tile, text="—",
                                 font=("TkDefaultFont", 18, "bold"),
                                 bg=self.BG_CARD, fg=self.FG_TEXT)
            value_lbl.place(x=15, y=32)

            hint_lbl = tk.Label(tile, text="",
                                font=("TkDefaultFont", 9),
                                bg=self.BG_CARD, fg=self.FG_MUTED)
            hint_lbl.place(x=15, y=65)

            self.kbzhu_tiles[key] = (value_lbl, hint_lbl)

        # ===== ГРАФИК + БОКОВЫЕ ПЛИТКИ =====
        mid_row = tk.Frame(card, bg=self.BG_CARD)
        mid_row.pack(fill="x", padx=25, pady=(0, 15))

        chart_frame = RoundedTile(mid_row, width=620, height=280,
                                  bg=self.BG_CARD,
                                  border_color="#D0D0D0",
                                  parent_bg=self.BG_CARD, radius=12)
        chart_frame.pack(side="left", fill="both", expand=True)

        tk.Label(chart_frame, text="Калории по дням",
                 font=("TkDefaultFont", 11, "bold"),
                 bg=self.BG_CARD, fg=self.FG_TEXT
                 ).place(x=15, y=12)

        self.chart_legend = tk.Label(
            chart_frame, text="", font=("TkDefaultFont", 9),
            bg=self.BG_CARD, fg=self.FG_ACCENT
        )
        self.chart_legend.place(x=500, y=15)

        self.chart_canvas = tk.Canvas(chart_frame, bg=self.BG_CARD,
                                      highlightthickness=0)
        self.chart_canvas.place(x=15, y=45, width=590, height=220)
        self.chart_canvas.bind("<Configure>",
                               lambda e: self._draw_chart())

        # Правая колонка
        side_col = tk.Frame(mid_row, bg=self.BG_CARD, width=280)
        side_col.pack(side="right", fill="y", padx=(15, 0))
        side_col.pack_propagate(False)

        # Вес
        weight_tile = RoundedTile(side_col, width=280, height=130,
                                  bg=self.BG_CARD,
                                  border_color="#D0D0D0",
                                  parent_bg=self.BG_CARD, radius=12)
        weight_tile.pack(fill="x", pady=(0, 10))

        tk.Label(weight_tile, text="Вес",
                 font=("TkDefaultFont", 10),
                 bg=self.BG_CARD, fg=self.FG_MUTED
                 ).place(x=15, y=12)

        self.weight_value = tk.Label(
            weight_tile, text="—",
            font=("TkDefaultFont", 16, "bold"),
            bg=self.BG_CARD, fg=self.FG_TEXT
        )
        self.weight_value.place(x=15, y=35)

        self.weight_delta = tk.Label(
            weight_tile, text="",
            font=("TkDefaultFont", 10, "bold"),
            bg=self.BG_CARD, fg=self.FG_ACCENT
        )
        self.weight_delta.place(x=110, y=40)

        self.weight_period = tk.Label(
            weight_tile, text="",
            font=("TkDefaultFont", 9),
            bg=self.BG_CARD, fg=self.FG_MUTED
        )
        self.weight_period.place(x=15, y=65)

        self.weight_canvas = tk.Canvas(weight_tile, bg=self.BG_CARD,
                                       highlightthickness=0)
        self.weight_canvas.place(x=15, y=85, width=250, height=35)
        self.weight_canvas.bind("<Configure>",
                                lambda e: self._draw_weight_chart())

        # Вода
        water_tile = RoundedTile(side_col, width=280, height=130,
                                 bg=self.BG_CARD,
                                 border_color="#D0D0D0",
                                 parent_bg=self.BG_CARD, radius=12)
        water_tile.pack(fill="x")

        tk.Label(water_tile, text="Вода",
                 font=("TkDefaultFont", 10),
                 bg=self.BG_CARD, fg=self.FG_MUTED
                 ).place(x=15, y=12)

        self.water_value = tk.Label(
            water_tile, text="—",
            font=("TkDefaultFont", 16, "bold"),
            bg=self.BG_CARD, fg=self.FG_TEXT
        )
        self.water_value.place(x=15, y=35)

        self.water_delta = tk.Label(
            water_tile, text="",
            font=("TkDefaultFont", 10, "bold"),
            bg=self.BG_CARD, fg=self.FG_ACCENT
        )
        self.water_delta.place(x=110, y=40)

        self.water_period = tk.Label(
            water_tile, text="",
            font=("TkDefaultFont", 9),
            bg=self.BG_CARD, fg=self.FG_MUTED
        )
        self.water_period.place(x=15, y=65)

        self.water_canvas = tk.Canvas(water_tile, bg=self.BG_CARD,
                                      highlightthickness=0)
        self.water_canvas.place(x=15, y=85, width=250, height=35)
        self.water_canvas.bind("<Configure>",
                               lambda e: self._draw_water_chart())

        # ===== КЛЮЧЕВЫЕ СРЕДНИЕ =====
        tk.Label(card, text="Ключевые средние",
                 font=("TkDefaultFont", 11, "bold"),
                 bg=self.BG_CARD, fg=self.FG_TEXT).pack(anchor="w",
                                                        padx=25,
                                                        pady=(0, 5))

        key_row = tk.Frame(card, bg=self.BG_CARD)
        key_row.pack(fill="x", padx=25, pady=(0, 15))

        self.key_tiles = {}
        for key, title in [
            ("deficit", "Дефицит"),
            ("meals", "Приёмов пищи"),
            ("water_target", "Вода по цели"),
            ("weight_change", "Изменение веса"),
        ]:
            tile = RoundedTile(key_row, width=200, height=95,
                               bg=self.BG_LIGHT_GRAY,
                               border_color=self.BG_LIGHT_GRAY,
                               parent_bg=self.BG_CARD, radius=12)
            tile.pack(side="left", padx=(0, 8), fill="x", expand=True)

            tk.Label(tile, text=title,
                     font=("TkDefaultFont", 9),
                     bg=self.BG_LIGHT_GRAY, fg=self.FG_MUTED
                     ).place(x=15, y=10)

            value_lbl = tk.Label(tile, text="—",
                                 font=("TkDefaultFont", 13, "bold"),
                                 bg=self.BG_LIGHT_GRAY, fg=self.FG_TEXT)
            value_lbl.place(x=15, y=35)

            hint_lbl = tk.Label(tile, text="",
                                font=("TkDefaultFont", 8),
                                bg=self.BG_LIGHT_GRAY, fg=self.FG_MUTED)
            hint_lbl.place(x=15, y=65)

            self.key_tiles[key] = (value_lbl, hint_lbl)

        # ===== КНОПКИ =====
        btns = tk.Frame(card, bg=self.BG_CARD)
        btns.pack(fill="x", padx=25, pady=(0, 20))

        RoundedButton(btns, text="Закрыть",
                      width=150, height=46, radius=12,
                      bg=self.BG_CARD, fg=self.FG_TEXT,
                      hover_bg="#E0E0E0",
                      font=("TkDefaultFont", 11),
                      border_color="#000000", border_width=1,
                      parent_bg=self.BG_CARD,
                      command=self.root.destroy
                      ).pack(side="left", padx=(0, 12))

        RoundedButton(btns, text="Экспорт",
                      width=150, height=46, radius=12,
                      bg=self.BG_BUTTON, fg=self.FG_WHITE,
                      hover_bg=self.BG_BUTTON_HOVER,
                      font=("TkDefaultFont", 11, "bold"),
                      parent_bg=self.BG_CARD,
                      command=self._export
                      ).pack(side="left")

    def _set_period(self, days):
        self.period_days.set(days)
        today = datetime.now()
        start = today - timedelta(days=days - 1)
        self.date_from.set(start.strftime("%d.%m.%Y"))
        self.date_to.set(today.strftime("%d.%m.%Y"))
        self._highlight_period_button(days)
        self._load_stats()

    def _highlight_period_button(self, days):
        for d, btn in self.period_buttons.items():
            if d == days:
                btn.bg_color = self.BG_ACCENT
                btn.itemconfig("shape", fill=self.BG_ACCENT,
                               outline=self.BG_ACCENT)
                for item in btn.find_all():
                    if btn.type(item) == "text":
                        btn.itemconfig(item, fill=self.FG_WHITE)
            else:
                btn.bg_color = self.BG_CARD
                btn.itemconfig("shape", fill=self.BG_CARD,
                               outline="#C0C0C0")
                for item in btn.find_all():
                    if btn.type(item) == "text":
                        btn.itemconfig(item, fill=self.FG_TEXT)

    def _load_stats(self):
        """Загружает статистику из БД."""
        dt_from = self._parse_date(self.date_from.get())
        dt_to = self._parse_date(self.date_to.get())

        if dt_from > dt_to:
            dt_from, dt_to = dt_to, dt_from

        date_from_str = dt_from.strftime("%Y-%m-%d")
        date_to_str = dt_to.strftime("%Y-%m-%d")

        days_total = (dt_to - dt_from).days + 1

        self.range_label.config(
            text=f"{dt_from.strftime('%d.%m.%Y')} — "
                 f"{dt_to.strftime('%d.%m.%Y')}"
        )

        # === КБЖУ ===
        result = self.db.execute("""
            SELECT
                COALESCE(SUM(сп.Вес_г * п.Калории_на_100г / 100), 0),
                COALESCE(SUM(сп.Вес_г * п.Белки_на_100г / 100), 0),
                COALESCE(SUM(сп.Вес_г * п.Жиры_на_100г / 100), 0),
                COALESCE(SUM(сп.Вес_г * п.Углеводы_на_100г / 100), 0),
                COUNT(DISTINCT пр.ДатаПриёма)
            FROM СоставПриёма сп
            JOIN Продукты п ON п.Код_продукта = сп.Код_продукта
            JOIN ПриёмыПищи пр ON пр.Код_приёма = сп.Код_приёма
            WHERE пр.Код_пользователя = ?
              AND пр.ДатаПриёма >= ?
              AND пр.ДатаПриёма <= ?
        """, (self.user.user_id, date_from_str, date_to_str))

        if result and len(result) > 0:
            row = result[0]
            total_cal = row[0] or 0
            total_p = row[1] or 0
            total_f = row[2] or 0
            total_c = row[3] or 0
            days_with_data = row[4] or 0
        else:
            total_cal = total_p = total_f = total_c = 0
            days_with_data = 0

        days_for_avg = days_with_data if days_with_data > 0 else 1
        avg_cal = int(total_cal / days_for_avg)
        avg_p = int(total_p / days_for_avg)
        avg_f = int(total_f / days_for_avg)
        avg_c = int(total_c / days_for_avg)

        # Нормы
        goal = self.db.execute(
            "SELECT НормаКалорий, НормаБелков, НормаЖиров, "
            "НормаУглеводов FROM Цели "
            "WHERE Код_пользователя = ? "
            "ORDER BY Код_цели DESC LIMIT 1",
            (self.user.user_id,)
        )
        if goal and len(goal) > 0:
            norm_cal, norm_p, norm_f, norm_c = goal[0]
        else:
            norm_cal, norm_p, norm_f, norm_c = 2810, 175, 93, 316

        self.norm_cal = norm_cal

        self.kbzhu_tiles["cal"][0].config(text=str(avg_cal))
        pct = min(int(avg_cal / norm_cal * 100), 100) if norm_cal else 0
        self.kbzhu_tiles["cal"][1].config(
            text=f"{pct}% цели", fg=self.FG_ACCENT
        )
        self.kbzhu_tiles["p"][0].config(text=str(avg_p))
        self.kbzhu_tiles["p"][1].config(text=f"цель {norm_p} г")
        self.kbzhu_tiles["f"][0].config(text=str(avg_f))
        self.kbzhu_tiles["f"][1].config(text=f"цель {norm_f} г")
        self.kbzhu_tiles["c"][0].config(text=str(avg_c))
        self.kbzhu_tiles["c"][1].config(text=f"цель {norm_c} г")

        # === Калории по дням ===
        daily = self.db.execute("""
            SELECT пр.ДатаПриёма,
                   SUM(сп.Вес_г * п.Калории_на_100г / 100)
            FROM СоставПриёма сп
            JOIN Продукты п ON п.Код_продукта = сп.Код_продукта
            JOIN ПриёмыПищи пр ON пр.Код_приёма = сп.Код_приёма
            WHERE пр.Код_пользователя = ?
              AND пр.ДатаПриёма >= ?
              AND пр.ДатаПриёма <= ?
            GROUP BY пр.ДатаПриёма
            ORDER BY пр.ДатаПриёма
        """, (self.user.user_id, date_from_str, date_to_str))

        self.daily_data = []
        if daily:
            for d in daily:
                self.daily_data.append((d[0], int(d[1])))

        try:
            self._draw_chart()
        except Exception as e:
            print(f"Ошибка графика калорий: {e}")

        # === Вес ===
        weight_data = self.db.execute("""
            SELECT ДатаЗаписи, ВесКг
            FROM ИсторияВеса
            WHERE Код_пользователя = ?
            ORDER BY ДатаЗаписи
        """, (self.user.user_id,))

        self.weight_data = []
        if weight_data and len(weight_data) > 0:
            self.weight_data = weight_data
            first_w = weight_data[0][1]
            last_w = weight_data[-1][1]
            delta = last_w - first_w

            self.weight_value.config(text=f"{last_w:.1f} кг")
            sign = "+" if delta >= 0 else ""
            color = self.FG_RED if delta > 0 else self.FG_GREEN
            self.weight_delta.config(
                text=f"{sign}{delta:.1f} кг", fg=color
            )
            self.weight_period.config(
                text=f"за {self.period_days.get()} дней"
            )
        else:
            self.weight_value.config(text="—")
            self.weight_delta.config(text="")
            self.weight_period.config(text="нет данных")

        try:
            self._draw_weight_chart()
        except Exception as e:
            print(f"Ошибка графика веса: {e}")

        # === Вода ===
        water_result = self.db.execute("""
            SELECT COALESCE(SUM(КоличествоМл), 0),
                   COUNT(DISTINCT ДатаЗаписи)
            FROM УчётВоды
            WHERE Код_пользователя = ?
              AND ДатаЗаписи >= ?
              AND ДатаЗаписи <= ?
        """, (self.user.user_id, date_from_str, date_to_str))

        if water_result and len(water_result) > 0:
            total_water = water_result[0][0] or 0
            days_water = water_result[0][1] or 0
        else:
            total_water = 0
            days_water = 0

        self.water_total = total_water

        if days_water > 0:
            avg_water = total_water / days_water / 1000
            self.water_value.config(text=f"{avg_water:.2f} л")
            self.water_delta.config(
                text=f"+{avg_water:.1f} л", fg=self.FG_ACCENT
            )
            self.water_period.config(text="среднее в день")
        else:
            self.water_value.config(text="0,00 л")
            self.water_delta.config(text="")
            self.water_period.config(text="нет данных")

        try:
            self._draw_water_chart()
        except Exception as e:
            print(f"Ошибка графика воды: {e}")

        # === Ключевые средние ===
        deficit = avg_cal - norm_cal
        self.key_tiles["deficit"][0].config(text=f"{deficit} ккал")
        self.key_tiles["deficit"][1].config(text="в среднем за день")

        meals_count_result = self.db.execute("""
            SELECT COUNT(*) FROM ПриёмыПищи
            WHERE Код_пользователя = ?
              AND ДатаПриёма >= ?
              AND ДатаПриёма <= ?
        """, (self.user.user_id, date_from_str, date_to_str))
        meals_total = (meals_count_result[0][0]
                       if meals_count_result else 0)
        avg_meals = (round(meals_total / days_total, 1)
                     if days_total else 0)
        self.key_tiles["meals"][0].config(text=f"{avg_meals:.0f}")
        self.key_tiles["meals"][1].config(text="из 4 запланированных")

        norm_water_total = 2000 * days_total
        water_pct = (min(int(total_water / norm_water_total * 100), 100)
                     if norm_water_total else 0)
        self.key_tiles["water_target"][0].config(text=f"{water_pct}%")
        self.key_tiles["water_target"][1].config(
            text=f"{days_water} дней из {days_total}"
        )

        if len(self.weight_data) >= 2:
            delta_w = self.weight_data[-1][1] - self.weight_data[0][1]
            sign = "+" if delta_w >= 0 else ""
            self.key_tiles["weight_change"][0].config(
                text=f"{sign}{delta_w:.1f} кг"
            )
            if abs(delta_w) < 0.5:
                hint = "устойчивый темп"
            elif delta_w < 0:
                hint = "снижение"
            else:
                hint = "набор"
            self.key_tiles["weight_change"][1].config(text=hint)
        else:
            self.key_tiles["weight_change"][0].config(text="—")
            self.key_tiles["weight_change"][1].config(text="нет данных")

    def _draw_chart(self):
        """Рисует график калорий по дням."""
        canvas = self.chart_canvas
        canvas.delete("all")

        canvas.update_idletasks()
        width = canvas.winfo_width()
        height = canvas.winfo_height()
        if width <= 10 or height <= 10:
            return

        self.chart_legend.config(text=f"цель {self.norm_cal} ккал")

        if not self.daily_data:
            canvas.create_text(
                width // 2, height // 2,
                text="Нет данных за период",
                fill=self.FG_MUTED,
                font=("TkDefaultFont", 10)
            )
            return

        pad_left = 50
        pad_right = 20
        pad_top = 20
        pad_bottom = 40

        chart_w = width - pad_left - pad_right
        chart_h = height - pad_top - pad_bottom

        max_val = max((d[1] for d in self.daily_data), default=1)
        max_val = max(max_val, self.norm_cal) * 1.15

        goal_y = pad_top + chart_h * (1 - self.norm_cal / max_val)
        canvas.create_line(
            pad_left, goal_y, width - pad_right, goal_y,
            fill="#BDBDBD", dash=(3, 3)
        )

        n = len(self.daily_data)
        step = chart_w / n
        bar_w = max(25, int(step * 0.55))

        days_short = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]

        for i, (date_str, value) in enumerate(self.daily_data):
            x_center = pad_left + step * i + step / 2
            bar_h = chart_h * (value / max_val) if max_val else 0

            x1 = x_center - bar_w / 2
            x2 = x_center + bar_w / 2
            y1 = pad_top + chart_h - bar_h
            y2 = pad_top + chart_h

            fill_color = (self.BG_ACCENT if i == n - 1
                          else "#D1C4E9")

            create_rounded_rect(
                canvas, x1, y1, x2, y2, 4,
                fill=fill_color, outline=fill_color
            )

            canvas.create_text(
                x_center, y1 - 10,
                text=str(value), fill=self.FG_TEXT,
                font=("TkDefaultFont", 8)
            )

            try:
                dt = datetime.strptime(date_str, "%Y-%m-%d")
                day_name = days_short[dt.weekday()]
            except Exception:
                day_name = date_str[-5:]

            canvas.create_text(
                x_center, pad_top + chart_h + 15,
                text=day_name, fill=self.FG_MUTED,
                font=("TkDefaultFont", 9)
            )

    def _draw_weight_chart(self):
        """Рисует линию веса."""
        canvas = self.weight_canvas
        canvas.delete("all")

        canvas.update_idletasks()
        width = canvas.winfo_width()
        height = canvas.winfo_height()
        if width <= 10 or height <= 10:
            return

        if not self.weight_data or len(self.weight_data) < 2:
            return

        values = [w[1] for w in self.weight_data[-14:]]
        if len(values) < 2:
            return

        min_v = min(values)
        max_v = max(values)
        if max_v == min_v:
            max_v += 1

        pad = 4
        chart_w = width - 2 * pad
        chart_h = height - 2 * pad

        points = []
        for i, v in enumerate(values):
            x = pad + chart_w * i / (len(values) - 1)
            y = pad + chart_h * (1 - (v - min_v) / (max_v - min_v))
            points.append((x, y))

        for i in range(len(points) - 1):
            canvas.create_line(
                points[i][0], points[i][1],
                points[i + 1][0], points[i + 1][1],
                fill=self.FG_ACCENT, width=2, smooth=True
            )

    def _draw_water_chart(self):
        """Рисует волнистую линию воды."""
        canvas = self.water_canvas
        canvas.delete("all")

        canvas.update_idletasks()
        width = canvas.winfo_width()
        height = canvas.winfo_height()
        if width <= 10 or height <= 10:
            return

        if self.water_total == 0:
            return

        pad = 4
        chart_w = width - 2 * pad
        chart_h = height - 2 * pad

        points = []
        steps = 30
        for i in range(steps + 1):
            x = pad + chart_w * i / steps
            y = (pad + chart_h * 0.5 +
                 math.sin(i * 0.5) * chart_h * 0.25)
            points.append((x, y))

        for i in range(len(points) - 1):
            canvas.create_line(
                points[i][0], points[i][1],
                points[i + 1][0], points[i + 1][1],
                fill=self.FG_ACCENT, width=2, smooth=True
            )

    def _export(self):
        messagebox.showinfo(
            "Экспорт",
            "Статистика экспортирована в PDF (демо)"
        )

    def run(self):
        self.root.wait_window()