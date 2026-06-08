"""Steam Playtime Idler — keeps Steam thinking a game is running without launching it.

Usage:
    python idle.py                  # open GUI
    python idle.py 730              # idle one game by AppID
    python idle.py 730 440 570      # idle multiple games (spawns one subprocess each)

Requires steam_api64.dll in the same folder (from Steamworks SDK redistributable_bin/win64).
Steam client must be running and logged in.
"""
import ctypes
import os
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path
from tkinter import BOTH, DISABLED, END, LEFT, NORMAL, RIGHT, Y, Canvas, Frame, Label, Listbox, Scrollbar, StringVar, Tk
from tkinter import filedialog, messagebox, ttk

HERE = Path(__file__).resolve().parent
DLL_PATH = HERE / "steam_api64.dll"


def idle_single(app_id):
    dll_local = Path.cwd() / "steam_api64.dll"
    dll_to_use = dll_local if dll_local.exists() else DLL_PATH
    if not dll_to_use.exists():
        print("[!] Missing steam_api64.dll — see README.md for how to get it.")
        return 1

    # steam_appid.txt tells Steamworks which app this process represents.
    # Must be written in CWD before SteamAPI_Init.
    (Path.cwd() / "steam_appid.txt").write_text(str(app_id).strip())

    steam = ctypes.CDLL(str(dll_to_use))
    steam.SteamAPI_Init.restype = ctypes.c_bool
    steam.SteamAPI_RunCallbacks.restype = None
    steam.SteamAPI_Shutdown.restype = None

    if not steam.SteamAPI_Init():
        print(f"[!] SteamAPI_Init failed for AppID {app_id}. "
              "Is Steam running and do you own this game?")
        return 2

    print(f"[+] Idling AppID {app_id}. Press Ctrl+C to stop.")
    stop = {"flag": False}

    def handler(signum, frame):
        stop["flag"] = True

    signal.signal(signal.SIGINT, handler)
    try:
        signal.signal(signal.SIGTERM, handler)
    except (ValueError, AttributeError):
        pass

    try:
        while not stop["flag"]:
            steam.SteamAPI_RunCallbacks()
            time.sleep(2)
    finally:
        steam.SteamAPI_Shutdown()
        print(f"[+] Stopped AppID {app_id}.")
    return 0


def spawn_many(app_ids):
    procs = []
    work_root = HERE / ".sessions"
    work_root.mkdir(exist_ok=True)

    for app_id in app_ids:
        work = work_root / app_id
        work.mkdir(exist_ok=True)
        dll_link = work / "steam_api64.dll"
        if not dll_link.exists():
            try:
                os.link(DLL_PATH, dll_link)
            except OSError:
                shutil.copy2(DLL_PATH, dll_link)
        p = subprocess.Popen([sys.executable, str(HERE / "idle.py"), app_id], cwd=str(work))
        procs.append((app_id, p))
        print(f"[+] Spawned idler for AppID {app_id} (pid {p.pid})")

    print("[i] All idlers running. Press Ctrl+C to stop all.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[i] Shutting down...")
        for app_id, p in procs:
            p.terminate()
        for app_id, p in procs:
            try:
                p.wait(timeout=5)
            except subprocess.TimeoutExpired:
                p.kill()
        print("[+] All idlers stopped.")
    return 0


