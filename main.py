import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os
from datetime import datetime
import webbrowser

# Конфигурация
FAVORITES_FILE = "favorites.json"
GITHUB_API_URL = "https://api.github.com/users/"


class GitHubUserFinder:
    def __init__(self, root):
        self.root = root
        self.root.title("GitHub User Finder")
        self.root.geometry("700x550")
        self.root.resizable(True, True)

        # Загружаем избранное
        self.favorites = self.load_favorites()

        # Создаем интерфейс
        self.create_widgets()

    def create_widgets(self):
        # === Главный фрейм ===
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # === Заголовок ===
        title_label = ttk.Label(
            main_frame,
            text="🔍 GitHub User Finder",
            font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 15))

        # === Поле поиска ===
        ttk.Label(main_frame, text="Имя пользователя GitHub:").grid(
            row=1, column=0, sticky=tk.W, pady=(0, 5)
        )

        search_frame = ttk.Frame(main_frame)
        search_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        search_frame.columnconfigure(0, weight=1)

        self.search_entry = ttk.Entry(search_frame, font=("Arial", 11))
        self.search_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))

        search_button = ttk.Button(
            search_frame,
            text="Найти",
            command=self.search_user
        )
        search_button.grid(row=0, column=1)

        # Биндим Enter
        self.search_entry.bind("<Return>", lambda event: self.search_user())

        # === Рамка для результатов поиска ===
        self.result_frame = ttk.LabelFrame(main_frame, text="Результат поиска", padding="10")
        self.result_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        # === Рамка для избранного ===
        favorites_frame = ttk.LabelFrame(main_frame, text="⭐ Избранные пользователи", padding="10")
        favorites_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.rowconfigure(4, weight=1)

        # Список избранных
        self.favorites_listbox = tk.Listbox(
            favorites_frame,
            height=8,
            font=("Arial", 10)
        )
        self.favorites_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        favorites_frame.columnconfigure(0, weight=1)
        favorites_frame.rowconfigure(0, weight=1)

        # Скроллбар для списка
        scrollbar = ttk.Scrollbar(favorites_frame, orient=tk.VERTICAL, command=self.favorites_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.favorites_listbox.config(yscrollcommand=scrollbar.set)

        # Кнопки управления избранным
        fav_buttons = ttk.Frame(favorites_frame)
        fav_buttons.grid(row=0, column=2, sticky=tk.N, padx=(5, 0))

        ttk.Button(
            fav_buttons,
            text="Открыть профиль",
            command=self.open_favorite_profile
        ).grid(row=0, column=0, pady=(0, 5))

        ttk.Button(
            fav_buttons,
            text="Удалить",
            command=self.remove_favorite
        ).grid(row=1, column=0)

        # Заполняем список избранных
        self.refresh_favorites_list()

    def search_user(self):
        """Поиск пользователя GitHub по имени"""
        username = self.search_entry.get().strip()

        # Валидация: поле не должно быть пустым
        if not username:
            messagebox.showwarning("Предупреждение", "Введите имя пользователя!")
            return

        # Очищаем предыдущие результаты
        for widget in self.result_frame.winfo_children():
            widget.destroy()

        # Делаем запрос к GitHub API
        try:
            response = requests.get(f"{GITHUB_API_URL}{username}", timeout=10)

            if response.status_code == 200:
                user_data = response.json()
                self.display_user(user_data)
                self.current_user = user_data  # Сохраняем для добавления в избранное
            elif response.status_code == 404:
                ttk.Label(
                    self.result_frame,
                    text="❌ Пользователь не найден",
                    foreground="red",
                    font=("Arial", 10)
                ).grid(row=0, column=0, pady=10)
                self.current_user = None
            elif response.status_code == 403:
                ttk.Label(
                    self.result_frame,
                    text="⚠️ Превышен лимит запросов к API. Попробуйте позже.",
                    foreground="orange",
                    font=("Arial", 10),
                    wraplength=500
                ).grid(row=0, column=0, pady=10)
                self.current_user = None
            else:
                ttk.Label(
                    self.result_frame,
                    text=f"⚠️ Ошибка: {response.status_code}",
                    foreground="red",
                    font=("Arial", 10)
                ).grid(row=0, column=0, pady=10)
                self.current_user = None

        except requests.exceptions.ConnectionError:
            messagebox.showerror("Ошибка", "Нет подключения к интернету!")
        except requests.exceptions.Timeout:
            messagebox.showerror("Ошибка", "Превышено время ожидания ответа от сервера!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")

    def display_user(self, user_data):
        """Отображение информации о пользователе"""
        # Аватар
        avatar_label = ttk.Label(self.result_frame)
        avatar_label.grid(row=0, column=0, rowspan=6, padx=(0, 15))

        # Загружаем аватар (упрощенно — без изображения, либо с Pillow)
        # Здесь показываем текстовую информацию
        if user_data.get("avatar_url"):
            try:
                from PIL import Image, ImageTk
                from io import BytesIO

                avatar_response = requests.get(user_data["avatar_url"], timeout=5)
                img = Image.open(BytesIO(avatar_response.content))
                img = img.resize((80, 80), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                avatar_label.config(image=photo)
                avatar_label.image = photo
            except ImportError:
                avatar_label.config(text="[Аватар]\n(Pillow не установлен)")
            except Exception:
                avatar_label.config(text="[Нет аватара]")

        # Информация
        info_frame = ttk.Frame(self.result_frame)
        info_frame.grid(row=0, column=1, sticky=tk.W)

        ttk.Label(info_frame, text=f"Логин: {user_data.get('login', 'Н/Д')}", font=("Arial", 11, "bold")).grid(
            row=0, column=0, sticky=tk.W
        )

        name = user_data.get("name") or "Не указано"
        ttk.Label(info_frame, text=f"Имя: {name}", font=("Arial", 10)).grid(
            row=1, column=0, sticky=tk.W, pady=(5, 0)
        )

        bio = user_data.get("bio") or "Нет описания"
        ttk.Label(info_frame, text=f"Описание: {bio}", wraplength=400).grid(
            row=2, column=0, sticky=tk.W, pady=(5, 0)
        )

        # Статистика
        stats_frame = ttk.Frame(self.result_frame)
        stats_frame.grid(row=6, column=0, columnspan=2, pady=(10, 0), sticky=tk.W)

        public_repos = user_data.get("public_repos", 0)
        followers = user_data.get("followers", 0)
        following = user_data.get("following", 0)

        ttk.Label(stats_frame, text=f"📁 Репозитории: {public_repos}").grid(row=0, column=0, padx=(0, 15))
        ttk.Label(stats_frame, text=f"👥 Подписчики: {followers}").grid(row=0, column=1, padx=(0, 15))
        ttk.Label(stats_frame, text=f"👤 Подписки: {following}").grid(row=0, column=2)

        # Кнопки
        buttons_frame = ttk.Frame(self.result_frame)
        buttons_frame.grid(row=7, column=0, columnspan=2, pady=(10, 0))

        ttk.Button(
            buttons_frame,
            text="⭐ Добавить в избранное",
            command=lambda: self.add_to_favorites(user_data)
        ).grid(row=0, column=0, padx=(0, 5))

        ttk.Button(
            buttons_frame,
            text="🔗 Открыть профиль",
            command=lambda: webbrowser.open(user_data.get("html_url", ""))
        ).grid(row=0, column=1)

    def add_to_favorites(self, user_data):
        """Добавление пользователя в избранное"""
        username = user_data.get("login")

        # Проверяем, нет ли уже в избранном
        if any(fav.get("login") == username for fav in self.favorites):
            messagebox.showinfo("Информация", f"Пользователь {username} уже в избранном!")
            return

        # Добавляем в избранное
        favorite = {
            "login": username,
            "name": user_data.get("name") or username,
            "html_url": user_data.get("html_url", ""),
            "avatar_url": user_data.get("avatar_url", ""),
            "public_repos": user_data.get("public_repos", 0),
            "followers": user_data.get("followers", 0),
            "added_at": datetime.now().isoformat()
        }
        self.favorites.append(favorite)
        self.save_favorites()
        self.refresh_favorites_list()
        messagebox.showinfo("Успех", f"Пользователь {username} добавлен в избранное!")

    def remove_favorite(self):
        """Удаление пользователя из избранного"""
        selection = self.favorites_listbox.curselection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите пользователя для удаления!")
            return

        index = selection[0]
        username = self.favorites[index]["login"]

        if messagebox.askyesno("Подтверждение", f"Удалить пользователя {username} из избранного?"):
            del self.favorites[index]
            self.save_favorites()
            self.refresh_favorites_list()

    def open_favorite_profile(self):
        """Открытие профиля избранного пользователя"""
        selection = self.favorites_listbox.curselection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите пользователя!")
            return

        index = selection[0]
        url = self.favorites[index]["html_url"]
        if url:
            webbrowser.open(url)

    def refresh_favorites_list(self):
        """Обновление списка избранных в интерфейсе"""
        self.favorites_listbox.delete(0, tk.END)
        for fav in self.favorites:
            display_text = f"{fav['login']} ({fav.get('name', 'Н/Д')})"
            self.favorites_listbox.insert(tk.END, display_text)

    def load_favorites(self):
        """Загрузка избранных из JSON-файла"""
        if os.path.exists(FAVORITES_FILE):
            try:
                with open(FAVORITES_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return []
        return []

    def save_favorites(self):
        """Сохранение избранных в JSON-файл"""
        with open(FAVORITES_FILE, "w", encoding="utf-8") as f:
            json.dump(self.favorites, f, ensure_ascii=False, indent=2)


def main():
    root = tk.Tk()
    app = GitHubUserFinder(root)
    root.mainloop()


if __name__ == "__main__":
    main()