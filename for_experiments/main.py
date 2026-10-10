import keyboard
import pystray
from PIL import Image, ImageDraw
import json
import os

CONFIG_FILE = "config.json"

class CyrillicTypist:
    def __init__(self):
        self.load_config()
        self.is_enabled = self.config.get("enabled_on_startup", True)
        self.current_layout = self.config.get("layout", "standard")
        self.map = self.config.get("mappings", {}).get(self.current_layout, {})
        self.icon = None

    def load_config(self):
        if not os.path.exists(CONFIG_FILE):
             print(f"Config file {CONFIG_FILE} not found. Please create it.")
             os._exit(1)
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
    def on_key_event(self, event):
        if event.event_type != keyboard.KEY_DOWN or not self.is_enabled:
            return True
        if keyboard.is_pressed('ctrl') or keyboard.is_pressed('alt') or keyboard.is_pressed('windows'):
            return True

        char = event.name
        
        if char in self.map:
            keyboard.write(self.map[char])
            return False 
            
        if len(char) == 1 and char.isalpha():
            lower_char = char.lower()
            if lower_char in self.map:
                mapped = self.map[lower_char]
                if event.modifiers or keyboard.is_pressed('shift'):
                    mapped = mapped.upper()
                keyboard.write(mapped)
                return False
        return True 

    def toggle_status(self):
        self.is_enabled = not self.is_enabled
        self.update_tray_icon()

    def update_tray_icon(self):
        if not self.icon: return
        color = "#4f46e5" if self.is_enabled else "#71717a"
        image = Image.new('RGB', (64, 64), color=color)
        dc = ImageDraw.Draw(image)
        dc.text((12, 24), "CYR" if self.is_enabled else "OFF", fill="white")
        self.icon.icon = image
        self.icon.title = f"Cyrillic Typist ( {'ON' if self.is_enabled else 'OFF'} )"

    def setup_tray(self):
        image = Image.new('RGB', (64, 64), color='#4f46e5')
        menu = pystray.Menu(
            pystray.MenuItem('Toggle Cyrillic (Ctrl+Alt+C)', lambda: self.toggle_status()),
            pystray.MenuItem('Quit', lambda: self.quit_app())
        )
        self.icon = pystray.Icon("cyrillic_typist", image, "Cyrillic Typist", menu)
        self.update_tray_icon()
        self.icon.run()

    def quit_app(self):
        keyboard.unhook_all()
        self.icon.stop()
        os._exit(0)

    def run(self):
        hotkey = self.config.get("hotkey_toggle", "ctrl+alt+c")
        keyboard.add_hotkey(hotkey, self.toggle_status)
        keyboard.hook(self.on_key_event, suppress=False) 
        print("Starting Cyrillic Typist Native Desktop Client...")
        self.setup_tray()

if __name__ == '__main__':
    app = CyrillicTypist()
    app.run()