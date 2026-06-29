import customtkinter as ctk  
import requests             
import threading            
import time                 
from pynput.keyboard import Controller, Key  # Controls Mac keyboard directly
from datetime import datetime

# --- CONFIGURATION ---
RENDER_URL = "https://talk-and-type.onrender.com"

# Initialize the native Mac keyboard controller
mac_keyboard = Controller()

# --- MAC SEAMLESS AUTOMATION ENGINE ---
def mac_type_text(text):
    """ 
    Natively types text and presses Enter on macOS.
    Bypasses AppleScript entirely, requiring ZERO settings changes for the user.
    """
    print(f"[MAC ENGINE] Natively typing text: '{text}'")
    try:
        # 1. Type the string out instantly character by character
        mac_keyboard.type(text)
        time.sleep(0.05) 
        
        # 2. Press and release the Return (Enter) key natively
        mac_keyboard.press(Key.enter)
        mac_keyboard.release(Key.enter)
        print("[MAC ENGINE] Text sent successfully.")
                
    except Exception as e:
        print(f"!!! Mac Typing Engine Error: {e}")

# --- MAIN APP CLASS ---
class TalkAndTypeReceiverMac(ctk.CTk):
    def __init__(self):
        super().__init__()

        # WINDOW SETUP
        self.title("Talk & Type Receiver (Mac)")
        self.geometry("450x470")
        self.resizable(False, False) 
        ctk.set_appearance_mode("system")  
        ctk.set_default_color_theme("dark-blue") 

        # TIME-BASED COLOR LOGIC
        current_hour = datetime.now().hour
        if current_hour >= 18 or current_hour < 6:
            title_color = "powderblue"  
        else:
            title_color = "#3a7ebf"     

        # UI ELEMENTS
        self.title_label = ctk.CTkLabel(self, text="TALK & TYPE", text_color=title_color, font=("Arial", 30, "bold"))
        self.title_label.pack(pady=20)

        self.code_entry = ctk.CTkEntry(self, placeholder_text="Enter 7-Digit Code", width=200, height=35)
        self.code_entry.pack(pady=10)

        self.status_indicator = ctk.CTkLabel(self, text="● OFFLINE", text_color="red", font=("Arial", 14, "bold"))
        self.status_indicator.pack(pady=5)

        self.start_btn = ctk.CTkButton(self, text="Start", command=self.start_thread)
        self.start_btn.pack(pady=15)

        self.log = ctk.CTkTextbox(self, width=400, height=150)
        self.log.pack(pady=10, padx=20)
        self.log.insert("0.0", "\n1. Open your web app link.\n2. Enter code and click Start.\n")
        self.log.configure(state="disabled")

        self.is_currently_typing = False
        self.last_text = ""  

    def start_thread(self):
        room_code = self.code_entry.get().strip()
        if not room_code:
            self.add_to_log("ERROR: Please enter a room code first!")
            return

        self.status_indicator.configure(text="● LIVE", text_color="green")
        self.start_btn.configure(state="disabled", text="Monitoring...")
        
        threading.Thread(target=self.run_receiver, daemon=True).start()

    def run_receiver(self):
        room_code = self.code_entry.get().strip()
        print(f"[Network] Mac Monitoring started for room code: {room_code}")
        
        while True:
            if self.is_currently_typing:
                time.sleep(0.5)
                continue

            try:
                response = requests.get(f"{RENDER_URL}/get_text", params={'code': room_code}, timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    new_text = data.get('text')
                    
                    print(f"[Network Raw Check] Server returned: {new_text} | Last typed text was: {self.last_text}")
                    
                    if new_text is not None and str(new_text).strip() != "" and new_text != self.last_text:
                        self.is_currently_typing = True
                        self.last_text = new_text  
                        
                        self.after(0, self.add_to_log, "Received text sequence.")
                        time.sleep(0.1)
                        
                        mac_type_text(new_text)
                        
                        self.is_currently_typing = False
                        
            except Exception as e:
                print(f"[Network Error] {e}")
                self.after(0, self.add_to_log, f"Connection Error: {str(e)}")

            time.sleep(0.8)

    def add_to_log(self, msg):
        self.log.configure(state="normal")
        self.log.insert("end", f">>> {msg}\n")
        self.log.see("end")
        self.log.configure(state="disabled")

if __name__ == "__main__":
    app = TalkAndTypeReceiverMac()
    app.mainloop()