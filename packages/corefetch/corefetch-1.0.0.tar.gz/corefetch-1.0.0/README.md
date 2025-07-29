<h1 align="center"> corefetch</h1>
<p align="center">
  <b>A powerful and fast system insights CLI tool, inspired by neofetch and metafetch.</b><br>
  <code>corefetch</code> gives you elegant, detailed information about your machine in seconds.
</p>

---

###  Features

- Custom Sharingan ASCII for flair
- Detailed OS, Kernel, Desktop, and Terminal insights
- Memory, Disk, CPU, GPU usage stats
- Local and Public IP display
- Battery Status, Temperature, Load Averages
- Installed packages summary (pip, apt, npm)
- Command Usage Insights (Beta)
- Clean CLI UX with loading animation
- Cross-platform support (Linux, macOS, Windows)

---

###  Preview

```shell
corefetch

itachi@desktop    
=============    

System:    
  OS: Ubuntu 22.04.3 LTS    
  Kernel: 5.15.0-84-generic    
  Architecture: x86_64    
  Uptime: 2d 14h 32m    

Software:    
  Packages: 2847 (apt), 23 (pip), 45 (npm)    
  Shell: bash 5.1.16    
  Desktop: GNOME    
  Terminal: gnome-terminal    

Hardware:    
  CPU: Intel i7-9700K (8C/16T)    
  GPU: NVIDIA GeForce RTX 3070    
  Memory: 8.2GB / 32.0GB (26%)    
  Disk: 245.8GB / 931.5GB (26%)    

Network:    
  Local IP: eth0 (192.168.1.100)    
  Public IP: 203.0.113.45    
  Resolution: 2560x1440    

Status:    
  Battery: 85% (Charging)    
  Temperature: 45.2°C    
  Load Avg: 0.85, 1.23, 1.45    
  Processes: 342    
```

---

###  Installation

Install the package via **pip**:

```bash
pip install corefetch
```

Run it:

```bash
corefetch
```

---

###  Supported Platforms

- Linux 🐧
- macOS 🍎
- Windows 🪟

---

###  Development

Clone the repo:

```bash
git clone https://github.com/yourusername/corefetch
cd corefetch
python corefetch.py
```

---

###  License

[MIT License](LICENSE)

---

###  Credits

Inspired by:  
- [neofetch](https://github.com/dylanaraps/neofetch)  
- [metafetch](https://github.com/volksgeistt/metafetch)
