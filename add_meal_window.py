"""Экран добавления приёма пищи — точно по макету."""

import tkinter as tk
from tkinter import messagebox
from datetime import datetime


class AddMealWindow:
    BG_MAIN = "#F0F0F0"
    BG_CARD = "#FFFFFF"
    BG_INPUT = "#E0E0E0"
    BG_BUTTON = "#7E57C2"
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
        self.root.title("Добавить приём пищи")
        self.root.geometry("720x820")
        self.root.configure(bg=self.BG_MAIN)
        self.root.resizable(False, False)

        self.selected_id = None
        self.selected_product = None
        self.rows_widgets = {}

        # Загружаем продукты
        self.all_products = []
        rows = self.db.execute(
            "SELECT Код_продукта, Название, Калории_на_100г, "
            "Белки_на_100г, Жиры_на_100г, Углеводы_на_100г "
            "FROM Продукты ORDER BY Название"
        )
        if rows:
            self.all_products = rows
            print(f"✅ Загружено продуктов: {len(self.all_products)}")

        self._build_ui()
        self._render_rows(self.all_products)

    def _build_ui(self):
        card = tk.Frame(self.root, bg=self.BG_CARD)
        card.pack(fill="both", expand=True, padx=20, pady=20)

        # ==== ЗАГОЛОВОК ====
        head = tk.Frame(card, bg=self.BG_CARD)
        head.pack(fill="x", padx=20, pady=(15, 10))

        tk.Label(head, text="Добавить приём пищи",
                 font=("TkDefaultFont", 15, "bold"),
                 bg=self.BG_CARD, fg=self.FG_TEXT).pack(side="left")

        close = tk.Label(head, text="✕",
                         font=("TkDefaultFont", 18, "bold"),
                         bg=self.BG_CARD, fg="#E53935",
                         cursor="hand2")
        close.pack(side="right")
        close.bind("<Button-1>", lambda e: self.root.destroy())

        tk.Frame(card, bg="#E0E0E0", height=1).pack(fill="x", padx=20)

        # ==== ПАРАМЕТРЫ ====
        tk.Label(card, text="Параметры приёма",
                 font=("TkDefaultFont", 11, "bold"),
                 bg=self.BG_CARD, fg=self.FG_TEXT).pack(anchor="w",
                                                        padx=20,
                                                        pady=(15, 8))

        params = tk.Frame(card, bg=self.BG_CARD)
        params.pack(fill="x", padx=20, pady=(0, 15))

        # Тип
        c1 = tk.Frame(params, bg=self.BG_CARD)
        c1.pack(side="left", padx=(0, 20))

        tk.Label(c1, text="Тип приёма",
                 font=("TkDefaultFont", 9),
                 bg=self.BG_CARD, fg=self.FG_MUTED).pack(anchor="w")

        self.meal_var = tk.StringVar(value="Завтрак")
        meal_frame = tk.Frame(c1, bg=self.BORDER_BLACK)
        meal_frame.pack(pady=(3, 0))
        meal_inner = tk.Frame(meal_frame, bg=self.BG_INPUT)
        meal_inner.pack(padx=1, pady=1)

        meal_lbl = tk.Label(meal_inner, textvariable=self.meal_var,
                            font=("TkDefaultFont", 10),
                            bg=self.BG_INPUT, fg=self.FG_TEXT,
                            width=18, anchor="w",
                            cursor="hand2")
        meal_lbl.pack(side="left", ipady=8, padx=(10, 0))

        arrow = tk.Label(meal_inner, text="▼",
                         font=("TkDefaultFont", 8),
                         bg=self.BG_INPUT, fg=self.FG_TEXT,
                         cursor="hand2")
        arrow.pack(side="right", padx=10)

        menu = tk.Menu(self.root, tearoff=0)
        for mt in ["Завтрак", "Обед", "Ужин", "Перекус"]:
            menu.add_command(label=mt,
                             command=lambda m=mt: self.meal_var.set(m))

        def open_menu(e):
            menu.tk_popup(e.x_root, e.y_root)

        for w in [meal_inner, meal_lbl, arrow]:
            w.bind("<Button-1>", open_menu)

        # Дата
        c2 = tk.Frame(params, bg=self.BG_CARD)
        c2.pack(side="left")

        tk.Label(c2, text="Дата",
                 font=("TkDefaultFont", 9),
                 bg=self.BG_CARD, fg=self.FG_MUTED).pack(anchor="w")

        self.date_var = tk.StringVar(
            value=datetime.now().strftime("%d.%m.%Y")
        )

        date_frame = tk.Frame(c2, bg=self.BORDER_BLACK)
        date_frame.pack(pady=(3, 0))
        date_inner = tk.Frame(date_frame, bg=self.BG_INPUT)
        date_inner.pack(padx=1, pady=1)

        tk.Entry(date_inner, textvariable=self.date_var,
                 font=("TkDefaultFont", 10),
                 bg=self.BG_INPUT, bd=0, width=18).pack(ipady=8, padx=10)

        # ==== ПОИСК ====
        tk.Label(card, text="Выбор продукта",
                 font=("TkDefaultFont", 11, "bold"),
                 bg=self.BG_CARD, fg=self.FG_TEXT).pack(anchor="w",
                                                        padx=20,
                                                        pady=(0, 5))

        tk.Label(card, text="Поиск продукта",
                 font=("TkDefaultFont", 9),
                 bg=self.BG_CARD, fg=self.FG_MUTED).pack(anchor="w",
                                                         padx=20)

        sf = tk.Frame(card, bg=self.BORDER_BLACK)
        sf.pack(fill="x", padx=20, pady=(3, 10))
        sf_inner = tk.Frame(sf, bg=self.BG_INPUT)
        sf_inner.pack(fill="x", padx=1, pady=1)

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *a: self._on_search())

        tk.Entry(sf_inner, textvariable=self.search_var,
                 font=("TkDefaultFont", 11),
                 bg=self.BG_INPUT, bd=0).pack(fill="x", ipady=8, padx=12)

        # ==== ТАБЛИЦА СО СКРОЛЛОМ ====
        table_outer = tk.Frame(card, bg=self.BORDER_BLACK)
        table_outer.pack(fill="x", padx=20, pady=(0, 10))
        table_inner = tk.Frame(table_outer, bg=self.BG_CARD)
        table_inner.pack(fill="x", padx=1, pady=1)

        # Шапка
        th = tk.Frame(table_inner, bg="#F5F5F5")
        th.pack(fill="x")

        tk.Label(th, text="Название продукта",
                 font=("TkDefaultFont", 10, "bold"),
                 bg="#F5F5F5", fg=self.FG_TEXT).pack(side="left",
                                                      padx=40, pady=8)
        tk.Label(th, text="Ккал/100г",
                 font=("TkDefaultFont", 10, "bold"),
                 bg="#F5F5F5", fg=self.FG_TEXT).pack(side="right",
                                                      padx=25)

        tk.Frame(table_inner, bg="#E0E0E0", height=1).pack(fill="x")

        # Область со скроллом
        list_frame = tk.Frame(table_inner, bg=self.BG_CARD, height=220)
        list_frame.pack(fill="x")
        list_frame.pack_propagate(False)

        self.canvas = tk.Canvas(list_frame, bg=self.BG_CARD,
                                highlightthickness=0, height=220)
        scrollbar = tk.Scrollbar(list_frame, orient="vertical",
                                 command=self.canvas.yview)
        self.rows_frame = tk.Frame(self.canvas, bg=self.BG_CARD)

        self.rows_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas_window = self.canvas.create_window(
            (0, 0), window=self.rows_frame, anchor="nw"
        )

        # Растягиваем внутренний фрейм по ширине canvas
        self.canvas.bind(
            "<Configure>",
            lambda e: self.canvas.itemconfig(
                self.canvas_window, width=e.width
            )
        )

        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Прокрутка колёсиком
        def on_mousewheel(event):
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)),
                                     "units")

        self.canvas.bind_all("<MouseWheel>", on_mousewheel)

        # ==== ПОРЦИЯ ====
        tk.Label(card, text="Порция",
                 font=("TkDefaultFont", 11, "bold"),
                 bg=self.BG_CARD, fg=self.FG_TEXT).pack(anchor="w",
                                                        padx=20,
                                                        pady=(10, 5))

        portion = tk.Frame(card, bg=self.BG_CARD)
        portion.pack(fill="x", padx=20, pady=(0, 15))

        tk.Label(portion, text="Вес, г",
                 font=("TkDefaultFont", 9),
                 bg=self.BG_CARD, fg=self.FG_MUTED).grid(row=0,
                                                         column=0,
                                                         sticky="w")

        w_frame = tk.Frame(portion, bg=self.BORDER_BLACK)
        w_frame.grid(row=1, column=0, pady=(3, 0))
        w_inner = tk.Frame(w_frame, bg=self.BG_INPUT)
        w_inner.pack(padx=1, pady=1)

        self.weight_var = tk.StringVar(value="150")
        self.weight_var.trace_add("write", lambda *a: self._update_total())

        tk.Entry(w_inner, textvariable=self.weight_var,
                 font=("TkDefaultFont", 11, "bold"),
                 bg=self.BG_INPUT, bd=0, width=10).pack(ipady=10, padx=12)

        total = tk.Frame(portion, bg=self.BG_ACCENT_LIGHT)
        total.grid(row=1, column=1, padx=(15, 0))

        self.total_label = tk.Label(
            total, text="Итого: 0 ккал",
            font=("TkDefaultFont", 11, "bold"),
            bg=self.BG_ACCENT_LIGHT, fg=self.FG_ACCENT,
            padx=15, pady=10
        )
        self.total_label.pack(side="left")

        self.total_kbzhu = tk.Label(
            total, text="Белки: 0 | Жиры: 0 | Углеводы: 0",
            font=("TkDefaultFont", 10),
            bg=self.BG_ACCENT_LIGHT, fg=self.FG_TEXT,
            padx=15, pady=10
        )
        self.total_kbzhu.pack(side="left")

        # ==== КНОПКИ ====
        btns = tk.Frame(card, bg=self.BG_CARD)
        btns.pack(fill="x", padx=20, pady=(0, 20))

        c_frame = tk.Frame(btns, bg=self.BORDER_BLACK)
        c_frame.pack(side="left", padx=(0, 12))
        c_inner = tk.Frame(c_frame, bg=self.BG_CARD)
        c_inner.pack(padx=1, pady=1)
        tk.Button(c_inner, text="Отмена",
                  font=("TkDefaultFont", 11),
                  bg=self.BG_CARD, fg=self.FG_TEXT,
                  bd=0, cursor="hand2",
                  command=self.root.destroy,
                  width=16).pack(ipady=10)

        s_frame = tk.Frame(btns, bg=self.BORDER_BLACK)
        s_frame.pack(side="left")
        s_inner = tk.Frame(s_frame, bg=self.BG_BUTTON)
        s_inner.pack(padx=1, pady=1)
        tk.Button(s_inner, text="Сохранить",
                  font=("TkDefaultFont", 11, "bold"),
                  bg=self.BG_BUTTON, fg=self.FG_WHITE,
                  bd=0, cursor="hand2",
                  command=self._save,
                  width=16).pack(ipady=10)

    def _render_rows(self, rows):
        """Отрисовывает строки таблицы."""
        for w in self.rows_frame.winfo_children():
            w.destroy()

        self.rows_widgets = {}

        if not rows:
            tk.Label(self.rows_frame,
                     text="Продукты не найдены",
                     font=("TkDefaultFont", 10),
                     bg=self.BG_CARD, fg=self.FG_MUTED,
                     pady=15).pack()
            return

        for r in rows:
            pid, name, cal = r[0], r[1], r[2]

            row = tk.Frame(self.rows_frame, bg=self.BG_CARD,
                           cursor="hand2")
            row.pack(fill="x")

            # Кружок
            circle = tk.Label(row, text="◯",
                              font=("TkDefaultFont", 14),
                              bg=self.BG_CARD, fg="#BDBDBD",
                              width=2, cursor="hand2")
            circle.pack(side="left", padx=(15, 8), pady=8)

            name_lbl = tk.Label(row, text=name,
                                font=("TkDefaultFont", 10),
                                bg=self.BG_CARD, fg=self.FG_TEXT,
                                anchor="w", cursor="hand2")
            name_lbl.pack(side="left", pady=10,
                          fill="x", expand=True)

            cal_lbl = tk.Label(row, text=f"{cal:.0f}",
                               font=("TkDefaultFont", 10),
                               bg=self.BG_CARD, fg=self.FG_TEXT,
                               cursor="hand2")
            cal_lbl.pack(side="right", padx=25, pady=10)

            tk.Frame(self.rows_frame, bg="#F0F0F0",
                     height=1).pack(fill="x")

            self.rows_widgets[pid] = (row, circle,
                                      name_lbl, cal_lbl)

            # Привязка клика
            def make_handler(product_id):
                def h(e):
                    self._select(product_id)
                return h

            handler = make_handler(pid)
            for w in [row, circle, name_lbl, cal_lbl]:
                w.bind("<Button-1>", handler)

    def _select(self, pid):
        """Выбор продукта."""
        # Сброс
        for old_pid, (r, c, n, cl) in self.rows_widgets.items():
            r.config(bg=self.BG_CARD)
            c.config(text="◯", fg="#BDBDBD", bg=self.BG_CARD)
            n.config(bg=self.BG_CARD)
            cl.config(bg=self.BG_CARD)

        # Выделение
        row, circle, name_lbl, cal_lbl = self.rows_widgets[pid]
        row.config(bg=self.BG_ACCENT_LIGHT)
        circle.config(text="●", fg=self.BG_ACCENT,
                      bg=self.BG_ACCENT_LIGHT)
        name_lbl.config(bg=self.BG_ACCENT_LIGHT)
        cal_lbl.config(bg=self.BG_ACCENT_LIGHT)

        self.selected_id = pid

        # Загружаем КБЖУ
        result = self.db.execute(
            "SELECT Калории_на_100г, Белки_на_100г, "
            "Жиры_на_100г, Углеводы_на_100г "
            "FROM Продукты WHERE Код_продукта = ?",
            (pid,)
        )
        if result and len(result) > 0:
            row_data = result[0]
            self.selected_product = {
                "cal": row_data[0] if row_data[0] is not None else 0,
                "p": row_data[1] if row_data[1] is not None else 0,
                "f": row_data[2] if row_data[2] is not None else 0,
                "c": row_data[3] if row_data[3] is not None else 0,
            }
            print(f"✅ Выбран продукт {pid}: {self.selected_product}")

        self._update_total()

    def _on_search(self):
        query = self.search_var.get().strip().lower()
        if not query:
            self._render_rows(self.all_products)
            return

        filtered = [p for p in self.all_products
                    if query in p[1].lower()]
        self._render_rows(filtered)

    def _update_total(self):
        if not self.selected_product:
            self.total_label.config(text="Итого: 0 ккал")
            self.total_kbzhu.config(
                text="Белки: 0 | Жиры: 0 | Углеводы: 0"
            )
            return

        try:
            weight = float(self.weight_var.get().replace(",", "."))
            if weight <= 0:
                raise ValueError
        except ValueError:
            return

        p = self.selected_product
        cal = p["cal"] * weight / 100
        protein = p["p"] * weight / 100
        fat = p["f"] * weight / 100
        carbs = p["c"] * weight / 100

        self.total_label.config(text=f"Итого: {cal:.0f} ккал")
        self.total_kbzhu.config(
            text=f"Белки: {protein:.1f} | "
                 f"Жиры: {fat:.1f} | "
                 f"Углеводы: {carbs:.1f}"
        )

    def _save(self):
        if not self.selected_id:
            messagebox.showwarning("Ошибка", "Выберите продукт")
            return

        try:
            weight = float(self.weight_var.get().replace(",", "."))
            if weight <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Ошибка", "Введите вес")
            return

        today = datetime.now().strftime("%Y-%m-%d")
        now = datetime.now().strftime("%H:%M")

        self.db.execute(
            "INSERT INTO ПриёмыПищи "
            "(Код_пользователя, ДатаПриёма, ТипПриёма, ВремяПриёма) "
            "VALUES (?, ?, ?, ?)",
            (self.user.user_id, today, self.meal_var.get(), now)
        )

        result = self.db.execute(
            "SELECT Код_приёма FROM ПриёмыПищи "
            "WHERE Код_пользователя = ? "
            "ORDER BY Код_приёма DESC LIMIT 1",
            (self.user.user_id,)
        )
        if not result:
            messagebox.showerror("Ошибка", "Не удалось сохранить")
            return

        meal_id = result[0][0]

        self.db.execute(
            "INSERT INTO СоставПриёма "
            "(Код_приёма, Код_продукта, Вес_г) "
            "VALUES (?, ?, ?)",
            (meal_id, self.selected_id, weight)
        )

        messagebox.showinfo("Успех", "Приём пищи сохранён")
        self.root.destroy()

    def run(self):
        self.root.wait_window()