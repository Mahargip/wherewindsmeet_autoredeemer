import os
import sys
import time
import threading
import ctypes
import json
import sqlite3
import winsound
import urllib.request
import urllib.error
import tkinter as tk
from tkinter import messagebox, ttk

# Try importing customtkinter for modern UI, fallback to standard tkinter
try:
    import customtkinter as ctk
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")
    HAS_CTK = True
except ImportError:
    HAS_CTK = False

try:
    import pyautogui
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.05
    HAS_PYAUTOGUI = True
except ImportError:
    HAS_PYAUTOGUI = False

try:
    import pyperclip
    HAS_PYPERCLIP = True
except ImportError:
    HAS_PYPERCLIP = False

try:
    import keyboard as win_keyboard
    HAS_KEYBOARD = True
except ImportError:
    HAS_KEYBOARD = False

try:
    from pynput import keyboard as pynput_keyboard
    HAS_PYNPUT = True
except ImportError:
    HAS_PYNPUT = False


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


def play_success_chime():
    """Play ascending success chime"""
    try:
        winsound.Beep(523, 120)  # C5
        time.sleep(0.04)
        winsound.Beep(659, 120)  # E5
        time.sleep(0.04)
        winsound.Beep(784, 250)  # G5
    except Exception:
        pass


def play_stop_chime():
    """Play descending alert tone on stop"""
    try:
        winsound.Beep(400, 150)
        time.sleep(0.04)
        winsound.Beep(300, 200)
    except Exception:
        pass


def format_seconds(seconds):
    """Format seconds into MM:SS or HH:MM:SS"""
    seconds = max(0, int(seconds))
    mins, secs = divmod(seconds, 60)
    hours, mins = divmod(mins, 60)
    if hours > 0:
        return f"{hours:02d}:{mins:02d}:{secs:02d}"
    return f"{mins:02d}:{secs:02d}"


