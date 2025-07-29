# corefetch.py

import os
import platform
import socket
import psutil
import requests
import shutil
import time
import datetime
import subprocess

YOKAI = """
⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣀⣤⣴⣶⣶⣶⣶⣦⣤⣀⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⣠⣴⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣦⣄⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⣠⣾⣿⣿⣿⣿⣿⣿⣿⠏⠁⠀⢶⣿⣿⣿⣿⣿⣿⣿⣷⣄⠀⠀⠀⠀
⠀⠀⢀⣾⣿⣿⣿⣿⣿⣿⡿⠿⣿⠀⠀⠀⠀⣿⠿⢿⣿⣿⣿⣿⣿⣿⣷⡀⠀⠀
⠀⢠⣾⣿⣿⣿⣿⣿⡿⠋⣠⣴⣿⣷⣤⣤⣾⣿⣦⣄⠙⢿⣿⣿⣿⣿⣿⣷⡄⠀
⠀⣼⣿⣿⣿⣿⣿⡏⢀⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⡀⢹⣿⣿⣿⣿⣿⣧⠀
⢰⣿⣿⣿⣿⣿⡿⠀⣾⣿⣿⣿⣿⠟⠉⠉⠻⣿⣿⣿⣿⣷⠀⢿⣿⣿⣿⣿⣿⡆
⢸⣿⣿⣿⣿⣿⣇⣰⣿⣿⣿⣿⡇⠀⠀⠀⠀⢸⣿⣿⣿⣿⣆⣸⣿⣿⣿⣿⣿⡇
⠸⣿⣿⣿⡿⣿⠟⠋⠙⠻⣿⣿⣿⣦⣀⣀⣴⣿⣿⣿⣿⠛⠙⠻⣿⣿⣿⣿⣿⠇
⠀⢻⣿⣿⣧⠉⠀⠀⠀⠀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀⠀⠀⠈⣿⣿⣿⡟⠀
⠀⠘⢿⣿⣿⣷⣦⣤⣴⣾⠛⠻⢿⣿⣿⣿⣿⡿⠟⠋⣿⣦⣤⠀⣰⣿⣿⡿⠃⠀
⠀⠀⠈⢿⣿⣿⣿⣿⣿⣿⣷⣶⣤⣄⣈⣁⣠⣤⣶⣾⣿⣿⣷⣾⣿⣿⡿⠁⠀⠀
⠀⠀⠀⠀⠙⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠋⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠙⠻⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠟⠋⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠉⠛⠻⠿⠿⠿⠿⠟⠛⠉⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀
"""

# ─── Loading Animation ─────────────────────────────────────
def loading():
    for i in range(5):
        print("\rLoading" + "." * (i % 4), end="")
        time.sleep(1)
    os.system('cls' if os.name == 'nt' else 'clear')

# ─── Helper Functions ───────────────────────────────────────
def get_uptime():
    uptime_seconds = time.time() - psutil.boot_time()
    return str(datetime.timedelta(seconds=int(uptime_seconds)))

def get_ip():
    try:
        return requests.get('https://api.ipify.org').text
    except:
        return 'Unavailable'

def get_resolution():
    try:
        if platform.system() == "Windows":
            import ctypes
            user32 = ctypes.windll.user32
            return f"{user32.GetSystemMetrics(0)}x{user32.GetSystemMetrics(1)}"
        else:
            output = subprocess.check_output('xrandr | grep "*"', shell=True)
            return output.decode().split()[0]
    except:
        return 'Unknown'

# ─── Main Info Display ───────────────────────────────────────
def main():
    loading()
    user = os.getenv("USER") or os.getenv("USERNAME")
    hostname = socket.gethostname()

    left_lines = YOKAI.splitlines()
    info_lines = []
    info_lines.append(f"{user}@{hostname}")
    info_lines.append("=" * 30)

    info_lines.append("System:")
    info_lines.append(f"  OS: {platform.system()} {platform.release()}")
    info_lines.append(f"  Kernel: {platform.version()}")
    info_lines.append(f"  Architecture: {platform.machine()}")
    info_lines.append(f"  Uptime: {get_uptime()}")

    info_lines.append("\nSoftware:")
    info_lines.append(f"  Shell: {os.getenv('SHELL') or 'Unknown'}")
    info_lines.append(f"  Desktop: {os.getenv('XDG_CURRENT_DESKTOP') or 'Unknown'}")
    info_lines.append(f"  Terminal: {os.getenv('TERM') or 'Unknown'}")
    info_lines.append(f"  Packages: apt(?) pip({len(psutil.pids())}) npm(?)")

    svmem = psutil.virtual_memory()
    total_memory = svmem.total / (1024 ** 3)
    used_memory = svmem.used / (1024 ** 3)

    disk = psutil.disk_usage('/')

    info_lines.append("\nHardware:")
    info_lines.append(f"  CPU: {platform.processor()}")
    info_lines.append(f"  Memory: {used_memory:.1f}GB / {total_memory:.1f}GB ({svmem.percent}%)")
    info_lines.append(f"  Disk: {disk.used // (2**30)}GB / {disk.total // (2**30)}GB ({disk.percent}%)")

    info_lines.append("\nNetwork:")
    info_lines.append(f"  Local IP: {socket.gethostbyname(hostname)}")
    info_lines.append(f"  Public IP: {get_ip()}")
    info_lines.append(f"  Resolution: {get_resolution()}")

    if hasattr(psutil, 'sensors_battery'):
        battery = psutil.sensors_battery()
        if battery:
            info_lines.append("\nStatus:")
            info_lines.append(f"  Battery: {battery.percent}% ({'Charging' if battery.power_plugged else 'Discharging'})")

    if hasattr(psutil, 'getloadavg'):
        load1, load5, load15 = psutil.getloadavg()
        info_lines.append(f"  Load Avg: {load1:.2f}, {load5:.2f}, {load15:.2f}")

    info_lines.append(f"  Processes: {len(psutil.pids())}")
    info_lines.append("\nCommand Usage Insights")
    info_lines.append("=" * 30)

    max_lines = max(len(left_lines), len(info_lines))
    left_lines += [" "] * (max_lines - len(left_lines))
    info_lines += [" "] * (max_lines - len(info_lines))

    for l, r in zip(left_lines, info_lines):
        print(f"{l:<50} {r}")

if __name__ == "__main__":
    main()
