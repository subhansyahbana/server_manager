# -------------------------------------------------------------------------
# COMMAND DICTIONARY MAP (BILINGUAL SUPPORT)
# -------------------------------------------------------------------------

COMMAND_MAP = {
    # -- System Menu --
    "Bootup & Shutdown": "systemctl list-units --type=service --state=running | head -n 20",
    "Mulai & Matikan": "systemctl list-units --type=service --state=running | head -n 20",
    
    "Software Updates": "sudo apt-get update && sudo apt-get --just-print upgrade | grep '^Inst' || echo 'No pending updates.'",
    "Pembaruan Software": "sudo apt-get update && sudo apt-get --just-print upgrade | grep '^Inst' || echo 'Tidak ada pembaruan tertunda.'",
    
    "System Logs": "journalctl -n 20 --no-pager",
    "Log Sistem": "journalctl -n 20 --no-pager",
    
    "Running Processes": "ps -eo pid,comm,%mem,%cpu --sort=-%cpu | head -n 15",
    "Proses Berjalan": "ps -eo pid,comm,%mem,%cpu --sort=-%cpu | head -n 15",

    # --- TOMBOL BARU: REBOOT & POWER OFF ---
    "Reboot Server": "sudo reboot",
    "Mulai Ulang Server": "sudo reboot",
    
    "Power Off Server": "sudo poweroff",
    "Matikan Server": "sudo poweroff",
    # ---------------------------------------

    # -- Server Menu --
    "Read User Mail": "tail -n 20 /var/mail/$(whoami) 2>/dev/null || echo 'No mail found for the current user.'",
    "Baca Pesan Pengguna": "tail -n 20 /var/mail/$(whoami) 2>/dev/null || echo 'Tidak ada email untuk pengguna saat ini.'",
    
    "SSH Server Status": "systemctl status ssh --no-pager",
    "Status Server SSH": "systemctl status ssh --no-pager",

    # -- Tools Menu --
    "System Status": "echo '--- MEMORY ---' && free -m && echo '\n--- UPTIME ---' && uptime",
    "Status Sistem": "echo '--- MEMORI ---' && free -m && echo '\n--- WAKTU AKTIF ---' && uptime",
    
    # -- Networking Menu --
    "Bandwidth Monitoring": "ip -s link",
    "Pemantauan Bandwidth": "ip -s link",

    # -- Hardware Menu --
    "System Time": "timedatectl",
    "Waktu Sistem": "timedatectl",
    
    "Local Disk Capacity": "df -h",
    "Kapasitas Disk Lokal": "df -h"
}

def get_command(button_text):
    """
    Retrieves the corresponding Linux shell command for a given button text.
    Returns None if the button text does not map to a direct command.
    """
    return COMMAND_MAP.get(button_text, None)