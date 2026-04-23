import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

# Файл для хранения данных
DATA_FILE = 'movies.json'

# Загрузка данных
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

# Сохранение данных
def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

class MovieLibraryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Movie Library")
        self.data = load_data()

        self.create_widgets()
        self.populate_table()

    def create_widgets(self):
        # Ввод данных
        ttk.Label(self.root, text="Название:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.title_entry = ttk.Entry(self.root)
        self.title_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.root, text="Жанр:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.genre_entry = ttk.Entry(self.root)
        self.genre_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(self.root, text="Год выпуска:").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.year_entry = ttk.Entry(self.root)
        self.year_entry.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(self.root, text="Рейтинг (0-10):").grid(row=3, column=0, padx=5, pady=5, sticky='w')
        self.rating_entry = ttk.Entry(self.root)
        self.rating_entry.grid(row=3, column=1, padx=5, pady=5)

        # Кнопка добавить
        self.add_button = ttk.Button(self.root, text="Добавить фильм", command=self.add_movie)
        self.add_button.grid(row=4, column=0, columnspan=2, pady=10)

        # Фильтры
        ttk.Label(self.root, text="Фильтр по жанру:").grid(row=0, column=2, padx=5, pady=5, sticky='w')
        self.genre_filter_var = tk.StringVar()
        self.genre_filter_var.set("Все")
        genres = ["Все"] + list({movie['genre'] for movie in self.data})
        self.genre_filter = ttk.OptionMenu(self.root, self.genre_filter_var, "Все", *genres, command=self.apply_filters)
        self.genre_filter.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(self.root, text="Фильтр по году:").grid(row=1, column=2, padx=5, pady=5, sticky='w')
        self.year_filter_var = tk.StringVar()
        self.year_filter_var.set("Все")
        self.year_filter = ttk.OptionMenu(self.root, self.year_filter_var, "Все", "Все")
        self.year_filter.grid(row=1, column=3, padx=5, pady=5)
        self.year_filter_var.trace('w', lambda *args: self.apply_filters())

        # Таблица фильмов
        columns = ("Название", "Жанр", "Год", "Рейтинг")
        self.tree = ttk.Treeview(self.root, columns=columns, show='headings')
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        self.tree.grid(row=5, column=0, columnspan=4, padx=5, pady=5)

    def add_movie(self):
        title = self.title_entry.get().strip()
        genre = self.genre_entry.get().strip()
        year = self.year_entry.get().strip()
        rating = self.rating_entry.get().strip()

        # Проверка корректности
        if not title or not genre or not year or not rating:
            messagebox.showwarning("Ошибка", "Заполните все поля.")
            return
        if not year.isdigit():
            messagebox.showwarning("Ошибка", "Год должен быть числом.")
            return
        try:
            rating_value = float(rating)
            if not (0 <= rating_value <= 10):
                raise ValueError
        except ValueError:
            messagebox.showwarning("Ошибка", "Рейтинг должен быть числом от 0 до 10.")
            return

        movie = {
            "title": title,
            "genre": genre,
            "year": int(year),
            "rating": rating_value
        }

        self.data.append(movie)
        save_data(self.data)
        self.clear_entries()
        self.update_filters()
        self.populate_table()

    def clear_entries(self):
        self.title_entry.delete(0, tk.END)
        self.genre_entry.delete(0, tk.END)
        self.year_entry.delete(0, tk.END)
        self.rating_entry.delete(0, tk.END)

    def populate_table(self, filtered_data=None):
        for row in self.tree.get_children():
            self.tree.delete(row)
        data_to_show = filtered_data if filtered_data is not None else self.data
        for movie in data_to_show:
            self.tree.insert('', tk.END, values=(
                movie['title'],
                movie['genre'],
                movie['year'],
                movie['rating']
            ))

    def apply_filters(self, *args):
        genre_filter = self.genre_filter_var.get()
        year_filter = self.year_filter_var.get()

        filtered = self.data
        if genre_filter != "Все":
            filtered = [m for m in filtered if m['genre'] == genre_filter]
        if year_filter != "Все":
            if year_filter.isdigit():
                filtered = [m for m in filtered if m['year'] == int(year_filter)]
        self.populate_table(filtered)

    def update_filters(self):
        # Обновляем список фильтров по жанру и году
        genres = {"Все"} | {movie['genre'] for movie in self.data}
        years = {"Все"} | {str(movie['year']) for movie in self.data}
        menu_genre = self.genre_filter["menu"]
        menu_year = self.year_filter["menu"]
        menu_genre.delete(0, 'end')
        menu_year.delete(0, 'end')
        for g in sorted(genres):
            menu_genre.add_command(label=g, command=lambda value=g: self.genre_filter_var.set(value))
        for y in sorted(years):
            menu_year.add_command(label=y, command=lambda value=y: self.year_filter_var.set(value))
        # Обновляем фильтр по году при необходимости
        if self.year_filter_var.get() not in years:
            self.year_filter_var.set("Все")

if __name__ == "__main__":
    root = tk.Tk()
    app = MovieLibraryApp(root)
    root.mainloop()