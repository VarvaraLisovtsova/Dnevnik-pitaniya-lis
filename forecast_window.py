"""Экран прогноза достижения цели (с автоматическим расчётом)."""

import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta


class ForecastWindow:
    """Окно прогноза цели."""

    BG_MAIN = "#F0F0F0"
    BG_CARD = "#FFFFFF"
    BG_INPUT = "#E0E0E0"
    BG_BUTTON = "#7E57C2"
    BG_BUTTON_HOVER = "#5E35B1"
    BG_ACCENT_LIGHT = "#EDE7F6"
    FG_TEXT = "#333333"
    FG_MUTED = "#9E9E9E"
    FG_WHITE = "#FFFFFF"
    FG_ACCENT = "#7E57C2"
    BORDER_BLACK = "#000000"

    def __init__(self, db, user, is_new=False):
        self.db = db
        self.user = user
        self.is_new = is_new

        self.root = tk.Toplevel() if not is_new else tk.Tk()
        self.root.title("Прогноз достижения цели")
        self.root.geometry("760x720")
        self.root.configure(bg=self.BG_MAIN)
        self.root.resizable(False, False)

        self._build_ui()

    def _build_ui(self):
        card = tk.Frame(self.root, bg=self.BG_CARD, bd=0)
        card.place(relx=0.5, rely=0.5, anchor="center",
                   width=720, height=680)

        # ===== ЗАГОЛОВОК =====
        header = tk.Frame(card, bg=self.BG_CARD)
        header.pack(fill="x", padx=30, pady=(25, 15))

        tk.Label(header, text="Прогноз достижения цели",
                 font=("TkDefaultFont", 16, "bold"),
                 bg=self.BG_CARD, fg=self.FG_TEXT).pack(side="left")

        close_btn = tk.Label(header, text="✕",
                             font=("TkDefaultFont", 18, "bold"),
                             bg=self.BG_CARD, fg="#E53935",
                             cursor="hand2")
        close_btn.pack(side="right")
        close_btn.bind("<Button-1>", lambda e: self._on_close())

        tk.Frame(card, bg="#E0E0E0", height=1).pack(fill="x", padx=30)

        # ===== ПАРАМЕТРЫ =====
        tk.Label(card, text="Параметры прогноза",
                 font=("TkDefaultFont", 12, "bold"),
                 bg=self.BG_CARD, fg=self.FG_TEXT).pack(anchor="w",
                                                        padx=30,
                                                        pady=(20, 12))

        fields_frame = tk.Frame(card, bg=self.BG_CARD)
        fields_frame.pack(fill="x", padx=30, pady=(0, 15))

        self.current_var = tk.StringVar()
        self.target_var = tk.StringVar()

        self._create_field(fields_frame, "Текущий вес",
                           self.current_var, "кг", 0)
        self._create_field(fields_frame, "Целевой вес",
                           self.target_var, "кг", 1)

        # ===== СРОК =====
        tk.Label(card, text="За какой срок хотите достичь цели?",
                 font=("TkDefaultFont", 11),
                 bg=self.BG_CARD, fg=self.FG_TEXT).pack(anchor="w",
                                                        padx=30,
                                                        pady=(0, 10))

        self.period_var = tk.StringVar(value="3 месяца")
        periods_frame = tk.Frame(card, bg=self.BG_CARD)
        periods_frame.pack(fill="x", padx=30, pady=(0, 20))

        for period in ["1 месяц", "3 месяца", "6 месяцев", "12 месяцев"]:
            rb = tk.Radiobutton(
                periods_frame, text=period,
                variable=self.period_var, value=period,
                font=("TkDefaultFont", 12),
                bg=self.BG_CARD, fg=self.FG_TEXT,
                activebackground=self.BG_CARD,
                activeforeground=self.FG_TEXT,
                selectcolor=self.FG_ACCENT,
                cursor="hand2", borderwidth=0,
                highlightthickness=0, padx=8, pady=4,
            )
            rb.pack(side="left", padx=(0, 15))

        # ===== БЛОК ПРОГНОЗА =====
        forecast_frame = tk.Frame(card, bg=self.BG_ACCENT_LIGHT)
        forecast_frame.pack(fill="x", padx=30, pady=(0, 20))

        inner = tk.Frame(forecast_frame, bg=self.BG_ACCENT_LIGHT)
        inner.pack(fill="x", padx=25, pady=20)

        tk.Label(inner, text="Прогноз",
                 font=("TkDefaultFont", 11),
                 bg=self.BG_ACCENT_LIGHT, fg=self.FG_ACCENT).pack(anchor="w")

        result_grid = tk.Frame(inner, bg=self.BG_ACCENT_LIGHT)
        result_grid.pack(fill="x", pady=(10, 0))

        col1 = tk.Frame(result_grid, bg=self.BG_ACCENT_LIGHT)
        col1.pack(side="left", padx=(0, 40))
        tk.Label(col1, text="Дата достижения",
                 font=("TkDefaultFont", 9),
                 bg=self.BG_ACCENT_LIGHT, fg=self.FG_MUTED).pack(anchor="w")
        self.result_date = tk.Label(col1, text="—",
                                    font=("TkDefaultFont", 14, "bold"),
                                    bg=self.BG_ACCENT_LIGHT,
                                    fg=self.FG_TEXT)
        self.result_date.pack(anchor="w")

        col2 = tk.Frame(result_grid, bg=self.BG_ACCENT_LIGHT)
        col2.pack(side="left")
        tk.Label(col2, text="Норма калорий",
                 font=("TkDefaultFont", 9),
                 bg=self.BG_ACCENT_LIGHT, fg=self.FG_MUTED).pack(anchor="w")
        self.result_cal = tk.Label(col2, text="—",
                                   font=("TkDefaultFont", 14, "bold"),
                                   bg=self.BG_ACCENT_LIGHT,
                                   fg=self.FG_TEXT)
        self.result_cal.pack(anchor="w")

        tk.Button(inner, text="Рассчитать",
                  font=("TkDefaultFont", 10, "bold"),
                  bg=self.BG_BUTTON, fg=self.FG_WHITE,
                  activebackground=self.BG_BUTTON_HOVER,
                  activeforeground=self.FG_WHITE,
                  bd=0, cursor="hand2",
                  command=self._calculate).pack(anchor="e",
                                                pady=(15, 0),
                                                ipady=6, ipadx=15)

        # ===== РЕКОМЕНДАЦИЯ =====
        tk.Label(card, text="Рекомендация",
                 font=("TkDefaultFont", 12, "bold"),
                 bg=self.BG_CARD, fg=self.FG_TEXT).pack(anchor="w",
                                                        padx=30,
                                                        pady=(0, 8))

        self.recommendation = tk.Text(card, height=6,
                                      font=("TkDefaultFont", 11),
                                      bg=self.BG_INPUT, bd=0,
                                      wrap="word")
        self.recommendation.pack(fill="x", padx=30, pady=(0, 20))
        self.recommendation.insert(
            "1.0",
            "Введите текущий и целевой вес, выберите срок — "
            "и нажмите «Рассчитать».\n\n"
            "Приложение само определит, нужно ли вам похудеть "
            "или набрать вес, и рассчитает норму калорий."
        )

        # ===== КНОПКИ =====
        btns = tk.Frame(card, bg=self.BG_CARD)
        btns.pack(fill="x", padx=30, pady=(0, 25))

        cancel_outer = tk.Frame(btns, bg=self.BORDER_BLACK)
        cancel_outer.pack(side="left", padx=(0, 12))
        cancel_inner = tk.Frame(cancel_outer, bg=self.BG_CARD)
        cancel_inner.pack(padx=1, pady=1)
        tk.Button(cancel_inner, text="Отмена",
                  font=("TkDefaultFont", 11),
                  bg=self.BG_CARD, fg=self.FG_TEXT,
                  activebackground="#E0E0E0",
                  activeforeground=self.FG_TEXT,
                  bd=0, cursor="hand2",
                  command=self._on_cancel,
                  width=14).pack(ipady=12)

        save_outer = tk.Frame(btns, bg=self.BORDER_BLACK)
        save_outer.pack(side="left")
        save_inner = tk.Frame(save_outer, bg=self.BG_BUTTON)
        save_inner.pack(padx=1, pady=1)
        tk.Button(save_inner, text="Сохранить",
                  font=("TkDefaultFont", 11, "bold"),
                  bg=self.BG_BUTTON, fg=self.FG_WHITE,
                  activebackground=self.BG_BUTTON_HOVER,
                  activeforeground=self.FG_WHITE,
                  bd=0, cursor="hand2",
                  command=self._save,
                  width=14).pack(ipady=12)

    def _create_field(self, parent, label, var, unit, col):
        frame = tk.Frame(parent, bg=self.BG_CARD)
        frame.grid(row=0, column=col, padx=6, sticky="ew")
        parent.grid_columnconfigure(col, weight=1)

        tk.Label(frame, text=label,
                 font=("TkDefaultFont", 10),
                 bg=self.BG_CARD, fg=self.FG_MUTED).pack(anchor="w")

        outer = tk.Frame(frame, bg=self.BORDER_BLACK)
        outer.pack(fill="x", pady=(5, 0))
        inner = tk.Frame(outer, bg=self.BG_INPUT)
        inner.pack(fill="x", padx=1, pady=1)

        e = tk.Entry(inner, textvariable=var,
                     font=("TkDefaultFont", 14, "bold"),
                     bg=self.BG_INPUT, fg=self.FG_TEXT,
                     bd=0, relief="flat", highlightthickness=0)
        e.pack(side="left", fill="x", expand=True, ipady=12, padx=12)

        tk.Label(inner, text=unit,
                 font=("TkDefaultFont", 9),
                 bg=self.BG_INPUT, fg=self.FG_MUTED).pack(side="right",
                                                          padx=12)

    def _calc_base_metabolism(self, weight: float) -> float:
        result = self.db.execute(
            "SELECT Пол, РостСм, ДатаРождения, УровеньАктивности "
            "FROM Пользователи WHERE Код_пользователя = ?",
            (self.user.user_id,)
        )
        if not result:
            return 1500

        gender, height, birth, activity = result[0]
        height = height or 170

        age = 30
        if birth:
            try:
                b = datetime.strptime(birth, "%Y-%m-%d")
                age = (datetime.now() - b).days // 365
            except Exception:
                pass

        if gender == "Женский":
            bmr = 10 * weight + 6.25 * height - 5 * age - 161
        else:
            bmr = 10 * weight + 6.25 * height - 5 * age + 5

        coef = {"Низкий": 1.2, "Средний": 1.55, "Высокий": 1.725}.get(
            activity, 1.375
        )
        return bmr * coef

    def _calculate(self):
        try:
            current = float(self.current_var.get().replace(",", "."))
            target = float(self.target_var.get().replace(",", "."))
        except ValueError:
            messagebox.showwarning("Ошибка",
                                   "Введите текущий и целевой вес")
            return

        if current <= 0 or target <= 0:
            messagebox.showwarning("Ошибка", "Вес должен быть положительным")
            return

        period = self.period_var.get()
        months = {"1 месяц": 1, "3 месяца": 3,
                  "6 месяцев": 6, "12 месяцев": 12}[period]
        days = months * 30

        diff = target - current
        total_kcal = abs(diff) * 7700
        daily_change = total_kcal / days

        base = self._calc_base_metabolism(current)

        if diff < 0:
            goal_type = "Похудение"
            norm_cal = int(base - daily_change)
            if norm_cal < 1200:
                norm_cal = 1200
        elif diff > 0:
            goal_type = "Набор массы"
            norm_cal = int(base + daily_change)
        else:
            goal_type = "Поддержание"
            norm_cal = int(base)

        forecast_date = datetime.now() + timedelta(days=days)

        norm_protein = int(norm_cal * 0.25 / 4)
        norm_fat = int(norm_cal * 0.30 / 9)
        norm_carbs = int(norm_cal * 0.45 / 4)

        self._calc_result = {
            "goal_type": goal_type,
            "target": target,
            "norm_cal": norm_cal,
            "norm_protein": norm_protein,
            "norm_fat": norm_fat,
            "norm_carbs": norm_carbs,
            "forecast_date": forecast_date,
            "current": current,
        }

        self.result_date.config(text=forecast_date.strftime("%d.%m.%Y"))
        self.result_cal.config(text=f"{norm_cal} ккал/день")

        self.recommendation.delete("1.0", tk.END)

        if diff < 0:
            text = (
                f"Цель: похудеть с {current:.1f} кг до {target:.1f} кг "
                f"за {months} мес.\n\n"
                f"Норма калорий: {norm_cal} ккал/день\n"
                f"Белки: {norm_protein} г  |  "
                f"Жиры: {norm_fat} г  |  "
                f"Углеводы: {norm_carbs} г\n\n"
                f"Рекомендация: придерживайтесь этой нормы, "
                f"и вы достигнете цели к "
                f"{forecast_date.strftime('%d.%m.%Y')}."
            )
        elif diff > 0:
            text = (
                f"Цель: набрать с {current:.1f} кг до {target:.1f} кг "
                f"за {months} мес.\n\n"
                f"Норма калорий: {norm_cal} ккал/день\n"
                f"Белки: {norm_protein} г  |  "
                f"Жиры: {norm_fat} г  |  "
                f"Углеводы: {norm_carbs} г\n\n"
                f"Рекомендация: придерживайтесь этой нормы, "
                f"и вы достигнете цели к "
                f"{forecast_date.strftime('%d.%m.%Y')}."
            )
        else:
            text = (
                f"Цель: поддерживать вес {current:.1f} кг.\n\n"
                f"Норма калорий: {norm_cal} ккал/день\n"
                f"Белки: {norm_protein} г  |  "
                f"Жиры: {norm_fat} г  |  "
                f"Углеводы: {norm_carbs} г"
            )

        self.recommendation.insert("1.0", text)

    def _save(self):
        """Сохранить цель и открыть дашборд."""
        if not hasattr(self, "_calc_result"):
            messagebox.showwarning("Ошибка",
                                   "Сначала нажмите «Рассчитать»")
            return

        r = self._calc_result
        messagebox.showinfo("Успех",
                            f"Цель «{r['goal_type']}» сохранена!\n"
                            f"Норма калорий: {r['norm_cal']} ккал/день")
        self._save_and_go_to_dashboard()

    def _on_close(self):
        """Крестик — если цель рассчитана, сохраняем и идём на дашборд."""
        if hasattr(self, "_calc_result"):
            self._save_and_go_to_dashboard()
        else:
            self._on_cancel()

    def _on_cancel(self):
        """Отмена — закрыть без сохранения."""
        if self.is_new:
            self.root.destroy()
            from login_window import LoginWindow
            LoginWindow(self.db).run()
        else:
            self.root.destroy()

    def _save_and_go_to_dashboard(self):
        """Сохраняет цель и открывает дашборд."""
        r = self._calc_result

        existing = self.db.execute(
            "SELECT Код_цели FROM Цели WHERE Код_пользователя = ?",
            (self.user.user_id,)
        )

        if existing:
            self.db.execute("""
                UPDATE Цели SET
                    ТипЦели = ?,
                    ЦелевойВесКг = ?,
                    НормаКалорий = ?,
                    НормаБелков = ?,
                    НормаЖиров = ?,
                    НормаУглеводов = ?,
                    ДатаНачала = DATE('now'),
                    ДатаОкончания = ?
                WHERE Код_пользователя = ?
            """, (r["goal_type"], r["target"],
                  r["norm_cal"], r["norm_protein"], r["norm_fat"],
                  r["norm_carbs"], r["forecast_date"].strftime("%Y-%m-%d"),
                  self.user.user_id))
        else:
            self.db.execute("""
                INSERT INTO Цели
                (Код_пользователя, ТипЦели, ЦелевойВесКг, НормаКалорий,
                 НормаБелков, НормаЖиров, НормаУглеводов,
                 ДатаНачала, ДатаОкончания)
                VALUES (?, ?, ?, ?, ?, ?, ?, DATE('now'), ?)
            """, (self.user.user_id, r["goal_type"], r["target"],
                  r["norm_cal"], r["norm_protein"], r["norm_fat"],
                  r["norm_carbs"], r["forecast_date"].strftime("%Y-%m-%d")))

        self.db.execute("""
            INSERT INTO ИсторияВеса (Код_пользователя, ДатаЗаписи, ВесКг)
            VALUES (?, DATE('now'), ?)
        """, (self.user.user_id, r["current"]))

        self.root.destroy()
        from main_window import MainWindow
        MainWindow(self.db, self.user).run()

    def run(self):
        self.root.mainloop()