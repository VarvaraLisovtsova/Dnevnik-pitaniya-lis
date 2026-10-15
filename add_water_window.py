"""Экран добавления воды — всё на Canvas со скруглением."""

import tkinter as tk
from tkinter import messagebox
from datetime import datetime


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
                 hover_bg="#5E35B1", width=130, height=46,
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


class RoundedQuickButton(tk.Canvas):
    def __init__(self, parent, text="", command=None,
                 width=105, height=44, radius=10,
                 bg="#FFFFFF", fg="#333333",
                 selected_bg="#EDE7F6", selected_fg="#7E57C2",
                 border_color="#C0C0C0",
                 parent_bg="#FFFFFF"):
        super().__init__(parent, width=width, height=height,
                         bg=parent_bg, highlightthickness=0, bd=0,
                         cursor="hand2")
        self.command = command
        self.bg_color = bg
        self.fg_color = fg
        self.selected_bg = selected_bg
        self.selected_fg = selected_fg
        self.border_color = border_color

        create_rounded_rect(
            self, 1, 1, width - 1, height - 1, radius,
            fill=bg, outline=border_color, width=1, tags="shape"
        )
        self.text_id = self.create_text(
            width // 2, height // 2,
            text=text, fill=fg, font=("TkDefaultFont", 10)
        )
        self.bind("<Button-1>", lambda e: command() if command else None)

    def set_selected(self, selected):
        if selected:
            self.itemconfig("shape", fill=self.selected_bg,
                            outline="#7E57C2")
            self.itemconfig(self.text_id, fill=self.selected_fg)
        else:
            self.itemconfig("shape", fill=self.bg_color,
                            outline=self.border_color)
            self.itemconfig(self.text_id, fill=self.fg_color)


