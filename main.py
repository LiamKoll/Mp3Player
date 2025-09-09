import os
import pygame
from tkinter import IntVar
from customtkinter import CTk, CTkButton, CTkLabel, CTkSlider, CTkCheckBox, CTkRadioButton, CTkFrame, filedialog, set_appearance_mode
from threading import Thread
import random

class MP3Player:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()

        self.playlist = []
        self.current_song = 0
        self.shuffle = False
        self.repeat_order = False
        self.paused = False
        self.volume = 0.5
        self.play_mode = None

        # Set appearance mode to Dark
        set_appearance_mode("dark")

        # Root window setup
        self.root = CTk()
        self.root.title("MP3 Player")
        self.root.geometry("400x500")
        self.root.iconbitmap("mp3_player.ico")

        # Info Frame
        self.info_frame = CTkFrame(self.root)
        self.info_frame.pack(pady=10, padx=10, fill="x")

        self.label_info = CTkLabel(self.info_frame, text="", text_color="gray")
        self.label_info.pack(pady=5)

        self.label_now_playing = CTkLabel(self.info_frame, text="Jetzt spielen: ", font=("Arial", 14))
        self.label_now_playing.pack(pady=5)

        # Controls Frame
        self.controls_frame = CTkFrame(self.root)
        self.controls_frame.pack(pady=10, padx=10, fill="x")

        self.button_load = CTkButton(self.controls_frame, text="Load Playlist", command=self.load_playlist)
        self.button_load.pack(pady=5, padx=5, fill="x")

        self.button_play_pause = CTkButton(self.controls_frame, text="Pause", command=self.toggle_pause)
        self.button_play_pause.pack(pady=5, padx=5, fill="x")

        self.button_skip = CTkButton(self.controls_frame, text="Skip", command=self.skip_song)
        self.button_skip.pack(pady=5, padx=5, fill="x")

        self.button_repeat_order = CTkCheckBox(self.controls_frame, text="Reihenfolge wiederholen", command=self.toggle_repeat_order)
        self.button_repeat_order.pack(pady=5)

        self.volume_slider = CTkSlider(self.controls_frame, from_=0.0, to=1.0, command=self.set_volume)
        self.volume_slider.set(self.volume)
        self.volume_slider.pack(pady=5)

        # Playback Mode
        self.play_mode_frame = CTkFrame(self.root)
        self.play_mode_frame.pack(pady=10, padx=10, fill="x")

        self.play_mode = IntVar(value=1)
        self.play_mode_radio1 = CTkRadioButton(self.play_mode_frame, text="Reihenfolge spielen", variable=self.play_mode, value=1, command=self.update_info)
        self.play_mode_radio1.pack(pady=5, anchor="w")

        self.play_mode_radio2 = CTkRadioButton(self.play_mode_frame, text="Shuffle spielen", variable=self.play_mode, value=2, command=self.update_info)
        self.play_mode_radio2.pack(pady=5, anchor="w")

        # Close Button
        self.close_button = CTkButton(self.root, text="Close", command=self.on_close, fg_color="red")
        self.close_button.pack(pady=10)

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def load_playlist(self):
        folder_path = filedialog.askdirectory()
        self.playlist = [os.path.join(folder_path, file) for file in os.listdir(folder_path) if file.endswith('.mp3')]
        if self.playlist:
            self.current_song = 0
            self.play_song()
            self.update_info()

    def play_song(self):
        if self.playlist:
            try:
                pygame.mixer.music.load(self.playlist[self.current_song])
                pygame.mixer.music.set_volume(self.volume)
                pygame.mixer.music.play()
                pygame.mixer.music.set_endevent(pygame.USEREVENT + 1)
                self.update_now_playing_label()
            except pygame.error as e:
                print(f"Error playing the song: {e}")

    def toggle_pause(self):
        if self.playlist:
            self.paused = not self.paused
            if self.paused:
                pygame.mixer.music.pause()
                self.button_play_pause.configure(text="Resume")
            else:
                pygame.mixer.music.unpause()
                self.button_play_pause.configure(text="Pause")

    def skip_song(self):
        if self.playlist:
            if self.play_mode.get() == 2:
                self.current_song = random.choice(list(range(len(self.playlist))))
            else:
                self.current_song += 1

            if self.current_song < len(self.playlist):
                self.play_song()
            else:
                if self.repeat_order:
                    self.current_song = 0
                    self.play_song()
                else:
                    self.label_info.configure(text="Es gibt kein weiteres Lied!")
        else:
            self.label_info.configure(text="")

    def set_volume(self, value):
        self.volume = float(value)
        pygame.mixer.music.set_volume(self.volume)

    def toggle_repeat_order(self):
        self.repeat_order = not self.repeat_order
        if self.repeat_order:
            self.label_info.configure(text="Reihenfolge wiederholen")
        else:
            self.update_info()

    def update_info(self):
        mode_text = "Reihenfolge" if self.play_mode.get() == 1 else "Shuffle"
        info_text = f"{mode_text} {'PAUSED' if self.paused else ''}"
        self.label_info.configure(text=info_text)

    def update_now_playing_label(self):
        if self.playlist:
            file_name = os.path.basename(self.playlist[self.current_song])
            self.label_now_playing.configure(text=f"Jetzt spielt: {file_name}")

    def on_close(self):
        pygame.quit()
        self.root.destroy()

    def play_next_song(self):
        if self.playlist:
            if not self.paused:
                if self.play_mode.get() == 1:
                    self.current_song += 1
                    if self.current_song >= len(self.playlist):
                        if self.repeat_order:
                            self.current_song = 0
                            self.play_song()
                        else:
                            self.label_info.configure(text="Es gibt kein weiteres Lied!")
                    else:
                        self.play_song()
                elif self.play_mode.get() == 2 and len(self.playlist) > 0:
                    self.current_song = random.choice(list(range(len(self.playlist))))
                    self.play_song()
        else:
            self.label_info.configure(text="")

    def event_loop(self):
        clock = pygame.time.Clock()
        while True:
            try:
                if not pygame.mixer.music.get_busy():
                    self.play_next_song()
                clock.tick(30)
            except KeyboardInterrupt:
                break

        pygame.quit()
        self.root.destroy()

    def run(self):
        thread = Thread(target=self.event_loop)
        thread.start()

        self.root.after(100, self.update_info)
        self.root.mainloop()

if __name__ == "__main__":
    player = MP3Player()
    player.run()
