import logging
import asyncio
import json
import os
import sys
import re
import paramiko
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, CallbackContext

import menus
import commands

# -------------------------------------------------------------------------
# LOGGING & CONFIGURATION
# -------------------------------------------------------------------------
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def load_config():
    config_file = "config.json"
    if os.path.exists(config_file):
        with open(config_file, "r") as file:
            return json.load(file)
    else:
        config = {
            "TOKEN": "MASUKKAN_TOKEN_BOT_DI_SINI",
            "AUTHORIZED_CHAT_ID": 123456789,
            "SSH_HOST": "localhost",
            "SSH_PORT": 22,
            "SSH_USER": "root",
            "SSH_PASSWORD": "password_stb_anda"
        }
        with open(config_file, "w") as file:
            json.dump(config, file, indent=4)
        return config

config = load_config()
TOKEN = config["TOKEN"]
AUTHORIZED_CHAT_ID = config["AUTHORIZED_CHAT_ID"]

if TOKEN in ["YOUR_DEFAULT_TOKEN", "MASUKKAN_TOKEN_BOT_DI_SINI", ""]:
    logger.error("TOKEN belum diatur! Silakan buka file config.json, masukkan TOKEN bot Anda, lalu jalankan ulang.")
    sys.exit(1)

# -------------------------------------------------------------------------
# STATE MANAGEMENT
# -------------------------------------------------------------------------
user_preferences = {}
user_states = {}      
temp_cmd_data = {}    

def get_user_lang(chat_id):
    return user_preferences.get(chat_id, "EN")