class SteamIdlerGui:
    def __init__(self):
        self.root = Tk()
        self.root.title("Steam Playtime Idler")
        self.root.geometry("760x520")
        self.root.minsize(680, 460)
        self.root.configure(bg="#101820")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.app_ids = StringVar()
        self.status = StringVar(value="พร้อมใช้งาน")
        self.processes = {}

        self.setup_style()
        self.build_ui()
        self.refresh_buttons()
        self.root.after(1000, self.watch_processes)

    def setup_style(self):
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except Exception:
            pass

        style.configure("Root.TFrame", background="#101820")
        style.configure("Panel.TFrame", background="#16222d")
        style.configure("Header.TLabel", background="#101820", foreground="#f5f7fb", font=("Segoe UI", 22, "bold"))
        style.configure("Sub.TLabel", background="#101820", foreground="#9fb1c1", font=("Segoe UI", 10))
        style.configure("PanelTitle.TLabel", background="#16222d", foreground="#f5f7fb", font=("Segoe UI", 12, "bold"))
        style.configure("Text.TLabel", background="#16222d", foreground="#b8c7d4", font=("Segoe UI", 10))
        style.configure("Status.TLabel", background="#101820", foreground="#80f2c4", font=("Segoe UI", 10, "bold"))
        style.configure("TEntry", fieldbackground="#0d141c", foreground="#f5f7fb", insertcolor="#f5f7fb", borderwidth=0)
        style.configure("Primary.TButton", background="#21c58e", foreground="#08120f", font=("Segoe UI", 10, "bold"), padding=(14, 9))
        style.map("Primary.TButton", background=[("active", "#38dca5"), ("disabled", "#426357")])
        style.configure("Danger.TButton", background="#ef6461", foreground="#fff7f7", font=("Segoe UI", 10, "bold"), padding=(14, 9))
        style.map("Danger.TButton", background=[("active", "#ff7b78"), ("disabled", "#694546")])
        style.configure("Ghost.TButton", background="#243443", foreground="#e8eef4", font=("Segoe UI", 10), padding=(12, 8))
        style.map("Ghost.TButton", background=[("active", "#304557"), ("disabled", "#1b2732")])

    def build_ui(self):
        root_frame = ttk.Frame(self.root, style="Root.TFrame", padding=24)
        root_frame.pack(fill=BOTH, expand=True)

        header = ttk.Frame(root_frame, style="Root.TFrame")
        header.pack(fill="x")
        ttk.Label(header, text="Steam Playtime Idler", style="Header.TLabel").pack(anchor="w")
        ttk.Label(
            header,
            text="ใส่ AppID แล้วกดเริ่ม โปรแกรมจะรัน idler แยกให้แต่ละเกม",
            style="Sub.TLabel",
        ).pack(anchor="w", pady=(4, 0))

        main = ttk.Frame(root_frame, style="Root.TFrame")
        main.pack(fill=BOTH, expand=True, pady=(22, 16))
        main.columnconfigure(0, weight=3)
        main.columnconfigure(1, weight=2)
        main.rowconfigure(0, weight=1)

        control = ttk.Frame(main, style="Panel.TFrame", padding=18)
        control.grid(row=0, column=0, sticky="nsew", padx=(0, 14))

        ttk.Label(control, text="เพิ่มเกม", style="PanelTitle.TLabel").pack(anchor="w")
        ttk.Label(control, text="ใส่เลข AppID คั่นด้วยช่องว่าง เช่น 730 440 570", style="Text.TLabel").pack(anchor="w", pady=(4, 10))

        entry_row = ttk.Frame(control, style="Panel.TFrame")
        entry_row.pack(fill="x")
        self.entry = ttk.Entry(entry_row, textvariable=self.app_ids, font=("Segoe UI", 13))
        self.entry.pack(side=LEFT, fill="x", expand=True, ipady=7)
        self.entry.bind("<Return>", lambda _event: self.start_idlers())
        ttk.Button(entry_row, text="เพิ่ม", style="Ghost.TButton", command=self.add_to_list).pack(side=RIGHT, padx=(10, 0))

        button_row = ttk.Frame(control, style="Panel.TFrame")
        button_row.pack(fill="x", pady=(16, 0))
        self.start_btn = ttk.Button(button_row, text="เริ่ม Idle", style="Primary.TButton", command=self.start_idlers)
        self.start_btn.pack(side=LEFT)
        self.stop_btn = ttk.Button(button_row, text="หยุดทั้งหมด", style="Danger.TButton", command=self.stop_all)
        self.stop_btn.pack(side=LEFT, padx=(10, 0))
        ttk.Button(button_row, text="เลือก DLL", style="Ghost.TButton", command=self.install_dll).pack(side=LEFT, padx=(10, 0))

        ttk.Label(control, text="รายการ AppID", style="PanelTitle.TLabel").pack(anchor="w", pady=(22, 8))
        list_wrap = Frame(control, bg="#0d141c", highlightbackground="#263747", highlightthickness=1)
        list_wrap.pack(fill=BOTH, expand=True)
        self.listbox = Listbox(
            list_wrap,
            bg="#0d141c",
            fg="#e8eef4",
            selectbackground="#21c58e",
            selectforeground="#08120f",
            relief="flat",
            borderwidth=0,
            highlightthickness=0,
            font=("Consolas", 12),
            activestyle="none",
        )
        scrollbar = Scrollbar(list_wrap, orient="vertical", command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=scrollbar.set)
        self.listbox.pack(side=LEFT, fill=BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=RIGHT, fill=Y)

        list_actions = ttk.Frame(control, style="Panel.TFrame")
        list_actions.pack(fill="x", pady=(10, 0))
        ttk.Button(list_actions, text="ลบที่เลือก", style="Ghost.TButton", command=self.remove_selected).pack(side=LEFT)
        ttk.Button(list_actions, text="ล้างรายการ", style="Ghost.TButton", command=self.clear_list).pack(side=LEFT, padx=(8, 0))

        info = ttk.Frame(main, style="Panel.TFrame", padding=18)
        info.grid(row=0, column=1, sticky="nsew")
        ttk.Label(info, text="สถานะ", style="PanelTitle.TLabel").pack(anchor="w")
        self.status_canvas = Canvas(info, width=150, height=150, bg="#16222d", highlightthickness=0)
        self.status_canvas.pack(pady=(16, 10))
        self.draw_badge("#21c58e", "READY")
        self.running_label = ttk.Label(info, text="กำลังรัน 0 เกม", style="PanelTitle.TLabel")
        self.running_label.pack(anchor="center", pady=(0, 18))

        tips = [
            "ต้องเปิด Steam และ login ไว้ก่อน",
            "ต้องมี steam_api64.dll ในโฟลเดอร์เดียวกัน",
            "กดเลือก DLL เพื่อคัดลอกไฟล์เข้ามาอัตโนมัติ",
            "ถ้า Init fail ให้เช็กว่าเป็นเจ้าของเกมนั้นหรือไม่",
            "ปิดหน้าต่างนี้เพื่อหยุด idler ทั้งหมด",
        ]
        for tip in tips:
            ttk.Label(info, text=f"- {tip}", style="Text.TLabel", wraplength=230).pack(anchor="w", pady=3)

        footer = ttk.Frame(root_frame, style="Root.TFrame")
        footer.pack(fill="x")
        ttk.Label(footer, textvariable=self.status, style="Status.TLabel").pack(side=LEFT)

    def draw_badge(self, color, text):
        canvas = self.status_canvas
        canvas.delete("all")
        canvas.create_oval(14, 14, 136, 136, fill="#0d141c", outline="#263747", width=2)
        canvas.create_oval(42, 42, 108, 108, fill=color, outline="")
        canvas.create_text(75, 126, text=text, fill="#f5f7fb", font=("Segoe UI", 10, "bold"))

    def parse_entry(self):
        raw = self.app_ids.get().replace(",", " ").split()
        return [item.strip() for item in raw if item.strip().isdigit()]

    def list_values(self):
        return list(self.listbox.get(0, END))

    def add_to_list(self):
        added = 0
        existing = set(self.list_values())
        for app_id in self.parse_entry():
            if app_id not in existing:
                self.listbox.insert(END, app_id)
                existing.add(app_id)
                added += 1
        self.app_ids.set("")
        self.status.set(f"เพิ่ม AppID แล้ว {added} รายการ" if added else "ยังไม่มี AppID ใหม่ให้เพิ่ม")

    def remove_selected(self):
        for index in reversed(self.listbox.curselection()):
            app_id = self.listbox.get(index)
            if app_id in self.processes:
                self.stop_process(app_id)
            self.listbox.delete(index)
        self.refresh_buttons()

    def clear_list(self):
        for app_id in self.list_values():
            if app_id in self.processes:
                self.stop_process(app_id)
        self.listbox.delete(0, END)
        self.status.set("ล้างรายการแล้ว")
        self.refresh_buttons()

    def start_idlers(self):
        self.add_to_list()
        app_ids = self.list_values()
        if not app_ids:
            messagebox.showwarning("ยังไม่มี AppID", "กรุณาใส่ AppID อย่างน้อย 1 เกม")
            return
        if not DLL_PATH.exists():
            if messagebox.askyesno("ไม่พบ DLL", "ไม่พบ steam_api64.dll ในโฟลเดอร์โปรแกรม\nต้องการเลือกไฟล์ DLL ตอนนี้ไหม?"):
                self.install_dll()
            return
            return

        started = 0
        work_root = HERE / ".sessions"
        work_root.mkdir(exist_ok=True)

        for app_id in app_ids:
            if app_id in self.processes and self.processes[app_id].poll() is None:
                continue

            work = work_root / app_id
            work.mkdir(exist_ok=True)
            dll_link = work / "steam_api64.dll"
            if not dll_link.exists():
                try:
                    os.link(DLL_PATH, dll_link)
                except OSError:
                    shutil.copy2(DLL_PATH, dll_link)

            proc = subprocess.Popen(
                [sys.executable, str(HERE / "idle.py"), "--worker", app_id],
                cwd=str(work),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
            )
            self.processes[app_id] = proc
            started += 1

        self.status.set(f"เริ่ม idle แล้ว {started} เกม" if started else "ทุกเกมในรายการกำลังรันอยู่แล้ว")
        self.refresh_buttons()

    def install_dll(self):
        file_path = filedialog.askopenfilename(
            title="เลือก steam_api64.dll",
            filetypes=[("Steam API DLL", "steam_api64.dll"), ("DLL files", "*.dll"), ("All files", "*.*")],
        )
        if not file_path:
            self.status.set("ยังไม่ได้เลือกไฟล์ DLL")
            return

        source = Path(file_path)
        if source.name.lower() != "steam_api64.dll":
            messagebox.showerror("ไฟล์ไม่ถูกต้อง", "กรุณาเลือกไฟล์ชื่อ steam_api64.dll")
            return

        try:
            if source.resolve() != DLL_PATH.resolve():
                shutil.copy2(source, DLL_PATH)
        except OSError as exc:
            messagebox.showerror("คัดลอก DLL ไม่สำเร็จ", str(exc))
            return

        self.status.set(f"ติดตั้ง DLL แล้ว: {DLL_PATH}")
        messagebox.showinfo("สำเร็จ", "คัดลอก steam_api64.dll เข้าโฟลเดอร์โปรแกรมแล้ว")

    def stop_process(self, app_id):
        proc = self.processes.pop(app_id, None)
        if proc and proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                proc.kill()

    def stop_all(self):
        for app_id in list(self.processes):
            self.stop_process(app_id)
        self.status.set("หยุด idler ทั้งหมดแล้ว")
        self.refresh_buttons()

    def watch_processes(self):
        stopped = [app_id for app_id, proc in self.processes.items() if proc.poll() is not None]
        for app_id in stopped:
            self.processes.pop(app_id, None)
        if stopped:
            self.status.set(f"บางเกมหยุดทำงาน: {', '.join(stopped)}")
        self.refresh_buttons()
        self.root.after(1000, self.watch_processes)

    def refresh_buttons(self):
        running = sum(1 for proc in self.processes.values() if proc.poll() is None)
        self.running_label.configure(text=f"กำลังรัน {running} เกม")
        if running:
            self.draw_badge("#21c58e", "RUNNING")
            self.stop_btn.configure(state=NORMAL)
        else:
            self.draw_badge("#21c58e", "READY")
            self.stop_btn.configure(state=DISABLED)
        self.start_btn.configure(state=NORMAL)

    def on_close(self):
        if self.processes and not messagebox.askyesno("หยุดทั้งหมด?", "ต้องการหยุด idler ทั้งหมดและปิดโปรแกรมไหม"):
            return
        self.stop_all()
        self.root.destroy()

    def run(self):
        self.entry.focus_set()
        self.root.mainloop()


def main():
    if len(sys.argv) < 2:
        SteamIdlerGui().run()
        return 0
    if sys.argv[1] == "--worker":
        if len(sys.argv) != 3 or not sys.argv[2].isdigit():
            return 1
        return idle_single(sys.argv[2])
    app_ids = [a for a in sys.argv[1:] if a.isdigit()]
    if not app_ids:
        print("[!] Provide one or more numeric AppIDs.")
        return 1
    if len(app_ids) == 1:
        return idle_single(app_ids[0])
    return spawn_many(app_ids)


if __name__ == "__main__":
    sys.exit(main())
