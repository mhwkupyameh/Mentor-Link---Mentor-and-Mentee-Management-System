import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json, os, uuid, random, math, csv, re
from datetime import datetime, date, timedelta

DATA_FILE = "mentor_mentee_data.json"

# ── Palette ──────────────────────────────────────────────────────────────────
BG      = "#0D1117"
SURFACE = "#161B27"
CARD    = "#1E2435"
CARD2   = "#252C40"
ACCENT  = "#7C6FFF"
TEAL    = "#0BBFAA"
PINK    = "#FF6B9D"
ORANGE  = "#FF9F43"
SUCCESS = "#26D980"
DANGER  = "#FF5A5A"
TEXT    = "#EEF0F8"
MUTED   = "#8891AA"
DIM     = "#4A5270"
BORDER  = "#2A3050"
INPUT_BG= "#1A2035"
WHITE   = "#FFFFFF"

# ── Fonts ─────────────────────────────────────────────────────────────────────
def ff(size, weight="normal", family="Segoe UI"):
    return (family, size, weight)

# ── Data ──────────────────────────────────────────────────────────────────────
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE) as f:
                return json.load(f)
        except:
            pass
    return {"mentors":[], "mentees":[], "sessions":[], "goals":[], "pairs":[]}

def save_data(d):
    with open(DATA_FILE, "w") as f:
        json.dump(d, f, indent=2, default=str)

def uid(): return str(uuid.uuid4())[:8]

# ── Avatar ────────────────────────────────────────────────────────────────────
AV = [("#4F3AE8","#A594FF"),("#0A7060","#40EDD4"),("#8B2252","#F090C0"),
      ("#1A5F8A","#60C0F8"),("#5A6E10","#B0E040"),("#7A3010","#F0904A")]

def av_col(name):
    return AV[sum(ord(c) for c in name) % len(AV)]

def initials(name):
    p = name.strip().split()
    return (p[0][0] + (p[-1][0] if len(p)>1 else "")).upper()

def draw_av(cv, x, y, r, name, fs=12):
    bg, fg = av_col(name)
    cv.create_oval(x-r, y-r, x+r, y+r, fill=bg, outline="")
    cv.create_text(x, y, text=initials(name), fill=fg,
                   font=("Segoe UI", fs, "bold"))

# ── Helpers ───────────────────────────────────────────────────────────────────
def lighter(c, amt=30):
    c = c.lstrip("#")
    r,g,b = int(c[0:2],16), int(c[2:4],16), int(c[4:6],16)
    return "#{:02x}{:02x}{:02x}".format(min(255,r+amt),min(255,g+amt),min(255,b+amt))

def darker(c, amt=20):
    c = c.lstrip("#")
    r,g,b = int(c[0:2],16), int(c[2:4],16), int(c[4:6],16)
    return "#{:02x}{:02x}{:02x}".format(max(0,r-amt),max(0,g-amt),max(0,b-amt))

# ── Base widget factories ─────────────────────────────────────────────────────
def hline(p, col=BORDER, h=1):
    f = tk.Frame(p, bg=col, height=h)
    f.pack_propagate(False)
    return f

def vline(p, col=BORDER, w=1):
    return tk.Frame(p, bg=col, width=w)

def Lbl(p, text, size=11, weight="normal", fg=TEXT, bg=BG, **kw):
    return tk.Label(p, text=text, font=ff(size,weight), fg=fg, bg=bg, **kw)

def Card(p, bg=CARD, border=BORDER, **kw):
    return tk.Frame(p, bg=bg, highlightthickness=1,
                    highlightbackground=border, **kw)

def Btn(p, text, cmd, bg=ACCENT, fg=WHITE, w=16, py=9, size=11):
    b = tk.Button(p, text=text, command=cmd, font=ff(size,"bold"),
                  fg=fg, bg=bg, activeforeground=WHITE,
                  activebackground=lighter(bg), relief="flat",
                  cursor="hand2", width=w, pady=py, bd=0)
    b.bind("<Enter>", lambda e: b.config(bg=lighter(bg,25)))
    b.bind("<Leave>", lambda e: b.config(bg=bg))
    return b

def GhostBtn(p, text, cmd, w=10, py=6, fg=MUTED, bg=CARD):
    b = tk.Button(p, text=text, command=cmd, font=ff(10),
                  fg=fg, bg=bg, activeforeground=TEXT,
                  activebackground=CARD2, relief="flat",
                  cursor="hand2", width=w, pady=py, bd=0,
                  highlightthickness=1, highlightbackground=BORDER)
    b.bind("<Enter>", lambda e: b.config(fg=TEXT, bg=CARD2, highlightbackground=DIM))
    b.bind("<Leave>", lambda e: b.config(fg=fg,   bg=bg,   highlightbackground=BORDER))
    return b