def load_custom_commands():
    if os.path.exists("custom_commands.json"):
        try:
            with open("custom_commands.json", "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_custom_commands(data):
    with open("custom_commands.json", "w") as f:
        json.dump(data, f, indent=4)

# -------------------------------------------------------------------------
# SSH EXECUTION ENGINE (ASYNC MODE)
# -------------------------------------------------------------------------
ssh_sessions = {}

def get_ssh_session(chat_id, force_reconnect=False):
    if force_reconnect or chat_id not in ssh_sessions:
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(
                config["SSH_HOST"], port=config["SSH_PORT"], 
                username=config["SSH_USER"], password=config["SSH_PASSWORD"],
                timeout=5.0
            )
            shell = client.invoke_shell()
            ssh_sessions[chat_id] = {"client": client, "shell": shell}
        except Exception as e:
            logger.error(f"SSH Error: {e}")
            return None
    return ssh_sessions.get(chat_id, None)

async def run_remote_command(chat_id, command):
    session = get_ssh_session(chat_id)
    lang = get_user_lang(chat_id)
    
    if not session:
        return "Error: Unable to establish SSH connection (Timeout)." if lang == "EN" else "Error: Gagal terhubung ke STB (Waktu Habis)."

    try:
        shell = session["shell"]
        shell.send(command + "\n")
        # Menggunakan asyncio.sleep agar bot tetap responsif!
        await asyncio.sleep(1.5) 
        output = ""
        while shell.recv_ready():
            output += shell.recv(4096).decode(errors='ignore')
            await asyncio.sleep(0.1)
        output = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', output)
        return output.strip() or ("Task completed without output." if lang == "EN" else "Perintah dieksekusi tanpa teks balasan.")
    except Exception:
        session = get_ssh_session(chat_id, force_reconnect=True)
        if session:
            try:
                shell = session["shell"]
                shell.send(command + "\n")
                await asyncio.sleep(1.5)
                output = ""
                while shell.recv_ready():
                    output += shell.recv(4096).decode(errors='ignore')
                    await asyncio.sleep(0.1)
                output = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', output)
                return output.strip() or ("Task completed without output." if lang == "EN" else "Perintah dieksekusi tanpa teks balasan.")
            except Exception as ex:
                return f"Execution error after retry: {str(ex)}"
        return "Connection dropped. Failed to reconnect." if lang == "EN" else "Koneksi terputus dan gagal menyambung ulang otomatis."

async def send_control_character(chat_id, char):
    session = get_ssh_session(chat_id)
    lang = get_user_lang(chat_id)
    
    if not session:
        return "No active SSH session." if lang == "EN" else "Tidak ada sesi SSH aktif."
    try:
        shell = session["shell"]
        shell.send(char)
        
        await asyncio.sleep(1.0) 
        output = ""
        while shell.recv_ready():
            output += shell.recv(4096).decode(errors='ignore')
            await asyncio.sleep(0.1)
        output = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', output)
        return output.strip() or ("(Screen unchanged / No output)" if lang == "EN" else "(Layar tidak berubah / Tidak ada teks balasan)")
        
    except Exception:
        session = get_ssh_session(chat_id, force_reconnect=True)
        if session:
            try:
                shell = session["shell"]
                shell.send(char)
                await asyncio.sleep(1.0)
                output = ""
                while shell.recv_ready():
                    output += shell.recv(4096).decode(errors='ignore')
                    await asyncio.sleep(0.1)
                output = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', output)
                return output.strip() or ("(Screen unchanged)" if lang == "EN" else "(Layar tidak berubah)")
            except Exception as e:
                return f"Failed to send signal: {str(e)}"
        return "Connection dropped. Failed to reconnect." if lang == "EN" else "Koneksi terputus dan gagal menyambung ulang otomatis."

# -------------------------------------------------------------------------
# TELEGRAM COMMAND HANDLERS
# -------------------------------------------------------------------------
async def start(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id
    if chat_id != AUTHORIZED_CHAT_ID: return
    lang = get_user_lang(chat_id)
    user_states.pop(chat_id, None)
    temp_cmd_data.pop(chat_id, None)

    msg = "System Management Bot Initialized." if lang == "EN" else "Bot Manajemen Sistem Diaktifkan."
    await update.message.reply_text(msg, reply_markup=menus.get_main_menu(lang))

async def toggle_language(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id
    if chat_id != AUTHORIZED_CHAT_ID: return
    current_lang = get_user_lang(chat_id)
    new_lang = "ID" if current_lang == "EN" else "EN"
    user_preferences[chat_id] = new_lang
    msg = "Language switched to English. Type /start." if new_lang == "EN" else "Bahasa diubah ke Indonesia. Ketik /start."
    await update.message.reply_text(msg)

async def help_command(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id
    if chat_id != AUTHORIZED_CHAT_ID: return
    lang = get_user_lang(chat_id)
    
    if lang == "ID":
        help_text = """
*Panduan Penggunaan Bot:*
/start - Membuka ulang menu utama
/lang - Mengubah bahasa antarmuka (EN/ID)
/help - Menampilkan pesan panduan ini
/ssh <perintah> - Eksekusi cepat perintah Linux
/keyboard - Memanggil tombol kontrol darurat (Ctrl/Tab/ESC)
"""
    else:
        help_text = """
*Bot Usage Guide:*
/start - Open the main menu
/lang - Switch interface language (EN/ID)
/help - Show this help message
/ssh <command> - Quick execute a Linux command
/keyboard - Show emergency control buttons (Ctrl/Tab/ESC)
"""
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def ssh_command(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id
    if chat_id != AUTHORIZED_CHAT_ID: return
    lang = get_user_lang(chat_id)
    
    if not context.args:
        msg = "Format salah. Gunakan: /ssh <perintah>" if lang == "ID" else "Invalid format. Usage: /ssh <command>"
        await update.message.reply_text(msg)
        return
        
    command = " ".join(context.args)
    exec_msg = f"Executing: {command}..." if lang == "EN" else f"Mengeksekusi: {command}..."
    await update.message.reply_text(exec_msg)
    
    result = await run_remote_command(chat_id, command)
    out_msg = f"Output:\n{result}" if lang == "EN" else f"Hasil:\n{result}"
    await update.message.reply_text(out_msg)

async def keyboard_command(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id
    if chat_id != AUTHORIZED_CHAT_ID: return
    lang = get_user_lang(chat_id)
    
    if lang == "ID":
        inline_kb = [
            [InlineKeyboardButton("Ctrl+C", callback_data="ctrlc"), InlineKeyboardButton("Ctrl+D", callback_data="ctrld")],
            [InlineKeyboardButton("Ctrl+A D", callback_data="ctrlad"), InlineKeyboardButton("Ctrl+X", callback_data="ctrlx")],
            [InlineKeyboardButton("Tab (Indentasi)", callback_data="tab"), InlineKeyboardButton("Ctrl+Z (Jeda)", callback_data="ctrlz")],
            [InlineKeyboardButton("ESC (Keluar)", callback_data="esc"), InlineKeyboardButton("Enter Manual", callback_data="enter")]
        ]
        panel_msg = "Panel Kontrol Darurat:"
    else:
        inline_kb = [
            [InlineKeyboardButton("Ctrl+C", callback_data="ctrlc"), InlineKeyboardButton("Ctrl+D", callback_data="ctrld")],
            [InlineKeyboardButton("Ctrl+A D", callback_data="ctrlad"), InlineKeyboardButton("Ctrl+X", callback_data="ctrlx")],
            [InlineKeyboardButton("Tab (Indentation)", callback_data="tab"), InlineKeyboardButton("Ctrl+Z (Pause)", callback_data="ctrlz")],
            [InlineKeyboardButton("ESC (Escape)", callback_data="esc"), InlineKeyboardButton("Manual Enter", callback_data="enter")]
        ]
        panel_msg = "Emergency Control Panel:"
        
    inline_markup = InlineKeyboardMarkup(inline_kb)
    await update.message.reply_text(panel_msg, reply_markup=inline_markup)

# -------------------------------------------------------------------------
# INTERACTIVE HANDLERS
# -------------------------------------------------------------------------
async def inline_button_handler(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    chat_id = query.message.chat_id
    lang = get_user_lang(chat_id)
    
    command_map = {
        "ctrlc": "\x03", "ctrld": "\x04", "ctrlad": "\x01d", "ctrlx": "\x18", 
        "enter": "\n", "tab": "\t", "ctrlz": "\x1a", "esc": "\x1b"
    }
    
    if query.data in command_map:
        await query.answer("Memproses..." if lang == "ID" else "Processing...") 
        
        result = await send_control_character(chat_id, command_map[query.data])
        
        action_text = "Layar STB setelah" if lang == "ID" else "Terminal output after"
        await context.bot.send_message(chat_id=chat_id, text=f"{action_text} {query.data}:\n\n{result}")

async def handle_interaction(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id
    if chat_id != AUTHORIZED_CHAT_ID: return
    
    text = update.message.text.strip()
    lang = get_user_lang(chat_id)
    state = user_states.get(chat_id)

    if text in ["Batal", "Cancel"] and state in ["WAITING_ADD_NAME", "WAITING_ADD_BASH", "WAITING_DELETE_NAME"]:
        user_states.pop(chat_id, None)
        temp_cmd_data.pop(chat_id, None)
        cancel_msg = "Operasi dibatalkan." if lang == "ID" else "Operation canceled."
        await update.message.reply_text(cancel_msg, reply_markup=menus.get_custom_commands_menu(lang))
        return

    if text in ["Kembali ke Menu Alat", "Back to Tools Menu"] and state not in ["WAITING_CONFIRMATION", "WAITING_SHELL_COMMAND"]:
        user_states.pop(chat_id, None)
        temp_cmd_data.pop(chat_id, None)

    # -- CONVERSATIONAL LOGIC FOR COMMAND SHELL --
    if state == "WAITING_SHELL_COMMAND":
        if text.lower() in ["batal", "cancel", "keluar", "exit"]:
            user_states.pop(chat_id, None)
            msg = "Keluar dari Mode Shell." if lang == "ID" else "Exited Shell Mode."
            await update.message.reply_text(msg, reply_markup=menus.get_tools_menu(lang))
            return
            
        exec_msg = f"Executing: {text}..." if lang == "EN" else f"Mengeksekusi: {text}..."
        await update.message.reply_text(exec_msg)
        
        result = await run_remote_command(chat_id, text)
        out_msg = f"Output:\n{result}\n\n(Ketik perintah lain, atau ketik 'Batal' untuk keluar)" if lang == "ID" else f"Output:\n{result}\n\n(Type another command, or 'Cancel' to exit)"
        await update.message.reply_text(out_msg)
        return

    # -- CONVERSATIONAL LOGIC FOR CONFIRMATION --
    elif state == "WAITING_CONFIRMATION":
        cmd_to_run = temp_cmd_data.pop(chat_id, None)
        user_states.pop(chat_id, None)
        
        if text in ["Yakin (OK)", "Yes (OK)"]:
            if cmd_to_run:
                linux_cmd = commands.get_command(cmd_to_run)
                if not linux_cmd:
                    linux_cmd = load_custom_commands().get(cmd_to_run)
                
                if linux_cmd:
                    warn_msg = "⚠️ Mengeksekusi perintah. Bot mungkin terputus (Offline)." if lang == "ID" else "⚠️ Executing command. Bot may go offline."
                    await update.message.reply_text(warn_msg)
                    await run_remote_command(chat_id, linux_cmd)
                else:
                    await update.message.reply_text("Error: Perintah tidak ditemukan." if lang == "ID" else "Error: Command not found.")
            return
        else:
            cancel_msg = "Operasi dibatalkan. Kembali ke Menu Sistem." if lang == "ID" else "Operation canceled. Back to System Menu."
            await update.message.reply_text(cancel_msg, reply_markup=menus.get_system_menu(lang))
            return

    # -- CONVERSATIONAL LOGIC FOR CUSTOM COMMANDS --
    elif state == "WAITING_ADD_NAME":
        if text.startswith("[") or text in ["System", "Server", "Tools", "Batal", "Cancel"]:
            msg = "Invalid name. Please provide a standard text name:" if lang == "EN" else "Nama tidak valid. Masukkan nama teks standar:"
            await update.message.reply_text(msg)
            return
        temp_cmd_data[chat_id] = text
        user_states[chat_id] = "WAITING_ADD_BASH"
        msg = "Enter the Linux command for this button:" if lang == "EN" else "Ketik perintah Linux untuk tombol tersebut:"
        await update.message.reply_text(msg)
        return

    elif state == "WAITING_ADD_BASH":
        cmd_name = temp_cmd_data.pop(chat_id, "")
        custom_data = load_custom_commands()
        custom_data[cmd_name] = text
        save_custom_commands(custom_data)
        user_states.pop(chat_id, None)
        
        msg = f"Command '{cmd_name}' saved." if lang == "EN" else f"Perintah '{cmd_name}' berhasil disimpan."
        await update.message.reply_text(msg, reply_markup=menus.get_custom_commands_menu(lang))
        return

    elif state == "WAITING_DELETE_NAME":
        custom_data = load_custom_commands()
        if text in custom_data:
            del custom_data[text]
            save_custom_commands(custom_data)
            msg = f"Command '{text}' deleted." if lang == "EN" else f"Perintah '{text}' berhasil dihapus."
        else:
            msg = "Command not found." if lang == "EN" else "Perintah tidak ditemukan."
        user_states.pop(chat_id, None)
        await update.message.reply_text(msg, reply_markup=menus.get_custom_commands_menu(lang))
        return

    # -- STANDARD NAVIGATION LOGIC --
    if text in ["System", "Sistem"]:
        await update.message.reply_text("System Menu:" if lang == "EN" else "Menu Sistem:", reply_markup=menus.get_system_menu(lang))
    elif text in ["Server", "Server"]:
        await update.message.reply_text("Server Menu:" if lang == "EN" else "Menu Server:", reply_markup=menus.get_server_menu(lang))
    elif text in ["Tools", "Alat"]:
        await update.message.reply_text("Tools Menu:" if lang == "EN" else "Menu Alat:", reply_markup=menus.get_tools_menu(lang))
    elif text in ["Networking", "Jaringan"]:
        await update.message.reply_text("Networking Menu:" if lang == "EN" else "Menu Jaringan:", reply_markup=menus.get_networking_menu(lang))
    elif text in ["Hardware", "Perangkat Keras"]:
        await update.message.reply_text("Hardware Menu:" if lang == "EN" else "Menu Perangkat Keras:", reply_markup=menus.get_hardware_menu(lang))
    elif text in ["Back to Main Menu", "Kembali ke Menu Utama"]:
        await update.message.reply_text("Main Menu:" if lang == "EN" else "Menu Utama:", reply_markup=menus.get_main_menu(lang))
    elif text in ["Kembali ke Menu Alat", "Back to Tools Menu"]:
        await update.message.reply_text("Tools Menu:" if lang == "EN" else "Menu Alat:", reply_markup=menus.get_tools_menu(lang))
    elif text in ["Close Menu", "Tutup Menu"]:
        await update.message.reply_text("Interface deactivated." if lang == "EN" else "Antarmuka dinonaktifkan.", reply_markup=menus.get_remove_keyboard())
    
    # -- CUSTOM COMMAND TRIGGER --
    elif text in ["Custom Commands", "Perintah Kustom"]:
        await update.message.reply_text("Custom Commands:" if lang == "EN" else "Perintah Kustom:", reply_markup=menus.get_custom_commands_menu(lang))
    elif text in ["[+] Tambah Perintah", "[+] Add Command"]:
        user_states[chat_id] = "WAITING_ADD_NAME"
        await update.message.reply_text("Enter the name of the new button (or type 'Cancel'):" if lang == "EN" else "Ketik nama tombol baru Anda (atau ketik 'Batal'):", reply_markup=menus.get_remove_keyboard())
    elif text in ["[-] Hapus Perintah", "[-] Delete Command"]:
        user_states[chat_id] = "WAITING_DELETE_NAME"
        await update.message.reply_text("Type the exact name of the button to delete, or type 'Batal':" if lang == "EN" else "Ketik nama persis tombol yang ingin dihapus, atau ketik 'Batal':")

    # -- COMMAND EXECUTION ROUTING --
    else:
        linux_cmd = commands.get_command(text)
        if not linux_cmd:
            linux_cmd = load_custom_commands().get(text)

        if linux_cmd:
            if text in ["Reboot Server", "Mulai Ulang Server", "Power Off Server", "Matikan Server", "Reboot STB", "Mulai Ulang STB", "Power Off STB", "Matikan STB"]:
                user_states[chat_id] = "WAITING_CONFIRMATION"
                temp_cmd_data[chat_id] = text
                warn_msg = f"⚠️ PERINGATAN: Anda yakin ingin mengeksekusi '{text}'?" if lang == "ID" else f"⚠️ WARNING: Are you sure you want to execute '{text}'?"
                await update.message.reply_text(warn_msg, reply_markup=menus.get_confirmation_menu(lang))
                return

            exec_msg = f"Executing: {text}..." if lang == "EN" else f"Mengeksekusi: {text}..."
            await update.message.reply_text(exec_msg)
            
            result = await run_remote_command(chat_id, linux_cmd)
            out_msg = f"Output:\n{result}" if lang == "EN" else f"Hasil:\n{result}"
            await update.message.reply_text(out_msg)
            
        elif text in ["Command Shell", "Shell Perintah"]:
            user_states[chat_id] = "WAITING_SHELL_COMMAND"
            msg = "Mode Shell Aktif. Silakan ketik perintah Linux apa saja (atau ketik 'Batal' untuk keluar)." if lang == "ID" else "Shell Mode Active. Type any Linux command (or type 'Cancel' to exit)."
            await update.message.reply_text(msg, reply_markup=menus.get_remove_keyboard())
            
            if lang == "ID":
                inline_kb = [
                    [InlineKeyboardButton("Ctrl+C", callback_data="ctrlc"), InlineKeyboardButton("Ctrl+D", callback_data="ctrld")],
                    [InlineKeyboardButton("Ctrl+A D", callback_data="ctrlad"), InlineKeyboardButton("Ctrl+X", callback_data="ctrlx")],
                    [InlineKeyboardButton("Tab (Indentasi)", callback_data="tab"), InlineKeyboardButton("Ctrl+Z (Jeda)", callback_data="ctrlz")],
                    [InlineKeyboardButton("ESC (Keluar)", callback_data="esc"), InlineKeyboardButton("Enter Manual", callback_data="enter")]
                ]
                panel_msg = "Panel Kontrol Darurat:"
            else:
                inline_kb = [
                    [InlineKeyboardButton("Ctrl+C", callback_data="ctrlc"), InlineKeyboardButton("Ctrl+D", callback_data="ctrld")],
                    [InlineKeyboardButton("Ctrl+A D", callback_data="ctrlad"), InlineKeyboardButton("Ctrl+X", callback_data="ctrlx")],
                    [InlineKeyboardButton("Tab (Indentation)", callback_data="tab"), InlineKeyboardButton("Ctrl+Z (Pause)", callback_data="ctrlz")],
                    [InlineKeyboardButton("ESC (Escape)", callback_data="esc"), InlineKeyboardButton("Manual Enter", callback_data="enter")]
                ]
                panel_msg = "Emergency Control Panel:"
                
            inline_markup = InlineKeyboardMarkup(inline_kb)
            await update.message.reply_text(panel_msg, reply_markup=inline_markup)
            
        else:
            err_msg = "Unrecognized command." if lang == "EN" else "Perintah tidak dikenali."
            await update.message.reply_text(err_msg)

if __name__ == "__main__":
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("lang", toggle_language))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("ssh", ssh_command))
    app.add_handler(CommandHandler("keyboard", keyboard_command))
    
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_interaction))
    app.add_handler(CallbackQueryHandler(inline_button_handler))
    
    logger.info("Service operational.")
    app.run_polling()