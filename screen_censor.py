import os, sys, time, threading, tempfile, tkinter as tk
from tkinter import messagebox
import cv2, numpy as np, mss
from PIL import Image, ImageTk
from nudenet import NudeDetector

BREAST_LABEL = "FEMALE_BREAST_EXPOSED"
THRESHOLD = 0.45
INTERVAL = 1.0

class App:
    def __init__(self, root):
        self.root = root
        root.title("Screen Censor 3.0 - Safe Preview")
        root.geometry("1180x780")
        root.minsize(800, 560)
        root.configure(bg="#151923")
        self.running = False
        self.stop_event = threading.Event()
        self.lock = threading.Lock()
        self.frame = None
        self.boxes = []
        self.photo = None
        self.detector = None
        self.cascade = None

        tk.Label(root, text="SCREEN CENSOR 3.0", fg="white", bg="#151923",
                 font=("Segoe UI", 18, "bold")).pack(anchor="w", padx=16, pady=(12, 2))
        tk.Label(root, text="Safe Preview — tanpa overlay fullscreen desktop",
                 fg="#b9c2d0", bg="#151923").pack(anchor="w", padx=16)

        bar = tk.Frame(root, bg="#151923")
        bar.pack(fill="x", padx=16, pady=12)
        self.start_btn = tk.Button(bar, text="MULAI SENSOR", command=self.start,
                                   bg="#238b57", fg="white", width=16)
        self.start_btn.pack(side="left", padx=(0, 8))
        self.stop_btn = tk.Button(bar, text="MATIKAN", command=self.stop,
                                  bg="#a83e45", fg="white", width=12, state="disabled")
        self.stop_btn.pack(side="left")
        self.status = tk.Label(bar, text="Status: Mati", fg="#ff7777", bg="#151923")
        self.status.pack(side="left", padx=16)

        self.view = tk.Label(root, text="Klik MULAI SENSOR untuk memulai",
                             bg="#090c12", fg="#dbe4ee", font=("Segoe UI", 14))
        self.view.pack(fill="both", expand=True, padx=16, pady=8)
        tk.Label(root, text="Deteksi semua wajah + area FEMALE_BREAST_EXPOSED. Hasil bisa salah/terlewat.",
                 bg="#151923", fg="#9aa5b5").pack(anchor="w", padx=16, pady=(0, 6))
        tk.Label(root, text="STOP darurat: Ctrl + Shift + F12",
                 bg="#151923", fg="#ffd166").pack(anchor="w", padx=16, pady=(0, 12))
        root.bind_all("<Control-Shift-F12>", lambda e: self.stop())
        root.protocol("WM_DELETE_WINDOW", self.close)
        root.after(250, self.refresh)

    def start(self):
        if self.running: return
        self.stop_event.clear()
        self.start_btn.config(state="disabled")
        self.status.config(text="Status: Memuat model…", fg="#ffd166")
        threading.Thread(target=self.worker, daemon=True).start()

    def worker(self):
        try:
            path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
            self.cascade = cv2.CascadeClassifier(path)
            if self.cascade.empty():
                raise RuntimeError("Haar Cascade wajah tidak ditemukan.")
            self.detector = NudeDetector()
            if self.stop_event.is_set():
                self.root.after(0, self.stopped_ui)
                return
            self.running = True
            self.root.after(0, lambda: self.status.config(text="Status: AKTIF", fg="#65d69a"))
            with mss.mss() as sct:
                monitor = sct.monitors[1]
                while self.running and not self.stop_event.is_set():
                    raw = np.asarray(sct.grab(monitor))
                    frame = cv2.cvtColor(raw, cv2.COLOR_BGRA2BGR)
                    h, w = frame.shape[:2]
                    boxes = []
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    faces = self.cascade.detectMultiScale(gray, 1.1, 5, minSize=(35, 35))
                    for x, y, fw, fh in faces:
                        boxes.append((int(x), int(y), int(x+fw), int(y+fh)))
                    tmp = None
                    try:
                        fd, tmp = tempfile.mkstemp(suffix=".jpg")
                        os.close(fd)
                        if not cv2.imwrite(tmp, frame):
                            raise RuntimeError("Gagal membuat frame sementara.")
                        for item in self.detector.detect(tmp):
                            if str(item.get("class", "")).upper() == BREAST_LABEL and float(item.get("score", 0)) >= THRESHOLD:
                                x, y, bw, bh = item.get("box", [0, 0, 0, 0])
                                px, py = int(bw*.1), int(bh*.1)
                                boxes.append((max(0,int(x)-px), max(0,int(y)-py),
                                              min(w,int(x+bw)+px), min(h,int(y+bh)+py)))
                    finally:
                        if tmp and os.path.exists(tmp):
                            try: os.remove(tmp)
                            except OSError: pass
                    with self.lock:
                        self.frame, self.boxes = frame, boxes
                    time.sleep(INTERVAL)
        except Exception as exc:
            self.running = False
            self.root.after(0, lambda err=str(exc): self.failed(err))
        finally:
            self.root.after(0, self.stopped_ui)

    def refresh(self):
        if self.running:
            with self.lock:
                frame = None if self.frame is None else self.frame.copy()
                boxes = list(self.boxes)
            if frame is not None:
                # Hide this app's own window area in the preview to prevent feedback.
                try:
                    self.root.update_idletasks()
                    x, y = self.root.winfo_rootx(), self.root.winfo_rooty()
                    x1, y1 = max(0,x), max(0,y)
                    x2, y2 = min(frame.shape[1],x+self.root.winfo_width()), min(frame.shape[0],y+self.root.winfo_height())
                    if x2>x1 and y2>y1: frame[y1:y2, x1:x2] = (28,32,42)
                except Exception: pass
                for x1,y1,x2,y2 in boxes:
                    cv2.rectangle(frame,(x1,y1),(x2,y2),(0,0,0),-1)
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                from PIL import Image
                im = Image.fromarray(rgb)
                im.thumbnail((1100,650), Image.Resampling.LANCZOS)
                self.photo = ImageTk.PhotoImage(im)
                self.view.config(image=self.photo, text="")
        self.root.after(250, self.refresh)

    def failed(self, err):
        self.status.config(text="Gagal / sensor berhenti", fg="#ff7777")
        messagebox.showerror("Screen Censor 3.0", "Deteksi gagal:\n\n"+err)

    def stopped_ui(self):
        self.running = False
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.status.config(text="Status: Mati", fg="#ff7777")

    def stop(self):
        self.running = False
        self.stop_event.set()
        self.stopped_ui()

    def close(self):
        self.stop()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
