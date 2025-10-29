import tkinter as tk
from tkinter import filedialog
from tkinter.ttk import Progressbar, Scale
import customtkinter as ctk
from mutagen.mp3 import MP3
import threading
import pygame
import time
import os

pygame.mixer.init()

# Хранение текущей позиции музыки
current_position = 0
paused = False
selected_folder_path = ""  # Хранение выбранного пути к папке с музыкой


def update_progress():
    global current_position
    while True:
        if pygame.mixer.music.get_busy() and not paused:
            current_position = pygame.mixer.music.get_pos() / 1000
            pbar["value"] = current_position

            # Проверка, достигла ли текущая песня максимальной длительности
            if current_position >= pbar["maximum"]:
                stop_music()
                pbar["value"] = 0

            window.update()
        time.sleep(0.1)


# Создание потока для обновления прогресс бара
pt = threading.Thread(target=update_progress)
pt.daemon = True
pt.start()


def select_music_folder():
    global selected_folder_path
    selected_folder_path = filedialog.askdirectory()
    if selected_folder_path:
        lbox.delete(0, tk.END)
        for filename in os.listdir(selected_folder_path):
            if filename.endswith(".mp3"):
                lbox.insert(tk.END, filename)


def previous_song():
    if len(lbox.curselection()) > 0:
        current_index = lbox.curselection()[0]
        if current_index > 0:
            lbox.selection_clear(0, tk.END)
            lbox.selection_set(current_index - 1)
            play_selected_song()


def next_song():
    if len(lbox.curselection()) > 0:
        current_index = lbox.curselection()[0]
        if current_index < lbox.size() - 1:
            lbox.selection_clear(0, tk.END)
            lbox.selection_set(current_index + 1)
            play_selected_song()


def play_music():
    global paused
    if paused:

        pygame.mixer.music.unpause()
        paused = False
    else:

        play_selected_song()


def play_selected_song():
    global current_position, paused
    if len(lbox.curselection()) > 0:
        current_index = lbox.curselection()[0]
        selected_song = lbox.get(current_index)
        full_path = os.path.join(selected_folder_path, selected_song)  # Добавить полный путь к файлу
        pygame.mixer.music.load(full_path)  # Загрузить выбранную песню
        pygame.mixer.music.play(start=current_position)  # Воспроизвести песню с текущей позиции
        paused = False
        audio = MP3(full_path)
        song_duration = audio.info.length
        pbar["maximum"] = song_duration  # Установить максимальное значение прогресс бара на длительность песни


def pause_music():
    global paused
    pygame.mixer.music.pause()
    paused = True


def stop_music():
    global paused
    # Остановить текущую музыку и сбросить прогресс бар
    pygame.mixer.music.stop()
    paused = False


def set_volume(volume):
    pygame.mixer.music.set_volume(float(volume) / 100)


# Создание главного окна
window = tk.Tk()
window.title("Приложение для проигрывания музыки")
window.geometry("600x550")

# Создание метки для заголовка музыкального проигрывателя
l_music_player = tk.Label(window, text="mp3 Player", font=("TkDefaultFont", 30, "bold"))
l_music_player.pack(pady=10)

# Создание кнопки для выбора папки с музыкой
btn_select_folder = ctk.CTkButton(window, text="Выбрать папку с музыкой",
                                  command=select_music_folder,
                                  font=("TkDefaultFont", 18))
btn_select_folder.pack(pady=20)

# Создание списка для отображения доступных песен
lbox = tk.Listbox(window, width=50, font=("TkDefaultFont", 16))
lbox.pack(pady=10)

# Создание фрейма для кнопок управления
btn_frame = tk.Frame(window)
btn_frame.pack(pady=20)
# Создание кнопки для перехода к предыдущей песне
btn_previous = ctk.CTkButton(btn_frame, text="<", command=previous_song,
                             width=50, font=("TkDefaultFont", 18))
btn_previous.pack(side=tk.LEFT, padx=5)

# Создание кнопки для воспроизведения музыки
btn_play = ctk.CTkButton(btn_frame, text="Воспроизвести", command=play_music, width=50,
                         font=("TkDefaultFont", 18))
btn_play.pack(side=tk.LEFT, padx=5)

# Создание кнопки для постановки музыки на паузу
btn_pause = ctk.CTkButton(btn_frame, text="Пауза", command=pause_music, width=50,
                          font=("TkDefaultFont", 18))
btn_pause.pack(side=tk.LEFT, padx=5)

# Создание кнопки для перехода к следующей песне
btn_next = ctk.CTkButton(btn_frame, text=">", command=next_song, width=50,
                         font=("TkDefaultFont", 18))
btn_next.pack(side=tk.LEFT, padx=5)

# Создание прогресс бара для отображения прогресса текущей песни
pbar = Progressbar(window, length=300, mode="determinate")
pbar.pack(pady=10)

# Создание бара для управления громкостью
volume = Scale(window, from_=100, to=0, orient=tk.VERTICAL, command=set_volume)
volume.set(50)
volume.pack()

window.mainloop()