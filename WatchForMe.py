import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog
import threading
import queue
import time
import re
import random
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pygame import mixer  # For MP3/WAV playback; install with `pip install pygame`

class RedirectText:
    """Class to redirect console output to Tkinter text widget"""
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.queue = queue.Queue()
        self.update_widget()
        
    def write(self, string):
        self.queue.put(string)
        
    def flush(self):
        pass
        
    def update_widget(self):
        try:
            while True:
                text = self.queue.get_nowait()
                self.text_widget.configure(state="normal")
                self.text_widget.insert(tk.END, text)
                self.text_widget.see(tk.END)
                self.text_widget.configure(state="disabled")
        except queue.Empty:
            self.text_widget.after(100, self.update_widget)

class TalkToMeBot:
    def __init__(self, root):
        self.root = root
        self.root.title("TalkToMe Bot")
        self.root.geometry("600x500")
        
        self.script_running = False
        self.paused = False
        self.driver = None
        self.thread = None
        self.stop_event = threading.Event()
        
        # Default sound file path
        self.default_sound_file = os.path.join(os.path.dirname(__file__), 'sound_effect', 'ding.mp3')
        
        self.create_widgets()
        
    def create_widgets(self):
        control_frame = ttk.LabelFrame(self.root, text="Controls")
        control_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(control_frame, text="URL:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.url_var = tk.StringVar(value="https://www.talktome.com/members/programs/")
        ttk.Entry(control_frame, textvariable=self.url_var, width=50).grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        settings_frame = ttk.LabelFrame(self.root, text="Settings")
        settings_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(settings_frame, text="Target Value:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.target_value = tk.DoubleVar(value=0.60)
        ttk.Entry(settings_frame, textvariable=self.target_value, width=10).grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(settings_frame, text="Max Refresh Interval (seconds):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.max_retry_interval = tk.IntVar(value=30)
        ttk.Entry(settings_frame, textvariable=self.max_retry_interval, width=10).grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        # Sound settings row
        ttk.Label(settings_frame, text="Sound File Path (.mp3/.wav):").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.sound_file_var = tk.StringVar(value="")
        ttk.Entry(settings_frame, textvariable=self.sound_file_var, width=25).grid(row=2, column=1, padx=5, pady=5, sticky="w")
        ttk.Button(settings_frame, text="Browse", command=self.browse_sound_file).grid(row=2, column=2, padx=5, pady=5)
        
        # Mute checkbox
        self.mute_sound_var = tk.BooleanVar(value=False)
        self.mute_checkbutton = ttk.Checkbutton(settings_frame, text="Mute Sound", variable=self.mute_sound_var)
        self.mute_checkbutton.grid(row=2, column=3, padx=10, pady=5, sticky="w")
        
        ttk.Label(settings_frame, text="Max Retries:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.max_retries = tk.IntVar(value=1000)
        ttk.Entry(settings_frame, textvariable=self.max_retries, width=10).grid(row=3, column=1, padx=5, pady=5, sticky="w")
        
        buttons_frame = ttk.Frame(self.root)
        buttons_frame.pack(fill="x", padx=10, pady=5)
        
        self.start_button = ttk.Button(buttons_frame, text="Start", command=self.start_script)
        self.start_button.pack(side="left", padx=5)
        
        self.pause_button = ttk.Button(buttons_frame, text="Pause", command=self.pause_script, state="disabled")
        self.pause_button.pack(side="left", padx=5)
        
        self.test_button = ttk.Button(buttons_frame, text="Test Connect", command=self.test_connect, state="disabled")
        self.test_button.pack(side="left", padx=5)
        
        self.stop_button = ttk.Button(buttons_frame, text="Stop", command=self.stop_script, state="disabled")
        self.stop_button.pack(side="left", padx=5)
        
        log_frame = ttk.LabelFrame(self.root, text="Log")
        log_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, state="disabled")
        self.log_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.text_redirect = RedirectText(self.log_text)
        
    def browse_sound_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3 *.wav")])
        if file_path:
            self.sound_file_var.set(file_path)
        
    def start_script(self):
        if self.script_running and self.paused:
            self.paused = False
            self.pause_button.configure(text="Pause")
            print("Script resumed")
            return
            
        self.script_running = True
        self.stop_event.clear()
        
        self.start_button.configure(state="disabled")
        self.pause_button.configure(state="normal")
        self.test_button.configure(state="normal")
        self.stop_button.configure(state="normal")
        
        self.thread = threading.Thread(target=self.run_script)
        self.thread.daemon = True
        self.thread.start()
        
    def pause_script(self):
        if not self.paused:
            self.paused = True
            self.pause_button.configure(text="Resume")
            print("Script paused")
        else:
            self.paused = False
            self.pause_button.configure(text="Pause")
            print("Script resumed")
            
    def test_connect(self):
        if self.driver:
            test_thread = threading.Thread(target=self.click_connect_button)
            test_thread.daemon = True
            test_thread.start()
        else:
            print("Browser not started. Please start the script first.")
            
    def click_connect_button(self):
        try:
            print("Testing: Clicking the connect button regardless of conditions...")
            connect_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.api_vc_connect"))
            )
            connect_button.click()
            print("Connect button clicked successfully!")
        except Exception as e:
            print(f"Error clicking connect button: {e}")
            
    def stop_script(self):
        if self.script_running:
            self.stop_event.set()
            self.script_running = False
            self.paused = False
            
            self.start_button.configure(state="normal")
            self.pause_button.configure(state="disabled", text="Pause")
            self.test_button.configure(state="disabled")
            self.stop_button.configure(state="disabled")
            
            if self.driver:
                print("Closing browser...")
                try:
                    self.driver.quit()
                except:
                    pass
                self.driver = None
                
            print("Script stopped")
            
    def play_alert_sound(self):
        if self.mute_sound_var.get():
            print("Sound alert muted.")
            return
        
        sound_file = self.sound_file_var.get().strip()
        if not sound_file:
            sound_file = self.default_sound_file
            if not os.path.exists(sound_file):
                print(f"Default sound file not found: {sound_file}. Skipping alert.")
                return
        
        try:
            mixer.init()
            mixer.music.load(sound_file)
            mixer.music.play()  # Non-blocking
            print(f"Playing sound: {sound_file}")
        except Exception as e:
            print(f"Error playing sound: {e}")
            
    def run_script(self):
        try:
            print("Initializing Chrome WebDriver...")
            self.driver = webdriver.Chrome()  # Add executable_path if needed
            
            url = self.url_var.get()
            print(f"Navigating to {url}")
            self.driver.get(url)
            
            print("Please log in manually in the browser window.")
            print("Once you're logged in and the page is fully loaded, click the Start button again or Resume if paused...")
            
            self.paused = True
            self.pause_button.configure(text="Resume")
            
            retry_count = 0
            max_retries = self.max_retries.get()
            max_retry_interval = self.max_retry_interval.get()
            target_value = self.target_value.get()
            reload_values = {0.40, 0.50}
            
            while retry_count < max_retries and not self.stop_event.is_set():
                while self.paused and not self.stop_event.is_set():
                    time.sleep(0.5)
                    
                if self.stop_event.is_set():
                    break
                    
                try:
                    vc_element = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "a.vc_rate"))
                    )
                    
                    vc_text = vc_element.text
                    match = re.search(r'\$(\d+\.\d+)', vc_text)
                    if not match:
                        print("Could not find a number in the text.")
                        break
                    
                    vc_value = float(match.group(1))
                    print(f"Current value: ${vc_value}")
                    
                    if vc_value == target_value:
                        print(f"Value is ${target_value}. Clicking the connect button.")
                        connect_button = WebDriverWait(self.driver, 10).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.api_vc_connect"))
                        )
                        connect_button.click()
                        self.play_alert_sound()
                    elif vc_value in reload_values:
                        print(f"Value is ${vc_value}. Refreshing the page.")
                        self.driver.refresh()
                        delay = random.uniform(1, max_retry_interval)
                        print(f"Waiting {delay:.2f} seconds before next check...")
                        time.sleep(delay)
                        retry_count += 1
                    
                except Exception as e:
                    print(f"Something went wrong: {e}")
                    delay = random.uniform(1, max_retry_interval)
                    time.sleep(delay)
                    retry_count += 1
                    
                time.sleep(2)
                
            if retry_count >= max_retries:
                print("Max retries reached. Stopping the script.")
                
        except Exception as e:
            print(f"Script error: {e}")
            
        finally:
            if not self.stop_event.is_set():
                self.stop_script()

if __name__ == "__main__":
    root = tk.Tk()
    app = TalkToMeBot(root)
    
    import sys
    sys.stdout = app.text_redirect
    
    root.mainloop()
    
    sys.stdout = sys.__stdout__