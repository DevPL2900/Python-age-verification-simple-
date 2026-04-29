import tkinter as tk
from tkinter import messagebox
import random
import datetime

# ── Farb-Konfiguration ────────────────────────────────────────────────────────
REZEPT_FARBEN = {
    "Rosa": {"bg": "#F8C8D0", "border": "#E0909E", "beschreibung": "Kassenrezept",     "gueltig": "28 Tage"},
    "Blau": {"bg": "#BDD9F2", "border": "#6AAAD4", "beschreibung": "Privatrezept",     "gueltig": "3 Monate"},
    "Grün": {"bg": "#B2E4B2", "border": "#5CB85C", "beschreibung": "Empfehlung",       "gueltig": "unbegrenzt"},
    "Gelb": {"bg": "#FFF0A0", "border": "#D4B800", "beschreibung": "Betäubungsmittel", "gueltig": "7 Tage"},
}

BG        = "#F4F7FB"
CARD      = "#FFFFFF"
PRIMARY   = "#1B3F6E"
ACCENT    = "#2E6DB4"
DARK_TXT  = "#1C2B3A"
BORDER    = "#D8E2EE"
CHECK_ON  = "#2E6DB4"
CHECK_OFF = "#FFFFFF"

# ══════════════════════════════════════════════════════════════════════════════
class CustomCheck(tk.Frame):
    def __init__(self, parent, text, variable, fg=DARK_TXT, command=None, **kw):
        super().__init__(parent, bg=kw.pop("bg", CARD), **kw)
        self.var = variable
        self.cb  = command
        self.canvas = tk.Canvas(self, width=18, height=18, bg=self["bg"],
                                highlightthickness=0, cursor="hand2")
        self.canvas.grid(row=0, column=0, padx=(0, 7))
        self.label = tk.Label(self, text=text, font=("Helvetica", 11),
                              bg=self["bg"], fg=fg, cursor="hand2")
        self.label.grid(row=0, column=1, sticky="w")
        self._draw()
        self.canvas.bind("<Button-1>", self._toggle)
        self.label.bind("<Button-1>",  self._toggle)

    def _draw(self):
        self.canvas.delete("all")
        on = self.var.get()
        fill   = CHECK_ON  if on else CHECK_OFF
        border = CHECK_ON  if on else BORDER
        self.canvas.create_rectangle(1, 1, 17, 17, outline=border, fill=fill, width=2)
        if on:
            self.canvas.create_line(4, 9,  7, 13, fill="white", width=2.5)
            self.canvas.create_line(7, 13, 14, 5, fill="white", width=2.5)

    def _toggle(self, _=None):
        self.var.set(not self.var.get())
        self._draw()
        if self.cb:
            self.cb()


# ══════════════════════════════════════════════════════════════════════════════
class CustomRadio(tk.Frame):
    def __init__(self, parent, text, variable, value, group_redraw=None, **kw):
        super().__init__(parent, bg=kw.pop("bg", CARD), **kw)
        self.var          = variable
        self.value        = value
        self.group_redraw = group_redraw
        self.canvas = tk.Canvas(self, width=18, height=18, bg=self["bg"],
                                highlightthickness=0, cursor="hand2")
        self.canvas.grid(row=0, column=0, padx=(0, 7))
        self.label = tk.Label(self, text=text, font=("Helvetica", 11),
                              bg=self["bg"], fg=DARK_TXT, cursor="hand2")
        self.label.grid(row=0, column=1, sticky="w")
        self._draw()
        self.canvas.bind("<Button-1>", self._select)
        self.label.bind("<Button-1>",  self._select)

    def _draw(self):
        self.canvas.delete("all")
        on = (self.var.get() == self.value)
        border = CHECK_ON if on else BORDER
        self.canvas.create_oval(1, 1, 17, 17, outline=border, fill=CHECK_OFF, width=2)
        if on:
            self.canvas.create_oval(5, 5, 13, 13, fill=CHECK_ON, outline="")

    def _select(self, _=None):
        self.var.set(self.value)
        if self.group_redraw:
            for r in self.group_redraw:
                r._draw()


