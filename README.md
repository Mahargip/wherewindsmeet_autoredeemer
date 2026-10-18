# Where Winds Meet Auto Code Redeemer

An automated desktop utility to redeem gift/promo codes in bulk for **Where Winds Meet** with a modern, sleek, and intuitive GUI.

![Platform](https://img.shields.io/badge/Platform-Windows-blue)
![Python](https://img.shields.io/badge/Python-3.10%2B-brightgreen)
![UI](https://img.shields.io/badge/UI-CustomTkinter-blueviolet)
![License](https://img.shields.io/badge/License-MIT-green)

---

## ✨ Features

- **🚀 Mass / Batch Redeeming**: Paste dozens of promo codes at once and let the tool automatically enter and redeem them in sequence.
- **🎯 Interactive Coordinate Calibration**: Easily calibrate and pinpoint the exact screen coordinates for the input field, the "Exchange/Redeem" button, and the "Confirm/Close" pop-up for your monitor resolution.
- **⏱️ Configurable Delays & Countdown**: Customize safety countdown intervals (giving you time to Alt-Tab into the game) and delay timers between keypresses/clicks for maximum reliability.
- **🛡️ Run as Admin Detection**: Automatically verifies administrator privileges to guarantee smooth input simulation (`pyautogui`/input hooks) over the game window.
- **💾 Local SQLite History**: Successfully redeemed and attempted codes are saved locally in `redeemed_history.db` so you never duplicate attempts.
- **🔔 Sound Effects & Chime Alerts**: Distinct audio cues on successful redemptions and task completion.
- **🎨 Modern Dark Mode UI**: Built with `CustomTkinter` for a clean, responsive, and aesthetic dark-themed user experience.
- **🌐 Bilingual Support**: Switch effortlessly between English and Indonesian.
- **🛑 Emergency Stop**: Press `ESC` or `F8` at any time to instantly abort the automation process.

---

## 📥 Getting Started

You can run this application in one of two ways:

### 🌟 Option 1: Standalone `.exe` (Recommended - No Python Required)
1. Navigate to the [**Releases**](https://github.com/Mahargip/wherewindsmeet_autoredeemer/releases) page of this repository.
2. Download the latest `WhereWindsMeet_AutoRedeemer.exe`.
3. Right-click the `.exe` file and select **Run as Administrator** *(Required for mouse and keyboard simulation to work within the game window)*.
4. You are ready to go!

---

### 🛠️ Option 2: Running from Source (Python)

If you prefer to run or modify the source code directly:

1. **Clone this repository:**
   ```bash
   git clone https://github.com/Mahargip/wherewindsmeet_autoredeemer.git
   cd wherewindsmeet_autoredeemer
   ```

2. **Install required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Launch the application:**
   ```bash
   python app.py
   ```
   *(Or double-click `run_as_admin.bat`)*

---

## 📖 Step-by-Step In-Game Guide

1. Launch **Where Winds Meet** and open the in-game **Redeem Code** menu.
2. Open **Where Winds Meet Auto Redeemer** as Administrator.
3. Paste your list of redeem codes into the text area (one code per line).
4. Click **Capture Position** to calibrate the buttons:
   - **Position 1**: Click on the code input text field.
   - **Position 2**: Click on the **Exchange / Redeem** button.
   - **Position 3**: Click on the reward confirmation or close button (optional).
5. Adjust the countdown timer (e.g., 5 seconds) to give yourself enough time to switch focus.
6. Click **Start**. Immediately switch (Alt-Tab) back to your game window before the countdown finishes.
7. Sit back and watch the application redeem all codes automatically!

---

## 🔨 Building the Standalone `.EXE`

If you made modifications to `app.py` and want to compile a standalone executable yourself:

1. Ensure PyInstaller is installed:
   ```bash
   pip install pyinstaller
   ```
2. Run the provided build script:
   ```cmd
   build_exe.bat
   ```
3. The newly generated binary will be placed in both `dist/` and the root folder as `WhereWindsMeet_AutoRedeemer.exe`.

---

## ⚠️ Disclaimer

This tool is a simple keyboard and mouse automation macro designed solely to save players time when redeeming large batches of community promo codes. It **DOES NOT** inject code, hook game memory, or modify game files in any way. Use responsibly.
