import tkinter as tk
from tkinter import ttk
from pynput.keyboard import Controller, Key, Listener
import threading
from ttkthemes import ThemedTk
import time
import os
import sys
class TypingSimulator:
    def __init__(self, master):
        self.master = master
        self.master.title("Human Typing Simulator")
        self.set_theme()  # Set the theme
        self.word_pause_index = 0
        self.word_paused_index = 0
        self.is_typing = False  # Track if typing is in progress
        self.write_words = False  # Track if word mode is enabled
        self.toggle_word_mode_var = tk.IntVar()  # Variable to track the state of the checkbox

        

        # Create a frame to contain all the widgets
        self.container = ttk.Frame(master)
        self.container.pack(fill=tk.BOTH, expand=True)  # Fill the entire window and expand with it

        self.label = ttk.Label(self.container, text="Enter text:")
        self.label.pack(pady=(10, 0))

        self.text_entry = tk.Text(self.container, width=50, height=10, font=('Georgia', 12), bg='lightgray', fg='black', borderwidth=2, relief="groove")
        self.text_entry.pack(padx=10, pady=(0, 10))

        self.speed_label = ttk.Label(self.container, text="Speed:")
        self.speed_label.pack(pady=(10, 0))

        self.speed_slider = ttk.Scale(self.container, from_=0.1, to=1.0, length=200, orient="horizontal", command=self.update_speed_label)
        self.speed_slider.set(0.5)  # Default speed
        self.speed_slider.pack(padx=10, pady=(0, 10))

        self.speed_value_label = ttk.Label(self.container, text=f"Current Speed: {self.speed_slider.get():.2f}")
        self.speed_value_label.pack(padx=10, pady=(0, 10))

        self.toggle_button = ttk.Button(self.container, text="Start Typing", command=self.toggle_typing)
        self.toggle_button.pack(padx=10, pady=(0, 10))

        self.clear_button = ttk.Button(self.container, text="Clear Text", command=self.clear_text)
        self.clear_button.pack(padx=10, pady=(0, 10))

        self.toggle_word_mode_var = tk.BooleanVar(value=False)
        self.toggle_word_mode_checkbox = ttk.Checkbutton(self.container, text="Write Words", variable=self.toggle_word_mode_var)
        self.toggle_word_mode_checkbox.pack(padx=10, pady=(0, 10))

        self.hotkey_combination = {Key.ctrl_l, Key.alt_l, Key.space}
        self.hotkey_pressed = set()

        self.listener_thread = threading.Thread(target=self.start_listener)
        self.listener_thread.start()

        self.keyboard = Controller()
        self.typing_thread = None
        
        self.pause_index = 0




    def resource_path(relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)
   
    
    def set_theme(self):
        self.style = ttk.Style()
        self.style.theme_use("black")  # Change the theme here
        
    def clear_text(self):
        # Clear the text widget
        self.text_entry.delete("1.0", tk.END)
        
        # Reset the pause index to 0
        self.paused_index = 0
        self.word_paused_index = 0
        
        # Reset other relevant variables and GUI elements if needed
        self.toggle_button.config(text="Start Typing")
        self.is_typing = False

    def stop_threads(self):
        if self.typing_thread and self.typing_thread.is_alive():
            self.typing_thread.join()
        if self.listener_thread and self.listener_thread.is_alive():
            self.listener_thread.join()      

    def update_speed_label(self, speed):
        rounded_speed = round(float(speed), 2)
        if hasattr(self, 'speed_value_label'):
            self.speed_value_label.config(text=f"Current Speed: {rounded_speed}")



    def toggle_typing(self):
        if self.toggle_word_mode_var.get():
            self.is_typing = not self.is_typing
            if self.is_typing:
                self.toggle_button.config(text="Pause")
                if not self.typing_thread or not self.typing_thread.is_alive():
                    # If typing thread is not yet started or not alive, start it
                    text_to_type = self.text_entry.get("1.0", tk.END)
                    self.typing_thread = threading.Thread(target=self.type_words, args=(text_to_type,))
                    self.typing_thread.start()
            else:
                self.toggle_button.config(text="Resume")
                # Store the pause index
                self.word_paused_index = self.word_pause_index +1

        else:
            
            self.is_typing = not self.is_typing
            if self.is_typing:
                self.toggle_button.config(text="Pause")
                if not self.typing_thread or not self.typing_thread.is_alive():
                    # If typing thread is not yet started or not alive, start it
                    text_to_type = self.text_entry.get("1.0", tk.END)
                    self.typing_thread = threading.Thread(target=self.type_text, args=(text_to_type,))
                    self.typing_thread.start()
            else:
                self.toggle_button.config(text="Resume")
                # Store the pause index
                self.paused_index = self.pause_index

    def type_text(self, text_to_type):
        if hasattr(self, 'paused_index'):
            # If there's a paused index, start typing from there
            self.pause_index = self.paused_index +1
            del self.paused_index  # Clear the paused index
        else:
            self.pause_index = 0  # Reset pause_index before processing

        text_length = len(text_to_type)
        time.sleep(2)  # Wait for 2 seconds before starting to type
        while self.pause_index < text_length:
            if not self.is_typing:
                return
            char = text_to_type[self.pause_index - 1]
            self.keyboard.type(char) 
            self.master.update()
            time.sleep(self.speed_slider.get())

            self.pause_index += 1  # Move to the next character

        # If it reaches the end of the text, reset to the beginning
        self.pause_index = 0
        self.is_typing = False
        self.toggle_button.config(text="Start Typing")

    def type_words(self, text_to_type):
        if hasattr(self, 'word_paused_index'):
            # If there's a paused index, start typing from the next word after the pause
            self.word_pause_index = self.word_paused_index 
            del self.word_paused_index  # Clear the paused index
        else:
            self.word_pause_index = 0  # Start from the beginning

        words = text_to_type.split()  # Split the text into words
        word_count = len(words)
        time.sleep(2)  # Wait for 2 seconds before starting to type

        while self.word_pause_index < word_count:
            if not self.is_typing:
                return
            word = words[self.word_pause_index]
            self.keyboard.type(word + " ")  # Add space after typing the word
            self.master.update()
            time.sleep(self.speed_slider.get())

            self.word_pause_index += 1  # Move to the next word

        # If it reaches the end of the text, reset to the beginning
        self.word_pause_index = 0
        self.is_typing = False
        self.toggle_button.config(text="Start Typing")


    def on_press(self, key):
        if key in self.hotkey_combination:
            self.hotkey_pressed.add(key)
            if len(self.hotkey_combination) == len(self.hotkey_pressed):
                self.toggle_typing()

    def on_release(self, key):
        if key in self.hotkey_pressed:
            self.hotkey_pressed.remove(key)

    def start_listener(self):
        with Listener(on_press=self.on_press, on_release=self.on_release) as listener:
            listener.join()
def main():
    root = ThemedTk(theme="adapta")
    def on_close():
        print("on_close called")
        root.destroy()
        os._exit(0)
        
    root.wm_attributes("-topmost", 1)
    root.protocol("WM_DELETE_WINDOW", on_close)
    root.geometry("530x440")
    app = TypingSimulator(root)
    root.mainloop()

if __name__ == "__main__":
    main()

