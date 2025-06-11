import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import datetime
import speech_recognition as sr
import pyttsx3
import pywhatkit
import pyautogui
from PIL import Image, ImageTk
import io
import base64

class VoiceAssistantGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("VERA - Voice Assistant")
        self.root.geometry("800x600")
        self.root.configure(bg='#2c3e50')
        
        # Initialize speech components
        self.engine = pyttsx3.init('sapi5')
        voices = self.engine.getProperty('voices')
        if voices:
            self.engine.setProperty('voice', voices[0].id)
        
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Control variables
        self.is_listening = False
        self.is_active = True
        
        # Configure recognizer settings
        self.recognizer.pause_threshold = 1
        self.recognizer.phrase_threshold = 0.3
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.operation_timeout = 5
        self.recognizer.non_speaking_duration = 0.5
        self.recognizer.energy_threshold = 4000
        
        self.setup_gui()
        self.wish_me()
        
    def setup_gui(self):
        # Main title
        title_frame = tk.Frame(self.root, bg='#2c3e50')
        title_frame.pack(pady=20)
        
        title_label = tk.Label(title_frame, text="VERA", 
                              font=('Arial', 28, 'bold'), 
                              fg='#3498db', bg='#2c3e50')
        title_label.pack()
        
        subtitle_label = tk.Label(title_frame, text="Voice Enabled Responsive Assistant", 
                                 font=('Arial', 12), 
                                 fg='#ecf0f1', bg='#2c3e50')
        subtitle_label.pack()
        
        # Status frame
        status_frame = tk.Frame(self.root, bg='#2c3e50')
        status_frame.pack(pady=10)
        
        self.status_label = tk.Label(status_frame, text="Ready to listen", 
                                    font=('Arial', 14, 'bold'), 
                                    fg='#27ae60', bg='#2c3e50')
        self.status_label.pack()
        
        # Control buttons frame
        control_frame = tk.Frame(self.root, bg='#2c3e50')
        control_frame.pack(pady=20)
        
        self.listen_btn = tk.Button(control_frame, text="🎤 Start Listening", 
                                   font=('Arial', 12, 'bold'),
                                   bg='#27ae60', fg='white', 
                                   command=self.toggle_listening,
                                   width=15, height=2)
        self.listen_btn.pack(side=tk.LEFT, padx=10)
        
        self.speak_btn = tk.Button(control_frame, text="🔇 Mute/Unmute", 
                                  font=('Arial', 12, 'bold'),
                                  bg='#f39c12', fg='white', 
                                  command=self.toggle_speech,
                                  width=15, height=2)
        self.speak_btn.pack(side=tk.LEFT, padx=10)
        
        self.clear_btn = tk.Button(control_frame, text="🗑️ Clear Log", 
                                  font=('Arial', 12, 'bold'),
                                  bg='#e74c3c', fg='white', 
                                  command=self.clear_log,
                                  width=15, height=2)
        self.clear_btn.pack(side=tk.LEFT, padx=10)
        
        # Text input frame
        input_frame = tk.Frame(self.root, bg='#2c3e50')
        input_frame.pack(pady=10, padx=20, fill=tk.X)
        
        tk.Label(input_frame, text="Type Command:", 
                font=('Arial', 12), fg='#ecf0f1', bg='#2c3e50').pack(anchor=tk.W)
        
        entry_frame = tk.Frame(input_frame, bg='#2c3e50')
        entry_frame.pack(fill=tk.X, pady=5)
        
        self.command_entry = tk.Entry(entry_frame, font=('Arial', 12), 
                                     bg='#34495e', fg='white', 
                                     insertbackground='white')
        self.command_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.command_entry.bind('<Return>', self.process_text_command)
        
        self.send_btn = tk.Button(entry_frame, text="Send", 
                                 font=('Arial', 10, 'bold'),
                                 bg='#3498db', fg='white', 
                                 command=self.process_text_command)
        self.send_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Log area
        log_frame = tk.Frame(self.root, bg='#2c3e50')
        log_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        tk.Label(log_frame, text="Activity Log:", 
                font=('Arial', 12, 'bold'), fg='#ecf0f1', bg='#2c3e50').pack(anchor=tk.W)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, 
                                                 font=('Courier', 10),
                                                 bg='#34495e', fg='#ecf0f1',
                                                 height=15)
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Available commands info
        info_frame = tk.Frame(self.root, bg='#2c3e50')
        info_frame.pack(pady=10, padx=20, fill=tk.X)
        
        info_text = """Available Commands: open [app], close, play [song], screenshot, switch tab, search [query], sleep"""
        tk.Label(info_frame, text=info_text, 
                font=('Arial', 9), fg='#95a5a6', bg='#2c3e50', 
                wraplength=760, justify=tk.LEFT).pack()
    
    def log_message(self, message, msg_type="INFO"):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        color_map = {
            "INFO": "#3498db",
            "USER": "#27ae60", 
            "VERA": "#e74c3c",
            "ERROR": "#e74c3c"
        }
        
        self.log_text.insert(tk.END, f"[{timestamp}] [{msg_type}] {message}\n")
        self.log_text.see(tk.END)
        
        # Color coding for different message types
        if msg_type in color_map:
            start_idx = self.log_text.index(f"{tk.END}-1c linestart")
            end_idx = self.log_text.index(f"{tk.END}-1c lineend")
            self.log_text.tag_add(msg_type, start_idx, end_idx)
            self.log_text.tag_config(msg_type, foreground=color_map[msg_type])
    
    def speak(self, text):
        if self.is_active:
            self.log_message(f"VERA: {text}", "VERA")
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception as e:
                self.log_message(f"Speech error: {str(e)}", "ERROR")
    
    def wish_me(self):
        hour = int(datetime.datetime.now().hour)
        if hour >= 0 and hour < 12:
            greeting = "Good morning!"
        elif hour >= 12 and hour < 18:
            greeting = "Good afternoon!"
        else:
            greeting = "Good evening!"
        
        full_greeting = f"{greeting} Hello, this is VERA. How can I help you today?"
        self.speak(full_greeting)
    
    def toggle_listening(self):
        if not self.is_listening:
            self.is_listening = True
            self.listen_btn.config(text="🛑 Stop Listening", bg='#e74c3c')
            self.status_label.config(text="Listening...", fg='#e74c3c')
            threading.Thread(target=self.continuous_listen, daemon=True).start()
        else:
            self.is_listening = False
            self.listen_btn.config(text="🎤 Start Listening", bg='#27ae60')
            self.status_label.config(text="Stopped listening", fg='#f39c12')
    
    def toggle_speech(self):
        self.is_active = not self.is_active
        status = "Unmuted" if self.is_active else "Muted"
        self.log_message(f"Speech {status}")
        if not self.is_active:
            self.speak_btn.config(bg='#e74c3c')
        else:
            self.speak_btn.config(bg='#f39c12')
    
    def clear_log(self):
        self.log_text.delete(1.0, tk.END)
        self.log_message("Log cleared")
    
    def continuous_listen(self):
        while self.is_listening:
            try:
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=10)
                
                try:
                    query = self.recognizer.recognize_google(audio, language="en-us")
                    self.log_message(f"User said: {query}", "USER")
                    self.process_command(query.lower())
                except sr.UnknownValueError:
                    self.log_message("Could not understand audio", "ERROR")
                except sr.RequestError as e:
                    self.log_message(f"Recognition error: {str(e)}", "ERROR")
                    
            except sr.WaitTimeoutError:
                continue
            except Exception as e:
                self.log_message(f"Listening error: {str(e)}", "ERROR")
                break
    
    def process_text_command(self, event=None):
        command = self.command_entry.get().strip()
        if command:
            self.log_message(f"Text command: {command}", "USER")
            self.process_command(command.lower())
            self.command_entry.delete(0, tk.END)
    
    def process_command(self, query):
        try:
            if 'open' in query:
                app_name = query.replace('open', '').strip()
                self.speak(f'Opening {app_name}')
                pyautogui.press('super')
                pyautogui.typewrite(app_name)
                pyautogui.sleep(0.7)
                pyautogui.press('enter')
                self.log_message(f"Opened application: {app_name}")
                
            elif 'close' in query:
                pyautogui.hotkey('alt', 'f4')
                self.speak('Done sir')
                self.log_message("Closed current application")
                
            elif 'play' in query:
                song_name = query.replace('play', '').strip()
                self.speak(f'Sure sir, playing {song_name}')
                pywhatkit.playonyt(song_name)
                self.log_message(f"Playing on YouTube: {song_name}")
                
            elif 'screenshot' in query:
                screenshot = pyautogui.screenshot()
                screenshot.save('screenshot.png')
                self.speak('Screenshot taken')
                self.log_message("Screenshot saved as screenshot.png")
                
            elif 'switch tab' in query:
                pyautogui.hotkey('ctrl', 'tab')
                self.speak('Tab switched')
                self.log_message("Switched browser tab")
                
            elif 'search' in query:
                search_term = query.replace('search', '').strip()
                pywhatkit.search(search_term)
                self.speak(f'Searching for {search_term}')
                self.log_message(f"Searched for: {search_term}")
                
            elif 'sleep' in query:
                self.speak('Sure sir, but you can wake me up anytime')
                self.is_listening = False
                self.listen_btn.config(text="🎤 Start Listening", bg='#27ae60')
                self.status_label.config(text="Sleeping - Click to wake up", fg='#f39c12')
                self.log_message("VERA is now sleeping")
                
            elif 'hello' in query or 'hi' in query:
                self.speak('Hello! How can I help you?')
                
            elif 'time' in query:
                current_time = datetime.datetime.now().strftime("%I:%M %p")
                self.speak(f'The time is {current_time}')
                self.log_message(f"Current time: {current_time}")
                
            elif 'date' in query:
                current_date = datetime.datetime.now().strftime("%B %d, %Y")
                self.speak(f'Today is {current_date}')
                self.log_message(f"Current date: {current_date}")
                
            else:
                self.speak("I didn't understand that. Please try again.")
                self.log_message(f"Unrecognized command: {query}")
                
        except Exception as e:
            error_msg = f"Error processing command: {str(e)}"
            self.log_message(error_msg, "ERROR")
            self.speak("Sorry, there was an error processing your command.")

def main():
    root = tk.Tk()
    app = VoiceAssistantGUI(root)
    
    # Handle window closing
    def on_closing():
        if messagebox.askokcancel("Quit", "Do you want to quit VERA?"):
            app.is_listening = False
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()