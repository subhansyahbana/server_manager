import json
import os
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove

# -------------------------------------------------------------------------
# MENU KEYBOARD BUILDERS (BILINGUAL SUPPORT)
# -------------------------------------------------------------------------

def load_custom_commands():
    """Loads custom commands from JSON database."""
    if os.path.exists("custom_commands.json"):
        try:
            with open("custom_commands.json", "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def get_main_menu(lang="EN"):
    if lang == "ID":
        keyboard = [['Sistem', 'Server'], ['Alat', 'Jaringan'], ['Perangkat Keras', 'Tutup Menu']]
    else:
        keyboard = [['System', 'Server'], ['Tools', 'Networking'], ['Hardware', 'Close Menu']]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_system_menu(lang="EN"):
    if lang == "ID":
        keyboard = [
            ['Mulai & Matikan', 'Pembaruan Software'], 
            ['Log Sistem', 'Proses Berjalan'], 
            ['Mulai Ulang Server', 'Matikan Server'], 
            ['Kembali ke Menu Utama']
        ]
    else:
        keyboard = [
            ['Bootup & Shutdown', 'Software Updates'], 
            ['System Logs', 'Running Processes'], 
            ['Reboot Server', 'Power Off Server'], 
            ['Back to Main Menu']
        ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_server_menu(lang="EN"):
    if lang == "ID":
        keyboard = [['Baca Pesan Pengguna', 'Status Server SSH'], ['Kembali ke Menu Utama']]
    else:
        keyboard = [['Read User Mail', 'SSH Server Status'], ['Back to Main Menu']]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_tools_menu(lang="EN"):
    if lang == "ID":
        keyboard = [['Shell Perintah', 'Perintah Kustom'], ['Status Sistem', 'Kembali ke Menu Utama']]
    else:
        keyboard = [['Command Shell', 'Custom Commands'], ['System Status', 'Back to Main Menu']]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_networking_menu(lang="EN"):
    if lang == "ID":
        keyboard = [['Pemantauan Bandwidth', 'Kembali ke Menu Utama']]
    else:
        keyboard = [['Bandwidth Monitoring', 'Back to Main Menu']]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_hardware_menu(lang="EN"):
    if lang == "ID":
        keyboard = [['Waktu Sistem', 'Kapasitas Disk Lokal'], ['Kembali ke Menu Utama']]
    else:
        keyboard = [['System Time', 'Local Disk Capacity'], ['Back to Main Menu']]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# -- CONFIRMATION MENU (SISTEM REM) --
def get_confirmation_menu(lang="EN"):
    if lang == "ID":
        keyboard = [['Yakin (OK)', 'Batal']]
    else:
        keyboard = [['Yes (OK)', 'Cancel']]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# -- DYNAMIC MENU FOR CUSTOM COMMANDS --
def get_custom_commands_menu(lang="EN"):
    """Builds a dynamic keyboard based on stored custom commands."""
    commands = load_custom_commands()
    keyboard = []
    
    # Render existing custom command buttons (2 per row for accessibility)
    row = []
    for cmd_name in commands.keys():
        row.append(cmd_name)
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
        
    # Append control logic buttons
    if lang == "ID":
        keyboard.append(['[+] Tambah Perintah', '[-] Hapus Perintah'])
        keyboard.append(['Kembali ke Menu Alat'])
    else:
        keyboard.append(['[+] Add Command', '[-] Delete Command'])
        keyboard.append(['Back to Tools Menu'])
        
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_remove_keyboard():
    return ReplyKeyboardRemove()