def Scroll(p, bg=BG):
    """Returns (inner_frame, canvas)"""
    wrap   = tk.Frame(p, bg=bg)
    wrap.pack(fill="both", expand=True)
    canvas = tk.Canvas(wrap, bg=bg, highlightthickness=0, bd=0)
    sb     = tk.Scrollbar(wrap, orient="vertical", command=canvas.yview,
                          bg=SURFACE, troughcolor=SURFACE, width=8)
    inner  = tk.Frame(canvas, bg=bg)
    inner.bind("<Configure>",
               lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    win = canvas.create_window((0,0), window=inner, anchor="nw")
    canvas.configure(yscrollcommand=sb.set)

    def _resize(e): canvas.itemconfig(win, width=e.width)
    canvas.bind("<Configure>", _resize)

    def _scroll(e):
        import sys
        delta = e.delta if sys.platform != "linux" else (-1 if e.num == 5 else 1) * 120
        canvas.yview_scroll(int(-1 * (delta / 120)), "units")
    canvas.bind("<MouseWheel>", _scroll)
    canvas.bind("<Button-4>",   _scroll)
    canvas.bind("<Button-5>",   _scroll)
    inner.bind("<MouseWheel>",  _scroll)
    inner.bind("<Button-4>",    _scroll)
    inner.bind("<Button-5>",    _scroll)

    canvas.pack(side="left", fill="both", expand=True)
    sb.pack(side="right", fill="y")
    return inner, canvas

def PageHeader(page, title, subtitle, btn_lbl=None, btn_cmd=None):
    hdr = tk.Frame(page, bg=BG)
    hdr.pack(fill="x", padx=36, pady=(30,0))
    tk.Label(hdr, text=title, font=("Georgia",21,"bold"),
             fg=TEXT, bg=BG).pack(side="left", anchor="s")
    if btn_lbl and btn_cmd:
        Btn(hdr, btn_lbl, btn_cmd, w=22, py=8).pack(side="right", anchor="s")
    tk.Label(page, text=subtitle, font=ff(10), fg=MUTED, bg=BG).pack(
        fill="x", padx=36, pady=(4,12))
    hline(page, BORDER).pack(fill="x", padx=36, pady=(0,16))

def EmptyState(p, title, sub, btn_lbl, btn_cmd):
    f = tk.Frame(p, bg=BG)
    f.pack(expand=True, fill="both")
    tk.Label(f, text="◈", font=("Georgia",52), fg=DIM, bg=BG).pack(pady=(90,6))
    tk.Label(f, text=title, font=("Georgia",17,"bold"), fg=TEXT,  bg=BG).pack()
    tk.Label(f, text=sub,   font=ff(10),                fg=MUTED, bg=BG).pack(pady=(3,20))
    Btn(f, btn_lbl, btn_cmd, w=26, py=11).pack()

# ══════════════════════════════════════════════════════════════════════════════
#  DATE PICKER  — popup calendar widget
# ══════════════════════════════════════════════════════════════════════════════
class DatePicker(tk.Toplevel):
    """Popup calendar that writes YYYY-MM-DD into a StringVar."""
    def __init__(self, parent, var):
        super().__init__(parent)
        self.var = var
        self.configure(bg=SURFACE)
        self.overrideredirect(True)          # borderless
        self.grab_set()
        self.bind("<Escape>", lambda e: self.destroy())

        # Determine initial month/year from var or today
        try:
            initial = datetime.strptime(var.get(), "%Y-%m-%d")
            self._year  = initial.year
            self._month = initial.month
        except Exception:
            today = date.today()
            self._year  = today.year
            self._month = today.month

        self._build()
        self._position(parent)
        self.wait_window()

    def _position(self, parent):
        self.update_idletasks()
        x = parent.winfo_rootx()
        y = parent.winfo_rooty() + parent.winfo_height() + 4
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        w, h   = self.winfo_width(), self.winfo_height()
        x = min(x, sw - w - 8)
        y = min(y, sh - h - 8)
        self.geometry(f"+{x}+{y}")

    def _build(self):
        for w in self.winfo_children(): w.destroy()

        # ── Header: prev / month-year / next ──
        hdr = tk.Frame(self, bg=CARD2)
        hdr.pack(fill="x")
        tk.Button(hdr, text="‹", font=ff(13,"bold"), fg=TEXT, bg=CARD2,
                  relief="flat", cursor="hand2", bd=0, padx=10,
                  command=self._prev_month).pack(side="left")
        tk.Button(hdr, text="›", font=ff(13,"bold"), fg=TEXT, bg=CARD2,
                  relief="flat", cursor="hand2", bd=0, padx=10,
                  command=self._next_month).pack(side="right")
        month_name = datetime(self._year, self._month, 1).strftime("%B %Y")
        tk.Label(hdr, text=month_name, font=ff(11,"bold"),
                 fg=TEXT, bg=CARD2).pack(expand=True, pady=8)

        # ── Day-of-week headers ──
        dow = tk.Frame(self, bg=SURFACE)
        dow.pack(fill="x", padx=6)
        for d in ["Mo","Tu","We","Th","Fr","Sa","Su"]:
            tk.Label(dow, text=d, font=ff(8,"bold"), fg=DIM,
                     bg=SURFACE, width=4).pack(side="left")

        hline(self, BORDER).pack(fill="x", padx=6)

        # ── Day grid ──
        grid = tk.Frame(self, bg=SURFACE)
        grid.pack(padx=6, pady=(4,8))

        import calendar
        first_wd, num_days = calendar.monthrange(self._year, self._month)
        # Fill blanks before 1st
        col = first_wd   # Mon=0
        row = 0

        try:
            sel = datetime.strptime(self.var.get(), "%Y-%m-%d").date()
        except Exception:
            sel = None

        today = date.today()

        for day in range(1, num_days + 1):
            d_obj = date(self._year, self._month, day)
            is_sel   = (d_obj == sel)
            is_today = (d_obj == today)

            fg_col = WHITE  if is_sel else (ACCENT if is_today else TEXT)
            bg_col = ACCENT if is_sel else CARD2  if is_today else SURFACE
            hl_col = ACCENT if is_sel else TEAL   if is_today else SURFACE

            btn = tk.Button(grid, text=str(day), font=ff(9),
                            fg=fg_col, bg=bg_col,
                            activeforeground=WHITE, activebackground=ACCENT,
                            relief="flat", cursor="hand2", bd=0,
                            width=3, pady=5,
                            command=lambda d=d_obj: self._pick(d))
            if is_sel or is_today:
                btn.config(highlightthickness=1, highlightbackground=hl_col)
            btn.grid(row=row, column=col, padx=1, pady=1)
            col += 1
            if col == 7:
                col = 0
                row += 1

        # ── Today shortcut ──
        hline(self, BORDER).pack(fill="x", padx=6)
        tk.Button(self, text="Today", font=ff(9), fg=TEAL, bg=SURFACE,
                  relief="flat", cursor="hand2", bd=0, pady=6,
                  command=lambda: self._pick(date.today())).pack()

    def _prev_month(self):
        self._month -= 1
        if self._month < 1: self._month = 12; self._year -= 1
        self._build()

    def _next_month(self):
        self._month += 1
        if self._month > 12: self._month = 1; self._year += 1
        self._build()

    def _pick(self, d):
        self.var.set(d.strftime("%Y-%m-%d"))
        self.destroy()


# ══════════════════════════════════════════════════════════════════════════════
#  TOAST NOTIFICATION  — non-blocking bottom-right popup
# ══════════════════════════════════════════════════════════════════════════════
class Toast:
    """Show a brief auto-dismissing notification in the bottom-right corner."""
    def __init__(self, root, message, color=SUCCESS, duration=3000):
        self._root = root
        w = tk.Toplevel(root)
        w.overrideredirect(True)
        w.configure(bg=color)
        w.attributes("-topmost", True)
        w.attributes("-alpha", 0.0)

        tk.Frame(w, bg=color, height=3).pack(fill="x")
        inner = tk.Frame(w, bg=darker(color, 30), padx=18, pady=12)
        inner.pack(fill="both")
        tk.Label(inner, text=message, font=ff(10,"bold"),
                 fg=WHITE, bg=darker(color, 30),
                 wraplength=280, justify="left").pack()

        w.update_idletasks()
        sw = root.winfo_screenwidth()
        sh = root.winfo_screenheight()
        ww = w.winfo_width()
        wh = w.winfo_height()
        w.geometry(f"+{sw - ww - 24}+{sh - wh - 60}")

        self._w = w
        self._fade_in(0)
        root.after(duration, lambda: self._fade_out(100))

    def _fade_in(self, step):
        alpha = step / 100
        try:
            self._w.attributes("-alpha", alpha)
            if step < 100:
                self._root.after(12, lambda: self._fade_in(step + 8))
        except Exception:
            pass

    def _fade_out(self, step):
        alpha = step / 100
        try:
            self._w.attributes("-alpha", alpha)
            if step > 0:
                self._root.after(18, lambda: self._fade_out(step - 8))
            else:
                self._w.destroy()
        except Exception:
            pass


# ══════════════════════════════════════════════════════════════════════════════
#  SEARCH BAR  — returns the Frame; caller packs it
# ══════════════════════════════════════════════════════════════════════════════
def SearchBar(parent, var, placeholder="Search…", bg=BG):
    wrap = tk.Frame(parent, bg=bg)
    border = tk.Frame(wrap, bg=BORDER, padx=1, pady=1)
    border.pack(fill="x")
    inner = tk.Frame(border, bg=INPUT_BG)
    inner.pack(fill="x")
    tk.Label(inner, text="⌕", font=ff(13), fg=MUTED, bg=INPUT_BG).pack(side="left", padx=(10,0))

    ent = tk.Entry(inner, textvariable=var, font=ff(11),
                   fg=MUTED, bg=INPUT_BG, insertbackground=TEXT,
                   relief="flat", bd=0)
    ent.insert(0, placeholder)
    ent.pack(side="left", fill="x", expand=True, padx=8, pady=9)

    def _fi(e):
        if ent.get() == placeholder:
            ent.delete(0, "end")
            ent.config(fg=TEXT)
        border.config(bg=ACCENT)

    def _fo(e):
        if not ent.get():
            ent.insert(0, placeholder)
            ent.config(fg=MUTED)
        border.config(bg=BORDER)

    ent.bind("<FocusIn>",  _fi)
    ent.bind("<FocusOut>", _fo)

    def _clear():
        ent.delete(0, "end")
        ent.insert(0, placeholder)
        ent.config(fg=MUTED)
        var.set("")

    clr = tk.Button(inner, text="✕", font=ff(9), fg=DIM, bg=INPUT_BG,
                    relief="flat", cursor="hand2", bd=0, padx=6,
                    command=_clear)
    clr.pack(side="right", padx=(0,4))
    clr.bind("<Enter>", lambda e: clr.config(fg=DANGER))
    clr.bind("<Leave>", lambda e: clr.config(fg=DIM))

    return wrap


# ══════════════════════════════════════════════════════════════════════════════
#  CSV EXPORT  helper
# ══════════════════════════════════════════════════════════════════════════════
def export_csv(root, rows, default_name="export.csv"):
    if not rows:
        messagebox.showinfo("Export", "Nothing to export.", parent=root)
        return
    path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV files","*.csv"),("All files","*.*")],
        initialfile=default_name,
        parent=root,
        title="Save CSV")
    if not path: return
    keys = list(rows[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    Toast(root, f"✓  Exported {len(rows)} rows\n{os.path.basename(path)}", SUCCESS)


# ══════════════════════════════════════════════════════════════════════════════
#  DIALOG  — working inputs, scrollable, gorgeous design
# ══════════════════════════════════════════════════════════════════════════════
class Dialog(tk.Toplevel):
    def __init__(self, parent, title, subtitle, fields, prefill=None):
        super().__init__(parent)
        self.result   = None
        self._fields  = fields
        self._pre     = prefill or {}
        self._vars    = {}
        self._widgets = {}

        self.title(title)
        self.configure(bg=SURFACE)
        self.grab_set()
        self.resizable(True, True)
        self.bind("<Escape>", lambda e: self.destroy())

        W = 640
        H = min(780, 200 + len(fields) * 90)
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self.geometry(f"{W}x{H}+{(sw-W)//2}+{(sh-H)//2}")
        self.minsize(600, 460)

        self._build(title, subtitle)
        self.after(150, self._focus_first)
        self.wait_window()

    def _focus_first(self):
        for w in self._widgets.values():
            if isinstance(w, tk.Entry):
                w.focus_set()
                return

    def _build(self, title, subtitle):
        # Top accent stripe
        tk.Frame(self, bg=ACCENT, height=5).pack(fill="x")

        # Header
        hdr = tk.Frame(self, bg=SURFACE)
        hdr.pack(fill="x", padx=30, pady=(20, 0))
        tk.Label(hdr, text=title,
                 font=("Georgia", 17, "bold"), fg=TEXT, bg=SURFACE).pack(anchor="w")
        tk.Label(hdr, text=subtitle,
                 font=ff(9), fg=MUTED, bg=SURFACE).pack(anchor="w", pady=(4, 0))

        # Divider
        tk.Frame(self, bg=BORDER, height=1).pack(fill="x", padx=30, pady=(14, 0))

        # Footer — packed SECOND-TO-LAST so it stays at bottom
        tk.Frame(self, bg=BORDER, height=1).pack(fill="x", side="bottom")
        foot = tk.Frame(self, bg=SURFACE)
        foot.pack(fill="x", side="bottom", padx=30, pady=16)

        # Save button
        bs = tk.Button(foot, text="  ✓  Save  ", command=self._save,
                       font=ff(12, "bold"), fg=WHITE, bg=ACCENT,
                       activeforeground=WHITE, activebackground=lighter(ACCENT, 25),
                       relief="flat", cursor="hand2", pady=11, padx=24, bd=0)
        bs.bind("<Enter>", lambda e: bs.config(bg=lighter(ACCENT, 25)))
        bs.bind("<Leave>", lambda e: bs.config(bg=ACCENT))
        bs.pack(side="right")

        # Cancel button
        bc = tk.Button(foot, text="Cancel", command=self.destroy,
                       font=ff(11), fg=MUTED, bg=SURFACE,
                       activeforeground=TEXT, activebackground=CARD,
                       relief="flat", cursor="hand2", width=10, pady=11, bd=0,
                       highlightthickness=1, highlightbackground=BORDER)
        bc.bind("<Enter>", lambda e: bc.config(fg=TEXT, bg=CARD,
                                               highlightbackground=DIM))
        bc.bind("<Leave>", lambda e: bc.config(fg=MUTED, bg=SURFACE,
                                               highlightbackground=BORDER))
        bc.pack(side="right", padx=(0, 12))

        self.bind("<Return>", lambda e: self._save())

        # ── Scrollable area: Canvas + Scrollbar ──────────────────────────────
        # The canvas holds ONE window (inner_frame).
        # We bind <Configure> on the canvas to keep inner_frame width in sync.
        # We call update_idletasks() before creating the window so the canvas
        # already has its real width.

        scroll_area = tk.Frame(self, bg=SURFACE)
        scroll_area.pack(fill="both", expand=True)

        self._canvas = tk.Canvas(scroll_area, bg=SURFACE,
                                 highlightthickness=0, bd=0)
        vsb = tk.Scrollbar(scroll_area, orient="vertical",
                           command=self._canvas.yview,
                           width=10, troughcolor=CARD, bg=BORDER)
        self._canvas.configure(yscrollcommand=vsb.set)

        vsb.pack(side="right", fill="y")
        self._canvas.pack(side="left", fill="both", expand=True)

        # Force canvas to render at full size before we create the window
        self._canvas.update_idletasks()

        # Inner frame — all fields go here
        self._inner = tk.Frame(self._canvas, bg=SURFACE)
        self._win_id = self._canvas.create_window(
            (0, 0), window=self._inner, anchor="nw",
            width=self._canvas.winfo_width()
        )

        # Keep inner width synced to canvas width
        def _sync_width(e):
            self._canvas.itemconfig(self._win_id, width=e.width)
        self._canvas.bind("<Configure>", _sync_width)

        # Update scrollregion when inner frame grows
        def _update_scroll(e):
            self._canvas.configure(scrollregion=self._canvas.bbox("all"))
        self._inner.bind("<Configure>", _update_scroll)

        # Mousewheel
        def _wheel(e):
            import sys
            delta = e.delta if sys.platform != "linux" else (-1 if e.num == 5 else 1) * 120
            self._canvas.yview_scroll(int(-1 * (delta / 120)), "units")
        self._canvas.bind_all("<MouseWheel>", _wheel)
        self._canvas.bind_all("<Button-4>",   _wheel)
        self._canvas.bind_all("<Button-5>",   _wheel)
        self.bind("<Destroy>", lambda e: (
            self._canvas.unbind_all("<MouseWheel>"),
            self._canvas.unbind_all("<Button-4>"),
            self._canvas.unbind_all("<Button-5>"),
        ))

        # Build fields
        for fd in self._fields:
            self._make_field(self._inner, fd)

        tk.Frame(self._inner, bg=SURFACE, height=24).pack()

    def _make_field(self, parent, fd):
        key   = fd["key"]
        ftype = fd.get("type", "entry")
        pre   = self._pre.get(key, "")

        # Row wrapper
        wrap = tk.Frame(parent, bg=SURFACE)
        wrap.pack(fill="x", padx=30, pady=(16, 0))

        # Label row
        lrow = tk.Frame(wrap, bg=SURFACE)
        lrow.pack(fill="x", pady=(0, 6))
        tk.Label(lrow, text=fd["label"],
                 font=ff(11, "bold"), fg=TEXT, bg=SURFACE).pack(side="left")
        if fd.get("required"):
            tk.Label(lrow, text=" *required",
                     font=ff(9), fg=DANGER, bg=SURFACE).pack(side="left", padx=(4, 0))

        # Inline error label (hidden until triggered)
        err_lbl = tk.Label(wrap, text="", font=ff(9), fg=DANGER, bg=SURFACE, anchor="w")
        # will be packed after the input; stored so validators can update it
        self._err_labels = getattr(self, "_err_labels", {})
        self._err_labels[key] = err_lbl

        # ── COMBO / DROPDOWN ──
        if ftype == "combo":
            vals = fd.get("values") or [""]
            var  = tk.StringVar(value=pre if pre else vals[0])
            self._vars[key] = var

            border_f = tk.Frame(wrap, bg=BORDER, padx=1, pady=1)
            border_f.pack(fill="x")
            inner_f  = tk.Frame(border_f, bg=INPUT_BG)
            inner_f.pack(fill="x")

            cb = ttk.Combobox(inner_f, textvariable=var, values=vals,
                              font=ff(12), state="readonly")
            cb.pack(fill="x", padx=8, pady=8)

            cb.bind("<<ComboboxSelected>>",
                    lambda e, b=border_f: b.config(bg=ACCENT))
            cb.bind("<FocusIn>",
                    lambda e, b=border_f: b.config(bg=ACCENT))
            cb.bind("<FocusOut>",
                    lambda e, b=border_f: b.config(bg=BORDER))
            self._widgets[key] = cb

        # ── DATE PICKER ──
        elif ftype == "datepicker":
            var = tk.StringVar(value=pre)
            self._vars[key] = var

            border_f = tk.Frame(wrap, bg=BORDER, padx=1, pady=1)
            border_f.pack(fill="x")
            inner_f  = tk.Frame(border_f, bg=INPUT_BG)
            inner_f.pack(fill="x")

            row_f = tk.Frame(inner_f, bg=INPUT_BG)
            row_f.pack(fill="x")

            ent = tk.Entry(row_f, textvariable=var, font=ff(13),
                           fg=TEXT, bg=INPUT_BG, insertbackground=WHITE,
                           relief="flat", bd=0, cursor="xterm")
            ent.pack(side="left", fill="x", expand=True, padx=14, pady=12)

            cal_btn = tk.Button(row_f, text="📅", font=ff(12),
                                fg=MUTED, bg=INPUT_BG,
                                activeforeground=ACCENT, activebackground=INPUT_BG,
                                relief="flat", cursor="hand2", bd=0, padx=8,
                                command=lambda v=var, b=border_f: (
                                    b.config(bg=ACCENT),
                                    DatePicker(self, v)
                                ))
            cal_btn.pack(side="right", padx=(0,8))
            cal_btn.bind("<Enter>", lambda e, b=cal_btn: b.config(fg=ACCENT))
            cal_btn.bind("<Leave>", lambda e, b=cal_btn: b.config(fg=MUTED))

            def _date_focus_in(e, b=border_f):  b.config(bg=ACCENT)
            def _date_focus_out(e, b=border_f): b.config(bg=BORDER)
            ent.bind("<FocusIn>",  _date_focus_in)
            ent.bind("<FocusOut>", _date_focus_out)

            # Real-time date format validation
            def _validate_date_rt(e, v=var, el=err_lbl, b=border_f):
                val = v.get().strip()
                if not val:
                    el.config(text=""); el.pack_forget(); b.config(bg=BORDER); return
                try:
                    datetime.strptime(val, "%Y-%m-%d")
                    el.config(text=""); el.pack_forget(); b.config(bg=SUCCESS)
                except ValueError:
                    el.config(text="⚠  Use format YYYY-MM-DD  e.g. 2026-08-15")
                    el.pack(fill="x", pady=(3,0))
                    b.config(bg=DANGER)
            ent.bind("<KeyRelease>", _validate_date_rt)
            var.trace_add("write", lambda *a, v=var, el=err_lbl, b=border_f: _validate_date_rt(None, v, el, b))

            self._widgets[key] = ent

        # ── MULTILINE TEXT ──
        elif ftype == "text":
            border_f = tk.Frame(wrap, bg=BORDER, padx=1, pady=1)
            border_f.pack(fill="x")
            inner_f  = tk.Frame(border_f, bg=INPUT_BG)
            inner_f.pack(fill="x")

            txt = tk.Text(inner_f, font=ff(12), fg=TEXT, bg=INPUT_BG,
                          insertbackground=TEXT, relief="flat",
                          height=fd.get("height", 3),
                          wrap="word", bd=8, cursor="xterm",
                          padx=4, pady=4)
            txt.pack(fill="x")

            ph = fd.get("placeholder", "")
            if pre:
                txt.insert("1.0", pre)
            elif ph:
                txt.insert("1.0", ph)
                txt.config(fg=MUTED)

            def _tfi(e, t=txt, ph=ph, b=border_f):
                if ph and t.get("1.0", "end-1c") == ph:
                    t.delete("1.0", "end")
                    t.config(fg=TEXT)
                b.config(bg=ACCENT)

            def _tfo(e, t=txt, ph=ph, b=border_f):
                if not t.get("1.0", "end-1c").strip() and ph:
                    t.insert("1.0", ph)
                    t.config(fg=MUTED)
                b.config(bg=BORDER)

            txt.bind("<FocusIn>",  _tfi)
            txt.bind("<FocusOut>", _tfo)
            self._vars[key]    = txt
            self._widgets[key] = txt

        # ── TEXT ENTRY ──
        else:
            border_f = tk.Frame(wrap, bg=BORDER, padx=1, pady=1)
            border_f.pack(fill="x")
            inner_f  = tk.Frame(border_f, bg=INPUT_BG)
            inner_f.pack(fill="x")

            var = tk.StringVar(value=pre)
            self._vars[key] = var

            ent = tk.Entry(inner_f, textvariable=var,
                           font=ff(13), fg=TEXT, bg=INPUT_BG,
                           insertbackground=WHITE,
                           relief="flat", bd=0, cursor="xterm")
            ent.pack(fill="x", padx=14, pady=12)

            ph = fd.get("placeholder", "")
            if ph and not pre:
                ent.insert(0, ph)
                ent.config(fg=MUTED)

            def _efi(e, en=ent, ph=ph, b=border_f):
                if ph and en.get() == ph:
                    en.delete(0, "end")
                    en.config(fg=TEXT)
                b.config(bg=ACCENT)

            def _efo(e, en=ent, ph=ph, b=border_f):
                if not en.get():
                    if ph:
                        en.insert(0, ph)
                        en.config(fg=MUTED)
                b.config(bg=BORDER)

            ent.bind("<FocusIn>",  _efi)
            ent.bind("<FocusOut>", _efo)

            # ── Real-time inline validation for constrained fields ──
            def _rt_validate(e, k=key, v=var, el=err_lbl, b=border_f, ph=ph):
                val = v.get().strip()
                if val == ph or not val: el.config(text=""); el.pack_forget(); return
                err = None
                if k == "name":   err = Dialog._validate_name(val)
                elif k == "email": err = Dialog._validate_email(val)
                elif k == "phone": err = Dialog._validate_phone(val)
                if err:
                    el.config(text=f"⚠  {err}")
                    el.pack(fill="x", pady=(3,0))
                    b.config(bg=DANGER)
                else:
                    el.config(text=""); el.pack_forget()
                    b.config(bg=SUCCESS)

            if key in ("name", "email", "phone"):
                ent.bind("<KeyRelease>", _rt_validate)
                var.trace_add("write", lambda *a, k=key, v=var, el=err_lbl, b=border_f, ph=ph:
                              _rt_validate(None, k, v, el, b, ph))

            self._widgets[key] = ent

        # err_lbl must be packed AFTER the input widget (so it appears below)
        # but only when it has content — it starts hidden
        err_lbl.pack_forget()

        # Hint text below field
        if fd.get("hint"):
            tk.Label(wrap, text="ℹ  " + fd["hint"],
                     font=ff(9), fg=DIM, bg=SURFACE).pack(anchor="w", pady=(5, 0))

    # ── Field validators ──────────────────────────────────────────────────────
    @staticmethod
    def _validate_name(val):
        """2–60 chars, letters/spaces/hyphens/apostrophes only."""
        import re
        if len(val) < 2:
            return "Name must be at least 2 characters."
        if len(val) > 60:
            return "Name must be 60 characters or fewer."
        if not re.match(r"^[A-Za-z\u00C0-\u024F '\-\.]+$", val):
            return "Name may only contain letters, spaces, hyphens, or apostrophes."
        return None

    @staticmethod
    def _validate_email(val):
        """Basic RFC-style check: local@domain.tld"""
        import re
        pattern = r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
        if not re.match(pattern, val):
            return "Please enter a valid email address (e.g. user@example.com)."
        return None

    @staticmethod
    def _validate_phone(val):
        """7–15 digits (ignoring spaces, dashes, dots, parentheses, leading +)."""
        import re
        digits = re.sub(r"[\s\-\.\(\)]+", "", val)
        if digits.startswith("+"):
            digits = digits[1:]
        if not digits.isdigit():
            return "Phone number may only contain digits, spaces, +, -, ( and )."
        if len(digits) < 7:
            return "Phone number must have at least 7 digits."
        if len(digits) > 15:
            return "Phone number must have 15 digits or fewer."
        return None

    def _save(self):
        friendly = {
            "name":        "Please enter a name.",
            "email":       "Please enter an email address.",
            "phone":       "Please enter a phone number.",
            "field":       "Please choose a domain or field.",
            "expertise":   "Please enter at least one skill.",
            "topic":       "Please enter what you want to learn.",
            "goal":        "Please describe your learning goal.",
            "title":       "Please give this a title.",
            "participants":"Please enter the participant names.",
            "date":        "Please enter a date (YYYY-MM-DD).",
            "status":      "Please choose a status.",
            "priority":    "Please choose a priority level.",
            "mentee":      "Please enter the mentee name.",
            "mentor_name": "Please select a mentor.",
            "mentee_name": "Please select a mentee.",
        }
        result = {}
        for fd in self._fields:
            key = fd["key"]
            w   = self._vars[key]
            if isinstance(w, tk.Text):
                val = w.get("1.0", "end-1c").strip()
                if val == fd.get("placeholder", ""): val = ""
            elif isinstance(w, tk.StringVar):
                val = w.get().strip()
                if val == fd.get("placeholder", ""): val = ""
            else:
                val = ""

            # ── Required check ──
            if fd.get("required") and not val:
                messagebox.showwarning(
                    "Missing Info",
                    friendly.get(key, f"Please fill in '{fd['label']}'."),
                    parent=self)
                wgt = self._widgets.get(key)
                if wgt: wgt.focus_set()
                return

            # ── Format constraints (only when a value is provided) ──
            if val:
                err = None
                if key == "name":
                    err = self._validate_name(val)
                elif key == "email":
                    err = self._validate_email(val)
                elif key == "phone":
                    err = self._validate_phone(val)

                if err:
                    messagebox.showwarning("Invalid Input", err, parent=self)
                    wgt = self._widgets.get(key)
                    if wgt: wgt.focus_set()
                    return

            result[key] = val
        self.result = result
        self.destroy()


# ══════════════════════════════════════════════════════════════════════════════
#  FIELD SCHEMAS
# ══════════════════════════════════════════════════════════════════════════════
DOMAINS = ["Engineering","Design","Product","Data Science","Marketing",
           "Business","Finance","Healthcare","Law","Education","Other"]
AVAIL   = ["30 mins/week","1 hr/week","2 hrs/week","3-5 hrs/week","Flexible"]
MODES   = ["Online","In-person","Both"]
GENDERS = ["Male","Female","Non-binary","Prefer not to say"]

MENTOR_F = [
    {"key":"name",        "label":"Name",                     "type":"entry",  "placeholder":"First and last name",           "required":True},
    {"key":"gender",      "label":"Gender",                   "type":"combo",  "values":GENDERS,                              "required":True},
    {"key":"age",         "label":"Age Group",                "type":"combo",  "values":["18-24","25-30","31-35","36-40","41-50","51+"], "required":True},
    {"key":"email",       "label":"Email",                    "type":"entry",  "placeholder":"Your email address",            "required":True},
    {"key":"phone",       "label":"Phone",                    "type":"entry",  "placeholder":"Your phone number",             "required":True},
    {"key":"field",       "label":"Domain / Field",           "type":"combo",  "values":DOMAINS,                              "required":True},
    {"key":"expertise",   "label":"Skills & Expertise",       "type":"entry",  "placeholder":"e.g. Python, ML, AWS",          "required":True},
    {"key":"years",       "label":"Years of Experience",      "type":"combo",  "values":["<1 year","1-2 years","3-5 years","6-10 years","10-15 years","15-20 years","20+ years"], "required":True},
    {"key":"company",     "label":"Company / Organisation",   "type":"entry",  "placeholder":"Where do you work?",            "required":True},
    {"key":"location",    "label":"City",                     "type":"entry",  "placeholder":"Your city",                     "required":True},
    {"key":"linkedin",    "label":"LinkedIn",                 "type":"entry",  "placeholder":"Your LinkedIn URL"},
    {"key":"availability","label":"Weekly Availability",      "type":"combo",  "values":AVAIL,                                "required":True},
    {"key":"mode",        "label":"Preferred Meeting Mode",   "type":"combo",  "values":MODES,                                "required":True},
    {"key":"language",    "label":"Languages",                "type":"entry",  "placeholder":"e.g. English, Hindi",           "required":True},
    {"key":"bio",         "label":"Short Bio",                "type":"text",   "placeholder":"Tell mentees about yourself and what you offer...", "height":4, "required":True},
]

MENTEE_F = [
    {"key":"name",        "label":"Name",                     "type":"entry",  "placeholder":"First and last name",           "required":True},
    {"key":"gender",      "label":"Gender",                   "type":"combo",  "values":GENDERS,                              "required":True},
    {"key":"age",         "label":"Age Group",                "type":"combo",  "values":["Under 18","18-22","23-27","28-32","33-40","41+"], "required":True},
    {"key":"email",       "label":"Email",                    "type":"entry",  "placeholder":"Your email address",            "required":True},
    {"key":"phone",       "label":"Phone",                    "type":"entry",  "placeholder":"Your phone number",             "required":True},
    {"key":"field",       "label":"Domain / Field",           "type":"combo",  "values":DOMAINS,                              "required":True},
    {"key":"level",       "label":"Current Level",            "type":"combo",  "values":["Student","Fresh Graduate","Junior (0-2 yrs)","Mid-level (2-5 yrs)","Senior / Career Change"], "required":True},
    {"key":"institution", "label":"College / Company",        "type":"entry",  "placeholder":"Where do you study or work?",   "required":True},
    {"key":"topic",       "label":"Topic / Skill to Learn",   "type":"entry",  "placeholder":"What do you want to learn?",    "required":True},
    {"key":"goal",        "label":"Learning Goal",            "type":"text",   "placeholder":"What do you want to achieve with a mentor?", "height":3, "required":True},
    {"key":"location",    "label":"City",                     "type":"entry",  "placeholder":"Your city",                     "required":True},
    {"key":"linkedin",    "label":"LinkedIn / Portfolio",     "type":"entry",  "placeholder":"Your LinkedIn or portfolio URL"},
    {"key":"availability","label":"Weekly Availability",      "type":"combo",  "values":AVAIL,                                "required":True},
    {"key":"mode",        "label":"Preferred Meeting Mode",   "type":"combo",  "values":MODES,                                "required":True},
    {"key":"language",    "label":"Languages",                "type":"entry",  "placeholder":"e.g. English, Hindi",           "required":True},
    {"key":"note",        "label":"Anything to Add?",         "type":"text",   "placeholder":"Any extra context for your mentor...", "height":3},
]

SESSION_F = [
    {"key":"title",       "label":"Session Title",            "type":"entry",      "placeholder":"e.g. Resume Review, Mock Interview", "required":True},
    {"key":"participants","label":"Participants",              "type":"entry",      "placeholder":"Mentor and mentee names",         "required":True},
    {"key":"date",        "label":"Date",                     "type":"datepicker", "placeholder":"YYYY-MM-DD",                      "required":True},
    {"key":"time",        "label":"Time",                     "type":"combo",      "values":["8:00 AM","9:00 AM","10:00 AM","11:00 AM","12:00 PM","1:00 PM","2:00 PM","3:00 PM","4:00 PM","5:00 PM","6:00 PM","7:00 PM","8:00 PM","9:00 PM"]},
    {"key":"duration",    "label":"Duration",                 "type":"combo",      "values":["15 mins","30 mins","45 mins","1 hour","1.5 hours","2 hours","2.5 hours","3 hours"]},
    {"key":"mode",        "label":"Meeting Mode",             "type":"combo",      "values":["Online — Google Meet","Online — Zoom","Online — Teams","Phone Call","In-person","Other"]},
    {"key":"topic",       "label":"Topic / Focus Area",       "type":"entry",      "placeholder":"What will this session cover?"},
    {"key":"status",      "label":"Status",                   "type":"combo",      "values":["Upcoming","Completed","Cancelled","Rescheduled"], "required":True},
    {"key":"notes",       "label":"Agenda / Notes",           "type":"text",       "placeholder":"What will be discussed? Any prep needed?", "height":3},
    {"key":"outcome",     "label":"Outcome / Action Items",   "type":"text",       "placeholder":"What was decided or assigned after the session?", "height":3},
]

GOAL_F = [
    {"key":"title",       "label":"Goal",                     "type":"entry",      "placeholder":"What is the goal?",             "required":True},
    {"key":"mentee",      "label":"Mentee",                   "type":"entry",      "placeholder":"Mentee name",                   "required":True},
    {"key":"mentor",      "label":"Mentor",                   "type":"entry",      "placeholder":"Mentor name"},
    {"key":"category",    "label":"Category",                 "type":"combo",      "values":["Skill Building","Career Growth","Academic","Personal Development","Certification","Portfolio / Projects","Networking","Other"]},
    {"key":"priority",    "label":"Priority",                 "type":"combo",      "values":["High","Medium","Low"],              "required":True},
    {"key":"due",         "label":"Due Date",                 "type":"datepicker", "placeholder":"YYYY-MM-DD"},
    {"key":"milestones",  "label":"Milestones / Steps",       "type":"text",       "placeholder":"Break it into steps...",        "height":4},
    {"key":"resources",   "label":"Resources",                "type":"text",       "placeholder":"Courses, books, links...",      "height":2},
    {"key":"status",      "label":"Status",                   "type":"combo",      "values":["Not Started","In Progress","Completed","On Hold","Dropped"], "required":True},
]

PAIR_F_BASE = [
    {"key":"field",       "label":"Focus Field",              "type":"combo",  "values":DOMAINS,   "required":True},
    {"key":"notes",       "label":"Pairing Notes",            "type":"text",   "placeholder":"Why is this a good match?", "height":3},
]

# ══════════════════════════════════════════════════════════════════════════════
#  DONUT CHART WIDGET
# ══════════════════════════════════════════════════════════════════════════════
def draw_donut(canvas, cx, cy, r_out, r_in, segments, bg_color):
    """segments = list of (value, color, label)"""
    total = sum(v for v,_,_ in segments) or 1
    angle = -90  # start top
    canvas.delete("all")

    for val, col, lbl in segments:
        sweep = 360 * val / total
        if sweep < 1: continue
        # Draw arc using polygon approximation
        steps = max(3, int(sweep / 3))
        outer_pts, inner_pts = [], []
        for i in range(steps+1):
            a = math.radians(angle + sweep*i/steps)
            outer_pts += [cx + r_out*math.cos(a), cy + r_out*math.sin(a)]
            inner_pts  = [cx + r_in*math.cos(a),  cy + r_in*math.sin(a)] + inner_pts
        pts = outer_pts + inner_pts
        if len(pts) >= 6:
            canvas.create_polygon(pts, fill=col, outline=bg_color, width=2)
        angle += sweep

    # Center hole fill
    canvas.create_oval(cx-r_in, cy-r_in, cx+r_in, cy+r_in,
                       fill=bg_color, outline="")

def draw_bar(canvas, x, y, w, h, pct, col, bg):
    canvas.create_rectangle(x, y, x+w, y+h, fill=bg, outline="")
    filled = int(w * min(pct,1))
    if filled > 0:
        canvas.create_rectangle(x, y, x+filled, y+h, fill=col, outline="")

# ══════════════════════════════════════════════════════════════════════════════
#  MAIN APP
# ══════════════════════════════════════════════════════════════════════════════
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MentorLink — Mentor & Mentee System")
        self.geometry("1300x820")
        self.minsize(1000, 660)
        self.configure(bg=BG)
        self.data         = load_data()
        self._active_tab  = ""
        self._build_ui()
        self.show("dashboard")

    # ── UI STRUCTURE ──────────────────────────────────────────────────────────
    def _build_ui(self):
        # ── Sidebar ──
        sb = tk.Frame(self, bg=SURFACE, width=248)
        sb.pack(side="left", fill="y")
        sb.pack_propagate(False)

        # Logo
        lo = tk.Frame(sb, bg=SURFACE)
        lo.pack(fill="x", padx=22, pady=(28,22))
        tk.Label(lo, text="◈", font=("Georgia",24), fg=ACCENT, bg=SURFACE).pack(side="left")
        tk.Label(lo, text="  MentorLink", font=("Georgia",16,"bold"),
                 fg=TEXT, bg=SURFACE).pack(side="left")

        hline(sb).pack(fill="x", padx=16, pady=(0,12))

        self._navbtns = {}
        tabs = [
            ("dashboard", "⊞", "Dashboard"),
            ("mentors",   "◉", "Mentors"),
            ("mentees",   "○", "Mentees"),
            ("sessions",  "◷", "Sessions"),
            ("goals",     "◈", "Goals & Progress"),
            ("matching",  "⇌", "Matching"),
        ]
        for tid, ico, lbl in tabs:
            row = tk.Frame(sb, bg=SURFACE, cursor="hand2")
            row.pack(fill="x", padx=8, pady=1)
            row.bind("<Button-1>", lambda e,t=tid: self.show(t))
            ico_l = tk.Label(row, text=ico, font=ff(14), fg=MUTED, bg=SURFACE,
                             width=3, cursor="hand2")
            lbl_l = tk.Label(row, text=lbl, font=ff(12), fg=MUTED, bg=SURFACE,
                             anchor="w", cursor="hand2", pady=11, padx=6)
            ico_l.pack(side="left", padx=(12,0))
            lbl_l.pack(side="left", fill="x", expand=True)
            ico_l.bind("<Button-1>", lambda e,t=tid: self.show(t))
            lbl_l.bind("<Button-1>", lambda e,t=tid: self.show(t))
            for w in [row, ico_l, lbl_l]:
                w.bind("<Enter>", lambda e,r=row,i=ico_l,l=lbl_l,t=tid:
                       self._nhover(r,i,l,t,True))
                w.bind("<Leave>", lambda e,r=row,i=ico_l,l=lbl_l,t=tid:
                       self._nhover(r,i,l,t,False))
            self._navbtns[tid] = (row, ico_l, lbl_l)

        tk.Label(sb, text="v3.0  ·  MentorLink", font=ff(9),
                 fg=DIM, bg=SURFACE).pack(side="bottom", pady=14)

        # ── Main area ──
        self._main = tk.Frame(self, bg=BG)
        self._main.pack(side="left", fill="both", expand=True)
        self._pages = {}
        for tid,_,_ in tabs:
            p = tk.Frame(self._main, bg=BG)
            p.place(relwidth=1, relheight=1)
            self._pages[tid] = p

        self._build_dashboard(self._pages["dashboard"])
        self._build_people_page("mentors","mentor")
        self._build_people_page("mentees","mentee")
        self._build_sessions_page()
        self._build_goals_page()
        self._build_matching_page()

    def _nhover(self, row, ico, lbl, tid, on):
        if tid == self._active_tab: return
        c_bg = CARD if on else SURFACE
        c_fg = TEXT if on else MUTED
        row.config(bg=c_bg); ico.config(fg=c_fg, bg=c_bg)
        lbl.config(fg=c_fg, bg=c_bg)

    def show(self, tid):
        old = self._active_tab
        self._active_tab = tid

        for t,(row,ico,lbl) in self._navbtns.items():
            if t == tid:
                row.config(bg=CARD2); ico.config(fg=ACCENT, bg=CARD2)
                lbl.config(fg=WHITE,  bg=CARD2, font=ff(12,"bold"))
            else:
                row.config(bg=SURFACE); ico.config(fg=MUTED, bg=SURFACE)
                lbl.config(fg=MUTED, bg=SURFACE, font=ff(12))

        for t,p in self._pages.items():
            (p.lift if t==tid else p.lower)()

        self.data = load_data()
        getattr(self, f"_refresh_{tid}")()


    # ══════════════════════════════════════════════════════════════════════════
    #  DASHBOARD — Professional graph layout
    # ══════════════════════════════════════════════════════════════════════════
    def _build_dashboard(self, page):
        self._db_greet  = tk.Frame(page, bg=BG)
        self._db_greet.pack(fill="x", padx=36, pady=(28,0))
        self._db_stats  = tk.Frame(page, bg=BG)
        self._db_stats.pack(fill="x", padx=36, pady=(14,0))
        self._db_charts = tk.Frame(page, bg=BG)
        self._db_charts.pack(fill="both", expand=True, padx=36, pady=(12,0))
        self._db_bottom = tk.Frame(page, bg=BG)
        self._db_bottom.pack(fill="x", padx=36, pady=(12,14))

    def _refresh_dashboard(self):
        for f in [self._db_greet, self._db_stats,
                  self._db_charts, self._db_bottom]:
            for w in f.winfo_children(): w.destroy()
        d = self.data

        # ── Greeting ──
        today_str = date.today().strftime("%A, %d %B %Y")
        tk.Label(self._db_greet, text="Welcome back to MentorLink",
                 font=("Georgia",22,"bold"), fg=TEXT, bg=BG).pack(side="left")
        tk.Label(self._db_greet, text=today_str, font=ff(10),
                 fg=MUTED, bg=BG).pack(side="right", anchor="s", pady=6)

        # ── Reminder banners ──
        today = date.today()
        upcoming_soon = []
        for s in d["sessions"]:
            if s.get("status") == "Upcoming":
                try:
                    sd = datetime.strptime(s["date"], "%Y-%m-%d").date()
                    days_away = (sd - today).days
                    if 0 <= days_away <= 3:
                        upcoming_soon.append((days_away, s))
                except Exception:
                    pass
        upcoming_soon.sort(key=lambda x: x[0])

        overdue_goals = []
        for g in d["goals"]:
            if g.get("status") not in ("Completed","Dropped") and g.get("due"):
                try:
                    gd = datetime.strptime(g["due"], "%Y-%m-%d").date()
                    if gd < today:
                        overdue_goals.append(g)
                except Exception:
                    pass

        if upcoming_soon or overdue_goals:
            alerts = tk.Frame(self._db_greet, bg=BG)
            alerts.pack(fill="x", side="bottom", pady=(8,0))
            # re-parent: put below greeting in same frame area — use db_stats space instead
            alerts.pack_forget()
            # draw banners in a dedicated row above stats
            banner_row = tk.Frame(self._db_stats, bg=BG)
            # We'll inject banners before the KPI cards: use a separate container
            # Actually inject after the greeting by using _db_stats pre-slot
            pass

        # Banners drawn inline after greeting
        for days_away, s in upcoming_soon[:2]:
            day_label = "Today" if days_away==0 else ("Tomorrow" if days_away==1 else f"In {days_away} days")
            banner = tk.Frame(self._db_greet, bg=CARD2,
                              highlightthickness=1, highlightbackground=ACCENT)
            banner.pack(fill="x", side="bottom", pady=(6,0))
            tk.Frame(banner, bg=ACCENT, width=4).pack(side="left", fill="y")
            tk.Label(banner,
                     text=f"◷  {day_label}: {s.get('title','')}  ·  {s.get('participants','')}  ·  {s.get('time','')}",
                     font=ff(10,"bold"), fg=TEXT, bg=CARD2,
                     padx=12, pady=7).pack(side="left")
            tk.Label(banner, text=day_label,
                     font=ff(9,"bold"), fg=ACCENT, bg=CARD2, padx=8).pack(side="right")

        for g in overdue_goals[:2]:
            banner = tk.Frame(self._db_greet, bg=CARD2,
                              highlightthickness=1, highlightbackground=DANGER)
            banner.pack(fill="x", side="bottom", pady=(4,0))
            tk.Frame(banner, bg=DANGER, width=4).pack(side="left", fill="y")
            tk.Label(banner,
                     text=f"⚠  Overdue goal: {g.get('title','')}  ·  Due {g.get('due','')}",
                     font=ff(10,"bold"), fg=TEXT, bg=CARD2,
                     padx=12, pady=7).pack(side="left")
            tk.Label(banner, text="Overdue",
                     font=ff(9,"bold"), fg=DANGER, bg=CARD2, padx=8).pack(side="right")

        # ── KPI cards ──
        goals    = d["goals"]
        total_g  = len(goals)
        done_g   = sum(1 for g in goals if g.get("status")=="Completed")
        pct_g    = int(done_g/total_g*100) if total_g else 0
        sessions = d["sessions"]
        upcoming = sum(1 for s in sessions if s.get("status")=="Upcoming")

        kpis = [
            ("Total Mentors", len(d["mentors"]), ACCENT,  "◉", f"{len(d['pairs'])} paired"),
            ("Total Mentees", len(d["mentees"]), TEAL,    "○", f"{len(d['pairs'])} paired"),
            ("Sessions",      len(sessions),     ORANGE,  "◷", f"{upcoming} upcoming"),
            ("Goals",         total_g,           PINK,    "◈", f"{pct_g}% complete"),
            ("Active Pairs",  len(d["pairs"]),   SUCCESS, "⇌", "matched"),
        ]
        for i,(lbl,val,col,ico,sub) in enumerate(kpis):
            self._db_stats.columnconfigure(i, weight=1)
            c = tk.Frame(self._db_stats, bg=CARD,
                         highlightthickness=1, highlightbackground=BORDER)
            c.grid(row=0, column=i, padx=(0,10), sticky="nsew")
            tk.Frame(c, bg=col, height=4).pack(fill="x")
            b = tk.Frame(c, bg=CARD)
            b.pack(fill="x", padx=14, pady=12)
            tk.Label(b, text=str(val), font=("Georgia",30,"bold"),
                     fg=col, bg=CARD).pack(anchor="w")
            tk.Label(b, text=lbl, font=ff(10,"bold"), fg=TEXT,  bg=CARD).pack(anchor="w")
            tk.Label(b, text=sub, font=ff(9),         fg=MUTED, bg=CARD).pack(anchor="w",pady=(2,0))
            bar_bg = tk.Frame(c, bg=CARD2, height=4)
            bar_bg.pack(fill="x")
            total_all = max(sum(len(d[k]) for k in ["mentors","mentees","sessions","goals","pairs"]),1)
            if val:
                tk.Frame(bar_bg, bg=col, height=4).place(relwidth=min(val/total_all,1), relheight=1)

        # ── Charts row: 3 columns ──
        col_a = tk.Frame(self._db_charts, bg=BG)
        col_a.pack(side="left", fill="both", expand=True, padx=(0,10))
        col_b = tk.Frame(self._db_charts, bg=BG)
        col_b.pack(side="left", fill="both", expand=True, padx=(0,10))
        col_c = tk.Frame(self._db_charts, bg=BG)
        col_c.pack(side="left", fill="both", expand=True)

        # ── A: Goals donut ──
        ga = tk.Frame(col_a, bg=CARD, highlightthickness=1, highlightbackground=BORDER)
        ga.pack(fill="both", expand=True)
        tk.Frame(ga, bg=ACCENT, height=4).pack(fill="x")
        th = tk.Frame(ga, bg=CARD)
        th.pack(fill="x", padx=16, pady=(12,0))
        tk.Label(th, text="Goals Overview",   font=ff(12,"bold"), fg=TEXT,  bg=CARD).pack(side="left")
        tk.Label(th, text=f"{total_g} total", font=ff(9),         fg=MUTED, bg=CARD).pack(side="right")

        g_prog = sum(1 for g in goals if g.get("status")=="In Progress")
        g_none = sum(1 for g in goals if g.get("status")=="Not Started")
        g_hold = sum(1 for g in goals if g.get("status") in ("On Hold","Dropped"))
        segs   = [(done_g,SUCCESS,"Completed"),(g_prog,ACCENT,"In Progress"),
                  (g_none,ORANGE,"Not Started"),(g_hold,MUTED,"On Hold")]
        segs   = [(v,c,l) for v,c,l in segs if v>0]

        cv_g = tk.Canvas(ga, width=260, height=200, bg=CARD, highlightthickness=0)
        cv_g.pack(pady=(8,0))
        if segs:
            draw_donut(cv_g, 130,100,90,54, segs, CARD)
            cv_g.create_text(130,88,  text=f"{pct_g}%", font=("Georgia",20,"bold"), fill=SUCCESS)
            cv_g.create_text(130,108, text="complete",   font=ff(9),                fill=MUTED)
            cv_g.create_text(130,124, text=f"{done_g}/{total_g}", font=ff(9),       fill=DIM)
        else:
            cv_g.create_text(130,100, text="No goals yet", font=ff(11), fill=MUTED)

        leg_f = tk.Frame(ga, bg=CARD)
        leg_f.pack(padx=16, pady=(6,12), fill="x")
        for idx,(val,col,lbl) in enumerate(segs):
            lg = tk.Frame(leg_f, bg=CARD)
            lg.grid(row=idx//2, column=idx%2, sticky="w", padx=(0,14), pady=2)
            tk.Frame(lg, bg=col, width=10, height=10).pack(side="left", padx=(0,5))
            tk.Label(lg, text=f"{lbl} ({val})", font=ff(9), fg=MUTED, bg=CARD).pack(side="left")

        # ── B: Stacked bar — People by field ──
        bc = tk.Frame(col_b, bg=CARD, highlightthickness=1, highlightbackground=BORDER)
        bc.pack(fill="both", expand=True)
        tk.Frame(bc, bg=TEAL, height=4).pack(fill="x")
        th2 = tk.Frame(bc, bg=CARD)
        th2.pack(fill="x", padx=16, pady=(12,0))
        tk.Label(th2, text="People by Field",    font=ff(12,"bold"), fg=TEXT,  bg=CARD).pack(side="left")
        tk.Label(th2, text="mentors + mentees",  font=ff(9),         fg=MUTED, bg=CARD).pack(side="right")

        fc = {}
        for m in d["mentors"]: f=m.get("field","Other"); fc.setdefault(f,[0,0]); fc[f][0]+=1
        for m in d["mentees"]: f=m.get("field","Other"); fc.setdefault(f,[0,0]); fc[f][1]+=1
        sorted_f  = sorted(fc.items(), key=lambda x:-(x[1][0]+x[1][1]))[:7]
        max_v     = max((v[0]+v[1] for _,v in sorted_f), default=1)

        bar_area = tk.Frame(bc, bg=CARD)
        bar_area.pack(fill="both", expand=True, padx=16, pady=(12,0))
        if not sorted_f:
            tk.Label(bar_area, text="No people added yet", font=ff(10), fg=MUTED, bg=CARD).pack(pady=40)
        else:
            for field,(mn,me) in sorted_f:
                row = tk.Frame(bar_area, bg=CARD)
                row.pack(fill="x", pady=5)
                tk.Label(row, text=field[:13], font=ff(9), fg=MUTED, bg=CARD,
                         width=11, anchor="e").pack(side="left", padx=(0,8))
                cv_b = tk.Canvas(row, height=20, bg=CARD, highlightthickness=0)
                cv_b.pack(side="left", fill="x", expand=True)
                cv_b.update_idletasks()
                bw = max(cv_b.winfo_width(), 120)
                mw = int(bw*mn/max_v); ew = int(bw*me/max_v)
                cv_b.create_rectangle(0,3,bw,17, fill=CARD2, outline="")
                if mw>0: cv_b.create_rectangle(0,3,mw,17, fill=ACCENT, outline="")
                if ew>0: cv_b.create_rectangle(mw,3,mw+ew,17, fill=TEAL, outline="")
                tk.Label(row, text=f"{mn+me}", font=ff(9,"bold"),
                         fg=TEXT, bg=CARD, width=3).pack(side="left", padx=(6,0))

        leg_b = tk.Frame(bc, bg=CARD)
        leg_b.pack(padx=16, pady=(8,12), anchor="w")
        for col,lbl in [(ACCENT,"Mentors"),(TEAL,"Mentees")]:
            r = tk.Frame(leg_b, bg=CARD)
            r.pack(side="left", padx=(0,14))
            tk.Frame(r, bg=col, width=10, height=10).pack(side="left", padx=(0,4))
            tk.Label(r, text=lbl, font=ff(9), fg=MUTED, bg=CARD).pack(side="left")

        # ── C: Activity timeline ──
        ac = tk.Frame(col_c, bg=CARD, highlightthickness=1, highlightbackground=BORDER)
        ac.pack(fill="both", expand=True)
        tk.Frame(ac, bg=PINK, height=4).pack(fill="x")
        tk.Label(ac, text="Recent Activity", font=ff(12,"bold"),
                 fg=TEXT, bg=CARD).pack(anchor="w", padx=14, pady=(12,8))

        events = []
        for s in sessions:
            scol = {"Completed":SUCCESS,"Upcoming":ACCENT,"Cancelled":DANGER}.get(s.get("status",""),MUTED)
            events.append((s.get("date",""), scol,
                           s.get("title","Session")[:26], f"Session · {s.get('status','')}"))
        for p in d["pairs"]:
            events.append((p.get("date",""), SUCCESS,
                           f"{p.get('mentor_name','')} ⇌ {p.get('mentee_name','')}",
                           "Pair created"))
        events.sort(key=lambda x:x[0], reverse=True)

        if not events:
            tk.Label(ac, text="No activity yet", font=ff(10), fg=MUTED, bg=CARD).pack(padx=14, anchor="w")
        for _,col,title,sub in events[:7]:
            row = tk.Frame(ac, bg=CARD)
            row.pack(fill="x", padx=8, pady=2)
            dot_f = tk.Frame(row, bg=CARD, width=20)
            dot_f.pack(side="left", fill="y")
            dot_f.pack_propagate(False)
            cv_d = tk.Canvas(dot_f, width=20, height=34, bg=CARD, highlightthickness=0)
            cv_d.pack()
            cv_d.create_oval(4,8,16,20, fill=col, outline="")
            cv_d.create_line(10,20,10,34, fill=BORDER, width=1)
            info = tk.Frame(row, bg=CARD2)
            info.pack(side="left", fill="x", expand=True, padx=(4,0))
            tk.Label(info, text=title, font=ff(9,"bold"), fg=TEXT,
                     bg=CARD2, anchor="w", padx=7, pady=3).pack(fill="x")
            tk.Label(info, text=sub,   font=ff(8),        fg=MUTED,
                     bg=CARD2, anchor="w", padx=7).pack(fill="x")
            tk.Frame(info, bg=CARD, height=2).pack(fill="x")

        # ── Bottom row ──
        gp = tk.Frame(self._db_bottom, bg=CARD, highlightthickness=1, highlightbackground=BORDER)
        gp.pack(side="left", fill="both", expand=True, padx=(0,10))
        tk.Frame(gp, bg=SUCCESS, height=4).pack(fill="x")
        gh = tk.Frame(gp, bg=CARD)
        gh.pack(fill="x", padx=16, pady=(12,6))
        tk.Label(gh, text="Goal Progress by Priority", font=ff(11,"bold"), fg=TEXT,  bg=CARD).pack(side="left")
        tk.Label(gh, text="click ◈ Goals to manage",   font=ff(9),         fg=MUTED, bg=CARD).pack(side="right")
        for priority,col in [("High",DANGER),("Medium",ORANGE),("Low",SUCCESS)]:
            pg = [g for g in goals if g.get("priority")==priority]
            if not pg: continue
            pd  = sum(1 for g in pg if g.get("status")=="Completed")
            pp  = int(pd/len(pg)*100)
            pr  = tk.Frame(gp, bg=CARD)
            pr.pack(fill="x", padx=16, pady=4)
            tk.Label(pr, text=priority, font=ff(9,"bold"), fg=col, bg=CARD, width=8, anchor="w").pack(side="left")
            bg2 = tk.Frame(pr, bg=CARD2, height=14)
            bg2.pack(side="left", fill="x", expand=True, padx=(6,8))
            bg2.update_idletasks()
            if pp: tk.Frame(bg2, bg=col, height=14).place(relwidth=pp/100, relheight=1)
            tk.Label(pr, text=f"{pp}% ({pd}/{len(pg)})", font=ff(9), fg=MUTED, bg=CARD, width=14, anchor="w").pack(side="left")
        tk.Frame(gp, bg=CARD, height=8).pack()

        qa_card = tk.Frame(self._db_bottom, bg=CARD, highlightthickness=1,
                           highlightbackground=BORDER, width=210)
        qa_card.pack(side="right", fill="y")
        qa_card.pack_propagate(False)
        tk.Frame(qa_card, bg=ORANGE, height=4).pack(fill="x")
        tk.Label(qa_card, text="Quick Actions", font=ff(11,"bold"),
                 fg=TEXT, bg=CARD).pack(anchor="w", padx=14, pady=(12,8))
        for lbl,tab,col in [("◉  Add Mentor","mentors",ACCENT),
                             ("○  Add Mentee","mentees",TEAL),
                             ("◷  Schedule","sessions",ORANGE),
                             ("◈  Add Goal","goals",PINK),
                             ("⇌  Create Pair","matching",SUCCESS)]:
            b = tk.Button(qa_card, text=lbl, font=ff(10,"bold"),
                          fg=col, bg=CARD2,
                          activeforeground=WHITE, activebackground=col,
                          relief="flat", cursor="hand2",
                          pady=8, padx=12, bd=0, anchor="w",
                          highlightthickness=1, highlightbackground=BORDER,
                          command=lambda t=tab: self.show(t))
            b.pack(fill="x", padx=8, pady=2)
            b.bind("<Enter>", lambda e,b=b,c=col: b.config(fg=WHITE, bg=c))
            b.bind("<Leave>", lambda e,b=b,c=col: b.config(fg=c, bg=CARD2))

    # ══════════════════════════════════════════════════════════════════════════
    #  MENTORS / MENTEES
    # ══════════════════════════════════════════════════════════════════════════
    def _build_people_page(self, page_key, role):
        page  = self._pages[page_key]
        title = "Mentors" if role=="mentor" else "Mentees"
        sub   = ("Experienced guides offering their knowledge."
                 if role=="mentor" else
                 "Motivated learners on their growth journey.")
        PageHeader(page, title, sub,
                   f"+ Add {title[:-1]}",
                   lambda r=role: self._add_person(r))

        # ── Toolbar: search + filter + export ──
        tb = tk.Frame(page, bg=BG)
        tb.pack(fill="x", padx=36, pady=(0,10))

        sv = tk.StringVar()
        sv.trace_add("write", lambda *a, r=role: self._refresh_people(r))
        setattr(self, f"_search_{role}", sv)
        SearchBar(tb, sv, f"Search {title.lower()}…").pack(side="left", fill="x", expand=True)

        # Field filter combo
        fv = tk.StringVar(value="All Fields")
        setattr(self, f"_filter_{role}", fv)
        fv.trace_add("write", lambda *a, r=role: self._refresh_people(r))
        f_border = tk.Frame(tb, bg=BORDER, padx=1, pady=1)
        f_border.pack(side="left", padx=(10,0))
        f_inner  = tk.Frame(f_border, bg=INPUT_BG)
        f_inner.pack()
        f_cb = ttk.Combobox(f_inner, textvariable=fv,
                            values=["All Fields"] + DOMAINS,
                            font=ff(10), state="readonly", width=16)
        f_cb.pack(padx=6, pady=6)

        export_col = ACCENT if role=="mentor" else TEAL
        Btn(tb, "⬇  Export CSV",
            lambda r=role: export_csv(self, self.data[f"{r}s"],
                                      f"{r}s.csv"),
            bg=export_col, w=16, py=7).pack(side="left", padx=(10,0))

        body = tk.Frame(page, bg=BG)
        body.pack(fill="both", expand=True)
        setattr(self, f"_body_{role}", body)

    def _refresh_mentors(self): self._refresh_people("mentor")
    def _refresh_mentees(self): self._refresh_people("mentee")

    def _refresh_people(self, role):
        body = getattr(self, f"_body_{role}")
        for w in body.winfo_children(): w.destroy()

        raw     = self.data[f"{role}s"]
        query   = getattr(self, f"_search_{role}", tk.StringVar()).get().strip().lower()
        ffilter = getattr(self, f"_filter_{role}", tk.StringVar()).get()

        people = raw
        if query and query not in ("search mentors…","search mentees…"):
            people = [p for p in people if
                      query in p.get("name","").lower() or
                      query in p.get("email","").lower() or
                      query in p.get("field","").lower() or
                      query in p.get("expertise","").lower() or
                      query in p.get("topic","").lower() or
                      query in p.get("location","").lower()]
        if ffilter and ffilter != "All Fields":
            people = [p for p in people if p.get("field","") == ffilter]

        if not people:
            f = tk.Frame(body, bg=BG)
            f.pack(expand=True, fill="both")
            msg = "No results match your search." if (query or ffilter!="All Fields") else f"No {role}s added yet."
            tk.Label(f, text="◈", font=("Georgia",52), fg=DIM, bg=BG).pack(pady=(90,6))
            tk.Label(f, text=msg, font=("Georgia",17,"bold"), fg=TEXT, bg=BG).pack()
            if not (query or ffilter not in ("All Fields",)):
                tk.Label(f, text=f"Click the button above to add your first {role}.",
                         font=ff(10), fg=MUTED, bg=BG).pack(pady=(3,20))
                Btn(f, f"+ Add {role.capitalize()}",
                    lambda r=role: self._add_person(r), w=26, py=11).pack()
            return

        inner, _ = Scroll(body, bg=BG)
        # result count label
        cnt = tk.Label(inner, text=f"{len(people)} of {len(raw)} {role}s",
                       font=ff(9), fg=MUTED, bg=BG, anchor="w")
        cnt.pack(fill="x", padx=40, pady=(4,0))
        grid = tk.Frame(inner, bg=BG)
        grid.pack(fill="both", padx=32, pady=4)
        for c in range(3): grid.columnconfigure(c, weight=1)
        for i,p in enumerate(people):
            self._person_card(grid, p, role).grid(
                row=i//3, column=i%3, padx=8, pady=8, sticky="nsew")

    def _person_card(self, parent, person, role):
        c = Card(parent, padx=0, pady=0)

        # Colour top accent
        col = ACCENT if role=="mentor" else TEAL
        tk.Frame(c, bg=col, height=3).pack(fill="x")

        body = tk.Frame(c, bg=CARD, padx=16, pady=14)
        body.pack(fill="both", expand=True)

        # Avatar + name
        top = tk.Frame(body, bg=CARD)
        top.pack(fill="x")
        cv = tk.Canvas(top, width=52, height=52, bg=CARD, highlightthickness=0)
        cv.pack(side="left")
        draw_av(cv, 26, 26, 22, person["name"], 13)

        info = tk.Frame(top, bg=CARD)
        info.pack(side="left", padx=10, fill="x", expand=True)
        tk.Label(info, text=person["name"], font=ff(13,"bold"),
                 fg=TEXT, bg=CARD).pack(anchor="w")
        sub = person.get("expertise") or person.get("topic","")
        if sub:
            tk.Label(info, text=sub[:36]+"…" if len(sub)>36 else sub,
                     font=ff(9), fg=MUTED, bg=CARD, wraplength=150).pack(anchor="w")

        # Pills
        pr = tk.Frame(body, bg=CARD)
        pr.pack(fill="x", pady=(8,0))
        for tag in [person.get("gender",""), person.get("age",""),
                    person.get("field","")]:
            if tag:
                # Fake pill via frame
                pf = tk.Frame(pr, bg=CARD2, highlightthickness=1,
                              highlightbackground=BORDER)
                pf.pack(side="left", padx=(0,5))
                tk.Label(pf, text=tag, font=ff(8), fg=MUTED,
                         bg=CARD2, padx=6, pady=3).pack()

        hline(body, BORDER).pack(fill="x", pady=10)

        # Details
        rows = [("✉",person.get("email","—")),
                ("☏",person.get("phone","—")),
                ("📍",person.get("location","—"))]
        if role=="mentor":
            rows += [("◷",f"{person.get('years','—')} exp"),
                     ("🏢",person.get("company","—"))]
        else:
            rows += [("◎",person.get("level","—")),
                     ("🏫",person.get("institution","—"))]
        rows.append(("⊙",person.get("availability","—")))

        for ico,val in rows:
            if val and val!="—":
                r = tk.Frame(body, bg=CARD)
                r.pack(fill="x", pady=1)
                tk.Label(r, text=ico, font=ff(10), bg=CARD,
                         fg=col, width=3).pack(side="left")
                tk.Label(r, text=str(val)[:40], font=ff(10),
                         fg=MUTED, bg=CARD).pack(side="left", padx=2)

        if person.get("bio") or person.get("goal"):
            note = person.get("bio") or person.get("goal","")
            hline(body, BORDER).pack(fill="x", pady=(8,4))
            tk.Label(body, text=note[:90]+"…" if len(note)>90 else note,
                     font=ff(9), fg=DIM, bg=CARD,
                     wraplength=210, justify="left").pack(anchor="w")

        hline(body, BORDER).pack(fill="x", pady=(10,8))
        br = tk.Frame(body, bg=CARD)
        br.pack(fill="x")
        GhostBtn(br,"✎  Edit",
                 lambda p=person,r=role: self._edit_person(p,r),
                 w=9).pack(side="left")
        GhostBtn(br,"✕  Delete",
                 lambda p=person,r=role: self._delete_person(p,r),
                 w=10).pack(side="right")
        return c

    def _add_person(self, role):
        fields = MENTOR_F if role=="mentor" else MENTEE_F
        dlg = Dialog(self, f"Add {role.capitalize()}",
                     "Fields marked * are required.",
                     fields)
        if dlg.result:
            dlg.result["id"] = uid()
            self.data[f"{role}s"].append(dlg.result)
            save_data(self.data)
            self._refresh_people(role)
            Toast(self, f"✓  {role.capitalize()} '{dlg.result.get('name','')}' added!", SUCCESS)

    def _edit_person(self, person, role):
        fields = MENTOR_F if role=="mentor" else MENTEE_F
        dlg = Dialog(self, f"Edit {role.capitalize()}",
                     "Update the details below.",
                     fields, prefill=person)
        if dlg.result:
            dlg.result["id"] = person["id"]
            lst = self.data[f"{role}s"]
            idx = next(i for i,p in enumerate(lst) if p["id"]==person["id"])
            lst[idx] = dlg.result
            save_data(self.data)
            self._refresh_people(role)
            Toast(self, f"✓  {role.capitalize()} updated.", TEAL)

    def _delete_person(self, person, role):
        if messagebox.askyesno("Delete",
                               f"Delete {person['name']}?"):
            self.data[f"{role}s"] = [p for p in self.data[f"{role}s"]
                                     if p["id"]!=person["id"]]
            save_data(self.data)
            self._refresh_people(role)
            Toast(self, f"✕  {person['name']} removed.", DANGER)

    # ══════════════════════════════════════════════════════════════════════════
    #  SESSIONS
    # ══════════════════════════════════════════════════════════════════════════
    def _build_sessions_page(self):
        page = self._pages["sessions"]
        PageHeader(page,"Sessions",
                   "Schedule, track and review all mentoring sessions.",
                   "+ Schedule Session", self._add_session)

        # Toolbar
        tb = tk.Frame(page, bg=BG)
        tb.pack(fill="x", padx=36, pady=(0,10))
        self._search_sessions = tk.StringVar()
        self._search_sessions.trace_add("write", lambda *a: self._refresh_sessions())
        SearchBar(tb, self._search_sessions, "Search sessions…").pack(side="left", fill="x", expand=True)

        self._filter_sessions = tk.StringVar(value="All")
        self._filter_sessions.trace_add("write", lambda *a: self._refresh_sessions())
        f_border = tk.Frame(tb, bg=BORDER, padx=1, pady=1)
        f_border.pack(side="left", padx=(10,0))
        f_inner  = tk.Frame(f_border, bg=INPUT_BG)
        f_inner.pack()
        ttk.Combobox(f_inner, textvariable=self._filter_sessions,
                     values=["All","Upcoming","Completed","Cancelled","Rescheduled"],
                     font=ff(10), state="readonly", width=14).pack(padx=6, pady=6)

        Btn(tb, "⬇  Export CSV",
            lambda: export_csv(self, self.data["sessions"], "sessions.csv"),
            bg=ORANGE, w=16, py=7).pack(side="left", padx=(10,0))

        self._body_sessions = tk.Frame(page, bg=BG)
        self._body_sessions.pack(fill="both", expand=True)

    def _refresh_sessions(self):
        for w in self._body_sessions.winfo_children(): w.destroy()
        raw      = self.data["sessions"]
        query    = getattr(self, "_search_sessions", tk.StringVar()).get().strip().lower()
        sf       = getattr(self, "_filter_sessions", tk.StringVar()).get()

        sessions = sorted(raw, key=lambda x: x.get("date",""), reverse=True)
        if query and query != "search sessions…":
            sessions = [s for s in sessions if
                        query in s.get("title","").lower() or
                        query in s.get("participants","").lower() or
                        query in s.get("topic","").lower() or
                        query in s.get("notes","").lower()]
        if sf and sf != "All":
            sessions = [s for s in sessions if s.get("status","") == sf]

        if not sessions:
            EmptyState(self._body_sessions,
                "No sessions found" if (query or sf!="All") else "No sessions yet",
                "Try a different search or schedule your first session.",
                "+ Schedule Session", self._add_session)
            return
        inner, _ = Scroll(self._body_sessions, bg=BG)
        tk.Label(inner, text=f"{len(sessions)} of {len(raw)} sessions",
                 font=ff(9), fg=MUTED, bg=BG, anchor="w").pack(fill="x", padx=40, pady=(4,0))
        cont = tk.Frame(inner, bg=BG)
        cont.pack(fill="both", padx=36)
        for s in sessions:
            self._session_row(cont, s)

    def _session_row(self, parent, s):
        scol = {"Upcoming":ACCENT,"Completed":SUCCESS,
                "Cancelled":DANGER,"Rescheduled":ORANGE}.get(s.get("status",""),MUTED)
        r = Card(parent, bg=CARD)
        r.pack(fill="x", pady=4)
        tk.Frame(r, bg=scol, width=4).pack(side="left", fill="y")

        # Date badge
        try:
            dt = datetime.strptime(s.get("date","2000-01-01"),"%Y-%m-%d")
            dys,mns = dt.strftime("%d"), dt.strftime("%b").upper()
        except: dys,mns="?","???"

        db = tk.Frame(r, bg=darker(scol,30), width=60, height=60)
        db.pack(side="left", padx=10, pady=10)
        db.pack_propagate(False)
        tk.Label(db, text=dys, font=("Georgia",17,"bold"),
                 fg=WHITE, bg=darker(scol,30)).pack(pady=(10,0))
        tk.Label(db, text=mns, font=ff(8,"bold"),
                 fg=WHITE, bg=darker(scol,30)).pack()

        # Info
        inf = tk.Frame(r, bg=CARD)
        inf.pack(side="left", fill="x", expand=True, pady=10)
        tk.Label(inf, text=s.get("title","—"), font=ff(13,"bold"),
                 fg=TEXT, bg=CARD, anchor="w").pack(fill="x")
        row2 = f"{s.get('participants','')}  ·  {s.get('time','')}  ·  {s.get('duration','')}  ·  {s.get('mode','')}"
        tk.Label(inf, text=row2, font=ff(10), fg=MUTED, bg=CARD, anchor="w").pack(fill="x")
        if s.get("topic"):
            tk.Label(inf, text=f"Topic: {s['topic']}", font=ff(9),
                     fg=MUTED, bg=CARD, anchor="w").pack(fill="x")
        if s.get("notes"):
            n = s["notes"]
            tk.Label(inf, text=n[:80]+"…" if len(n)>80 else n,
                     font=ff(9), fg=DIM, bg=CARD, anchor="w",
                     wraplength=550, justify="left").pack(fill="x", pady=(2,0))

        rt = tk.Frame(r, bg=CARD)
        rt.pack(side="right", anchor="n", padx=10, pady=10)
        tk.Label(rt, text=s.get("status",""), font=ff(9,"bold"),
                 fg=scol, bg=CARD).pack(anchor="e")
        GhostBtn(rt,"Edit",   lambda s=s:        self._edit_session(s),  w=7).pack(pady=(8,2))
        GhostBtn(rt,"Delete", lambda sid=s["id"]: self._del_session(sid), w=7).pack()

    def _add_session(self):
        pairs = [f"{p['mentor_name']} & {p['mentee_name']}"
                 for p in self.data["pairs"]]
        fields = []
        for fd in SESSION_F:
            fd = dict(fd)
            if fd["key"]=="participants" and pairs:
                fd["type"]="combo"; fd["values"]=pairs
            fields.append(fd)
        dlg = Dialog(self,"Schedule Session","Fields marked * are required.",fields)
        if dlg.result:
            dlg.result["id"] = uid()
            self.data["sessions"].append(dlg.result)
            save_data(self.data)
            self._refresh_sessions()
            Toast(self, f"✓  Session '{dlg.result.get('title','')}' scheduled!", SUCCESS)

    def _edit_session(self, s):
        dlg = Dialog(self,"Edit Session","Update session details.",
                     SESSION_F, prefill=s)
        if dlg.result:
            dlg.result["id"] = s["id"]
            lst = self.data["sessions"]
            idx = next(i for i,x in enumerate(lst) if x["id"]==s["id"])
            lst[idx] = dlg.result
            save_data(self.data)
            self._refresh_sessions()
            Toast(self, "✓  Session updated.", TEAL)

    def _del_session(self, sid):
        if messagebox.askyesno("Delete","Delete this session?"):
            self.data["sessions"] = [x for x in self.data["sessions"]
                                     if x["id"]!=sid]
            save_data(self.data)
            self._refresh_sessions()
            Toast(self, "✕  Session deleted.", DANGER)

    # ══════════════════════════════════════════════════════════════════════════
    #  GOALS
    # ══════════════════════════════════════════════════════════════════════════
    def _build_goals_page(self):
        page = self._pages["goals"]
        PageHeader(page,"Goals & Progress",
                   "Set SMART goals, track milestones and celebrate wins.",
                   "+ Add Goal", self._add_goal)

        # Toolbar
        tb = tk.Frame(page, bg=BG)
        tb.pack(fill="x", padx=36, pady=(0,10))
        self._search_goals = tk.StringVar()
        self._search_goals.trace_add("write", lambda *a: self._refresh_goals())
        SearchBar(tb, self._search_goals, "Search goals…").pack(side="left", fill="x", expand=True)

        self._filter_goals = tk.StringVar(value="All Status")
        self._filter_goals.trace_add("write", lambda *a: self._refresh_goals())
        f_border = tk.Frame(tb, bg=BORDER, padx=1, pady=1)
        f_border.pack(side="left", padx=(10,0))
        f_inner  = tk.Frame(f_border, bg=INPUT_BG)
        f_inner.pack()
        ttk.Combobox(f_inner, textvariable=self._filter_goals,
                     values=["All Status","Not Started","In Progress","Completed","On Hold","Dropped"],
                     font=ff(10), state="readonly", width=14).pack(padx=6, pady=6)

        self._filter_goals_pri = tk.StringVar(value="All Priority")
        self._filter_goals_pri.trace_add("write", lambda *a: self._refresh_goals())
        p_border = tk.Frame(tb, bg=BORDER, padx=1, pady=1)
        p_border.pack(side="left", padx=(6,0))
        p_inner  = tk.Frame(p_border, bg=INPUT_BG)
        p_inner.pack()
        ttk.Combobox(p_inner, textvariable=self._filter_goals_pri,
                     values=["All Priority","High","Medium","Low"],
                     font=ff(10), state="readonly", width=13).pack(padx=6, pady=6)

        Btn(tb, "⬇  Export CSV",
            lambda: export_csv(self, self.data["goals"], "goals.csv"),
            bg=PINK, w=16, py=7).pack(side="left", padx=(10,0))

        self._body_goals = tk.Frame(page, bg=BG)
        self._body_goals.pack(fill="both", expand=True)

    def _refresh_goals(self):
        for w in self._body_goals.winfo_children(): w.destroy()
        raw   = self.data["goals"]
        query = getattr(self, "_search_goals", tk.StringVar()).get().strip().lower()
        sf    = getattr(self, "_filter_goals", tk.StringVar()).get()
        pf    = getattr(self, "_filter_goals_pri", tk.StringVar()).get()

        goals = raw
        if query and query != "search goals…":
            goals = [g for g in goals if
                     query in g.get("title","").lower() or
                     query in g.get("mentee","").lower() or
                     query in g.get("mentor","").lower() or
                     query in g.get("category","").lower()]
        if sf and sf != "All Status":
            goals = [g for g in goals if g.get("status","") == sf]
        if pf and pf != "All Priority":
            goals = [g for g in goals if g.get("priority","") == pf]

        if not goals:
            EmptyState(self._body_goals,
                "No goals found" if (query or sf!="All Status" or pf!="All Priority") else "No goals yet",
                "Set your first SMART goal to start tracking progress.",
                "+ Add Goal", self._add_goal)
            return
        inner, _ = Scroll(self._body_goals, bg=BG)
        cont = tk.Frame(inner, bg=BG)
        cont.pack(fill="both", padx=36)

        total = len(goals)
        done  = sum(1 for g in goals if g.get("status")=="Completed")
        pct   = done/total if total else 0

        # Progress bar card
        pc = Card(cont, bg=CARD)
        pc.pack(fill="x", pady=(0,14))
        tk.Frame(pc, bg=SUCCESS, height=3).pack(fill="x")
        pi = tk.Frame(pc, bg=CARD)
        pi.pack(fill="x", padx=18, pady=12)

        # Mini donut in progress card
        pcv = tk.Canvas(pi, width=64, height=64, bg=CARD, highlightthickness=0)
        pcv.pack(side="left", padx=(0,14))
        pct_segs = [(done,SUCCESS,"Done"),
                    (total-done,CARD2,"Remaining")]
        pct_segs = [(v,c,l) for v,c,l in pct_segs if v>0]
        if pct_segs:
            draw_donut(pcv, 32,32, 28,18, pct_segs, CARD)
        pcv.create_text(32,32, text=f"{int(pct*100)}%",
                        font=ff(9,"bold"), fill=SUCCESS)

        pr = tk.Frame(pi, bg=CARD)
        pr.pack(side="left", fill="x", expand=True)
        tk.Label(pr, text=f"{done} / {total} goals completed",
                 font=ff(13,"bold"), fg=TEXT, bg=CARD).pack(anchor="w")
        bg_b = tk.Frame(pr, bg=BORDER, height=10)
        bg_b.pack(fill="x", pady=(8,0))
        bg_b.update_idletasks()
        if pct:
            tk.Frame(bg_b, bg=SUCCESS, height=10).place(relwidth=pct, relheight=1)

        tk.Label(cont, text=f"{len(goals)} of {len(raw)} goals",
                 font=ff(9), fg=MUTED, bg=BG, anchor="w").pack(fill="x", pady=(0,4))

        # Goal rows
        for g in goals:
            self._goal_row(cont, g)

    def _goal_row(self, parent, g):
        done_f = g.get("status")=="Completed"
        pcol   = {"High":DANGER,"Medium":ORANGE,"Low":SUCCESS}.get(g.get("priority",""),MUTED)

        r = Card(parent, bg=CARD)
        r.pack(fill="x", pady=4)
        r.columnconfigure(1, weight=1)

        # Checkbox
        chk_bg = SUCCESS if done_f else BORDER
        cv = tk.Canvas(r, width=30, height=30, bg=CARD, highlightthickness=0)
        cv.grid(row=0, column=0, rowspan=2, padx=(14,12), pady=12, sticky="ns")
        cv.create_oval(3,3,27,27, fill=chk_bg, outline="")
        if done_f:
            cv.create_line(9,16,14,22,22,10, fill=WHITE, width=2.5,
                           capstyle="round", joinstyle="round")
        cv.config(cursor="hand2")
        cv.bind("<Button-1>", lambda e, gid=g["id"]: self._toggle_goal(gid))

        # Text
        tfont = ff(12,"bold") if not done_f else ff(12)
        tk.Label(r, text=g.get("title","—"), font=tfont,
                 fg=DIM if done_f else TEXT, bg=CARD).grid(
                 row=0, column=1, sticky="w", pady=(12,2))
        meta = (f"Mentee: {g.get('mentee','')}  ·  "
                f"Due: {g.get('due','')}  ·  "
                f"Category: {g.get('category','')}  ·  "
                f"Mentor: {g.get('mentor','')}")
        tk.Label(r, text=meta, font=ff(9), fg=DIM, bg=CARD).grid(
                 row=1, column=1, sticky="w", pady=(0,12))

        # Priority badge
        pf = tk.Frame(r, bg=CARD2, highlightthickness=1,
                      highlightbackground=pcol)
        pf.grid(row=0, column=2, padx=10, sticky="ns", pady=12)
        tk.Label(pf, text=g.get("priority",""), font=ff(9,"bold"),
                 fg=pcol, bg=CARD2, padx=8, pady=4).pack()

        # Buttons
        bf = tk.Frame(r, bg=CARD)
        bf.grid(row=0, column=3, rowspan=2, padx=(0,12))
        GhostBtn(bf,"Edit",  lambda g=g:          self._edit_goal(g),  w=6).pack(pady=(0,3))
        GhostBtn(bf,"✕",     lambda gid=g["id"]:  self._del_goal(gid), w=3).pack()

    def _add_goal(self):
        mentees = [m["name"] for m in self.data["mentees"]]
        mentors = [m["name"] for m in self.data["mentors"]]
        fields  = self._inject_people(GOAL_F, mentors, mentees)
        dlg = Dialog(self,"Add Goal","Fields marked * are required.",fields)
        if dlg.result:
            dlg.result["id"] = uid()
            self.data["goals"].append(dlg.result)
            save_data(self.data)
            self._refresh_goals()
            Toast(self, f"✓  Goal '{dlg.result.get('title','')}' added!", SUCCESS)

    def _edit_goal(self, g):
        mentees = [m["name"] for m in self.data["mentees"]]
        mentors = [m["name"] for m in self.data["mentors"]]
        fields  = self._inject_people(GOAL_F, mentors, mentees)
        dlg = Dialog(self,"Edit Goal","Update goal details.",
                     fields, prefill=g)
        if dlg.result:
            dlg.result["id"] = g["id"]
            lst = self.data["goals"]
            idx = next(i for i,x in enumerate(lst) if x["id"]==g["id"])
            lst[idx] = dlg.result
            save_data(self.data)
            self._refresh_goals()
            Toast(self, "✓  Goal updated.", TEAL)

    def _inject_people(self, fields, mentors, mentees):
        out = []
        for fd in fields:
            fd = dict(fd)
            if fd["key"]=="mentee" and mentees:
                fd["type"]="combo"; fd["values"]=mentees
            if fd["key"]=="mentor" and mentors:
                fd["type"]="combo"; fd["values"]=mentors
            out.append(fd)
        return out

    def _toggle_goal(self, gid):
        for g in self.data["goals"]:
            if g["id"]==gid:
                g["status"] = "In Progress" if g.get("status")=="Completed" else "Completed"
        save_data(self.data)
        self._refresh_goals()

    def _del_goal(self, gid):
        if messagebox.askyesno("Delete","Delete this goal?"):
            self.data["goals"] = [g for g in self.data["goals"] if g["id"]!=gid]
            save_data(self.data)
            self._refresh_goals()
            Toast(self, "✕  Goal deleted.", DANGER)

    # ══════════════════════════════════════════════════════════════════════════
    #  MATCHING
    # ══════════════════════════════════════════════════════════════════════════
    def _build_matching_page(self):
        page = self._pages["matching"]
        PageHeader(page,"Matching System",
                   "Pair mentors with mentees by field and expertise.",
                   "+ Create Pair", self._add_pair)
        top = tk.Frame(page, bg=BG)
        top.pack(fill="x", padx=36, pady=(0,14))
        Btn(top,"⚡  Auto-match All", self._auto_match,
            bg=TEAL, w=22, py=8).pack(side="left")
        tk.Label(top,
                 text="  Automatically pairs unmatched mentees with mentors in the same field",
                 font=ff(10), fg=MUTED, bg=BG).pack(side="left")
        self._body_matching = tk.Frame(page, bg=BG)
        self._body_matching.pack(fill="both", expand=True)

    def _refresh_matching(self):
        for w in self._body_matching.winfo_children(): w.destroy()
        pairs = self.data["pairs"]
        if not pairs:
            EmptyState(self._body_matching,
                "No pairs yet",
                "Create a pair manually or use Auto-match.",
                "+ Create Pair", self._add_pair)
            return
        inner, _ = Scroll(self._body_matching, bg=BG)
        cont = tk.Frame(inner, bg=BG)
        cont.pack(fill="both", padx=36)
        for p in pairs:
            self._pair_row(cont, p)

    def _pair_row(self, parent, p):
        r = Card(parent, bg=CARD)
        r.pack(fill="x", pady=5)
        mcol = SUCCESS if p.get("auto") else ACCENT
        tk.Frame(r, bg=mcol, width=4).pack(side="left", fill="y")

        # Avatars
        cv = tk.Canvas(r, width=90, height=54, bg=CARD, highlightthickness=0)
        cv.pack(side="left", padx=12, pady=10)
        draw_av(cv, 20, 27, 20, p.get("mentor_name","?"), 11)
        cv.create_text(45, 27, text="⇌", fill=MUTED, font=ff(16))
        draw_av(cv, 70, 27, 20, p.get("mentee_name","?"), 11)

        mid = tk.Frame(r, bg=CARD)
        mid.pack(side="left", fill="x", expand=True, pady=10)
        tk.Label(mid, text=f"{p.get('mentor_name','')}   →   {p.get('mentee_name','')}",
                 font=ff(13,"bold"), fg=TEXT, bg=CARD, anchor="w").pack(fill="x")
        tk.Label(mid, text=f"Field: {p.get('field','')}  ·  Matched: {p.get('date','')}",
                 font=ff(10), fg=MUTED, bg=CARD, anchor="w").pack(fill="x")
        if p.get("notes"):
            tk.Label(mid, text=p["notes"][:70]+"…" if len(p.get("notes",""))>70 else p["notes"],
                     font=ff(9), fg=DIM, bg=CARD, anchor="w").pack(fill="x", pady=(2,0))

        rt = tk.Frame(r, bg=CARD)
        rt.pack(side="right", anchor="n", padx=12, pady=10)
        mlbl = "Auto-matched" if p.get("auto") else "Manual"
        tk.Label(rt, text=mlbl, font=ff(9,"bold"), fg=mcol, bg=CARD).pack(anchor="e")
        GhostBtn(rt,"Remove", lambda pid=p["id"]: self._del_pair(pid),
                 w=9).pack(pady=(10,0))

    def _add_pair(self):
        mentors = [m["name"] for m in self.data["mentors"]] or ["(Add mentors first)"]
        mentees = [m["name"] for m in self.data["mentees"]] or ["(Add mentees first)"]
        fields  = [
            {"key":"mentor_name","label":"Select Mentor","type":"combo","values":mentors,"required":True},
            {"key":"mentee_name","label":"Select Mentee","type":"combo","values":mentees,"required":True},
        ] + PAIR_F_BASE
        dlg = Dialog(self,"Create Pair","Manually pair a mentor with a mentee.",fields)
        if dlg.result:
            dlg.result.update({"id":uid(),"date":date.today().isoformat(),"auto":False})
            self.data["pairs"].append(dlg.result)
            save_data(self.data)
            self._refresh_matching()
            Toast(self, f"✓  Pair created: {dlg.result.get('mentor_name','')} ⇌ {dlg.result.get('mentee_name','')}", SUCCESS)

    def _auto_match(self):
        if not self.data["mentors"] or not self.data["mentees"]:
            messagebox.showinfo("Auto-match",
                "You need at least one mentor and one mentee.")
            return
        paired = {p["mentee_name"] for p in self.data["pairs"]}
        new = []
        for mentee in self.data["mentees"]:
            if mentee["name"] in paired: continue
            same = [m for m in self.data["mentors"]
                    if m.get("field")==mentee.get("field")]
            chosen = random.choice(same) if same \
                     else random.choice(self.data["mentors"])
            new.append({"id":uid(),
                        "mentor_name":chosen["name"],
                        "mentee_name":mentee["name"],
                        "field":mentee.get("field","General"),
                        "date":date.today().isoformat(),
                        "auto":True,
                        "notes":f"Auto-matched by field: {mentee.get('field','General')}"})
        if new:
            self.data["pairs"].extend(new)
            save_data(self.data)
            messagebox.showinfo("Auto-match",f"{len(new)} new pair(s) created!")
            Toast(self, f"⚡  {len(new)} pair(s) auto-matched!", SUCCESS)
        else:
            messagebox.showinfo("Auto-match","All mentees are already paired!")
        self._refresh_matching()

    def _del_pair(self, pid):
        if messagebox.askyesno("Remove","Remove this pair?"):
            self.data["pairs"] = [p for p in self.data["pairs"] if p["id"]!=pid]
            save_data(self.data)
            self._refresh_matching()
            Toast(self, "✕  Pair removed.", DANGER)


# ── Entry ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = App()  # Tk root must exist before ttk.Style()
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TCombobox",
                    fieldbackground=INPUT_BG,
                    background=INPUT_BG,
                    foreground=TEXT,
                    selectbackground=ACCENT,
                    selectforeground=WHITE,
                    bordercolor=BORDER,
                    arrowcolor=TEXT,
                    insertcolor=TEXT,
                    padding=4)
    style.map("TCombobox",
              fieldbackground=[("readonly",INPUT_BG)],
              foreground=[("readonly",TEXT)],
              selectbackground=[("readonly",ACCENT)])
    app.mainloop()