class StorageManager:
    def __init__(self, db_path="redeemed_history.db", session_path="session_data.json"):
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(os.path.abspath(sys.executable))
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.join(base_dir, db_path)
        self.session_path = os.path.join(base_dir, session_path)
        self.init_db()

    def init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS redeemed_codes (
                    code TEXT PRIMARY KEY,
                    claimed_at TEXT,
                    status TEXT
                )
            """)
            conn.commit()

    def is_claimed(self, code):
        code_clean = code.strip().upper()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM redeemed_codes WHERE UPPER(code) = ?", (code_clean,))
            return cursor.fetchone() is not None

    def add_claimed(self, code, status="SUCCESS"):
        code_clean = code.strip().upper()
        claimed_at = time.strftime("%Y-%m-%d %H:%M:%S")
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO redeemed_codes (code, claimed_at, status)
                VALUES (?, ?, ?)
            """, (code_clean, claimed_at, status))
            conn.commit()

    def get_all_claimed(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT code, claimed_at, status FROM redeemed_codes ORDER BY claimed_at DESC")
            return cursor.fetchall()

    def clear_history(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM redeemed_codes")
            conn.commit()

    def count_claimed(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM redeemed_codes")
            row = cursor.fetchone()
            return row[0] if row else 0

    def save_session(self, data):
        try:
            with open(self.session_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print("Session save error:", e)

    def load_session(self):
        if os.path.exists(self.session_path):
            try:
                with open(self.session_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print("Session load error:", e)
        return {}


TRANSLATIONS = {
    "ID": {
        "title": "⚔️ Where Winds Meet - Auto Redeemer",
        "subtitle": "Aplikasi Otomatisasi Redeem Kode | Developer: Xuanyuan (ID: 4027655505)",
        "admin_active": "🛡️ Administrator: AKTIF",
        "admin_inactive": "⚠️ Bukan Admin (Buka via run_as_admin.bat jika ketikan tidak masuk)",
        "input_label": "Daftar Kode Redeem (Satu per baris):",
        "rec_header": "🎯 Rekam 3 Posisi Pointer (Klik & Arahkan Kursor dalam 3 detik):",
        "btn_pos1": "1️⃣ Tombol Buka Exchange",
        "btn_pos2": "2️⃣ Kolom Teks Kode (Field)",
        "btn_pos3": "3️⃣ Pop-Up OK / Confirm",
        "btn_pos1_short": "Exchange",
        "btn_pos2_short": "Field",
        "btn_pos3_short": "OK",
        "btn_reset_pos": "🔄 Reset Posisi",
        "confirm_reset_pos": "Apakah Anda yakin ingin mereset seluruh posisi mouse yang tersimpan?",
        "pos_info_default": "[1 Buka]: Auto Current | [2 Field]: Auto Current | [3 OK]: Auto Space Key",
        "pos_info_saved": "(💾 Tersimpan Permanen)",
        "seq_header": "🔄 Alur Eksekusi per Kode:",
        "chk_esc": "Tekan ESC setelah paste kode (unselect field)",
        "chk_space": "Tekan SPACE untuk Submit Claim",
        "lbl_countdown": "Hitung Mundur Start (s):",
        "lbl_enter_delay": "Jeda setelah Claim (s):",
        "lbl_space_delay": "Jeda antar Kode (s):",
        "chk_dry_run": "Simulasi (Dry Run)",
        "chk_sound": "🔊 Sound Notifikasi Selesai",
        "stat_header": "📊 Dashboard Statistik & Estimasi Waktu (ETA):",
        "stat_total": "Total: {val}",
        "stat_claimed": "Klaim Baru: {val}",
        "stat_skipped": "Skipped (DB): {val}",
        "stat_elapsed": "Waktu Jalan: {val}",
        "stat_eta": "Estimasi ETA: {val}",
        "btn_start": "🚀 START REDEEMING",
        "btn_stop": "🛑 STOP (F9)",
        "btn_readme": "📖 Readme",
        "btn_clear": "🗑️ Hapus List",
        "btn_sync": "🔄 New Code Sync (yar.gg)",
        "btn_manual_mark": "📝 Tandai Sudah Redeem",
        "manual_mark_title": "📝 Kelola & Tandai Kode Sudah Redeem",
        "manual_mark_subtitle": "Klik 'Simpan ke DB' di samping kode yang sudah Anda klaim manual di game agar masuk ke DB & dihapus dari field:",
        "btn_mark_claimed": "💾 Simpan ke DB",
        "btn_mark_all_claimed": "✅ Tandai SEMUA Sudah Redeem",
        "badge_claimed": "✅ Tersimpan di DB",
        "badge_unclaimed": "⏳ Belum di-redeem",
        "confirm_mark_all": "Apakah Anda yakin ingin menandai SEMUA kode di field sebagai sudah di-redeem dan menyimpannya ke Database?",
        "msg_no_codes_in_field": "Field kode redeem saat ini kosong. Masukkan kode atau klik 'New Code Sync' terlebih dahulu.",
        "btn_history": "📜 Riwayat DB ({count})",
        "status_ready": "Status: Siap.",
        "status_stopping": "Menghentikan...",
        "status_cancelled": "Proses dihentikan oleh pengguna.",
        "status_done": "Selesai! Semua kode telah diproses.",
        "status_running": "Sedang Proses Klaim Kode...",
        "creator_footer": "👤 Author / Creator: Xuanyuan | In-Game Name & ID: Xuanyuan - 4027655505",
        "rec_target_1": "Tombol Buka Exchange Menu",
        "rec_target_2": "Kolom Teks Kode (Field)",
        "rec_target_3": "Pop-Up OK / Confirm",
        "rec_countdown_msg": "🎯 Rekam Target #{num} ({target}): Arahkan kursor dalam {sec}s...",
        "rec_success_msg": "✅ Posisi {num} Terrekam: X={x}, Y={y}",
        "msg_skip": "⏭️ [SKIP DB] Kode '{code}' sudah pernah di-claim sebelumnya (Tersimpan di DB). Dilewati.",
        "history_title": "📜 Riwayat Kode yang Pernah Di-claim (Local DB)",
        "history_empty": "Belum ada riwayat kode yang tersimpan di Database.",
        "btn_clear_db": "⚠️ Hapus Riwayat Database",
        "confirm_clear_db": "Apakah Anda yakin ingin menghapus seluruh riwayat DB kode yang pernah di-claim?",
        "syncing": "🌐 Menghubungi codes.yar.gg & memfilter kode...",
        "sync_success": "✅ Sync Berhasil! {new_cnt} kode baru siap di-claim ({skipped_cnt} kode lama di DB dibersihkan).",
        "sync_no_new": "🎉 Semua ({total_active}) kode aktif dari yar.gg sudah pernah Anda klaim di DB lokal!",
        "sync_error": "❌ Gagal sync dari yar.gg: {err}",
        "tutorial_title": "📖 Tutorial & Petunjuk Penggunaan",
        "tutorial_text": (
            "==================================================\n"
            "  TUTORIAL & PETUNJUK PENGGUNAAN (BAHASA INDONESIA)\n"
            "==================================================\n\n"
            "Developer / Creator: Xuanyuan (ID: 4027655505)\n\n"
            "1. 🔄 FITUR NEW CODE SYNC (YAR.GG):\n"
            "   - Ambil kode WWM terbaru langsung dari website codes.yar.gg!\n"
            "   - Otomatis MENGHAPUS kode yang sudah pernah di-redeem (ada di DB)\n"
            "     sehingga hanya kode baru yang belum diklaim yang masuk ke field.\n\n"
            "2. 💾 POSISI MOUSE TERPANTAU & TERSIMPAN PERMANEN:\n"
            "   - Koordinat yang Anda set TIDAK AKAN HILANG saat aplikasi ditutup!\n"
            "   - Tombol akan berubah HIJAU (✅) dengan koordinat aktif saat terbuka.\n"
            "   - Anda bisa meresetnya kapan saja dengan tombol '🔄 Reset Posisi'.\n\n"
            "3. DASHBOARD STATISTIK & ESTIMASI WAKTU (ETA):\n"
            "   - Menampilkan total kode, jumlah klaim baru, jumlah kode yang\n"
            "     di-skip (DB), waktu berjalan, dan perkiraan sisa waktu (ETA).\n\n"
            "4. SOUND NOTIFIKASI:\n"
            "   - Membunyikan nada instan saat seluruh kode selesai di-claim!\n\n"
            "5. CARA MENJALANKAN:\n"
            "   - Buka via 'run_as_admin.bat' agar Windows mengizinkan simulasi klik/ketik.\n\n"
            "6. TOMBOL DARURAT:\n"
            "   - Tekan F9 di keyboard kapan saja untuk menghentikan otomatisasi.\n"
        )
    },
    "EN": {
        "title": "⚔️ Where Winds Meet - Auto Redeemer",
        "subtitle": "Code Redemption Automation Tool | Developer: Xuanyuan (ID: 4027655505)",
        "admin_active": "🛡️ Administrator: ACTIVE",
        "admin_inactive": "⚠️ Non-Admin (Run via run_as_admin.bat if typing fails)",
        "input_label": "Redeem Code List (One code per line):",
        "rec_header": "🎯 Record 3 Pointer Positions (Click & Point Cursor within 3s):",
        "btn_pos1": "1️⃣ Open Exchange Button",
        "btn_pos2": "2️⃣ Text Code Field",
        "btn_pos3": "3️⃣ Pop-Up OK / Confirm",
        "btn_pos1_short": "Exchange",
        "btn_pos2_short": "Field",
        "btn_pos3_short": "OK",
        "btn_reset_pos": "🔄 Reset Pos",
        "confirm_reset_pos": "Are you sure you want to reset all saved mouse positions?",
        "pos_info_default": "[1 Open]: Auto Current | [2 Field]: Auto Current | [3 OK]: Auto Space Key",
        "pos_info_saved": "(💾 Saved Permanently)",
        "seq_header": "🔄 Execution Sequence per Code:",
        "chk_esc": "Press ESC after pasting code (unselect field)",
        "chk_space": "Press SPACE to Submit Claim",
        "lbl_countdown": "Start Countdown (s):",
        "lbl_enter_delay": "Post-Claim Delay (s):",
        "lbl_space_delay": "Inter-Code Delay (s):",
        "chk_dry_run": "Simulation (Dry Run)",
        "chk_sound": "🔊 Sound Alert on Finish",
        "stat_header": "📊 Live Statistics & Estimated Time (ETA):",
        "stat_total": "Total: {val}",
        "stat_claimed": "New Claimed: {val}",
        "stat_skipped": "Skipped (DB): {val}",
        "stat_elapsed": "Elapsed: {val}",
        "stat_eta": "ETA: {val}",
        "btn_start": "🚀 START REDEEMING",
        "btn_stop": "🛑 STOP (F9)",
        "btn_readme": "📖 Readme",
        "btn_clear": "🗑️ Clear List",
        "btn_sync": "🔄 New Code Sync (yar.gg)",
        "btn_manual_mark": "📝 Mark as Redeemed",
        "manual_mark_title": "📝 Manage & Mark Redeemed Codes",
        "manual_mark_subtitle": "Click 'Save to DB' next to any code you already redeemed manually to store it in DB & remove from field:",
        "btn_mark_claimed": "💾 Save to DB",
        "btn_mark_all_claimed": "✅ Mark ALL as Redeemed",
        "badge_claimed": "✅ Saved in DB",
        "badge_unclaimed": "⏳ Not redeemed yet",
        "confirm_mark_all": "Are you sure you want to mark ALL codes in the field as redeemed and save them to Database?",
        "msg_no_codes_in_field": "Redeem code field is currently empty. Enter codes or click 'New Code Sync' first.",
        "btn_history": "📜 DB History ({count})",
        "status_ready": "Status: Ready.",
        "status_stopping": "Stopping...",
        "status_cancelled": "Process stopped by user.",
        "status_done": "Done! All codes processed.",
        "status_running": "Processing Redeem Codes...",
        "creator_footer": "👤 Author / Creator: Xuanyuan | In-Game Name & ID: Xuanyuan - 4027655505",
        "rec_target_1": "Open Exchange Menu Button",
        "rec_target_2": "Text Code Field",
        "rec_target_3": "Pop-Up OK / Confirm",
        "rec_countdown_msg": "🎯 Recording Target #{num} ({target}): Move cursor in {sec}s...",
        "rec_success_msg": "✅ Position {num} Recorded: X={x}, Y={y}",
        "msg_skip": "⏭️ [SKIP DB] Code '{code}' was already claimed previously (found in DB). Skipped.",
        "history_title": "📜 Claimed Codes History (Local DB)",
        "history_empty": "No claimed codes history found in Database yet.",
        "btn_clear_db": "⚠️ Clear DB History",
        "confirm_clear_db": "Are you sure you want to clear all claimed codes history from the DB?",
        "syncing": "🌐 Fetching codes from codes.yar.gg & filtering...",
        "sync_success": "✅ Sync Success! {new_cnt} new codes ready ({skipped_cnt} already-claimed codes removed).",
        "sync_no_new": "🎉 All ({total_active}) active codes from yar.gg are already redeemed in your DB!",
        "sync_error": "❌ Failed to sync from yar.gg: {err}",
        "tutorial_title": "📖 Tutorial & User Guide",
        "tutorial_text": (
            "==================================================\n"
            "        TUTORIAL & USER GUIDE (ENGLISH)\n"
            "==================================================\n\n"
            "Developer / Creator: Xuanyuan (ID: 4027655505)\n\n"
            "1. 🔄 NEW CODE SYNC (YAR.GG):\n"
            "   - Fetches the freshest WWM active codes directly from codes.yar.gg!\n"
            "   - Automatically PURGES already-redeemed codes stored in your DB,\n"
            "     so only unredeemed codes are loaded into the field.\n\n"
            "2. 💾 PERMANENT MOUSE POSITIONS:\n"
            "   - Your recorded coordinates DO NOT disappear when you close the app!\n"
            "   - Buttons highlight in GREEN (✅) with active coordinates on startup.\n"
            "   - Click '🔄 Reset Pos' anytime if you want to re-record.\n\n"
            "3. LIVE STATISTICS & ETA DASHBOARD:\n"
            "   - Tracks total codes, new claims, DB skipped codes, elapsed time,\n"
            "     and estimated time remaining (ETA) in real-time.\n\n"
            "4. SOUND ALERTS:\n"
            "   - Plays an ascending chime sequence when all codes complete!\n\n"
            "5. HOW TO RUN:\n"
            "   - Launch via 'run_as_admin.bat' for administrator privilege.\n\n"
            "6. EMERGENCY STOP:\n"
            "   - Press F9 on your keyboard anytime to halt automation instantly.\n"
        )
    },
    "ZH": {
        "title": "⚔️ 燕云十六声 (Where Winds Meet) - 自动兑换码工具",
        "subtitle": "兑换码自动处理工具 | 开发者: Xuanyuan (游戏ID: 4027655505)",
        "admin_active": "🛡️ 管理员权限: 已激活",
        "admin_inactive": "⚠️ 未以管理员运行 (如无法输入请通过 run_as_admin.bat 运行)",
        "input_label": "兑换码列表 (每行一个代码):",
        "rec_header": "🎯 记录3个鼠标指针位置 (点击按钮并在3秒内指向目标):",
        "btn_pos1": "1️⃣ 打开兑换界面按钮",
        "btn_pos2": "2️⃣ 兑换码输入框",
        "btn_pos3": "3️⃣ 确认/OK弹窗按钮",
        "btn_pos1_short": "界面",
        "btn_pos2_short": "输入框",
        "btn_pos3_short": "确认",
        "btn_reset_pos": "🔄 重置位置",
        "confirm_reset_pos": "您确定要重置所有保存的鼠标位置吗？",
        "pos_info_default": "[1 界面]: 自动当前位置 | [2 输入框]: 自动当前位置 | [3 确认]: 自动空格键",
        "pos_info_saved": "(💾 已永久保存)",
        "seq_header": "🔄 单个代码执行流程:",
        "chk_esc": "粘贴代码后按 ESC (取消选中输入框)",
        "chk_space": "按 SPACE 键提交兑换",
        "lbl_countdown": "启动倒计时 (秒):",
        "lbl_enter_delay": "兑换后延迟 (秒):",
        "lbl_space_delay": "代码间延迟 (秒):",
        "chk_dry_run": "模拟运行 (Dry Run)",
        "chk_sound": "🔊 完成时提示音",
        "stat_header": "📊 实时统计与剩余时间估算 (ETA):",
        "stat_total": "总数: {val}",
        "stat_claimed": "新兑换: {val}",
        "stat_skipped": "已跳过(DB): {val}",
        "stat_elapsed": "已用时间: {val}",
        "stat_eta": "预计剩余: {val}",
        "btn_start": "🚀 开始自动兑换",
        "btn_stop": "🛑 停止 (F9)",
        "btn_readme": "📖 说明",
        "btn_clear": "🗑️ 清空列表",
        "btn_sync": "🔄 同步新兑换码 (yar.gg)",
        "btn_manual_mark": "📝 标记已兑换",
        "manual_mark_title": "📝 管理并标记已兑换代码",
        "manual_mark_subtitle": "若您已在游戏中手动兑换过该代码，点击'存入数据库'以记录到DB并从输入框中移除：",
        "btn_mark_claimed": "💾 存入数据库",
        "btn_mark_all_claimed": "✅ 全部标记为已兑换",
        "badge_claimed": "✅ 已存入数据库",
        "badge_unclaimed": "⏳ 尚未兑换",
        "confirm_mark_all": "您确定要将输入框内的所有代码全部标记为已兑换并存入数据库吗？",
        "msg_no_codes_in_field": "兑换码输入框当前为空。请先输入代码或点击'同步新兑换码'。",
        "btn_history": "📜 兑换历史 ({count})",
        "status_ready": "状态: 就绪。",
        "status_stopping": "正在停止...",
        "status_cancelled": "用户已取消运行。",
        "status_done": "完成！所有兑换码处理完毕。",
        "status_running": "正在兑换代码...",
        "creator_footer": "👤 开发者 / Creator: Xuanyuan | 游戏名与ID: Xuanyuan - 4027655505",
        "rec_target_1": "打开兑换界面按钮",
        "rec_target_2": "兑换码输入框",
        "rec_target_3": "确认/OK弹窗按钮",
        "rec_countdown_msg": "🎯 记录目标 #{num} ({target}): 请在 {sec}秒 内指向目标...",
        "rec_success_msg": "✅ 位置 {num} 已记录: X={x}, Y={y}",
        "msg_skip": "⏭️ [跳过 DB] 代码 '{code}' 之前已在本地数据库中记录兑换。已自动跳过。",
        "history_title": "📜 已兑换代码历史记录 (本地数据库)",
        "history_empty": "本地数据库中暂无兑换记录。",
        "btn_clear_db": "⚠️ 清空数据库历史",
        "confirm_clear_db": "您确定要清空本地数据库中所有已兑换的历史记录吗？",
        "syncing": "🌐 正在从 codes.yar.gg 获取并过滤最新兑换码...",
        "sync_success": "✅ 同步成功！{new_cnt} 个未兑换新代码就绪 (已清除 {skipped_cnt} 个已兑换代码)。",
        "sync_no_new": "🎉 来自 yar.gg 的所有 ({total_active}) 个有效代码均已在本地数据库中兑换！",
        "sync_error": "❌ 同步失败: {err}",
        "tutorial_title": "📖 使用教程指南 (简体中文)",
        "tutorial_text": (
            "==================================================\n"
            "        燕云十六声 自动兑换码工具使用教程\n"
            "==================================================\n\n"
            "开发者 / 作者: Xuanyuan (游戏ID: 4027655505)\n\n"
            "1. 🔄 同步新兑换码 (YAR.GG):\n"
            "   - 从 codes.yar.gg 一键获取最新有效兑换码！\n"
            "   - 自动过滤并剔除已存在于数据库中的已兑换代码，\n"
            "     确保输入框内仅保留崭新的未兑换代码。\n\n"
            "2. 💾 鼠标位置永久保存:\n"
            "   - 记录的坐标在关闭程序后不会丢失！\n"
            "   - 重新打开时按钮直接显示绿色 (✅) 及已记录坐标。\n"
            "   - 如需重置可随时点击 '🔄 重置位置' 按钮。\n\n"
            "3. 实时统计与剩余时间估算 (ETA):\n"
            "   - 实时显示兑换码总数、新兑换数、跳过数、已用时间与预计剩余时间。\n\n"
            "4. 完成提示音:\n"
            "   - 当所有兑换码处理完毕时播放悦耳提示音！\n\n"
            "5. 如何运行:\n"
            "   - 建议通过 'run_as_admin.bat' 脚本运行。\n\n"
            "6. 紧急停止:\n"
            "   - 运行中随时按下键盘 F9 键即可立即中止程序。\n"
        )
    }
}


class AutoRedeemerApp:
    def __init__(self, root):
        self.root = root
        self.root.geometry("760x980")
        self.root.minsize(660, 840)

        self.storage = StorageManager()

        self.lang = "ID"  # Default Language: ID, EN, ZH
        self.is_running = False
        self.stop_requested = False
        self.thread = None
        self.listener = None

        # Statistics variables
        self.stat_total_val = 0
        self.stat_claimed_val = 0
        self.stat_skipped_val = 0
        self.stat_start_time = 0
        self.stat_elapsed_str = "00:00"
        self.stat_eta_str = "00:00"

        # Recorded Coordinates
        self.pos1 = None  # Tombol Buka Exchange Code (Re-open menu)
        self.pos2 = None  # Kolom Teks Kode (Field)
        self.pos3 = None  # Tombol Confirm / Pop-up OK (Opsional)

        self.setup_ui()
        self.setup_hotkey()

        # Load session & restore saved state
        self.load_session_state()

        # Handle window close protocol to save session
        self.root.protocol("WM_DELETE_WINDOW", self.on_window_close)

    def t(self, key, **kwargs):
        """Get translated text for given key"""
        text = TRANSLATIONS.get(self.lang, TRANSLATIONS["ID"]).get(key, key)
        if kwargs:
            try:
                return text.format(**kwargs)
            except Exception:
                pass
        return text

    def set_language(self, new_lang):
        """Switch current language and refresh UI"""
        self.lang = new_lang
        self.update_language()
        self.log(f"🌐 Language switched to: {new_lang}")

    def setup_ui(self):
        if HAS_CTK:
            self.build_ctk_ui()
        else:
            self.build_standard_ui()

    def build_ctk_ui(self):
        # Header Frame with Language Flags
        header = ctk.CTkFrame(self.root, corner_radius=10)
        header.pack(fill="x", padx=15, pady=8)

        # Top bar: Title + Flag Buttons
        top_bar = ctk.CTkFrame(header, fg_color="transparent")
        top_bar.pack(fill="x", padx=10, pady=(6, 2))

        self.title_label = ctk.CTkLabel(
            top_bar,
            text=self.t("title"),
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.title_label.pack(side="left", padx=5)

        # Flags selector
        flags_frame = ctk.CTkFrame(top_bar, fg_color="transparent")
        flags_frame.pack(side="right", padx=5)

        self.btn_flag_id = ctk.CTkButton(
            flags_frame, text="🇮🇩 ID", width=55, height=28,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#2980b9", command=lambda: self.set_language("ID")
        )
        self.btn_flag_id.pack(side="left", padx=2)

        self.btn_flag_en = ctk.CTkButton(
            flags_frame, text="🇬🇧 EN", width=55, height=28,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#7f8c8d", command=lambda: self.set_language("EN")
        )
        self.btn_flag_en.pack(side="left", padx=2)

        self.btn_flag_zh = ctk.CTkButton(
            flags_frame, text="🇨🇳 ZH", width=55, height=28,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#7f8c8d", command=lambda: self.set_language("ZH")
        )
        self.btn_flag_zh.pack(side="left", padx=2)

        self.subtitle_label = ctk.CTkLabel(
            header,
            text=self.t("subtitle"),
            font=ctk.CTkFont(size=11),
            text_color="#95a5a6"
        )
        self.subtitle_label.pack(pady=(0, 2))

        admin_status = self.t("admin_active") if is_admin() else self.t("admin_inactive")
        admin_color = "#2ecc71" if is_admin() else "#e67e22"

        self.admin_label = ctk.CTkLabel(
            header,
            text=admin_status,
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=admin_color
        )
        self.admin_label.pack(pady=(0, 6))

        # Main Layout
        main_frame = ctk.CTkFrame(self.root, corner_radius=10)
        main_frame.pack(fill="both", expand=True, padx=15, pady=5)

        # Code Input Header Box (Title + Clear Button)
        input_header_box = ctk.CTkFrame(main_frame, fg_color="transparent")
        input_header_box.pack(fill="x", padx=15, pady=(8, 2))

        self.input_label = ctk.CTkLabel(
            input_header_box,
            text=self.t("input_label"),
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.input_label.pack(side="left")

        self.clear_btn = ctk.CTkButton(
            input_header_box,
            text=self.t("btn_clear"),
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#e74c3c",
            hover_color="#c0392b",
            width=80, height=26,
            command=self.clear_code_textbox
        )
        self.clear_btn.pack(side="right")

        self.manual_mark_btn = ctk.CTkButton(
            input_header_box,
            text=self.t("btn_manual_mark"),
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#8e44ad",
            hover_color="#732d91",
            width=165, height=26,
            command=self.show_manual_mark_modal
        )
        self.manual_mark_btn.pack(side="right", padx=(0, 5))

        self.sync_btn = ctk.CTkButton(
            input_header_box,
            text=self.t("btn_sync"),
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#16a085",
            hover_color="#117864",
            width=175, height=26,
            command=self.start_sync_codes_thread
        )
        self.sync_btn.pack(side="right", padx=(0, 5))

        self.code_textbox = ctk.CTkTextbox(main_frame, height=120, font=("Consolas", 12))
        self.code_textbox.pack(fill="x", padx=15, pady=4)
        self.code_textbox.insert(
            "1.0",
            "WWM2026GIFTS\n"
            "WHEREWINDSMEET\n"
            "FREEEXCHANGECODE888\n"
        )

        # Position Recorder Section
        pos_frame = ctk.CTkFrame(main_frame)
        pos_frame.pack(fill="x", padx=15, pady=6)

        rec_header_box = ctk.CTkFrame(pos_frame, fg_color="transparent")
        rec_header_box.pack(fill="x", padx=10, pady=(6, 4))

        self.rec_header_lbl = ctk.CTkLabel(
            rec_header_box,
            text=self.t("rec_header"),
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#f1c40f"
        )
        self.rec_header_lbl.pack(side="left")

        self.reset_pos_btn = ctk.CTkButton(
            rec_header_box,
            text=self.t("btn_reset_pos"),
            font=ctk.CTkFont(size=10, weight="bold"),
            fg_color="#7f8c8d",
            hover_color="#636e72",
            width=85, height=22,
            command=self.reset_positions
        )
        self.reset_pos_btn.pack(side="right")

        pos_btn_box = ctk.CTkFrame(pos_frame, fg_color="transparent")
        pos_btn_box.pack(fill="x", padx=10, pady=(0, 4))

        self.pos1_btn = ctk.CTkButton(
            pos_btn_box,
            text=self.t("btn_pos1"),
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#34495e",
            hover_color="#2c3e50",
            command=lambda: self.record_position(1)
        )
        self.pos1_btn.pack(side="left", expand=True, fill="x", padx=2)

        self.pos2_btn = ctk.CTkButton(
            pos_btn_box,
            text=self.t("btn_pos2"),
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#34495e",
            hover_color="#2c3e50",
            command=lambda: self.record_position(2)
        )
        self.pos2_btn.pack(side="left", expand=True, fill="x", padx=2)

        self.pos3_btn = ctk.CTkButton(
            pos_btn_box,
            text=self.t("btn_pos3"),
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#34495e",
            hover_color="#2c3e50",
            command=lambda: self.record_position(3)
        )
        self.pos3_btn.pack(side="left", expand=True, fill="x", padx=2)

        self.pos_info_label = ctk.CTkLabel(
            pos_frame,
            text=self.t("pos_info_default"),
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        self.pos_info_label.pack(anchor="w", padx=10, pady=(0, 6))

        # Sequence Settings Frame
        seq_frame = ctk.CTkFrame(main_frame)
        seq_frame.pack(fill="x", padx=15, pady=4)

        self.seq_header_lbl = ctk.CTkLabel(
            seq_frame,
            text=self.t("seq_header"),
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#3498db"
        )
        self.seq_header_lbl.pack(anchor="w", padx=10, pady=(4, 2))

        # Step checkboxes
        self.step_esc_var = ctk.BooleanVar(value=True)
        self.step_esc_cb = ctk.CTkCheckBox(
            seq_frame,
            text=self.t("chk_esc"),
            variable=self.step_esc_var
        )
        self.step_esc_cb.pack(anchor="w", padx=15, pady=2)

        self.step_space_var = ctk.BooleanVar(value=True)
        self.step_space_cb = ctk.CTkCheckBox(
            seq_frame,
            text=self.t("chk_space"),
            variable=self.step_space_var
        )
        self.step_space_cb.pack(anchor="w", padx=15, pady=(2, 4))

        # Delays Frame
        delays_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        delays_frame.pack(fill="x", padx=15, pady=4)

        self.lbl_countdown = ctk.CTkLabel(delays_frame, text=self.t("lbl_countdown"))
        self.lbl_countdown.grid(row=0, column=0, sticky="w", pady=2)
        self.countdown_entry = ctk.CTkEntry(delays_frame, width=70)
        self.countdown_entry.grid(row=0, column=1, sticky="w", padx=5, pady=2)
        self.countdown_entry.insert(0, "5")

        self.lbl_enter_delay = ctk.CTkLabel(delays_frame, text=self.t("lbl_enter_delay"))
        self.lbl_enter_delay.grid(row=0, column=2, sticky="w", padx=(15, 0), pady=2)
        self.enter_delay_entry = ctk.CTkEntry(delays_frame, width=70)
        self.enter_delay_entry.grid(row=0, column=3, sticky="w", padx=5, pady=2)
        self.enter_delay_entry.insert(0, "1.2")

        self.lbl_space_delay = ctk.CTkLabel(delays_frame, text=self.t("lbl_space_delay"))
        self.lbl_space_delay.grid(row=1, column=0, sticky="w", pady=2)
        self.space_delay_entry = ctk.CTkEntry(delays_frame, width=70)
        self.space_delay_entry.grid(row=1, column=1, sticky="w", padx=5, pady=2)
        self.space_delay_entry.insert(0, "0.8")

        self.dry_run_var = ctk.BooleanVar(value=False)
        self.dry_run_cb = ctk.CTkCheckBox(
            delays_frame,
            text=self.t("chk_dry_run"),
            variable=self.dry_run_var
        )
        self.dry_run_cb.grid(row=1, column=2, columnspan=2, sticky="w", padx=(15, 0), pady=2)

        # Sound Alert Checkbox
        self.sound_var = ctk.BooleanVar(value=True)
        self.sound_cb = ctk.CTkCheckBox(
            delays_frame,
            text=self.t("chk_sound"),
            variable=self.sound_var
        )
        self.sound_cb.grid(row=2, column=0, columnspan=4, sticky="w", pady=2)

        # Statistics & ETA Dashboard Frame
        stat_frame = ctk.CTkFrame(main_frame, fg_color="#1e272e")
        stat_frame.pack(fill="x", padx=15, pady=6)

        self.stat_header_lbl = ctk.CTkLabel(
            stat_frame,
            text=self.t("stat_header"),
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#1bac78"
        )
        self.stat_header_lbl.pack(anchor="w", padx=10, pady=(4, 2))

        stat_labels_box = ctk.CTkFrame(stat_frame, fg_color="transparent")
        stat_labels_box.pack(fill="x", padx=10, pady=(0, 6))

        self.lbl_stat_total = ctk.CTkLabel(stat_labels_box, text=self.t("stat_total", val=0), font=ctk.CTkFont(size=11, weight="bold"))
        self.lbl_stat_total.pack(side="left", expand=True)

        self.lbl_stat_claimed = ctk.CTkLabel(stat_labels_box, text=self.t("stat_claimed", val=0), font=ctk.CTkFont(size=11, weight="bold"), text_color="#2ecc71")
        self.lbl_stat_claimed.pack(side="left", expand=True)

        self.lbl_stat_skipped = ctk.CTkLabel(stat_labels_box, text=self.t("stat_skipped", val=0), font=ctk.CTkFont(size=11, weight="bold"), text_color="#e67e22")
        self.lbl_stat_skipped.pack(side="left", expand=True)

        self.lbl_stat_elapsed = ctk.CTkLabel(stat_labels_box, text=self.t("stat_elapsed", val="00:00"), font=ctk.CTkFont(size=11, weight="bold"), text_color="#3498db")
        self.lbl_stat_elapsed.pack(side="left", expand=True)

        self.lbl_stat_eta = ctk.CTkLabel(stat_labels_box, text=self.t("stat_eta", val="00:00"), font=ctk.CTkFont(size=11, weight="bold"), text_color="#f1c40f")
        self.lbl_stat_eta.pack(side="left", expand=True)

        # Action Buttons Frame (Start, Stop, History DB, Readme)
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=6)

        self.start_btn = ctk.CTkButton(
            btn_frame,
            text=self.t("btn_start"),
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#27ae60",
            hover_color="#219150",
            height=38,
            command=self.start_redeem_thread
        )
        self.start_btn.pack(side="left", expand=True, fill="x", padx=2)

        self.stop_btn = ctk.CTkButton(
            btn_frame,
            text=self.t("btn_stop"),
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#c0392b",
            hover_color="#962d22",
            height=38,
            state="disabled",
            command=self.stop_redeem
        )
        self.stop_btn.pack(side="left", expand=True, fill="x", padx=2)

        self.history_btn = ctk.CTkButton(
            btn_frame,
            text=self.t("btn_history", count=self.storage.count_claimed()),
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#d35400",
            hover_color="#a04000",
            height=38,
            command=self.show_history_modal
        )
        self.history_btn.pack(side="left", expand=True, fill="x", padx=2)

        self.readme_btn = ctk.CTkButton(
            btn_frame,
            text=self.t("btn_readme"),
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#8e44ad",
            hover_color="#732d91",
            height=38,
            command=self.show_readme_modal
        )
        self.readme_btn.pack(side="left", expand=True, fill="x", padx=2)

        # Status & Progress Section
        status_frame = ctk.CTkFrame(main_frame)
        status_frame.pack(fill="both", expand=True, padx=15, pady=(4, 6))

        self.status_label = ctk.CTkLabel(
            status_frame,
            text=self.t("status_ready"),
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#3498db"
        )
        self.status_label.pack(anchor="w", padx=10, pady=(4, 2))

        self.progress_bar = ctk.CTkProgressBar(status_frame)
        self.progress_bar.pack(fill="x", padx=10, pady=3)
        self.progress_bar.set(0)

        # Log Text Box
        self.log_box = ctk.CTkTextbox(status_frame, height=100, font=("Consolas", 11))
        self.log_box.pack(fill="both", expand=True, padx=10, pady=(3, 6))

        # Footer Credits
        footer_frame = ctk.CTkFrame(self.root, corner_radius=8, fg_color="#1a252f")
        footer_frame.pack(fill="x", padx=15, pady=(0, 10))

        self.footer_label = ctk.CTkLabel(
            footer_frame,
            text=self.t("creator_footer"),
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#f1c40f"
        )
        self.footer_label.pack(pady=6)

    def build_standard_ui(self):
        # Fallback Standard Tkinter UI
        header = tk.Frame(self.root, bg="#2c3e50")
        header.pack(fill="x")

        self.title_label = tk.Label(header, text=self.t("title"), font=("Helvetica", 14, "bold"), fg="white", bg="#2c3e50")
        self.title_label.pack(pady=5)

        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill="both", expand=True)

        input_box = ttk.Frame(main_frame)
        input_box.pack(fill="x")
        self.input_label = ttk.Label(input_box, text=self.t("input_label"), font=("Helvetica", 10, "bold"))
        self.input_label.pack(side="left")

        self.clear_btn = tk.Button(input_box, text=self.t("btn_clear"), bg="#e74c3c", fg="white", font=("Helvetica", 9, "bold"), command=self.clear_code_textbox)
        self.clear_btn.pack(side="right")

        self.manual_mark_btn = tk.Button(input_box, text=self.t("btn_manual_mark"), bg="#8e44ad", fg="white", font=("Helvetica", 9, "bold"), command=self.show_manual_mark_modal)
        self.manual_mark_btn.pack(side="right", padx=3)

        self.sync_btn = tk.Button(input_box, text=self.t("btn_sync"), bg="#16a085", fg="white", font=("Helvetica", 9, "bold"), command=self.start_sync_codes_thread)
        self.sync_btn.pack(side="right", padx=3)

        self.code_textbox = tk.Text(main_frame, height=8, font=("Consolas", 11))
        self.code_textbox.pack(fill="x", pady=5)
        self.code_textbox.insert("1.0", "WWM2026GIFTS\nWHEREWINDSMEET\n")

        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill="x", pady=10)

        self.start_btn = tk.Button(btn_frame, text=self.t("btn_start"), bg="#27ae60", fg="white", font=("Helvetica", 10, "bold"), command=self.start_redeem_thread)
        self.start_btn.pack(side="left", expand=True, fill="x", padx=2)

        self.stop_btn = tk.Button(btn_frame, text=self.t("btn_stop"), bg="#c0392b", fg="white", font=("Helvetica", 10, "bold"), state="disabled", command=self.stop_redeem)
        self.stop_btn.pack(side="left", expand=True, fill="x", padx=2)

        self.history_btn = tk.Button(btn_frame, text=self.t("btn_history", count=self.storage.count_claimed()), bg="#d35400", fg="white", font=("Helvetica", 10, "bold"), command=self.show_history_modal)
        self.history_btn.pack(side="left", expand=True, fill="x", padx=2)

        self.readme_btn = tk.Button(btn_frame, text=self.t("btn_readme"), bg="#8e44ad", fg="white", font=("Helvetica", 10, "bold"), command=self.show_readme_modal)
        self.readme_btn.pack(side="left", expand=True, fill="x", padx=2)

        self.status_label = ttk.Label(main_frame, text=self.t("status_ready"), font=("Helvetica", 10, "bold"))
        self.status_label.pack(anchor="w", pady=5)

        self.progress_bar = ttk.Progressbar(main_frame, mode="determinate")
        self.progress_bar.pack(fill="x", pady=5)

        self.log_box = tk.Text(main_frame, height=8, font=("Consolas", 10))
        self.log_box.pack(fill="both", expand=True, pady=5)

        self.footer_label = tk.Label(main_frame, text=self.t("creator_footer"), font=("Helvetica", 9, "bold"), fg="#f1c40f")
        self.footer_label.pack(pady=4)

    def clear_code_textbox(self):
        """Clear the code textbox"""
        if HAS_CTK:
            self.code_textbox.delete("1.0", "end")
        else:
            self.code_textbox.delete("1.0", tk.END)
        self.log("🗑️ Code list cleared.")
        self.save_session_state()

    def update_stats_ui(self):
        """Refresh Dashboard labels"""
        if HAS_CTK:
            self.lbl_stat_total.configure(text=self.t("stat_total", val=self.stat_total_val))
            self.lbl_stat_claimed.configure(text=self.t("stat_claimed", val=self.stat_claimed_val))
            self.lbl_stat_skipped.configure(text=self.t("stat_skipped", val=self.stat_skipped_val))
            self.lbl_stat_elapsed.configure(text=self.t("stat_elapsed", val=self.stat_elapsed_str))
            self.lbl_stat_eta.configure(text=self.t("stat_eta", val=self.stat_eta_str))

    def update_language(self):
        """Update all text components to current language"""
        self.root.title(self.t("title"))
        db_cnt = self.storage.count_claimed()
        
        if HAS_CTK:
            self.title_label.configure(text=self.t("title"))
            self.subtitle_label.configure(text=self.t("subtitle"))
            self.admin_label.configure(
                text=self.t("admin_active") if is_admin() else self.t("admin_inactive")
            )
            self.input_label.configure(text=self.t("input_label"))
            self.clear_btn.configure(text=self.t("btn_clear"))
            self.manual_mark_btn.configure(text=self.t("btn_manual_mark"))
            self.sync_btn.configure(text=self.t("btn_sync"))
            self.rec_header_lbl.configure(text=self.t("rec_header"))
            self.reset_pos_btn.configure(text=self.t("btn_reset_pos"))
            self.update_position_buttons_ui()
            self.seq_header_lbl.configure(text=self.t("seq_header"))
            self.step_esc_cb.configure(text=self.t("chk_esc"))
            self.step_space_cb.configure(text=self.t("chk_space"))
            self.lbl_countdown.configure(text=self.t("lbl_countdown"))
            self.lbl_enter_delay.configure(text=self.t("lbl_enter_delay"))
            self.lbl_space_delay.configure(text=self.t("lbl_space_delay"))
            self.dry_run_cb.configure(text=self.t("chk_dry_run"))
            self.sound_cb.configure(text=self.t("chk_sound"))
            self.stat_header_lbl.configure(text=self.t("stat_header"))
            self.update_stats_ui()
            self.start_btn.configure(text=self.t("btn_start"))
            self.stop_btn.configure(text=self.t("btn_stop"))
            self.history_btn.configure(text=self.t("btn_history", count=db_cnt))
            self.readme_btn.configure(text=self.t("btn_readme"))
            self.footer_label.configure(text=self.t("creator_footer"))

            # Update flag button highlights
            self.btn_flag_id.configure(fg_color="#2980b9" if self.lang == "ID" else "#7f8c8d")
            self.btn_flag_en.configure(fg_color="#2980b9" if self.lang == "EN" else "#7f8c8d")
            self.btn_flag_zh.configure(fg_color="#2980b9" if self.lang == "ZH" else "#7f8c8d")
        else:
            self.title_label.configure(text=self.t("title"))
            self.input_label.configure(text=self.t("input_label"))
            self.clear_btn.configure(text=self.t("btn_clear"))
            if hasattr(self, 'manual_mark_btn'):
                self.manual_mark_btn.configure(text=self.t("btn_manual_mark"))
            if hasattr(self, 'sync_btn'):
                self.sync_btn.configure(text=self.t("btn_sync"))
            self.start_btn.configure(text=self.t("btn_start"))
            self.stop_btn.configure(text=self.t("btn_stop"))
            self.history_btn.configure(text=self.t("btn_history", count=db_cnt))
            self.readme_btn.configure(text=self.t("btn_readme"))
            self.footer_label.configure(text=self.t("creator_footer"))

    def update_position_buttons_ui(self):
        """Update position buttons and indicator label based on saved coordinates"""
        p1_set = self.pos1 is not None
        p2_set = self.pos2 is not None
        p3_set = self.pos3 is not None

        if HAS_CTK:
            if p1_set:
                self.pos1_btn.configure(
                    text=f"✅ 1️⃣ {self.t('btn_pos1_short')} ({self.pos1[0]}, {self.pos1[1]})",
                    fg_color="#27ae60",
                    hover_color="#219150"
                )
            else:
                self.pos1_btn.configure(
                    text=self.t("btn_pos1"),
                    fg_color="#34495e",
                    hover_color="#2c3e50"
                )

            if p2_set:
                self.pos2_btn.configure(
                    text=f"✅ 2️⃣ {self.t('btn_pos2_short')} ({self.pos2[0]}, {self.pos2[1]})",
                    fg_color="#27ae60",
                    hover_color="#219150"
                )
            else:
                self.pos2_btn.configure(
                    text=self.t("btn_pos2"),
                    fg_color="#34495e",
                    hover_color="#2c3e50"
                )

            if p3_set:
                self.pos3_btn.configure(
                    text=f"✅ 3️⃣ {self.t('btn_pos3_short')} ({self.pos3[0]}, {self.pos3[1]})",
                    fg_color="#27ae60",
                    hover_color="#219150"
                )
            else:
                self.pos3_btn.configure(
                    text=self.t("btn_pos3"),
                    fg_color="#34495e",
                    hover_color="#2c3e50"
                )

            p1_str = f"✅ X={self.pos1[0]}, Y={self.pos1[1]}" if p1_set else "Auto Current"
            p2_str = f"✅ X={self.pos2[0]}, Y={self.pos2[1]}" if p2_set else "Auto Current"
            p3_str = f"✅ X={self.pos3[0]}, Y={self.pos3[1]}" if p3_set else "Auto Space Key"
            info_text = f"[1 Buka]: {p1_str} | [2 Field]: {p2_str} | [3 OK]: {p3_str}"
            if p1_set and p2_set:
                info_text += f" | {self.t('pos_info_saved')}"
            self.pos_info_label.configure(
                text=info_text,
                text_color="#2ecc71" if (p1_set and p2_set) else "#95a5a6"
            )

    def reset_positions(self):
        """Reset all recorded mouse coordinates after user confirmation"""
        if messagebox.askyesno("Confirm Reset", self.t("confirm_reset_pos")):
            self.pos1 = None
            self.pos2 = None
            self.pos3 = None
            self.save_session_state()
            self.update_position_buttons_ui()
            self.log("🔄 Semua posisi mouse telah di-reset.")
            self.set_status("Posisi mouse di-reset.", "#3498db")

    def fetch_codes_api(self):
        """Fetch active codes from codes.yar.gg or worker fallback"""
        endpoints = [
            "https://codes.yar.gg/api/codes",
            "https://codes-backend.wwmcodes.workers.dev/v1/codes"
        ]
        for url in endpoints:
            try:
                req = urllib.request.Request(
                    url,
                    headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) WhereWindsMeetAutoRedeemer/1.0"
                    }
                )
                with urllib.request.urlopen(req, timeout=8) as response:
                    if response.status == 200:
                        payload = json.loads(response.read().decode("utf-8"))
                        active = payload.get("active", [])
                        codes = []
                        for item in active:
                            if isinstance(item, dict) and "code" in item:
                                c = item["code"].strip().upper()
                                if c and c not in codes:
                                    codes.append(c)
                            elif isinstance(item, str):
                                c = item.strip().upper()
                                if c and c not in codes:
                                    codes.append(c)
                        if codes:
                            return codes, payload.get("updatedAt", "")
            except Exception:
                continue
        return [], ""

    def start_sync_codes_thread(self):
        """Start code sync in background thread to avoid freezing UI"""
        if self.is_running:
            messagebox.showwarning("Warning", "Otomasi sedang berjalan. Hentikan proses terlebih dahulu.")
            return
        threading.Thread(target=self.sync_codes_from_web, daemon=True).start()

    def sync_codes_from_web(self):
        if HAS_CTK:
            self.sync_btn.configure(state="disabled")
        elif hasattr(self, 'sync_btn'):
            self.sync_btn.configure(state="disabled")

        self.set_status(self.t("syncing"), "#f39c12")
        self.log("🌐 [SYNC] Menghubungi server codes.yar.gg untuk mengambil kode terbaru...")

        try:
            fetched_codes, updated_at = self.fetch_codes_api()
            if not fetched_codes:
                err_msg = self.t("sync_error", err="Koneksi timeout / gagal mengambil data.")
                self.set_status(err_msg, "#e74c3c")
                self.log(f"❌ {err_msg}")
                messagebox.showerror("Sync Error", err_msg)
                return

            self.log(f"📥 [SYNC] Ditemukan {len(fetched_codes)} kode aktif di codes.yar.gg (Updated: {updated_at}).")

            # Ambil juga kode-kode yang ada di field saat ini (jika user ada mengetik kode custom)
            current_textbox_codes = self.get_clean_codes()

            # Gabungkan kandidat: kode dari web terlebih dahulu, lalu kode custom tambahan
            candidates = []
            for c in fetched_codes:
                if c not in candidates:
                    candidates.append(c)
            for c in current_textbox_codes:
                c_clean = c.strip().upper()
                if c_clean and c_clean not in candidates:
                    candidates.append(c_clean)

            # Filter: Hapus semua kode yang sudah ada di database (sudah pernah di-claim)
            unredeemed = []
            removed_claimed = []
            for c in candidates:
                if self.storage.is_claimed(c):
                    removed_claimed.append(c)
                else:
                    unredeemed.append(c)

            def apply_to_ui():
                if HAS_CTK:
                    self.code_textbox.delete("1.0", "end")
                    if unredeemed:
                        self.code_textbox.insert("1.0", "\n".join(unredeemed) + "\n")
                else:
                    self.code_textbox.delete("1.0", tk.END)
                    if unredeemed:
                        self.code_textbox.insert("1.0", "\n".join(unredeemed) + "\n")

                self.save_session_state()

                if unredeemed:
                    succ_msg = self.t("sync_success", new_cnt=len(unredeemed), skipped_cnt=len(removed_claimed))
                    self.set_status(succ_msg, "#2ecc71")
                    self.log(succ_msg)
                    if removed_claimed:
                        self.log(f"   ↳ {len(removed_claimed)} kode yang sudah pernah di-claim otomatis dibersihkan dari field: {', '.join(removed_claimed)}")
                    try:
                        winsound.Beep(659, 100)
                        winsound.Beep(880, 150)
                    except Exception:
                        pass
                else:
                    no_new_msg = self.t("sync_no_new", total_active=len(fetched_codes))
                    self.set_status(no_new_msg, "#3498db")
                    self.log(no_new_msg)
                    if removed_claimed:
                        self.log(f"   ↳ Seluruh {len(removed_claimed)} kode aktif dari web sudah tersimpan di database lokal Anda.")
                    messagebox.showinfo("New Code Sync", no_new_msg)

            self.root.after(0, apply_to_ui)

        finally:
            def restore_btn():
                if HAS_CTK:
                    self.sync_btn.configure(state="normal")
                elif hasattr(self, 'sync_btn'):
                    self.sync_btn.configure(state="normal")
            self.root.after(0, restore_btn)

    def show_readme_modal(self):
        """Show tutorial window"""
        modal = ctk.CTkToplevel(self.root) if HAS_CTK else tk.Toplevel(self.root)
        modal.title(self.t("tutorial_title"))
        modal.geometry("620x520")
        modal.grab_set()

        if HAS_CTK:
            title = ctk.CTkLabel(modal, text=self.t("tutorial_title"), font=ctk.CTkFont(size=16, weight="bold"))
            title.pack(pady=10)

            textbox = ctk.CTkTextbox(modal, font=("Consolas", 11))
            textbox.pack(fill="both", expand=True, padx=15, pady=10)
            textbox.insert("1.0", self.t("tutorial_text"))

            close_btn = ctk.CTkButton(modal, text="Close / Tutup", command=modal.destroy)
            close_btn.pack(pady=10)
        else:
            title = tk.Label(modal, text=self.t("tutorial_title"), font=("Helvetica", 14, "bold"))
            title.pack(pady=10)

            textbox = tk.Text(modal, font=("Consolas", 10))
            textbox.pack(fill="both", expand=True, padx=10, pady=10)
            textbox.insert("1.0", self.t("tutorial_text"))

            close_btn = tk.Button(modal, text="Close / Tutup", command=modal.destroy)
            close_btn.pack(pady=10)

    def show_history_modal(self):
        """Show modal window listing all claimed codes from DB"""
        modal = ctk.CTkToplevel(self.root) if HAS_CTK else tk.Toplevel(self.root)
        modal.title(self.t("history_title"))
        modal.geometry("580x480")
        modal.grab_set()

        records = self.storage.get_all_claimed()

        if HAS_CTK:
            title = ctk.CTkLabel(modal, text=f"{self.t('history_title')} ({len(records)})", font=ctk.CTkFont(size=15, weight="bold"))
            title.pack(pady=10)

            textbox = ctk.CTkTextbox(modal, font=("Consolas", 11))
            textbox.pack(fill="both", expand=True, padx=15, pady=10)

            if not records:
                textbox.insert("1.0", self.t("history_empty"))
            else:
                formatted = "KODE REDEEM                | WAKTU CLAIM           | STATUS\n"
                formatted += "-" * 60 + "\n"
                for code, claimed_at, status in records:
                    formatted += f"{code:<26} | {claimed_at} | {status}\n"
                textbox.insert("1.0", formatted)

            btn_box = ctk.CTkFrame(modal, fg_color="transparent")
            btn_box.pack(fill="x", padx=15, pady=10)

            def do_clear_history():
                if messagebox.askyesno("Confirm", self.t("confirm_clear_db"), parent=modal):
                    self.storage.clear_history()
                    textbox.delete("1.0", "end")
                    textbox.insert("1.0", self.t("history_empty"))
                    self.update_language()
                    self.log("⚠️ Cleared all local DB redemption history.")

            clear_db_btn = ctk.CTkButton(btn_box, text=self.t("btn_clear_db"), fg_color="#c0392b", hover_color="#962d22", command=do_clear_history)
            clear_db_btn.pack(side="left", padx=5)

            close_btn = ctk.CTkButton(btn_box, text="Close / Tutup", command=modal.destroy)
            close_btn.pack(side="right", padx=5)
        else:
            title = tk.Label(modal, text=self.t("history_title"), font=("Helvetica", 12, "bold"))
            title.pack(pady=10)

            textbox = tk.Text(modal, font=("Consolas", 10))
            textbox.pack(fill="both", expand=True, padx=10, pady=10)

            if not records:
                textbox.insert("1.0", self.t("history_empty"))
            else:
                formatted = "KODE REDEEM                | WAKTU CLAIM           | STATUS\n"
                formatted += "-" * 60 + "\n"
                for code, claimed_at, status in records:
                    formatted += f"{code:<26} | {claimed_at} | {status}\n"
                textbox.insert("1.0", formatted)

            btn_close = tk.Button(modal, text="Close / Tutup", command=modal.destroy)
            btn_close.pack(pady=10)

    def show_manual_mark_modal(self):
        """Show modal dialog listing current textbox codes with individual manual save to DB buttons"""
        codes = self.get_clean_codes()
        if not codes:
            messagebox.showinfo("Info", self.t("msg_no_codes_in_field"))
            return

        modal = ctk.CTkToplevel(self.root) if HAS_CTK else tk.Toplevel(self.root)
        modal.title(self.t("manual_mark_title"))
        modal.geometry("640x580")
        modal.minsize(540, 450)
        modal.grab_set()

        if HAS_CTK:
            # Header Frame
            header_box = ctk.CTkFrame(modal, fg_color="transparent")
            header_box.pack(fill="x", padx=16, pady=(12, 4))

            title_lbl = ctk.CTkLabel(
                header_box,
                text=f"{self.t('manual_mark_title')} ({len(codes)})",
                font=ctk.CTkFont(size=16, weight="bold")
            )
            title_lbl.pack(anchor="w")

            sub_lbl = ctk.CTkLabel(
                header_box,
                text=self.t("manual_mark_subtitle"),
                font=ctk.CTkFont(size=11),
                text_color="#95a5a6",
                wraplength=580,
                justify="left"
            )
            sub_lbl.pack(anchor="w", pady=(2, 0))

            # Action Top Bar
            action_bar = ctk.CTkFrame(modal, fg_color="#1a252f", corner_radius=8)
            action_bar.pack(fill="x", padx=16, pady=(6, 8))

            unclaimed_cnt = sum(1 for c in codes if not self.storage.is_claimed(c))
            counter_lbl = ctk.CTkLabel(
                action_bar,
                text=f"Total: {len(codes)} kode | Belum di DB: {unclaimed_cnt} kode",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color="#f1c40f"
            )
            counter_lbl.pack(side="left", padx=12, pady=6)

            # Scrollable Frame for codes list
            scroll_frame = ctk.CTkScrollableFrame(modal, width=600, height=370)
            scroll_frame.pack(fill="both", expand=True, padx=16, pady=(0, 8))

            row_map = {}

            def remove_code_from_textbox(target):
                cur = self.get_clean_codes()
                rem = [c for c in cur if c.strip().upper() != target.strip().upper()]
                self.code_textbox.delete("1.0", "end")
                if rem:
                    self.code_textbox.insert("1.0", "\n".join(rem) + "\n")
                self.save_session_state()
                self.update_language()

            def mark_code(code_str, button, status_label):
                self.storage.add_claimed(code_str, status="MANUAL_CLAIM")
                button.configure(
                    text=self.t("badge_claimed"),
                    fg_color="#27ae60",
                    state="disabled"
                )
                status_label.configure(text=self.t("badge_claimed"), text_color="#2ecc71")
                remove_code_from_textbox(code_str)
                self.log(f"💾 [MANUAL CLAIM] Kode '{code_str}' disimpan ke DB & dihapus dari field.")
                try:
                    winsound.Beep(750, 70)
                except Exception:
                    pass

                # Refresh counter
                rem_codes = self.get_clean_codes()
                unclaimed = sum(1 for c in rem_codes if not self.storage.is_claimed(c))
                counter_lbl.configure(text=f"Total: {len(rem_codes)} kode | Belum di DB: {unclaimed} kode")

            def mark_all_codes():
                if not messagebox.askyesno("Confirm", self.t("confirm_mark_all"), parent=modal):
                    return
                for c_str in list(row_map.keys()):
                    self.storage.add_claimed(c_str, status="MANUAL_CLAIM")
                    btn, slbl = row_map[c_str]
                    btn.configure(text=self.t("badge_claimed"), fg_color="#27ae60", state="disabled")
                    slbl.configure(text=self.t("badge_claimed"), text_color="#2ecc71")

                self.code_textbox.delete("1.0", "end")
                self.save_session_state()
                self.update_language()
                counter_lbl.configure(text="Total: 0 kode | Belum di DB: 0 kode")
                self.log(f"💾 [MANUAL CLAIM] Seluruh {len(codes)} kode telah disimpan ke DB & dibersihkan dari field.")
                try:
                    winsound.Beep(880, 150)
                except Exception:
                    pass

            mark_all_btn = ctk.CTkButton(
                action_bar,
                text=self.t("btn_mark_all_claimed"),
                font=ctk.CTkFont(size=11, weight="bold"),
                fg_color="#27ae60",
                hover_color="#219150",
                height=28,
                command=mark_all_codes
            )
            mark_all_btn.pack(side="right", padx=10, pady=6)

            # Populate each code card
            for idx, c in enumerate(codes, 1):
                row = ctk.CTkFrame(scroll_frame, fg_color="#202b32", corner_radius=6)
                row.pack(fill="x", pady=3, padx=2)

                code_lbl = ctk.CTkLabel(
                    row,
                    text=f"{idx:02d}.  {c}",
                    font=("Consolas", 13, "bold"),
                    anchor="w"
                )
                code_lbl.pack(side="left", padx=12, pady=7)

                is_saved = self.storage.is_claimed(c)

                status_lbl = ctk.CTkLabel(
                    row,
                    text=self.t("badge_claimed") if is_saved else self.t("badge_unclaimed"),
                    font=ctk.CTkFont(size=10, weight="bold"),
                    text_color="#2ecc71" if is_saved else "#e67e22"
                )
                status_lbl.pack(side="left", padx=10, pady=7)

                if is_saved:
                    btn = ctk.CTkButton(
                        row,
                        text=self.t("badge_claimed"),
                        font=ctk.CTkFont(size=11, weight="bold"),
                        fg_color="#2c3e50",
                        state="disabled",
                        width=140, height=28
                    )
                else:
                    btn = ctk.CTkButton(
                        row,
                        text=self.t("btn_mark_claimed"),
                        font=ctk.CTkFont(size=11, weight="bold"),
                        fg_color="#2980b9",
                        hover_color="#1f618d",
                        width=140, height=28
                    )
                    btn.configure(command=lambda code_val=c, b=btn, s=status_lbl: mark_code(code_val, b, s))

                btn.pack(side="right", padx=10, pady=5)
                row_map[c] = (btn, status_lbl)

            # Bottom Close Button
            bottom_box = ctk.CTkFrame(modal, fg_color="transparent")
            bottom_box.pack(fill="x", padx=16, pady=(4, 12))

            close_btn = ctk.CTkButton(
                bottom_box,
                text="Tutup / Selesai",
                font=ctk.CTkFont(size=12, weight="bold"),
                fg_color="#34495e",
                hover_color="#2c3e50",
                height=32,
                command=modal.destroy
            )
            close_btn.pack(side="right")
        else:
            # Fallback Tkinter Modal
            title = tk.Label(modal, text=self.t("manual_mark_title"), font=("Helvetica", 14, "bold"))
            title.pack(pady=10)

            frame = ttk.Frame(modal, padding=10)
            frame.pack(fill="both", expand=True)

            for idx, c in enumerate(codes, 1):
                row = ttk.Frame(frame)
                row.pack(fill="x", pady=2)
                lbl = ttk.Label(row, text=f"{idx}. {c}", font=("Consolas", 11, "bold"))
                lbl.pack(side="left", padx=5)

                def do_claim(target_c=c):
                    self.storage.add_claimed(target_c, status="MANUAL_CLAIM")
                    cur = self.get_clean_codes()
                    rem = [code for code in cur if code.strip().upper() != target_c.strip().upper()]
                    self.code_textbox.delete("1.0", tk.END)
                    if rem:
                        self.code_textbox.insert("1.0", "\n".join(rem) + "\n")
                    self.save_session_state()
                    self.update_language()

                btn = tk.Button(row, text=self.t("btn_mark_claimed"), bg="#2980b9", fg="white", font=("Helvetica", 9), command=do_claim)
                btn.pack(side="right", padx=5)

            btn_close = tk.Button(modal, text="Close / Tutup", command=modal.destroy)
            btn_close.pack(pady=10)

    def save_session_state(self):
        """Save current GUI state & code text list to session_data.json"""
        if HAS_CTK:
            code_text = self.code_textbox.get("1.0", "end")
        else:
            code_text = self.code_textbox.get("1.0", tk.END)

        data = {
            "lang": self.lang,
            "code_text": code_text,
            "pos1": self.pos1,
            "pos2": self.pos2,
            "pos3": self.pos3,
            "countdown": self.countdown_entry.get(),
            "enter_delay": self.enter_delay_entry.get(),
            "space_delay": self.space_delay_entry.get(),
            "step_esc": self.step_esc_var.get() if HAS_CTK else True,
            "step_space": self.step_space_var.get() if HAS_CTK else True,
            "sound": self.sound_var.get() if HAS_CTK else True,
        }
        self.storage.save_session(data)

    def load_session_state(self):
        """Restore saved session state if available"""
        session = self.storage.load_session()
        if not session:
            return

        if "lang" in session:
            self.lang = session["lang"]
        if "pos1" in session and session["pos1"]:
            self.pos1 = tuple(session["pos1"])
        if "pos2" in session and session["pos2"]:
            self.pos2 = tuple(session["pos2"])
        if "pos3" in session and session["pos3"]:
            self.pos3 = tuple(session["pos3"])

        if "code_text" in session and session["code_text"]:
            if HAS_CTK:
                self.code_textbox.delete("1.0", "end")
                self.code_textbox.insert("1.0", session["code_text"])
            else:
                self.code_textbox.delete("1.0", tk.END)
                self.code_textbox.insert("1.0", session["code_text"])

        if "countdown" in session:
            self.countdown_entry.delete(0, tk.END)
            self.countdown_entry.insert(0, str(session["countdown"]))
        if "enter_delay" in session:
            self.enter_delay_entry.delete(0, tk.END)
            self.enter_delay_entry.insert(0, str(session["enter_delay"]))
        if "space_delay" in session:
            self.space_delay_entry.delete(0, tk.END)
            self.space_delay_entry.insert(0, str(session["space_delay"]))

        if HAS_CTK:
            if "step_esc" in session:
                self.step_esc_var.set(session["step_esc"])
            if "step_space" in session:
                self.step_space_var.set(session["step_space"])
            if "sound" in session:
                self.sound_var.set(session["sound"])

        self.update_language()

    def on_window_close(self):
        """Triggered when user closes the app window"""
        self.save_session_state()
        self.root.destroy()

    def log(self, message):
        timestamp = time.strftime("[%H:%M:%S] ")
        full_msg = f"{timestamp}{message}\n"
        if HAS_CTK:
            self.log_box.insert("end", full_msg)
            self.log_box.see("end")
        else:
            self.log_box.insert(tk.END, full_msg)
            self.log_box.see(tk.END)

    def set_status(self, text, color="#3498db"):
        if HAS_CTK:
            self.status_label.configure(text=f"Status: {text}", text_color=color)
        else:
            self.status_label.configure(text=f"Status: {text}")

    def setup_hotkey(self):
        if HAS_PYNPUT:
            def on_press(key):
                try:
                    if key == pynput_keyboard.Key.f9:
                        if self.is_running:
                            self.log("⚠️ F9 Hotkey Pressed! Stopping automation...")
                            self.stop_redeem()
                except Exception:
                    pass

            self.listener = pynput_keyboard.Listener(on_press=on_press)
            self.listener.daemon = True
            self.listener.start()

    def record_position(self, pos_num):
        """Record screen coordinates after 3 seconds countdown"""
        targets = {
            1: self.t("rec_target_1"),
            2: self.t("rec_target_2"),
            3: self.t("rec_target_3")
        }
        
        def worker():
            target_name = targets.get(pos_num, f"Posisi #{pos_num}")
            for i in range(3, 0, -1):
                msg = self.t("rec_countdown_msg", num=pos_num, target=target_name, sec=i)
                self.set_status(msg, "#f39c12")
                self.log(msg)
                time.sleep(1.0)
            
            if HAS_PYAUTOGUI:
                x, y = pyautogui.position()
                if pos_num == 1:
                    self.pos1 = (x, y)
                elif pos_num == 2:
                    self.pos2 = (x, y)
                else:
                    self.pos3 = (x, y)

                succ_msg = self.t("rec_success_msg", num=pos_num, x=x, y=y)
                self.log(succ_msg)
                self.save_session_state()

                self.root.after(0, self.update_position_buttons_ui)
                self.set_status("OK! Koordinat tersimpan permanen.", "#2ecc71")

        threading.Thread(target=worker, daemon=True).start()

    def get_clean_codes(self):
        if HAS_CTK:
            raw_text = self.code_textbox.get("1.0", "end")
        else:
            raw_text = self.code_textbox.get("1.0", tk.END)

        lines = raw_text.splitlines()
        codes = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith("#"):
                codes.append(line)
        return codes

    def start_redeem_thread(self):
        codes = self.get_clean_codes()
        if not codes:
            messagebox.showwarning("Warning", "Please enter at least 1 redeem code.")
            return

        self.save_session_state()

        try:
            countdown = float(self.countdown_entry.get())
            enter_delay = float(self.enter_delay_entry.get())
            space_delay = float(self.space_delay_entry.get())
        except ValueError:
            messagebox.showerror("Error Input", "Invalid number input for timing delays.")
            return

        self.is_running = True
        self.stop_requested = False

        if HAS_CTK:
            self.start_btn.configure(state="disabled")
            self.stop_btn.configure(state="normal")
        else:
            self.start_btn.configure(state="disabled")
            self.stop_btn.configure(state="normal")

        do_esc = self.step_esc_var.get() if HAS_CTK else True
        do_space = self.step_space_var.get() if HAS_CTK else True
        do_sound = self.sound_var.get() if HAS_CTK else True

        self.thread = threading.Thread(
            target=self.run_redemption_process,
            args=(codes, countdown, enter_delay, space_delay, self.dry_run_var.get(), do_esc, do_space, do_sound),
            daemon=True
        )
        self.thread.start()

    def stop_redeem(self):
        if self.is_running:
            self.stop_requested = True
            self.set_status(self.t("status_stopping"), "#e74c3c")
            self.log("🛑 Stopping process...")

    def paste_code(self, code):
        """Paste code using clipboard"""
        if HAS_PYPERCLIP:
            pyperclip.copy(code)
            time.sleep(0.05)
        
        if HAS_PYAUTOGUI:
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.05)
            pyautogui.hotkey('ctrl', 'v')
        elif HAS_KEYBOARD:
            win_keyboard.send('ctrl+a')
            time.sleep(0.05)
            win_keyboard.send('ctrl+v')

    def run_redemption_process(self, codes, countdown, enter_delay, space_delay, is_dry_run, do_esc, do_space, do_sound):
        total = len(codes)
        self.stat_total_val = total
        self.stat_claimed_val = 0
        self.stat_skipped_val = 0
        self.stat_start_time = time.time()
        self.stat_elapsed_str = "00:00"
        self.stat_eta_str = "00:00"
        self.update_stats_ui()

        self.log(f"📋 Starting redemption ({total} codes). Checking Local DB...")
        if is_dry_run:
            self.log("🔍 SIMULATION MODE (Dry Run) ACTIVE.")

        # Countdown phase
        for i in range(int(countdown), 0, -1):
            if self.stop_requested:
                break
            self.set_status(f"Starting in {i}s... Switch window!", "#f39c12")
            self.log(f"⏳ Countdown: {i}s...")
            time.sleep(1.0)

        if self.stop_requested:
            if do_sound:
                play_stop_chime()
            self.finish_process(cancelled=True)
            return

        self.set_status(self.t("status_running"), "#2ecc71")
        start_process_time = time.time()

        for idx, code in enumerate(codes, 1):
            if self.stop_requested:
                self.log(f"⚠️ Cancelled at code #{idx} / {total}.")
                break

            # Calculate live ETA and Elapsed time
            now = time.time()
            elapsed_sec = now - start_process_time
            self.stat_elapsed_str = format_seconds(elapsed_sec)

            avg_time_per_code = elapsed_sec / idx if idx > 0 else 2.5
            remaining_codes = total - idx
            eta_sec = remaining_codes * avg_time_per_code
            self.stat_eta_str = format_seconds(eta_sec)

            progress_val = idx / total
            if HAS_CTK:
                self.progress_bar.set(progress_val)
            else:
                self.progress_bar['value'] = progress_val * 100

            # DB Verification / Skip Check
            if self.storage.is_claimed(code):
                self.stat_skipped_val += 1
                self.update_stats_ui()
                skip_msg = self.t("msg_skip", code=code)
                self.log(skip_msg)
                time.sleep(0.08)
                continue

            self.log(f"▶️ [{idx}/{total}] Processing Code: {code}")

            if not is_dry_run and HAS_PYAUTOGUI:
                try:
                    # Step 1: Click Open Exchange Menu Button (pos1)
                    if self.pos1:
                        pyautogui.click(self.pos1[0], self.pos1[1])
                        self.log(f"   ↳ 1. Click Open Exchange Menu (Pos 1: X={self.pos1[0]}, Y={self.pos1[1]}).")
                        time.sleep(0.3)
                    else:
                        pyautogui.click()
                        time.sleep(0.2)

                    if self.stop_requested:
                        break

                    # Step 2: Click Code Text Field (pos2)
                    if self.pos2:
                        pyautogui.click(self.pos2[0], self.pos2[1])
                        self.log(f"   ↳ 2. Click Code Field (Pos 2: X={self.pos2[0]}, Y={self.pos2[1]}).")
                        time.sleep(0.15)

                    if self.stop_requested:
                        break

                    # Step 3: Paste Code (Ctrl+A -> Ctrl+V)
                    self.paste_code(code)
                    self.log(f"   ↳ 3. Paste '{code}' into field.")
                    time.sleep(0.2)

                    if self.stop_requested:
                        break

                    # Step 4: Press ESC (unselect field)
                    if do_esc:
                        pyautogui.press('esc')
                        self.log("   ↳ 4. Press ESC (unselect field).")
                        time.sleep(0.2)

                    if self.stop_requested:
                        break

                    # Step 5: Press SPACE (Submit Claim)
                    if do_space:
                        pyautogui.press('space')
                        self.log("   ↳ 5. Press SPACE (Submit Claim).")

                    self.log(f"   ↳ Waiting server response ({enter_delay}s)...")
                    time.sleep(enter_delay)

                    if self.stop_requested:
                        break

                    # Step 6: Click Pop-Up OK / Confirm (pos3) if recorded, else press SPACE
                    if self.pos3:
                        pyautogui.click(self.pos3[0], self.pos3[1])
                        self.log(f"   ↳ 6. Click Pop-Up OK (Pos 3: X={self.pos3[0]}, Y={self.pos3[1]}).")
                    else:
                        pyautogui.press('space')

                    # Mark code as claimed in local SQLite database!
                    self.storage.add_claimed(code)
                    self.stat_claimed_val += 1
                    self.update_stats_ui()

                    self.log(f"💾 [DB SAVED] Code '{code}' registered to Local DB.")
                    self.update_language()

                    time.sleep(space_delay)

                except Exception as e:
                    self.log(f"❌ Error during execution: {str(e)}")
                    break
            else:
                # Dry run simulation
                time.sleep(0.4)
                self.log(f"   ↳ [Dry Run] Click Open -> Click Field -> Paste '{code}' -> Press ESC -> Press SPACE -> Wait {enter_delay}s -> Click OK -> Wait {space_delay}s")
                self.storage.add_claimed(code, status="DRY_RUN")
                self.stat_claimed_val += 1
                self.update_stats_ui()
                self.update_language()
                time.sleep(0.4)

        self.stat_eta_str = "00:00"
        self.update_stats_ui()

        if do_sound:
            if self.stop_requested:
                play_stop_chime()
            else:
                play_success_chime()

        self.finish_process(cancelled=self.stop_requested)

    def finish_process(self, cancelled=False):
        self.is_running = False
        if HAS_CTK:
            self.start_btn.configure(state="normal")
            self.stop_btn.configure(state="disabled")
            self.progress_bar.set(1.0 if not cancelled else 0)
        else:
            self.start_btn.configure(state="normal")
            self.stop_btn.configure(state="disabled")

        if cancelled:
            self.set_status(self.t("status_cancelled"), "#e74c3c")
            self.log("⏹️ Process stopped.")
        else:
            self.set_status(self.t("status_done"), "#2ecc71")
            self.log("✅ DONE! All codes have been submitted.")


def main():
    root = ctk.CTk() if HAS_CTK else tk.Tk()
    app = AutoRedeemerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
