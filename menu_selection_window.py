"""Экран подбора меню — с сохранением, рецептами и прокруткой."""

import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import random


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


TECH_PRODUCTS = [
    "разрыхлитель", "сода", "дрожжи", "крахмал", "желатин",
    "агар", "уксус", "соевый соус", "кетчуп", "майонез",
    "горчица", "хрен", "специи", "приправа", "соль",
    "сахарная пудра", "фруктоза", "мука", "какао-порошок",
    "ванилин", "сахар",
]


class RoundedButton(tk.Canvas):
    def __init__(self, parent, text="", command=None,
                 bg="#7E57C2", fg="#FFFFFF",
                 hover_bg="#5E35B1", width=130, height=44,
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


class ChipWidget(tk.Canvas):
    def __init__(self, parent, text, on_remove=None,
                 height=28, radius=8, bg="#EDE7F6", fg="#7E57C2",
                 parent_bg="#FFFFFF"):
        width = max(65, len(text) * 7 + 40)
        super().__init__(parent, width=width, height=height,
                         bg=parent_bg, highlightthickness=0, bd=0)
        self.on_remove = on_remove
        self.text_value = text

        create_rounded_rect(
            self, 1, 1, width - 1, height - 1, radius,
            fill=bg, outline="#7E57C2", width=1
        )
        self.create_text(10, height // 2, text=text,
                         anchor="w", fill=fg,
                         font=("TkDefaultFont", 9))
        self.create_text(width - 12, height // 2, text="✕",
                         fill=fg, font=("TkDefaultFont", 9, "bold"),
                         tags="remove")
        self.tag_bind("remove", "<Button-1>",
                      lambda e: self._remove())
        self.tag_bind("remove", "<Enter>",
                      lambda e: self.itemconfig("remove", fill="#E53935"))
        self.tag_bind("remove", "<Leave>",
                      lambda e: self.itemconfig("remove", fill=fg))

    def _remove(self):
        if self.on_remove:
            self.on_remove(self.text_value)


class MenuSelectionWindow:
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

    def __init__(self, db, user):
        self.db = db
        self.user = user
        self.root = tk.Toplevel()
        self.root.title("Подбор меню")
        self.root.geometry("960x900")
        self.root.configure(bg=self.BG_MAIN)
        self.root.resizable(False, False)

        self.norm_cal = self._load_norm()

        self.goal_cal = tk.IntVar(value=self.norm_cal)
        self.meals_count = tk.StringVar(value="4")
        self.period_var = tk.StringVar(value="7 дней")

        # Загружаем сохранённые предпочтения и исключения
        self.preferences = self._load_list("preferences")
        self.exclusions = self._load_list("exclusions")

        self.menu_result = []
        self.menu_totals = None
        self.current_dish_name = ""

        self._build_ui()

    def _load_norm(self):
        result = self.db.execute(
            "SELECT НормаКалорий FROM Цели "
            "WHERE Код_пользователя = ? "
            "ORDER BY Код_цели DESC LIMIT 1",
            (self.user.user_id,)
        )
        if result and len(result) > 0:
            return int(result[0][0] or 1800)
        return 1800

    def _load_list(self, key):
        """Загружает список из таблицы Настройки."""
        try:
            result = self.db.execute(
                "SELECT Значение FROM Настройки "
                "WHERE Код_пользователя = ? AND Ключ = ?",
                (self.user.user_id, key)
            )
            if result and len(result) > 0:
                value = result[0][0] or ""
                if value:
                    return value.split("|")
        except Exception:
            pass
        return []

    def _save_list(self, key, items):
        """Сохраняет список в таблицу Настройки."""
        try:
            self.db.execute(
                "DELETE FROM Настройки "
                "WHERE Код_пользователя = ? AND Ключ = ?",
                (self.user.user_id, key)
            )
            value = "|".join(items)
            self.db.execute(
                "INSERT INTO Настройки "
                "(Код_пользователя, Ключ, Значение) "
                "VALUES (?, ?, ?)",
                (self.user.user_id, key, value)
            )
        except Exception as e:
            print(f"Ошибка сохранения: {e}")

    def _build_ui(self):
        # Прокрутка
        outer = tk.Frame(self.root, bg=self.BG_MAIN)
        outer.pack(fill="both", expand=True)

        self.main_canvas = tk.Canvas(outer, bg=self.BG_MAIN,
                                     highlightthickness=0)
        scrollbar = tk.Scrollbar(outer, orient="vertical",
                                 command=self.main_canvas.yview)
        self.main_canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        self.main_canvas.pack(side="left", fill="both", expand=True)

        card = tk.Frame(self.main_canvas, bg=self.BG_CARD)
        card_window = self.main_canvas.create_window(
            (0, 0), window=card, anchor="nw"
        )

        card.bind(
            "<Configure>",
            lambda e: self.main_canvas.configure(
                scrollregion=self.main_canvas.bbox("all")
            )
        )
        self.main_canvas.bind(
            "<Configure>",
            lambda e: self.main_canvas.itemconfig(
                card_window, width=e.width
            )
        )

        def on_mousewheel(event):
            self.main_canvas.yview_scroll(
                int(-1 * (event.delta / 120)), "units"
            )

        self.main_canvas.bind_all("<MouseWheel>", on_mousewheel)

        # Внутренний отступ
        inner = tk.Frame(card, bg=self.BG_CARD)
        inner.pack(fill="both", expand=True, padx=20, pady=20)

        # ===== ЗАГОЛОВОК =====
        head = tk.Frame(inner, bg=self.BG_CARD)
        head.pack(fill="x", padx=5, pady=(10, 15))

        tk.Label(head, text="Подбор меню",
                 font=("TkDefaultFont", 15, "bold"),
                 bg=self.BG_CARD, fg=self.FG_TEXT).pack(side="left")

        close = tk.Label(head, text="✕",
                         font=("TkDefaultFont", 18, "bold"),
                         bg=self.BG_CARD, fg="#E53935",
                         cursor="hand2")
        close.pack(side="right")
        close.bind("<Button-1>", lambda e: self.root.destroy())

        # ===== ПАРАМЕТРЫ =====
        tk.Label(inner, text="Параметры подбора",
                 font=("TkDefaultFont", 11, "bold"),
                 bg=self.BG_CARD, fg=self.FG_TEXT).pack(anchor="w",
                                                        padx=5,
                                                        pady=(0, 8))

        params = tk.Frame(inner, bg=self.BG_CARD)
        params.pack(fill="x", padx=5, pady=(0, 15))
        params.grid_columnconfigure(0, weight=1)
        params.grid_columnconfigure(1, weight=1)
        params.grid_columnconfigure(2, weight=1)

        # Цель
        c1 = tk.Frame(params, bg=self.BG_CARD)
        c1.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        tk.Label(c1, text="Цель по калориям",
                 font=("TkDefaultFont", 9),
                 bg=self.BG_CARD, fg=self.FG_MUTED).pack(anchor="w")
        cal_c = tk.Canvas(c1, height=40, bg=self.BG_CARD,
                          highlightthickness=0)
        cal_c.pack(fill="x", pady=(3, 0))
        cal_c.bind("<Configure>",
                   lambda e: self._draw_input_bg(cal_c, e.width))
        tk.Entry(cal_c, textvariable=self.goal_cal,
                 font=("TkDefaultFont", 11), bg=self.BG_INPUT,
                 bd=0, justify="left").place(x=15, y=8, width=100,
                                              height=22)
        tk.Label(cal_c, text="ккал/день",
                 font=("TkDefaultFont", 9),
                 bg=self.BG_INPUT, fg=self.FG_MUTED).place(x=170, y=13)

        # Приёмов
        c2 = tk.Frame(params, bg=self.BG_CARD)
        c2.grid(row=0, column=1, sticky="ew", padx=8)
        tk.Label(c2, text="Приёмов пищи",
                 font=("TkDefaultFont", 9),
                 bg=self.BG_CARD, fg=self.FG_MUTED).pack(anchor="w")
        meals_c = tk.Canvas(c2, height=40, bg=self.BG_CARD,
                            highlightthickness=0)
        meals_c.pack(fill="x", pady=(3, 0))
        meals_c.bind("<Configure>",
                     lambda e: self._draw_input_bg(meals_c, e.width))
        meals_lbl = tk.Label(meals_c, textvariable=self.meals_count,
                             font=("TkDefaultFont", 11),
                             bg=self.BG_INPUT, fg=self.FG_TEXT,
                             anchor="w")
        meals_lbl.place(x=15, y=8, width=150, height=22)
        meals_arrow = tk.Label(meals_c, text="▼",
                               font=("TkDefaultFont", 8),
                               bg=self.BG_INPUT, fg=self.FG_TEXT,
                               cursor="hand2")
        meals_arrow.place(x=250, y=10)

        meals_menu = tk.Menu(self.root, tearoff=0)
        for m in ["3", "4", "5"]:
            meals_menu.add_command(
                label=m,
                command=lambda x=m: self.meals_count.set(x)
            )

        def open_meals_menu(e):
            meals_menu.tk_popup(e.x_root, e.y_root)

        for w in [meals_c, meals_lbl, meals_arrow]:
            w.bind("<Button-1>", open_meals_menu)

        # Период
        c3 = tk.Frame(params, bg=self.BG_CARD)
        c3.grid(row=0, column=2, sticky="ew", padx=(8, 0))
        tk.Label(c3, text="Период",
                 font=("TkDefaultFont", 9),
                 bg=self.BG_CARD, fg=self.FG_MUTED).pack(anchor="w")
        period_c = tk.Canvas(c3, height=40, bg=self.BG_CARD,
                             highlightthickness=0)
        period_c.pack(fill="x", pady=(3, 0))
        period_c.bind("<Configure>",
                      lambda e: self._draw_input_bg(period_c, e.width))
        period_lbl = tk.Label(period_c, textvariable=self.period_var,
                              font=("TkDefaultFont", 11),
                              bg=self.BG_INPUT, fg=self.FG_TEXT,
                              anchor="w")
        period_lbl.place(x=15, y=8, width=150, height=22)
        period_arrow = tk.Label(period_c, text="▼",
                                font=("TkDefaultFont", 8),
                                bg=self.BG_INPUT, fg=self.FG_TEXT,
                                cursor="hand2")
        period_arrow.place(x=250, y=10)

        period_menu = tk.Menu(self.root, tearoff=0)
        for p in ["1 день", "3 дня", "7 дней"]:
            period_menu.add_command(
                label=p,
                command=lambda x=p: self.period_var.set(x)
            )

        def open_period_menu(e):
            period_menu.tk_popup(e.x_root, e.y_root)

        for w in [period_c, period_lbl, period_arrow]:
            w.bind("<Button-1>", open_period_menu)

        # ===== ПРЕДПОЧТЕНИЯ / ИСКЛЮЧЕНИЯ =====
        prefs_row = tk.Frame(inner, bg=self.BG_CARD)
        prefs_row.pack(fill="x", padx=5, pady=(5, 10))
        prefs_row.grid_columnconfigure(0, weight=1)
        prefs_row.grid_columnconfigure(1, weight=1)

        pc = tk.Frame(prefs_row, bg=self.BG_CARD)
        pc.grid(row=0, column=0, sticky="new", padx=(0, 5))
        tk.Label(pc, text="Предпочтения",
                 font=("TkDefaultFont", 9),
                 bg=self.BG_CARD, fg=self.FG_MUTED).pack(anchor="w")
        self.prefs_frame = tk.Frame(pc, bg=self.BG_CARD,
                                    highlightthickness=1,
                                    highlightbackground="#D0D0D0")
        self.prefs_frame.pack(fill="x", pady=(3, 0))

        ec = tk.Frame(prefs_row, bg=self.BG_CARD)
        ec.grid(row=0, column=1, sticky="new", padx=(5, 0))
        tk.Label(ec, text="Исключения",
                 font=("TkDefaultFont", 9),
                 bg=self.BG_CARD, fg=self.FG_MUTED).pack(anchor="w")
        self.excs_frame = tk.Frame(ec, bg=self.BG_CARD,
                                   highlightthickness=1,
                                   highlightbackground="#D0D0D0")
        self.excs_frame.pack(fill="x", pady=(3, 0))

        # ===== ОПИСАНИЕ + КНОПКА =====
        action = tk.Frame(inner, bg=self.BG_CARD)
        action.pack(fill="x", padx=5, pady=(10, 15))

        tk.Label(action,
                 text="Расчёт учитывает цель, выбранные продукты "
                      "и распределение калорий в течение дня.",
                 font=("TkDefaultFont", 9),
                 bg=self.BG_CARD, fg=self.FG_MUTED,
                 justify="left", wraplength=500).pack(side="left")

        RoundedButton(action, text="Подобрать меню",
                      width=180, height=44, radius=10,
                      bg=self.BG_ACCENT, fg=self.FG_WHITE,
                      hover_bg=self.BG_BUTTON_HOVER,
                      font=("TkDefaultFont", 11, "bold"),
                      parent_bg=self.BG_CARD,
                      command=self._generate_menu
                      ).pack(side="right")

        # ===== МЕНЮ =====
        tk.Label(inner, text="Предложенное меню",
                 font=("TkDefaultFont", 11, "bold"),
                 bg=self.BG_CARD, fg=self.FG_TEXT).pack(anchor="w",
                                                        padx=5,
                                                        pady=(5, 5))

        table_head = tk.Frame(inner, bg="#F5F5F5")
        table_head.pack(fill="x", padx=5)

        headers = [("Приём пищи", 12, "w"),
                   ("Блюда", 40, "w"),
                   ("Ккал", 8, "e"),
                   ("Белки", 8, "e"),
                   ("Жиры", 8, "e"),
                   ("Углев.", 8, "e")]

        for text, width, anchor in headers:
            tk.Label(table_head, text=text,
                     font=("TkDefaultFont", 10, "bold"),
                     bg="#F5F5F5", fg=self.FG_TEXT,
                     width=width, anchor=anchor).pack(side="left",
                                                       padx=2, pady=8)

        self.menu_canvas = tk.Canvas(inner, height=340,
                                     bg=self.BG_CARD,
                                     highlightthickness=0)
        self.menu_canvas.pack(fill="x", padx=5)
        self.menu_canvas.bind("<Configure>", self._draw_menu_rows)

        self.total_canvas = tk.Canvas(inner, height=50,
                                      bg=self.BG_CARD,
                                      highlightthickness=0)
        self.total_canvas.pack(fill="x", padx=5, pady=(5, 10))
        self.total_canvas.bind("<Configure>", self._draw_total)

        self.status_canvas = tk.Canvas(inner, height=40,
                                       bg=self.BG_CARD,
                                       highlightthickness=0)
        self.status_canvas.pack(fill="x", padx=5, pady=(0, 15))
        self.status_canvas.bind("<Configure>", self._draw_status)

        # ===== КНОПКИ =====
        btns = tk.Frame(inner, bg=self.BG_CARD)
        btns.pack(fill="x", padx=5, pady=(0, 20))

        RoundedButton(btns, text="Отмена",
                      width=150, height=46, radius=12,
                      bg=self.BG_CARD, fg=self.FG_TEXT,
                      hover_bg="#E0E0E0",
                      font=("TkDefaultFont", 11),
                      border_color="#000000", border_width=1,
                      parent_bg=self.BG_CARD,
                      command=self.root.destroy
                      ).pack(side="left", padx=(0, 12))

        RoundedButton(btns, text="Сохранить",
                      width=150, height=46, radius=12,
                      bg=self.BG_BUTTON, fg=self.FG_WHITE,
                      hover_bg=self.BG_BUTTON_HOVER,
                      font=("TkDefaultFont", 11, "bold"),
                      parent_bg=self.BG_CARD,
                      command=self._save
                      ).pack(side="left")

        self._refresh_prefs()
        self._refresh_excs()

    def _draw_input_bg(self, canvas, width):
        canvas.delete("bg")
        create_rounded_rect(
            canvas, 1, 1, width - 1, 39, 10,
            fill=self.BG_INPUT, outline="#C0C0C0", width=1,
            tags="bg"
        )
        canvas.tag_lower("bg")

    def _refresh_prefs(self):
        for w in self.prefs_frame.winfo_children():
            w.destroy()
        inner = tk.Frame(self.prefs_frame, bg=self.BG_CARD)
        inner.pack(fill="x", padx=8, pady=6)

        if not self.preferences:
            tk.Label(inner, text="Все продукты",
                     font=("TkDefaultFont", 9),
                     bg=self.BG_CARD, fg=self.FG_MUTED).pack(side="left")

        row = tk.Frame(inner, bg=self.BG_CARD)
        row.pack(fill="x", anchor="w")
        cw = 0
        for p in self.preferences:
            chip_w = max(65, len(p) * 7 + 40)
            if cw + chip_w > 380:
                row = tk.Frame(inner, bg=self.BG_CARD)
                row.pack(fill="x", anchor="w", pady=(4, 0))
                cw = 0
            ChipWidget(row, text=p,
                       on_remove=self._remove_pref).pack(side="left",
                                                          padx=2)
            cw += chip_w + 4

        add_row = tk.Frame(inner, bg=self.BG_CARD)
        add_row.pack(fill="x", anchor="w", pady=(4, 0))
        ab = tk.Label(add_row, text="+ Добавить",
                      font=("TkDefaultFont", 9),
                      bg=self.BG_CARD, fg=self.FG_ACCENT,
                      cursor="hand2")
        ab.pack(side="left")
        ab.bind("<Button-1>", lambda e: self._add_pref())

    def _refresh_excs(self):
        for w in self.excs_frame.winfo_children():
            w.destroy()
        inner = tk.Frame(self.excs_frame, bg=self.BG_CARD)
        inner.pack(fill="x", padx=8, pady=6)

        if not self.exclusions:
            tk.Label(inner, text="Нет исключений",
                     font=("TkDefaultFont", 9),
                     bg=self.BG_CARD, fg=self.FG_MUTED).pack(side="left")

        row = tk.Frame(inner, bg=self.BG_CARD)
        row.pack(fill="x", anchor="w")
        cw = 0
        for ex in self.exclusions:
            chip_w = max(65, len(ex) * 7 + 40)
            if cw + chip_w > 380:
                row = tk.Frame(inner, bg=self.BG_CARD)
                row.pack(fill="x", anchor="w", pady=(4, 0))
                cw = 0
            ChipWidget(row, text=ex,
                       on_remove=self._remove_exc).pack(side="left",
                                                         padx=2)
            cw += chip_w + 4

        add_row = tk.Frame(inner, bg=self.BG_CARD)
        add_row.pack(fill="x", anchor="w", pady=(4, 0))
        ab = tk.Label(add_row, text="+ Добавить",
                      font=("TkDefaultFont", 9),
                      bg=self.BG_CARD, fg=self.FG_ACCENT,
                      cursor="hand2")
        ab.pack(side="left")
        ab.bind("<Button-1>", lambda e: self._add_exc())

    def _is_tech(self, name):
        nl = name.lower()
        for t in TECH_PRODUCTS:
            if t in nl:
                return True
        return False

    def _load_all_products(self, exclude_names):
        result = self.db.execute(
            "SELECT Название, Калории_на_100г, Белки_на_100г, "
            "Жиры_на_100г, Углеводы_на_100г, Категория "
            "FROM Продукты ORDER BY Название"
        )
        if not result:
            return []

        filtered = []
        for p in result:
            if self._is_tech(p[0]):
                continue
            skip = False
            for ex in exclude_names:
                if ex.lower() in p[0].lower():
                    skip = True
                    break
            if not skip:
                filtered.append(p)
        return filtered

    def _open_product_picker(self, title):
        products_data = self.db.execute(
            "SELECT Название FROM Продукты "
            "WHERE Категория NOT IN ('Прочее', 'Спорт', 'Жиры') "
            "ORDER BY Название"
        )
        if not products_data:
            messagebox.showwarning("Ошибка", "База продуктов пуста")
            return None

        products = [row[0] for row in products_data
                    if not self._is_tech(row[0])]

        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("400x520")
        dialog.configure(bg="#FFFFFF")
        dialog.transient(self.root)

        tk.Label(dialog, text=title,
                 font=("TkDefaultFont", 12, "bold"),
                 bg="#FFFFFF", fg="#333333").pack(pady=15)

        search_var = tk.StringVar()
        tk.Entry(dialog, textvariable=search_var,
                 font=("TkDefaultFont", 11),
                 bg="#E0E0E0", bd=1, relief="solid").pack(
            fill="x", padx=20, ipady=6
        )

        list_frame = tk.Frame(dialog, bg="#FFFFFF")
        list_frame.pack(fill="both", expand=True, padx=20, pady=10)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")

        listbox = tk.Listbox(list_frame,
                             font=("TkDefaultFont", 10),
                             bg="#F5F5F5", bd=0,
                             yscrollcommand=scrollbar.set)
        listbox.pack(fill="both", expand=True)
        scrollbar.config(command=listbox.yview)

        def fill_list():
            listbox.delete(0, tk.END)
            q = search_var.get().strip().lower()
            for p in products:
                if not q or q in p.lower():
                    listbox.insert(tk.END, p)

        fill_list()
        search_var.trace_add("write", lambda *a: fill_list())

        result = {"value": None}

        def on_select():
            sel = listbox.curselection()
            if sel:
                result["value"] = listbox.get(sel[0])
            dialog.destroy()

        btns = tk.Frame(dialog, bg="#FFFFFF")
        btns.pack(fill="x", padx=20, pady=15)

        tk.Button(btns, text="Отмена",
                  font=("TkDefaultFont", 11),
                  bg="#FFFFFF", fg="#333333",
                  bd=1, relief="solid",
                  command=dialog.destroy).pack(side="left", padx=5)

        tk.Button(btns, text="Выбрать",
                  font=("TkDefaultFont", 11, "bold"),
                  bg="#7E57C2", fg="#FFFFFF",
                  bd=0,
                  command=on_select).pack(side="right", padx=5)

        listbox.bind("<Double-Button-1>", lambda e: on_select())
        dialog.after(150, lambda: self._safe_grab(dialog))

        self.root.wait_window(dialog)
        return result["value"]

    def _safe_grab(self, dialog):
        try:
            dialog.grab_set()
        except tk.TclError:
            pass

    def _add_pref(self):
        name = self._open_product_picker("Выберите предпочтение")
        if name and name not in self.preferences:
            self.preferences.append(name)
            self._save_list("preferences", self.preferences)
            self._refresh_prefs()

    def _add_exc(self):
        name = self._open_product_picker("Выберите исключение")
        if name and name not in self.exclusions:
            self.exclusions.append(name)
            self._save_list("exclusions", self.exclusions)
            self._refresh_excs()

    def _remove_pref(self, name):
        if name in self.preferences:
            self.preferences.remove(name)
            self._save_list("preferences", self.preferences)
            self._refresh_prefs()

    def _remove_exc(self, name):
        if name in self.exclusions:
            self.exclusions.remove(name)
            self._save_list("exclusions", self.exclusions)
            self._refresh_excs()

    def _generate_menu(self):
        """Генерирует меню с 4 ингредиентами."""
        try:
            target_cal = int(self.goal_cal.get())
            meals_cnt = int(self.meals_count.get())
        except ValueError:
            messagebox.showerror("Ошибка", "Проверьте параметры")
            return

        exclude_names = list(self.exclusions)

        all_products = self._load_all_products(exclude_names)
        if not all_products:
            messagebox.showwarning("Ошибка",
                                   "Нет подходящих продуктов")
            return

        # Индексируем по категориям
        by_cat = {}
        for p in all_products:
            by_cat.setdefault(p[5], []).append(p)

        # Предпочтения
        pref_products = []
        for pref_name in self.preferences:
            for p in all_products:
                if p[0] == pref_name:
                    pref_products.append(p)
                    break

        pref_by_cat = {}
        for p in pref_products:
            pref_by_cat.setdefault(p[5], []).append(p)

        # Приёмы
        if meals_cnt == 3:
            meals_def = [
                ("Завтрак", 0.30, "08:00"),
                ("Обед", 0.40, "13:00"),
                ("Ужин", 0.30, "19:00"),
            ]
        elif meals_cnt == 4:
            meals_def = [
                ("Завтрак", 0.25, "08:00"),
                ("Обед", 0.35, "13:00"),
                ("Перекус", 0.10, "16:30"),
                ("Ужин", 0.30, "19:30"),
            ]
        else:
            meals_def = [
                ("Завтрак", 0.25, "08:00"),
                ("Обед", 0.30, "13:00"),
                ("Перекус", 0.10, "16:30"),
                ("Полдник", 0.05, "17:30"),
                ("Ужин", 0.30, "19:30"),
            ]

        self.menu_result = []
        total_cal = total_p = total_f = total_c = 0

        used_prefs = set()

        for idx, (meal_name, weight, time_str) in enumerate(meals_def):
            meal_target = target_cal * weight

            # Собираем продукты
            recipe_products = self._pick_recipe_products(
                idx, meals_cnt, by_cat, pref_by_cat,
                used_prefs, all_products
            )

            if not recipe_products:
                continue

            # Масштабируем порции до цели
            portions = [150] * len(recipe_products)

            for _ in range(30):
                current_cal = sum(
                    (recipe_products[i][1] or 0) * portions[i] / 100
                    for i in range(len(recipe_products))
                )
                if current_cal == 0:
                    break
                ratio = meal_target / current_cal
                if 0.9 < ratio < 1.1:
                    break
                for i in range(len(portions)):
                    portions[i] = int(portions[i] * ratio)
                    portions[i] = max(20, min(portions[i], 500))

            # Считаем КБЖУ
            dish_parts = []
            meal_cal = meal_p = meal_f = meal_c = 0

            for i, p in enumerate(recipe_products):
                name = p[0]
                cal100 = p[1] or 0
                protein100 = p[2] or 0
                fat100 = p[3] or 0
                carbs100 = p[4] or 0
                portion = portions[i]

                p_cal = cal100 * portion / 100
                p_protein = protein100 * portion / 100
                p_fat = fat100 * portion / 100
                p_carbs = carbs100 * portion / 100

                dish_parts.append(f"{name} — {portion} г")
                meal_cal += p_cal
                meal_p += p_protein
                meal_f += p_fat
                meal_c += p_carbs

            # Название
            dish_name = self._name_dish(recipe_products, meal_name)

            self.menu_result.append({
                "meal": meal_name,
                "time": time_str,
                "dish_name": dish_name,
                "ingredients": ", ".join(dish_parts),
                "cal": int(meal_cal),
                "p": int(meal_p),
                "f": int(meal_f),
                "c": int(meal_c),
            })

            total_cal += meal_cal
            total_p += meal_p
            total_f += meal_f
            total_c += meal_c

        self.menu_totals = {
            "cal": int(total_cal),
            "p": int(total_p),
            "f": int(total_f),
            "c": int(total_c),
        }

        self._draw_menu_rows()
        self._draw_total()
        self._draw_status()

    def _pick_recipe_products(self, meal_idx, meals_cnt,
                              by_cat, pref_by_cat,
                              used_prefs, all_products):
        """Собирает 4 ингредиента по рецепту."""
        result = []

        def take_pref(cat):
            if cat in pref_by_cat:
                for p in pref_by_cat[cat]:
                    if p[0] not in used_prefs:
                        used_prefs.add(p[0])
                        return p
            return None

        def take_any(cat):
            if cat in by_cat and by_cat[cat]:
                return random.choice(by_cat[cat])
            return None

        def add(cat):
            p = take_pref(cat)
            if p:
                result.append(p)
                return True
            p = take_any(cat)
            if p:
                result.append(p)
                return True
            return False

        # Рецепты
        if meals_cnt == 3:
            if meal_idx == 0:
                add("Крупы"); add("Молочные")
                add("Фрукты"); add("Напитки")
            elif meal_idx == 1:
                (add("Мясо") or add("Рыба"))
                (add("Крупы") or add("Овощи"))
                add("Овощи"); add("Хлеб")
            else:
                (add("Рыба") or add("Мясо"))
                add("Овощи"); add("Овощи"); add("Молочные")
        elif meals_cnt == 4:
            if meal_idx == 0:
                add("Крупы"); add("Молочные")
                add("Фрукты"); add("Напитки")
            elif meal_idx == 1:
                (add("Мясо") or add("Рыба"))
                add("Крупы"); add("Овощи"); add("Хлеб")
            elif meal_idx == 2:
                add("Фрукты"); add("Орехи"); add("Сладкое")
            else:
                (add("Рыба") or add("Мясо"))
                add("Овощи"); add("Овощи"); add("Молочные")
        else:
            if meal_idx == 0:
                add("Крупы"); add("Молочные")
                add("Фрукты"); add("Напитки")
            elif meal_idx == 1:
                (add("Мясо") or add("Рыба"))
                add("Крупы"); add("Овощи"); add("Хлеб")
            elif meal_idx == 2:
                add("Фрукты"); add("Орехи")
            elif meal_idx == 3:
                add("Молочные"); add("Фрукты")
            else:
                (add("Рыба") or add("Мясо"))
                add("Овощи"); add("Овощи"); add("Молочные")

        # Добираем до 4
        attempts = 0
        while len(result) < 4 and attempts < 20:
            p = random.choice(all_products)
            if p not in result:
                result.append(p)
            attempts += 1

        return result[:4]

    def _name_dish(self, products, meal_name):
        """Название блюда."""
        cats = [p[5] for p in products]
        names = [p[0] for p in products]

        if meal_name == "Завтрак":
            if "Крупы" in cats:
                grain = next(p[0] for p in products if p[5] == "Крупы")
                if "Молочные" in cats:
                    return f"Каша «{grain}» на молоке"
                if "Фрукты" in cats:
                    fruit = next(p[0] for p in products
                                 if p[5] == "Фрукты")
                    return f"Каша «{grain}» с {fruit.lower()}"
                return f"Каша «{grain}»"
            if "Яйца" in cats:
                if "Овощи" in cats:
                    return "Омлет с овощами"
                return "Яичница"

        if meal_name == "Обед":
            if "Мясо" in cats:
                meat = next(p[0] for p in products if p[5] == "Мясо")
                if "Крупы" in cats:
                    grain = next(p[0] for p in products
                                 if p[5] == "Крупы")
                    return f"{meat} с {grain.lower()} и овощами"
                return f"{meat} с овощами"
            if "Рыба" in cats:
                fish = next(p[0] for p in products if p[5] == "Рыба")
                return f"{fish} с гарниром"

        if meal_name == "Перекус":
            if "Фрукты" in cats and "Орехи" in cats:
                return "Фрукты с орехами"
            if "Фрукты" in cats:
                return "Фруктовая тарелка"
            if "Сладкое" in cats:
                return "Десерт"

        if meal_name == "Ужин":
            if "Рыба" in cats:
                fish = next(p[0] for p in products if p[5] == "Рыба")
                return f"{fish} с овощами"
            if "Мясо" in cats:
                meat = next(p[0] for p in products if p[5] == "Мясо")
                return f"{meat} с овощами"

        return " и ".join(names[:2])

    def _draw_menu_rows(self, event=None):
        canvas = self.menu_canvas
        canvas.delete("all")

        if not self.menu_result:
            canvas.create_text(
                canvas.winfo_width() // 2, 100,
                text="Нажмите «Подобрать меню»",
                fill=self.FG_MUTED,
                font=("TkDefaultFont", 11)
            )
            return

        width = canvas.winfo_width()
        row_h = 85
        col_x = [10, 130, 480, 590, 670, 750, 830]

        for i, row in enumerate(self.menu_result):
            y1 = i * row_h
            y2 = y1 + row_h

            bg = self.BG_CARD if i % 2 == 0 else "#FAFAFA"
            canvas.create_rectangle(0, y1, width, y2,
                                    fill=bg, outline="")
            canvas.create_line(0, y2, width, y2, fill="#EEEEEE")

            canvas.create_text(col_x[0], y1 + 15,
                               text=row["meal"], anchor="nw",
                               fill=self.FG_TEXT,
                               font=("TkDefaultFont", 10, "bold"))
            canvas.create_text(col_x[0], y1 + 38,
                               text=row["time"], anchor="nw",
                               fill=self.FG_MUTED,
                               font=("TkDefaultFont", 8))

            canvas.create_text(col_x[1], y1 + 12,
                               text=row["dish_name"], anchor="nw",
                               fill=self.FG_TEXT,
                               font=("TkDefaultFont", 10, "bold"),
                               width=340)

            canvas.create_text(col_x[1], y1 + 38,
                               text=row["ingredients"], anchor="nw",
                               fill=self.FG_MUTED,
                               font=("TkDefaultFont", 8),
                               width=340)

            canvas.create_text(col_x[2], y1 + row_h // 2,
                               text=str(row["cal"]), anchor="e",
                               fill=self.FG_TEXT,
                               font=("TkDefaultFont", 10, "bold"))
            canvas.create_text(col_x[3], y1 + row_h // 2,
                               text=f"{row['p']} г", anchor="e",
                               fill=self.FG_TEXT,
                               font=("TkDefaultFont", 9))
            canvas.create_text(col_x[4], y1 + row_h // 2,
                               text=f"{row['f']} г", anchor="e",
                               fill=self.FG_TEXT,
                               font=("TkDefaultFont", 9))
            canvas.create_text(col_x[5], y1 + row_h // 2,
                               text=f"{row['c']} г", anchor="e",
                               fill=self.FG_TEXT,
                               font=("TkDefaultFont", 9))

        canvas.configure(height=row_h * len(self.menu_result))

    def _draw_total(self, event=None):
        canvas = self.total_canvas
        canvas.delete("all")

        if not self.menu_totals:
            return

        width = canvas.winfo_width()

        create_rounded_rect(
            canvas, 0, 5, width, 45, 8,
            fill=self.BG_ACCENT_LIGHT, outline=self.BG_ACCENT_LIGHT
        )

        canvas.create_text(20, 25,
                           text="Итого за день", anchor="w",
                           fill=self.FG_TEXT,
                           font=("TkDefaultFont", 11, "bold"))

        canvas.create_text(500, 25,
                           text=f"{self.menu_totals['cal']} ккал",
                           anchor="e",
                           fill=self.FG_ACCENT,
                           font=("TkDefaultFont", 12, "bold"))

        canvas.create_text(620, 25,
                           text=f"Белки: {self.menu_totals['p']} г",
                           anchor="e",
                           fill=self.FG_TEXT,
                           font=("TkDefaultFont", 9))
        canvas.create_text(720, 25,
                           text=f"Жиры: {self.menu_totals['f']} г",
                           anchor="e",
                           fill=self.FG_TEXT,
                           font=("TkDefaultFont", 9))
        canvas.create_text(830, 25,
                           text=f"Углеводы: {self.menu_totals['c']} г",
                           anchor="e",
                           fill=self.FG_TEXT,
                           font=("TkDefaultFont", 9))

    def _draw_status(self, event=None):
        canvas = self.status_canvas
        canvas.delete("all")

        if not self.menu_totals:
            return

        width = canvas.winfo_width()

        create_rounded_rect(
            canvas, 0, 5, width, 35, 8,
            fill="#F5F5F5", outline="#F5F5F5"
        )

        diff = self.menu_totals['cal'] - int(self.goal_cal.get())
        if abs(diff) <= 100:
            text = (f"Меню соответствует цели: отклонение {diff} ккал. "
                    f"Баланс КБЖУ рассчитан на один день.")
        else:
            text = (f"Отклонение от цели: {diff} ккал. "
                    f"Рекомендуется скорректировать порции.")

        canvas.create_text(width // 2, 20,
                           text=text, anchor="center",
                           fill=self.FG_MUTED,
                           font=("TkDefaultFont", 9))

    def _save(self):
        if not self.menu_result:
            messagebox.showwarning("Ошибка", "Сначала подберите меню")
            return

        messagebox.showinfo(
            "Успех",
            f"Меню сохранено!\n"
            f"Итого: {self.menu_totals['cal']} ккал"
        )
        self.root.destroy()

    def run(self):
        self.root.wait_window()