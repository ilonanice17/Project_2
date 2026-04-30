import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

class MovieLibraryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Movie Library (Личная кинотека)")
        self.root.geometry("850x600")
        self.movies = []
        self.data_file = "movies.json"

        self._create_widgets()
        self._load_data()

    def _create_widgets(self):
        # --- Ввод данных ---
        input_frame = ttk.LabelFrame(self.root, text="Добавить фильм")
        input_frame.pack(padx=10, pady=5, fill="x")

        ttk.Label(input_frame, text="Название:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.entry_title = ttk.Entry(input_frame, width=35)
        self.entry_title.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Жанр:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.entry_genre = ttk.Entry(input_frame, width=15)
        self.entry_genre.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(input_frame, text="Год:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.entry_year = ttk.Entry(input_frame, width=10)
        self.entry_year.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Рейтинг:").grid(row=1, column=2, padx=5, pady=5, sticky="e")
        self.entry_rating = ttk.Entry(input_frame, width=10)
        self.entry_rating.grid(row=1, column=3, padx=5, pady=5)

        self.btn_add = ttk.Button(input_frame, text="Добавить фильм", command=self._add_movie)
        self.btn_add.grid(row=0, column=4, rowspan=2, padx=10, pady=5)

        # --- Фильтрация ---
        filter_frame = ttk.LabelFrame(self.root, text="Фильтр")
        filter_frame.pack(padx=10, pady=5, fill="x")

        ttk.Label(filter_frame, text="Жанр:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.combo_filter_genre = ttk.Combobox(filter_frame, width=15, state="readonly")
        self.combo_filter_genre.grid(row=0, column=1, padx=5, pady=5)
        self.combo_filter_genre.bind("<<ComboboxSelected>>", lambda e: self._apply_filter())

        ttk.Label(filter_frame, text="Год:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.entry_filter_year = ttk.Entry(filter_frame, width=10)
        self.entry_filter_year.grid(row=0, column=3, padx=5, pady=5)
        self.entry_filter_year.bind("<Return>", lambda e: self._apply_filter())

        self.btn_filter = ttk.Button(filter_frame, text="Применить фильтр", command=self._apply_filter)
        self.btn_filter.grid(row=0, column=4, padx=5, pady=5)
        self.btn_reset = ttk.Button(filter_frame, text="Сбросить", command=self._reset_filter)
        self.btn_reset.grid(row=0, column=5, padx=5, pady=5)

        # --- Таблица ---
        table_frame = ttk.Frame(self.root)
        table_frame.pack(padx=10, pady=5, fill="both", expand=True)

        columns = ("title", "genre", "year", "rating")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        self.tree.heading("title", text="Название")
        self.tree.heading("genre", text="Жанр")
        self.tree.heading("year", text="Год выпуска")
        self.tree.heading("rating", text="Рейтинг")

        self.tree.column("title", width=350)
        self.tree.column("genre", width=120)
        self.tree.column("year", width=80, anchor="center")
        self.tree.column("rating", width=80, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # --- Кнопки сохранения/загрузки ---
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(padx=10, pady=5, fill="x")
        ttk.Button(btn_frame, text="💾 Сохранить в JSON", command=self._save_data).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="📂 Загрузить из JSON", command=self._load_data).pack(side="left", padx=5)

    def _validate_input(self):
        title = self.entry_title.get().strip()
        genre = self.entry_genre.get().strip()
        year_str = self.entry_year.get().strip()
        rating_str = self.entry_rating.get().strip()

        if not title or not genre:
            messagebox.showwarning("Ошибка ввода", "Поля «Название» и «Жанр» не могут быть пустыми.")
            return None

        try:
            year = int(year_str)
        except ValueError:
            messagebox.showwarning("Ошибка ввода", "Год должен быть целым числом.")
            return None

        try:
            rating = float(rating_str)
            if not (0.0 <= rating <= 10.0):
                raise ValueError
        except ValueError:
            messagebox.showwarning("Ошибка ввода", "Рейтинг должен быть числом от 0 до 10.")
            return None

        return {"title": title, "genre": genre, "year": year, "rating": round(rating, 1)}

    def _add_movie(self):
        data = self._validate_input()
        if data:
            self.movies.append(data)
            self._update_table()
            self._update_genre_combobox()
            self._clear_inputs()
            messagebox.showinfo("Успех", f"Фильм «{data['title']}» добавлен.")

    def _clear_inputs(self):
        self.entry_title.delete(0, tk.END)
        self.entry_genre.delete(0, tk.END)
        self.entry_year.delete(0, tk.END)
        self.entry_rating.delete(0, tk.END)

    def _update_genre_combobox(self):
        genres = sorted(list(set(m["genre"] for m in self.movies)))
        self.combo_filter_genre["values"] = ["", *genres]
        if self.combo_filter_genre.get() not in genres:
            self.combo_filter_genre.set("")

    def _apply_filter(self):
        genre_filter = self.combo_filter_genre.get()
        year_filter_str = self.entry_filter_year.get().strip()

        filtered = self.movies
        if genre_filter:
            filtered = [m for m in filtered if m["genre"] == genre_filter]
        if year_filter_str:
            try:
                year_val = int(year_filter_str)
                filtered = [m for m in filtered if m["year"] == year_val]
            except ValueError:
                messagebox.showwarning("Ошибка фильтра", "Год фильтра должен быть числом.")
                return

        self._render_table(filtered)

    def _reset_filter(self):
        self.combo_filter_genre.set("")
        self.entry_filter_year.delete(0, tk.END)
        self._update_table()

    def _update_table(self):
        self._render_table(self.movies)

    def _render_table(self, data_list):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for m in data_list:
            self.tree.insert("", tk.END, values=(m["title"], m["genre"], m["year"], m["rating"]))

    def _save_data(self):
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(self.movies, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("Успех", "Данные сохранены в movies.json")
        except Exception as e:
            messagebox.showerror("Ошибка сохранения", str(e))

    def _load_data(self):
        if not os.path.exists(self.data_file):
            self.movies = []
            messagebox.showinfo("Информация", "Файл movies.json не найден. Создана новая коллекция.")
        else:
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    self.movies = json.load(f)
            except Exception as e:
                messagebox.showerror("Ошибка загрузки", f"Не удалось прочитать файл:\n{e}")
                self.movies = []
        self._update_table()
        self._update_genre_combobox()

if __name__ == "__main__":
    root = tk.Tk()
    app = MovieLibraryApp(root)
    root.mainloop()
