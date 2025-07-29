# 🔍 opscan

**opscan** is a fast and lightweight Python-based port scanner that scans all 65,535 TCP ports of a target IP address and identifies which ports are open.

Designed for developers, security learners, and network enthusiasts who want a simple, no-nonsense CLI tool for port scanning.

---

## 🚀 Features

- 🔎 Scans all TCP ports (0–65535)
- ⚡ Uses multi-threading for faster results
- 📆 Easy to install as a Python package
- 🧪 Great for learning networking, ethical hacking, and recon basics

---

## 📦 Installation

Install from PyPI:

```bash
pip install opscan
```

> Or clone and install in editable mode:
> ```bash
> git clone https://github.com/mr-bala-kavi/pypacake-opscan.git
> cd opscan
> pip install -e .
> ```

---

## 🛠 Usage

Once installed, you can run it directly from your terminal:

```bash
opscan <IP_ADDRESS>
```

### Example:

```bash
opscan 192.168.1.1
```

The tool will scan all TCP ports from 0 to 65535 and display a list of open ports like this:

```
Scanning 192.168.1.1 for open ports (0–65535)...

👌 Open ports found:
  🔓 Port 22
  🔓 Port 80
  🔓 Port 443
```

---

## 🔐 Legal Disclaimer

This tool is intended **only for educational and ethical testing purposes**.  
**Never scan IPs that you do not own or do not have permission to scan.**

The author takes **no responsibility** for misuse.

---

## 📁 Project Structure

```
opscan/
│
├── opscan/                  # Core package
│   ├── __init__.py
│   ├── __main__.py          # CLI Entry point
│   └── scanner.py           # Port scanning logic
│
├── LICENSE
├── README.md
├── setup.py
```

---

## 👨‍💻 Author

Made with 💻 and ☕ by **Mr.Balakavi**  
GitHub: [@mr-bala-kavi](https://github.com/mr-bala-kavi)

---

## 📄 License

This project is licensed under the [MIT License](./LICENSE).