class AddWaterWindow:
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

    NORM_ML = 2000

    def __init__(self, db, user):
        self.db = db
        self.user = user
        self.root = tk.Toplevel()
        self.root.title("Добавить воду")
        self.root.geometry("580x740")
        self.root.configure(bg=self.BG_MAIN)
        self.root.resizable(False, False)

        self.current_ml = self._get_today_total()
        self.selected_volume = tk.IntVar(value=250)

        self._build_ui()

    def _get_today_total(self):
        today = datetime.now().strftime("%Y-%m-%d")
        result = self.db.execute(
            "SELECT COALESCE(SUM(КоличествоМл), 0) FROM УчётВоды "
            "WHERE Код_пользователя = ? AND ДатаЗаписи = ?",
            (self.user.user_id, today)
        )
        if result and len(result) > 0:
            return int(result[0][0] or 0)
        return 0

    def _get_last_record_time(self):
        today = datetime.now().strftime("%Y-%m-%d")
        result = self.db.execute(
            "SELECT ВремяЗаписи, КоличествоМл FROM УчётВоды "
            "WHERE Код_пользователя = ? AND ДатаЗаписи = ? "
            "ORDER BY Код_записи DESC LIMIT 1",
            (self.user.user_id, today)
        )
        if result and len(result) > 0:
            return result[0]
        return None

    def _build_ui(self):
        card = tk.Frame(self.root, bg=self.BG_CARD)
        card.pack(fill="both", expand=True, padx=20, pady=20)

        # ===== ЗАГОЛОВОК =====
        head = tk.Frame(card, bg=self.BG_CARD)
        head.pack(fill="x", padx=25, pady=(20, 15))

        tk.Label(head, text="Добавить воду",
                 font=("TkDefaultFont", 15, "bold"),
                 bg=self.BG_CARD, fg=self.FG_TEXT).pack(side="left")

        close = tk.Label(head, text="✕",
                         font=("TkDefaultFont", 18, "bold"),
                         bg=self.BG_CARD, fg="#E53935",
                         cursor="hand2")
        close.pack(side="right")
        close.bind("<Button-1>", lambda e: self.root.destroy())

        # ===== ПРОГРЕСС (весь блок на Canvas) =====
        self.progress_canvas = tk.Canvas(card, height=120,
                                         bg=self.BG_CARD,
                                         highlightthickness=0)
        self.progress_canvas.pack(fill="x", padx=25, pady=(0, 15))
        self.progress_canvas.bind("<Configure>", self._draw_progress)

        # Внутренние элементы прогресса (созданы в _draw_progress)

        # ===== БЫСТРЫЙ ВЫБОР =====
        header = tk.Frame(card, bg=self.BG_CARD)
        header.pack(fill="x", padx=25, pady=(5, 3))

        tk.Label(header, text="Быстрый выбор объёма",
                 font=("TkDefaultFont", 11, "bold"),
                 bg=self.BG_CARD, fg=self.FG_TEXT).pack(side="left")
        tk.Label(header, text="Можно изменить ниже",
                 font=("TkDefaultFont", 9),
                 bg=self.BG_CARD, fg=self.FG_MUTED).pack(side="right")

        quick_frame = tk.Frame(card, bg=self.BG_CARD)
        quick_frame.pack(fill="x", padx=25, pady=(5, 15))

        self.quick_buttons = {}
        for ml in [150, 250, 300, 500]:
            btn = RoundedQuickButton(
                quick_frame, text=f"{ml} мл",
                width=105, height=44, radius=10,
                bg=self.BG_CARD, fg=self.FG_TEXT,
                selected_bg=self.BG_ACCENT_LIGHT,
                selected_fg=self.BG_ACCENT,
                border_color="#C0C0C0",
                parent_bg=self.BG_CARD,
                command=lambda m=ml: self._select_volume(m)
            )
            btn.pack(side="left", padx=4)
            self.quick_buttons[ml] = btn

        # ===== ПРОИЗВОЛЬНЫЙ + ВРЕМЯ =====
        custom_frame = tk.Frame(card, bg=self.BG_CARD)
        custom_frame.pack(fill="x", padx=25, pady=(0, 15))
        custom_frame.grid_columnconfigure(0, weight=1)
        custom_frame.grid_columnconfigure(1, weight=0)

        # Объём
        vol_col = tk.Frame(custom_frame, bg=self.BG_CARD)
        vol_col.grid(row=0, column=0, sticky="ew")

        tk.Label(vol_col, text="Произвольный объём",
                 font=("TkDefaultFont", 9),
                 bg=self.BG_CARD, fg=self.FG_MUTED).pack(anchor="w")

        self.vol_canvas = tk.Canvas(vol_col, height=48,
                                    bg=self.BG_CARD,
                                    highlightthickness=0)
        self.vol_canvas.pack(fill="x", pady=(3, 0))
        self.vol_canvas.bind("<Configure>", self._draw_volume)

        # Время
        time_col = tk.Frame(custom_frame, bg=self.BG_CARD)
        time_col.grid(row=0, column=1, padx=(10, 0), sticky="e")

        tk.Label(time_col, text="Время",
                 font=("TkDefaultFont", 9),
                 bg=self.BG_CARD, fg=self.FG_MUTED).pack(anchor="w")

        self.time_canvas = tk.Canvas(time_col, width=130, height=48,
                                     bg=self.BG_CARD,
                                     highlightthickness=0)
        self.time_canvas.pack(pady=(3, 0))
        create_rounded_rect(
            self.time_canvas, 1, 1, 129, 47, 10,
            fill=self.BG_INPUT, outline="#C0C0C0", width=1
        )

        self.time_var = tk.StringVar(
            value=datetime.now().strftime("%H:%M")
        )
        time_entry = tk.Entry(self.time_canvas, textvariable=self.time_var,
                              font=("TkDefaultFont", 11),
                              bg=self.BG_INPUT, bd=0,
                              justify="center")
        time_entry.place(x=20, y=13, width=90, height=22)

        # ===== ПРЕДПРОСМОТР =====
        self.preview_canvas = tk.Canvas(card, height=80,
                                        bg=self.BG_CARD,
                                        highlightthickness=0)
        self.preview_canvas.pack(fill="x", padx=25, pady=(0, 15))
        self.preview_canvas.bind("<Configure>", self._draw_preview)

        # Внутренние элементы
        self.preview_label_1 = tk.Label(
            self.preview_canvas, text="Будет добавлено",
            font=("TkDefaultFont", 9),
            bg=self.BG_CARD, fg=self.FG_MUTED, anchor="w"
        )
        self.preview_label_1.place(x=20, y=15)

        self.preview_label_2 = tk.Label(
            self.preview_canvas, text="250 мл воды",
            font=("TkDefaultFont", 12, "bold"),
            bg=self.BG_CARD, fg=self.FG_TEXT, anchor="w"
        )
        self.preview_label_2.place(x=20, y=38)

        # Forecast badge
        self.forecast_canvas = tk.Canvas(self.preview_canvas,
                                         width=200, height=36,
                                         bg=self.BG_CARD,
                                         highlightthickness=0)
        self.forecast_canvas.place(relx=1.0, rely=0.5,
                                   anchor="e", x=-15)
        create_rounded_rect(
            self.forecast_canvas, 1, 1, 199, 35, 10,
            fill=self.BG_ACCENT_LIGHT,
            outline=self.BG_ACCENT, width=1
        )
        self.forecast_label = tk.Label(
            self.forecast_canvas, text="",
            font=("TkDefaultFont", 10, "bold"),
            bg=self.BG_ACCENT_LIGHT, fg=self.FG_ACCENT,
            anchor="center"
        )
        self.forecast_label.place(x=5, y=8, width=190, height=20)

        # ===== ПОДСКАЗКА =====
        self.hint_canvas = tk.Canvas(card, height=64,
                                     bg=self.BG_CARD,
                                     highlightthickness=0)
        self.hint_canvas.pack(fill="x", padx=25, pady=(0, 15))
        self.hint_canvas.bind("<Configure>", self._draw_hint)

        tk.Label(self.hint_canvas,
                 text="Пейте небольшими порциями в течение дня — "
                      "так проще поддерживать водный баланс.",
                 font=("TkDefaultFont", 9),
                 bg=self.BG_LIGHT_GRAY, fg=self.FG_MUTED,
                 justify="left", wraplength=440,
                 anchor="w").place(x=20, y=20)

        # ===== НИЖНЯЯ СТРОКА =====
        bottom = tk.Frame(card, bg=self.BG_CARD)
        bottom.pack(fill="x", padx=25, pady=(0, 20))

        last = self._get_last_record_time()
        if last:
            last_text = f"Последняя запись: {last[1]} мл в {last[0]}"
        else:
            last_text = "Записей ещё нет"

        tk.Label(bottom, text=last_text,
                 font=("TkDefaultFont", 9),
                 bg=self.BG_CARD, fg=self.FG_MUTED).pack(side="left")

        btns = tk.Frame(bottom, bg=self.BG_CARD)
        btns.pack(side="right")

        RoundedButton(btns, text="Отмена",
                      width=130, height=46, radius=12,
                      bg=self.BG_CARD, fg=self.FG_TEXT,
                      hover_bg="#E0E0E0",
                      font=("TkDefaultFont", 11),
                      border_color="#000000", border_width=1,
                      parent_bg=self.BG_CARD,
                      command=self.root.destroy
                      ).pack(side="left", padx=(0, 12))

        RoundedButton(btns, text="Добавить",
                      width=130, height=46, radius=12,
                      bg=self.BG_BUTTON, fg=self.FG_WHITE,
                      hover_bg=self.BG_BUTTON_HOVER,
                      font=("TkDefaultFont", 11, "bold"),
                      parent_bg=self.BG_CARD,
                      command=self._save
                      ).pack(side="left")

        self._select_volume(250)

    def _draw_progress(self, event):
        """Рисует весь блок прогресса на Canvas."""
        canvas = self.progress_canvas
        canvas.delete("all")
        width = event.width
        height = 120

        # Фон (светло-фиолетовый, скруглённый)
        create_rounded_rect(
            canvas, 0, 0, width, height, 14,
            fill=self.BG_ACCENT_LIGHT, outline=self.BG_ACCENT_LIGHT
        )

        # Заголовок «200 из 2000 мл»
        canvas.create_text(
            20, 20,
            text=f"{self.current_ml} из {self.NORM_ML} мл",
            anchor="nw", fill=self.FG_TEXT,
            font=("TkDefaultFont", 14, "bold")
        )

        # Проценты
        percent_display = min(int(self.current_ml / self.NORM_ML * 100), 100)
        canvas.create_text(
            width - 20, 20,
            text=f"{percent_display}%",
            anchor="ne", fill=self.FG_ACCENT,
            font=("TkDefaultFont", 11, "bold")
        )

        # Прогресс-бар
        bar_x1 = 20
        bar_x2 = width - 20
        bar_y1 = 55
        bar_y2 = 67
        bar_r = 6

        create_rounded_rect(
            canvas, bar_x1, bar_y1, bar_x2, bar_y2, bar_r,
            fill="#DDDDDD", outline="#DDDDDD"
        )

        percent = min(self.current_ml / self.NORM_ML, 1.0)
        fill_width = max(int((bar_x2 - bar_x1) * percent), bar_r * 2)
        create_rounded_rect(
            canvas, bar_x1, bar_y1, bar_x1 + fill_width, bar_y2, bar_r,
            fill=self.BG_ACCENT, outline=self.BG_ACCENT
        )

        # Нижняя строка
        canvas.create_text(
            20, height - 20,
            text="Сегодня",
            anchor="sw", fill=self.FG_MUTED,
            font=("TkDefaultFont", 9)
        )

        remaining = max(self.NORM_ML - self.current_ml, 0)
        canvas.create_text(
            width - 20, height - 20,
            text=f"Осталось {remaining} мл",
            anchor="se", fill=self.FG_MUTED,
            font=("TkDefaultFont", 9)
        )

    def _draw_volume(self, event):
        """Рисует фон поля объёма."""
        canvas = self.vol_canvas
        canvas.delete("bg")
        width = event.width

        create_rounded_rect(
            canvas, 1, 1, width - 1, 47, 10,
            fill=self.BG_INPUT, outline="#C0C0C0", width=1,
            tags="bg"
        )
        canvas.tag_lower("bg")

        # Кнопка «−» — слева
        canvas.delete("minus")
        canvas.create_text(
            25, 24,
            text="−", fill=self.FG_TEXT,
            font=("TkDefaultFont", 14, "bold"),
            tags="minus"
        )

        # Кнопка «+» — справа
        canvas.delete("plus")
        canvas.create_text(
            width - 25, 24,
            text="+", fill=self.FG_TEXT,
            font=("TkDefaultFont", 14, "bold"),
            tags="plus"
        )

        # Текст «250 мл»
        canvas.delete("volume_text")
        canvas.create_text(
            width // 2, 24,
            text=f"{self.selected_volume.get()} мл",
            fill=self.FG_TEXT,
            font=("TkDefaultFont", 11, "bold"),
            tags="volume_text"
        )

        # Привязка кликов
        canvas.bind("<Button-1>", self._on_vol_click)

    def _on_vol_click(self, event):
        """Обработка клика по полю объёма."""
        canvas = self.vol_canvas
        width = canvas.winfo_width()

        if event.x < 60:
            self._decrease()
        elif event.x > width - 60:
            self._increase()

    def _draw_preview(self, event):
        """Рисует рамку предпросмотра."""
        canvas = self.preview_canvas
        canvas.delete("bg")
        create_rounded_rect(
            canvas, 1, 1, event.width - 1, 79, 12,
            fill=self.BG_CARD, outline="#D0D0D0", width=1,
            tags="bg"
        )
        canvas.tag_lower("bg")

    def _draw_hint(self, event):
        """Рисует фон подсказки."""
        canvas = self.hint_canvas
        canvas.delete("bg")
        create_rounded_rect(
            canvas, 1, 1, event.width - 1, 63, 12,
            fill=self.BG_LIGHT_GRAY, outline=self.BG_LIGHT_GRAY, width=1,
            tags="bg"
        )
        canvas.tag_lower("bg")

    def _select_volume(self, ml):
        self.selected_volume.set(ml)
        for value, btn in self.quick_buttons.items():
            btn.set_selected(value == ml)
        self._update_preview()

    def _decrease(self):
        val = max(self.selected_volume.get() - 50, 50)
        self.selected_volume.set(val)
        self._update_preview()

    def _increase(self):
        val = self.selected_volume.get() + 50
        self.selected_volume.set(val)
        self._update_preview()

    def _update_preview(self):
        vol = self.selected_volume.get()
        self.preview_label_2.config(text=f"{vol} мл воды")

        # Перерисовываем поле объёма
        self.vol_canvas.event_generate("<Configure>")

        new_total = self.current_ml + vol
        percent = min(int(new_total / self.NORM_ML * 100), 999)
        self.forecast_label.config(
            text=f"{new_total} / {self.NORM_ML} мл · {percent}%"
        )

    def _save(self):
        vol = self.selected_volume.get()
        if vol <= 0:
            messagebox.showwarning("Ошибка", "Объём должен быть больше 0")
            return

        time_str = self.time_var.get().strip()
        if not time_str:
            time_str = datetime.now().strftime("%H:%M")

        today = datetime.now().strftime("%Y-%m-%d")

        self.db.execute(
            "INSERT INTO УчётВоды "
            "(Код_пользователя, ДатаЗаписи, КоличествоМл, ВремяЗаписи) "
            "VALUES (?, ?, ?, ?)",
            (self.user.user_id, today, vol, time_str)
        )

        messagebox.showinfo("Успех", f"Добавлено {vol} мл воды")
        self.root.destroy()

    def run(self):
        self.root.wait_window()