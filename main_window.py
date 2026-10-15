"""Главное окно — дашборд."""

import tkinter as tk
from datetime import datetime, timedelta


class MainWindow:
    """Главное окно приложения."""

    BG_MAIN = "#EDEDED"
    BG_CARD = "#FFFFFF"
    BG_ACCENT = "#7E57C2"
    BG_ACCENT_LIGHT = "#EDE7F6"
    FG_TEXT = "#333333"
    FG_MUTED = "#9E9E9E"
    FG_ACCENT = "#7E57C2"
    BORDER = "#D0D0D0"

    def __init__(self, db, user):
        self.db = db
        self.user = user
        self.current_date = datetime.now()
        self.root = tk.Tk()
        self.root.title("Дневник питания")
        self.root.geometry("1280x720")
        self.root.configure(bg=self.BG_MAIN)
        self._build_ui()

    def _build_ui(self):
        # ===== ВЕРХНЯЯ ПАНЕЛЬ =====
        header = tk.Frame(self.root, bg=self.BG_CARD, height=80)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(header, text="Дневник питания",
                 font=("TkDefaultFont", 17, "bold"),
                 bg=self.BG_CARD, fg=self.FG_TEXT).pack(side="left", padx=40)

        user_block = tk.Frame(header, bg=self.BG_CARD)
        user_block.pack(side="right", padx=40)
        tk.Label(user_block, text=f"Пользователь: {self.user.login}",
                 font=("TkDefaultFont", 11), bg=self.BG_CARD,
                 fg=self.FG_TEXT).pack(anchor="e")
        tk.Label(user_block, text="Личный профиль",
                 font=("TkDefaultFont", 9), bg=self.BG_CARD,
                 fg=self.FG_MUTED).pack(anchor="e")

        tk.Frame(self.root, bg=self.BORDER, height=1).pack(fill="x")

        # ===== ОСНОВНОЙ БЛОК =====
        main = tk.Frame(self.root, bg=self.BG_MAIN)
        main.pack(fill="both", expand=True, padx=30, pady=20)

        # ---------- ЛЕВАЯ ЧАСТЬ ----------
        left = tk.Frame(main, bg=self.BG_MAIN)
        left.pack(side="left", fill="both", expand=True)

        # Дата с листанием
        date_frame = tk.Frame(left, bg=self.BG_CARD, bd=0,
                              highlightthickness=1,
                              highlightbackground=self.BORDER)
        date_frame.pack(fill="x", pady=(0, 15))

        inner_date = tk.Frame(date_frame, bg=self.BG_CARD)
        inner_date.pack(fill="x", padx=15, pady=10)

        tk.Button(inner_date, text="‹",
                  font=("TkDefaultFont", 14),
                  bg=self.BG_CARD, fg=self.FG_TEXT,
                  bd=0, cursor="hand2",
                  command=self._prev_day).pack(side="left", padx=(0, 8))

        self.date_label = tk.Label(inner_date, text="",
                                   font=("TkDefaultFont", 11, "bold"),
                                   bg=self.BG_CARD, fg=self.FG_TEXT)
        self.date_label.pack(side="left", padx=10)

        tk.Button(inner_date, text="›",
                  font=("TkDefaultFont", 14),
                  bg=self.BG_CARD, fg=self.FG_TEXT,
                  bd=0, cursor="hand2",
                  command=self._next_day).pack(side="left", padx=(8, 0))

        self._update_date_label()

        # Плитки
        self.tiles_frame = tk.Frame(left, bg=self.BG_MAIN)
        self.tiles_frame.pack(fill="both", expand=True)

        self._refresh_tiles()

        # Нижняя панель «Прогресс дня»
        bottom = tk.Frame(left, bg=self.BG_CARD, bd=0,
                          highlightthickness=1,
                          highlightbackground=self.BORDER)
        bottom.pack(fill="x", pady=(15, 0))

        inner_bottom = tk.Frame(bottom, bg=self.BG_CARD)
        inner_bottom.pack(fill="x", padx=30, pady=20)

        tk.Label(inner_bottom, text="Прогресс дня",
                 font=("TkDefaultFont", 11, "bold"),
                 bg=self.BG_CARD, fg=self.FG_TEXT).pack(side="left",
                                                        padx=(0, 30))

        self.progress_frame = tk.Frame(inner_bottom, bg=self.BG_CARD)
        self.progress_frame.pack(side="left", fill="x", expand=True)

        self._refresh_bottom()

        # ---------- ПРАВАЯ ЧАСТЬ ----------
        right = tk.Frame(main, bg=self.BG_CARD, bd=0,
                         highlightthickness=1,
                         highlightbackground=self.BORDER,
                         width=320)
        right.pack(side="right", fill="y", padx=(20, 0))
        right.pack_propagate(False)

        inner_right = tk.Frame(right, bg=self.BG_CARD)
        inner_right.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(inner_right, text="Быстрые действия",
                 font=("TkDefaultFont", 13, "bold"),
                 bg=self.BG_CARD, fg=self.FG_TEXT).pack(anchor="w")
        tk.Label(inner_right, text="Управление дневником",
                 font=("TkDefaultFont", 9),
                 bg=self.BG_CARD, fg=self.FG_MUTED).pack(anchor="w",
                                                         pady=(0, 15))

        actions = [
            ("Добавить приём пищи", "Записать еду или продукт",
             self._open_add_meal, True),
            ("Добавить воду", "Обновить объём за день",
             self._open_add_water, False),
            ("Самочувствие", "Отметить состояние",
             self._open_wellbeing, False),
            ("Подбор меню", "Составить рацион",
             self._open_menu, False),
            ("Прогноз цели", "Посмотреть динамику",
             self._open_forecast, False),
            ("Статистика", "Открыть аналитику",
             self._open_stats, False),
        ]

        for title, subtitle, cmd, primary in actions:
            self._create_action(inner_right, title, subtitle, cmd, primary)

    def _update_date_label(self):
        today = datetime.now().date()
        current = self.current_date.date()
        if current == today:
            text = f"Сегодня, {current.strftime('%d.%m.%Y')}"
        elif current == today - timedelta(days=1):
            text = f"Вчера, {current.strftime('%d.%m.%Y')}"
        elif current == today + timedelta(days=1):
            text = f"Завтра, {current.strftime('%d.%m.%Y')}"
        else:
            text = current.strftime("%d.%m.%Y")
        self.date_label.config(text=text)

    def _prev_day(self):
        self.current_date -= timedelta(days=1)
        self._update_date_label()
        self._refresh_tiles()
        self._refresh_bottom()

    def _next_day(self):
        self.current_date += timedelta(days=1)
        self._update_date_label()
        self._refresh_tiles()
        self._refresh_bottom()

    def _refresh_tiles(self):
        for w in self.tiles_frame.winfo_children():
            w.destroy()

        tiles_data = self._load_day_data()
        for i, tile in enumerate(tiles_data):
            row, col = divmod(i, 3)
            self._create_tile(self.tiles_frame, tile, row, col)

    def _refresh_bottom(self):
        for w in self.progress_frame.winfo_children():
            w.destroy()

        tiles = self._load_day_data()
        for tile in tiles[:5]:
            col = tk.Frame(self.progress_frame, bg=self.BG_CARD)
            col.pack(side="left", padx=25)
            tk.Label(col, text=f"{tile['percent']}%",
                     font=("TkDefaultFont", 18, "bold"),
                     bg=self.BG_CARD, fg=self.FG_ACCENT).pack()
            tk.Label(col, text=tile["title"].capitalize(),
                     font=("TkDefaultFont", 9),
                     bg=self.BG_CARD, fg=self.FG_MUTED).pack()

    def _load_day_data(self):
        date_str = self.current_date.strftime("%Y-%m-%d")

        cal = protein = fat = carbs = 0
        water = 0
        weight = 0

        try:
            result = self.db.execute("""
                SELECT
                    COALESCE(SUM(сп.Вес_г * п.Калории_на_100г / 100), 0),
                    COALESCE(SUM(сп.Вес_г * п.Белки_на_100г / 100), 0),
                    COALESCE(SUM(сп.Вес_г * п.Жиры_на_100г / 100), 0),
                    COALESCE(SUM(сп.Вес_г * п.Углеводы_на_100г / 100), 0)
                FROM СоставПриёма сп
                JOIN Продукты п ON п.Код_продукта = сп.Код_продукта
                JOIN ПриёмыПищи пр ON пр.Код_приёма = сп.Код_приёма
                WHERE пр.Код_пользователя = ? AND пр.ДатаПриёма = ?
            """, (self.user.user_id, date_str))
            if result:
                cal, protein, fat, carbs = result[0]

            water_result = self.db.execute(
                "SELECT COALESCE(SUM(КоличествоМл), 0) FROM УчётВоды "
                "WHERE Код_пользователя = ? AND ДатаЗаписи = ?",
                (self.user.user_id, date_str)
            )
            if water_result:
                water = int(water_result[0][0])

            weight_result = self.db.execute(
                "SELECT ВесКг FROM ИсторияВеса "
                "WHERE Код_пользователя = ? "
                "ORDER BY ДатаЗаписи DESC LIMIT 1",
                (self.user.user_id,)
            )
            if weight_result:
                weight = weight_result[0][0]
        except Exception as e:
            print(f"Ошибка загрузки: {e}")

        # Нормы из цели
        norm_cal, norm_protein, norm_fat, norm_carbs = 2200, 150, 70, 220
        try:
            goal_result = self.db.execute(
                "SELECT НормаКалорий, НормаБелков, НормаЖиров, НормаУглеводов "
                "FROM Цели WHERE Код_пользователя = ? "
                "ORDER BY Код_цели DESC LIMIT 1",
                (self.user.user_id,)
            )
            if goal_result:
                norm_cal, norm_protein, norm_fat, norm_carbs = goal_result[0]
        except Exception as e:
            print(f"Ошибка цели: {e}")

        norm_water = int(weight * 30) if weight else 2000

        return [
            {"title": "КАЛОРИИ", "value": int(cal),
             "norm": norm_cal, "unit": "ккал",
             "hint": f"Осталось {max(int(norm_cal - cal), 0)} ккал",
             "percent": min(int(cal / norm_cal * 100), 100) if norm_cal else 0},
            {"title": "БЕЛКИ", "value": int(protein),
             "norm": norm_protein, "unit": "г",
             "hint": f"Осталось {max(int(norm_protein - protein), 0)} г",
             "percent": min(int(protein / norm_protein * 100), 100) if norm_protein else 0},
            {"title": "ЖИРЫ", "value": int(fat),
             "norm": norm_fat, "unit": "г",
             "hint": f"Осталось {max(int(norm_fat - fat), 0)} г",
             "percent": min(int(fat / norm_fat * 100), 100) if norm_fat else 0},
            {"title": "УГЛЕВОДЫ", "value": int(carbs),
             "norm": norm_carbs, "unit": "г",
             "hint": f"Осталось {max(int(norm_carbs - carbs), 0)} г",
             "percent": min(int(carbs / norm_carbs * 100), 100) if norm_carbs else 0},
            {"title": "ВОДА", "value": water,
             "norm": norm_water, "unit": "мл",
             "hint": f"Осталось {max(norm_water - water, 0)} мл",
             "percent": min(int(water / norm_water * 100), 100) if norm_water else 0},
            {"title": "ВЕС", "value": weight, "norm": 0,
             "unit": "кг",
             "hint": "Изменение за день: —",
             "percent": 0},
        ]

    def _create_tile(self, parent, tile, row, col):
        frame = tk.Frame(parent, bg=self.BG_CARD, bd=0,
                         highlightthickness=1,
                         highlightbackground=self.BORDER)
        frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        parent.grid_columnconfigure(col, weight=1)
        parent.grid_rowconfigure(row, weight=1)

        top = tk.Frame(frame, bg=self.BG_CARD)
        top.pack(fill="x", padx=20, pady=(18, 5))

        tk.Label(top, text=tile["title"],
                 font=("TkDefaultFont", 10, "bold"),
                 bg=self.BG_CARD, fg=self.FG_MUTED).pack(side="left")

        if tile["percent"] > 0:
            tk.Label(top, text=f"{tile['percent']}%",
                     font=("TkDefaultFont", 10, "bold"),
                     bg=self.BG_ACCENT_LIGHT, fg=self.FG_ACCENT,
                     padx=8, pady=2).pack(side="right")

        value_frame = tk.Frame(frame, bg=self.BG_CARD)
        value_frame.pack(fill="x", padx=20, pady=(5, 0))

        tk.Label(value_frame, text=str(tile["value"]),
                 font=("TkDefaultFont", 24, "bold"),
                 bg=self.BG_CARD, fg=self.FG_TEXT).pack(side="left")

        if tile["norm"]:
            tk.Label(value_frame,
                     text=f"/ {tile['norm']} {tile['unit']}",
                     font=("TkDefaultFont", 11),
                     bg=self.BG_CARD, fg=self.FG_MUTED).pack(side="left",
                                                              padx=6)

        if tile["percent"] > 0:
            bar = tk.Frame(frame, bg="#E0E0E0", height=4)
            bar.pack(fill="x", padx=20, pady=(15, 5))
            fill = tk.Frame(bar, bg=self.FG_ACCENT, height=4)
            fill.place(relwidth=tile["percent"] / 100, relheight=1)

        tk.Label(frame, text=tile["hint"],
                 font=("TkDefaultFont", 9),
                 bg=self.BG_CARD, fg=self.FG_MUTED).pack(anchor="w",
                                                         padx=20,
                                                         pady=(5, 18))

    def _create_action(self, parent, title, subtitle, cmd, primary):
        bg = self.BG_ACCENT if primary else self.BG_CARD
        fg = "#FFFFFF" if primary else self.FG_TEXT
        sub_fg = "#FFFFFF" if primary else self.FG_MUTED
        border = 0 if primary else 1
        border_color = self.BG_ACCENT if primary else self.BORDER

        frame = tk.Frame(parent, bg=bg, bd=0,
                         highlightthickness=border,
                         highlightbackground=border_color,
                         cursor="hand2")
        frame.pack(fill="x", pady=4)

        inner = tk.Frame(frame, bg=bg)
        inner.pack(fill="x", padx=18, pady=14)

        text_frame = tk.Frame(inner, bg=bg)
        text_frame.pack(side="left", fill="x", expand=True)

        tk.Label(text_frame, text=title,
                 font=("TkDefaultFont", 11, "bold"),
                 bg=bg, fg=fg, anchor="w").pack(anchor="w")
        tk.Label(text_frame, text=subtitle,
                 font=("TkDefaultFont", 9),
                 bg=bg, fg=sub_fg, anchor="w").pack(anchor="w")

        tk.Label(inner, text="›",
                 font=("TkDefaultFont", 15),
                 bg=bg, fg=fg).pack(side="right")

        for w in [frame, inner, text_frame] + \
                 list(inner.winfo_children()) + \
                 list(text_frame.winfo_children()):
            w.bind("<Button-1>", lambda e, c=cmd: c())

    def _open_add_meal(self):
        from add_meal_window import AddMealWindow
        AddMealWindow(self.db, self.user).run()
        self.root.destroy()
        MainWindow(self.db, self.user).run()

    def _open_add_water(self):
        from add_water_window import AddWaterWindow
        AddWaterWindow(self.db, self.user).run()
        self.root.destroy()
        MainWindow(self.db, self.user).run()

    def _open_wellbeing(self):
        from wellbeing_window import WellbeingWindow
        WellbeingWindow(self.db, self.user).run()
        self.root.destroy()
        MainWindow(self.db, self.user).run()

    def _open_menu(self):
        from menu_selection_window import MenuSelectionWindow
        MenuSelectionWindow(self.db, self.user).run()
        self.root.destroy()
        MainWindow(self.db, self.user).run()

    def _open_forecast(self):
        from forecast_window import ForecastWindow
        ForecastWindow(self.db, self.user).run()
        self.root.destroy()
        MainWindow(self.db, self.user).run()

    def _open_stats(self):
        from statistics_window import StatisticsWindow
        StatisticsWindow(self.db, self.user).run()
        self.root.destroy()
        MainWindow(self.db, self.user).run()

    def run(self):
        self.root.mainloop()