# ══════════════════════════════════════════════════════════════════════════════
class RezeptApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Arzt-Rezept System")
        self.root.geometry("780x720")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)

        self.versicherung_var  = tk.StringVar(value="")
        self.verschreibung_var = tk.BooleanVar()
        self.betaeubung_var    = tk.BooleanVar()
        self.gewaehlte_farbe   = tk.StringVar(value="Rosa")
        self._placeholder      = "Diagnose, Medikament, Dosierung …"

        self._build_ui()

    def _build_ui(self):
        # Titelleiste
        header = tk.Frame(self.root, bg=PRIMARY, height=64)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="🏥  Arzt-Rezept System",
                 font=("Georgia", 17, "bold"), bg=PRIMARY, fg="white"
                 ).pack(side="left", padx=22, pady=12)
        tk.Label(header, text="Rezeptverwaltung",
                 font=("Helvetica", 9), bg=PRIMARY, fg="#8FB5D8"
                 ).pack(side="right", padx=22)

        # Scrollbereich
        cv = tk.Canvas(self.root, bg=BG, highlightthickness=0)
        sb = tk.Scrollbar(self.root, orient="vertical", command=cv.yview)
        cv.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        cv.pack(fill="both", expand=True)

        self.main = tk.Frame(cv, bg=BG)
        win_id = cv.create_window((0, 0), window=self.main, anchor="nw")

        def _resize(e):
            cv.configure(scrollregion=cv.bbox("all"))
            cv.itemconfig(win_id, width=e.width)
        cv.bind("<Configure>", _resize)
        self.main.bind("<Configure>",
                       lambda e: cv.configure(scrollregion=cv.bbox("all")))

        # 1 · Versicherung
        card1 = self._card(self.main)
        self._card_title(card1, "1", "Versicherungsart")
        v_inner = tk.Frame(card1, bg=CARD)
        v_inner.pack(anchor="w", padx=16, pady=(0, 12))
        radio_list = []
        for lbl, val in [("Gesetzlich versichert (GKV)", "gesetzlich"),
                         ("Privat versichert (PKV)",     "privat")]:
            r = CustomRadio(v_inner, text=lbl,
                            variable=self.versicherung_var, value=val,
                            group_redraw=radio_list, bg=CARD)
            r.pack(anchor="w", pady=5)
            radio_list.append(r)

        # 2 · Rezeptart
        card2 = self._card(self.main)
        self._card_title(card2, "2", "Rezeptart")
        c_inner = tk.Frame(card2, bg=CARD)
        c_inner.pack(anchor="w", padx=16, pady=(0, 12))
        self.cb_rx = CustomCheck(c_inner, "Verschreibungspflichtig  (Rx)",
                                 self.verschreibung_var, bg=CARD)
        self.cb_rx.pack(anchor="w", pady=5)
        self.cb_btm = CustomCheck(c_inner, "Betäubungsmittel  (BtM-Rezept)",
                                  self.betaeubung_var,
                                  fg="#8B0000", bg=CARD,
                                  command=self._btm_gewaehlt)
        self.cb_btm.pack(anchor="w", pady=5)

        # 3 · Farbe
        card3 = self._card(self.main)
        self._card_title(card3, "3", "Rezeptfarbe wählen")
        legend = tk.Frame(card3, bg=CARD)
        legend.pack(anchor="w", padx=16, pady=(0, 8))
        for farbe, info in REZEPT_FARBEN.items():
            tk.Label(legend,
                     text=f"  {farbe}: {info['beschreibung']} ({info['gueltig']})  ",
                     font=("Helvetica", 9), bg=info["bg"], fg="#333",
                     padx=4, pady=3
                     ).pack(side="left", padx=3)

        farb_frame = tk.Frame(card3, bg=CARD)
        farb_frame.pack(padx=16, pady=(4, 16), anchor="w")
        self.farb_buttons = {}
        for farbe, info in REZEPT_FARBEN.items():
            btn = tk.Button(
                farb_frame, text=farbe,
                bg=info["bg"], fg=PRIMARY,
                font=("Helvetica", 11, "bold"),
                relief="flat", bd=0, width=11, pady=8,
                cursor="hand2",
                activebackground=info["border"],
                command=lambda f=farbe: self._farbe_setzen(f)
            )
            btn.pack(side="left", padx=7)
            self.farb_buttons[farbe] = btn
        self._farbe_setzen("Rosa")

        # 4 · Notizen
        card4 = self._card(self.main)
        self._card_title(card4, "4", "Ärztliche Notizen / Diagnose")
        notiz_wrap = tk.Frame(card4, bg=BORDER, bd=0)
        notiz_wrap.pack(padx=16, pady=(0, 16), fill="x")
        self.notiz_text = tk.Text(
            notiz_wrap, height=5,
            font=("Helvetica", 11),
            bg=CARD, fg="#AAAAAA",
            relief="flat", bd=8,
            wrap="word",
            insertbackground=PRIMARY
        )
        self.notiz_text.pack(fill="x", padx=1, pady=1)
        self.notiz_text.insert("1.0", self._placeholder)
        self.notiz_text.bind("<FocusIn>",  self._notiz_focus_in)
        self.notiz_text.bind("<FocusOut>", self._notiz_focus_out)

        # Ausstellen-Button
        btn_frame = tk.Frame(self.main, bg=BG)
        btn_frame.pack(pady=(4, 28))
        self.ausstellen_btn = tk.Button(
            btn_frame,
            text="📋   Krankenschein ausstellen",
            font=("Helvetica", 13, "bold"),
            bg=PRIMARY, fg="white",
            activebackground=ACCENT,
            activeforeground="white",
            relief="flat", cursor="hand2",
            padx=28, pady=12,
            command=self._ausstellen
        )
        self.ausstellen_btn.pack()
        self.ausstellen_btn.bind("<Enter>",
            lambda e: self.ausstellen_btn.config(bg=ACCENT))
        self.ausstellen_btn.bind("<Leave>",
            lambda e: self.ausstellen_btn.config(bg=PRIMARY))

    def _card(self, parent):
        outer = tk.Frame(parent, bg=BG)
        outer.pack(fill="x", padx=22, pady=8)
        card = tk.Frame(outer, bg=CARD, highlightbackground=BORDER,
                        highlightthickness=1)
        card.pack(fill="x")
        return card

    def _card_title(self, card, num, text):
        row = tk.Frame(card, bg=PRIMARY)
        row.pack(fill="x")
        tk.Label(row, text=f"  {num}  ",
                 font=("Helvetica", 10, "bold"),
                 bg=ACCENT, fg="white", padx=6, pady=4
                 ).pack(side="left")
        tk.Label(row, text=text,
                 font=("Helvetica", 11, "bold"),
                 bg=PRIMARY, fg="white", padx=10, pady=4
                 ).pack(side="left")
        tk.Frame(card, bg=CARD, height=10).pack()

    def _farbe_setzen(self, farbe):
        self.gewaehlte_farbe.set(farbe)
        for f, btn in self.farb_buttons.items():
            info = REZEPT_FARBEN[f]
            if f == farbe:
                btn.config(relief="flat",
                           highlightthickness=3,
                           highlightbackground=info["border"])
            else:
                btn.config(relief="flat",
                           highlightthickness=0)

    def _btm_gewaehlt(self):
        if self.betaeubung_var.get():
            self._farbe_setzen("Gelb")
            self.verschreibung_var.set(True)
            self.cb_rx._draw()

    def _notiz_focus_in(self, _=None):
        if self.notiz_text.get("1.0", "end-1c") == self._placeholder:
            self.notiz_text.delete("1.0", "end")
            self.notiz_text.config(fg=DARK_TXT)

    def _notiz_focus_out(self, _=None):
        if not self.notiz_text.get("1.0", "end-1c").strip():
            self.notiz_text.insert("1.0", self._placeholder)
            self.notiz_text.config(fg="#AAAAAA")

    def _ausstellen(self):
        if not self.versicherung_var.get():
            messagebox.showwarning(
                "Fehlende Angabe", "Bitte wählen Sie die Versicherungsart aus.")
            return

        farbe = self.gewaehlte_farbe.get()
        info  = REZEPT_FARBEN[farbe]
        notiz = self.notiz_text.get("1.0", "end-1c").strip()
        if notiz == self._placeholder or not notiz:
            notiz = "—"

        versicherung  = ("Gesetzlich versichert (GKV)"
                         if self.versicherung_var.get() == "gesetzlich"
                         else "Privat versichert (PKV)")
        verschreibung = "Ja" if self.verschreibung_var.get() else "Nein"
        betaeubung    = "Ja" if self.betaeubung_var.get()    else "Nein"
        rezept_nr     = random.randint(100000, 999999)
        datum         = datetime.date.today().strftime("%d.%m.%Y")

        win = tk.Toplevel(self.root)
        win.title("Rezept ausgestellt")
        win.geometry("500x500")
        win.configure(bg=info["bg"])
        win.resizable(False, False)
        win.grab_set()

        head = tk.Frame(win, bg=info["border"])
        head.pack(fill="x")
        tk.Label(head, text=f"🩺  {info['beschreibung'].upper()}",
                 font=("Georgia", 16, "bold"),
                 bg=info["border"], fg="#1a3c5e",
                 pady=14, padx=20).pack(side="left")
        tk.Label(head, text=f"Nr. {rezept_nr}",
                 font=("Helvetica", 9),
                 bg=info["border"], fg="#444",
                 padx=20).pack(side="right")

        body = tk.Frame(win, bg=info["bg"])
        body.pack(fill="both", expand=True, padx=28, pady=16)

        details = [
            ("Datum",               datum),
            ("Versicherung",        versicherung),
            ("Rezeptfarbe",         f"{farbe}  ({info['beschreibung']})"),
            ("Gültigkeit",          info["gueltig"]),
            ("Verschreibungspfl.",  verschreibung),
            ("Betäubungsmittel",    betaeubung),
            ("Notizen / Diagnose",  notiz),
        ]

        for i, (lbl, val) in enumerate(details):
            row_bg = info["bg"] if i % 2 == 0 else self._darken(info["bg"])
            row = tk.Frame(body, bg=row_bg)
            row.pack(fill="x")
            tk.Label(row, text=lbl, width=22, anchor="w",
                     font=("Helvetica", 10, "bold"),
                     bg=row_bg, fg="#1a3c5e", pady=7, padx=8
                     ).pack(side="left")
            tk.Label(row, text=val, anchor="w",
                     font=("Helvetica", 10),
                     bg=row_bg, fg="#222", wraplength=250, pady=7
                     ).pack(side="left")

        tk.Frame(win, height=1, bg=info["border"]).pack(fill="x")

        btn_area = tk.Frame(win, bg=info["bg"])
        btn_area.pack(pady=16)

        def neues_rezept():
            win.destroy()
            self._formular_zuruecksetzen()

        tk.Button(btn_area,
                  text="✚   Neues Rezept ausstellen",
                  font=("Helvetica", 11, "bold"),
                  bg=PRIMARY, fg="white",
                  activebackground=ACCENT,
                  relief="flat", cursor="hand2",
                  padx=18, pady=9,
                  command=neues_rezept
                  ).pack(side="left", padx=8)

        tk.Button(btn_area,
                  text="Schließen",
                  font=("Helvetica", 10),
                  bg="#7A90A8", fg="white",
                  activebackground="#5A6E80",
                  relief="flat", cursor="hand2",
                  padx=14, pady=9,
                  command=win.destroy
                  ).pack(side="left", padx=8)

    def _formular_zuruecksetzen(self):
        self.versicherung_var.set("")
        self.verschreibung_var.set(False)
        self.betaeubung_var.set(False)
        self.cb_rx._draw()
        self.cb_btm._draw()
        self._farbe_setzen("Rosa")
        self.notiz_text.delete("1.0", "end")
        self.notiz_text.insert("1.0", self._placeholder)
        self.notiz_text.config(fg="#AAAAAA")

    @staticmethod
    def _darken(hex_color, amount=12):
        hex_color = hex_color.lstrip("#")
        r, g, b = (int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        return f"#{max(0,r-amount):02x}{max(0,g-amount):02x}{max(0,b-amount):02x}"


if __name__ == "__main__":
    root = tk.Tk()
    app = RezeptApp(root)
    root.mainloop()
